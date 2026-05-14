# Data sources: what we extract and what it produces

One row per data source feeding the STEMI competitive transfer zones analysis. Each row maps a dataset to the specific fields we extract from it and the calculation step / downstream metric those fields produce. SHA256 checksums and exact column-level field references live in `national/data/MANIFEST.md`; this file is the human-readable summary suitable for the manuscript Methods.

## Primary datasets

| # | Dataset | Vintage | What we extract | What it produces |
|---|---|---|---|---|
| 1 | **CMS Provider of Services (PoS)** | Dec 2024 (NBER snapshot) | CCN, provider subtype (01 short-term general / 11 critical access), `cath_lab_service_code` (1 or 3 = Tier A), `cath_lab_room_count`, facility name, full address, state FIPS, bed count | Hospital analysis universe (n = 4,408); Tier A PCI-capable (n = 1,598) / Tier B non-PCI acute (n = 2,810); Critical Access Hospital flag; S6 concordant Tier A sensitivity (service code AND room count ≥ 1); geocoding input addresses |
| 2 | **CMS IPPS DRG Public Use File** | FY2024 | Provider CCN, DRG codes 280/281/282 (AMI), `Tot_Dschrgs` | `ami_volume_2024` per hospital (Medicare FFS-only AMI discharge count); AMI volume tertile within Tier A; retained for Paper 2; excluded from `top_hospitals.csv` supplement to avoid FFS-only / all-payer denominator confusion |
| 3 | **CMS Hospital General Information** | 2024 | Hospital lat/lon (primary geocoding source for hospitals present in this file) | Hospital coordinates for OSRM destinations; highest-precision tier (street-level) for matched hospitals |
| 4 | **Census Geocoder API** | 2026 access | Hospital lat/lon (fallback geocoder for hospitals not in CMS HGI); precision tier returned per result | Coordinates for unmatched hospitals via 4-pass cascade (street → ZIP+4 centroid → ZIP centroid → ZIP-3 prefix); S1 sensitivity (drop ZIP-centroid + ZIP-prefix tiers; keep street-level only) |
| 5 | **Census 2020 CenPop Mean BG** | Decennial 2020 (`CenPop2020_Mean_BG.txt`) | 12-digit GEOID (STATEFP + COUNTYFP + TRACTCE + BLKGRPCE), `LATITUDE`, `LONGITUDE`, all-ages `POPULATION` | BG centroid coordinates → OSRM origin points; 238,193-BG CONUS analysis universe; `county_fips` construction for state/county aggregations; all-ages population kept as context only after Amendment 2026-05-08-C (no longer the STEMI rate denominator) |
| 6 | **ACS 2019–2023 5-year, Table B01001 (Sex by Age)** | Released Dec 2024 via Census Data API | Sex-by-age bands aged 20+ summed per BG (18 male bands `B01001_008..025` + 18 female bands `B01001_032..049`) | `adult_pop_20plus` per BG; the STEMI rate denominator; 248.3M CONUS adults aged 20+ national total; used directly in `stemi_per_yr = adult_pop_20plus × 0.001` |
| 7 | **TIGER 2023 Cartographic Boundary Files; Counties (1:5M)** | 2023 vintage | County polygons (multi-part shapes), GEOID, NAME, STATEFP | Choropleth county boundaries (matplotlib + interactive web); 9 CT Planning Region polygons → CT BG-centroid spatial join (`01c_ct_planning_region_crosswalk.py`); 3,109 CONUS counties incl. CT planning regions post-crosswalk |
| 8 | **OpenStreetMap North America extract + OSRM** | Geofabrik May 2026 extract; OSRM build on EC2 r6i.8xlarge (torn down post-run) | Road network → driving-time matrix for every (BG centroid × hospital) pair within 150-mile haversine pre-filter | `drive_times.parquet` (17.6M CCN × bg_id pairs); T1_PCI (nearest PCI), T2_PCI (2nd-nearest PCI), T1_any (nearest of any tier) per BG; `competitive_margin_sec = T2_PCI − T1_PCI`; `is_competitive_15 = margin ≤ 15 min` (the headline classifier); S4 AM-peak sensitivity (post-hoc metro multiplier applied to free-flow times) |

## Published references used as constants or validity anchors

| # | Reference | Year | What we use | What it produces |
|---|---|---|---|---|
| 9 | **AHA Heart Disease and Stroke Statistics 2024** (Tsao/Martin et al., *Circulation*) | Published Jan 2024 | Published U.S. STEMI incidence rate referenced to adults aged 20+ | `INCIDENCE_RATE = 0.001` STEMI per adult/yr; the rate constant in `06`, `07`, `09`; cited in abstract Methods; external validity check #1: implied national STEMI 248,269/yr inside published 250–280k range |
| 10 | **Wang et al., *Circulation* 2024** | Published 2024 | Published 60-min PCI access estimate (91–95% of U.S. adults) | External validity check #2 in `06_classify_zones.py`; compared to our 94.2% (concordant within published band); cited implicitly in abstract Background |
| 11 | **Concannon et al., *Circ: Cardiovascular Quality and Outcomes* 2014** | Published 2014 | Published 30-min PCI access estimate (~80% of U.S. adults) | External validity check #3 in `06_classify_zones.py`; compared to our 80.6% (matches within 1 pp) |

## Derived analytic artifacts

These aren't external datasets but are the canonical intermediates the abstract relies on.

| Artifact | Built from | Purpose |
|---|---|---|
| `hospitals_classified.parquet` | (1) + (2) + (3) + (4) | The canonical hospital frame: CCN, name, geocoded lat/lon, tier (A/B), AMI volume, critical access flag, geocoding precision tier |
| `zones_classified.parquet` | (5) + (6) + (7) + (8) + `hospitals_classified` | The canonical per-BG analytic file. One row per CONUS BG with `population`, `adult_pop_20plus`, drive times to T1_PCI / T2_PCI / T1_any, `competitive_margin_sec`, `is_competitive_10/15/20`, `cross_state` flag |
| `state_summary.csv`, `county_summary.csv`, `top_hospitals.csv` | aggregations over `zones_classified.parquet` | State-level, county-level, and hospital-level rollups feeding the abstract Results and supplement tables |
| `sensitivity_table.csv` | `09_sensitivities.py` over `zones_classified.parquet` + `drive_times.parquet` | Six pre-registered sensitivity analyses; the basis for the abstract's "robust within ±25%" robustness claim |
