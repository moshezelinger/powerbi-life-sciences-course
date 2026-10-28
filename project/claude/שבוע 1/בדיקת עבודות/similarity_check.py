#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
similarity_check.py: איתור דמיון חשוד בין הגשות של תלמידים (טקסט וצילומי מסך).

מה הוא בודק:
  1. טקסט: רצפי מילים זהים בין שני תלמידים, אחרי שמסירים שורות תבנית וצירופים שמופיעים אצל הרבה תלמידים
     (למשל ניסוח מהרמזים באפליקציה). מספרים נכונים זהים (15,120 או 14,492) לא נחשבים דמיון.
  2. צילומי מסך: קובצי תמונה זהים בתוכן (MD5) אצל תלמידים שונים, כולל תמונות שהודבקו בתוך קובצי docx.
     צילום שהוקטן או הוגדל לא מזוהה כאן, ולכן משווים גם בעין.

הוא מסמן חשד, ולא קובע העתקה. ההחלטה בידי המורה. בכיתה עובדים בזוגות בחלק מהצעדים.

מבנה התיקייה: תיקייה לכל תלמיד (כמו ב-Download all submissions של Moodle), ובה onlinetext.html או
קובצי txt, md, html, docx וקובצי תמונה. בלי תיקיות משנה, מקבצים לפי שם הקובץ עד "_assignsubmission".

שימוש:
  python3 similarity_check.py תיקיית_ההגשות [תיקיית_פלט]
