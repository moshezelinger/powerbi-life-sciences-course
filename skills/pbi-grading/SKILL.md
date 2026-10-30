---
name: "pbi-grading"
description: "Use when building a rubric (מחוון) or grading student work for Moshe's high-school Power BI course: new exercise rubric, grading workbook for a student group, partial scores, point deductions for copying, weighted grades, or converting an existing rubric or grading workbook to whole numbers."
---

# Rubrics and grading with whole numbers

This skill keeps every rubric and every grade in the course on whole numbers, in the same Excel structure each time, so grading a new week gives results very similar to week 1. It came from the week 1 rubric and the grading of two student groups, and Moshe approved the method on 30.10.2026.

All text for students and teacher is Hebrew. Follow Moshe's writing preferences: native Hebrew, verbs over nouns, no em or en dashes.

## The rule

- Every part of the rubric is worth a whole number of points, and every partial score is a whole number. Never 2.5, 5.4 or 0.5, in any part, not only in the final grade.
- Partial scores: compute from the scale (100%, 90%, 60%, 30%, 0%), round to the nearest integer, 0.5 rounds up. If rounding would give full marks to an answer that is not fully correct, give one point less.
- A part split into components gets whole points per component, the hard one gets more (5 = 1 + 1 + 3, not 1.5 + 1.5 + 2).
- A score written in the rubric overrides the formula, as long as it is whole.
- The weighted grade is rounded once, at the end.

## Sources of truth

Read these before building a rubric or grading:

1. `references/rubric-structure.md`: sheets of the rubric, the scale, fixed rules, rounding table, weights.
2. `references/grading-workbook-structure.md`: sheets, columns, formulas and filling rules of the grading workbook.
3. `references/week1-rubric-integers.md`: the week 1 rubric in whole numbers, as the model to copy.
4. `scripts/round_grading_workbook.py`: converts an existing workbook to whole numbers and reproduces the approved result.

If a rule here conflicts with what Moshe says in the chat, Moshe wins. If it conflicts with `project/claude/מערכת/מדריך פיתוח שבוע חדש.md`, the guide wins on lesson content and this skill wins on scoring.

## Procedure: new rubric

1. Read the week's lesson material and the answer key. Every expected number comes from the class data files, computed in code.
2. Split the points per lesson: written part 70, screenshots 30, bonus up to 5. Each lesson in a two-lesson exercise is worth 50. Check that every part is a whole number and that the parts sum to 100.
3. Write the rubric sheets in the order of `rubric-structure.md`: exercise sheet, rules, deductions and decisions, key. Put the full score of each component in brackets in the "התשובה המלאה" column, and every wrong case with its score in the partial column.
4. Get Moshe's approval of the points before grading. Show the table, not the whole workbook.

## Procedure: grading a group

1. Copy the previous grading workbook of the same exercise type, clear the data rows, and keep the structure and formulas. Never rebuild the layout from scratch.
2. Fill scores per part from the rubric. Write the explanation per part in the feedback sheet, and make it match the score cell.
3. Fill the teacher sheet: identical screenshots, another student's file name, similar text, doubts decided in the student's favor. Similar text never lowers a grade.
4. Recalculate (Excel or LibreOffice) and check: no fractions in score columns, no #DIV/0!, final grade 0 to 100, the weighted grade matches (2 x exercises 1-2 + exercise 3) / 3.
5. Report to Moshe what changed against the rubric and which doubts were decided up, in short.

## Converting an existing workbook

```bash
python3 skills/pbi-grading/scripts/round_grading_workbook.py INPUT.xlsx OUTPUT.xlsx
python3 skills/pbi-grading/scripts/round_grading_workbook.py --selftest
```

A part whose maximum is not whole (for example 2.5) needs `--remap "Choose Columns:3"`, so the new maximum is a conscious rubric decision. The script keeps formulas, so recalculate before reading grades. It was verified against both week 1 groups: the output matches the approved files cell by cell.

## Rules that always hold

- Do not change a decision Moshe already approved (cancelled part, who got full marks, the weight between exercises). Propose it and wait.
- Do not invent scores. If an answer is not readable, give 60% of the part and mark it for the teacher.
- When the integer rule changes a student's final grade by one point or more, tell Moshe which students and why.
- Keep the rubric and the grading workbook in the same structure. If a new week needs another column or sheet, propose it first, then update both reference files.
