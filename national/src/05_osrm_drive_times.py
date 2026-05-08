"""Hospital × block-group drive-time matrix via local OSRM.

Reads:
  hospitals_geocoded.parquet  (4,408 hospitals with lat/lon)
  CenPop2020_Mean_BG.txt      (238k CONUS block group centroids)

For each hospital, haversine-pre-filters to BGs within 90 mi, then queries
the local OSRM daemon's Table API in batches of 90 destinations per call.

Writes:
  drive_times.parquet  (hospital_ccn, bg_id, drive_time_sec)

Designed to run ON the same EC2 instance as the OSRM daemon, querying
http://localhost:5000. Total runtime ~30-60 min for 4,408 hospitals
× ~3,000 nearby BGs each.

Usage (on EC2, with daemon already running on localhost:5000):
    python3 05_osrm_drive_times.py
"""
import pandas as pd
import numpy as np
import requests
import time
import sys
from pathlib import Path

OSRM = "http://localhost:5000"
HAVERSINE_RADIUS_MI = 90.0
BATCH_SIZE = 90  # under OSRM's default max-table-size of 100

NON_CONUS = {"02", "15", "60", "66", "69", "72", "78"}


def haversine_vec(lat1, lon1, lat2_arr, lon2_arr):
    R = 3958.8
    lat1r, lon1r = np.radians(lat1), np.radians(lon1)
    lat2r, lon2r = np.radians(lat2_arr), np.radians(lon2_arr)
    dlat = lat2r - lat1r
    dlon = lon2r - lon1r
    a = np.sin(dlat/2)**2 + np.cos(lat1r)*np.cos(lat2r)*np.sin(dlon/2)**2
    return 2 * R * np.arcsin(np.sqrt(a))


def osrm_table_one_to_many(src_lon, src_lat, dst_lons, dst_lats):
    coords = [(src_lon, src_lat)] + list(zip(dst_lons, dst_lats))
    coord_str = ";".join(f"{lon},{lat}" for lon, lat in coords)
    n = len(dst_lons)
    url = (f"{OSRM}/table/v1/driving/{coord_str}"
           f"?sources=0&destinations={';'.join(str(k+1) for k in range(n))}"
           "&annotations=duration")
    r = requests.get(url, timeout=180)
    r.raise_for_status()
    return r.json()["durations"][0]


def main():
    hospitals = pd.read_parquet("hospitals_geocoded.parquet")
    hospitals = hospitals[hospitals["geocoded"]
                          & hospitals["lat"].notna()
                          & hospitals["lon"].notna()].reset_index(drop=True)
    print(f"hospitals: {len(hospitals):,}")

    bgs = pd.read_csv("CenPop2020_Mean_BG.txt", encoding="utf-8-sig",
                      dtype={"STATEFP": str, "COUNTYFP": str,
                             "TRACTCE": str, "BLKGRPCE": str})
    bgs = bgs[~bgs["STATEFP"].isin(NON_CONUS)].reset_index(drop=True)
    bgs["bg_id"] = (bgs["STATEFP"] + bgs["COUNTYFP"]
                    + bgs["TRACTCE"] + bgs["BLKGRPCE"])
    print(f"CONUS BGs: {len(bgs):,}")

    bg_lat = bgs["LATITUDE"].values
    bg_lon = bgs["LONGITUDE"].values
    bg_id = bgs["bg_id"].values

    results = []
    t0 = time.time()
    n_hosp = len(hospitals)

    for i, h in hospitals.iterrows():
        d_mi = haversine_vec(h["lat"], h["lon"], bg_lat, bg_lon)
        within = np.where(d_mi <= HAVERSINE_RADIUS_MI)[0]
        if len(within) == 0:
            continue
        for batch_start in range(0, len(within), BATCH_SIZE):
            batch_idx = within[batch_start:batch_start + BATCH_SIZE]
            try:
                durs = osrm_table_one_to_many(
                    h["lon"], h["lat"],
                    bg_lon[batch_idx], bg_lat[batch_idx])
            except Exception as e:
                print(f"  hospital {h['ccn']} batch error: {e}", file=sys.stderr)
                continue
            for k, idx in enumerate(batch_idx):
                if durs[k] is not None:
                    results.append((h["ccn"], bg_id[idx], int(durs[k])))
        if (i + 1) % 50 == 0 or i == n_hosp - 1:
            elapsed = time.time() - t0
            rate = (i + 1) / elapsed
            eta = (n_hosp - i - 1) / rate if rate > 0 else 0
            print(f"  {i+1:,}/{n_hosp:,} hospitals, "
                  f"{len(results):,} pairs, "
                  f"{elapsed:.0f}s elapsed, ETA {eta:.0f}s")

    df = pd.DataFrame(results, columns=["ccn", "bg_id", "drive_time_sec"])
    df.to_parquet("drive_times.parquet", index=False)
    print(f"\nsaved {len(df):,} pairs → drive_times.parquet "
          f"({Path('drive_times.parquet').stat().st_size/1e6:.1f} MB)")


if __name__ == "__main__":
    main()
