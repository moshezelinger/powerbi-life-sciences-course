#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
check_week.py: בדיקת סגנון ותבנית לחומרי שבוע בקורס Power BI.

מה הוא בודק (לפי "מדריך פיתוח שבוע חדש", פרקים 3 ו-7):
  E  שגיאה, חייבים לתקן לפני מסירה
  W  אזהרה, קוראים ומחליטים

  E-dash      מקף ארוך או קצר (U+2014, U+2013), או "--" בתוך טקסט
  E-dot       נקודה אמצעית (·), חוץ משורת התאריך והמחבר במסמכי Docs
  E-term      מונח שהוחלף במונחון הקבוע (למשל "לכידות לסבב")
  E-click     "לחצו X" בלי "על" לפני שם של כפתור
  E-imper     ציווי ביחיד בתחילת משפט ("ודא", "פתח", "בדוק"): לתלמידים "פתחו", למורה "לפתוח" או "פותחים"
  E-gender    פנייה בלשון זכר ("אתה", "תוכל", "שים לב")
  E-id        מזהה צעד או משימה שמופיע פעמיים
  E-min       זמן הכנה שאינו כפולה של 5 דקות
  E-expect    צעד בדוח הלמידה בלי "מה אמור להופיע" (e)
  W-chip      [[כפתור]] שאין לו מיקום בלקט הכפתורים (LOC)
  W-long      צעד ארוך מ-40 מילים: לפצל, או להעביר את ההסבר לתיבה "למה עושים את זה?"
  W-define    מונח שמופיע בשיעור בלי ההגדרה שלו באותו שיעור (מתכון, מאמץ דגימה, ממוצע לכידות בסבב)
  W-times     זמני השיעור (times) לא מסתכמים ב-45 דקות
  W-dash      מקף מוקף ברווחים ( - ), שאינו חלק משם של קובץ או אפליקציה

שימוש:
  python3 check_week.py קובץ [קובץ ...]
  python3 check_week.py --role teacher קובץ    (student, teacher או doc; ברירת המחדל לפי שם הקובץ)

קטע שמכיל דוגמאות מכוונות (למשל טבלת "לפני ואחרי") עוטפים בהערות:
  <!-- check:off --> ... <!-- check:on -->
והסקריפט מדלג עליו.

