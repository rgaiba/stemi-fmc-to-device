# Data download guide

Four source files. Download them yourself in this order, apply the filters at download time where possible (smaller uploads, less to clean later), and drop them in the indicated folders. After each upload, run the validation snippet for that source to confirm the shape is right before moving on.

All files are public, no auth required, no IRB.

---

## 1. Population centroids — CenPop 2020 Mean BG (smallest, do this first)

**Why first:** It's tiny (~10 MB), it's the denominator for everything else, and validating it against the Delaware prototype gives an immediate sanity check that the upload path works.

**Download:**
- URL: <https://www2.census.gov/geo/docs/reference/cenpop2020/blkgrp/CenPop2020_Mean_BG.txt>
- It's a single CSV-ish text file (comma-delimited, has a header row).

**No filtering at download.** Take the whole file.

**Drop here:** `national/data/raw/cenpop2020/CenPop2020_Mean_BG.txt`

**Expected:**
- Rows (excluding header): ~242,000 (all U.S. block groups including PR/AK/HI; we drop FIPS 02/15/72 in the pipeline)
- Columns: `STATEFP, COUNTYFP, TRACTCE, BLKGRPCE, POPULATION, LATITUDE, LONGITUDE`
- File size: ~9–10 MB

---

## 2. PCI center identification — CMS Provider of Services (PoS)

**This is the central data-quality input.** Spend more care here than the other three combined. A wrong PCI list contaminates every downstream number.

**Download:**
- URL: <https://data.cms.gov/provider-characteristics/hospitals-and-other-facilities/provider-of-services-file-hospital-non-long-term-care>
- Click the most recent **annual** release (Q4 of the most recent year — annual release has been QC'd; quarterly releases sometimes drop facilities). As of writing, the latest annual is the file labelled "Provider of Services File - Hospital & Non-Hospital Facilities, [most recent year]".
- Choose the **CSV** download.

**Filter at download time using the data.gov column filter UI** (saves ~80% of the upload size):
- `PRVDR_CTGRY_CD` = `01` (short-term general hospital)
- Keep only U.S. states + DC (drop territories: `STATE_CD` not in `PR, VI, GU, MP, AS`)

**Columns to keep** (drop the rest using the column-picker on data.gov before download):
- `PRVDR_NUM` (CMS Certification Number / CCN — primary key)
- `FAC_NAME`
- `ST_ADR`, `CITY_NAME`, `STATE_CD`, `ZIP_CD`
- `PRVDR_CTGRY_CD`, `PRVDR_CTGRY_SBTYP_CD`
- Any column with `CRDC` or `CARDIAC` in the name (cardiac cath / cath lab capability)
- `BED_CNT`
- `CRTFCTN_DT`

**Drop here:** `national/data/raw/cms_pos/cms_pos_<YYYY>.csv`
(replace `<YYYY>` with the release year, e.g., `cms_pos_2024.csv`)

**Expected after filtering:** ~3,500–4,000 rows (short-term general hospitals nationally).

---

## 3. STEMI volume + PCI proxy — CMS IPPS DRG file

**Why we need it:** Two jobs. (a) A hospital with non-zero DRG 246 or 247 volume actually performs PCI — this is the operational truth-check on the PoS-based PCI candidate list. (b) DRG 280–282 volume is the per-hospital STEMI exposure proxy that weights the system ranking.

**Download:**
- URL: <https://data.cms.gov/provider-summary-by-type-of-service/medicare-inpatient-hospitals/medicare-inpatient-hospitals-by-provider-and-service>
- Pick the most recent fiscal year available.
- Choose **CSV** download.

**Filter at download time:**
- `DRG_Cd` (or `MS-DRG`) in `{246, 247, 280, 281, 282}`
  - 246 = PCI w/ drug-eluting stent w/ MCC or 4+ vessels/stents
  - 247 = PCI w/ drug-eluting stent w/o MCC
  - 280/281/282 = AMI w/ MCC / w/ CC / w/o CC
- Keep all 50 states + DC.

**Columns to keep:**
- `Rndrng_Prvdr_CCN` (matches CCN from PoS)
- `Rndrng_Prvdr_Org_Name`
- `Rndrng_Prvdr_State_Abrvtn`
- `DRG_Cd`, `DRG_Desc`
- `Tot_Dschrgs` (the count we'll use)

**Drop here:** `national/data/raw/cms_ipps/cms_ipps_drg_<FY>.csv`
(e.g., `cms_ipps_drg_FY2023.csv`)

**Expected after filtering:** ~10,000–15,000 rows (multiple DRGs × ~3,000 hospitals).

---

## 4. County boundaries (for the choropleth only)

**Why now:** The map is the abstract figure; we need it. **Use the cartographic-boundary generalized version**, not the topological line file — same FIPS codes, ~50× smaller, identical for choropleth purposes.

**Download:**
- URL: <https://www2.census.gov/geo/tiger/GENZ2023/shp/cb_2023_us_county_5m.zip>
- It's a zipped shapefile (~3 MB).

**No filtering.** Continental-US filter (FIPS 02/15/72 dropped) is done in the pipeline.

**Drop here:** `national/data/raw/tiger_county/cb_2023_us_county_5m.zip`
(don't unzip — geopandas reads the zip directly)

**Expected:** ~3,200 counties; file size ~3 MB.

---

## After every upload, run this validation

A small Python script (will be added at `national/src/00_validate_uploads.py` after first upload) will check row counts, expected columns, and basic ranges (lat/lon in CONUS bounds, FIPS codes parseable). Run it after each upload and post the output here. If anything looks off, fix the source file before moving to the next step — cleaning bad data downstream is the most common way these analyses go wrong silently.

---

## Optional but high-value: Mission: Lifeline STEMI-receiving center list

If you can pull a list of currently registered ACC/AHA Mission: Lifeline STEMI-receiving centers (often available as a state-level PDF roster from each state department of health, or aggregated by AHA), drop it at `national/data/raw/mission_lifeline/`. We use it as a third cross-reference for the PCI candidate list — catches small-volume centers that have a cath lab but don't show up in DRG 246/247 because of low Medicare volume. This is the single biggest data-quality lift available for the central contribution; CMS data alone leaves a meaningful gray zone.

If it's a hassle to obtain, skip — the CMS-only list is publishable, just acknowledge the gap in the limitations.

---

## What we will *not* download

- AHA Annual Survey (paywalled, license restricts redistribution; CMS substitutes are sufficient)
- Real-time traffic data (not modeled per proposal §4)
- Patient-level data (not needed; we estimate dS2B at population level)

---

## File sizes after filtering (target totals)

| Source | Raw | After filter |
|---|---|---|
| CenPop2020 | 10 MB | 10 MB (no filter) |
| CMS PoS | ~80 MB | ~2 MB |
| CMS IPPS DRG | ~50 MB | ~1 MB |
| TIGER counties | (5m generalized) | 3 MB |
| **Total upload** | | **~16 MB** |

---

## Reproducibility

This `README.md` is the **how-to-download** guide. The accompanying `MANIFEST.md` is the **what-was-actually-downloaded** ledger — every source file with URL, vintage, prep script, and SHA256 checksum. The repo-root `national/REPRODUCIBILITY.md` documents the broader reproducibility model and gives the manuscript-ready statement template.

Every CSV/parquet under `data/raw/` and `data/processed/` should have its corresponding entry in MANIFEST. If you upload a new source file or re-derive an existing one, update MANIFEST in the same commit.
