"""Six pre-registered sensitivity analyses per pre_registration.md D8 (amended).

STEMI count throughout this script is:
    stemi_per_yr = adult_pop_20plus * INCIDENCE_RATE
where INCIDENCE_RATE = 0.001 STEMI per adult aged 20+ per year (AHA Heart
Disease and Stroke Statistics 2024) and adult_pop_20plus comes from ACS
2019-2023 5-year table B01001 via 01b_prepare_acs_age.py. This is the
methodology adopted in pre_registration.md Amendment 2026-05-08-C; see
also REPRODUCIBILITY.md D8.

The all-ages `population` column is used only as a county-classification
input for the S4 metropolitan multiplier (where the urban/suburban/rural
threshold is defined on total county population in the FHWA / INRIX
literature, not adult population).

Memory-efficient implementation: avoids merging the 17.6M-pair drive-time
matrix with hospital metadata. Instead uses ccn-keyed lookup sets to filter
the matrix before any groupby. drive_time_sec is cast to int32 for ~50%
memory savings on the matrix.
"""
from __future__ import annotations

from pathlib import Path
import pandas as pd
import numpy as np

REPO = Path(__file__).resolve().parents[2]
PROC = REPO / "national" / "data" / "processed"

# STEMI per adult aged 20+ per year. See REPRODUCIBILITY.md D8 / pre_registration
# Amendment 2026-05-08-C.
INCIDENCE_RATE = 0.001


def competitive_pop_via_ccn_filter(dt: pd.DataFrame, allowed_ccns: set,
                                    bg_pop_map: dict, threshold_sec: int = 900) -> tuple[int, int]:
    """Compute (stemi_pop, n_competitive_bgs) with only the allowed CCNs as candidates.

    Memory-efficient: filters dt by ccn first (small mask), then sorts and ranks.
    """
    # Filter rows where ccn is in allowed set
    mask = dt["ccn"].isin(allowed_ccns)
    sub = dt.loc[mask, ["bg_id", "drive_time_sec"]].copy()
    if len(sub) == 0:
        return 0, 0
    # For each BG, get top-2 drive times (smallest = nearest)
    sub.sort_values(["bg_id", "drive_time_sec"], inplace=True)
    sub["rank"] = sub.groupby("bg_id").cumcount()
    top2 = sub[sub["rank"] < 2]
    if len(top2) == 0:
        return 0, 0
    # Pivot: for each BG, get t1 and t2
    pivot = top2.pivot_table(
        index="bg_id", columns="rank", values="drive_time_sec", aggfunc="first")
    # Only consider BGs with both t1 (rank 0) and t2 (rank 1)
    if 1 not in pivot.columns:
        return 0, 0
    pivot = pivot.dropna(subset=[1])
    margin = pivot[1] - pivot[0]
    competitive_bgs = pivot.index[margin <= threshold_sec]
    pop = sum(bg_pop_map.get(b, 0) for b in competitive_bgs)
    return pop, len(competitive_bgs)


