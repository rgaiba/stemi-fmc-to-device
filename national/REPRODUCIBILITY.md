# Reproducibility

This analysis follows the *re-run from public sources* standard expected for *Circulation: Cardiovascular Quality and Outcomes* and similar cardiovascular outcomes journals. Anyone with internet access and Python should be able to reproduce every number in the manuscript from this repository.

## What "reproducible" means here

Three layers, each verifiable independently:

1. **Same inputs.** Every source file is documented in `data/MANIFEST.md` with its source URL, release vintage, access date, and SHA256 checksum. Anyone re-downloading from the same source URL on the same NBER/CMS/Census release should compute the same SHA256.

2. **Same derivation.** Every transformation from raw input to analysis-ready file lives in a numbered script under `src/`. Running the scripts in numeric order against the documented inputs reproduces the derived files in `data/raw/`. Each derived file's SHA256 is also recorded in MANIFEST.

3. **Same outputs.** Every figure and table in the manuscript is traceable to a script in `src/` that produces it from `data/processed/` artifacts. Random seeds (where used) are fixed and documented.

If any of those three layers diverges between two runs, the diverging step is identifiable.

## What goes in MANIFEST vs what goes in REPRODUCIBILITY

- **MANIFEST.md** — per-file: source, vintage, accessed date, prep command, checksums, validation summary. Authoritative record of *what data* the analysis uses.
- **REPRODUCIBILITY.md** *(this file)* — per-analysis: the rules above + how to bring up a clean environment to re-run. Authoritative record of *how to use* the data.

## Clean re-run from a new machine

```bash
git clone git@github.com:rgaiba/stemi-fmc-to-device.git
cd stemi-fmc-to-device

# Python environment (will be pinned in requirements.txt as src/ matures)
python -m venv .venv
source .venv/bin/activate
pip install pandas numpy geopandas matplotlib requests pyarrow tqdm scipy scikit-learn

# Pull source files. URLs and expected checksums are in national/data/MANIFEST.md.
# Each script writes a derived file to national/data/raw/<source>/.
cd national

# Source 1 — population centroids (no prep, used as-is)
curl -o data/raw/cenpop2020/CenPop2020_Mean_BG.txt \
  https://www2.census.gov/geo/docs/reference/cenpop2020/blkgrp/CenPop2020_Mean_BG.txt

# Source 2 — CMS PoS hospital list (filter via NBER snapshot)
curl -A "Mozilla/5.0" -o data/raw/cms_pos/posotherdec2024.csv \
  https://data.nber.org/homes/data/cms/pos/csv/2024/posotherdec2024.csv
python src/01_prepare_pos.py --release 2024-12   # raw file already in data/raw/cms_pos/

# Source 3 — CMS IPPS DRG (filtered API query saves directly to raw/)
URL='https://data.cms.gov/data-api/v1/dataset/ca9b5ef0-1386-4759-b2b6-5f9b35116786/data'
curl -G \
  --data-urlencode 'filter[drg][condition][path]=DRG_Cd' \
  --data-urlencode 'filter[drg][condition][operator]=IN' \
  --data-urlencode 'filter[drg][condition][value][]=246' \
  --data-urlencode 'filter[drg][condition][value][]=247' \
  --data-urlencode 'filter[drg][condition][value][]=280' \
  --data-urlencode 'filter[drg][condition][value][]=281' \
  --data-urlencode 'filter[drg][condition][value][]=282' \
  --data-urlencode 'size=50000' \
  -o data/raw/cms_ipps/cms_ipps_drg_FY2024.json \
  "$URL"
python src/02_prepare_ipps.py

# Source 4 — TIGER counties (used as-is, no prep script)
curl -L -o data/raw/tiger_county/cb_2023_us_county_5m.zip \
  https://www2.census.gov/geo/tiger/GENZ2023/shp/cb_2023_us_county_5m.zip

# Validate every uploaded source against the canonical specs
python src/00_validate_uploads.py
```

After running, every file under `data/raw/<source>/` should have a SHA256 matching the one in `data/MANIFEST.md`. If a checksum diverges:

- A new release was published to the same URL by the upstream provider (NBER, CMS, Census) — this is rare but happens. Update MANIFEST with the new vintage and rerun validation; if the validator still passes, the divergence is benign.
- A bug was introduced in the prep script — diff against the script's last passing commit.
- Local environment difference (line endings on Windows) — re-run on Linux/macOS.

## What is *not* in the repo

- **Raw NBER `posotherdec2024.csv` (106 MB)** — too large to commit. URL is in MANIFEST and the prep script downloads it on demand.
- **OSRM road network extracts** — multi-GB OSM `.pbf` files; documented in MANIFEST with download URL and Docker setup commands.
- **Patient-level data** — none used. This is a population-geography analysis on public sources only; no IRB.

