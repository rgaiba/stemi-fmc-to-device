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

# Source 4 — TIGER counties (added as script lands)

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

## Reproducibility statement template for the manuscript

> Code and data preparation scripts are available at <https://github.com/rgaiba/stemi-fmc-to-device> at commit `<HASH>` (DOI to be assigned via Zenodo at acceptance). Source files are listed in `national/data/MANIFEST.md` with full URLs, release vintages, access dates, and SHA256 checksums of derived analysis-ready files. The analysis can be reproduced from public sources by following the instructions in `national/REPRODUCIBILITY.md`.
