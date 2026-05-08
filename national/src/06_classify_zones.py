"""Classify each CONUS block group's competitive PCI catchment status.

Inputs:
  national/data/processed/drive_times.parquet      (17.6M ccn × bg_id pairs)
  national/data/processed/hospitals_classified.parquet  (4,408 hospitals, tier A/B)
  national/data/raw/cenpop2020/CenPop2020_Mean_BG.txt   (BG centroids + population)

Output:
  national/data/processed/zones_classified.parquet
    one row per CONUS BG (~238k), with:
      bg_id, STATEFP, COUNTYFP, TRACTCE, BLKGRPCE
      population
      T1_PCI: ccn_t1_pci, drive_t1_pci_sec, fips_t1_pci, state_t1_pci
      T2_PCI: ccn_t2_pci, drive_t2_pci_sec, fips_t2_pci, state_t2_pci
      competitive_margin_sec  (T2_PCI - T1_PCI)
      is_competitive_10, _15, _20  (margin <= 10/15/20 min)
      cross_state  (T1_PCI and T2_PCI in different states than BG)
      T1_any:  ccn_t1_any, drive_t1_any_sec, tier_t1_any
      is_pop2_candidate  (T1_any is Tier B AND T1_PCI reachable)

This is the canonical per-BG analytic file; downstream aggregations
(STEMI patient counts, choropleth, sensitivity analyses) read this.
"""
from __future__ import annotations

from pathlib import Path
import pandas as pd

REPO = Path(__file__).resolve().parents[2]
PROC = REPO / "national" / "data" / "processed"
RAW  = REPO / "national" / "data" / "raw"

NON_CONUS = {"02", "15", "60", "66", "69", "72", "78"}


