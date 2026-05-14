"""
Prepare the CMS Provider of Services (PoS) hospital list.

Input:  NBER's posotherdec<MMYYYY>.csv (full ~106 MB, ~115k rows, 488 cols)
Output: national/data/raw/cms_pos/cms_pos_<YYYY-MM>.csv (~0.7 MB, ~6.6k rows, 15 cols)

The output is the canonical CONUS short-term general hospital list. Every
downstream PCI identification step (02_identify_pci.py, etc.) joins from this
file.

Filters applied (in order):
  1. prvdr_ctgry_cd == '01'       ; short-term general hospitals
  2. fips_state_cd not in non-CONUS; drops AK/HI/AS/GU/MP/PR/VI by FIPS
  3. state_cd in CONUS whitelist   ; belt+suspenders; drops 'CN' (Canada),
                                      'MX' (Mexico), and any state_cd/fips_state_cd
                                      inconsistencies that slip past filter 2
  4. pgm_trmntn_cd == '00'         ; active providers only

Columns retained: 15 (CCN, name, address, FIPS state, category, beds,
cardiac cath capability flags, certification date, termination code).

Source citation:
  National Bureau of Economic Research. Provider of Services Files. Derived
  from CMS Provider of Services public-use file release dated December 2024.
  https://data.nber.org/data/cms.html  (file: posotherdec2024.csv)

Usage:
    python national/src/01_prepare_pos.py    # uses raw file co-located in data/raw/cms_pos/
    # writes national/data/raw/cms_pos/cms_pos_2024-12.csv

Reproducibility:
    See national/REPRODUCIBILITY.md and national/data/MANIFEST.md for the
    SHA256 checksum of input + output files at each documented release.
"""
from __future__ import annotations

import argparse
import hashlib
from pathlib import Path

import pandas as pd

REPO = Path(__file__).resolve().parents[2]

NON_CONUS_FIPS = {"02", "15", "60", "66", "69", "72", "78"}

CONUS_STATE_CD = {
    "AL","AR","AZ","CA","CO","CT","DC","DE","FL","GA","IA","ID","IL","IN","KS","KY",
    "LA","MA","MD","ME","MI","MN","MO","MS","MT","NC","ND","NE","NH","NJ","NM","NV",
    "NY","OH","OK","OR","PA","RI","SC","SD","TN","TX","UT","VA","VT","WA","WI","WV","WY",
}

KEEP_COLS = [
    "prvdr_num", "fac_name",
    "st_adr", "city_name", "state_cd", "zip_cd",
    "fips_state_cd",
    "prvdr_ctgry_cd", "prvdr_ctgry_sbtyp_cd",
    "bed_cnt", "crtfd_bed_cnt",
    "crdc_cthrtztn_lab_srvc_cd", "crdc_cthrtztn_prcdr_rooms_cnt",
    "crtfctn_dt", "pgm_trmntn_cd",
]


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.split("\n")[1].strip())
    p.add_argument("--src", default=REPO / "national" / "data" / "raw" / "cms_pos" / "posotherdec2024.csv", type=Path,
                   help="Path to NBER posotherdec<MMYYYY>.csv")
    p.add_argument("--release", default="2024-12",
                   help="Release tag for output filename (YYYY-MM)")
    args = p.parse_args()

    if not args.src.exists():
        raise SystemExit(f"input not found: {args.src}")

    print(f"input:  {args.src}  ({args.src.stat().st_size/1e6:.1f} MB)")
    print(f"sha256: {sha256(args.src)}")

    df = pd.read_csv(args.src, dtype=str, low_memory=False)
    print(f"  raw rows: {len(df):,}  ({len(df.columns)} cols)")

    df = df[df["prvdr_ctgry_cd"] == "01"]
    print(f"  after prvdr_ctgry_cd=='01':       {len(df):,}")

    df = df[~df["fips_state_cd"].isin(NON_CONUS_FIPS)]
    print(f"  after non-CONUS FIPS drop:        {len(df):,}")

    n_before = len(df)
    df = df[df["state_cd"].isin(CONUS_STATE_CD)]
    print(f"  after state_cd CONUS whitelist:   {len(df):,}  (dropped {n_before - len(df)})")

    n_before = len(df)
    df = df[df["pgm_trmntn_cd"] == "00"]
    print(f"  after pgm_trmntn_cd=='00':        {len(df):,}  (dropped {n_before - len(df)} terminated)")

    missing = [c for c in KEEP_COLS if c not in df.columns]
    if missing:
        raise SystemExit(f"input missing expected columns: {missing}")
    df = df[KEEP_COLS].copy()

    out = REPO / "national" / "data" / "raw" / "cms_pos" / f"cms_pos_{args.release}.csv"
    out.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out, index=False)
    print(f"output: {out}  ({out.stat().st_size/1e6:.2f} MB)")
    print(f"sha256: {sha256(out)}")
    print(f"  rows: {len(df):,}  cols: {len(df.columns)}")
    print(f"  states: {df['state_cd'].nunique()}")
    print(f"  PCI candidates (cath service 1|3): {df['crdc_cthrtztn_lab_srvc_cd'].isin(['1','3']).sum():,}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
