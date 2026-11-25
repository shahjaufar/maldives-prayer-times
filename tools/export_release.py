"""Write the release CSVs from data/.

Usage: python tools/export_release.py data dist

  dist/islands.csv       one row per island
  dist/prayer_times.csv  one row per island and calendar day (366 days; 29 February is for leap years only)

Times are local Maldives time (UTC+5), HH:MM, with the island's offset already applied. The files are UTF-8 with a
byte-order mark, so that Excel shows the Dhivehi names correctly, and use CRLF line endings.
"""
import csv, datetime, os, sys

HEAD_ISLANDS = ["island_id", "atoll", "atoll_dv", "name_en", "name_dv", "category_id", "offset_min",
                "lat", "lon", "active"]
HEAD_TIMES = ["island_id", "atoll", "island", "island_dv", "month", "day", "leap_year_only",
              "fajr", "sunrise", "dhuhr", "asr", "maghrib", "isha"]


def read_islands(folder):
    atolls = {int(r[0]): r for r in csv.reader(open(os.path.join(folder, "atolls.csv"), encoding="utf-8")) if r}
    out = []
    for r in csv.reader(open(os.path.join(folder, "islands.csv"), encoding="utf-8")):
        if not r:
            continue
        # category, island, atoll, name_en, name_dv, name_ar (sometimes split by a comma), offset, [lat, lon,] status
        has_coords = len(r) >= 10
        offset = int(r[-4] if has_coords else r[-2])
        lat, lon = (r[-3].strip(), r[-2].strip()) if has_coords else ("", "")
        a = atolls[int(r[2])]
        out.append({"island_id": int(r[1]), "atoll": a[2].strip(), "atoll_dv": a[3].strip(),
                    "name_en": r[3].strip(), "name_dv": r[4].strip(), "category_id": int(r[0]),
                    "offset_min": offset, "lat": lat, "lon": lon, "active": int(r[-1])})
    return sorted(out, key=lambda i: i["island_id"])


def hm(m):
    return f"{m // 60:02d}:{m % 60:02d}"


def main(folder, dist):
    os.makedirs(dist, exist_ok=True)
    islands = read_islands(folder)
    # Row r is the r-th day of a leap year: row 0 = 1 January, row 59 = 29 February, row 365 = 31 December.
    days = [datetime.date(2028, 1, 1) + datetime.timedelta(days=r) for r in range(366)]

    with open(os.path.join(dist, "islands.csv"), "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f, lineterminator="\r\n")
        w.writerow(HEAD_ISLANDS)
        for i in islands:
            w.writerow([i[k] for k in HEAD_ISLANDS])

    n = 0
    with open(os.path.join(dist, "prayer_times.csv"), "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f, lineterminator="\r\n")
        w.writerow(HEAD_TIMES)
        for i in islands:
            rows = [r for r in csv.reader(open(os.path.join(folder, "islands", f"{i['island_id']}.csv"))) if r]
            if [int(r[0]) for r in rows] != list(range(366)):
                sys.exit(f"island {i['island_id']}: rows are not 0..365")
            for r in rows:
                d = days[int(r[0])]
                w.writerow([i["island_id"], i["atoll"], i["name_en"], i["name_dv"], d.month, d.day,
                            1 if (d.month, d.day) == (2, 29) else 0] + [hm(int(x)) for x in r[1:7]])
                n += 1
    print(f"{len(islands)} islands, {n} prayer-time rows written to {dist}")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    main(sys.argv[1], sys.argv[2])
