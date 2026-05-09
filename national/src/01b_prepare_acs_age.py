"""Pull ACS 5-year (2019-2023) block-group adult population, table B01001.

Why this script exists
----------------------
The competitive-zone analysis applies a published U.S. STEMI incidence rate
(approximately 1 per 1,000 adults per year, AHA Heart Disease and Stroke
Statistics 2024) to each block-group's adult population to estimate annual
STEMI exposure. The Census 2020 CenPop Mean BG file (CenPop2020_Mean_BG.txt)
that the rest of the pipeline already consumes carries only an all-ages
POPULATION column. Multiplying a per-adult rate by an all-ages denominator
overstates the implied STEMI count by the share of the population under the
adult age cutoff. This script supplies the missing adult-population-by-BG
column from a defensible public source so 06_classify_zones.py can compute
`adult_pop x rate` directly, with no calibration.

Source: ACS 2019-2023 5-year, table B01001 (Sex by Age)
-------------------------------------------------------
ACS 5-year is the only Census product that estimates demographic structure
at block-group resolution; the 1-year ACS stops at county level (and only
for counties with population >= 65,000), and the Decennial Census tabulates
limited age detail at BG. B01001 (Sex by Age) is the only BG-level table
that carries a usable age structure in the ACS detailed-tables set.

Vintage selection: 2019-2023 is the most recent ACS 5-year release as of
this analysis (released December 2024). It overlaps the pandemic but is the
standard published vintage and matches the temporal window for the rest of
the pipeline (CMS PoS 2024-12, CMS IPPS FY2024).

Adult cutoff: 20+
-----------------
The AHA Heart Disease and Stroke Statistics annual update reports STEMI
incidence rates referenced to the adult population aged 20+ (NHANES adult
definition). To match that denominator, this script sums B01001 male and
female bands aged 20+. The 18-19 cohort (~8M people nationally) is excluded;
including it would inflate the adult denominator relative to the rate's
denominator and reintroduce the calibration mismatch this script is designed
to remove.

B01001 variable layout (gotcha): single-year cohorts at 20 and 21
-----------------------------------------------------------------
B01001 collapses adult age into multi-year ranges (22-24, 25-29, ..., 85+)
*except* at ages 20 and 21, which are single-year cohorts broken out
separately. The full layout for adults 20+ is:

    Male 20:        B01001_008E
    Male 21:        B01001_009E
    Male 22-24:     B01001_010E
    Male 25-29:     B01001_011E
    ...
    Male 85+:       B01001_025E
    Female 20:      B01001_032E
    Female 21:      B01001_033E
    Female 22-24:   B01001_034E
    ...
    Female 85+:     B01001_049E

That gives 36 adult bands total (18 male + 18 female). An earlier version
of this script started the male and female ranges at _010E and _034E,
silently dropping M20, M21, F20, F21 and undercounting adults by about 10M
nationally. The bug surfaced as an implausibly low adult fraction (0.726
versus the expected ~0.75). The current ranges are wider on purpose; if
this section gets edited, recheck the adult-fraction validation below.

Geographic scope: CONUS only
----------------------------
The competitive-zone analysis defined in 06_classify_zones.py is CONUS-only:
it excludes Alaska (FIPS 02), Hawaii (15), and Puerto Rico (72) because the
OSRM U.S. road-network extract has no continuity between CONUS and those
geographies (no land-route drive times exist between CONUS and AK/HI/PR).
ACS does cover AK and HI; PR is in a separate ACSPR product not on this
endpoint. To make the validation totals printed by this script directly
comparable to the analysis denominator (zones_classified.parquet), the
state list below pulls only the 49 CONUS entities (48 contiguous states +
DC). If you need AK/HI for a non-CONUS analysis, restore them to the list.

API choice: Census Data API, not bulk download
----------------------------------------------
The Census API allows up to 500 unauthenticated calls per day. We make 49
(one per state). The bulk ACS summary file alternative is a multi-GB
state-by-state zip that requires custom parsers; the API delivers the same
data in JSON in roughly a minute. For higher-volume work, a free key
(https://api.census.gov/data/key_signup.html) raises the limit; the script
picks one up from $CENSUS_API_KEY if set.

Sandbox note: the cowork sandbox proxy blocks Census endpoints, so this
script must be run on the user's local machine. The output CSV lives in
the repo and is read from there by downstream sandbox steps.

Output
------
    national/data/raw/acs5_2023/acs5_2023_b01001_bg.csv
        Columns:
            bg_id              str   12-digit GEOID = STATEFP(2) + COUNTYFP(3)
                                     + TRACTCE(6) + BLKGRPCE(1)
            total_pop_acs      int   B01001_001E (sanity check vs CenPop2020 POPULATION;
                                     not used downstream)
            adult_pop_20plus   int   sum of 36 adult bands; consumed by
                                     06_classify_zones.py
    national/data/raw/acs5_2023/SHA256.txt
        SHA256 of the CSV; recorded in MANIFEST.md.

Validation expectations (CONUS, ACS 2019-2023 5-year, adults 20+)
-----------------------------------------------------------------
The script prints summary totals and runs three range checks. The expected
values reflect ACS 2019-2023 published estimates and CenPop2020 BG counts;
allow approximately +/- 2% wiggle for vintage drift between releases.

    BG count                : 235,000 to 245,000
        (zones_classified.parquet has 238,193 CONUS BGs from CenPop2020;
        ACS 2023 BG count is within ~2% of this and approximately a few
        hundred BGs may differ between vintages)
    total_pop_acs sum       : 320M to 335M
        (published ACS 2019-2023 total population: 332M U.S.; CONUS share
        ~98%, so ~325M)
    adult_pop_20plus sum    : 240M to 255M
        (published ACS 2019-2023 S0101 U.S. 20+: ~258M; CONUS share ~98%,
        so ~253M)
    adult fraction          : 0.73 to 0.77
        (CONUS 20+ share of total population, stable across recent vintages)

Any value outside these bands triggers a "WARN:" line. The script does not
hard-fail on a warning; it leaves the decision to the user, since a
genuine vintage update could move totals slightly out of band.

Downstream consumer
-------------------
06_classify_zones.py left-joins this CSV onto zones on bg_id and uses
adult_pop_20plus (renamed `adult_pop` in zones_classified.parquet) as the
denominator for `stemi_per_yr = adult_pop * 0.001`. See REPRODUCIBILITY.md
section "Analytic decisions and changes" decision D8.
"""
from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path
import urllib.parse
import urllib.request