## Analytic decisions and changes

This is not a registered study (no IRB; no protocol filed with ClinicalTrials.gov or an AHA pre-registration registry). It uses public population, hospital, and road-network data only.

Methodological decisions are recorded in two complementary places:

- **`notes/pre_registration.md`** is the dated, append-only methodological audit trail. Original decisions D1–D9 were locked on 2026-05-07 before any drive-time computation; subsequent changes are filed as dated amendments (2026-05-07-A, 2026-05-08-A through D as of this commit). That file is the authoritative methodological log; if it conflicts with anything below, it wins.
- **This section** is the operational mirror: a single-table snapshot of *current* values for each decision keyed to the script that implements it, plus an operational change log focused on which artifacts were re-derived after each change. Read it to answer "what does the code do today and which file changed when X was changed."

### Locked decisions (current operational state)

| # | Decision | Value | Implemented in |
|---|---|---|---|
| D1 | Hospital analysis universe | CMS PoS subtypes 01 (short-term general) and 11 (critical access); active CONUS only | `src/03_classify_hospitals.py` |
| D2 | Tier A (PCI-capable) definition | `cath_lab_service_code in {"1","3"}` | `src/03_classify_hospitals.py` |
| D3 | Tier B (non-PCI acute) definition | analysis-universe hospital with `cath_lab_service_code not in {"1","3"}` | `src/03_classify_hospitals.py` |
| D4 | Geographic scope | CONUS block groups (exclude STATEFP 02 Alaska, 15 Hawaii, 72 Puerto Rico) | `src/06_classify_zones.py` |
| D5 | Drive-time engine | OSRM with the U.S. OSM extract, `car` profile, free-flow speeds (no live traffic) | `src/05_drive_times.py`, OSRM build on EC2 (torn down post-run) |
| D6 | Competitive-zone definition | `T2_PCI − T1_PCI ≤ 15 min` (primary). 10 and 20 min reported as sensitivity | `src/06_classify_zones.py`, `09_sensitivities.py` (S2) |
| D7 | Hospital geocoding precision tiers | All four tiers admitted to primary (street, ZIP+4 centroid, ZIP centroid, ZIP-3 prefix); street-only sensitivity in S1 | `src/04_geocode_hospitals.py`, `09_sensitivities.py` (S1) |
| D8 | STEMI incidence rate and denominator | **0.001 STEMI per adult aged 20+ per year** (AHA *Heart Disease and Stroke Statistics* 2024) applied to **block-group adult population aged 20+** sourced from ACS 2019-2023 5-year table B01001 (Sex by Age). Adult cutoff matches the rate's NHANES-based denominator. Rate sweep at 0.0008 / 0.0010 / 0.0012 reported as sensitivity (S3). | `src/01b_prepare_acs_age.py` (denominator), `src/06_classify_zones.py`, `07_aggregate.py`, `09_sensitivities.py` (S3) |
| D9 | Time-of-day (AM peak) handling | Literature-based metropolitan multiplier (urban ×1.30 / suburban ×1.15 / rural ×1.05) applied to free-flow drive times. OSRM speed profiles not used. Reported as sensitivity, not as primary | `src/09_sensitivities.py` (S4) |
| D10 | Cross-state routing | Cross-state pairs admitted to primary; same-state-only reported as sensitivity | `src/06_classify_zones.py` (`cross_state` flag), `09_sensitivities.py` (S5) |
| D11 | Tier A concordance check | Sensitivity adds `cath_lab_service_code in {"1","3"} AND cath_lab_room_count ≥ 1` as a tighter Tier A definition | `src/09_sensitivities.py` (S6) |
| D12 | External validity anchors | Two automated checks on every run of `06_classify_zones.py`: (a) implied national STEMI count from rate × denominator must fall in 250,000–280,000/yr (AHA HDSS 2024); (b) % CONUS adults within 30/60/90 min of nearest PCI hospital must match Concannon (Circ CVQO 2014) and Wang (Circulation 2024) within ±1 percentage point. WARN, not fail, if out-of-band. | `src/06_classify_zones.py` (External Validity Checks block); narrative record at `notes/external_validity.md` |

### Change log

Each entry records the date, the change, the reason, and the artifacts that were re-derived. Entries before 2026-05-08 are reconstructions: they correspond to commitments visible in the current code state but the original prose log did not survive into this commit. They are dated to the day the corresponding code was committed where determinable from `git log`.

**2026-05-07 — Scope descope.** Project scope reduced from a combined drive-time-plus-D2B model to drive-time geometry only for Paper 1. D2B-conditional analyses moved to a planned Paper 2. *Reason:* the absence of facility-specific live D2B data made the combined model speculative for the headline claim; drive-time geometry is independently defensible from public sources. *Re-derived:* analytic scope; no numerical outputs existed yet at this point.

