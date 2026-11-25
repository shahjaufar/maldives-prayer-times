"""Check a timetable folder for jumps and order errors. Exits 1 if anything is found.

Usage: python tools/check_timetable.py data

For every island, prayer and row, the value may differ by no more than 4 minutes from the average of the days either
side (wrapping round at the year end: row 365 is followed by row 0). Each day's times must also be in order
(fajr < sunrise < dhuhr < asr < maghrib < isha), and every file must have rows 0..365.
"""
import csv, os, sys

PRAYERS = ["fajr", "sunrise", "dhuhr", "asr", "maghrib", "isha"]
LIMIT = 4


def main(folder):
    problems = []
    names = {int(r[1]): f"{r[3].strip()} (category {r[0]})"
             for r in csv.reader(open(os.path.join(folder, "islands.csv"), encoding="utf-8")) if r}
    for iid in sorted(names):
        rows = [r for r in csv.reader(open(os.path.join(folder, "islands", f"{iid}.csv"), encoding="ascii")) if r]
        if [int(r[0]) for r in rows] != list(range(366)):
            problems.append(f"{names[iid]}: rows are not 0..365")
            continue
        t = [[int(x) for x in r[1:7]] for r in rows]
        for i in range(366):
            if any(a >= b for a, b in zip(t[i], t[i][1:])):
                problems.append(f"{names[iid]} row {i}: out of order {t[i]}")
            for p in range(6):
                prev, v, nxt = t[(i - 1) % 366][p], t[i][p], t[(i + 1) % 366][p]
                if abs(v - (prev + nxt) / 2) > LIMIT:
                    problems.append(f"{names[iid]} {PRAYERS[p]} row {i}: {prev} {v} {nxt}")
    for p in problems:
        print(p)
    print(f"{len(names)} islands checked, {len(problems)} problems")
    sys.exit(1 if problems else 0)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    main(sys.argv[1])