def main() -> int:
    print("loading drive times...")
    dt = pd.read_parquet(PROC / "drive_times.parquet")
    print(f"  {len(dt):,} pairs, {dt['ccn'].nunique():,} hospitals, {dt['bg_id'].nunique():,} BGs")

    print("loading hospital classification...")
    hosp = pd.read_parquet(PROC / "hospitals_classified.parquet")
    print(f"  {len(hosp):,} hospitals (Tier A: {(hosp['tier']=='A').sum():,}, B: {(hosp['tier']=='B').sum():,})")

    # Attach tier + state to drive-time pairs
    dt = dt.merge(
        hosp[["ccn", "tier", "fips_state_cd", "state_cd"]],
        on="ccn", how="left",
    )

    # ---- Tier A only — compute T1_PCI / T2_PCI per BG ----
    print("computing T1_PCI / T2_PCI per BG...")
    dt_a = dt[dt["tier"] == "A"].sort_values(["bg_id", "drive_time_sec"]).copy()
    dt_a["rank"] = dt_a.groupby("bg_id").cumcount()
    top2 = dt_a[dt_a["rank"] < 2].copy()

    t1 = (top2[top2["rank"] == 0]
          .rename(columns={"ccn": "ccn_t1_pci",
                           "drive_time_sec": "drive_t1_pci_sec",
                           "fips_state_cd": "fips_t1_pci",
                           "state_cd": "state_t1_pci"})
          [["bg_id", "ccn_t1_pci", "drive_t1_pci_sec", "fips_t1_pci", "state_t1_pci"]])

    t2 = (top2[top2["rank"] == 1]
          .rename(columns={"ccn": "ccn_t2_pci",
                           "drive_time_sec": "drive_t2_pci_sec",
                           "fips_state_cd": "fips_t2_pci",
                           "state_cd": "state_t2_pci"})
          [["bg_id", "ccn_t2_pci", "drive_t2_pci_sec", "fips_t2_pci", "state_t2_pci"]])

    pci = t1.merge(t2, on="bg_id", how="left")
    pci["competitive_margin_sec"] = pci["drive_t2_pci_sec"] - pci["drive_t1_pci_sec"]

    print(f"  BGs with at least 1 PCI hospital reachable: {len(t1):,}")
    print(f"  BGs with at least 2 PCI hospitals reachable: {pci['drive_t2_pci_sec'].notna().sum():,}")

    # ---- T1_any (could be Tier B) per BG ----
    print("computing T1_any per BG...")
    dt_sorted = dt.sort_values(["bg_id", "drive_time_sec"])
    t1any = (dt_sorted.groupby("bg_id").first().reset_index()
             [["bg_id", "ccn", "drive_time_sec", "tier"]]
             .rename(columns={"ccn": "ccn_t1_any",
                              "drive_time_sec": "drive_t1_any_sec",
                              "tier": "tier_t1_any"}))
    print(f"  T1_any tier distribution: A={(t1any['tier_t1_any']=='A').sum():,}, B={(t1any['tier_t1_any']=='B').sum():,}")

    # ---- Load CenPop + filter CONUS, attach population ----
    print("loading CenPop2020 + attaching population...")
    cenpop = pd.read_csv(
        RAW / "cenpop2020" / "CenPop2020_Mean_BG.txt",
        encoding="utf-8-sig",
        dtype={"STATEFP": str, "COUNTYFP": str, "TRACTCE": str, "BLKGRPCE": str},
    )
    cenpop = cenpop[~cenpop["STATEFP"].isin(NON_CONUS)].copy()
    cenpop["bg_id"] = cenpop["STATEFP"] + cenpop["COUNTYFP"] + cenpop["TRACTCE"] + cenpop["BLKGRPCE"]
    print(f"  {len(cenpop):,} CONUS BGs in CenPop")

    # ---- Build the final per-BG dataframe ----
    print("merging...")
    result = (cenpop[["bg_id", "STATEFP", "COUNTYFP", "TRACTCE", "BLKGRPCE", "POPULATION"]]
              .merge(pci, on="bg_id", how="left")
              .merge(t1any, on="bg_id", how="left"))
    result.rename(columns={"POPULATION": "population"}, inplace=True)

    # Threshold flags (only meaningful where T2_PCI exists)
    for k in (10, 15, 20):
        result[f"is_competitive_{k}"] = (result["competitive_margin_sec"] <= k * 60)

    # Cross-state: T1_PCI's state FIPS ≠ BG's state FIPS
    result["cross_state"] = (result["fips_t1_pci"] != result["STATEFP"]) & result["fips_t1_pci"].notna()

    # Population 2 candidate: T1_any is Tier B AND T1_PCI is reachable
    result["is_pop2_candidate"] = (result["tier_t1_any"] == "B") & result["drive_t1_pci_sec"].notna()

    # Save
    out = PROC / "zones_classified.parquet"
    result.to_parquet(out, index=False)
    print(f"\nsaved {len(result):,} BGs → {out} ({out.stat().st_size/1e6:.1f} MB)")

    # ---- Summary print ----
    print(f"\n=== SUMMARY ===")
    n_total = len(result)
    pop_total = result["population"].sum()
    print(f"CONUS BGs:                  {n_total:>10,}  pop {pop_total:>13,}")

    has_t1 = result["drive_t1_pci_sec"].notna()
    has_t2 = result["drive_t2_pci_sec"].notna()
    print(f"BGs with ≥1 PCI reachable:  {has_t1.sum():>10,}  pop {result.loc[has_t1,'population'].sum():>13,}")
    print(f"BGs with ≥2 PCI reachable:  {has_t2.sum():>10,}  pop {result.loc[has_t2,'population'].sum():>13,}")

    print(f"\nCompetitive zones (T2-T1 ≤ threshold):")
    for k in (10, 15, 20):
        flag = result[f"is_competitive_{k}"].fillna(False)
        n_bg = flag.sum()
        n_pop = result.loc[flag, "population"].sum()
        n_stemi = int(n_pop * 0.004)
        print(f"  ≤{k:2d} min: {n_bg:>10,} BGs ({n_bg/n_total*100:5.1f}%), "
              f"pop {n_pop:>13,} ({n_pop/pop_total*100:5.1f}%), "
              f"~{n_stemi:>9,} STEMI/yr")

    print(f"\nCross-state subset (T1_PCI in different state than BG):")
    cross = result["cross_state"]
    n_cross = cross.sum()
    print(f"  {n_cross:,} BGs ({n_cross/n_total*100:.1f}% of CONUS)")
    n_cross_compet = (cross & result["is_competitive_15"].fillna(False)).sum()
    n_compet_15 = result["is_competitive_15"].fillna(False).sum()
    print(f"  Of competitive-zone BGs (≤15min): {n_cross_compet:,} cross-state "
          f"({n_cross_compet/n_compet_15*100:.1f}% of competitive zones)")

    print(f"\nPopulation 2 (nearest hospital is Tier B, Tier A reachable):")
    p2 = result["is_pop2_candidate"]
    n_p2 = p2.sum()
    n_p2_pop = result.loc[p2, "population"].sum()
    print(f"  {n_p2:>10,} BGs ({n_p2/n_total*100:5.1f}%), pop {n_p2_pop:>13,} ({n_p2_pop/pop_total*100:5.1f}%)")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
