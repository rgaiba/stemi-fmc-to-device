"""
Validate uploaded source files in national/data/raw/.

Run after each upload to catch shape/quality issues before pipeline writes
parquet against bad data. Each validator returns a list of (level, msg) tuples
where level is one of: OK, WARN, FAIL. Exit code is non-zero if any FAIL.

Usage:
    python national/src/00_validate_uploads.py
    python national/src/00_validate_uploads.py --source cenpop2020
"""
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

import pandas as pd

REPO = Path(__file__).resolve().parents[2]
RAW = Path(os.environ.get("STEMI_DATA_ROOT", REPO / "national" / "data")) / "raw"


# ---------------------------------------------------------------------------
# CenPop2020 — population-weighted block group centroids
# ---------------------------------------------------------------------------

EXPECTED_CENPOP_COLS = [
    "STATEFP", "COUNTYFP", "TRACTCE", "BLKGRPCE",
    "POPULATION", "LATITUDE", "LONGITUDE",
]

# Continental-US bounding box (loose, to catch obvious geocoding errors).
# Includes a margin for offshore islands within CONUS states.
CONUS_LAT = (24.0, 49.5)
CONUS_LON = (-125.5, -66.5)

# FIPS codes excluded from continental-US analysis.
NON_CONUS_FIPS = {"02", "15", "60", "66", "69", "72", "78"}


def validate_cenpop2020() -> list[tuple[str, str]]:
    out: list[tuple[str, str]] = []
    path = RAW / "cenpop2020" / "CenPop2020_Mean_BG.txt"
    if not path.exists():
        return [("FAIL", f"missing file: {path}")]

    out.append(("OK", f"file present, {path.stat().st_size / 1e6:.1f} MB"))

    # encoding='utf-8-sig' strips the BOM that Census attaches.
    # STATEFP/COUNTYFP/TRACTCE/BLKGRPCE are zero-padded numeric IDs — read as str
    # to preserve leading zeros (otherwise '01' becomes 1 and joins break later).
    df = pd.read_csv(
        path,
        encoding="utf-8-sig",
        dtype={"STATEFP": str, "COUNTYFP": str, "TRACTCE": str, "BLKGRPCE": str},
    )

    # 1. Column shape
    if list(df.columns) != EXPECTED_CENPOP_COLS:
        out.append(("FAIL",
                    f"column mismatch — got {list(df.columns)}, "
                    f"expected {EXPECTED_CENPOP_COLS}"))
        return out
    out.append(("OK", f"columns match expected schema ({len(df.columns)})"))

    # 2. Row count — full file ~242k, CONUS ~217k
    n_total = len(df)
    out.append(("OK", f"total rows: {n_total:,}"))
    if not (240_000 <= n_total <= 245_000):
        out.append(("WARN",
                    f"row count outside expected 240k–245k window: {n_total:,}"))

    # 3. FIPS code shape — STATEFP must be 2-digit zero-padded
    bad_state = df[df["STATEFP"].str.len() != 2]
    if len(bad_state):
        out.append(("FAIL",
                    f"{len(bad_state)} rows with malformed STATEFP "
                    f"(not 2-digit zero-padded) — leading zeros likely lost"))

    # 4. Lat/lon types and bounds (CONUS only)
    df["LATITUDE"] = pd.to_numeric(df["LATITUDE"], errors="coerce")
    df["LONGITUDE"] = pd.to_numeric(df["LONGITUDE"], errors="coerce")

    bad_latlon = df[df["LATITUDE"].isna() | df["LONGITUDE"].isna()]
    if len(bad_latlon):
        out.append(("FAIL", f"{len(bad_latlon)} rows with non-numeric lat/lon"))

    # 5. CONUS subset diagnostics
    conus = df[~df["STATEFP"].isin(NON_CONUS_FIPS)].copy()
    n_conus = len(conus)
    out.append(("OK", f"CONUS rows (after dropping {sorted(NON_CONUS_FIPS)}): {n_conus:,}"))
    if not (235_000 <= n_conus <= 240_000):
        out.append(("WARN",
                    f"CONUS row count outside expected 235k–240k window: {n_conus:,}"))

    out_of_box = conus[
        (conus["LATITUDE"] < CONUS_LAT[0]) | (conus["LATITUDE"] > CONUS_LAT[1]) |
        (conus["LONGITUDE"] < CONUS_LON[0]) | (conus["LONGITUDE"] > CONUS_LON[1])
    ]
    if len(out_of_box):
        out.append(("WARN",
                    f"{len(out_of_box)} CONUS-FIPS rows fall outside the "
                    f"CONUS bounding box {CONUS_LAT}, {CONUS_LON}"))
    else:
        out.append(("OK", "all CONUS rows within CONUS bounding box"))

    # 6. Population sanity — total should be ~330M (2020 census), CONUS ~325M
    pop_total = int(df["POPULATION"].sum())
    pop_conus = int(conus["POPULATION"].sum())
    out.append(("OK", f"total population (all FIPS): {pop_total:,}"))
    out.append(("OK", f"CONUS population:           {pop_conus:,}"))
    if not (320_000_000 <= pop_conus <= 330_000_000):
        out.append(("WARN",
                    f"CONUS population outside expected 320M–330M window: {pop_conus:,}"))

    # 7. Per-state coverage — CONUS should have 49 distinct state FIPS (50 - HI/AK + DC)
    n_states_conus = conus["STATEFP"].nunique()
    out.append(("OK", f"distinct CONUS state FIPS: {n_states_conus}"))
    if n_states_conus != 49:  # 48 states + DC
        out.append(("WARN", f"expected 49 CONUS state FIPS (48 states + DC), got {n_states_conus}"))

    # 8. Delaware quick check — prototype baseline. DE = STATEFP '10', ~706k people, ~706 BGs.
    de = conus[conus["STATEFP"] == "10"]
    out.append(("OK",
                f"Delaware (STATEFP=10): {len(de)} BGs, "
                f"population {int(de['POPULATION'].sum()):,} "
                f"— compare to your prototype's expectation"))

    return out


