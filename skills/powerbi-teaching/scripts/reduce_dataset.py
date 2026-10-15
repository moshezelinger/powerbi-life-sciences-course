#!/usr/bin/env python3
"""
Reduce a dataset to classroom scale and clean it for use in a lesson.

A 50,000-row CSV cannot be reasoned about in a 45-minute class. This script cuts
it down to something students can hold in their heads, and writes UTF-8 with BOM
so Hebrew labels survive in Excel and Power BI.

Usage:
  reduce_dataset.py INPUT.csv OUTPUT.csv [options]

Options:
  --max-rows N          Keep at most N rows (after any filtering/aggregation).
  --columns A,B,C       Keep only these columns (by name).
  --filter "COL=VALUE"  Keep only rows where COL equals VALUE (repeatable).
  --group-by COL        Aggregate: group by COL...
  --agg COL:FUNC        ...and aggregate another column with FUNC
                        (sum, mean, count, min, max). Repeatable.
  --top COL:N           After everything, keep the N rows with the largest COL.
  --round K             Round numeric columns to K decimals (default: leave as is).

Examples:
  # 12 clean rows for a bar chart, biggest first
  reduce_dataset.py world.csv class.csv --columns Country,CO2 --top CO2:12 --round 1

  # average score per group, a handful of groups
  reduce_dataset.py scores.csv class.csv --group-by Class --agg Score:mean --round 1
"""
import argparse
import csv
import sys


def read_csv(path):
    with open(path, "r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        return reader.fieldnames or [], rows


def to_number(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def main():
    ap = argparse.ArgumentParser(description="Reduce a dataset to classroom scale.")
    ap.add_argument("input")
    ap.add_argument("output")
    ap.add_argument("--max-rows", type=int)
    ap.add_argument("--columns")
    ap.add_argument("--filter", action="append", default=[])
    ap.add_argument("--group-by")
    ap.add_argument("--agg", action="append", default=[])
    ap.add_argument("--top")
    ap.add_argument("--round", type=int, dest="round_k")
    args = ap.parse_args()

    fields, rows = read_csv(args.input)
    note = ["read %d rows, %d columns" % (len(rows), len(fields))]

    # Filter
    for f in args.filter:
        if "=" not in f:
            sys.exit("bad --filter (need COL=VALUE): " + f)
        col, val = f.split("=", 1)
        rows = [r for r in rows if str(r.get(col, "")).strip() == val.strip()]
        note.append("filtered %s=%s -> %d rows" % (col, val, len(rows)))

    # Aggregate
    if args.group_by:
        aggs = []
        for a in args.agg:
            if ":" not in a:
                sys.exit("bad --agg (need COL:FUNC): " + a)
            col, func = a.split(":", 1)
            aggs.append((col, func))
        groups = {}
        for r in rows:
            key = str(r.get(args.group_by, ""))
            groups.setdefault(key, []).append(r)
        new_rows = []
        for key, grp in groups.items():
            out = {args.group_by: key}
            for col, func in aggs:
                nums = [to_number(r.get(col)) for r in grp]
                nums = [x for x in nums if x is not None]
                if func == "count":
                    out[col] = len(grp)
                elif not nums:
                    out[col] = ""
                elif func == "sum":
                    out[col] = sum(nums)
                elif func == "mean":
                    out[col] = sum(nums) / len(nums)
                elif func == "min":
                    out[col] = min(nums)
                elif func == "max":
                    out[col] = max(nums)
                else:
                    sys.exit("unknown agg func: " + func)
            new_rows.append(out)
        rows = new_rows
        fields = [args.group_by] + [c for c, _ in aggs]
        note.append("grouped by %s -> %d groups" % (args.group_by, len(rows)))

    # Column selection
    if args.columns:
        keep = [c.strip() for c in args.columns.split(",")]
        missing = [c for c in keep if c not in fields]
        if missing:
            sys.exit("columns not found: %s (have: %s)" % (missing, fields))
        fields = keep
        rows = [{c: r.get(c, "") for c in keep} for r in rows]
        note.append("kept columns %s" % keep)

    # Top N by a column
    if args.top:
        if ":" not in args.top:
            sys.exit("bad --top (need COL:N): " + args.top)
        col, n = args.top.split(":", 1)
        n = int(n)
        rows = [r for r in rows if to_number(r.get(col)) is not None]
        rows.sort(key=lambda r: to_number(r.get(col)), reverse=True)
        rows = rows[:n]
        note.append("kept top %d by %s" % (n, col))

    # Max rows (simple even sampling if still too many)
    if args.max_rows and len(rows) > args.max_rows:
        step = len(rows) / args.max_rows
        rows = [rows[int(i * step)] for i in range(args.max_rows)]
        note.append("sampled down to %d rows" % len(rows))

    # Rounding
    if args.round_k is not None:
        for r in rows:
            for c in fields:
                num = to_number(r.get(c))
                if num is not None and str(r.get(c)).strip() != "":
                    r[c] = round(num, args.round_k)

    with open(args.output, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for r in rows:
            writer.writerow(r)

    note.append("wrote %d rows to %s" % (len(rows), args.output))
    print(" | ".join(note))


if __name__ == "__main__":
    main()
