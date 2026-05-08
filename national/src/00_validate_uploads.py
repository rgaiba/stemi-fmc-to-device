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

EXPECTED_POS_COLS = [
    "prvdr_num", "fac_name",
    "st_adr", "city_name", "state_cd", "zip_cd",
    "fips_state_cd",
    "prvdr_ctgry_cd", "prvdr_ctgry_sbtyp_cd",
    "bed_cnt", "crtfd_bed_cnt",
    "crdc_cthrtztn_lab_srvc_cd", "crdc_cthrtztn_prcdr_rooms_cnt",
    "crtfctn_dt", "pgm_trmntn_cd",
]

# 48 CONUS states + DC
CONUS_STATE_CD = {
    "AL","AR","AZ","CA","CO","CT","DC","DE","FL","GA","IA","ID","IL","IN","KS","KY",
    "LA","MA","MD","ME","MI","MN","MO","MS","MT","NC","ND","NE","NH","NJ","NM","NV",
    "NY","OH","OK","OR","PA","RI","SC","SD","TN","TX","UT","VA","VT","WA","WI","WV","WY",
}


def validate_cms_pos() -> list[tuple[str, str]]:
    out: list[tuple[str, str]] = []
    matches = sorted((RAW / "cms_pos").glob("cms_pos_*.csv"))
    if not matches:
        return [("WARN", "cms_pos: not yet uploaded — see national/data/README.md §2")]
    if len(matches) > 1:
        out.append(("WARN", f"multiple cms_pos files found: {[m.name for m in matches]}; using newest"))
    path = matches[-1]
    out.append(("OK", f"file: {path.name} ({path.stat().st_size/1e6:.2f} MB)"))

    df = pd.read_csv(path, dtype=str)

    # Column shape
    if list(df.columns) != EXPECTED_POS_COLS:
        out.append(("FAIL",
                    f"column mismatch — got {list(df.columns)}, "
                    f"expected {EXPECTED_POS_COLS}"))
        return out
    out.append(("OK", f"columns match expected schema ({len(df.columns)})"))

    # Row count window — active CONUS short-term general hospitals
    n = len(df)
    out.append(("OK", f"row count: {n:,}"))
    if not (5_500 <= n <= 7_500):
        out.append(("WARN", f"row count outside expected 5,500–7,500: {n:,}"))

    # All rows should be prvdr_ctgry_cd='01' (the filter)
    bad_ctgry = df[df["prvdr_ctgry_cd"] != "01"]
    if len(bad_ctgry):
        out.append(("FAIL", f"{len(bad_ctgry)} rows with prvdr_ctgry_cd != '01'"))
    else:
        out.append(("OK", "all rows are short-term general hospitals (prvdr_ctgry_cd='01')"))

    # All rows should be pgm_trmntn_cd='00' (active filter)
    bad_term = df[df["pgm_trmntn_cd"] != "00"]
    if len(bad_term):
        out.append(("FAIL", f"{len(bad_term)} rows with pgm_trmntn_cd != '00' (terminated)"))
    else:
        out.append(("OK", "all rows are active providers (pgm_trmntn_cd='00')"))

    # State code in CONUS whitelist
    bad_state = df[~df["state_cd"].isin(CONUS_STATE_CD)]
    if len(bad_state):
        out.append(("FAIL",
                    f"{len(bad_state)} rows with non-CONUS state_cd: "
                    f"{bad_state['state_cd'].value_counts().to_dict()}"))
    else:
        out.append(("OK", f"all rows in CONUS whitelist ({df['state_cd'].nunique()} distinct codes)"))

    # CCN (prvdr_num) uniqueness
    n_unique = df["prvdr_num"].nunique()
    if n_unique != n:
        dups = df[df.duplicated("prvdr_num", keep=False)]
        out.append(("FAIL",
                    f"{n - n_unique} duplicate CCNs — {len(dups)} affected rows. "
                    f"Sample: {dups['prvdr_num'].head(5).tolist()}"))
    else:
        out.append(("OK", f"CCNs unique ({n_unique:,})"))

    # CCN format — should be 6 chars, all digits
    bad_ccn = df[~df["prvdr_num"].str.match(r"^\d{6}$", na=False)]
    if len(bad_ccn):
        out.append(("WARN",
                    f"{len(bad_ccn)} CCNs not 6-digit format — "
                    f"sample: {bad_ccn['prvdr_num'].head(3).tolist()}"))
    else:
        out.append(("OK", "all CCNs are 6-digit numeric"))

    # Address completeness — anything missing state, ZIP, city, or address blocks downstream geocoding
    for col in ["st_adr", "city_name", "zip_cd"]:
        n_missing = df[col].isna().sum()
        if n_missing:
            out.append(("WARN", f"{n_missing} rows missing {col}"))

    # PCI capability distribution — derived from cath lab fields
    # Code 1 or 3 = on-site cath lab; this is our PCI capability candidate set
    pci_by_srvc = df["crdc_cthrtztn_lab_srvc_cd"].isin(["1", "3"]).sum()
    out.append(("OK", f"PCI candidates by cath lab service code (1 or 3): {pci_by_srvc:,}"))

    # Room count: hospitals with crdc_cthrtztn_prcdr_rooms_cnt >= 1
    rooms = pd.to_numeric(df["crdc_cthrtztn_prcdr_rooms_cnt"], errors="coerce").fillna(0)
    pci_by_rooms = (rooms >= 1).sum()
    out.append(("OK", f"PCI candidates by cath lab room count (>= 1): {pci_by_rooms:,}"))

    # Concordance between the two PCI signals
    has_srvc = df["crdc_cthrtztn_lab_srvc_cd"].isin(["1", "3"])
    has_room = rooms >= 1
    n_both = (has_srvc & has_room).sum()
    n_srvc_no_room = (has_srvc & ~has_room).sum()
    n_room_no_srvc = (~has_srvc & has_room).sum()
    out.append(("OK", f"PCI signal concordance: both={n_both:,}  srvc-only={n_srvc_no_room:,}  rooms-only={n_room_no_srvc:,}"))

    # Bed count sanity
    beds = pd.to_numeric(df["bed_cnt"], errors="coerce")
    out.append(("OK",
                f"bed count: median {beds.median():.0f}, "
                f"mean {beds.mean():.0f}, max {int(beds.max())}, "
                f"missing {beds.isna().sum()}"))

    # Per-state hospital counts — flag any state with implausibly few
    state_counts = df["state_cd"].value_counts()
    if state_counts.min() < 5:
        bad = state_counts[state_counts < 5].to_dict()
        out.append(("WARN", f"states with very few hospitals (could indicate data gap): {bad}"))

    return out