import pandas as pd

REPO = Path(__file__).resolve().parents[2]
RAW = REPO / "national" / "data" / "raw" / "acs5_2023"
RAW.mkdir(parents=True, exist_ok=True)

# ACS vintage. "2023" means the 2019-2023 5-year release.
ACS_VINTAGE = "2023"
BASE = f"https://api.census.gov/data/{ACS_VINTAGE}/acs/acs5"

# CONUS state FIPS codes: 48 contiguous states + DC (49 entities).
# Aligned with 06_classify_zones.py CONUS filter (excludes 02, 15, 72).
# See module docstring section "Geographic scope: CONUS only" for rationale.
STATE_FIPS = [
    "01","04","05","06","08","09","10","11","12","13","16","17",
    "18","19","20","21","22","23","24","25","26","27","28","29","30","31",
    "32","33","34","35","36","37","38","39","40","41","42","44","45","46",
    "47","48","49","50","51","53","54","55","56",
]

# Adult 20+ variable list. See module docstring section "B01001 variable
# layout (gotcha): single-year cohorts at 20 and 21" before editing.
MALE_20PLUS = [f"B01001_{i:03d}E" for i in range(8, 26)]    # 008..025  (18 bands)
FEMALE_20PLUS = [f"B01001_{i:03d}E" for i in range(32, 50)]  # 032..049  (18 bands)
ADULT_VARS = MALE_20PLUS + FEMALE_20PLUS
GET_VARS = ["B01001_001E"] + ADULT_VARS

# Validation bands (see module docstring section "Validation expectations").
EXPECTED_BG_COUNT = (235_000, 245_000)
EXPECTED_TOTAL_POP = (320_000_000, 335_000_000)
EXPECTED_ADULT_POP = (240_000_000, 255_000_000)
EXPECTED_ADULT_FRACTION = (0.73, 0.77)

KEY = os.environ.get("CENSUS_API_KEY", "")


def fetch_state(state: str) -> pd.DataFrame:
    """Pull all BGs for one state from the Census API and return a tidy frame."""
    params = {
        "get": ",".join(["NAME"] + GET_VARS),
        "for": "block group:*",
        "in": f"state:{state} county:*",
    }
    if KEY:
        params["key"] = KEY
    url = f"{BASE}?{urllib.parse.urlencode(params)}"
    req = urllib.request.Request(url, headers={"User-Agent": "stemi-fmc-to-device/1.0"})

    # 3 retries with exponential backoff. Census endpoint is reliable; this
    # is mostly to soak up transient TLS hiccups, not real availability gaps.
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                data = json.loads(r.read().decode())
            break
        except Exception as e:
            if attempt == 2:
                raise
            print(f"    state {state} attempt {attempt+1} failed: {e}; retrying...")
            time.sleep(2 ** attempt)

    header, rows = data[0], data[1:]
    df = pd.DataFrame(rows, columns=header)

    # Build the 12-digit GEOID. Census API returns the four geographic
    # components as separate string fields; concatenated they form bg_id,
    # which matches the `bg_id` column in zones_classified.parquet.
    df["bg_id"] = (
        df["state"].astype(str)
        + df["county"].astype(str)
        + df["tract"].astype(str)
        + df["block group"].astype(str)
    )

    # ACS uses -666666666 as a sentinel for "estimate not available."
    # For population counts at BG level this is rare but does occur in very
    # small BGs; treat as 0 so it doesn't pollute the sum.
    for v in GET_VARS:
        df[v] = pd.to_numeric(df[v], errors="coerce").fillna(0)
        df.loc[df[v] < 0, v] = 0

    df["total_pop_acs"] = df["B01001_001E"].astype(int)
    df["adult_pop_20plus"] = df[ADULT_VARS].sum(axis=1).astype(int)

    return df[["bg_id", "total_pop_acs", "adult_pop_20plus"]]


