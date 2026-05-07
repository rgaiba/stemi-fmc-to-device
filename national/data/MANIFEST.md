# Data manifest

Recorded validation outputs per source. Append a new entry after each upload.

---

## CenPop2020_Mean_BG.txt

- Source: <https://www2.census.gov/geo/docs/reference/cenpop2020/blkgrp/CenPop2020_Mean_BG.txt>
- Downloaded: 2026-05-07
- File size: 10.6 MB
- Total rows: 242,335
- CONUS rows (after dropping FIPS 02/15/60/66/69/72/78): 238,193
- CONUS population: 329,260,619
- Distinct CONUS state FIPS: 49 (48 states + DC) ✓
- Delaware (STATEFP=10): 706 BGs, population 989,948 ✓ (exact match to 2020 Census state total)
- Lat/lon bounds: all CONUS rows within (24.0–49.5, −125.5 to −66.5) ✓
- Validation: passed (no FAIL, no WARN)

Note on row count: the proposal cites 217,740 block groups (2010 figure). 2020
decennial released 238,193 CONUS BGs (~10% more). All numbers in the abstract
should use the 2020 figure. Worth flagging in proposal §4 before submission.

---

## cms_pos — pending upload

## cms_ipps — pending upload

## tiger_county — pending upload
