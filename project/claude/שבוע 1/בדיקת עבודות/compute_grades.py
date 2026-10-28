#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
compute_grades.py: חישוב ציונים לפי המחוון של שיעורים 1 ו-2 (שבוע 1, קורס Power BI).

הקלט: קובץ scores.json שהבדיקה כתבה, בצורה הזו:
{
  "students": [
    {"name": "כהן נועה", "folder": "שם התיקייה",
     "submitted": {"L1": true, "L2": true},
     "scores": {"L1.S": 7, "L1.Q1a": 5.5, ... , "B.L1Q3": 2, "B.insight": 0},
     "identical_screens": ["L2"],
     "foreign_file": false,
     "copy_flag": "none" | "medium" | "strong",
     "teacher_review": true | false,
     "mistakes": ["M1-3", "M2-9"]}
  ]
}
בשיעור שלא הוגש ("submitted": false) אפשר להשמיט את החלקים שלו, והם נספרים 0.
ב-L1.S וב-L2.S רושמים את הנקודות שהצילום קיבל לפי המחוון. אם השיעור מופיע ב-identical_screens
(צילום זהה לצילום של תלמיד אחר), הסקריפט נותן חצי מהנקודות האלה. foreign_file: true (שם קובץ של
תלמיד אחר בכותרת הצילום) מוריד נקודה אחת מהציון הסופי. שני השדות לא חובה.

מה הוא עושה:
  1. בודק שכל חלק קיים, בין 0 למקסימום, בקפיצות של 0.5.
  2. מחשב ציון לכל שיעור, בונוס, הורדות וציון סופי (מעוגל כלפי מעלה מ-0.5, ולא יותר מ-100).
  3. כותב grades.csv (UTF-8 עם BOM, נפתח ב-Excel בעברית) ו-class_summary.md.

שימוש:
  python3 compute_grades.py scores.json [תיקיית_פלט]

