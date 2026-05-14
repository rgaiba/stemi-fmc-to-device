"""Per-block-group T1 / T2 / T2-T1 export for the web 'States' page.

This script complements 07b_aggregate_strata.py (which aggregates BGs into
counties for CONUS-scale views). The States page operates at higher
resolution -- block-group centroids inside a single chosen state -- so it
needs a per-BG payload rather than a per-county aggregation.

For each block group in a target state:
  * T1 = drive time (sec) from BG centroid to the *nearest* tier-A
    PCI-capable hospital (CCN ranked #1 by drive_time_sec).
  * T2 = drive time to the second-nearest tier-A PCI hospital.
  * delta = T2 - T1 (seconds; minutes derived for the web payload).

A BG is "competitive" iff a second PCI hospital is reachable at all; BGs
with only one reachable tier-A hospital (or none) get T2 = null and are
rendered in a neutral fill on the States page (matching the Map page's
gray for ge30 counties).

Inputs:
  national/data/processed/drive_times.parquet      (ccn, bg_id, drive_time_sec)
  national/data/raw/cenpop2020/CenPop2020_Mean_BG.txt   (BG centroids)
  national/data/raw/acs5_2023/acs5_2023_b01001_bg.csv   (adult_pop_20plus per BG)
  web/src/data/hospitals_tier_a.json                 (1,588 PCI-capable CCNs)

Output:
  web/src/data/state_bg_<FIPS>.json
    [
      { "bg": "100030101001",
        "lat": 39.65, "lon": -75.71,
        "adult_pop": 612,
        "t1_min": 4.2, "t2_min": 9.8, "delta_min": 5.6,
        "ccn1": "080001", "ccn2": "080003" },
      ...
    ]

Usage:
  python national/src/10_state_bg_strata.py 10        # Delaware
  python national/src/10_state_bg_strata.py 10 37     # Delaware + NC

Sign convention: delta_min is always >= 0. The States page inverts the
encoding so that smaller delta_min reads as darker (more routing
leverage) -- matching Strata page semantics where darker counties =
more adults whose nearest two PCI hospitals are within X minutes.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd

REPO = Path(__file__).resolve().parents[2]
PROC = REPO / "national" / "data" / "processed"
RAW = REPO / "national" / "data" / "raw"
# State JSONs are static assets served lazily, not bundled by Vite, so
# they live in web/public/data/ (copied as-is to dist/) rather than
# web/src/data/ (eager-imported into the bundle). hospitals_tier_a.json
# is still in src/data because it IS imported into the main bundle.
WEB_DATA = REPO / "web" / "public" / "data"
HOSPITALS_JSON = REPO / "web" / "src" / "data" / "hospitals_tier_a.json"


# Module-level caches so a batch run over 50 states reads the centroid
# table, ACS table, hospital filter, and drive-times parquet exactly once
# rather than once per state (each parquet read is ~5s on a cold cache).
_CACHE: dict = {}


def _load_inputs():
    """Read the four input files into the module-level cache. Idempotent."""
    if _CACHE:
        return _CACHE
    print("Loading shared inputs (one-time)...")
    cp = pd.read_csv(
        RAW / "cenpop2020" / "CenPop2020_Mean_BG.txt",
        dtype={"STATEFP": str, "COUNTYFP": str, "TRACTCE": str, "BLKGRPCE": str},
    )
    cp["bg_id"] = cp["STATEFP"] + cp["COUNTYFP"] + cp["TRACTCE"] + cp["BLKGRPCE"]
    cp = cp[["STATEFP", "bg_id", "LATITUDE", "LONGITUDE", "POPULATION"]].rename(
        columns={"LATITUDE": "lat", "LONGITUDE": "lon", "POPULATION": "total_pop"}
    )
    acs = pd.read_csv(
        RAW / "acs5_2023" / "acs5_2023_b01001_bg.csv",
        dtype={"bg_id": str},
    )[["bg_id", "adult_pop_20plus"]].rename(columns={"adult_pop_20plus": "adult_pop"})
    with open(HOSPITALS_JSON) as f:
        tier_a = {h["ccn"] for h in json.load(f)}
    print(f"  loading drive_times.parquet ({(PROC / 'drive_times.parquet').stat().st_size / 1e6:.1f} MB)...")
    dt = pd.read_parquet(PROC / "drive_times.parquet")
    dt = dt[dt["ccn"].isin(tier_a)].copy()   # filter to tier-A once for all states
    print(f"  drive_times after tier-A filter: {len(dt):,} rows; {dt['bg_id'].nunique():,} BGs")
    # CT crosswalk: 2020 county-based BG -> 2023 planning-region (5-digit).
    # Needed because CenPop centroids and drive_times use county-based bg_ids
    # while ACS uses planning-region-based bg_ids; a direct join is empty.
    ct_cw = pd.read_csv(
        PROC / "ct_bg_to_planning_region.csv",
        dtype=str,
    )[["bg_id", "planning_region"]]
    _CACHE.update(cp=cp, acs=acs, tier_a=tier_a, dt=dt, ct_cw=ct_cw)
    return _CACHE


def _ct_adults_by_county_bg(cache: dict) -> dict:
    """Allocate CT planning-region-level ACS adults to each county-based
    BG by its share of CenPop total_pop within the same planning region.

    Returns a dict bg_id (12-digit county-based) -> adult_pop (rounded int).
    """
    # Aggregate ACS adults to planning region (the 5-digit prefix of the
    # planning-region-based bg_id IS the planning region FIPS).
    ct_acs = cache["acs"][cache["acs"]["bg_id"].str.startswith("09")].copy()
    ct_acs["pr"] = ct_acs["bg_id"].str[:5]
    pr_adults = ct_acs.groupby("pr")["adult_pop"].sum()

    # CenPop CT BGs joined to crosswalk for their planning region.
    cp_ct = cache["cp"][cache["cp"]["STATEFP"] == "09"].copy()
    cp_ct = cp_ct.merge(cache["ct_cw"], on="bg_id", how="left")
    # Total CenPop population per planning region (the allocation
    # denominator).
    pr_totpop = cp_ct.groupby("planning_region")["total_pop"].sum()

    cp_ct["pr_totpop"] = cp_ct["planning_region"].map(pr_totpop)
    cp_ct["pr_adults"] = cp_ct["planning_region"].map(pr_adults)
    # Proportional allocation: this BG's share of the PR's CenPop pop,
    # times the PR's total ACS adult population. Falls back to 0 if any
    # join key is missing (shouldn't happen given the crosswalk is
    # complete by construction).
    cp_ct["adult_pop"] = (
        (cp_ct["pr_adults"] * cp_ct["total_pop"] / cp_ct["pr_totpop"])
        .fillna(0)
        .round()
        .astype(int)
    )
    # Sanity check: per-PR sum after allocation should equal pr_adults
    # within rounding error.
    realloc_check = cp_ct.groupby("planning_region")["adult_pop"].sum()
    diffs = (realloc_check - pr_adults).abs()
    max_diff = diffs.max() if len(diffs) else 0
    if max_diff > 5:
        print(f"  [CT] WARNING: allocation drift up to {max_diff} adults in a PR")
    else:
        print(
            f"  [CT] allocated {cp_ct['adult_pop'].sum():,} adults to "
            f"{len(cp_ct)} BGs across {len(pr_totpop)} planning regions "
            f"(rounding drift <= {int(max_diff)} per PR)"
        )
    return dict(zip(cp_ct["bg_id"], cp_ct["adult_pop"]))


def export_state(state_fips: str) -> dict:
    """Build per-BG T1/T2/delta JSON for one state. Returns summary stats."""
    state_fips = str(state_fips).zfill(2)
    print(f"\n=== Building state_bg_{state_fips}.json ===")
    cache = _load_inputs()

    # --- BG centroids ---------------------------------------------------
    cp = cache["cp"][cache["cp"]["STATEFP"] == state_fips].copy()
    cp = cp.drop(columns=["STATEFP"])
    print(f"  centroids: {len(cp)} BGs in state {state_fips}")

    # --- ACS adult population (B01001 sum 20+) -------------------------
    # Connecticut's bg_id format differs between CenPop (2020 county-based)
    # and ACS (2023 planning-region-based) because of the Census Bureau's
    # 2022 county-to-planning-region transition. A direct ACS join yields
    # zero matches; instead, allocate planning-region adults to county
    # BGs proportionally by CenPop total_pop share. All other states use
    # the straight bg_id join.
    if state_fips == "09":
        ct_adults = _ct_adults_by_county_bg(cache)
        bg = cp.copy()
        bg["adult_pop"] = bg["bg_id"].map(ct_adults).fillna(0).astype(int)
    else:
        bg = cp.merge(cache["acs"], on="bg_id", how="left")
        bg["adult_pop"] = bg["adult_pop"].fillna(0).astype(int)
    print(f"  adult-pop join: {bg['adult_pop'].sum():,} adults 20+ in state")

    # --- Drive times, filtered to state's BGs (tier-A already applied) -
    dt = cache["dt"][cache["dt"]["bg_id"].astype(str).str.startswith(state_fips)].copy()
    print(f"  drive-time rows for state: {len(dt):,}")

    # --- Per-BG: rank tier-A CCNs by drive time, take top 2 -----------
    # Split into two pivots so the numeric and string columns keep their
    # native dtypes (a combined pivot upcasts everything to object).
    # Some BGs in remote states have only one PCI reachable within the
    # OSRM cutoff -- in that case the pivot only produces a rank-0 column;
    # we explicitly reindex to guarantee both columns exist.
    dt = dt.sort_values(["bg_id", "drive_time_sec"], kind="mergesort")
    dt["rank"] = dt.groupby("bg_id").cumcount()
    top2 = dt[dt["rank"] < 2].copy()
    sec_pivot = top2.pivot(index="bg_id", columns="rank", values="drive_time_sec")
    sec_pivot = sec_pivot.reindex(columns=[0, 1])
    sec_pivot.columns = ["t1_sec", "t2_sec"]
    ccn_pivot = top2.pivot(index="bg_id", columns="rank", values="ccn")
    ccn_pivot = ccn_pivot.reindex(columns=[0, 1])
    ccn_pivot.columns = ["ccn1", "ccn2"]
    pivoted = sec_pivot.join(ccn_pivot).reset_index()
    print(f"  per-BG top-2 ranked: {len(pivoted)} BGs")

    # --- Join centroids + ACS + ranking; derive minutes + delta -------
    out = bg.merge(pivoted, on="bg_id", how="left")
    out["t1_min"] = (out["t1_sec"] / 60.0).round(2)
    out["t2_min"] = (out["t2_sec"] / 60.0).round(2)
    out["delta_min"] = (out["t2_min"] - out["t1_min"]).round(2)
    # BGs with no reachable PCI hospital (no rank-0 row) get NaNs across
    # the t1/t2 columns; payload uses None so JS gets null.

    records = []
    for _, r in out.iterrows():
        rec = {
            "bg": r["bg_id"],
            "lat": round(float(r["lat"]), 5),
            "lon": round(float(r["lon"]), 5),
            "adult_pop": int(r["adult_pop"]),
        }
        if pd.notna(r["t1_min"]):
            rec["t1_min"] = float(r["t1_min"])
            rec["ccn1"] = str(r["ccn1"])
        else:
            rec["t1_min"] = None
            rec["ccn1"] = None
        if pd.notna(r["t2_min"]):
            rec["t2_min"] = float(r["t2_min"])
            rec["ccn2"] = str(r["ccn2"])
            rec["delta_min"] = float(r["delta_min"])
        else:
            rec["t2_min"] = None
            rec["ccn2"] = None
            rec["delta_min"] = None
        records.append(rec)

    out_path = WEB_DATA / f"state_bg_{state_fips}.json"
    with open(out_path, "w") as f:
        json.dump(records, f, separators=(",", ":"))
    sz = out_path.stat().st_size
    print(f"  wrote {out_path} ({sz / 1024:.1f} KB)")

    # --- Summary --------------------------------------------------------
    with_delta = out[out["delta_min"].notna()]
    one_hospital = out[out["t2_min"].isna() & out["t1_min"].notna()]
    no_hospital = out[out["t1_min"].isna()]
    return {
        "state_fips": state_fips,
        "n_bgs": len(out),
        "n_bgs_with_two_pci": len(with_delta),
        "n_bgs_one_pci_only": len(one_hospital),
        "n_bgs_no_pci": len(no_hospital),
        "adults_total": int(out["adult_pop"].sum()),
        "adults_with_two_pci": int(with_delta["adult_pop"].sum()),
        "delta_min_p25": float(with_delta["delta_min"].quantile(0.25)) if len(with_delta) else None,
        "delta_min_p50": float(with_delta["delta_min"].quantile(0.50)) if len(with_delta) else None,
        "delta_min_p75": float(with_delta["delta_min"].quantile(0.75)) if len(with_delta) else None,
    }


ALL_50_PLUS_DC = [
    "01", "02", "04", "05", "06", "08", "09", "10", "11", "12", "13", "15",
    "16", "17", "18", "19", "20", "21", "22", "23", "24", "25", "26", "27",
    "28", "29", "30", "31", "32", "33", "34", "35", "36", "37", "38", "39",
    "40", "41", "42", "44", "45", "46", "47", "48", "49", "50", "51", "53",
    "54", "55", "56",
]


def main() -> None:
    args = sys.argv[1:]
    if args and args[0] == "--all":
        targets = ALL_50_PLUS_DC
    else:
        targets = args or ["10"]   # default: Delaware
    summaries = [export_state(fips) for fips in targets]
    print("\n=== summary ===")
    for s in summaries:
        print(json.dumps(s, indent=2))


if __name__ == "__main__":
    main()