def main() -> int:
    print("loading...")
    zones = pd.read_parquet(PROC / "zones_classified.parquet")
    hosp = pd.read_parquet(PROC / "hospitals_classified.parquet")
    dt = pd.read_parquet(PROC / "drive_times.parquet")
    geocoded = pd.read_parquet(PROC / "hospitals_geocoded.parquet")
    print(f"  {len(zones):,} BGs, {len(hosp):,} hospitals, {len(dt):,} drive-time pairs")

    # Memory: cast drive_time_sec to int32
    dt["drive_time_sec"] = dt["drive_time_sec"].astype("int32")

    # Adult-population-20+ map keyed on bg_id; this is the STEMI rate
    # denominator for every sensitivity that uses competitive_pop_via_ccn_filter.
    bg_pop_map = dict(zip(zones["bg_id"], zones["adult_pop_20plus"]))

    # Pre-compute hospital subsets we'll need
    tier_a_ccns = set(hosp.loc[hosp["tier"] == "A", "ccn"])
    concordant_ccns = set(hosp.loc[hosp["pci_signal_concordant"] == True, "ccn"])
    street_ccns = set(geocoded.loc[
        geocoded["precision_tier"].isin(["exact", "non_exact"]), "ccn"])
    print(f"  tier_a_ccns: {len(tier_a_ccns)}")
    print(f"  concordant_ccns (Tier A AND room count ≥ 1): {len(concordant_ccns)}")
    print(f"  street-level geocoded ccns (any tier): {len(street_ccns)}")

    # Baseline: 15-min margin, 0.001/adult/yr rate, all Tier A hospitals,
    # all geocoding precision tiers. Reads from is_competitive_15 already
    # in zones_classified; multiplies adult population (not all-ages).
    baseline_adult = zones.loc[zones["is_competitive_15"].fillna(False), "adult_pop_20plus"].sum()
    baseline_stemi = baseline_adult * INCIDENCE_RATE
    print(f"\nbaseline: {int(baseline_stemi):,} STEMI/yr "
          f"({int(baseline_adult):,} adults 20+ in 15-min competitive zones)")

    results = []

    def add(name: str, group: str, description: str, stemi: float):
        delta_pct = (stemi - baseline_stemi) / baseline_stemi * 100
        within = abs(delta_pct) <= 25.0
        results.append({
            "sensitivity": name,
            "group": group,
            "description": description,
            "stemi_per_yr": int(round(stemi)),
            "pct_change_vs_baseline": round(delta_pct, 1),
            "within_25pct": within,
        })

    add("baseline", "baseline",
        "15-min margin, 0.001/adult/yr rate x ACS 20+ adult pop, all Tier A hospitals, all precision tiers",
        baseline_stemi)

    # S2: threshold sweep
    print("\nS2 — competitive margin threshold sweep:")
    for k in (10, 15, 20):
        adult = zones.loc[zones[f"is_competitive_{k}"].fillna(False), "adult_pop_20plus"].sum()
        stemi = adult * INCIDENCE_RATE
        add(f"S2_margin_{k}min", "S2", f"competitive margin <= {k} min", stemi)
        print(f"  <={k} min: {int(stemi):>10,} STEMI/yr ({(stemi-baseline_stemi)/baseline_stemi*100:+.1f}%)")

    # S3: incidence sweep
    # Note: 0.0008 corresponds to the briefly-used calibrated rate (Amendment
    # 2026-05-08-C interim, superseded). Kept as a sensitivity bound so the
    # absolute count under the calibration approach is reproducible.
    print("\nS3 — STEMI incidence rate sweep (per-adult rates):")
    for r in (0.0008, 0.0010, 0.0012):
        stemi = baseline_adult * r
        add(f"S3_rate_{r:.4f}", "S3", f"STEMI incidence {r:.4f}/adult/yr", stemi)
        print(f"  rate {r:.4f}: {int(stemi):>10,} STEMI/yr ({(stemi-baseline_stemi)/baseline_stemi*100:+.1f}%)")

    # S5: same-state-only
    print("\nS5 — same-state-only subset:")
    mask = zones["is_competitive_15"].fillna(False) & (~zones["cross_state"].fillna(False))
    adult = zones.loc[mask, "adult_pop_20plus"].sum()
    stemi = adult * INCIDENCE_RATE
    add("S5_same_state_only", "S5",
        "exclude cross-state competitive zones", stemi)
    print(f"  {int(stemi):>10,} STEMI/yr ({(stemi-baseline_stemi)/baseline_stemi*100:+.1f}%)")

    # S6: Tier A concordant subset
    print("\nS6 — Tier A concordant inclusion criterion:")
    pop_s6, n_bg_s6 = competitive_pop_via_ccn_filter(
        dt, concordant_ccns, bg_pop_map, threshold_sec=15*60)
    stemi = pop_s6 * INCIDENCE_RATE
    add("S6_tier_a_concordant", "S6",
        "Tier A = cath service code 1|3 AND room count ≥ 1", stemi)
    print(f"  {int(stemi):>10,} STEMI/yr in {n_bg_s6:,} competitive BGs "
          f"({(stemi-baseline_stemi)/baseline_stemi*100:+.1f}%)")

    # S1: precision-tier filter — street-level Tier A only
    print("\nS1 — precision-tier filter (street-level only):")
    s1_ccns = tier_a_ccns & street_ccns
    print(f"  Tier A AND street-level: {len(s1_ccns)}")
    pop_s1, n_bg_s1 = competitive_pop_via_ccn_filter(
        dt, s1_ccns, bg_pop_map, threshold_sec=15*60)
    stemi = pop_s1 * INCIDENCE_RATE
    add("S1_street_level_only", "S1",
        "Tier A hospitals at street-level precision only "
        "(drop zip_centroid + zip_prefix tiers)", stemi)
    print(f"  {int(stemi):>10,} STEMI/yr in {n_bg_s1:,} competitive BGs "
          f"({(stemi-baseline_stemi)/baseline_stemi*100:+.1f}%)")

    # S4: AM peak multiplier — apply per-BG multiplier to drive times, re-rank.
    # County urban/suburban/rural classification uses ALL-AGES population
    # (the FHWA / INRIX literature defines the metro-pop thresholds on total
    # county population, not adult-only). Once classified, the STEMI count
    # within reclassified competitive zones uses adult population via
    # bg_pop_map (built from adult_pop_20plus above).
    print("\nS4 — AM peak metropolitan multiplier:")
    print("  county-pop-based proxy: >1M -> x1.30, 250k-1M -> x1.15, <250k -> x1.05")
    zones["county_fips"] = zones["STATEFP"] + zones["COUNTYFP"]
    county_pop = zones.groupby("county_fips")["population"].sum()
    def _mult(cp):
        if cp >= 1_000_000:
            return 1.30
        elif cp >= 250_000:
            return 1.15
        return 1.05
    county_mult = county_pop.apply(_mult)
    bg_to_mult = dict(zip(zones["bg_id"], zones["county_fips"].map(county_mult)))

    # Apply multiplier and re-rank (Tier A only)
    dt_a = dt[dt["ccn"].isin(tier_a_ccns)].copy()
    dt_a["mult"] = dt_a["bg_id"].map(bg_to_mult).astype("float32")
    dt_a["drive_time_sec"] = (dt_a["drive_time_sec"] * dt_a["mult"]).astype("int32")
    dt_a.drop(columns=["mult"], inplace=True)

    pop_s4, n_bg_s4 = competitive_pop_via_ccn_filter(
        dt_a, tier_a_ccns, bg_pop_map, threshold_sec=15*60)
    stemi = pop_s4 * INCIDENCE_RATE
    add("S4_am_peak_multiplier", "S4",
        "AM peak metro multiplier: drive times × 1.30 (urban) / 1.15 (suburban) / 1.05 (rural)",
        stemi)
    print(f"  {int(stemi):>10,} STEMI/yr in {n_bg_s4:,} competitive BGs "
          f"({(stemi-baseline_stemi)/baseline_stemi*100:+.1f}%)")

    del dt_a  # free memory

    # =====================================================================
    print("\n=== SENSITIVITY TABLE ===")
    df_out = pd.DataFrame(results)
    df_out.to_csv(PROC / "sensitivity_table.csv", index=False)
    out_dir = REPO / "national" / "outputs" / "tables"
    out_dir.mkdir(parents=True, exist_ok=True)
    df_out.to_csv(out_dir / "sensitivity_table.csv", index=False)
    print(df_out.to_string(index=False, max_colwidth=70))

    print(f"\n=== ROBUSTNESS PER D8 ===")
    non_baseline = df_out[df_out["sensitivity"] != "baseline"]
    by_group = non_baseline.groupby("group")["within_25pct"].all()
    n_robust = by_group.sum()
    n_total = len(by_group)
    print(f"\n  Per-group robustness:")
    for grp, ok in by_group.items():
        flag = "✓ ROBUST" if ok else "⚠ VIOLATION"
        worst = non_baseline.loc[non_baseline["group"] == grp, "pct_change_vs_baseline"].abs().max()
        print(f"    {grp}: {flag}  (worst Δ = {worst:.1f}%)")
    print(f"\n  Robust groups: {n_robust} of {n_total}")
    print(f"  D8 requires ≥4 of 6 — {'✓ headline robust' if n_robust >= 4 else '⚠ headline NOT robust, methods iteration required'}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
