"""
Geocode the analysis-universe hospitals via Census Geocoder Batch API.

Census Geocoder is free, no key, no rate limits at this scale. Batch API
accepts up to 10,000 addresses per request and returns lat/lon plus match
quality flags.

Input:  national/data/processed/hospitals_classified.parquet  (4,408 rows)
Output: national/data/processed/hospitals_geocoded.parquet

Output schema = input schema + {
  match_indicator   str   "Match" | "No_Match" | "Tie"
  match_type        str   "Exact" | "Non_Exact" | NaN
  matched_address   str   Census-canonicalized address (or NaN)
  lat               float WGS84 latitude
  lon               float WGS84 longitude
  geocoded          bool  True if Match indicator was "Match"
}

Quality interpretation for catchment analysis:
  Match + Exact      — street-level precision, full confidence (typical ~85%)
  Match + Non_Exact  — interpolated within block, ~500m accuracy (typical ~10%)
  No_Match / Tie     — failed; will fall back to ZIP centroid in a follow-on step
                       OR drop and document, depending on rate

For block-group-scale STEMI catchment analysis, both "Match" tiers are usable
since block groups are typically 200–1000 m wide. Non-matches need a fallback.

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


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def geocode_batch(addresses_df: pd.DataFrame, batch_idx: int = 0) -> pd.DataFrame:
    """POST a batch CSV to the Census Geocoder, parse the response."""
    # Census Geocoder batch input: CSV with columns
    # Unique_ID, Street_address, City, State, ZIP — NO header row
    buf = io.StringIO()
    addresses_df.to_csv(buf, index=False, header=False)
    files = {"addressFile": ("addresses.csv", buf.getvalue(), "text/csv")}
    data = {"benchmark": "Public_AR_Current", "returntype": "locations"}

    print(f"  posting batch {batch_idx} ({len(addresses_df):,} rows)...", end="", flush=True)
    t0 = time.time()
    r = requests.post(GEOCODER_URL, files=files, data=data, timeout=600)
    print(f" {r.status_code} in {time.time()-t0:.1f}s")
    r.raise_for_status()

    # Response is CSV: ID, Input_address, Match_indicator, Match_type,
    # Matched_address, Coordinates(lon,lat), TIGER_line_id, TIGER_side
    cols = [
        "ccn", "input_address",
        "match_indicator", "match_type",
        "matched_address", "coords",
        "tigerline_id", "tiger_side",
    ]
    out = pd.read_csv(
        io.StringIO(r.text), header=None, names=cols,
        dtype=str, keep_default_na=False,
    )
    return out


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--src", default=REPO / "national" / "data" / "processed" / "hospitals_classified.parquet",
                   type=Path)
    p.add_argument("--out-dir", default=REPO / "national" / "data" / "processed", type=Path)
    p.add_argument("--batch-size", default=5000, type=int,
                   help="Addresses per batch — Census limit is 10,000; 5000 is safer")
    args = p.parse_args()

    if not args.src.exists():
        raise SystemExit(f"input not found: {args.src}")

    print(f"input:  {args.src}  sha256={sha256(args.src)[:16]}…")
    df = pd.read_parquet(args.src)
    print(f"  {len(df):,} hospitals to geocode")

    # Build the batch input. Census wants 5 columns: id, street, city, state, zip
    batch_in = df[["ccn", "st_adr", "city_name", "state_cd", "zip5"]].copy()
    batch_in.columns = ["Unique_ID", "Street_address", "City", "State", "ZIP"]

    # Split into chunks
    results = []
    n_batches = (len(batch_in) + args.batch_size - 1) // args.batch_size
    print(f"\ngeocoding in {n_batches} batch(es) of up to {args.batch_size:,}:")
    for i in range(n_batches):
        chunk = batch_in.iloc[i * args.batch_size : (i + 1) * args.batch_size]
        results.append(geocode_batch(chunk, batch_idx=i))

    geocoded = pd.concat(results, ignore_index=True)
    print(f"\n  responses received: {len(geocoded):,}")

    # Parse coordinates "lon,lat" → two float columns
    coords = geocoded["coords"].str.split(",", expand=True)
    geocoded["lon"] = pd.to_numeric(coords.get(0), errors="coerce")
    geocoded["lat"] = pd.to_numeric(coords.get(1), errors="coerce")
    geocoded["geocoded"] = geocoded["match_indicator"] == "Match"

    # Match quality summary
    print(f"\n  match indicator distribution:")
    print(f"    Match:    {(geocoded['match_indicator'] == 'Match').sum():,}")
    print(f"    No_Match: {(geocoded['match_indicator'] == 'No_Match').sum():,}")
    print(f"    Tie:      {(geocoded['match_indicator'] == 'Tie').sum():,}")
    print(f"  match type (where matched):")
    print(f"    Exact:     {(geocoded['match_type'] == 'Exact').sum():,}")
    print(f"    Non_Exact: {(geocoded['match_type'] == 'Non_Exact').sum():,}")

    # Sanity: coords within CONUS bounding box
    in_box = (
        geocoded["lat"].between(24.0, 49.5, inclusive="both") &
        geocoded["lon"].between(-125.5, -66.5, inclusive="both")
    )
    print(f"  matches with coords in CONUS bounding box: {in_box.sum():,}")
    out_of_box = geocoded[geocoded["geocoded"] & ~in_box]
    if len(out_of_box):
        print(f"  WARN: {len(out_of_box)} matches with coords outside CONUS — investigate")

    # Merge back onto the spine, keeping all hospitals (matched or not)
    out = df.merge(
        geocoded[["ccn", "match_indicator", "match_type", "matched_address", "lat", "lon", "geocoded"]],
        on="ccn", how="left",
    )
    assert len(out) == len(df), "merge changed row count"

    # Per-tier match rates
    print(f"\n  per-tier match rate:")
    for tier in ["A", "B"]:
        sub = out[out["tier"] == tier]
        n_match = sub["geocoded"].sum()
        print(f"    Tier {tier}: {n_match:,} / {len(sub):,} ({n_match/len(sub)*100:.1f}%)")

    # Write
    args.out_dir.mkdir(parents=True, exist_ok=True)
    pq = args.out_dir / "hospitals_geocoded.parquet"
    csv = args.out_dir / "hospitals_geocoded.csv"
    out.to_parquet(pq, index=False)
    out.to_csv(csv, index=False)

    print(f"\noutput: {pq}  ({pq.stat().st_size/1e6:.2f} MB, sha256={sha256(pq)[:16]}…)")
    print(f"output: {csv}  ({csv.stat().st_size/1e6:.2f} MB)")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
