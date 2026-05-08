"""
Geocode the analysis-universe hospitals to lat/lon.

Three-pass strategy:
  1. Census Geocoder Batch API — street-level lat/lon where TIGER has the road.
     Free, no key, ~85% Tier A match rate in practice.
  2. ZIP centroid fallback (Census 2020 Gazetteer ZCTA file) — for hospitals
     where Census Geocoder returned No_Match or Tie. Lower precision (~1-3 km)
     but covers virtually all hospitals since every ZIP has a known centroid.

Output `precision_tier` ∈ {exact, non_exact, zip_centroid, missing} preserves
the per-row provenance so a sensitivity analysis can drop the zip_centroid
subset and confirm the headline finding is robust.

Inputs:
  national/data/processed/hospitals_classified.parquet   (4,408 rows)
  national/data/raw/cenpop2020/2020_Gaz_zcta_national.txt (33k ZCTAs)

Output:
  national/data/processed/hospitals_geocoded.parquet
  national/data/processed/hospitals_geocoded.csv

Output schema = input schema + {
  match_indicator   str   "Match" | "No_Match" | "Tie" | "ZIP_Fallback"
  match_type        str   "Exact" | "Non_Exact" | "Centroid" | NaN
  matched_address   str   Census-canonicalized address (or NaN for fallback)
  lat               float WGS84 latitude
  lon               float WGS84 longitude
  precision_tier    str   "exact" | "non_exact" | "zip_centroid" | "zip_prefix" | "missing"
  geocoded          bool  True if any precision tier was assigned
}

Usage:
    python national/src/04_geocode_hospitals.py
"""
from __future__ import annotations

import argparse
import hashlib
import io
import time
from pathlib import Path

import pandas as pd
import requests

REPO = Path(__file__).resolve().parents[2]
GEOCODER_URL = "https://geocoding.geo.census.gov/geocoder/locations/addressbatch"
ZCTA_FILE = REPO / "national" / "data" / "raw" / "cenpop2020" / "2020_Gaz_zcta_national.txt"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def census_batch_geocode(addresses_df: pd.DataFrame, batch_idx: int = 0) -> pd.DataFrame:
    """POST a batch CSV to Census Geocoder. Returns result DataFrame."""
    buf = io.StringIO()
    addresses_df.to_csv(buf, index=False, header=False)
    files = {"addressFile": ("addresses.csv", buf.getvalue(), "text/csv")}
    data = {"benchmark": "Public_AR_Current", "returntype": "locations"}

    print(f"  posting batch {batch_idx} ({len(addresses_df):,} rows)...", end="", flush=True)
    t0 = time.time()
    r = requests.post(GEOCODER_URL, files=files, data=data, timeout=600)
    print(f" {r.status_code} in {time.time()-t0:.1f}s")
    r.raise_for_status()

    cols = [
        "ccn", "input_address",
        "match_indicator", "match_type",
        "matched_address", "coords",
        "tigerline_id", "tiger_side",
    ]
    return pd.read_csv(io.StringIO(r.text), header=None, names=cols,
                       dtype=str, keep_default_na=False)


