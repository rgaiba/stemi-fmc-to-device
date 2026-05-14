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
WEB_DATA = REPO / "web" / "src" / "data"


def export_state(state_fips: str) -> dict:
    """Build per-BG T1/T2/delta JSON for one state. Returns summary stats."""
    state_fips = str(state_fips).zfill(2)
    print(f"\n=== Building state_bg_{state_fips}.json ===")

    # --- BG centroids ---------------------------------------------------
    cp = pd.read_csv(
        RAW / "cenpop2020" / "CenPop2020_Mean_BG.txt",
        dtype={"STATEFP": str, "COUNTYFP": str, "TRACTCE": str, "BLKGRPCE": str},
    )
    cp = cp[cp["STATEFP"] == state_fips].copy()
    cp["bg_id"] = cp["STATEFP"] + cp["COUNTYFP"] + cp["TRACTCE"] + cp["BLKGRPCE"]
    cp = cp[["bg_id", "LATITUDE", "LONGITUDE", "POPULATION"]].rename(
        columns={"LATITUDE": "lat", "LONGITUDE": "lon", "POPULATION": "total_pop"}
    )
    print(f"  centroids: {len(cp)} BGs in state {state_fips}")

    # --- ACS adult population (B01001 sum 20+) -------------------------
    acs = pd.read_csv(
        RAW / "acs5_2023" / "acs5_2023_b01001_bg.csv",
        dtype={"bg_id": str},
    )
    acs = acs[["bg_id", "adult_pop_20plus"]].rename(columns={"adult_pop_20plus": "adult_pop"})
    bg = cp.merge(acs, on="bg_id", how="left")
    bg["adult_pop"] = bg["adult_pop"].fillna(0).astype(int)
    print(f"  ACS join: {bg['adult_pop'].sum():,} adults 20+ in state")

    # --- Drive times, filtered to state's BGs and tier-A CCNs ---------
    dt = pd.read_parquet(PROC / "drive_times.parquet")
    with open(WEB_DATA / "hospitals_tier_a.json") as f:
        tier_a = {h["ccn"] for h in json.load(f)}
    dt = dt[dt["bg_id"].astype(str).str.startswith(state_fips)]
    dt = dt[dt["ccn"].isin(tier_a)].copy()
    print(f"  drive-time rows after tier-A filter: {len(dt):,}")

    # --- Per-BG: rank tier-A CCNs by drive time, take top 2 -----------
    # Split into two pivots so the numeric and string columns keep their
    # native dtypes (a combined pivot upcasts everything to object).
    dt = dt.sort_values(["bg_id", "drive_time_sec"], kind="mergesort")
    dt["rank"] = dt.groupby("bg_id").cumcount()
    top2 = dt[dt["rank"] < 2].copy()
    sec_pivot = top2.pivot(index="bg_id", columns="rank", values="drive_time_sec")
    sec_pivot.columns = ["t1_sec", "t2_sec"]
    ccn_pivot = top2.pivot(index="bg_id", columns="rank", values="ccn")
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


def main() -> None:
    targets = sys.argv[1:] or ["10"]   # default: Delaware
    summaries = [export_state(fips) for fips in targets]
    print("\n=== summary ===")
    for s in summaries:
        print(json.dumps(s, indent=2))


if __name__ == "__main__":
    main()