קוד יציאה 1 אם נמצאה שגיאה. דרוש Python 3 בלבד, בלי ספריות נוספות.
"""
import re
import sys

HEB = "֐-׿"
NOT_HEB_BEFORE = "(?<![" + HEB + "])"
NOT_HEB_AFTER = "(?![" + HEB + "])"

# מונח שהוחלף -> ההחלפה (מונחון קבוע, פרק 3.2 במדריך)
TERMS = [
    (r"לכידות לסבב", "ממוצע לכידות בסבב"),
    (r"כמה חיפשו|שבהם חיפשו|מפחות חיפוש", "מאמץ הדגימה (כמה סבבי לכידה נערכו)"),
    (r"חלק(?:ה|ות)[^.\n\"]{0,12}" + NOT_HEB_BEFORE + r"נבדק|" + NOT_HEB_BEFORE + r"נבדק(?:ה|ו|ת)?" + NOT_HEB_AFTER + r"[^.\n\"]{0,12}חלק",
     "הציבו בחלקה מלכודות / באותו סבב לא הציבו מלכודות בחלקה"),
    (r"מחוץ לפרוטוקול", "נרשמה מחוץ לסבבים הקבועים"),
    (NOT_HEB_BEFORE + r"בהגינות", "בצורה הוגנת"),
    (NOT_HEB_BEFORE + r"(?:עושים|עשו|תעשו) (?:את )?(?:ה)?צעד", "מבצעים ב-Power BI את מה שכתוב בצעד"),
    (r"הגרף בודק", "בודקים בגרף (האדם פועל, לא הכלי)"),
]

IMPERATIVES = ["ודא", "בדוק", "פתח", "שמור", "הקרן", "הדגם", "שאל", "הכן", "העלה", "הורד", "צלם",
               "לחץ", "בחר", "גרור", "הוסף", "סמן", "כתוב", "קרא", "מחק", "סנן", "הפעל"]
IMPER_RE = re.compile(
    r"(?:^|[.!?:]\s+|[\"'>(]\s*|\n\s*(?:[-*]|\d+\.)\s+)(" + "|".join(IMPERATIVES) + r")" + NOT_HEB_AFTER,
    re.M)
GENDER_RE = re.compile(NOT_HEB_BEFORE + r"(אתה|תוכל|תצטרך|תרצה|שים לב)" + NOT_HEB_AFTER)
CLICK_RE = re.compile(NOT_HEB_BEFORE + r"(לחצו|לוחצים|לחץ|ללחוץ)\s+(?!על|פעמיים)(?=[A-Za-z\[])")
SPACED_DASH_OK = re.compile(r"(לתלמיד|למורה) - |- אחרי המשוב|- הכנת|- בחירת|- דוח")
BYLINE_RE = re.compile(r"(\d{4}|\d{1,2}\.\d{1,2}\.\d{4}) · @")


def role_of(path, forced):
    if forced:
        return forced
    p = path.lower()
    if any(k in p for k in ("journey", "teacher", "למורה", "מדריך", "guide", "outline", "מתווה")):
        return "teacher"
    if any(k in p for k in ("student", "לתלמיד", "checklist", "צ'קליסט")):
        return "student"
    return "doc"


def line_of(text, pos):
    return text.count("\n", 0, pos) + 1


def snippet(text, pos, width=36):
    a = max(0, pos - width)
    b = min(len(text), pos + width)
    return text[a:b].replace("\n", " ").strip()


def block(text, start_pat):
    """מחזיר את הבלוק של מערך או אובייקט שמתחיל בתבנית, לפי איזון סוגריים (מתעלם ממחרוזות)."""
    m = re.search(start_pat, text)
    if not m:
        return None, -1
    i = text.find("[", m.start()) if "[" in start_pat else text.find("{", m.start())
    open_c = text[i]
    close_c = "]" if open_c == "[" else "}"
    depth, j, in_str, esc = 0, i, None, False
    while j < len(text):
        c = text[j]
        if in_str:
            if esc:
                esc = False
            elif c == "\\":
                esc = True
            elif c == in_str:
                in_str = None
        else:
            if c in "\"'":
                in_str = c
            elif c == open_c:
                depth += 1
            elif c == close_c:
                depth -= 1
                if depth == 0:
                    return text[i:j + 1], i
        j += 1
    return None, -1


def lesson_sections(text, is_app):
    """מחלק לשיעורים: באפליקציות לפי '{ n: N', במסמכים לפי כותרות שמתחילות ב'שיעור' או 'מצגת'."""
    if is_app:
        marks = [m.start() for m in re.finditer(r"\{ n: \d+,", text)]
    else:
        marks = [m.start() for m in re.finditer(r"^#{2,4} (?:שיעור|מצגת) \d", text, re.M)]
    marks.append(len(text))
    return [(marks[k], text[marks[k]:marks[k + 1]]) for k in range(len(marks) - 1)]


def check(path, forced_role=None):
    text = open(path, encoding="utf-8").read()
    # קטעים שמסומנים לדילוג מוחלפים ברווחים, כדי שמספרי השורות יישארו נכונים
    text = re.sub(r"<!-- check:off.*?<!-- check:on -->",
                  lambda m: re.sub(r"[^\n]", " ", m.group(0)), text, flags=re.S)
    role = role_of(path, forced_role)
    out = []

    def add(code, pos, msg):
        out.append((code, line_of(text, pos), msg, snippet(text, pos)))

    # פיסוק
    for m in re.finditer("[–—]|(?<=[" + HEB + r"\w]) -- (?=[" + HEB + r"\w])", text):
        add("E-dash", m.start(), "מקף ארוך או קצר: להחליף בפסיק, בנקודה, בנקודתיים או בסוגריים")
    for m in re.finditer("·", text):
        line_start = text.rfind("\n", 0, m.start()) + 1
        line_end = text.find("\n", m.start())
        if not BYLINE_RE.search(text[line_start:line_end if line_end > 0 else None]):
            add("E-dot", m.start(), "נקודה אמצעית: להחליף בפסיק")
    for m in re.finditer(r"(?<=[" + HEB + r"]) - (?=[" + HEB + r"])", text):
        ctx = text[max(0, m.start() - 12):m.end() + 14]
        if not SPACED_DASH_OK.search(ctx):
            add("W-dash", m.start(), "מקף מוקף ברווחים: אם זה לא שם של קובץ, להחליף בפסיק או בנקודתיים")

    # מונחים, לחיצה, פנייה
    for pat, rep in TERMS:
        for m in re.finditer(pat, text):
            add("E-term", m.start(), "מונח שהוחלף. במקומו: " + rep)
    for m in CLICK_RE.finditer(text):
        add("E-click", m.start(), "לפני שם של כפתור כותבים 'לחצו על'")
    for m in IMPER_RE.finditer(text):
        word = m.group(1)
        fix = "לתלמידים: ציווי ברבים (" + word + "ו)" if role == "student" else "למורה: שם פועל או הווה ברבים"
        add("E-imper", m.start(1), "ציווי ביחיד '" + word + "'. " + fix)
    for m in GENDER_RE.finditer(text):
        add("E-gender", m.start(), "פנייה בלשון זכר: לנסח בשם פועל, ברבים או בניסוח כללי")

    # מבנה האפליקציות
    lessons, l_at = block(text, r"var LESSONS = \[")
    stations, s_at = block(text, r"var STATIONS = \[")
    loc, _ = block(text, r"var LOC = \{")
    paste, _ = block(text, r"var PASTE = \{")
    loc_keys = set()
    for b in (loc, paste):
        if b:
            loc_keys |= set(re.findall(r'"((?:[^"\\]|\\.)+)"\s*:', b))

    if lessons:
        ids = re.findall(r'\bid: "(l\d+-(?:q)?\d+)"', lessons)
        for dup in sorted({i for i in ids if ids.count(i) > 1}):
            add("E-id", l_at + lessons.find('"' + dup + '"'), "מזהה כפול: " + dup)
        for m in re.finditer(r'\{ id: "(l\d+-\d+)"(.*?)\}(?=,\s*\{ id:|\s*\])', lessons, re.S):
            body = m.group(2)
            if not re.search(r'\be: "', body):
                add("E-expect", l_at + m.start(), "לצעד " + m.group(1) + " אין 'מה אמור להופיע' (e)")
            t = re.search(r'\bt: "((?:[^"\\]|\\.)*)"', body)
            if t and len(re.sub(r"\[\[|\]\]|\{\{|\}\}", "", t.group(1)).split()) > 40:
                add("W-long", l_at + m.start(), "צעד " + m.group(1) + " ארוך מ-40 מילים")

    if stations:
        items = re.findall(r'\["(s\d+-[\w]+)",\s*"(?:[^"\\]|\\.)*",\s*(\d+)(?:,\s*"after")?\]', stations)
        ids = [i for i, _ in items]
        for dup in sorted({i for i in ids if ids.count(i) > 1}):
            add("E-id", s_at + stations.find('"' + dup + '"'), "מזהה משימה כפול: " + dup)
        for i, mins in items:
            if int(mins) < 5 or int(mins) % 5:
                add("E-min", s_at + stations.find('"' + i + '"'), "משימה " + i + ": " + mins + " דקות. זמנים בבלוקים של 5")
        for m in re.finditer(r"times: \[(.*?)\]\],", stations):
            total = sum(int(x) for x in re.findall(r",\s*(\d+),", m.group(1)))
            if total != 45:
                add("W-times", s_at + m.start(), "זמני השיעור מסתכמים ב-" + str(total) + " דקות, לא 45")

    for src, at in ((lessons, l_at), (stations, s_at)):
        if src and loc_keys:
            for m in re.finditer(r'\[\[([^\[\]"\n]+?)\]\]', src):
                if m.group(1) not in loc_keys:
                    add("W-chip", at + m.start(), "לכפתור '" + m.group(1) + "' אין מיקום ב-LOC")

    # הגדרות בכל שיעור
    for at, sec in lesson_sections(text, path.lower().endswith((".html", ".htm", ".js"))):
        if "מתכון" in sec and "Applied Steps" not in sec:
            add("W-define", at + sec.find("מתכון"), "'מתכון' בלי 'רשימת הצעדים (Applied Steps)' באותו שיעור")
        if re.search(r"מאמץ (?:ה)?דגימה", sec) and "סבבי לכידה" not in sec and "סבבי הלכידה" not in sec:
            add("W-define", at + re.search(r"מאמץ (?:ה)?דגימה", sec).start(), "'מאמץ דגימה' בלי ההגדרה (כמה סבבי לכידה נערכו)")
        if "ממוצע לכידות בסבב" in sec and "חלקי" not in sec:
            add("W-define", at + sec.find("ממוצע לכידות בסבב"), "'ממוצע לכידות בסבב' בלי ההגדרה (לכידות בשנה, חלקי סבבים)")

    summary = None
    if stations:
        per = {}
        for m in re.finditer(r'\["s(\d+)-[\w]+",\s*"(?:[^"\\]|\\.)*",\s*(\d+)\]', stations):
            per[int(m.group(1))] = per.get(int(m.group(1)), 0) + int(m.group(2))
        run, parts = 0, []
        for k in sorted(per):
            run += per[k]
            parts.append("תחנה %d: %d דק' (מצטבר %d:%02d)" % (k, per[k], run // 60, run % 60))
        summary = parts
    return role, out, summary


def main(argv):
    forced = None
    if "--role" in argv:
        k = argv.index("--role")
        forced = argv[k + 1]
        argv = argv[:k] + argv[k + 2:]
    files = argv[1:]
    if not files:
        print(__doc__)
        return 2
    errors = 0
    for path in files:
        role, out, summary = check(path, forced)
        out.sort(key=lambda r: (r[1], r[0]))
        e = sum(1 for r in out if r[0].startswith("E"))
        w = len(out) - e
        errors += e
        print("== %s (%s): %d שגיאות, %d אזהרות" % (path, role, e, w))
        for code, ln, msg, snip in out:
            print("  %-9s שורה %-5d %s\n            ...%s..." % (code, ln, msg, snip))
        if summary:
            print("  זמני הכנה: " + " | ".join(summary))
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
