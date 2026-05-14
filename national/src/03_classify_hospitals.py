"""
Classify hospitals into Tier A (PCI-capable) / Tier B (non-PCI acute) and
attach analysis-ready attributes per CCN.

Per national/notes/hospital_classification.md, the analysis treats every
active CONUS short-term general hospital as a first-class node. Tier A
hospitals are direct STEMI destinations; Tier B hospitals are initial-
receiving facilities that trigger the DIDO leg on transfer to nearest
Tier A.

Inputs:
  national/data/raw/cms_pos/cms_pos_<release>.csv   (6,634 active CONUS hospitals)
  national/data/raw/cms_ipps/cms_ipps_drg_<release>.csv  (AMI volume per CCN)

Output:
  national/data/processed/hospitals_classified.parquet
  national/data/processed/hospitals_classified.csv     (mirror for human review / git diff)

Schema:
  ccn                              str   primary key (CMS Certification Number)
  fac_name                         str
  st_adr, city_name, state_cd, zip5  str   for geocoding
  fips_state_cd                    str   joins to CenPop2020 STATEFP
  bed_cnt                          Int64 total beds (nullable)
  ruca                             str   1-10 (from IPPS where present)
  ami_volume_2024                  Int64 sum of DRG 280-282 Tot_Dschrgs (null if not in PUF)
  ami_volume_tertile               Int64 1=lowest, 3=highest, within Tier A only (null elsewhere)
  cath_lab_service_code            str   PoS crdc_cthrtztn_lab_srvc_cd raw value
  cath_lab_room_count              Int64 PoS crdc_cthrtztn_prcdr_rooms_cnt as int
  tier                             str   "A" (PCI-capable) | "B" (non-PCI acute)
  is_pci_capable                   bool  tier == "A"
  pci_signal_concordant            bool  cath_service in {1,3} AND room_count >= 1
  is_critical_access_candidate     bool  bed_cnt < 25 AND ruca >= 7
  has_ami_volume_in_puf            bool  ccn has any IPPS DRG 280-282 record
"""
from __future__ import annotations

import argparse
import hashlib
from pathlib import Path

import pandas as pd

