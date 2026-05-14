"""Build the CT 2020-county to 2023-planning-region BG crosswalk.

Why this script exists
----------------------
Connecticut transitioned from 8 historical counties to 9 planning regions in
2022 via Census Bureau action. TIGER 2023 ships CT counties at the new
planning-region GEOIDs (09110, 09120, 09130, 09140, 09150, 09160, 09170,
09180, 09190). CenPop2020 is the 2020 Decennial vintage and indexes CT
block groups under the historical county GEOIDs (09001 Fairfield, 09003
Hartford, 09005 Litchfield, 09007 Middlesex, 09009 New Haven, 09011 New
London, 09013 Tolland, 09015 Windham).

Without a crosswalk, joining CenPop2020-derived data against TIGER 2023
shapes drops all CT counties from the choropleth. The 9 unshaded entities
in the Northeast of the v9 first-cut figure are exactly these planning
regions.

Approach: spatial join
----------------------
The mapping from BG to planning region is well-defined at BG resolution
(planning region boundaries are unions of BGs, not splits of them). For
each historical CT BG centroid (lat/lon from CenPop2020), find the
TIGER 2023 planning region whose polygon contains the centroid. Point-in-
polygon tested against each planning region; the first containing match
wins. Falls back to nearest-polygon by Euclidean distance if no contain
match (boundary precision edge cases).

This avoids needing the Census Bureau's relationship file
(https://www2.census.gov/geo/relfiles/); everything we need is already
local. It also keeps the pipeline geopandas-free; uses pyshp +
matplotlib.path.Path for point-in-polygon.

Input
-----
  national/data/raw/cenpop2020/CenPop2020_Mean_BG.txt   (BG centroids; lat/lon)
  national/data/raw/tiger_county/cb_2023_us_county_5m.zip (planning region polygons)

Output
------
  national/data/processed/ct_bg_to_planning_region.csv
      Columns:
          bg_id             str  12-digit historical-CT BG GEOID (e.g. 090011024001)
          planning_region   str  5-digit TIGER 2023 planning region FIPS (09110..09190)
          method            str  "contains" or "nearest" (audit)

Sandbox-runnable: TIGER and CenPop2020 are local files; no API calls.

Validation
----------
  - All ~2,700 historical CT BGs should resolve to one of the 9 planning regions.
  - Total CT adult population aggregated by planning region must equal the
    historical-county total (no BGs added, none lost).
  - "method=nearest" rows should be ~0 (a few at most, on lake/coast boundary BGs).
"""
from __future__ import annotations

import io
import zipfile
from pathlib import Path

import numpy as np
import pandas as pd
from matplotlib.path import Path as MplPath
import shapefile  # pyshp


REPO = Path(__file__).resolve().parents[2]
RAW = REPO / "national" / "data" / "raw"
PROC = REPO / "national" / "data" / "processed"

CT_HISTORICAL_FIPS = {"09001", "09003", "09005", "09007", "09009", "09011", "09013", "09015"}
CT_PLANNING_REGION_FIPS = {"09110", "09120", "09130", "09140", "09150", "09160", "09170", "09180", "09190"}


def load_ct_bgs() -> pd.DataFrame:
    """Read CenPop2020 and return CT historical-vintage BG centroids."""
    cp = pd.read_csv(
        RAW / "cenpop2020" / "CenPop2020_Mean_BG.txt",
        encoding="utf-8-sig",
        dtype={"STATEFP": str, "COUNTYFP": str, "TRACTCE": str, "BLKGRPCE": str},
    )
    cp = cp[cp["STATEFP"] == "09"].copy()
    cp["bg_id"] = cp["STATEFP"] + cp["COUNTYFP"] + cp["TRACTCE"] + cp["BLKGRPCE"]
    cp["county_fips_historical"] = cp["STATEFP"] + cp["COUNTYFP"]
    # Strip the leading "+" / "-" sign that CenPop2020 prepends to coordinates.
    cp["LAT"] = cp["LATITUDE"].astype(str).str.replace("+", "", regex=False).astype(float)
    cp["LON"] = cp["LONGITUDE"].astype(str).str.replace("+", "", regex=False).astype(float)
    return cp[["bg_id", "county_fips_historical", "POPULATION", "LAT", "LON"]].reset_index(drop=True)


