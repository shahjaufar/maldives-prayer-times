# Maldives prayer times, corrected

The island prayer timetable for the Maldives (205 islands, 42 timetable categories), with two problems fixed:

1. **How the rows are read.** The 366 rows are a leap-year calendar. Reading them by day of year shows the wrong day's times from 1 January to 28 February, and all year in leap years.
2. **Bad values in the data.** 15 base values (114 island values) are wrong: mostly sunrise times an hour late, plus one Isha time 10 minutes early.
3. **Island names.** 33 English island names are corrected to the official spelling (see [Island names](#island-names)).

The data comes from [n4ff4h/namaadhu_app](https://github.com/n4ff4h/namaadhu_app) (MIT, commit `f610de5`).

Checked on 25 November 2026 against times worked out from the sun's position.

---

## Problem 1: the day lookup is one day ahead in January and February

Each island file has 366 rows, numbered 0 to 365. **They are laid out as a leap year:**

| Row | Date |
|---|---|
| 0 | 1 January |
| 58 | 28 February |
| 59 | 29 February (**skip in normal years**) |
| 60 | 1 March |
| 365 | 31 December |

The obvious lookup, `row = day of year` (1 January = 1), is wrong:

- **Normal years, 1 January to 28 February:** shows the next day's times.
- **Leap years, all year:** shows the next day's times. On 31 December the day of year is 366, which is not a row at all. With `% 366` it wraps to row 0, which holds 1 January.
- **Normal years, 1 March to 31 December:** happens to be right.

namaadhu_app's own lookup does this: it matches `element.id == dayOfYear`, where `dayOfYear` is `DateFormat("D")`, counting from 1.

**Evidence.** Sunrise, sunset and noon worked out from the sun's position fit this reading better than the day-of-year reading, in all 42 categories.

### Correct lookup

```kotlin
// Kotlin / Java (java.time.LocalDate)
val row = if (date.isLeapYear || date.monthValue <= 2) date.dayOfYear - 1 else date.dayOfYear
```

```dart
// Dart
int row(DateTime d) {
  final dayOfYear = int.parse(DateFormat("D").format(d)); // 1 January = 1
  final leap = (d.year % 4 == 0 && d.year % 100 != 0) || d.year % 400 == 0;
  return (leap || d.month <= 2) ? dayOfYear - 1 : dayOfYear;
}
```

```python
# Python
import calendar
def row(d):
    doy = d.timetuple().tm_yday  # 1 January = 1
    return doy - 1 if calendar.isleap(d.year) or d.month <= 2 else doy
```

The result is always between 0 and 365, no two dates in a year share a row, and row 59 is used only on 29 February.

### Check values: K. Malé (island 102, category 57, offset 0)

| Date | Row | Fajr | Sunrise | Dhuhr | Asr | Maghrib | Isha |
|---|---|---|---|---|---|---|---|
| 2026-01-01 | 0 | 04:54 | 06:11 | 12:13 | 15:34 | 18:08 | 19:25 |
| 2026-02-28 | 58 | 05:05 | 06:16 | 12:23 | 15:36 | 18:21 | 19:33 |
| 2026-03-01 | 60 | 05:04 | 06:16 | 12:23 | 15:36 | 18:21 | 19:33 |
| 2026-12-31 | 365 | 04:54 | 06:10 | 12:13 | 15:33 | 18:07 | 19:25 |
| 2028-02-29 | 59 | 05:04 | 06:16 | 12:23 | 15:36 | 18:21 | 19:33 |
| 2028-03-01 | 60 | 05:04 | 06:16 | 12:23 | 15:36 | 18:21 | 19:33 |
| 2028-12-31 | 365 | 04:54 | 06:10 | 12:13 | 15:33 | 18:07 | 19:25 |

---

## Problem 2: bad values in the data

Any value more than 4 minutes from the average of the days either side was flagged, then checked against the sun's position. The upstream data has 150 such flags. All of them come from the 15 values below; the rest are the neighbouring days, flagged because they sit next to a bad value. After the fix there are none.

Times below are the **category base time** (offset 0). Islands with an offset of +1 or −1 minute have the same error shifted by that minute, and are corrected the same way.

| Category | Prayer | Row | Date | Was | Now | Why |
|---|---|---|---|---|---|---|
| 44 | Sunrise | 332 | 28 Nov | **06:59** | 05:59 | hour digit wrong; days either side 05:59, 06:00 |
| 44 | Sunrise | 333 | 29 Nov | **07:59** | 05:59 | hour digit wrong |
| 50 | Sunrise | 332 | 28 Nov | **06:59** | 05:59 | hour digit wrong; days either side 05:58, 06:00 |
| 50 | Sunrise | 333 | 29 Nov | **06:59** | 05:59 | hour digit wrong |
| 53 | Sunrise | 332 | 28 Nov | **06:58** | 05:58 | hour digit wrong; days either side 05:58, 05:59 |
| 53 | Sunrise | 333 | 29 Nov | **06:58** | 05:58 | hour digit wrong |
| 53 | Sunrise | 334 | 30 Nov | **06:59** | 05:59 | hour digit wrong |
| 46 | Sunrise | 213 | 1 Aug | **06:59** | 05:59 | hour digit wrong; days either side 05:59, 06:00 |
| 46 | Sunrise | 214 | 2 Aug | **06:59** | 05:59 | hour digit wrong |
| 46 | Sunrise | 215 | 3 Aug | **06:59** | 05:59 | hour digit wrong |
| 46 | Sunrise | 216 | 4 Aug | **06:59** | 05:59 | hour digit wrong |
| 81 | Sunrise | 357 | 23 Dec | **06:59** | 05:59 | hour digit wrong; days either side 05:59, 06:00 |
| 80 | Sunrise | 247 | 4 Sep | **06:10** | 06:01 | days either side 06:02, 06:01; sun position gives 06:01 |
| 80 | Sunrise | 248 | 5 Sep | **06:10** | 06:01 | (as above) |
| 75 | Isha | 30 | 31 Jan | **19:28** | 19:38 | days either side 19:38, 19:38; sun position gives 19:38 |

A wrong sunrise also puts the end of Fajr, and the start of Duha, an hour late on those days.

The dates in the table are the same in every year, because rows after February line up with the calendar in both normal and leap years. Before 1 March, a day-of-year lookup (Problem 1) would show the bad Isha value on 30 January instead of 31 January.

### Islands affected

| Category | Islands (offset, if not 0) |
|---|---|
| 44 | Sh. Noomaraa, Sh. Kanditheemu (+1), Sh. Goidhoo (+1), Sh. Feydhoo, Sh. Feevah, Sh. Bilehfahi (+1), Sh. Foakaidhoo, Sh. Narudhoo, Sh. Maakandoodhoo (inactive), Sh. Milandhoo |
| 50 | R. Rasmaadhoo, R. Innamaadhoo, R. Maduvvari, R. Inguraidhoo, R. Meedhoo, R. Fainu, R. Kinolhas |
| 53 | B. Thulhaadhoo, B. Hithaadhoo, B. Fulhadhoo, B. Fehendhoo, B. Goidhoo |
| 46 | N. Henbadhoo, N. Kendhikulhudhoo, N. Tholhendhoo (inactive), N. Maalhendhoo, N. Kudafari, N. Landhoo, N. Maafaru, N. Lhohi, N. Miladhoo, N. Magoodhoo, N. Manadhoo |
| 81 | Gn. Fuvahmulah |
| 80 | GDh. Nadellaa (+1), GDh. Gadhdhoo (−1), GDh. Rathafandhoo, GDh. Vaadhoo, GDh. Fiyoaree, GDh. Maathoda, GDh. Fares |
| 75 | L. Isdhoo, L. Dhanbidhoo, L. Maabaidhoo, L. Mundoo, L. Kalaidhoo (inactive), L. Gan |

47 island files change. The other 158 are the same as upstream.

---

## Island names

The English names in namaadhu_app are spelled inconsistently. They are corrected to the islands' official council names, as listed by the Elections Commission of Maldives for the Local Council Election 2026.

Only the English names change. The Dhivehi names (`name_dv`) and Arabic names are as in namaadhu_app. Islands that list does not have on their own keep their names. These are most inactive islands, L. Gaadhoo, and GDh. Fares and GDh. Maathoda, which the Elections Commission lists together as Faresmaathodaa. For HA. Molhadhoo, the source's Dhivehi name is މުޅަދޫ.

| Atoll | Was | Now | Dhivehi |
|---|---|---|---|
| HA. | Uligamu | **Uligan** | އުލިގަމު |
| HA. | Mulhadhoo | **Molhadhoo** | މުޅަދޫ |
| HA. | Dhidhoo | **Dhidhdhoo** | ދިއްދޫ |
| HA. | Fillaidhoo | **Filladhoo** | ފިއްލަދޫ |
| HDh. | Hanimadhoo | **Hanimaadhoo** | ހަނިމާދޫ |
| HDh. | Naavaidhoo | **Naivaadhoo** | ނައިވާދޫ |
| HDh. | Nolhivaram | **Nolhivaran** | ނޮޅިވަރަމު |
| HDh. | Kurinbee | **Kurinbi** | ކުރިނބި |
| N. | Hembadhoo | **Henbadhoo** | ހެނބަދޫ |
| N. | Kendhikolhudhoo | **Kendhikulhudhoo** | ކެނދިކުޅުދޫ |
| N. | Kudafaree | **Kudafari** | ކުޑަފަރި |
| N. | Lhohee | **Lhohi** | ޅޮހި |
| N. | Fohdhoo | **Fodhdhoo** | ފޮއްދޫ |
| B. | Dhonfanu | **Dhonfan** | ދޮންފަނު |
| K. | Hura | **Huraa** | ހުރާ |
| K. | Himmafushi | **Hinmafushi** | ހިންމަފުށި |
| AA. | Himendhoo | **Himandhoo** | ހިމެންދޫ |
| ADh. | Hanyameedhoo | **Hangnaameedhoo** | ހަންޏާމީދޫ |
| ADh. | Kumburudhoo | **Kunburudhoo** | ކުނބުރުދޫ |
| ADh. | Dhidhoo | **Dhidhdhoo** | ދިއްދޫ |
| M. | Raimandhoo | **Raiymandhoo** | ރަތްމަންދޫ |
| F. | Dharamboodhoo | **Dharanboodhoo** | ދަރަނބޫދޫ |
| Dh. | Rimbudhoo | **Rinbudhoo** | ރިނބުދޫ |
| Dh. | Maaemboodhoo | **Maaenboodhoo** | މާއެނބޫދޫ |
| Th. | Burunee | **Buruni** | ބުރުނި |
| Th. | Veymandhoo | **Veymandoo** | ވޭމަންޑޫ |
| Th. | Kimbidhoo | **Kinbidhoo** | ކިނބިދޫ |
| L. | Dhambidhoo | **Dhanbidhoo** | ދަނބިދޫ |
| L. | Kalhaidhoo | **Kalaidhoo** | ކަޅައިދޫ |
| GDh. | Hoadedhoo | **Hoandedhdhoo** | ހޯނޑެއްދޫ |
| GDh. | Nadella | **Nadellaa** | ނަޑައްލާ |
| GDh. | Fiyoree | **Fiyoaree** | ފިޔޯރީ |
| S. | Maradhoofeydhoo | **Maradhoo-Feydhoo** | މަރަދޫފޭދޫ |

The list is in [`names.csv`](names.csv). `tools/fix_timetable.py` applies it to `data/islands.csv`, and changes only the `name_en` field of those 33 lines.

---

## Other sites checked

On 25 November 2026 we also looked at two Maldivian prayer-time sites. They seem to use the same timetable, so these notes may be useful to the people who run them. We're grateful for their work in sharing prayer times.

- **namaadhuvaguthu.com**: dates are matched to the right rows. It shows the 15 values in [Problem 2](#problem-2-bad-values-in-the-data) as they are in the source. It also shows Dhuhr as 12:59 on 6–8 October for the five islands in category 77 (GA. Kolamaafushi, Vilingili, Maamendhoo, Nilandhoo and Dhaandhoo), where 11:59 looks right.
- **dhivehi.mv**: shows the same values, including that Dhuhr on 6–8 October. Its 2026 table also has a row for 29 February. Three islands, Sh. Milandhoo, R. Dhuvaafaru and R. Hulhudhuffaaru, show an empty table. Before an island is chosen, the table shows another island's times than the one named in the island box.

---

## What's here

```
data/                 corrected copy, same layout as namaadhu_app's assets/csv
  atolls.csv          atoll_id, name_en, abbr_en, abbr_dv, abbr_ar          (unchanged)
  islands.csv         category_id, island_id, atoll_id, name_en, name_dv, name_ar, offset_min, lat, lon, status
                      (only name_en changes, for 33 islands; a few rows have no lat/lon, and some Arabic names contain a comma)
  islands/<id>.csv    row, fajr, sunrise, dhuhr, asr, maghrib, isha
                      minutes after local midnight (Maldives time, UTC+5), island offset already applied
corrections.csv       the 15 corrections, as category base times
names.csv             the 33 English name corrections
tools/fix_timetable.py    rebuilds data/ from upstream; stops if any "from" value doesn't match
tools/check_timetable.py  the jump and order check
```

The files in `data/` keep upstream's format exactly: CRLF line endings, and no final newline in the island files. You can drop them into a namaadhu_app checkout.

### Rebuild and check

```
git clone https://github.com/n4ff4h/namaadhu_app
python tools/fix_timetable.py namaadhu_app/assets/csv data
python tools/check_timetable.py data                       # 205 islands checked, 0 problems
python tools/check_timetable.py namaadhu_app/assets/csv    # upstream: 150 problems
```

The check fails on any value more than 4 minutes from the average of the days either side (row 365 wraps round to row 0), on times out of order, and on missing rows.

---

## Caveats

- This fixes values that are plainly inconsistent with the days around them. It does not confirm that the rest of the timetable is right. The official publisher (understood to be the Ministry of Islamic Affairs) has not reviewed these corrections.
- For the two sunrise values in category 80 and the Isha value in category 75, the corrected value comes from the sun's position and the days either side.

## Licence

MIT. The timetable data is © 2023 Naffah Abdulla Rasheed (namaadhu_app), MIT-licensed. See [LICENSE](LICENSE).