REPO = Path(__file__).resolve().parents[2]


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--pos", default=REPO / "national" / "data" / "raw" / "cms_pos" / "cms_pos_2024-12.csv",
                   type=Path)
    p.add_argument("--ipps", default=REPO / "national" / "data" / "raw" / "cms_ipps" / "cms_ipps_drg_FY2024.csv",
                   type=Path)
    p.add_argument("--out-dir", default=REPO / "national" / "data" / "processed", type=Path)
    args = p.parse_args()

    for f in (args.pos, args.ipps):
        if not f.exists():
            raise SystemExit(f"missing input: {f}")

    print(f"pos:  {args.pos}  sha256={sha256(args.pos)[:16]}…")
    print(f"ipps: {args.ipps}  sha256={sha256(args.ipps)[:16]}…")
    print()

    # Load PoS; universe-define to STEMI-routable subtypes only.
    # PoS prvdr_ctgry_cd=01 includes specialty subtypes (long-term, psych,
    # rehab, children's, religious-non-medical) that aren't realistic EMS
    # destinations for adult STEMI. We restrict to:
    #   sbtyp 01 = Short-Term General Hospital   (~3,062)
    #   sbtyp 11 = Critical Access Hospital      (~1,346)
    # Excluded subtypes: 02 long-term, 04 psych, 05 rehab, 06 religious,
    # 20 children's, 28 religious-non-medical, 24/25 IHS specialty, NaN.
    # The excluded ~2,226 hospitals do not appear as Tier A or Tier B nodes
    # in the routing analysis. Documented in notes/hospital_classification.md.
    STEMI_ROUTABLE_SUBTYPES = {"01", "11"}
    pos_full = pd.read_csv(args.pos, dtype=str)
    print(f"PoS raw (all subtypes):      {len(pos_full):,} hospitals")
    pos = pos_full[pos_full["prvdr_ctgry_sbtyp_cd"].isin(STEMI_ROUTABLE_SUBTYPES)].copy()
    print(f"PoS analysis universe (subtypes 01, 11):  {len(pos):,}")
    excluded = pos_full[~pos_full["prvdr_ctgry_sbtyp_cd"].isin(STEMI_ROUTABLE_SUBTYPES)]
    print(f"  excluded subtypes: {dict(excluded['prvdr_ctgry_sbtyp_cd'].value_counts(dropna=False).head(10))}")

    # Load IPPS and aggregate AMI volume per CCN (sum across DRG 280, 281, 282)
    ipps = pd.read_csv(args.ipps, dtype=str)
    ipps["Tot_Dschrgs"] = pd.to_numeric(ipps["Tot_Dschrgs"], errors="coerce")
    ami_per_ccn = (
        ipps.groupby("Rndrng_Prvdr_CCN")
        .agg(ami_volume_2024=("Tot_Dschrgs", "sum"),
             ruca=("Rndrng_Prvdr_RUCA", "first"))
        .reset_index()
        .rename(columns={"Rndrng_Prvdr_CCN": "ccn"})
    )
    print(f"IPPS aggregated: {len(ami_per_ccn):,} hospitals with AMI volume")

    # Join (left from PoS; keep every PoS hospital, attach IPPS where present)
    df = pos.rename(columns={"prvdr_num": "ccn",
                             "zip_cd": "zip5"}).merge(
        ami_per_ccn, on="ccn", how="left"
    )
    assert len(df) == len(pos), "join changed row count; investigate"

    # Numeric coercions, preserving null where missing
    df["bed_cnt"] = pd.to_numeric(df["bed_cnt"], errors="coerce").astype("Int64")
    df["cath_lab_room_count"] = pd.to_numeric(df["crdc_cthrtztn_prcdr_rooms_cnt"], errors="coerce").astype("Int64")
    df["ami_volume_2024"] = df["ami_volume_2024"].astype("Int64")

    # RUCA: keep as string (preserves decimal subcodes like "1.1", "4.1", "7.2"
    # which distinguish primary/secondary commuting flows). For numeric checks we
    # take the floor of the float; RUCA 7.1 floors to 7 = small town, still rural.
    # Code "99" = missing → treated as null.
    ruca_float = pd.to_numeric(df["ruca"].replace("99", pd.NA), errors="coerce")
    ruca_floor = ruca_float.fillna(-1).astype(int)  # -1 sentinel for missing

    # Rename PoS column for output clarity
    df["cath_lab_service_code"] = df["crdc_cthrtztn_lab_srvc_cd"]

    # Tier classification
    is_pci = df["cath_lab_service_code"].isin(["1", "3"])
    df["tier"] = is_pci.map({True: "A", False: "B"})
    df["is_pci_capable"] = is_pci

    # Concordance flag; both PoS PCI signals agree
    df["pci_signal_concordant"] = (
        df["cath_lab_service_code"].isin(["1", "3"])
        & (df["cath_lab_room_count"].fillna(0) >= 1)
    )

    # Critical access flag; definitive via PoS subtype 11. Not a heuristic;
    # subtype 11 is the CMS administrative definition of CAH (matches CCN 13XX
    # convention). RUCA-based heuristic was undercounting CAHs by ~99% because
    # most CAHs are suppressed from IPPS (the only RUCA source).
    df["is_critical_access"] = df["prvdr_ctgry_sbtyp_cd"] == "11"

    df["has_ami_volume_in_puf"] = df["ami_volume_2024"].notna()

    # AMI volume tertile within Tier A only; used for D2B prior stratification
    df["ami_volume_tertile"] = pd.NA
    tier_a_with_volume = df["is_pci_capable"] & df["has_ami_volume_in_puf"]
    if tier_a_with_volume.any():
        tertiles = pd.qcut(
            df.loc[tier_a_with_volume, "ami_volume_2024"].astype(int),
            q=3, labels=[1, 2, 3], duplicates="drop"
        )
        df.loc[tier_a_with_volume, "ami_volume_tertile"] = tertiles
    df["ami_volume_tertile"] = df["ami_volume_tertile"].astype("Int64")

    # Subset and order columns
    keep = [
        "ccn", "fac_name",
        "st_adr", "city_name", "state_cd", "zip5",
        "fips_state_cd",
        "bed_cnt",
        "ruca",
        "ami_volume_2024", "ami_volume_tertile",
        "cath_lab_service_code", "cath_lab_room_count",
        "tier", "is_pci_capable", "pci_signal_concordant",
        "is_critical_access", "has_ami_volume_in_puf",
        "prvdr_ctgry_sbtyp_cd",
    ]
    out = df[keep].sort_values("ccn").reset_index(drop=True)

    # Write parquet (canonical) + CSV (human-reviewable diff)
    args.out_dir.mkdir(parents=True, exist_ok=True)
    pq = args.out_dir / "hospitals_classified.parquet"
    csv = args.out_dir / "hospitals_classified.csv"
    out.to_parquet(pq, index=False)
    out.to_csv(csv, index=False)

    print()
    print(f"output: {pq}  ({pq.stat().st_size/1e6:.2f} MB, sha256={sha256(pq)[:16]}…)")
    print(f"output: {csv}  ({csv.stat().st_size/1e6:.2f} MB, sha256={sha256(csv)[:16]}…)")
    print()
    print(f"=== summary ===")
    print(f"total hospitals:                  {len(out):,}")
    print(f"  Tier A (PCI-capable):           {out['is_pci_capable'].sum():,}")
    print(f"  Tier B (non-PCI acute):         {(~out['is_pci_capable']).sum():,}")
    print(f"  PCI signal concordant (A only): {out['pci_signal_concordant'].sum():,}")
    print(f"  critical access hospitals (subtype 11): {out['is_critical_access'].sum():,}")
    print(f"    of which Tier A (PCI-capable CAH): {(out['is_critical_access'] & out['is_pci_capable']).sum():,}")
    print(f"    of which Tier B (non-PCI CAH):     {(out['is_critical_access'] & ~out['is_pci_capable']).sum():,}")
    print(f"  with AMI volume in PUF:         {out['has_ami_volume_in_puf'].sum():,}")
    print()
    print("Tier A AMI tertile distribution:")
    for t, n in out[out["is_pci_capable"]]["ami_volume_tertile"].value_counts(dropna=False).sort_index().items():
        print(f"  tertile {t}: {n:,}")
    print()
    # AMI volume range per tertile
    if out["is_pci_capable"].sum() and out["has_ami_volume_in_puf"].sum():
        for t in [1, 2, 3]:
            sub = out[(out["is_pci_capable"]) & (out["ami_volume_tertile"] == t)]
            if len(sub):
                print(f"  Tier A tertile {t}: AMI volume range {int(sub['ami_volume_2024'].min())}–{int(sub['ami_volume_2024'].max())} (median {int(sub['ami_volume_2024'].median())})")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
