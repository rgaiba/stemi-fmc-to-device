"""Six pre-registered sensitivity analyses per pre_registration.md D8.

Each sensitivity recomputes the headline metric (annual STEMI patients in
15-min competitive zones) under a modified assumption and reports the
percent change vs the baseline (260,549 STEMI/yr). Per D8, the headline
must hold within ±25% under at least 4 of 6 to be considered robust.

Output:
  national/data/processed/sensitivity_table.csv
  national/outputs/tables/sensitivity_table.csv  (also)

Sensitivities (per pre_registration.md D8 amended):
  1. Precision-tier filter — drop zip_centroid + zip_prefix hospitals
  2. Competitive-margin sweep — 10 / 15 / 20 min
  3. STEMI incidence sweep — 0.0008 / 0.0010 / 0.0012
  4. AM peak metropolitan multiplier (Amendment 2026-05-08-A)
  5. Same-state-only subset (exclude cross-state competitive zones)
  6. Tier A inclusion criterion (concordant subset only)
"""
from __future__ import annotations

from pathlib import Path
import pandas as pd
import numpy as np

REPO = Path(__file__).resolve().parents[2]
PROC = REPO / "national" / "data" / "processed"

INCIDENCE_RATE = 0.001  # per Amendment 2026-05-08-B
NON_CONUS = {"02", "15", "60", "66", "69", "72", "78"}


def compute_t1t2_competitive(dt_subset: pd.DataFrame, threshold_sec: int = 900) -> pd.Series:
    """Given a (filtered) drive-time matrix, compute per-BG is_competitive flag.

    Returns a pandas Series indexed by bg_id with True where T2_PCI - T1_PCI <= threshold.
    Only includes BGs that have at least 2 PCI hospitals reachable.
    """
    sorted_dt = dt_subset.sort_values(["bg_id", "drive_time_sec"])
    sorted_dt["rank"] = sorted_dt.groupby("bg_id").cumcount()
    top2 = sorted_dt[sorted_dt["rank"] < 2]
    pivot = top2.pivot_table(
        index="bg_id", columns="rank", values="drive_time_sec", aggfunc="first")
    pivot.columns = [f"t{i+1}" for i in pivot.columns]
    if "t2" not in pivot.columns:
        return pd.Series(dtype=bool)
    pivot["margin"] = pivot["t2"] - pivot["t1"]
    return pivot["margin"] <= threshold_sec


