"""Apply corrections.csv to the upstream namaadhu_app timetable and write the corrected copy.

Usage: python tools/fix_timetable.py <namaadhu_app>/assets/csv data

Reads  <in>/atolls.csv, <in>/islands.csv, <in>/islands/<island_id>.csv
Writes <out>/atolls.csv (copied unchanged), <out>/islands.csv (English names from names.csv) and
       <out>/islands/<island_id>.csv (times from corrections.csv).

Each correction in corrections.csv is given for the category base time (offset 0). It is applied to every island in
that category, with the island's own minute offset added. Before changing a value, the script checks that the
island's current value equals "from" + offset; if any does not, it stops without writing anything.

Only the corrected lines change. Every other byte of each file (CRLF line endings, no final newline) is kept as is.
"""
import csv, os, shutil, sys

PRAYERS = ["fajr", "sunrise", "dhuhr", "asr", "maghrib", "isha"]


def minutes(hhmm):
    h, m = hhmm.split(":")
    return int(h) * 60 + int(m)


def island_offsets(islands_csv):
    """island_id -> (category_id, offset). The Arabic name sometimes spans two fields, so read numbers from the end."""
    out = {}
    for r in csv.reader(open(islands_csv, encoding="utf-8")):
        if not r:
            continue
        category, island_id = int(r[0]), int(r[1])
        offset = int(r[-4]) if len(r) >= 10 else int(r[-2])  # 8 fields: no coordinates
        out[island_id] = (category, offset)
    return out


def main(src, out):
    here = os.path.dirname(os.path.abspath(__file__))
    corrections = list(csv.DictReader(open(os.path.join(here, "..", "corrections.csv"), encoding="utf-8")))
    islands = island_offsets(os.path.join(src, "islands.csv"))

    files = {}  # island_id -> list of lines (without line endings)
    for iid in islands:
        with open(os.path.join(src, "islands", f"{iid}.csv"), encoding="ascii", newline="") as f:
            files[iid] = f.read().split("\r\n")

    errors, changed = [], 0
    for c in corrections:
        cat, row, col = int(c["category"]), int(c["row"]), 1 + PRAYERS.index(c["prayer"])
        targets = [iid for iid, (icat, _) in islands.items() if icat == cat]
        if not targets:
            errors.append(f"category {cat}: no islands")
        for iid in targets:
            off = islands[iid][1]
            lines = files[iid]
            if row >= len(lines):
                errors.append(f"island {iid}: no row {row}")
                continue
            fields = lines[row].split(",")
            if int(fields[0]) != row:
                errors.append(f"island {iid}: line {row} holds row {fields[0]}")
                continue
            want = minutes(c["from"]) + off
            if int(fields[col]) != want:
                errors.append(f"island {iid} (category {cat}, offset {off}) {c['prayer']} row {row}: "
                              f"expected {want}, found {fields[col]}")
                continue
            fields[col] = str(minutes(c["to"]) + off)
            lines[row] = ",".join(fields)
            changed += 1

    if errors:
        sys.exit("not applied:\n  " + "\n  ".join(errors))

    # English names (names.csv): only the name_en field of each listed island's line changes.
    with open(os.path.join(src, "islands.csv"), encoding="utf-8", newline="") as f:
        island_lines = f.read().split("\r\n")
    names = list(csv.DictReader(open(os.path.join(here, "..", "names.csv"), encoding="utf-8")))
    for nm in names:
        hits = [i for i, line in enumerate(island_lines) if line.split(",")[1:2] == [nm["island_id"]]]
        if len(hits) != 1:
            errors.append(f"names: island {nm['island_id']} found {len(hits)} times")
            continue
        fields = island_lines[hits[0]].split(",")
        if fields[3] != nm["from"]:
            errors.append(f"names: island {nm['island_id']}: expected {nm['from']!r}, found {fields[3]!r}")
            continue
        fields[3] = nm["to"]
        island_lines[hits[0]] = ",".join(fields)
    if errors:
        sys.exit("not applied:\n  " + "\n  ".join(errors))

    os.makedirs(os.path.join(out, "islands"), exist_ok=True)
    shutil.copyfile(os.path.join(src, "atolls.csv"), os.path.join(out, "atolls.csv"))
    with open(os.path.join(out, "islands.csv"), "w", encoding="utf-8", newline="") as f:
        f.write("\r\n".join(island_lines))
    for iid, lines in files.items():
        with open(os.path.join(out, "islands", f"{iid}.csv"), "w", encoding="ascii", newline="") as f:
            f.write("\r\n".join(lines))
    print(f"{len(corrections)} corrections, {changed} island values changed, {len(files)} island files written, "
          f"{len(names)} island names corrected")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    main(sys.argv[1], sys.argv[2])
