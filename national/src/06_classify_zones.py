"""Classify each CONUS block group's competitive PCI catchment status.

Inputs:
  national/data/processed/drive_times.parquet           (17.6M ccn x bg_id pairs)
  national/data/processed/hospitals_classified.parquet  (4,408 hospitals, tier A/B)
  national/data/raw/cenpop2020/CenPop2020_Mean_BG.txt   (BG centroids + all-ages population)
  national/data/raw/acs5_2023/acs5_2023_b01001_bg.csv   (BG adult population aged 20+)

Output:
  national/data/processed/zones_classified.parquet
    one row per CONUS BG (~238k), with:
      bg_id, STATEFP, COUNTYFP, TRACTCE, BLKGRPCE
      population              (all-ages, from CenPop2020; kept for reference / choropleth scaling)
      adult_pop_20plus        (ACS 2019-2023 5-year B01001; STEMI rate denominator; see D8)
      T1_PCI: ccn_t1_pci, drive_t1_pci_sec, fips_t1_pci, state_t1_pci
      T2_PCI: ccn_t2_pci, drive_t2_pci_sec, fips_t2_pci, state_t2_pci
      competitive_margin_sec  (T2_PCI - T1_PCI)
      is_competitive_10, _15, _20  (margin <= 10/15/20 min)
      cross_state             (T1_PCI in different state FIPS than BG)
      T1_any:  ccn_t1_any, drive_t1_any_sec, tier_t1_any
      is_pop2_candidate       (T1_any is Tier B AND T1_PCI reachable)

STEMI count throughout this analysis is computed as:
    stemi_per_yr = adult_pop_20plus * INCIDENCE_RATE
where INCIDENCE_RATE = 0.001 STEMI per adult aged 20+ per year (AHA Heart
Disease and Stroke Statistics 2024). The all-ages `population` column is
NOT used for STEMI rate multiplication; it remains in the file for
choropleth scaling and reference only. See REPRODUCIBILITY.md "Analytic
decisions and changes" section, decision D8 and its change-log entries,
for the methodological history.

This is the canonical per-BG analytic file; downstream aggregations
(07_aggregate.py, 08_choropleth.py, 09_sensitivities.py) read this.
"""
from __future__ import annotations

from pathlib import Path
import pandas as pd

REPO = Path(__file__).resolve().parents[2]
PROC = REPO / "national" / "data" / "processed"
RAW  = REPO / "national" / "data" / "raw"

NON_CONUS = {"02", "15", "60", "66", "69", "72", "78"}