EXPECTED_IPPS_COLS = [
    "Rndrng_Prvdr_CCN", "Rndrng_Prvdr_Org_Name",
    "Rndrng_Prvdr_City", "Rndrng_Prvdr_St",
    "Rndrng_Prvdr_State_FIPS", "Rndrng_Prvdr_Zip5",
    "Rndrng_Prvdr_State_Abrvtn",
    "Rndrng_Prvdr_RUCA", "Rndrng_Prvdr_RUCA_Desc",
    "DRG_Cd", "DRG_Desc", "Tot_Dschrgs",
    "Avg_Submtd_Cvrd_Chrg", "Avg_Tot_Pymt_Amt", "Avg_Mdcr_Pymt_Amt",
]


def validate_cms_ipps() -> list[tuple[str, str]]:
    out: list[tuple[str, str]] = []
    matches = sorted((RAW / "cms_ipps").glob("cms_ipps_drg_*.csv"))
    if not matches:
        return [("WARN", "cms_ipps: not yet uploaded — see national/data/README.md §3")]
    if len(matches) > 1:
        out.append(("WARN", f"multiple cms_ipps files: {[m.name for m in matches]}; using newest"))
    path = matches[-1]
    out.append(("OK", f"file: {path.name} ({path.stat().st_size/1e6:.2f} MB)"))

    df = pd.read_csv(path, dtype=str)

    if list(df.columns) != EXPECTED_IPPS_COLS:
        out.append(("FAIL",
                    f"column mismatch — got {list(df.columns)}, "
                    f"expected {EXPECTED_IPPS_COLS}"))
        return out
    out.append(("OK", f"columns match expected schema ({len(df.columns)})"))

    n = len(df)
    out.append(("OK", f"row count: {n:,}"))
    if not (2_500 <= n <= 20_000):
        out.append(("WARN", f"row count outside expected 2,500–20,000: {n:,}"))

    # DRG distribution. We expect 280/281/282 (AMI severity tiers).
    # 246/247 (PCI procedures) are documented as absent from this PUF — see MANIFEST.
    drg_counts = df["DRG_Cd"].value_counts().sort_index()
    out.append(("OK", "DRG distribution: " + ", ".join(f"{k}={v:,}" for k, v in drg_counts.items())))
    expected_drgs = {"280", "281", "282"}
    actual_drgs = set(drg_counts.index)
    missing = expected_drgs - actual_drgs
    if missing:
        out.append(("FAIL", f"missing expected AMI DRGs: {missing}"))
    if "246" in actual_drgs or "247" in actual_drgs:
        out.append(("WARN",
                    "DRG 246/247 present — MANIFEST note about PCI DRG absence may be outdated"))

    # State coverage — should be 49 CONUS after prep filter
    bad_state = df[~df["Rndrng_Prvdr_State_Abrvtn"].isin(CONUS_STATE_CD)]
    if len(bad_state):
        out.append(("FAIL",
                    f"{len(bad_state)} rows with non-CONUS state: "
                    f"{bad_state['Rndrng_Prvdr_State_Abrvtn'].value_counts().to_dict()}"))
    else:
        out.append(("OK", f"all rows in CONUS whitelist ({df['Rndrng_Prvdr_State_Abrvtn'].nunique()} distinct states)"))

    # CCN format — should be 6 chars, all digits (or with F suffix for sub-units)
    bad_ccn = df[~df["Rndrng_Prvdr_CCN"].str.match(r"^\d{6}[A-Z]?$", na=False)]
    if len(bad_ccn):
        out.append(("WARN",
                    f"{len(bad_ccn)} CCNs not in standard format — "
                    f"sample: {bad_ccn['Rndrng_Prvdr_CCN'].head(3).tolist()}"))

    n_hospitals = df["Rndrng_Prvdr_CCN"].nunique()
    out.append(("OK", f"distinct hospitals (CCNs): {n_hospitals:,}"))

    # Per-DRG hospital coverage
    for drg in sorted(actual_drgs):
        n_hosp = df[df["DRG_Cd"] == drg]["Rndrng_Prvdr_CCN"].nunique()
        n_dis = pd.to_numeric(df[df["DRG_Cd"] == drg]["Tot_Dschrgs"], errors="coerce").sum()
        out.append(("OK", f"  DRG {drg}: {n_hosp:,} hospitals, {int(n_dis):,} total discharges"))

    # Cross-reference with PoS — how many IPPS hospitals are in the PoS active list?
    pos_path = sorted((RAW / "cms_pos").glob("cms_pos_*.csv"))
    if pos_path:
        pos = pd.read_csv(pos_path[-1], dtype=str)
        ipps_ccns = set(df["Rndrng_Prvdr_CCN"].unique())
        pos_ccns = set(pos["prvdr_num"].unique())
        n_match = len(ipps_ccns & pos_ccns)
        n_only_ipps = len(ipps_ccns - pos_ccns)
        n_only_pos = len(pos_ccns - ipps_ccns)
        pct_pos_in_ipps = n_match / len(pos_ccns) * 100
        pct_ipps_in_pos = n_match / len(ipps_ccns) * 100
        out.append(("OK", f"PoS↔IPPS join: {n_match:,} CCN match  ({pct_pos_in_ipps:.1f}% of PoS, {pct_ipps_in_pos:.1f}% of IPPS)"))
        out.append(("OK", f"  hospitals in IPPS but not active PoS: {n_only_ipps:,} (likely terminated or different CCN format)"))
        out.append(("OK", f"  hospitals in PoS but not IPPS: {n_only_pos:,} (no AMI volume in FY2024 PUF, likely <11 discharges suppressed)"))

    return out




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
