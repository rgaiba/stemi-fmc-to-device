# Data manifest

Authoritative record of every source file feeding the analysis. For each upload, records:

- **Source URL** — exact download location
- **Release date** — vintage of the source data
- **Access date** — when we pulled it
- **Filter / preparation script** — repo-relative path to the script that turned the raw download into the file the pipeline reads
- **Checksums** — SHA256 of raw input AND derived output, so any deviation from the canonical files surfaces immediately
- **Validation outputs** — counts, distributions, notes from `00_validate_uploads.py`

Anyone re-running the analysis must reproduce the same checksums on the derived files. If they don't, something diverged.

---

## 1. CenPop2020_Mean_BG.txt

- **Source URL:** <https://www2.census.gov/geo/docs/reference/cenpop2020/blkgrp/CenPop2020_Mean_BG.txt>
- **Release vintage:** 2020 Decennial Census (Mean Center of Population by Block Group)
- **Accessed:** 2026-05-07
- **Preparation script:** none (raw file is used as-is, no filter)
- **Repo path:** `national/data/raw/cenpop2020/CenPop2020_Mean_BG.txt`
- **File size:** 10.6 MB
- **Validation:** passed (`python national/src/00_validate_uploads.py --source cenpop2020`)
  - Total rows: 242,335
  - CONUS rows (drop FIPS 02/15/60/66/69/72/78): 238,193
  - CONUS population: 329,260,619
  - Distinct CONUS state FIPS: 49 (48 states + DC)
  - Delaware (STATEFP=10): 706 BGs, population 989,948 ✓ exact match to 2020 Census state total

**Note on row count vs proposal:** the proposal cites 217,740 BGs (a 2010 figure). 2020 BG count is 238,193 CONUS. Update before submission.

---

## 2. CMS Provider of Services — short-term general hospitals (CONUS, active)

### Raw input

- **Source URL:** <https://data.nber.org/homes/data/cms/pos/csv/2024/posotherdec2024.csv>
- **Source:** NBER curated extract of CMS Provider of Services public-use file
- **Release vintage:** December 2024 annual snapshot
- **NBER last-modified:** 2025-09-18
- **Accessed:** 2026-05-07
- **File:** `posotherdec2024.csv` (106 MB, 115,647 rows × 488 cols) — *not committed to repo* (size)
- **SHA256 of raw input:** `5c2811da112e6f707278d647b9e75b40866a1fd1c87dcda38eea9ed93b6f4077`

### Preparation

- **Script:** `national/src/01_prepare_pos.py`
- **Command:** `python national/src/01_prepare_pos.py --src ~/Downloads/posotherdec2024.csv --release 2024-12`
- **Filters applied (in order):**
  1. `prvdr_ctgry_cd == '01'` — short-term general hospitals only (drops nursing homes, hospice, ASCs, RHCs, ESRD, etc.)
  2. `fips_state_cd not in {'02','15','60','66','69','72','78'}` — drops AK, HI, AS, GU, MP, PR, VI by FIPS code
  3. `state_cd in CONUS whitelist` (48 states + DC) — belt-and-suspenders; this caught **282 hospitals** with `state_cd` indicating non-CONUS where `fips_state_cd` did not (predominantly `CN`=Canada at 263, plus `MX`=7, `AK`=3, `HI`=1, `AS`=1)
  4. `pgm_trmntn_cd == '00'` — active providers only (drops 6,311 historically-listed but now-terminated providers)
- **Columns retained:** 15 of 488 (CCN, name, address, FIPS state, category, beds, cardiac cath capability flags, certification date, termination code)

### Derived output

- **Repo path:** `national/data/raw/cms_pos/cms_pos_2024-12.csv`
- **File size:** 0.73 MB
- **Rows × cols:** 6,634 × 15
- **SHA256:** `845e2a2a6d2309dc50e3f62f2843b4f87045d146543c8424e93a033917c59460`
- **Validation:** passed (`python national/src/00_validate_uploads.py --source cms_pos`)
  - 49 CONUS state codes ✓
  - All `prvdr_ctgry_cd='01'`, all `pgm_trmntn_cd='00'` ✓
  - CCNs unique (6,634 distinct)
  - 491 CCNs with `F` suffix (CMS facility-only sub-units; rehab/psych units within parent hospitals — handled in join logic downstream)
  - 66 rows missing `st_adr` (1.0%; addresses recoverable via geocoding from city + ZIP)
  - **PCI capability candidates:**
    - by cath lab service code (1 or 3 = on-site): **1,635**
    - by cath lab room count (≥1): **1,201**
    - concordant on both signals: **1,129**
    - union: 1,707
  - Bed count: median 73, mean 166, max 3,289

**Notes:**
- 263 Canadian-coded hospitals in raw NBER file are CMS-tracked under cross-border Medicare reciprocity (Sec. 1814(f) of the SSA). Excluded from analysis as they are not valid US EMS routing destinations.

