"""Aggregate per-BG zone classification → state, county, and hospital rollups.

Inputs:
  national/data/processed/zones_classified.parquet    (per-BG analytic file)
  national/data/processed/hospitals_classified.parquet (hospital metadata)

Outputs:
  national/data/processed/state_summary.csv      (one row per CONUS state)
  national/data/processed/county_summary.csv     (one row per CONUS county; feeds choropleth)
  national/data/processed/top_hospitals.csv      (top N PCI hospitals by competitive-zone exposure)

System-level (chain) aggregation is deferred to Paper 2 — CMS PoS does not include
parent system identifiers, and AHA Annual Survey was excluded by the public-source
constraint. Hospital-level aggregation is the public-source-defensible substitute
and is what feeds the manuscript's "top hospitals serving competitive-zone catchment"
table.

STEMI incidence rate: 0.001 per Amendment 2026-05-08-B (corrected from original
AMI-grade 0.004).
"""
from __future__ import annotations

from pathlib import Path
import pandas as pd

REPO = Path(__file__).resolve().parents[2]
PROC = REPO / "national" / "data" / "processed"

INCIDENCE_RATE = 0.001  # per Amendment 2026-05-08-B

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
    zones["stemi_per_yr"] = zones["population"] * INCIDENCE_RATE

    # === State-level summary ===
    print("\n--- per-state aggregation ---")
    by_state = zones.groupby("state_abbr").agg(
        total_bgs=("bg_id", "size"),
        total_pop=("population", "sum"),
        total_stemi_per_yr=("stemi_per_yr", "sum"),
        competitive_bgs=("is_competitive_15", "sum"),
        competitive_pop=("population", lambda s: zones.loc[s.index].loc[zones.loc[s.index, "is_competitive_15"], "population"].sum()),
        cross_state_bgs=("cross_state", "sum"),
    ).reset_index()
    by_state["competitive_stemi_per_yr"] = by_state["competitive_pop"] * INCIDENCE_RATE
    by_state["pct_pop_in_competitive"] = (by_state["competitive_pop"] / by_state["total_pop"] * 100).round(1)
    by_state["pct_bgs_in_competitive"] = (by_state["competitive_bgs"] / by_state["total_bgs"] * 100).round(1)

    by_state = by_state.sort_values("competitive_stemi_per_yr", ascending=False)
    out_state = PROC / "state_summary.csv"
    by_state.to_csv(out_state, index=False)
    print(f"  saved: {out_state}")

    print("\n  Top 10 states by competitive-zone STEMI/yr:")
    cols = ["state_abbr", "total_pop", "competitive_pop", "pct_pop_in_competitive", "competitive_stemi_per_yr", "cross_state_bgs"]
    print(by_state[cols].head(10).to_string(index=False))

    # === County-level summary (for choropleth) ===
    print("\n--- per-county aggregation (for choropleth) ---")
    zones["county_fips"] = zones["STATEFP"] + zones["COUNTYFP"]
    by_county = zones.groupby("county_fips").agg(
        total_bgs=("bg_id", "size"),
        total_pop=("population", "sum"),
        competitive_bgs=("is_competitive_15", "sum"),
    ).reset_index()
    by_county["competitive_bgs"] = by_county["competitive_bgs"].astype(int)
    by_county["pct_bgs_competitive"] = (by_county["competitive_bgs"] / by_county["total_bgs"] * 100).round(1)
    out_county = PROC / "county_summary.csv"
    by_county.to_csv(out_county, index=False)
    print(f"  saved: {out_county}  ({len(by_county):,} CONUS counties)")
    print(f"  pct_bgs_competitive distribution:")
    for pct in (0, 25, 50, 75, 90, 95, 100):
        print(f"    p{pct:>3}: {by_county['pct_bgs_competitive'].quantile(pct/100):>5.1f}%")

    # === Hospital-level: which Tier A hospitals serve the most competitive-zone STEMI? ===
    # For each Tier A hospital, count BGs where this hospital is T1_PCI AND BG is in 15-min competitive zone
    print("\n--- top hospitals by competitive-zone catchment ---")
    competitive_t1 = zones[zones["is_competitive_15"] & zones["ccn_t1_pci"].notna()].copy()
    by_hosp = competitive_t1.groupby("ccn_t1_pci").agg(
        bgs_served=("bg_id", "size"),
        pop_served=("population", "sum"),
    ).reset_index().rename(columns={"ccn_t1_pci": "ccn"})
    by_hosp["stemi_per_yr"] = by_hosp["pop_served"] * INCIDENCE_RATE

    # Attach hospital name + state for readability
    by_hosp = by_hosp.merge(
        hosp[["ccn", "fac_name", "city_name", "state_cd", "bed_cnt", "is_critical_access", "ami_volume_2024"]],
        on="ccn", how="left",
    )
    by_hosp = by_hosp.sort_values("stemi_per_yr", ascending=False)

    out_hosp = PROC / "top_hospitals.csv"
    by_hosp.to_csv(out_hosp, index=False)
    print(f"  saved: {out_hosp}  ({len(by_hosp):,} Tier A hospitals serving competitive zones)")

    print("\n  Top 25 PCI-capable hospitals by competitive-zone catchment STEMI/yr:")
    show_cols = ["ccn", "fac_name", "city_name", "state_cd", "bed_cnt", "ami_volume_2024", "bgs_served", "stemi_per_yr"]
    show = by_hosp[show_cols].head(25).copy()
    show["stemi_per_yr"] = show["stemi_per_yr"].round(0).astype(int)
    print(show.to_string(index=False, max_colwidth=40))

    # === Headline summary ===
    print(f"\n=== HEADLINE NUMBERS (per pre_registration.md D1 + Amendment 2026-05-08-B) ===")
    n_compet_bgs = zones["is_competitive_15"].sum()
    pop_compet = zones.loc[zones["is_competitive_15"], "population"].sum()
    stemi_compet = pop_compet * INCIDENCE_RATE
    n_total = len(zones)
    pop_total = zones["population"].sum()
    print(f"  CONUS total: {n_total:,} BGs, {pop_total:,} pop, {int(pop_total*INCIDENCE_RATE):,} STEMI/yr")
    print(f"  In 15-min competitive zones:")
    print(f"    {n_compet_bgs:,} BGs ({n_compet_bgs/n_total*100:.1f}%)")
    print(f"    {pop_compet:,} people ({pop_compet/pop_total*100:.1f}%)")
    print(f"    ~{int(stemi_compet):,} STEMI/yr ({stemi_compet/(pop_total*INCIDENCE_RATE)*100:.1f}% of national STEMI)")
    print(f"\n  Top 5 states alone account for: ", end="")
    top5_pop = by_state.head(5)["competitive_pop"].sum()
    print(f"{int(top5_pop*INCIDENCE_RATE):,} STEMI/yr ({top5_pop/pop_compet*100:.1f}% of competitive-zone STEMI)")
    print(f"  Top 25 hospitals alone account for: ", end="")
    top25_stemi = by_hosp.head(25)["stemi_per_yr"].sum()
    print(f"{int(top25_stemi):,} STEMI/yr ({top25_stemi/stemi_compet*100:.1f}% of competitive-zone STEMI)")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
