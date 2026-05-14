"""Per-county aggregation by T2-T1 stratum, for the web 'Burden' page.

This script does NOT replace 07_aggregate.py. It runs on the same per-BG
analytic file (zones_classified.parquet) but emits a different per-county
table whose columns slice the competitive-zone population into three
disjoint T2-T1 strata:

    stratum                competitive_margin_sec
    -----------------------------------------------
    lt10    [0, 10) min     [0, 600)
    10_20   [10, 20) min    [600, 1200)
    20_30   [20, 30) min    [1200, 1800)
    ge30    [>=30 / NaN)    [>=1800] or T2 unreachable   (neutral gray on the map)

The web 'Burden' page renders a bivariate choropleth (stratum -> hue, total
competitive-zone residents -> log-scaled alpha) plus three small-multiples
panels, one per CZ stratum.

Inputs:
  national/data/processed/zones_classified.parquet
  national/data/processed/ct_bg_to_planning_region.csv  (CT historical-county -> planning-region remap)
  web/src/data/county_values.json                       (carries county name + state for join)

Outputs:
  national/data/processed/county_strata_summary.csv     (one row per CONUS county; manuscript reference)
  national/data/processed/county_strata_summary.json    (web-shaped JSON, FIPS-keyed)

STEMI counts use adult_pop_20plus x INCIDENCE_RATE = 0.001 (AHA HDSS 2024).
Identical convention to 07_aggregate.py / REPRODUCIBILITY.md D8.
"""
from __future__ import annotations

import json
import math
from pathlib import Path
import pandas as pd

REPO = Path(__file__).resolve().parents[2]
PROC = REPO / "national" / "data" / "processed"
WEB_DATA = REPO / "web" / "src" / "data"

INCIDENCE_RATE = 0.001

# Stratum boundaries in SECONDS (T2 - T1). Disjoint, left-inclusive,
# right-exclusive ("0-10" means margin < 10 min; "10-20" means 10 <= margin < 20).
STRATA = [
    ("lt10",   0,      600),    # [0, 10) min
    ("10_20",  600,    1200),   # [10, 20) min
    ("20_30",  1200,   1800),   # [20, 30) min
]
# Anything else (margin >= 1800 sec, or T2 unreachable) -> 'ge30'.