# ---------------------------------------------------------------------------
# Stubs for the other three sources — fail loudly until uploaded
# ---------------------------------------------------------------------------

def validate_cms_pos() -> list[tuple[str, str]]:
    matches = list((RAW / "cms_pos").glob("cms_pos_*.csv"))
    if not matches:
        return [("WARN", "cms_pos: not yet uploaded — see national/data/README.md §2")]
    return [("WARN", f"cms_pos: validator not yet written; found {[m.name for m in matches]}")]


def validate_cms_ipps() -> list[tuple[str, str]]:
    matches = list((RAW / "cms_ipps").glob("cms_ipps_drg_*.csv"))
    if not matches:
        return [("WARN", "cms_ipps: not yet uploaded — see national/data/README.md §3")]
    return [("WARN", f"cms_ipps: validator not yet written; found {[m.name for m in matches]}")]


def validate_tiger_county() -> list[tuple[str, str]]:
    matches = list((RAW / "tiger_county").glob("cb_*_us_county_*m.zip"))
    if not matches:
        return [("WARN", "tiger_county: not yet uploaded — see national/data/README.md §4")]
    return [("WARN", f"tiger_county: validator not yet written; found {[m.name for m in matches]}")]


VALIDATORS = {
    "cenpop2020": validate_cenpop2020,
    "cms_pos": validate_cms_pos,
    "cms_ipps": validate_cms_ipps,
    "tiger_county": validate_tiger_county,
}


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--source", choices=list(VALIDATORS.keys()) + ["all"], default="all")
    args = p.parse_args()

    sources = list(VALIDATORS.keys()) if args.source == "all" else [args.source]
    n_fail = 0
    for src in sources:
        print(f"\n=== {src} ===")
        for level, msg in VALIDATORS[src]():
            print(f"  [{level:4}] {msg}")
            if level == "FAIL":
                n_fail += 1
    print()
    if n_fail:
        print(f"{n_fail} FAIL(s) — fix before proceeding.")
        return 1
    print("validation passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
