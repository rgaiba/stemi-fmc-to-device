"""Aggregate per-BG zone classification -> state, county, and hospital rollups.

Inputs:
  national/data/processed/zones_classified.parquet    (per-BG analytic file with adult_pop_20plus)
  national/data/processed/hospitals_classified.parquet (hospital metadata)

Outputs:
  national/data/processed/state_summary.csv      (one row per CONUS state)
  national/data/processed/county_summary.csv     (one row per CONUS county; feeds choropleth)
  national/data/processed/top_hospitals.csv      (top N PCI hospitals by competitive-zone exposure)

STEMI count throughout this file:
    stemi_per_yr = adult_pop_20plus * INCIDENCE_RATE
where INCIDENCE_RATE = 0.001 STEMI per adult aged 20+ per year (AHA Heart
Disease and Stroke Statistics 2024). The all-ages `population` column is
retained in summaries as context, never multiplied by the rate. See
REPRODUCIBILITY.md decision D8 for the rate-and-denominator rationale.

System-level (chain) aggregation is deferred to Paper 2 — CMS PoS does not
include parent system identifiers, and the AHA Annual Survey was excluded
by the public-source constraint. Hospital-level aggregation is the
public-source-defensible substitute that feeds the manuscript's "top
hospitals serving competitive-zone catchment" table.
"""
from __future__ import annotations

from pathlib import Path
import pandas as pd

REPO = Path(__file__).resolve().parents[2]
PROC = REPO / "national" / "data" / "processed"

# STEMI per adult aged 20+ per year. See REPRODUCIBILITY.md D8.
INCIDENCE_RATE = 0.001

# State FIPS → 2-letter abbreviation
STATE_FIPS = {
    "01":"AL","04":"AZ","05":"AR","06":"CA","08":"CO","09":"CT","10":"DE","11":"DC",
    "12":"FL","13":"GA","16":"ID","17":"IL","18":"IN","19":"IA","20":"KS","21":"KY",
    "22":"LA","23":"ME","24":"MD","25":"MA","26":"MI","27":"MN","28":"MS","29":"MO",
    "30":"MT","31":"NE","32":"NV","33":"NH","34":"NJ","35":"NM","36":"NY","37":"NC",
    "38":"ND","39":"OH","40":"OK","41":"OR","42":"PA","44":"RI","45":"SC","46":"SD",
    "47":"TN","48":"TX","49":"UT","50":"VT","51":"VA","53":"WA","54":"WV","55":"WI","56":"WY",
}


