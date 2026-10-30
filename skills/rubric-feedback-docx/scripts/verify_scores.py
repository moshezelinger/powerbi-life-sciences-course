"""
verify_scores.py: check that the scores written in the comments of each Word file add up.

Usage:
    python verify_scores.py <folder or .docx> [<folder or .docx> ...] [--excel grades.json]

Runs on generated files and, more importantly, on files the teacher edited by hand.
For every file it reads the comments by "משה זלינגר" (or any author) and checks:

  1. every head of the form "... (X מתוך Y)" has 0 <= X <= Y
  2. the grade comment ("ציון ...: N מתוך 100") agrees with its own breakdown:
        N == written + screenshots + bonus - deductions        (rounded, clamped 0..100)
  3. written     == sum of the question comments + completeness ("שלמות ההגשה")
     screenshots == sum of the screenshot comments ("צילום")
     (when a part has no comments in this file, that check is skipped)
  4. optional: N matches the grade in a JSON {student name: final} exported from the grade workbook

Exit code 1 if any file fails, so it can gate the delivery step.
"""
import glob, json, os, re, sys
import docx

PTS = re.compile(r"\((\d+)\s*מתוך\s*(\d+)\)")
GRADE = re.compile(r"ציון[^:\n]*:\s*(\d+)\s*מתוך\s*100")
FIELD = {
    "written": re.compile(r"חלק כתוב:\s*(\d+)\s*מתוך"),
    "shots": re.compile(r"צילומי מסך:\s*(\d+)\s*מתוך"),
    "bonus": re.compile(r"בונוס:\s*(\d+)"),
    "ded": re.compile(r"הורדות:\s*(\d+)"),
}
COMPLETE = re.compile(r"שלמות ההגשה:([^\n]*)")


def check_file(paths, expected=None):
    # one student may have several files in the same folder: their comments are checked together
    comments = [c.text for p in paths for c in docx.Document(p).comments]
    problems, items = [], []
    grade_c = next((t for t in comments if GRADE.search(t.split("\n")[0])), None)
    for t in comments:
        if t is grade_c:
            continue
        head = t.split("\n")[0]
        m = PTS.search(head)
        if not m:
            continue
        x, y = int(m.group(1)), int(m.group(2))
        if not 0 <= x <= y:
            problems.append(f"ניקוד לא תקין: {head}")
        items.append((head, x, y))
    if grade_c is None:
        return ["לא נמצאה הערת ציון בראש המסמך"] if items else [], None
    final = int(GRADE.search(grade_c).group(1))
    f = {k: (int(r.search(grade_c).group(1)) if r.search(grade_c) else None) for k, r in FIELD.items()}
    if f["written"] is not None and f["shots"] is not None:
        calc = max(0, min(100, f["written"] + f["shots"] + (f["bonus"] or 0) - (f["ded"] or 0)))
        if calc != final:
            problems.append(f"הציון בכותרת {final}, אבל הפירוט נותן {calc} "
                            f"(כתוב {f['written']} + צילומים {f['shots']} + בונוס {f['bonus'] or 0} - הורדות {f['ded'] or 0})")
    shots = [x for h, x, y in items if "צילום" in h]
    quest = [x for h, x, y in items if "צילום" not in h and "בונוס" not in h]
    bonus = [x for h, x, y in items if "בונוס" in h]
    if shots and f["shots"] is not None and sum(shots) != f["shots"]:
        problems.append(f"סכום הערות הצילום {sum(shots)}, אבל בפירוט כתוב צילומי מסך {f['shots']}")
    comp = COMPLETE.search(grade_c)
    comp_pts = sum(int(a) for a in re.findall(r"(\d+)\s*מתוך\s*\d+", comp.group(1))) if comp else 0
    if quest and f["written"] is not None and sum(quest) + comp_pts != f["written"]:
        problems.append(f"סכום הערות השאלות {sum(quest)} ועוד שלמות ההגשה {comp_pts} = {sum(quest) + comp_pts}, "
                        f"אבל בפירוט כתוב חלק כתוב {f['written']}")
    if bonus and f["bonus"] is not None and sum(bonus) != f["bonus"]:
        problems.append(f"הערת הבונוס {sum(bonus)}, אבל בפירוט כתוב בונוס {f['bonus']}")
    if expected is not None and expected != final:
        problems.append(f"בקובץ הציונים {expected}, ובהערה {final}")
    return problems, final


def main(args):
    exp = {}
    if "--excel" in args:
        i = args.index("--excel"); exp = json.load(open(args[i + 1], encoding="utf-8")); args = args[:i] + args[i + 2:]
    files = []
    for a in args:          # os.walk, not glob: folder names from Moodle contain [brackets]
        if os.path.isdir(a):
            files += sorted(os.path.join(r, n) for r, _, ns in os.walk(a) for n in ns
                            if n.endswith(".docx") and not n.startswith("~$"))
        else:
            files.append(a)
    groups = {}
    for p in files:
        groups.setdefault(os.path.dirname(p), []).append(p)
    bad = 0
    for folder, paths in groups.items():
        student = next((s for s in exp if s in folder), None)
        probs, final = check_file(paths, exp.get(student) if student else None)
        name = os.path.basename(folder) + " / " + ", ".join(os.path.basename(p) for p in paths)
        if probs:
            bad += 1
            print(f"✗ {name}")
            for x in probs:
                print("    ", x)
        else:
            print(f"✓ {name}" + (f"  ({final})" if final is not None else ""))
    print(f"\n{len(groups) - bad} תקינים, {bad} דורשים בדיקה")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
