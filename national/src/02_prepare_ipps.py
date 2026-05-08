"""
Prepare the CMS IPPS DRG hospital volume data for STEMI analysis.

Input:  national/data/raw/cms_ipps/cms_ipps_drg_FY<YYYY>.json (CMS API response)
Output: national/data/raw/cms_ipps/cms_ipps_drg_FY<YYYY>.csv (CONUS-filtered)

The input JSON is the response from a filtered query against the CMS
Medicare Inpatient Hospitals - by Provider and Service dataset
(UUID ca9b5ef0-1386-4759-b2b6-5f9b35116786). The filter restricts to
DRGs we care about for STEMI analysis: 246, 247 (PCI procedures), and
280, 281, 282 (acute MI by complication severity).

NOTE on DRG 246/247: as of FY2024, the public-use file does not surface
records for DRG 246/247 in this dataset (returns empty even with simple-
equality filters). Most likely cause: post-2018 shift of uncomplicated
PCI to outpatient billing under CMS's 2-midnight rule, plus per-cell
suppression for hospitals with <11 inpatient PCIs per year. PCI capability
is therefore identified from the PoS cardiac catheterization lab service
code (see national/data/MANIFEST.md §2). The IPPS file is used only for
STEMI exposure weighting via DRG 280/281/282 admission volume.

Filter applied:
  state_cd in CONUS whitelist (48 states + DC). Drops AK, HI, territories.
  Same whitelist used in 01_prepare_pos.py for cross-source consistency.

Source citation:
  Centers for Medicare & Medicaid Services. Medicare Inpatient Hospitals -
  by Provider and Service. FY2024 release. Available:
  https://data.cms.gov/provider-summary-by-type-of-service/medicare-inpatient-hospitals/medicare-inpatient-hospitals-by-provider-and-service
  Dataset UUID: ca9b5ef0-1386-4759-b2b6-5f9b35116786

The exact API query that produced the JSON input is recorded in MANIFEST.

Usage:
    python national/src/02_prepare_ipps.py
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import pandas as pd

REPO = Path(__file__).resolve().parents[2]

CONUS_STATE_CD = {
    "AL","AR","AZ","CA","CO","CT","DC","DE","FL","GA","IA","ID","IL","IN","KS","KY",
    "LA","MA","MD","ME","MI","MN","MO","MS","MT","NC","ND","NE","NH","NJ","NM","NV",
    "NY","OH","OK","OR","PA","RI","SC","SD","TN","TX","UT","VA","VT","WA","WI","WV","WY",
}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--src", default=REPO / "national" / "data" / "raw" / "cms_ipps" / "cms_ipps_drg_FY2024.json",
                   type=Path, help="Path to CMS API JSON response")
    p.add_argument("--release", default="FY2024",
                   help="Release tag for output filename")
    args = p.parse_args()

    if not args.src.exists():
        raise SystemExit(f"input not found: {args.src}")

    print(f"input:  {args.src}  ({args.src.stat().st_size/1e6:.2f} MB)")
    print(f"sha256: {sha256(args.src)}")

    with args.src.open() as f:
        records = json.load(f)
    df = pd.DataFrame(records)
    print(f"  raw rows: {len(df):,}  ({len(df.columns)} cols)")

    print(f"  DRG distribution (raw):")
    for drg, n in df["DRG_Cd"].value_counts().sort_index().items():
        print(f"    {drg}: {n:,}")

    n_before = len(df)
    df = df[df["Rndrng_Prvdr_State_Abrvtn"].isin(CONUS_STATE_CD)]
    print(f"  after CONUS state filter:  {len(df):,}  (dropped {n_before - len(df)})")

    out = REPO / "national" / "data" / "raw" / "cms_ipps" / f"cms_ipps_drg_{args.release}.csv"
    out.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out, index=False)
    print(f"output: {out}  ({out.stat().st_size/1e6:.2f} MB)")
    print(f"sha256: {sha256(out)}")
    print(f"  rows: {len(df):,}  cols: {len(df.columns)}")
    print(f"  distinct CCNs: {df['Rndrng_Prvdr_CCN'].nunique():,}")
    print(f"  distinct states: {df['Rndrng_Prvdr_State_Abrvtn'].nunique()}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