def in_band(value: float, band: tuple[float, float]) -> bool:
    return band[0] <= value <= band[1]


def main():
    print(f"ACS vintage:    2019-2023 5-year (vintage code {ACS_VINTAGE})")
    print(f"Variables:      {len(GET_VARS)} ({GET_VARS[0]} + {len(ADULT_VARS)} adult bands)")
    print(f"Census API key: {'present' if KEY else 'NOT SET (anonymous, 500 calls/day limit)'}")
    print(f"State scope:    {len(STATE_FIPS)} CONUS entities (48 contiguous states + DC)")
    print(f"Pulling...")

    parts = []
    for s in STATE_FIPS:
        try:
            d = fetch_state(s)
            parts.append(d)
            print(f"  state {s}: {len(d):>6,} BGs, "
                  f"adult_20plus = {d['adult_pop_20plus'].sum():>12,}")
        except Exception as e:
            print(f"  state {s}: FAILED ({e})", file=sys.stderr)
            raise

    full = pd.concat(parts, ignore_index=True)

    # Summary
    n_bg = len(full)
    total_pop = int(full["total_pop_acs"].sum())
    adult_pop = int(full["adult_pop_20plus"].sum())
    adult_frac = adult_pop / total_pop

    print(f"\nNational (CONUS) total:")
    print(f"  BG count:               {n_bg:>14,}")
    print(f"  total_pop_acs sum:      {total_pop:>14,}")
    print(f"  adult_pop_20plus sum:   {adult_pop:>14,}")
    print(f"  adult fraction:         {adult_frac:>14.4f}")

    # Validation: range checks, not hard-fail. See docstring "Validation
    # expectations" for the source of each band.
    print(f"\nValidation:")
    checks = [
        ("BG count",         n_bg,        EXPECTED_BG_COUNT),
        ("total_pop_acs",    total_pop,   EXPECTED_TOTAL_POP),
        ("adult_pop_20plus", adult_pop,   EXPECTED_ADULT_POP),
        ("adult fraction",   adult_frac,  EXPECTED_ADULT_FRACTION),
    ]
    all_ok = True
    for name, val, band in checks:
        ok = in_band(val, band)
        status = "OK  " if ok else "WARN"
        all_ok = all_ok and ok
        if isinstance(val, float):
            print(f"  [{status}] {name:<20s} {val:>14.4f}   expected {band[0]}..{band[1]}")
        else:
            print(f"  [{status}] {name:<20s} {val:>14,}   expected {band[0]:,}..{band[1]:,}")
    if not all_ok:
        print("\n  One or more checks landed outside the expected band. Inspect")
        print("  totals against the most recent published ACS S0101 before using")
        print("  this file downstream. The pipeline does not hard-fail on a WARN.")

    # bg_id format check: every value should be exactly 12 chars.
    bad_ids = full[full["bg_id"].str.len() != 12]
    if len(bad_ids):
        print(f"  [WARN] bg_id length: {len(bad_ids):,} rows are not 12 chars")
    else:
        print(f"  [OK  ] bg_id length: all {n_bg:,} values are exactly 12 chars")

    # Per-state floor (catches a silently truncated state pull).
    per_state = full.assign(state=full["bg_id"].str[:2]).groupby("state").size()
    too_few = per_state[per_state < 50]
    if len(too_few):
        print(f"  [WARN] states with < 50 BGs (likely truncated):")
        for st, cnt in too_few.items():
            print(f"           {st}: {cnt}")
    else:
        print(f"  [OK  ] every state returned >= 50 BGs (no truncation)")

    # Write CSV + checksum
    out = RAW / "acs5_2023_b01001_bg.csv"
    full.to_csv(out, index=False)
    print(f"\nWrote {out} ({out.stat().st_size/1e6:.1f} MB)")

    import hashlib
    h = hashlib.sha256()
    with open(out, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    sha = h.hexdigest()
    (RAW / "SHA256.txt").write_text(f"{sha}  acs5_2023_b01001_bg.csv\n")
    print(f"SHA256: {sha}")
    print(f"\nNext step: 06_classify_zones.py will join this on bg_id and "
          f"use adult_pop_20plus as the STEMI rate denominator.")


if __name__ == "__main__":
    main()