# STEMI incidence rate. Per AHA Heart Disease and Stroke Statistics 2024,
# applied to adults aged 20+ (NHANES adult definition). See REPRODUCIBILITY.md
# decision D8. Used here only for the diagnostic summary print at the end of
# this script; the canonical multiplication happens in 07_aggregate.py.
INCIDENCE_RATE = 0.001


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

    # ---- Tier A only; compute T1_PCI / T2_PCI per BG ----
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

    # ---- Load ACS adult population (aged 20+) ----
    # Source: ACS 2019-2023 5-year, table B01001. See 01b_prepare_acs_age.py
    # for the variable selection and CONUS filter rationale.
    print("loading ACS adult population (20+) ...")
    acs_path = RAW / "acs5_2023" / "acs5_2023_b01001_bg.csv"
    acs = pd.read_csv(acs_path, dtype={"bg_id": str})
    print(f"  {len(acs):,} BGs in ACS B01001 file")
    print(f"  total adult_pop_20plus: {int(acs['adult_pop_20plus'].sum()):,}")

    # ---- Build the final per-BG dataframe ----
    print("merging...")
    result = (cenpop[["bg_id", "STATEFP", "COUNTYFP", "TRACTCE", "BLKGRPCE", "POPULATION"]]
              .merge(pci, on="bg_id", how="left")
              .merge(t1any, on="bg_id", how="left")
              .merge(acs[["bg_id", "adult_pop_20plus"]], on="bg_id", how="left"))
    result.rename(columns={"POPULATION": "population"}, inplace=True)

    # Vintage drift between CenPop2020 and ACS 2019-2023 leaves a small number
    # of BGs in the analysis frame that the ACS file does not enumerate
    # (~tens of BGs out of ~238k). For these BGs, fall back to the CONUS
    # adult fraction (~0.752 from the ACS national totals) applied to the
    # CenPop all-ages count, so they do not silently drop out of the STEMI
    # denominator. The fallback is logged.
    missing_acs = result["adult_pop_20plus"].isna().sum()
    if missing_acs:
        adult_fraction = acs["adult_pop_20plus"].sum() / acs["total_pop_acs"].sum()
        print(f"  {missing_acs:,} BGs missing from ACS file "
              f"(vintage drift); imputing adult_pop = population * {adult_fraction:.4f}")
        mask = result["adult_pop_20plus"].isna()
        result.loc[mask, "adult_pop_20plus"] = (result.loc[mask, "population"] * adult_fraction).round().astype(int)
    result["adult_pop_20plus"] = result["adult_pop_20plus"].astype(int)

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
    # STEMI counts use adult_pop_20plus (ACS 20+) * INCIDENCE_RATE (0.001/adult/yr).
    # The all-ages `population` column is reported alongside for context.
    print(f"\n=== SUMMARY ===")
    n_total = len(result)
    pop_total = result["population"].sum()
    adult_total = result["adult_pop_20plus"].sum()
    print(f"CONUS BGs:                  {n_total:>10,}")
    print(f"  all-ages population:    {pop_total:>14,}")
    print(f"  adult population (20+): {adult_total:>14,}  ({adult_total/pop_total*100:.1f}%)")
    print(f"  implied national STEMI: {int(adult_total*INCIDENCE_RATE):>14,}/yr  "
          f"(rate {INCIDENCE_RATE:.4f}/adult/yr)")

    has_t1 = result["drive_t1_pci_sec"].notna()
    has_t2 = result["drive_t2_pci_sec"].notna()
    print(f"\nBGs with >=1 PCI reachable: {has_t1.sum():>10,}  "
          f"adult-pop {int(result.loc[has_t1,'adult_pop_20plus'].sum()):>13,}")
    print(f"BGs with >=2 PCI reachable: {has_t2.sum():>10,}  "
          f"adult-pop {int(result.loc[has_t2,'adult_pop_20plus'].sum()):>13,}")

    print(f"\nCompetitive zones (T2-T1 <= threshold):")
    for k in (10, 15, 20):
        flag = result[f"is_competitive_{k}"].fillna(False)
        n_bg = int(flag.sum())
        n_adult = int(result.loc[flag, "adult_pop_20plus"].sum())
        n_stemi = int(n_adult * INCIDENCE_RATE)
        print(f"  <={k:2d} min: {n_bg:>10,} BGs ({n_bg/n_total*100:5.1f}%), "
              f"adult-pop {n_adult:>13,} ({n_adult/adult_total*100:5.1f}%), "
              f"~{n_stemi:>9,} STEMI/yr")

    print(f"\nCross-state subset (T1_PCI in different state than BG):")
    cross = result["cross_state"]
    n_cross = int(cross.sum())
    print(f"  {n_cross:,} BGs ({n_cross/n_total*100:.1f}% of CONUS)")
    n_cross_compet = int((cross & result["is_competitive_15"].fillna(False)).sum())
    n_compet_15 = int(result["is_competitive_15"].fillna(False).sum())
    print(f"  Of competitive-zone BGs (<=15min): {n_cross_compet:,} cross-state "
          f"({n_cross_compet/n_compet_15*100:.1f}% of competitive zones)")

    print(f"\nPopulation 2 (nearest hospital is Tier B, Tier A reachable):")
    p2 = result["is_pop2_candidate"]
    n_p2 = int(p2.sum())
    n_p2_adult = int(result.loc[p2, "adult_pop_20plus"].sum())
    print(f"  {n_p2:>10,} BGs ({n_p2/n_total*100:5.1f}%), "
          f"adult-pop {n_p2_adult:>13,} ({n_p2_adult/adult_total*100:5.1f}%)")

    # ---- External validity check ----
    # The drive-time engine and the rate-times-denominator must each produce
    # numbers consistent with the published U.S. literature, otherwise the
    # competitive-zone claim built on top of them is not defensible. The two
    # checks below are the ones a reviewer at Circulation: CVQO is most
    # likely to perform mentally:
    #
    #   1. Implied national STEMI count vs AHA Heart Disease and Stroke
    #      Statistics 2024. Expected band: 250,000-280,000/yr.
    #
    #   2. Adult population within 60-min drive of nearest PCI hospital,
    #      vs Wang et al. (Circulation 2024) and Concannon et al.
    #      (Circ CVQO 2014). Expected band: 91-95% of adults.
    #
    # We also report 30-min, 90-min, and the median nearest-PCI drive time
    # so the supplement table is ready to lift.
    #
    # If a check lands outside its expected band, the script emits a WARN
    # but does not hard-fail; the analyst may have made a deliberate
    # methodological change (e.g., different matrix radius) that needs to
    # be reflected in the manuscript text.
    # Tolerance philosophy: the published estimates themselves carry
    # uncertainty (Wang 2024 reports a 4-percentage-point range; AHA HDSS
    # cites a 30k/yr range). The bands below add roughly ±2% of the
    # estimate or ±2 percentage points (whichever is larger) on each side
    # of the published range. A value strictly inside the published range
    # is naturally [OK]; a value outside the published range but inside
    # tolerance is [OK] with an "edge" note; a value outside tolerance
    # is [WARN].
    print(f"\n=== EXTERNAL VALIDITY CHECKS ===")
    implied_stemi = int(adult_total * INCIDENCE_RATE)
    print(f"\n  [1] Implied national STEMI count (rate x denominator)")
    print(f"      Computed:    {implied_stemi:>10,}/yr")
    print(f"      Published:   250,000-280,000/yr "
          f"(AHA Heart Disease and Stroke Statistics 2024)")
    pub_lo, pub_hi = 250_000, 280_000
    tol_lo, tol_hi = 240_000, 285_000           # ~+/-2% of published range
    if pub_lo <= implied_stemi <= pub_hi:
        print(f"      Status:      [OK]   inside published band")
    elif tol_lo <= implied_stemi <= tol_hi:
        edge = "low edge" if implied_stemi < pub_lo else "high edge"
        delta = abs(implied_stemi - (pub_lo if implied_stemi < pub_lo else pub_hi))
        print(f"      Status:      [OK]   {edge} of band ({delta:,} from nearest bound)")
    else:
        print(f"      Status:      [WARN] outside tolerance; reconcile rate or denominator")

    print(f"\n  [2] Adult population within drive-time of nearest PCI hospital")
    drive_min = result["drive_t1_pci_sec"] / 60
    for cutoff_min, label, pub_lo, pub_hi, tol_lo, tol_hi, expected_src in (
        # cutoff, published lo, published hi, tolerance lo, tolerance hi, source
        (30, "<= 30 min", 78, 82, 75, 85, "Concannon Circ CVQO 2014: ~80%"),
        (60, "<= 60 min", 91, 95, 89, 97, "Wang Circulation 2024: 91-95%"),
        (90, "<= 90 min", 96, 98, 94, 99, "follow-on access studies: ~96-98%"),
    ):
        flag = drive_min <= cutoff_min
        n_adult = int(result.loc[flag, "adult_pop_20plus"].sum())
        pct = n_adult / adult_total * 100
        if pub_lo <= pct <= pub_hi:
            status = "[OK]  "
        elif tol_lo <= pct <= tol_hi:
            status = "[OK*] "  # inside tolerance, outside published band
        else:
            status = "[WARN]"
        print(f"      {label:>10s}: {pct:5.1f}% of CONUS adults"
              f"   published {pub_lo}-{pub_hi}%   "
              f"{status}  ({expected_src})")

    median_min = drive_min.median()
    iqr_lo = drive_min.quantile(0.25)
    iqr_hi = drive_min.quantile(0.75)
    print(f"\n      median nearest-PCI drive time: {median_min:.1f} min   "
          f"IQR {iqr_lo:.1f}-{iqr_hi:.1f} min")
    print(f"      (published range: median 11-15 min in metro-weighted analyses)")

    n_no_pci_in_matrix = int(result["drive_t1_pci_sec"].isna().sum())
    print(f"\n      Remote tail: {n_no_pci_in_matrix:,} BGs have no PCI hospital in")
    print(f"      the matrix radius (~150 mi haversine). Reported as a manuscript")
    print(f"      footnote, not as 'unreachable' (the radius is a matrix-build")
    print(f"      parameter, not an access definition).")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
