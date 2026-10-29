#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
compute_grades.py: חישוב ציונים לפי המחוונים של שבוע 1 בקורס Power BI: שיעורים 1 ו-2, או שיעור 3.

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
בחלקי הצילום (L1.S ו-L2.S, ובשיעור 3 L3.SG ו-L3.ST) רושמים את הנקודות שהצילום קיבל לפי המחוון.
כל צילום שמופיע ב-identical_screens (קובץ צילום זהה לקובץ של תלמיד אחר) מוריד נקודה אחת מהציון הסופי,
ובשיעור 3 שתי נקודות.
בשיעורים 1 ו-2 הערכים ב-identical_screens הם L1 ו-L2, ובשיעור 3 הם graph ו-table. foreign_file: true (שם קובץ של
תלמיד אחר בכותרת הצילום) מוריד עוד נקודה אחת. שני השדות לא חובה.

מה הוא עושה:
  1. בודק שכל חלק קיים, בין 0 למקסימום, בקפיצות של 0.5.
  2. מחשב ציון לכל שיעור, בונוס, הורדות וציון סופי (מעוגל כלפי מעלה מ-0.5, ולא יותר מ-100).
  3. כותב grades.csv (UTF-8 עם BOM, נפתח ב-Excel בעברית) ו-class_summary.md.

שימוש:
  python3 compute_grades.py scores.json [תיקיית_פלט]
  python3 compute_grades.py --lesson 3 scores.json [תיקיית_פלט]    (מחוון שיעור 3)

אם משנים נקודות במחוון, משנים גם את PARTS_12 או PARTS_3 כאן. קוד היציאה 1 אם יש שגיאה. Python 3 בלבד.
"""
import csv
import json
import math
import os
import statistics
import sys

# (מזהה, שיעור, מקסימום, תיאור)
PARTS_12 = [
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
BONUS_12 = [
    ("B.L1Q3", 3, "בונוס: אתגר סוגי המשתנים (שיעור 1)"),
    ("B.insight", 2, "בונוס: תובנה עצמאית"),
]
PARTS_3 = [
    ("L3.SG", "L3", 15, "שיעור 3: צילום הגרף"),
    ("L3.ST", "L3", 15, "שיעור 3: צילום טבלת הסבבים"),
    ("L3.Q1", "L3", 6, "שיעור 3, שאלה 1: שתי השערות לירידה ב-2020"),
    ("L3.Q2a", "L3", 20, "שיעור 3, שאלה 2 א: לכידות, סבבים וממוצע לסבב"),
    ("L3.Q2b", "L3", 14, "שיעור 3, שאלה 2 ב: פחות חיות או מאמץ דגימה קטן יותר"),
    ("L3.Q2c", "L3", 8, "שיעור 3, שאלה 2 ג: 2023 מול 2025"),
    ("L3.Q2d", "L3", 18, "שיעור 3, שאלה 2 ד: טענה, ראיה ונימוק"),
    ("L3.C", "L3", 4, "שיעור 3: שלמות ההגשה"),
]
BONUS_3 = [
    ("B.season", 3, "בונוס: עונתיות ב-2020"),
    ("B.insight", 2, "בונוס: תובנה עצמאית"),
]
RUBRICS = {
    "1-2": dict(parts=PARTS_12, bonus=BONUS_12, screens={"L1": "L1.S", "L2": "L2.S"}, title="שיעורים 1 ו-2"),
    "3": dict(parts=PARTS_3, bonus=BONUS_3, screens={"graph": "L3.SG", "table": "L3.ST"}, title="שיעור 3",
              identical_penalty=2),
}
RUBRIC = RUBRICS["1-2"]
PARTS, BONUS, SCREENS = RUBRIC["parts"], RUBRIC["bonus"], RUBRIC["screens"]
MAX_TOTAL = 100
FLAGS = ("none", "medium", "strong")
FOREIGN_FILE_PENALTY = 1
IDENTICAL_PENALTY = 1


def half_up(x):
    return int(math.floor(x + 0.5))


def fmt(x):
    return str(int(x)) if float(x).is_integer() else str(x)


def lessons():
    out = []
    for _, les, _, _ in PARTS:
        if les not in out:
            out.append(les)
    return out


def lesson_max(les):
    return sum(mx for _, l, mx, _ in PARTS if l == les)


def load(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def grade_student(st, errors):
    name = st.get("name") or st.get("folder") or "(בלי שם)"
    scores = st.get("scores", {})
    sub = st.get("submitted", {les: True for les in lessons()})
    res = {les: 0.0 for les in lessons()}
    res.update(bonus=0.0, parts={})
    identical = st.get("identical_screens", [])
    if not isinstance(identical, list) or any(x not in SCREENS for x in identical):
        errors.append("%s: identical_screens צריך להיות רשימה של %s" % (name, ", ".join(SCREENS)))
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
    penalty = RUBRIC.get("identical_penalty", IDENTICAL_PENALTY) * len(identical) + (FOREIGN_FILE_PENALTY if st.get("foreign_file") else 0)
    raw = sum(res[les] for les in lessons()) + res["bonus"] - penalty
    res.update(name=name, folder=st.get("folder", ""), raw=raw, total=max(0, min(MAX_TOTAL, half_up(raw))),
               identical=identical, penalty=penalty,
               copy_flag=flag, review=bool(st.get("teacher_review")), mistakes=list(st.get("mistakes", [])),
               submitted=sub)
    return res


def write_csv(path, rows):
    with open(path, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f)
        w.writerow(["שם", "תיקייה"] + ["שיעור %s (מתוך %s)" % (les[1:], fmt(lesson_max(les))) for les in lessons()] +
                   ["בונוס (עד %s)" % fmt(sum(mx for _, mx, _ in BONUS)), "צילום זהה", "הורדות", "ציון סופי",
                    "חשד להעתקה", "לבדיקת מורה", "טעויות נפוצות"])
        for r in rows:
            w.writerow([r["name"], r["folder"]] + [fmt(r[les]) for les in lessons()] + [fmt(r["bonus"]),
                        " ".join(r["identical"]), fmt(r["penalty"]) if r["penalty"] else "", r["total"],
                        r["copy_flag"], "כן" if r["review"] else "", " ".join(r["mistakes"])])


def write_summary(path, rows):
    totals = [r["total"] for r in rows]
    out = ["# תמונת מצב: שבוע 1, %s" % RUBRIC["title"], ""]
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
    notsub = [r for r in rows if not all(r["submitted"].get(k, True) for k in lessons())]
    out.append("")
    out.append("הגשה חלקית או חסרה: %s" % (", ".join(r["name"] for r in notsub) or "אין"))
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(out) + "\n")


def main(argv):
    global RUBRIC, PARTS, BONUS, SCREENS
    argv = list(argv)
    if "--lesson" in argv:
        i = argv.index("--lesson")
        key = argv[i + 1] if i + 1 < len(argv) else ""
        if key not in RUBRICS:
            print("--lesson צריך להיות אחד מ-%s" % ", ".join(RUBRICS))
            return 1
        RUBRIC = RUBRICS[key]
        PARTS, BONUS, SCREENS = RUBRIC["parts"], RUBRIC["bonus"], RUBRIC["screens"]
        del argv[i:i + 2]
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