def load_ct_planning_regions() -> dict[str, list[np.ndarray]]:
    """Read TIGER 2023 county shapes; return {planning_region_fips: [ring, ring, ...]}.

    Multi-part polygons are returned as a list of separate ring arrays. A point
    is considered inside the planning region if it is inside ANY of the rings
    (which approximates the outer boundary; planning regions don't have holes
    in practice, so this is exact).
    """
    zip_path = RAW / "tiger_county" / "cb_2023_us_county_5m.zip"
    polygons: dict[str, list[np.ndarray]] = {}

    with zipfile.ZipFile(zip_path) as z:
        sf = shapefile.Reader(
            shp=io.BytesIO(z.read("cb_2023_us_county_5m.shp")),
            shx=io.BytesIO(z.read("cb_2023_us_county_5m.shx")),
            dbf=io.BytesIO(z.read("cb_2023_us_county_5m.dbf")),
        )
        fields = [f[0] for f in sf.fields[1:]]
        for r in sf.shapeRecords():
            d = dict(zip(fields, r.record))
            if d["GEOID"] not in CT_PLANNING_REGION_FIPS:
                continue
            pts = np.array(r.shape.points)
            parts = list(r.shape.parts) + [len(pts)]
            rings = [pts[parts[i]:parts[i + 1]] for i in range(len(parts) - 1)]
            polygons[d["GEOID"]] = rings

    if len(polygons) != 9:
        missing = CT_PLANNING_REGION_FIPS - set(polygons.keys())
        raise SystemExit(f"expected 9 CT planning regions; got {len(polygons)}; missing {missing}")
    return polygons


def assign_planning_region(
    bgs: pd.DataFrame,
    polygons: dict[str, list[np.ndarray]],
) -> pd.DataFrame:
    """For each BG centroid, find containing planning region (or nearest if none)."""
    # Precompute matplotlib paths for each ring for each planning region.
    paths: dict[str, list[MplPath]] = {
        pr: [MplPath(ring) for ring in rings] for pr, rings in polygons.items()
    }

    points = bgs[["LON", "LAT"]].to_numpy()
    n = len(points)
    assigned = np.full(n, "", dtype=object)
    method = np.full(n, "", dtype=object)

    # Pass 1: containment
    contains_count = 0
    for pr, ps in paths.items():
        # contains_points returns boolean per point per path; OR over rings
        mask = np.zeros(n, dtype=bool)
        for p in ps:
            mask |= p.contains_points(points)
        # Don't overwrite a previous match
        new = mask & (assigned == "")
        assigned[new] = pr
        method[new] = "contains"
        contains_count += int(new.sum())

    # Pass 2: nearest centroid for any unassigned (boundary precision edge cases)
    leftover = np.where(assigned == "")[0]
    if len(leftover) > 0:
        # Compute centroid of each planning region (mean of its largest ring)
        pr_centroids = {}
        for pr, rings in polygons.items():
            largest = max(rings, key=lambda r: len(r))
            pr_centroids[pr] = largest.mean(axis=0)
        for i in leftover:
            pt = points[i]
            best_pr = min(
                pr_centroids.keys(),
                key=lambda pr: ((pr_centroids[pr][0] - pt[0]) ** 2 + (pr_centroids[pr][1] - pt[1]) ** 2),
            )
            assigned[i] = best_pr
            method[i] = "nearest"

    out = bgs.copy()
    out["planning_region"] = assigned
    out["method"] = method
    return out[["bg_id", "county_fips_historical", "planning_region", "method", "POPULATION"]]


def main() -> int:
    print("loading CT BGs from CenPop2020...")
    bgs = load_ct_bgs()
    print(f"  {len(bgs):,} CT block groups across {bgs['county_fips_historical'].nunique()} historical counties")

    print("\nloading TIGER 2023 CT planning region polygons...")
    polys = load_ct_planning_regions()
    print(f"  {len(polys)} planning regions loaded ({sum(len(r) for r in polys.values())} total polygon rings)")

    print("\nspatial join (point-in-polygon, then nearest fallback)...")
    crosswalk = assign_planning_region(bgs, polys)

    n_contains = (crosswalk["method"] == "contains").sum()
    n_nearest = (crosswalk["method"] == "nearest").sum()
    print(f"  contains:  {n_contains:>6,}")
    print(f"  nearest:   {n_nearest:>6,}  (boundary precision fallbacks)")

    print(f"\nplanning-region distribution:")
    for pr, sub in crosswalk.groupby("planning_region"):
        print(f"  {pr}: {len(sub):>5,} BGs, pop {int(sub['POPULATION'].sum()):>10,}")

    # Sanity check: total CT pop unchanged (BGs are reassigned, not added/lost)
    pop_orig = bgs["POPULATION"].sum()
    pop_xw = crosswalk["POPULATION"].sum()
    print(f"\ntotal CT population: {int(pop_orig):,} (orig) vs {int(pop_xw):,} (after xw); "
          f"{'✓ exact match' if pop_orig == pop_xw else '✗ MISMATCH'}")

    out_csv = PROC / "ct_bg_to_planning_region.csv"
    crosswalk[["bg_id", "county_fips_historical", "planning_region", "method"]].to_csv(out_csv, index=False)
    print(f"\nwrote {out_csv}  ({out_csv.stat().st_size/1024:.1f} KB)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