def load_zcta_centroids(path: Path) -> pd.DataFrame:
    """Census 2020 Gazetteer ZCTA centroid file. Whitespace-delimited, header row."""
    df = pd.read_csv(path, sep=r"\s+", dtype={"GEOID": str})
    return df[["GEOID", "INTPTLAT", "INTPTLONG"]].rename(
        columns={"GEOID": "zip5", "INTPTLAT": "zip_lat", "INTPTLONG": "zip_lon"}
    )


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--src", default=REPO / "national" / "data" / "processed" / "hospitals_classified.parquet",
                   type=Path)
    p.add_argument("--zcta", default=ZCTA_FILE, type=Path,
                   help="Census 2020 Gazetteer ZCTA centroid file")
    p.add_argument("--out-dir", default=REPO / "national" / "data" / "processed", type=Path)
    p.add_argument("--batch-size", default=5000, type=int)
    args = p.parse_args()

    if not args.src.exists():
        raise SystemExit(f"input not found: {args.src}")
    if not args.zcta.exists():
        raise SystemExit(f"ZCTA file not found: {args.zcta} — see national/data/README.md")

    print(f"input:  {args.src}  sha256={sha256(args.src)[:16]}…")
    print(f"zcta:   {args.zcta}  sha256={sha256(args.zcta)[:16]}…")
    df = pd.read_parquet(args.src)
    print(f"  {len(df):,} hospitals to geocode")

    # === Pass 1: Census Geocoder Batch ===
    batch_in = df[["ccn", "st_adr", "city_name", "state_cd", "zip5"]].copy()
    batch_in.columns = ["Unique_ID", "Street_address", "City", "State", "ZIP"]

    results = []
    n_batches = (len(batch_in) + args.batch_size - 1) // args.batch_size
    print(f"\nPass 1 — Census Geocoder ({n_batches} batch(es) of up to {args.batch_size:,}):")
    for i in range(n_batches):
        chunk = batch_in.iloc[i * args.batch_size : (i + 1) * args.batch_size]
        results.append(census_batch_geocode(chunk, batch_idx=i))

    geocoded = pd.concat(results, ignore_index=True)
    coords = geocoded["coords"].str.split(",", expand=True)
    geocoded["lat"] = pd.to_numeric(coords.get(1), errors="coerce")
    geocoded["lon"] = pd.to_numeric(coords.get(0), errors="coerce")

    n_match = (geocoded["match_indicator"] == "Match").sum()
    n_no_match = (geocoded["match_indicator"] == "No_Match").sum()
    n_tie = (geocoded["match_indicator"] == "Tie").sum()
    print(f"  pass-1 results: {n_match:,} match / {n_no_match:,} no-match / {n_tie:,} tie")

    # Map match_type → precision_tier for matched rows
    geocoded["precision_tier"] = pd.NA
    geocoded.loc[geocoded["match_type"] == "Exact", "precision_tier"] = "exact"
    geocoded.loc[geocoded["match_type"] == "Non_Exact", "precision_tier"] = "non_exact"

    # === Pass 2: ZIP centroid fallback for the misses ===
    zcta = load_zcta_centroids(args.zcta)
    zcta_map = dict(zip(zcta["zip5"], zip(zcta["zip_lat"], zcta["zip_lon"])))
    print(f"\nPass 2 — ZIP centroid fallback ({len(zcta):,} ZCTAs loaded):")

    # Merge so we can look up the original ZIP for each unmatched CCN
    geo_with_zip = geocoded.merge(df[["ccn", "zip5"]], on="ccn", how="left")
    needs_fallback = geo_with_zip["match_indicator"].isin(["No_Match", "Tie"])

    n_recovered = 0
    n_zip5_miss = []
    for idx in geo_with_zip[needs_fallback].index:
        zip5 = geo_with_zip.at[idx, "zip5"]
        if zip5 in zcta_map:
            geocoded.at[idx, "lat"] = zcta_map[zip5][0]
            geocoded.at[idx, "lon"] = zcta_map[zip5][1]
            geocoded.at[idx, "match_indicator"] = "ZIP_Fallback"
            geocoded.at[idx, "match_type"] = "Centroid"
            geocoded.at[idx, "precision_tier"] = "zip_centroid"
            n_recovered += 1
        else:
            n_zip5_miss.append(idx)
    print(f"  recovered via ZIP centroid: {n_recovered:,}")

    # === Pass 3: ZIP-3-prefix fallback ===
    # Institutional ZIPs (e.g., Yale-New Haven 06504, UVA 22908, Wake Forest 27157)
    # don't exist as ZCTAs but share their first 3 digits with surrounding ZCTAs in
    # the same city. Falling back to the centroid of any 3-digit-prefix-matched ZCTA
    # places the hospital in the right metro area, ~5-15 km precision.
    print(f"\nPass 3 — ZIP-3-prefix fallback for {len(n_zip5_miss)} institutional ZIPs:")
    from collections import defaultdict
    prefix_index = defaultdict(list)
    for z in zcta_map:
        prefix_index[z[:3]].append(z)

    n_prefix_recovered = 0
    n_irrecoverable = 0
    for idx in n_zip5_miss:
        zip5 = geo_with_zip.at[idx, "zip5"]
        prefix = zip5[:3]
        candidates = prefix_index.get(prefix, [])
        if candidates:
            # Use the centroid of the geographically-closest-numbered ZCTA in the prefix.
            # In practice all 3-digit-prefix ZCTAs cluster in the same metro; pick the
            # numerically nearest as a deterministic tie-breaker.
            chosen = min(candidates, key=lambda z: abs(int(z) - int(zip5)))
            geocoded.at[idx, "lat"] = zcta_map[chosen][0]
            geocoded.at[idx, "lon"] = zcta_map[chosen][1]
            geocoded.at[idx, "match_indicator"] = "ZIP3_Fallback"
            geocoded.at[idx, "match_type"] = f"Prefix_via_{chosen}"
            geocoded.at[idx, "precision_tier"] = "zip_prefix"
            n_prefix_recovered += 1
        else:
            geocoded.at[idx, "precision_tier"] = "missing"
            n_irrecoverable += 1
    print(f"  recovered via ZIP-3-prefix: {n_prefix_recovered:,}")
    if n_irrecoverable:
        print(f"  WARN: {n_irrecoverable:,} hospitals with ZIP3 prefix not in Gazetteer either")

    geocoded["geocoded"] = geocoded["precision_tier"].isin(["exact", "non_exact", "zip_centroid", "zip_prefix"])

    # CONUS bounding box check on all final lat/lon
    in_box = (
        geocoded["lat"].between(24.0, 49.5, inclusive="both") &
        geocoded["lon"].between(-125.5, -66.5, inclusive="both")
    )
    n_out_of_box = (geocoded["geocoded"] & ~in_box).sum()
    print(f"\n  total geocoded: {geocoded['geocoded'].sum():,} / {len(geocoded):,}")
    if n_out_of_box:
        print(f"  WARN: {n_out_of_box:,} geocoded rows outside CONUS bounding box — investigate")

    # Merge back onto the spine
    out = df.merge(
        geocoded[["ccn", "match_indicator", "match_type", "matched_address",
                  "lat", "lon", "precision_tier", "geocoded"]],
        on="ccn", how="left",
    )
    assert len(out) == len(df)

    # Per-tier, per-precision-tier summary
    print(f"\n  per-tier coverage:")
    for tier in ["A", "B"]:
        sub = out[out["tier"] == tier]
        n_geo = sub["geocoded"].sum()
        print(f"    Tier {tier}: {n_geo:,}/{len(sub):,} ({n_geo/len(sub)*100:.1f}%)")
        for pt in ["exact", "non_exact", "zip_centroid", "zip_prefix", "missing"]:
            n_pt = (sub["precision_tier"] == pt).sum()
            if n_pt:
                print(f"      precision_tier={pt}: {n_pt:,}")

    # Write
    args.out_dir.mkdir(parents=True, exist_ok=True)
    pq = args.out_dir / "hospitals_geocoded.parquet"
    csv = args.out_dir / "hospitals_geocoded.csv"
    out.to_parquet(pq, index=False)
    out.to_csv(csv, index=False)

    print(f"\noutput: {pq}  ({pq.stat().st_size/1e6:.2f} MB, sha256={sha256(pq)[:16]}…)")
    print(f"output: {csv}  ({csv.stat().st_size/1e6:.2f} MB, sha256={sha256(csv)[:16]}…)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