def main() -> int:
    print("loading...")
    zones = pd.read_parquet(PROC / "zones_classified.parquet")
    hosp = pd.read_parquet(PROC / "hospitals_classified.parquet")
    dt = pd.read_parquet(PROC / "drive_times.parquet")
    geocoded = pd.read_parquet(PROC / "hospitals_geocoded.parquet")
    print(f"  {len(zones):,} BGs, {len(hosp):,} hospitals, {len(dt):,} drive-time pairs")

    bg_pop = dict(zip(zones["bg_id"], zones["population"]))

    # Attach tier + RUCA + state to drive-time pairs once
    dt = dt.merge(
        hosp[["ccn", "tier", "fips_state_cd", "ruca", "pci_signal_concordant"]],
        on="ccn", how="left",
    )
    print(f"  drive-time pairs after tier merge: {len(dt):,}")

    # Baseline: 15-min margin, 0.001 rate, all Tier A hospitals
    baseline_pop = zones.loc[zones["is_competitive_15"].fillna(False), "population"].sum()
    baseline_stemi = baseline_pop * INCIDENCE_RATE
    print(f"\nbaseline: {int(baseline_stemi):,} STEMI/yr")

    results = []

    def add(name: str, description: str, stemi: float, group: str):
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

    add("baseline", "15-min margin, 0.001 rate, all hospitals, all precision tiers",
        baseline_stemi, "baseline")

    # =====================================================================
    # S2: Threshold sweep
    # =====================================================================
    print("\nS2 — competitive margin threshold sweep:")
    for k in (10, 15, 20):
        pop = zones.loc[zones[f"is_competitive_{k}"].fillna(False), "population"].sum()
        stemi = pop * INCIDENCE_RATE
        add(f"S2_margin_{k}min", f"competitive margin ≤ {k} min", stemi, "S2")
        print(f"  ≤{k} min: {int(stemi):>10,} STEMI/yr ({(stemi-baseline_stemi)/baseline_stemi*100:+.1f}%)")

    # =====================================================================
    # S3: Incidence rate sweep
    # =====================================================================
    print("\nS3 — STEMI incidence rate sweep (constant 15-min margin):")
    for r in (0.0008, 0.0010, 0.0012):
        stemi = baseline_pop * r
        add(f"S3_rate_{r:.4f}", f"STEMI incidence {r:.4f}/yr", stemi, "S3")
        print(f"  rate {r:.4f}: {int(stemi):>10,} STEMI/yr ({(stemi-baseline_stemi)/baseline_stemi*100:+.1f}%)")

    # =====================================================================
    # S5: Same-state-only (exclude cross-state competitive zones)
    # =====================================================================
    print("\nS5 — same-state-only subset:")
    mask = zones["is_competitive_15"].fillna(False) & (~zones["cross_state"].fillna(False))
    pop = zones.loc[mask, "population"].sum()
    stemi = pop * INCIDENCE_RATE
    add("S5_same_state_only", "exclude cross-state competitive zones (T1_PCI in BG's state)",
        stemi, "S5")
    print(f"  {int(stemi):>10,} STEMI/yr ({(stemi-baseline_stemi)/baseline_stemi*100:+.1f}%)")

    # =====================================================================
    # S6: Tier A concordant subset (cath service code AND room count ≥ 1)
    # =====================================================================
    print("\nS6 — Tier A concordant inclusion criterion:")
    concordant_ccns = set(hosp.loc[hosp["pci_signal_concordant"] == True, "ccn"])
    print(f"  hospitals in concordant subset: {len(concordant_ccns):,}")
    dt_a_concordant = dt[(dt["tier"] == "A") & dt["ccn"].isin(concordant_ccns)].copy()
    is_compet_concordant = compute_t1t2_competitive(dt_a_concordant, threshold_sec=15*60)
    pop = sum(bg_pop.get(bg, 0) for bg in is_compet_concordant[is_compet_concordant].index)
    stemi = pop * INCIDENCE_RATE
    add("S6_tier_a_concordant", "Tier A = cath service code 1|3 AND room count ≥ 1",
        stemi, "S6")
    print(f"  {int(stemi):>10,} STEMI/yr ({(stemi-baseline_stemi)/baseline_stemi*100:+.1f}%)")

    # =====================================================================
    # S1: Precision-tier filter (street-level only)
    # =====================================================================
    print("\nS1 — precision-tier filter (street-level only):")
    street_ccns = set(geocoded.loc[
        geocoded["precision_tier"].isin(["exact", "non_exact"]), "ccn"])
    print(f"  hospitals at street-level precision: {len(street_ccns):,}")
    dt_a_street = dt[(dt["tier"] == "A") & dt["ccn"].isin(street_ccns)].copy()
    is_compet_street = compute_t1t2_competitive(dt_a_street, threshold_sec=15*60)
    pop = sum(bg_pop.get(bg, 0) for bg in is_compet_street[is_compet_street].index)
    stemi = pop * INCIDENCE_RATE
    add("S1_street_level_only", "drop hospitals at zip_centroid + zip_prefix precision tiers",
        stemi, "S1")
    print(f"  {int(stemi):>10,} STEMI/yr ({(stemi-baseline_stemi)/baseline_stemi*100:+.1f}%)")

    # =====================================================================
    # S4: AM peak metro multiplier (Amendment 2026-05-08-A)
    # =====================================================================
    print("\nS4 — AM peak metropolitan multiplier:")
    print("  Using county total population as urbanicity proxy:")
    print("    >1M pop → factor 1.30 (urban core)")
    print("    250k-1M → factor 1.15 (suburban)")
    print("    <250k  → factor 1.05 (rural)")

    # Compute county pop totals
    zones["county_fips"] = zones["STATEFP"] + zones["COUNTYFP"]
    county_pop = zones.groupby("county_fips")["population"].sum().to_dict()

    # Build BG → multiplier mapping
    def bg_multiplier(row):
        cp = county_pop.get(row["county_fips"], 0)
        if cp >= 1_000_000:
            return 1.30
        elif cp >= 250_000:
            return 1.15
        return 1.05

    zones["am_multiplier"] = zones.apply(bg_multiplier, axis=1)

    # Apply multiplier to drive times by joining BG → multiplier
    bg_mult_map = dict(zip(zones["bg_id"], zones["am_multiplier"]))
    dt_a = dt[dt["tier"] == "A"].copy()
    dt_a["mult"] = dt_a["bg_id"].map(bg_mult_map)
    dt_a["drive_time_peak_sec"] = (dt_a["drive_time_sec"] * dt_a["mult"].fillna(1.0)).astype(int)

    # Re-rank with peak times
    dt_a_peak = dt_a.rename(columns={"drive_time_sec": "_orig",
                                      "drive_time_peak_sec": "drive_time_sec"}).copy()
    is_compet_peak = compute_t1t2_competitive(dt_a_peak[["bg_id", "drive_time_sec"]],
                                               threshold_sec=15*60)
    pop = sum(bg_pop.get(bg, 0) for bg in is_compet_peak[is_compet_peak].index)
    stemi = pop * INCIDENCE_RATE
    add("S4_am_peak_multiplier",
        "AM peak: drive times × 1.30 (urban) / 1.15 (suburban) / 1.05 (rural)",
        stemi, "S4")
    print(f"  {int(stemi):>10,} STEMI/yr ({(stemi-baseline_stemi)/baseline_stemi*100:+.1f}%)")

    # =====================================================================
    # Output table
    # =====================================================================
    print("\n=== SENSITIVITY TABLE ===")
    df_out = pd.DataFrame(results)
    df_out.to_csv(PROC / "sensitivity_table.csv", index=False)
    out_dir = REPO / "national" / "outputs" / "tables"
    out_dir.mkdir(parents=True, exist_ok=True)
    df_out.to_csv(out_dir / "sensitivity_table.csv", index=False)

    print(df_out.to_string(index=False, max_colwidth=70))

    # Robustness summary per D8
    non_baseline = df_out[df_out["sensitivity"] != "baseline"]
    n_within = non_baseline["within_25pct"].sum()
    n_total = len(non_baseline)
    print(f"\n=== ROBUSTNESS PER D8 ===")
    print(f"Sensitivities holding within ±25%: {n_within} of {n_total}")
    print(f"D8 threshold: ≥4 of 6 sensitivities (counting groups, not individual sweep variants)")
    # By group: any group with at least one violation flags the group
    by_group = df_out[df_out["sensitivity"] != "baseline"].groupby("group")["within_25pct"].all()
    print("\n  Per-group robustness:")
    for grp, ok in by_group.items():
        flag = "✓ ROBUST" if ok else "⚠ VIOLATION"
        print(f"    {grp}: {flag}")
    n_groups_robust = by_group.sum()
    print(f"\n  {n_groups_robust} of {len(by_group)} sensitivity groups robust (D8 requires ≥ 4 of 6)")
    if n_groups_robust >= 4:
        print(f"  ✓ Headline holds within pre-registered tolerance.")
    else:
        print(f"  ⚠ Headline does NOT hold within pre-registered tolerance — methods iteration required.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