### Citation

> National Bureau of Economic Research. Provider of Services Files. Derived from CMS Provider of Services public-use file (Hospital & Non-Long-Term Care), December 2024 release. Available: <https://data.nber.org/data/cms.html>. Accessed 7 May 2026.

---

## 3. CMS IPPS DRG — Medicare Inpatient Hospitals by Provider and Service (AMI severity tiers)

### Raw input

- **Source:** Centers for Medicare & Medicaid Services. *Medicare Inpatient Hospitals - by Provider and Service.* FY2024 release.
- **Source page:** <https://data.cms.gov/provider-summary-by-type-of-service/medicare-inpatient-hospitals/medicare-inpatient-hospitals-by-provider-and-service>
- **Dataset UUID:** `ca9b5ef0-1386-4759-b2b6-5f9b35116786`
- **Accessed:** 2026-05-07
- **API query (canonical provenance line):**
  ```
  GET https://data.cms.gov/data-api/v1/dataset/ca9b5ef0-1386-4759-b2b6-5f9b35116786/data
      ?filter[drg][condition][path]=DRG_Cd
      &filter[drg][condition][operator]=IN
      &filter[drg][condition][value][]=246
      &filter[drg][condition][value][]=247
      &filter[drg][condition][value][]=280
      &filter[drg][condition][value][]=281
      &filter[drg][condition][value][]=282
      &size=50000
  ```
  Response is JSON; saved verbatim as the raw input.
- **File:** `national/data/raw/cms_ipps/cms_ipps_drg_FY2024.json` (2.0 MB, 3,428 records)
- **SHA256 of raw input:** `bc3912b9dbbbac87dee54978fd265cda09b9803176cfec61142342ccf9dcea76`

### Preparation

- **Script:** `national/src/02_prepare_ipps.py`
- **Command:** `python national/src/02_prepare_ipps.py` (defaults to in-repo paths)
- **Filter applied:** `Rndrng_Prvdr_State_Abrvtn` in CONUS whitelist (same set as PoS — 48 states + DC). Drops 20 AK/HI rows.
- **Conversion:** JSON → CSV. Same 15 columns, no column subsetting.

### Derived output

- **Repo path:** `national/data/raw/cms_ipps/cms_ipps_drg_FY2024.csv`
- **File size:** 0.91 MB
- **Rows × cols:** 3,408 × 15
- **SHA256:** `bbd5a5c16e5404fa3741d444e7c784c9dc7062ec1c9ec64c20d9b48578b76a9d`
- **Validation:** passed (`python national/src/00_validate_uploads.py --source cms_ipps`)
  - 49 CONUS states ✓
  - DRG distribution: 280=1,811 / 281=1,234 / 282=363
  - 1,828 distinct hospitals with AMI volume
  - **PoS ↔ IPPS cross-reference:** 1,828 CCN matches (100% of IPPS hospitals are in active PoS list — zero orphans)
  - 4,806 PoS hospitals do not appear in IPPS — these are predominantly small-volume facilities (<11 AMI admissions/year, suppressed by CMS de-identification policy). They remain in the analysis as STEMI-initial-receiving facilities; only their volume weight is unavailable.
  - Total Medicare FFS AMI admissions in file: 119,620 (~15% of all-payer national AMI per AHA estimate, consistent with Medicare-only PUF scope)

### Important note on DRG 246/247 absence

The query above requests DRGs 246, 247, 280, 281, 282. The response contains records only for DRGs 280/281/282 — DRG 246 (PCI w/ DES w/ MCC) and DRG 247 (PCI w/ DES w/o MCC) are not present, even when queried with simple-equality filters (`?filter[DRG_Cd]=246` returns `[]`).

Most likely cause: post-2018 implementation of CMS's 2-midnight rule shifted the majority of uncomplicated PCI to outpatient billing (where they appear in the *outpatient* PUF, not this inpatient file). Residual inpatient PCI volume is below the <11-discharge per-cell suppression threshold at most hospitals.

**Implication for the analysis:** PCI capability is identified from the PoS cardiac catheterization lab service code (§2 of this manifest, 1,635 candidates by service code). The IPPS file is used only for STEMI exposure weighting via DRG 280/281/282 admission volume. Procedural PCI volume cross-reference at the hospital level is not available from this public source. Acknowledged as a limitation in the manuscript.

### Citation

> Centers for Medicare & Medicaid Services. *Medicare Inpatient Hospitals - by Provider and Service (FY2024).* Available: <https://data.cms.gov/provider-summary-by-type-of-service/medicare-inpatient-hospitals/medicare-inpatient-hospitals-by-provider-and-service>. Dataset UUID `ca9b5ef0-1386-4759-b2b6-5f9b35116786`. Accessed 7 May 2026.

---

## 4. tiger_county — pending upload