**2026-05-08 — Time-of-day handling.** Switched from per-edge OSRM speed profiles (planned but not built) to a literature-based metropolitan multiplier (urban ×1.30 / suburban ×1.15 / rural ×1.05) applied to free-flow drive times, reported only as sensitivity S4. *Reason:* OSRM speed profiles for the U.S. extract require traffic count layers that are not in the public OSM data, and the metro multiplier preserves the qualitative claim (peak-hour competitive-zone reclassification) without overstating the measurement precision. *Re-derived:* `09_sensitivities.py` S4 row in `outputs/tables/sensitivity_table.csv`.

**2026-05-08 — STEMI incidence rate, first correction.** Changed from 0.004/yr (AMI rate, applied to all-ages BG population) to 0.001/yr (per-adult STEMI rate, applied to all-ages BG population). *Reason:* AMI ≠ STEMI; the original rate conflated the two. *Re-derived:* `zones_classified.parquet`, `state_summary.csv`, `county_summary.csv`, `top_hospitals.csv`, `sensitivity_table.csv`. *Known residual issue at the time:* the per-adult rate was being applied to a denominator that includes children, leaving the implied national STEMI count ~25% high; flagged for later correction (see next entry).

**2026-05-08 — STEMI incidence rate, second correction (calibration approach, superseded same day).** Changed from 0.001/yr (per-adult, applied to all-ages population) to **0.0008/yr (calibrated to all-ages population)**. *Reason at the time:* with 0.001 × CONUS all-ages population, the implied national STEMI count was ~329,000/yr, materially above the AHA *Heart Disease and Stroke Statistics* 2024 range (~250–280k). 0.0008 was chosen to calibrate the implied count to ~263k while keeping the existing all-ages denominator. *Status:* superseded by the next entry the same day. The calibration approach was discarded in favor of correcting the denominator directly, because (a) "rate × calibrated rate" is awkward to defend in Methods and (b) per-adult rate × adult population is the same multiplication a reviewer would do mentally. The 0.0008 value is preserved only as one of the rate-sweep points in S3.

**2026-05-08 — STEMI incidence rate, third correction (denominator approach, current).** Reverted the rate to **0.001 per adult aged 20+ per year** (the published AHA value) and changed the denominator from all-ages BG population to **adults aged 20+ from ACS 2019-2023 5-year table B01001 (Sex by Age)**, sourced via a new script `01b_prepare_acs_age.py`. *Reason:* the right fix for the original methodological mismatch is to correct the denominator to the population the rate references, not to rescale the rate against the wrong denominator. The adult cutoff is 20+, matching the NHANES adult definition that AHA uses to anchor STEMI rates. ACS 5-year is the only Census product with block-group age structure. *Affected scripts:* `01b_prepare_acs_age.py` (new), `06_classify_zones.py` (joins adult population), `07_aggregate.py`, `09_sensitivities.py`. *Re-derived:* `zones_classified.parquet`, `state_summary.csv`, `county_summary.csv`, `top_hospitals.csv`, `sensitivity_table.csv`. *Headline impact:* annual competitive-zone STEMI count is in the ~200,000 range (a few percent below the calibrated 0.0008 value, varies by local age structure).

**2026-05-08 — ACS pull bug discovered and fixed in `01b_prepare_acs_age.py` (pre-merge).** The first run of `01b_prepare_acs_age.py` undercounted adults 20+ by approximately 10M nationally because the male and female age-band ranges started at B01001_010E and B01001_034E, respectively, silently dropping the single-year-of-age cohorts at 20 and 21 (B01001_008E/009E for males and B01001_032E/033E for females). The error surfaced as an implausibly low adult fraction (0.726 vs expected ~0.75). Same run also pulled all 50 states + DC, including Alaska and Hawaii, which the competitive-zone analysis universe excludes from CONUS. Both issues fixed before the file was merged into `zones_classified.parquet`: the variable ranges now span B01001_008–025 (male) and B01001_032–049 (female), 36 adult bands total, and the state list is reduced to the 49 CONUS entities (48 contiguous states + DC). *Re-derived:* none yet (caught pre-merge); the broken ACS CSV was overwritten in place. The script docstring carries the variable-layout gotcha so a future editor does not reintroduce the off-by-two.

## Reproducibility statement template for the manuscript

> Code and data preparation scripts are available at <https://github.com/rgaiba/stemi-fmc-to-device> at commit `<HASH>` (DOI to be assigned via Zenodo at acceptance). Source files are listed in `national/data/MANIFEST.md` with full URLs, release vintages, access dates, and SHA256 checksums of derived analysis-ready files. The analysis can be reproduced from public sources by following the instructions in `national/REPRODUCIBILITY.md`.
