#!/usr/bin/env python3
"""
Convert a grading workbook (the Excel structure described in
references/grading-workbook-structure.md) to whole-number scoring.

Every score, in every part, becomes an integer. Partial scores are rounded to
the nearest integer, 0.5 rounds up, and a part that was not fully correct never
rounds up to full marks (it drops one point instead). A score equal to the
part's maximum stays the maximum.

What it changes:
  * score cells in the grading sheets (header ends with "(N)", excluding
    totals, final grade and bonus caps)
  * the "נקודות" and "מתוך" columns of the detailed-feedback sheet, and any
    "X מתוך Y" fragments in its explanation text
  * weighted-grade and average formulas in the summary sheet: the final ROUND
    digit becomes 0
  * a one-line rounding note below the summary table

Parts whose maximum is not an integer (for example 2.5) must be remapped on
purpose with --remap, so the new maximum is a conscious rubric decision.

Usage:
  round_grading_workbook.py INPUT.xlsx OUTPUT.xlsx [--remap "Choose Columns:3" ...]
  round_grading_workbook.py --selftest

Requires openpyxl. Formulas are kept as formulas; open the result in Excel or
LibreOffice to recalculate before reading the grades.
"""
import argparse
import re
import sys

NOTE = ('כל הציונים שלמים: ניקוד חלקי מעגלים למספר שלם (0.5 עולה), '
        'בלי להגיע לניקוד מלא בעיגול. את הציון המשוקלל מעגלים רק בסוף.')
FRACTION = re.compile(r'(\d+(?:\.\d+)?) מתוך (\d+(?:\.\d+)?)')
MAX_IN_HEADER = re.compile(r'\(([\d.]+)\)\s*$')


def round_part(score, old_max, new_max=None):
    """Whole-number score for one part. See the module docstring for the rule."""
    new_max = old_max if new_max is None else new_max
    if not isinstance(score, (int, float)):
        return score
    if score >= old_max:
        return int(round(new_max))
    value = int(score / old_max * new_max + 0.5 + 1e-9)
    if value >= new_max:
        value = int(new_max) - 1
    return value


def is_total_header(text):
    return 'סה"כ' in text or 'ציון סופי' in text


def find_header_row(ws):
    for row in range(1, 4):
        if ws.cell(row, 1).value == 'שם התלמיד':
            return row
    return None


def convert_scoring_sheet(ws, header_row, remaps):
    changed = 0
    for col in range(1, ws.max_column + 1):
        header = ws.cell(header_row, col).value
        if not isinstance(header, str) or is_total_header(header):
            continue
        match = MAX_IN_HEADER.search(header)
        if not match:
            continue
        old_max = float(match.group(1))
        new_max = old_max
        if old_max != int(old_max):
            hit = [m for key, m in remaps.items() if key in header]
            if not hit:
                raise SystemExit('Non-integer maximum %g in "%s": add --remap "<part name>:<new max>"'
                                 % (old_max, header))
            new_max = hit[0]
            ws.cell(header_row, col).value = header.replace('(%g)' % old_max, '(%d)' % new_max)
        for row in range(header_row + 1, ws.max_row + 1):
            value = ws.cell(row, col).value
            if isinstance(value, (int, float)):
                new_value = round_part(value, old_max, new_max)
                changed += new_value != value
                ws.cell(row, col).value = new_value
    return changed


def convert_feedback_sheet(ws):
    def fraction(m):
        old_max = float(m.group(2))
        return '%d מתוך %d' % (round_part(float(m.group(1)), old_max), old_max)

    for row in range(2, ws.max_row + 1):
        points, out_of, text = (ws.cell(row, c).value for c in (3, 4, 5))
        if isinstance(points, (int, float)) and isinstance(out_of, (int, float)):
            ws.cell(row, 3).value = round_part(points, out_of)
            ws.cell(row, 4).value = int(out_of)
        if isinstance(text, str):
            ws.cell(row, 5).value = FRACTION.sub(fraction, text)


def convert_summary_sheet(ws):
    for row in range(2, ws.max_row + 1):
        for col in range(2, ws.max_column + 1):
            value = ws.cell(row, col).value
            if not (isinstance(value, str) and value.startswith('=')):
                continue
            if value.endswith(',1))'):
                ws.cell(row, col).value = value[:-4] + ',0))'
            elif value.endswith(',1)'):
                ws.cell(row, col).value = value[:-3] + ',0)'
    for row in range(2, ws.max_row + 2):
        if ws.cell(row, 1).value is None and ws.cell(row - 1, 1).value is None and row > 3:
            ws.cell(row, 1).value = NOTE
            ws.cell(row, 1)._style = ws.cell(row - 2, 1)._style
            break


def convert(src, dst, remaps):
    import openpyxl
    wb = openpyxl.load_workbook(src)
    changed = 0
    for ws in wb:
        header_row = find_header_row(ws)
        title = ws.cell(1, 2).value
        if isinstance(title, str) and title.startswith('ציון תרגילים'):
            convert_summary_sheet(ws)
        elif header_row and ws.cell(header_row, 2).value != 'חלק':
            changed += convert_scoring_sheet(ws, header_row, remaps)
        elif ws.cell(1, 3).value == 'נקודות' and ws.cell(1, 4).value == 'מתוך':
            convert_feedback_sheet(ws)
    wb.save(dst)
    return changed


def selftest():
    cases = [  # (score, old max, new max, expected)
        (5.5, 6, None, 5), (3.5, 6, None, 4), (4.5, 7, None, 5), (4.5, 5, None, 4),
        (12.5, 14, None, 13), (11.5, 18, None, 12), (6, 6, None, 6), (0, 6, None, 0),
        (2.5, 2.5, 3, 3), (1.5, 2.5, 3, 2), (2.5, 2.5, 2, 2), (1.5, 2.5, 2, 1),
        (0.5, 3, None, 1),
    ]
    bad = [c for c in cases if round_part(*c[:3]) != c[3]]
    for c in bad:
        print('FAIL', c, round_part(*c[:3]))
    print('selftest:', 'FAILED' if bad else 'ok (%d cases)' % len(cases))
    return 1 if bad else 0


def main():
    parser = argparse.ArgumentParser(description=__doc__.split('\n\n')[0])
    parser.add_argument('input', nargs='?')
    parser.add_argument('output', nargs='?')
    parser.add_argument('--remap', action='append', default=[],
                        metavar='PART:MAX', help='new integer maximum for a part whose old maximum is not an integer')
    parser.add_argument('--selftest', action='store_true')
    args = parser.parse_args()
    if args.selftest:
        return selftest()
    if not (args.input and args.output):
        parser.error('INPUT and OUTPUT are required')
    remaps = {k: int(v) for k, v in (r.rsplit(':', 1) for r in args.remap)}
    print('cells changed in grading sheets:', convert(args.input, args.output, remaps))
    return 0


if __name__ == '__main__':
    sys.exit(main())
