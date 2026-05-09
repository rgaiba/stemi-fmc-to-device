# stemi-fmc-to-device

National analysis of U.S. PCI competitive catchment zones for STEMI routing optimization. Companion code and data preparation scripts for the AHA Scientific Sessions 2026 abstract and forthcoming *Circulation: Cardiovascular Quality and Outcomes* manuscript.

> Across the United States, approximately **196,000 STEMI patients per year (79% of U.S. STEMI cases)** live where a second PCI-capable hospital is reachable within 15 additional minutes of drive time beyond the nearest. For these patients, the proximity-based default destination is not necessarily fastest to reperfusion. The geographic substrate is distributed across approximately **1,550 PCI-capable hospitals** rather than concentrated at flagship centers.

The figure below summarises the analysis at the U.S. county level. Each county is shaded by the share of adults whose second-nearest PCI-capable hospital is within 15 minutes of the nearest by drive time. See `national/outputs/figures/choropleth_competitive_zones.pdf` for the publication-quality version.

---

## Where to start (peer reviewers)

The manuscript code, data preparation scripts, audit trail, and all reproducibility artifacts live under [`national/`](./national/).

Recommended reading order for a peer reviewer:

| Read this first | What it answers |
|---|---|
| [`national/REPRODUCIBILITY.md`](./national/REPRODUCIBILITY.md) | How to re-run the analysis from public sources, with the locked operational state of every analytic decision and the operational change log |
| [`national/notes/pre_registration.md`](./national/notes/pre_registration.md) | The dated, append-only methodological audit trail (D1–D9 + Amendments 2026-05-07-A through 2026-05-08-E) |
| [`national/notes/external_validity.md`](./national/notes/external_validity.md) | Concordance of this analysis with published U.S. PCI access estimates (Concannon 2014; Wang 2024) and AHA *Heart Disease and Stroke Statistics* 2024; this is the reviewer-checkable validity record |
| [`national/data/MANIFEST.md`](./national/data/MANIFEST.md) | Per-source provenance: URL, vintage, access date, SHA256 of every derived analysis-ready file |
| [`national/notes/abstract_draft_v9.md`](./national/notes/abstract_draft_v9.md) | The current abstract draft (v9, FINAL) with the edit ledger documenting every change from v1 |

---

## Reproduce from public sources

The analysis re-runs from public sources only. No patient-level data; no IRB. Approximate environment: Python 3.10+, pandas 2.x, numpy 1.24+, geopandas-free pipeline using `pyshp` and `pyproj`. See [`national/REPRODUCIBILITY.md`](./national/REPRODUCIBILITY.md) for the full clean-room recipe.

```bash
git clone git@github.com:rgaiba/stemi-fmc-to-device.git
cd stemi-fmc-to-device

# Python environment
python3 -m venv .venv
source .venv/bin/activate
pip install pandas numpy matplotlib pyproj pyshp pyarrow tqdm scipy scikit-learn

# Pull public-source data files (URLs and expected checksums in national/data/MANIFEST.md)
# then run the pipeline:
python national/src/00_validate_uploads.py
python national/src/01_prepare_pos.py --release 2024-12
python national/src/01b_prepare_acs_age.py
python national/src/02_prepare_ipps.py
python national/src/03_classify_hospitals.py
python national/src/04_geocode_hospitals.py
python national/src/05_osrm_drive_times.py        # requires local OSRM; see notes
python national/src/06_classify_zones.py
python national/src/07_aggregate.py
python national/src/08_choropleth.py
python national/src/09_sensitivities.py
```

The OSRM drive-time matrix (`drive_times.parquet`, ~71 MB) is built once via a one-shot AWS EC2 deployment of the OpenStreetMap U.S. extract; build instructions in [`national/REPRODUCIBILITY.md`](./national/REPRODUCIBILITY.md) and [`national/notes/manuscript_methods_reference.md`](./national/notes/manuscript_methods_reference.md). For the manuscript submission, this file will be deposited on Zenodo with its own DOI so reviewers can skip the OSRM build.

---

## Citing this repository

A `CITATION.cff` file at the repository root provides citation metadata. GitHub renders this as a "Cite this repository" widget. For a tagged release (e.g., `v0.1-aha-ss-2026`), reviewers should cite the specific tag rather than the moving `main` branch.

---

## Repository structure

```
stemi-fmc-to-device/
├── national/                # Manuscript code, data, audit trail (peer-review entry point)
│   ├── REPRODUCIBILITY.md
│   ├── src/                 # Numbered analysis scripts (01_..., 02_..., ...)
│   ├── data/
│   │   ├── MANIFEST.md      # Source provenance with checksums
│   │   ├── raw/             # Public-source downloads (gitignored; regenerable)
│   │   └── processed/       # Pipeline outputs (gitignored; regenerable from scripts)
│   ├── notes/               # Pre-registration, external validity, abstract drafts
│   └── outputs/             # Publication figures and tables
└── legacy/
    └── delaware-prototype/  # Earlier exploratory work (Delaware single-state Vite/React
                             # prototype + ambulance-post p-median optimizer). Not part
                             # of the manuscript; preserved for project history only.
```

---

## License and attribution

Code: MIT (or as specified in LICENSE if added). Data: per the licenses of the upstream Census Bureau, CMS, OpenStreetMap, AHA HDSS sources cited in `national/data/MANIFEST.md`.

Contact: Rahul Gaiba, MD · Bayhealth Medical Center, Department of Internal Medicine.