def main() -> int:
    print("loading zones_classified.parquet ...")
    z = pd.read_parquet(PROC / "zones_classified.parquet")
    print(f"  {len(z):,} BGs")

    # Default county_fips = STATEFP + COUNTYFP (CenPop2020 vintage)
    z["county_fips"] = z["STATEFP"] + z["COUNTYFP"]

    # Connecticut: remap historical-county BGs to TIGER 2023 planning regions.
    # Identical handling to 07_aggregate.py so the web map's county geometry
    # (us-atlas, which now uses planning regions) lines up.
    ct_xw_path = PROC / "ct_bg_to_planning_region.csv"
    if ct_xw_path.exists():
        ct_xw = pd.read_csv(ct_xw_path, dtype={"bg_id": str, "planning_region": str})
        ct_map = dict(zip(ct_xw["bg_id"], ct_xw["planning_region"]))
        n_ct = z["bg_id"].isin(ct_map).sum()
        z["county_fips"] = z["bg_id"].map(ct_map).fillna(z["county_fips"])
        print(f"  CT crosswalk applied: {n_ct:,} CT BGs remapped")
    else:
        print(f"  WARN: CT crosswalk not found")

    # Per-BG stratum assignment.
    margin = z["competitive_margin_sec"]
    z["stratum"] = "ge30"  # default: includes margin>=1800 AND NaN (T2 unreachable)
    for name, lo, hi in STRATA:
        mask = margin.notna() & (margin >= lo) & (margin < hi)
        z.loc[mask, "stratum"] = name

    # Sanity: stratum counts at the BG level should match step 06's numbers.
    print("\nBG-level stratum check (should match step 06 summary):")
    for s in ("lt10", "10_20", "20_30", "ge30"):
        n_bg = int((z["stratum"] == s).sum())
        n_adult = int(z.loc[z["stratum"] == s, "adult_pop_20plus"].sum())
        print(f"  {s:>6}: {n_bg:>10,} BGs   adult_pop {n_adult:>13,}")
    print(f"  TOTAL: {len(z):>10,} BGs   adult_pop {int(z['adult_pop_20plus'].sum()):>13,}")

    # County x stratum pivot. One row per county, columns = adult_pop_{stratum}.
    print("\naggregating per county x stratum ...")
    pivot = (
        z.pivot_table(
            index="county_fips",
            columns="stratum",
            values="adult_pop_20plus",
            aggfunc="sum",
            fill_value=0,
        )
        .rename(columns={
            "lt10":  "adult_pop_lt10",
            "10_20": "adult_pop_10_20",
            "20_30": "adult_pop_20_30",
            "ge30":  "adult_pop_ge30",
        })
        .reset_index()
    )
    for col in ("adult_pop_lt10", "adult_pop_10_20", "adult_pop_20_30", "adult_pop_ge30"):
        if col not in pivot.columns:
            pivot[col] = 0
        pivot[col] = pivot[col].astype(int)

    pivot["adult_pop_total"] = (
        pivot["adult_pop_lt10"] + pivot["adult_pop_10_20"]
        + pivot["adult_pop_20_30"] + pivot["adult_pop_ge30"]
    )
    pivot["cz_residents"] = (
        pivot["adult_pop_lt10"] + pivot["adult_pop_10_20"] + pivot["adult_pop_20_30"]
    )

    # Dominant stratum: the CZ stratum (lt10 / 10_20 / 20_30) with the most
    # adults in this county. If all three CZ counts are zero, dominant_stratum
    # = "ge30" (county is neutral gray on the map).
    cz_cols = ["adult_pop_lt10", "adult_pop_10_20", "adult_pop_20_30"]
    cz_names = ["lt10", "10_20", "20_30"]
    cz_idx = pivot[cz_cols].values.argmax(axis=1)
    cz_max = pivot[cz_cols].values.max(axis=1)
    pivot["dominant_stratum"] = [
        cz_names[i] if cz_max[k] > 0 else "ge30"
        for k, i in enumerate(cz_idx)
    ]

    # STEMI/yr per stratum (adult x rate, rounded to integer counts).
    for s in ("lt10", "10_20", "20_30"):
        pivot[f"stemi_{s}"] = (pivot[f"adult_pop_{s}"] * INCIDENCE_RATE).round().astype(int)
    pivot["stemi_cz_total"] = (pivot["cz_residents"] * INCIDENCE_RATE).round().astype(int)

    # Sanity: per-county totals should reconcile to step 07's adult_pop totals.
    # We load county_values.json (the existing per-county adult_pop) and join.
    print("\nreconciliation against existing county_values.json ...")
    cv_path = WEB_DATA / "county_values.json"
    with open(cv_path) as f:
        cv = json.load(f)
    cv_df = pd.DataFrame([
        {"county_fips": k, "name": v["name"], "state": v["state"],
         "adult_pop_v07": v["adult_pop"]}
        for k, v in cv.items()
    ])
    merged = pivot.merge(cv_df, on="county_fips", how="outer", indicator=True)
    n_only_left = int((merged["_merge"] == "left_only").sum())
    n_only_right = int((merged["_merge"] == "right_only").sum())
    n_both = int((merged["_merge"] == "both").sum())
    print(f"  counties present in both:        {n_both:,}")
    print(f"  counties only in strata pivot:   {n_only_left:,}")
    print(f"  counties only in county_values:  {n_only_right:,}")

    # On counties present in both, check that adult_pop totals match (within
    # rounding tolerance; we cast to int in two places).
    both = merged[merged["_merge"] == "both"].copy()
    both["pop_delta"] = (both["adult_pop_total"] - both["adult_pop_v07"]).abs()
    max_delta = int(both["pop_delta"].max())
    n_off = int((both["pop_delta"] > 1).sum())
    print(f"  max |adult_pop_strata - adult_pop_v07| across counties: {max_delta:,}")
    print(f"  counties with |delta| > 1: {n_off}")
    if n_off > 0:
        worst = both.nlargest(5, "pop_delta")[["county_fips", "name", "state",
                                                "adult_pop_total", "adult_pop_v07", "pop_delta"]]
        print(worst.to_string(index=False))

    # National totals (must match step 06):
    print("\nnational totals across CONUS counties:")
    print(f"  adult_pop_lt10:    {int(pivot['adult_pop_lt10'].sum()):>13,}")
    print(f"  adult_pop_10_20:   {int(pivot['adult_pop_10_20'].sum()):>13,}")
    print(f"  adult_pop_20_30:   {int(pivot['adult_pop_20_30'].sum()):>13,}")
    print(f"  adult_pop_ge30:    {int(pivot['adult_pop_ge30'].sum()):>13,}")
    print(f"  adult_pop_total:   {int(pivot['adult_pop_total'].sum()):>13,}")
    print(f"  cz_residents:      {int(pivot['cz_residents'].sum()):>13,}  "
          f"(~{int(pivot['cz_residents'].sum() * INCIDENCE_RATE):,} STEMI/yr)")
    print(f"  stemi_cz_total:    {int(pivot['stemi_cz_total'].sum()):>13,}")

    # Dominant-stratum distribution
    print("\ncounties by dominant stratum:")
    for s in ("lt10", "10_20", "20_30", "ge30"):
        n_c = int((pivot["dominant_stratum"] == s).sum())
        n_pop = int(pivot.loc[pivot["dominant_stratum"] == s, "cz_residents"].sum())
        print(f"  {s:>6}: {n_c:>5,} counties   cz_residents in those counties {n_pop:>13,}")

    # === Per-county CDF at 1-minute granularity (for the slider) ===
    # For each county, emit a 30-element array cdf where cdf[X-1] is the
    # number of adults in that county with T2-T1 < X minutes. Monotonic
    # non-decreasing by construction. Used by the Strata page to drive a
    # continuous-threshold slider without re-aggregating in the browser.
    print("\nbuilding per-county CDF at 1-min granularity ...")
    N_BUCKETS = 30
    margin_min = z["competitive_margin_sec"] / 60
    # Vectorized: for each X, sum adult_pop where margin_min is non-null and < X.
    cdf_columns = {}
    for X in range(1, N_BUCKETS + 1):
        mask = margin_min.notna() & (margin_min < X)
        cdf_columns[X] = (
            z.loc[mask].groupby("county_fips")["adult_pop_20plus"].sum()
        )
    cdf_df = pd.DataFrame(cdf_columns).fillna(0).astype(int)
    cdf_df = cdf_df.reindex(pivot["county_fips"].values).fillna(0).astype(int)

    # Reconciliation: cdf[15] (X=15 -> margin < 15 min) should equal
    # adult_pop_lt10 + adult_pop_10_20 (well, partially) -- actually:
    # cdf[15] = adults with margin < 15 = lt10 + (portion of 10_20 with margin < 15).
    # Cleaner anchors:
    #   cdf[10] should equal adult_pop_lt10 (counties' adults with margin < 10).
    #   cdf[20] should equal adult_pop_lt10 + adult_pop_10_20.
    #   cdf[30] should equal cz_residents (all three CZ strata).
    print("\nCDF reconciliation against strata pivot:")
    nat_cdf10 = int(cdf_df[10].sum())
    nat_cdf20 = int(cdf_df[20].sum())
    nat_cdf30 = int(cdf_df[30].sum())
    nat_lt10  = int(pivot["adult_pop_lt10"].sum())
    nat_10_20 = int(pivot["adult_pop_10_20"].sum())
    nat_20_30 = int(pivot["adult_pop_20_30"].sum())
    nat_cz    = int(pivot["cz_residents"].sum())
    print(f"  cdf[10] (margin<10):  {nat_cdf10:>13,}   adult_pop_lt10:                                 {nat_lt10:>13,}   match: {nat_cdf10 == nat_lt10}")
    print(f"  cdf[20] (margin<20):  {nat_cdf20:>13,}   adult_pop_lt10 + 10_20:                          {nat_lt10 + nat_10_20:>13,}   match: {nat_cdf20 == nat_lt10 + nat_10_20}")
    print(f"  cdf[30] (margin<30):  {nat_cdf30:>13,}   adult_pop_lt10 + 10_20 + 20_30 (=cz_residents): {nat_cz:>13,}   match: {nat_cdf30 == nat_cz}")
    # 15-min anchor: the existing abstract headline (~196M adults, ~196,253 STEMI/yr).
    nat_cdf15 = int(cdf_df[15].sum())
    print(f"  cdf[15] (margin<15):  {nat_cdf15:>13,}   ~{int(nat_cdf15 * INCIDENCE_RATE):,} STEMI/yr "
          f"(existing abstract headline)")

    # Save CSV summary (manuscript reference)
    out_csv = PROC / "county_strata_summary.csv"
    out_cols = ["county_fips", "adult_pop_total",
                "adult_pop_lt10", "adult_pop_10_20", "adult_pop_20_30", "adult_pop_ge30",
                "cz_residents", "dominant_stratum",
                "stemi_lt10", "stemi_10_20", "stemi_20_30", "stemi_cz_total"]
    pivot[out_cols].to_csv(out_csv, index=False)
    print(f"\nsaved: {out_csv}")

    # Save web-shaped JSON. Each county carries:
    #   name, state, adult_pop      — county identity + denominator
    #   adult_pop_{lt10,10_20,20_30,ge30}, cz_residents, stratum   — small-multiples + tooltip
    #   stemi_{...}                                                — derived counts (for hover)
    #   cdf                         — 30-element array; cdf[X-1] = adults with margin < X min
    cv_lookup = {k: v for k, v in cv.items()}
    web_dict = {}
    for _, row in pivot.iterrows():
        fips = row["county_fips"]
        meta = cv_lookup.get(fips, {})
        cdf_row = cdf_df.loc[fips] if fips in cdf_df.index else None
        cdf_list = [int(cdf_row[X]) for X in range(1, N_BUCKETS + 1)] if cdf_row is not None \
                    else [0] * N_BUCKETS
        web_dict[fips] = {
            "name":   meta.get("name", ""),
            "state":  meta.get("state", ""),
            "adult_pop":        int(row["adult_pop_total"]),
            "cz_residents":     int(row["cz_residents"]),
            "stratum":          row["dominant_stratum"],
            "adult_pop_lt10":   int(row["adult_pop_lt10"]),
            "adult_pop_10_20":  int(row["adult_pop_10_20"]),
            "adult_pop_20_30":  int(row["adult_pop_20_30"]),
            "adult_pop_ge30":   int(row["adult_pop_ge30"]),
            "stemi_lt10":       int(row["stemi_lt10"]),
            "stemi_10_20":      int(row["stemi_10_20"]),
            "stemi_20_30":      int(row["stemi_20_30"]),
            "stemi_cz_total":   int(row["stemi_cz_total"]),
            "cdf":              cdf_list,
        }
    out_json = WEB_DATA / "county_strata.json"
    with open(out_json, "w") as f:
        json.dump(web_dict, f, separators=(",", ":"))
    print(f"saved: {out_json}  ({out_json.stat().st_size/1024:.1f} KB, {len(web_dict):,} counties)")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