כותב similarity_report.md ו-similarity_report.json. Python 3 בלבד, בלי ספריות נוספות.
"""
import difflib
import hashlib
import html
import json
import os
import re
import sys
import zipfile
from html.parser import HTMLParser

IMG_EXT = {".png", ".jpg", ".jpeg", ".gif", ".bmp", ".webp"}
TEXT_EXT = {".txt", ".md", ".html", ".htm", ".docx"}
SKIP_NAMES = {"similarity_report.md", "similarity_report.json", "grades.csv", "class_summary.md", "scores.json"}
MIN_WORDS = 25          # פחות מזה: קצר מדי להשוואה
SHINGLE = 5             # אורך צירוף מילים
STRONG_RUN, MEDIUM_RUN = 15, 8
STRONG_SHARED, MEDIUM_SHARED = 10, 3

NIQQUD = re.compile("[֑-ׇ]")
NONWORD = re.compile(r"[^\w֐-׿]+", re.U)
MOODLE_NAME = re.compile(r"^(.*?)_\d+_assignsubmission.*$")


class _Text(HTMLParser):
    def __init__(self):
        super().__init__()
        self.parts = []

    def handle_data(self, d):
        self.parts.append(d)

    def handle_starttag(self, tag, attrs):
        if tag in ("br", "p", "div", "li", "tr", "h1", "h2", "h3"):
            self.parts.append("\n")


def read_text(path):
    ext = os.path.splitext(path)[1].lower()
    try:
        if ext == ".docx":
            with zipfile.ZipFile(path) as z:
                xml = z.read("word/document.xml").decode("utf-8", "ignore")
            xml = re.sub(r"</w:p>", "\n", xml)
            return html.unescape(re.sub(r"<[^>]+>", "", xml))
        raw = open(path, encoding="utf-8", errors="ignore").read()
        if ext in (".html", ".htm"):
            p = _Text()
            p.feed(raw)
            return html.unescape("".join(p.parts))
        return raw
    except Exception:
        return ""


def docx_images(path):
    """התמונות שהודבקו בתוך קובץ docx, כזוגות (נתיב הקובץ, שם התמונה בתוכו)."""
    try:
        with zipfile.ZipFile(path) as z:
            return [(path, m) for m in z.namelist()
                    if m.startswith("word/media/") and os.path.splitext(m)[1].lower() in IMG_EXT]
    except Exception:
        return []


def image_bytes(img):
    if isinstance(img, tuple):
        with zipfile.ZipFile(img[0]) as z:
            return z.read(img[1])
    with open(img, "rb") as f:
        return f.read()


def image_label(root, img):
    if isinstance(img, tuple):
        return "%s:%s" % (os.path.relpath(img[0], root), os.path.basename(img[1]))
    return os.path.relpath(img, root)


def norm_line(line):
    return " ".join(NONWORD.sub(" ", NIQQUD.sub("", line)).lower().split())


def student_key(root, path):
    rel = os.path.relpath(path, root)
    parts = rel.split(os.sep)
    if len(parts) > 1:
        top = parts[0]
    else:
        top = os.path.splitext(parts[0])[0]
    m = MOODLE_NAME.match(top)
    return (m.group(1) if m else top).strip()


def collect(root, outdir):
    students = {}
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if not d.startswith(".") and os.path.abspath(os.path.join(dirpath, d)) != os.path.abspath(outdir)]
        for fn in filenames:
            if fn in SKIP_NAMES or fn.startswith("."):
                continue
            path = os.path.join(dirpath, fn)
            ext = os.path.splitext(fn)[1].lower()
            if ext not in IMG_EXT and ext not in TEXT_EXT:
                continue
            if ext in TEXT_EXT and dirpath == root and fn.lower().endswith(".md") and "מחוון" in fn:
                continue
            key = student_key(root, path)
            s = students.setdefault(key, {"text": [], "images": [], "unread": []})
            if ext in IMG_EXT:
                s["images"].append(path)
            else:
                t = read_text(path)
                (s["text"] if t.strip() else s["unread"]).append((path, t))
                if ext == ".docx":
                    s["images"] += docx_images(path)
    return students


def words_of(lines):
    return [w for l in lines for w in l.split()]


def main(argv):
    if len(argv) < 2:
        print(__doc__)
        return 1
    root = os.path.abspath(argv[1])
    outdir = os.path.abspath(argv[2]) if len(argv) > 2 else root
    os.makedirs(outdir, exist_ok=True)
    students = collect(root, outdir)
    names = sorted(students)
    n = len(names)

    # שורות מנורמלות לכל תלמיד, בלי שורות תבנית (שורות שמופיעות אצל חצי מהכיתה או יותר)
    lines = {k: [norm_line(l) for t in (x[1] for x in students[k]["text"]) for l in t.splitlines()] for k in names}
    lines = {k: [l for l in v if l] for k, v in lines.items()}
    line_df = {}
    for k in names:
        for l in set(lines[k]):
            line_df[l] = line_df.get(l, 0) + 1
    tmpl_cut = max(3, (n + 1) // 2)
    body = {k: [l for l in lines[k] if line_df[l] < tmpl_cut] for k in names}
    toks = {k: words_of(body[k]) for k in names}

    # צירופי מילים נפוצים (כאלה שמופיעים אצל הרבה תלמידים) לא נחשבים דמיון
    sh = {k: {tuple(toks[k][i:i + SHINGLE]) for i in range(max(0, len(toks[k]) - SHINGLE + 1))} for k in names}
    sh_df = {}
    for k in names:
        for s in sh[k]:
            sh_df[s] = sh_df.get(s, 0) + 1
    common_cut = max(3, (n + 3) // 4)
    rare = {k: {s for s in sh[k] if sh_df[s] < common_cut} for k in names}

    pairs, short = [], [k for k in names if len(toks[k]) < MIN_WORDS]
    for i in range(n):
        for j in range(i + 1, n):
            a, b = names[i], names[j]
            if len(toks[a]) < MIN_WORDS or len(toks[b]) < MIN_WORDS:
                continue
            shared = len(rare[a] & rare[b])
            sm = difflib.SequenceMatcher(None, toks[a], toks[b], autojunk=False)
            m = sm.find_longest_match(0, len(toks[a]), 0, len(toks[b]))
            run = m.size
            if shared >= MEDIUM_SHARED or run >= MEDIUM_RUN:
                level = "strong" if (run >= STRONG_RUN or shared >= STRONG_SHARED) else "medium"
                pairs.append({"a": a, "b": b, "level": level, "longest_run_words": run, "shared_rare_phrases": shared,
                              "passage": " ".join(toks[a][m.a:m.a + run])})

    # צילומי מסך זהים בתוכן
    by_hash = {}
    for k in names:
        for p in students[k]["images"]:
            h = hashlib.md5(image_bytes(p)).hexdigest()
            by_hash.setdefault(h, []).append((k, image_label(root, p)))
    dup_images = [{"md5": h, "files": v} for h, v in by_hash.items() if len({k for k, _ in v}) > 1]

    pairs.sort(key=lambda p: (p["level"] != "strong", -p["longest_run_words"], -p["shared_rare_phrases"]))
    report = {"students": n, "pairs": pairs, "identical_screenshots": dup_images, "too_short_to_compare": short,
              "no_text_found": [k for k in names if not students[k]["text"]],
              "no_image_found": [k for k in names if not students[k]["images"]]}
    with open(os.path.join(outdir, "similarity_report.json"), "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    out = ["# דוח דמיון בין הגשות", "",
           "הדוח מסמן חשד בלבד. בכיתה עובדים בזוגות בחלק מהצעדים, ולכן ההחלטה למורה.", "",
           "תלמידים שנבדקו: %d" % n, ""]
    out += ["## צילומי מסך זהים", ""]
    if dup_images:
        for d in dup_images:
            out.append("- אותו קובץ בתוכן: " + "; ".join("%s (%s)" % (k, f) for k, f in d["files"]))
    else:
        out.append("לא נמצאו.")
    out += ["", "## טקסט דומה", ""]
    if pairs:
        out += ["| רמה | תלמיד א | תלמיד ב | הרצף הארוך ביותר (מילים) | צירופים נדירים משותפים |", "| --- | --- | --- | --- | --- |"]
        for p in pairs:
            out.append("| %s | %s | %s | %d | %d |" % ("חזק" if p["level"] == "strong" else "בינוני", p["a"], p["b"], p["longest_run_words"], p["shared_rare_phrases"]))
        out += ["", "### הקטעים", ""]
        for p in pairs:
            out.append("- %s ו-%s: «%s»" % (p["a"], p["b"], p["passage"]))
    else:
        out.append("לא נמצאו זוגות חשודים.")
    if short:
        out += ["", "## קצר מדי להשוואה (פחות מ-%d מילים אחרי הסרת תבנית)" % MIN_WORDS, "", ", ".join(short)]
    if report["no_text_found"]:
        out += ["", "## לא נמצא טקסט שנקרא", "", ", ".join(report["no_text_found"])]
    if report["no_image_found"]:
        out += ["", "## לא נמצא קובץ תמונה", "", ", ".join(report["no_image_found"])]
    with open(os.path.join(outdir, "similarity_report.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(out) + "\n")
    print("נבדקו %d תלמידים: %d זוגות חשודים, %d קובצי תמונה זהים. נכתבו similarity_report.md ו-similarity_report.json ב-%s"
          % (n, len(pairs), len(dup_images), outdir))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