def main() -> int:
    print("loading...")
    zones = pd.read_parquet(PROC / "zones_classified.parquet")
    hosp = pd.read_parquet(PROC / "hospitals_classified.parquet")
    print(f"  {len(zones):,} BGs, {len(hosp):,} hospitals")

    zones["is_competitive_15"] = zones["is_competitive_15"].fillna(False)
    zones["state_abbr"] = zones["STATEFP"].map(STATE_FIPS)
    # STEMI count uses adult population (20+), not all-ages population.
    zones["stemi_per_yr"] = zones["adult_pop_20plus"] * INCIDENCE_RATE

    # === State-level summary ===
    print("\n--- per-state aggregation ---")
    # Build a competitive-only frame once, then aggregate it; cleaner than
    # the prior nested-lambda pattern and avoids repeated boolean indexing.
    compet = zones[zones["is_competitive_15"]]
    by_state = zones.groupby("state_abbr").agg(
        total_bgs=("bg_id", "size"),
        total_pop=("population", "sum"),
        total_adult_pop=("adult_pop_20plus", "sum"),
        total_stemi_per_yr=("stemi_per_yr", "sum"),
        cross_state_bgs=("cross_state", "sum"),
    ).reset_index()
    state_compet = compet.groupby("state_abbr").agg(
        competitive_bgs=("bg_id", "size"),
        competitive_pop=("population", "sum"),
        competitive_adult_pop=("adult_pop_20plus", "sum"),
    ).reset_index()
    by_state = by_state.merge(state_compet, on="state_abbr", how="left").fillna(
        {"competitive_bgs": 0, "competitive_pop": 0, "competitive_adult_pop": 0}
    )
    by_state["competitive_bgs"] = by_state["competitive_bgs"].astype(int)
    by_state["competitive_stemi_per_yr"] = by_state["competitive_adult_pop"] * INCIDENCE_RATE
    by_state["pct_pop_in_competitive"] = (by_state["competitive_pop"] / by_state["total_pop"] * 100).round(1)
    by_state["pct_adult_in_competitive"] = (by_state["competitive_adult_pop"] / by_state["total_adult_pop"] * 100).round(1)
    by_state["pct_bgs_in_competitive"] = (by_state["competitive_bgs"] / by_state["total_bgs"] * 100).round(1)

    by_state = by_state.sort_values("competitive_stemi_per_yr", ascending=False)
    out_state = PROC / "state_summary.csv"
    by_state.to_csv(out_state, index=False)
    print(f"  saved: {out_state}")

    print("\n  Top 10 states by competitive-zone STEMI/yr:")
    cols = ["state_abbr", "total_adult_pop", "competitive_adult_pop", "pct_adult_in_competitive",
            "competitive_stemi_per_yr", "cross_state_bgs"]
    show = by_state[cols].head(10).copy()
    show["competitive_stemi_per_yr"] = show["competitive_stemi_per_yr"].round(0).astype(int)
    print(show.to_string(index=False))

    # === County-level summary (for choropleth) ===
    print("\n--- per-county aggregation (for choropleth) ---")
    zones["county_fips"] = zones["STATEFP"] + zones["COUNTYFP"]
    by_county = zones.groupby("county_fips").agg(
        total_bgs=("bg_id", "size"),
        total_pop=("population", "sum"),
        total_adult_pop=("adult_pop_20plus", "sum"),
        competitive_bgs=("is_competitive_15", "sum"),
    ).reset_index()
    county_compet = compet.groupby(compet["STATEFP"] + compet["COUNTYFP"]).agg(
        competitive_pop=("population", "sum"),
        competitive_adult_pop=("adult_pop_20plus", "sum"),
    ).reset_index().rename(columns={"index": "county_fips"})
    county_compet.columns = ["county_fips", "competitive_pop", "competitive_adult_pop"]
    by_county = by_county.merge(county_compet, on="county_fips", how="left").fillna(
        {"competitive_pop": 0, "competitive_adult_pop": 0}
    )
    by_county["competitive_bgs"] = by_county["competitive_bgs"].astype(int)
    by_county["pct_bgs_competitive"] = (by_county["competitive_bgs"] / by_county["total_bgs"] * 100).round(1)
    out_county = PROC / "county_summary.csv"
    by_county.to_csv(out_county, index=False)
    print(f"  saved: {out_county}  ({len(by_county):,} CONUS counties)")
    print(f"  pct_bgs_competitive distribution:")
    for pct in (0, 25, 50, 75, 90, 95, 100):
        print(f"    p{pct:>3}: {by_county['pct_bgs_competitive'].quantile(pct/100):>5.1f}%")

    # === Hospital-level: which Tier A hospitals serve the most competitive-zone STEMI? ===
    # For each Tier A hospital, count BGs where this hospital is T1_PCI AND BG is
    # in a 15-min competitive zone. STEMI count uses adult population (20+).
    print("\n--- top hospitals by competitive-zone catchment ---")
    competitive_t1 = zones[zones["is_competitive_15"] & zones["ccn_t1_pci"].notna()].copy()
    by_hosp = competitive_t1.groupby("ccn_t1_pci").agg(
        bgs_served=("bg_id", "size"),
        pop_served=("population", "sum"),
        adult_pop_served=("adult_pop_20plus", "sum"),
    ).reset_index().rename(columns={"ccn_t1_pci": "ccn"})
    by_hosp["stemi_per_yr"] = by_hosp["adult_pop_served"] * INCIDENCE_RATE

    # Attach hospital name + state for readability.
    #
    # IMPORTANT: ami_volume_2024 is intentionally EXCLUDED from the published
    # supplement (top_hospitals.csv). The two columns answer different
    # questions on different denominators and printing them side-by-side
    # invites a wrong inference:
    #   stemi_per_yr      = STEMI exposure in this hospital's competitive-zone
    #                       catchment, all-payer, derived from population x rate.
    #   ami_volume_2024   = Medicare fee-for-service-only AMI discharges (CMS
    #                       IPPS PUF), which is roughly 25-35% of true volume
    #                       at most hospitals once Medicare Advantage,
    #                       commercial, and dual-eligibles are included.
    # Reviewers will read the columns, not the footnote. We keep
    # ami_volume_2024 in the on-disk hospitals_classified.parquet for
    # downstream sensitivity / Paper-2 work, but it does not appear in the
    # supplement table.
    by_hosp = by_hosp.merge(
        hosp[["ccn", "fac_name", "city_name", "state_cd", "bed_cnt", "is_critical_access"]],
        on="ccn", how="left",
    )
    by_hosp = by_hosp.sort_values("stemi_per_yr", ascending=False)

    out_hosp = PROC / "top_hospitals.csv"
    by_hosp.to_csv(out_hosp, index=False)
    print(f"  saved: {out_hosp}  ({len(by_hosp):,} Tier A hospitals serving competitive zones)")
    print(f"  note: ami_volume_2024 deliberately excluded — see comment above")

    print("\n  Top 25 PCI-capable hospitals by competitive-zone catchment STEMI/yr:")
    show_cols = ["ccn", "fac_name", "city_name", "state_cd", "bed_cnt", "bgs_served", "stemi_per_yr"]
    show = by_hosp[show_cols].head(25).copy()
    show["stemi_per_yr"] = show["stemi_per_yr"].round(0).astype(int)
    print(show.to_string(index=False, max_colwidth=40))

    # === Headline summary ===
    print(f"\n=== HEADLINE NUMBERS (per REPRODUCIBILITY.md D8) ===")
    n_total = len(zones)
    n_compet_bgs = int(zones["is_competitive_15"].sum())
    pop_total = int(zones["population"].sum())
    adult_total = int(zones["adult_pop_20plus"].sum())
    adult_compet = int(zones.loc[zones["is_competitive_15"], "adult_pop_20plus"].sum())
    stemi_compet = adult_compet * INCIDENCE_RATE
    stemi_total = adult_total * INCIDENCE_RATE
    print(f"  CONUS total: {n_total:,} BGs")
    print(f"    all-ages population:  {pop_total:>14,}")
    print(f"    adult population 20+: {adult_total:>14,}")
    print(f"    implied national STEMI: {int(stemi_total):,}/yr  (rate {INCIDENCE_RATE:.4f}/adult/yr)")
    print(f"  In 15-min competitive zones:")
    print(f"    {n_compet_bgs:,} BGs ({n_compet_bgs/n_total*100:.1f}% of CONUS BGs)")
    print(f"    adult-pop {adult_compet:,} ({adult_compet/adult_total*100:.1f}% of CONUS adults)")
    print(f"    ~{int(stemi_compet):,} STEMI/yr ({stemi_compet/stemi_total*100:.1f}% of national STEMI)")
    print(f"\n  Top 5 states alone account for: ", end="")
    top5_adult = int(by_state.head(5)["competitive_adult_pop"].sum())
    print(f"{int(top5_adult*INCIDENCE_RATE):,} STEMI/yr "
          f"({top5_adult/adult_compet*100:.1f}% of competitive-zone STEMI)")
    print(f"  Top 25 hospitals alone account for: ", end="")
    top25_stemi = by_hosp.head(25)["stemi_per_yr"].sum()
    print(f"{int(top25_stemi):,} STEMI/yr ({top25_stemi/stemi_compet*100:.1f}% of competitive-zone STEMI)")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