אם משנים נקודות במחוון, משנים גם את PARTS כאן. קוד היציאה 1 אם יש שגיאה. Python 3 בלבד.
"""
import csv
import json
import math
import os
import statistics
import sys

# (מזהה, שיעור, מקסימום, תיאור)
PARTS = [
    ("L1.S", "L1", 12, "שיעור 1: צילום הכרטיס"),
    ("L1.Q1a", "L1", 6, "שיעור 1, שאלה 1 א: מה כתוב בשורה"),
    ("L1.Q1b", "L1", 6, "שיעור 1, שאלה 1 ב: פרט שחוזר"),
    ("L1.Q2a", "L1", 8, "שיעור 1, שאלה 2 א: שורות בלי species"),
    ("L1.Q2b", "L1", 7, "שיעור 1, שאלה 2 ב: משמעות הפרט שחוזר"),
    ("L1.Q2c", "L1", 7, "שיעור 1, שאלה 2 ג: למה פחות מ-15,120"),
    ("L1.C", "L1", 4, "שיעור 1: שלמות ההגשה"),
    ("L2.S", "L2", 18, "שיעור 2: צילום רשימת הצעדים"),
    ("L2.Q1a", "L2", 5, "שיעור 2, שאלה 1 א: מה זה NA"),
    ("L2.Q1b", "L2", 7, "שיעור 2, שאלה 1 ב: למה NA נשאר"),
    ("L2.Q2a", "L2", 5, "שיעור 2, שאלה 2 א: מה הוריד סינון period"),
    ("L2.Q2b", "L2", 5, "שיעור 2, שאלה 2 ב: מה הוריד סינון species"),
    ("L2.Q2c", "L2", 6, "שיעור 2, שאלה 2 ג: הכלל מאחורי כל סינון"),
    ("L2.C", "L2", 4, "שיעור 2: שלמות ההגשה"),
]
BONUS = [
    ("B.L1Q3", 3, "בונוס: אתגר סוגי המשתנים (שיעור 1)"),
    ("B.insight", 2, "בונוס: תובנה עצמאית"),
]
MAX_TOTAL = 100
FLAGS = ("none", "medium", "strong")
SCREENS = {"L1": "L1.S", "L2": "L2.S"}
FOREIGN_FILE_PENALTY = 1


def half_up(x):
    return int(math.floor(x + 0.5))


def fmt(x):
    return str(int(x)) if float(x).is_integer() else str(x)


def load(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def grade_student(st, errors):
    name = st.get("name") or st.get("folder") or "(בלי שם)"
    scores = st.get("scores", {})
    sub = st.get("submitted", {"L1": True, "L2": True})
    res = {"L1": 0.0, "L2": 0.0, "bonus": 0.0, "parts": {}}
    identical = st.get("identical_screens", [])
    if not isinstance(identical, list) or any(x not in SCREENS for x in identical):
        errors.append("%s: identical_screens צריך להיות רשימה של L1 ו-L2" % name)
        identical = []
    for pid, les, mx, _ in PARTS:
        if pid not in scores:
            if sub.get(les, True):
                errors.append("%s: חסר חלק %s" % (name, pid))
            val = 0.0
        else:
            val = scores[pid]
        if not isinstance(val, (int, float)) or val < 0 or val > mx or (val * 2) % 1 != 0:
            errors.append("%s: הערך של %s הוא %r, צריך מספר בין 0 ל-%d בקפיצות של 0.5" % (name, pid, val, mx))
            val = 0.0
        if pid == SCREENS.get(les) and les in identical:
            val = val / 2
        res["parts"][pid] = val
        res[les] += val
    for pid, mx, _ in BONUS:
        val = scores.get(pid, 0)
        if not isinstance(val, (int, float)) or val < 0 or val > mx or (val * 2) % 1 != 0:
            errors.append("%s: הערך של %s הוא %r, צריך מספר בין 0 ל-%d בקפיצות של 0.5" % (name, pid, val, mx))
            val = 0.0
        res["parts"][pid] = val
        res["bonus"] += val
    flag = st.get("copy_flag", "none")
    if flag not in FLAGS:
        errors.append("%s: copy_flag חייב להיות אחד מ-%s" % (name, ", ".join(FLAGS)))
        flag = "none"
    penalty = FOREIGN_FILE_PENALTY if st.get("foreign_file") else 0
    raw = res["L1"] + res["L2"] + res["bonus"] - penalty
    res.update(name=name, folder=st.get("folder", ""), raw=raw, total=max(0, min(MAX_TOTAL, half_up(raw))),
               identical=identical, penalty=penalty,
               copy_flag=flag, review=bool(st.get("teacher_review")), mistakes=list(st.get("mistakes", [])),
               submitted=sub)
    return res


def write_csv(path, rows):
    with open(path, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f)
        w.writerow(["שם", "תיקייה", "שיעור 1 (מתוך 50)", "שיעור 2 (מתוך 50)", "בונוס (עד 5)",
                    "צילום זהה (חצי מנקודות הצילום)", "שם קובץ של אחר (הורדה)", "ציון סופי",
                    "חשד להעתקה", "לבדיקת מורה", "טעויות נפוצות"])
        for r in rows:
            w.writerow([r["name"], r["folder"], fmt(r["L1"]), fmt(r["L2"]), fmt(r["bonus"]),
                        " ".join(r["identical"]), fmt(r["penalty"]) if r["penalty"] else "", r["total"],
                        r["copy_flag"], "כן" if r["review"] else "", " ".join(r["mistakes"])])


def write_summary(path, rows):
    totals = [r["total"] for r in rows]
    out = ["# תמונת מצב: שבוע 1, שיעורים 1 ו-2", ""]
    out.append("תלמידים שנבדקו: %d" % len(rows))
    if totals:
        out.append("ממוצע: %.1f, חציון: %s, נמוך: %d, גבוה: %d" % (statistics.mean(totals), fmt(statistics.median(totals)), min(totals), max(totals)))
        bands = [("90 ומעלה", 90, 101), ("80 עד 89", 80, 90), ("70 עד 79", 70, 80), ("60 עד 69", 60, 70), ("מתחת ל-60", 0, 60)]
        out += ["", "## התפלגות", "", "| טווח | תלמידים |", "| --- | --- |"]
        for label, lo, hi in bands:
            out.append("| %s | %d |" % (label, sum(1 for t in totals if lo <= t < hi)))
    out += ["", "## ממוצע לכל חלק", "", "| חלק | ממוצע | מקסימום | אחוז | תיאור |", "| --- | --- | --- | --- | --- |"]
    for pid, les, mx, desc in PARTS:
        vals = [r["parts"][pid] for r in rows if r["submitted"].get(les, True)]
        if vals:
            avg = statistics.mean(vals)
            out.append("| %s | %.1f | %d | %d%% | %s |" % (pid, avg, mx, round(100 * avg / mx), desc))
    tally = {}
    for r in rows:
        for m in r["mistakes"]:
            tally.setdefault(m, []).append(r["name"])
    if tally:
        out += ["", "## טעויות נפוצות", "", "| קוד | תלמידים | שמות |", "| --- | --- | --- |"]
        for m, names in sorted(tally.items(), key=lambda kv: (-len(kv[1]), kv[0])):
            out.append("| %s | %d | %s |" % (m, len(names), ", ".join(names)))
    flagged = [r for r in rows if r["copy_flag"] != "none"]
    review = [r for r in rows if r["review"]]
    out += ["", "## לתשומת לב המורה", ""]
    out.append("חשד להעתקה (חזק או בינוני): %s" % (", ".join("%s (%s)" % (r["name"], r["copy_flag"]) for r in flagged) or "אין"))
    out.append("")
    out.append("לבדיקת מורה: %s" % (", ".join(r["name"] for r in review) or "אין"))
    notsub = [r for r in rows if not all(r["submitted"].get(k, True) for k in ("L1", "L2"))]
    out.append("")
    out.append("הגשה חלקית או חסרה: %s" % (", ".join(r["name"] for r in notsub) or "אין"))
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(out) + "\n")


def main(argv):
    if len(argv) < 2:
        print(__doc__)
        return 1
    data = load(argv[1])
    outdir = argv[2] if len(argv) > 2 else os.path.dirname(os.path.abspath(argv[1]))
    os.makedirs(outdir, exist_ok=True)
    errors = []
    rows = [grade_student(st, errors) for st in data.get("students", [])]
    if errors:
        print("נמצאו %d שגיאות. לא נכתבו קבצים." % len(errors))
        for e in errors:
            print(" - " + e)
        return 1
    rows.sort(key=lambda r: r["name"])
    write_csv(os.path.join(outdir, "grades.csv"), rows)
    write_summary(os.path.join(outdir, "class_summary.md"), rows)
    print("נכתבו grades.csv ו-class_summary.md ב-%s (%d תלמידים)" % (outdir, len(rows)))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
