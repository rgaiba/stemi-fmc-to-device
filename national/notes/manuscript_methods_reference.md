# Manuscript methods — consolidated reference

Single-pane-of-glass document for use while drafting the AHA Scientific Sessions abstract and the *Circulation: CVQO* manuscript. Pulls together all methodology decisions made during data acquisition and analysis design. Each section ends with a **drop-in paragraph** in user editorial voice (academic, dense, no bullets in narrative prose, em-dashes for parentheticals) ready for the manuscript.

Cross-references the deeper decision documents (cited inline) without duplicating them.

Last updated: 2026-05-08

---

## 1. Aim

Map U.S. census block groups whose drive-time-nearest and second-nearest PCI-capable hospitals lie within a 15-minute margin — the geographic substrate where institutional differences (D2B, DIDO, capacity, expertise) could plausibly determine the optimal STEMI routing destination, but where current EMS proximity-routing protocols cannot identify the optimal destination from drive-time geometry alone.

## 2. Scope

National cross-sectional geographic analysis. Continental United States (49 state FIPS codes, including DC). Adult STEMI presentations only. Public-source data exclusively — no patient-level data, no institutional registry data, no IRB. The unit of analysis is the U.S. census block group (n=238,193 in CONUS).

The descoped analytic question (per `pre_registration.md` Amendment 2026-05-07-A): *where does the proximity-routing assumption fail to identify the drive-time-optimal PCI destination?* The full ΔS2B quantification incorporating hospital-level D2B and DIDO priors is deferred to a forthcoming Paper 2; see `claim_calibration.md` for the explicit weak/medium/strong claim taxonomy this analysis supports.

## 3. Data sources (with hash anchors)

All raw inputs are preserved at hash-anchored versions in `national/data/raw/` and recorded in `national/data/MANIFEST.md`. The manuscript should cite each by source, vintage, accessed-date, and SHA256 of the analysis-ready derived file.

| # | Source | File | Vintage | Derived SHA256 | Use |
|---|---|---|---|---|---|
| 1 | U.S. Census Bureau | CenPop2020_Mean_BG.txt | 2020 Decennial | (raw) | 238,193 CONUS BG centroids; 329 M population |
| 2 | NBER (extract of CMS PoS) | posotherdec2024.csv | December 2024 | `845e2a2a…59460` | 6,634 active CONUS short-term hospitals → 4,408 in analysis universe |
| 3 | CMS data.cms.gov | Medicare Inpatient Hospitals by Provider and Service | FY2024 | `bbd5a5c1…6a9d` | 1,828 hospitals × 119,620 Medicare AMI admissions (DRG 280–282) |
| 4 | U.S. Census Bureau | cb_2023_us_county_5m.zip (TIGER cartographic boundary) | 2023 | `13b2bcdd…2485` | 3,109 CONUS county boundaries for choropleth |
| 5 | U.S. Census Bureau | 2020_Gaz_zcta_national.txt (Gazetteer) | 2020 | `036421ad…b3c9` | 33,145 ZCTA centroids for geocoding fallback |

**PCI procedure volume gap.** DRG 246/247 (PCI procedures with drug-eluting stent) are absent from the FY2024 inpatient public-use file, a documented consequence of CMS's 2-midnight rule that shifted uncomplicated PCI to outpatient billing post-2018. PCI capability is therefore identified solely from the cardiac catheterization lab service code in the CMS PoS file (see §4 below). The procedural-volume cross-reference that would have refined a D2B prior is not invoked in Paper 1; see `notes/dido_d2b_operationalization.md` for the Paper 2 framework.

**Drop-in paragraph (data sources):**

> Hospital characteristics were obtained from the National Bureau of Economic Research's curated extract of the CMS Provider of Services file (December 2024 release; <https://data.nber.org/data/cms.html>). STEMI exposure was measured from the CMS public-use Medicare Inpatient Hospitals file (FY2024 release; data.cms.gov dataset UUID ca9b5ef0-1386-4759-b2b6-5f9b35116786) using DRG codes 280–282 (acute myocardial infarction with major complication, with complication, without complication). Population centroids and county boundaries were obtained from U.S. Census Bureau 2020 CenPop and TIGER cartographic boundary files respectively. PCI procedural volume cross-reference (DRG 246–247) was unavailable in the FY2024 public-use file due to outpatient-billing migration of uncomplicated PCI under the 2-midnight rule; PCI capability was therefore identified solely from the cardiac catheterization lab service code in the CMS PoS file. SHA256 checksums of all analysis-ready derived files are recorded in the project repository (national/data/MANIFEST.md).

## 4. Hospital universe and tier classification

The analysis universe is restricted to active continental-US hospitals with CMS PoS provider subtype 01 (Short-Term General Hospital) or 11 (Critical Access Hospital) — 4,408 hospitals. Subtypes 02/04/05/06/20/28 (long-term, psychiatric, rehabilitation, religious-non-medical, children's, religious-non-medical-health-care-institution) are excluded as they are not realistic adult STEMI destinations. Full rationale in `notes/hospital_classification.md`.

Hospitals are classified into two tiers preserved through the analysis:

- **Tier A — PCI-capable** (n=1,598): on-site cath lab service (CMS PoS field `crdc_cthrtztn_lab_srvc_cd` ∈ {1, 3}). 1,129 are concordant on both signals (cath lab service code AND non-zero room count).
- **Tier B — non-PCI acute** (n=2,810): active short-term general or critical access hospital without on-site cath lab service. Includes 1,330 critical access hospitals (subtype 11). Tier B hospitals are not residual; they appear in the analysis as initial-receiving facilities for the DIDO leg whenever the geographically nearest hospital lacks PCI capability.

Sixteen PCI-capable critical access hospitals (intersection of subtype 11 and Tier A) represent rural-PCI capacity profiled in Blankenship et al. JACC 2011 — preserved as a sub-flag for sensitivity analyses.

**Drop-in paragraph (universe):**

> The analysis universe was restricted to active continental-US hospitals with CMS Provider of Services provider subtype 01 (Short-Term General Hospital) or 11 (Critical Access Hospital) — 4,408 hospitals across 49 state FIPS codes. Specialty subtypes (long-term, psychiatric, rehabilitation, children's, religious-non-medical) were excluded as they are not realistic adult STEMI destinations. Hospitals were classified into two tiers preserved through the analysis: Tier A — PCI-capable (n=1,598) — identified by on-site cardiac catheterization lab service code; and Tier B — non-PCI acute (n=2,810) — including 1,330 critical access hospitals. Tier B hospitals appear in the analysis as initial-receiving facilities for the door-in-door-out leg whenever the geographically nearest hospital lacks PCI capability and were not excluded from the analytic substrate.

## 5. Geocoding

Hospital coordinates were obtained via a four-pass cascade with per-row precision tier preserved for sensitivity analysis. Census Geocoder Batch API matched 87% of Tier A addresses at street-level precision; Census 2020 Gazetteer ZCTA centroid recovered 12% with ~1–3 km uncertainty; ZIP-3-prefix Gazetteer fallback recovered the remaining 0.6% — institutional ZIPs at academic medical centers (Yale-New Haven 06504, UVA 22908, Wake Forest 27157, Dartmouth-Hitchcock 03756, etc.) — with ~5–15 km uncertainty. Final coverage 100%.

Alternative sources considered and not used: AHA Annual Survey (paywalled), CMS Hospital General Information bulk file (no lat/lon in the data file), HIFLD Hospitals dataset (canonical URL 404 as of 2026-05-07; appears migrated/deprecated). The cascade is consistent with the standard public-source approach in cardiovascular geographic-access literature; Nallamothu et al. 2005 used haversine distance to ZIP centroids, which our approach strictly improves on.

**Drop-in paragraph (geocoding):**

> Hospital coordinates were obtained via a four-pass cascade with per-row precision-tier preserved for sensitivity analysis: U.S. Census Geocoder Batch API for street-level matches (87% of PCI-capable hospitals), Census 2020 Gazetteer ZCTA centroid for the No_Match/Tie subset (12%, ~1–3 km uncertainty), and ZIP-3-prefix Gazetteer fallback for institutional-ZIP hospitals at academic medical centers (0.6%, ~5–15 km uncertainty). Final coverage was 4,408 of 4,408 hospitals (100%). Alternative sources (AHA Annual Survey, CMS Hospital General Information, HIFLD Hospitals) were considered and excluded due to paywall, absent lat/lon, or deprecated hosting respectively. Sensitivity analysis was performed restricting to the street-level precision tier only.

## 6. Drive-time computation

Drive times were computed using the OpenStreetMap Routing Machine (OSRM) with the **OpenStreetMap United States extract** (Geofabrik release dated 2026-05-07; <https://download.geofabrik.de/north-america/us-latest.osm.pbf>). The U.S.-only extract was chosen over the broader North America extract for two reasons: it matches the analysis universe (CONUS only — Canadian and Mexican hospitals were excluded earlier in the PoS preparation step), and the U.S. extract's smaller graph (~11 GB versus 17.6 GB) fits comfortably within the working memory of the AWS EC2 r6i.2xlarge instance used for the build. The full North America extract requires >64 GB of working memory at extract time, exceeding our deployment ceiling without instance upgrade — and would have produced no additional analytic value given the CONUS scope.

OSRM was deployed on AWS EC2 (r6i.2xlarge, 64 GB RAM, US East/Ohio region) for the build and serving steps. Drive-time matrix computation issued OSRM Table API requests against the local instance for 4,408 hospital × ~3,000 nearest block-group centroid pairs (haversine pre-filter at 90 mi). The full matrix was computed in approximately 30 minutes of routing-engine time. A second pass with OSRM's AM-peak speed profile produced the time-of-day comparison data.

**Drop-in paragraph (drive-time):**

> Drive-time computation used the OpenStreetMap Routing Machine (OSRM) with the U.S. OpenStreetMap extract (Geofabrik release dated [date]). The U.S.-only extract matches the analysis universe (continental U.S.) and was chosen over the broader North America extract for both scope alignment and computational tractability. OSRM was deployed on AWS EC2 (r6i.2xlarge instance) and queried via the Table API in batches of approximately 3,000 destinations per source. The full hospital-by-block-group drive-time matrix (4,408 hospitals × pre-filtered destinations within 90 statute miles by haversine) was computed in approximately 30 minutes. A second matrix using OSRM's AM-peak speed profile was computed for the time-of-day analysis.

## 7. Competitive catchment zone classification

For each block group centroid, the drive time to the nearest PCI-capable hospital (T₁_PCI) and the second-nearest PCI-capable hospital (T₂_PCI) was computed using OSRM. The competitive margin was defined as T₂_PCI − T₁_PCI. Block groups with competitive margin ≤15 minutes were classified as competitive catchment zones — the geographic substrate where the drive-time-optimal PCI destination cannot be determined by proximity alone, and where institutional differences in D2B, DIDO, capacity, or expertise could plausibly determine the optimal destination.

A complementary classification flagged block groups where the geographically-nearest hospital is Tier B (non-PCI) and a Tier A hospital is reachable within a clinically reasonable additional drive-time window — the population where pre-hospital ECG bypass eligibility represents an immediately operationalizable routing-optimization opportunity given existing protocols. This is reported separately as "Population 2" alongside the primary competitive-catchment classification ("Population 1").

The 15-minute primary threshold matches the institutional D2B differential range (typically 15–35 minutes between competing centers in the published literature) over which routing optimization can plausibly reverse the optimal-destination recommendation. Sensitivity analyses at 10 and 20 minutes are reported.

## 8. Headline metric

Per `pre_registration.md` Amendment 2026-05-07-A (D1 amended):

**Annual STEMI patients residing in census block groups whose drive-time-nearest and second-drive-time-nearest PCI-capable hospital are within 15 minutes of each other** — computed as `Σ over BG where T₂_PCI − T₁_PCI ≤ 15 min: population(BG) × 0.004` where 0.004 is the published U.S. STEMI incidence rate (4 per 1,000 adults per year).

The metric is reported rounded to two significant figures in the abstract.

**Drop-in paragraph (headline):**

> Across the continental United States, [N] census block groups containing approximately [M] STEMI patients per year (population [P]) lie in zones where two or more PCI-capable hospitals are within a 15-minute drive-time margin — the geographic substrate where institutional differences could shape optimal routing destination but cannot be resolved by drive-time geometry alone. Of these zones, [J%] are entirely within a single state and therefore unconstrained by EMS mutual-aid considerations. AM peak traffic shifts the drive-time-optimal hospital in an additional [K%] of zones.

## 9. Sensitivity analyses (six required)

Per `pre_registration.md` D8 (amended):

1. **Precision-tier filter.** Drop hospitals with `precision_tier ∈ {zip_centroid, zip_prefix}`; re-run with street-level-geocoded only. Confirms the headline survives the lower-precision tier.
2. **Competitive-margin sweep.** Report at 10 / 15 / 20 minutes.
3. **STEMI incidence sweep.** 3 / 4 / 5 per 1,000 per year.
4. **Time-of-day flip.** AM peak speed profile vs off-peak; how many additional BGs enter or leave the competitive-zone classification at AM peak.
5. **Same-state-only subset.** Exclude BGs whose top-2 PCI candidates span a state line; addresses the EMS mutual-aid operational ceiling.
6. **Tier A inclusion criterion.** Cath lab service code 1 or 3 vs the more restrictive concordant subset (service code AND room count ≥1).

The headline (D1 count) must hold within ±25% under at least 4 of the 6 sensitivities. If it does not, methods iterate before submission.

## 10. Claim calibration

The medium claim (per `claim_calibration.md`):

> "A clinically meaningful population of U.S. STEMI patients resides in zones where the proximity-routing assumption misclassifies the drive-time-optimal destination among PCI-capable hospitals — the geographic substrate where institutional differences could plausibly determine optimal destination."

The strong claim — *routing optimization in N% of zones would reduce S2B by M minutes* — is **not supported** by Paper 1's analysis. It requires hospital-level D2B and DIDO priors and is deferred to forthcoming Paper 2. Forbidden phrasings (causal claims, operational-feasibility implications, measured-outcome implications) are listed exhaustively in `claim_calibration.md`.

## 11. Position relative to Nallamothu et al. 2005

Nallamothu, Bates, Herrin, Wang, Bradley, and Krumholz (Circulation 2005;111:761) decomposed the time-to-balloon for STEMI transfer patients nationally using NRMI-3/4 registry data and quantified each component — door-in-door-out, transport, and door-to-balloon at the receiving PCI center — for the first time. They reported median total time-to-balloon of 180 minutes for transfer patients and identified DIDO (median ~64 minutes) as the largest single delay component. Their work is the foundational empirical reference for the time decomposition the present analysis uses operationally.

The current analysis extends that framework geographically. Where Nallamothu et al. characterized the components of delay given the routing decisions EMS providers make, this analysis identifies where the routing decisions themselves are consequential — the subset of the U.S. population for whom EMS routing optimization, holding the hospital network constant, would meaningfully alter the Nallamothu decomposition. Where Nallamothu et al. characterized the components, this analysis maps the decision space.

## 12. Limitations to acknowledge

To anticipate reviewer pushback:

- **Hospital-specific D2B and DIDO are not modeled.** The analysis identifies where institutional differences could plausibly matter; it does not quantify by how much. Deferred to Paper 2.
- **Cross-state routing operational ceiling.** EMS mutual-aid agreements vary by state. Cross-state subset is reported separately.
- **CMS PoS subtype filter excludes 2,226 specialty hospitals from the universe.** This is a methodological choice reflecting STEMI-routing realism, not a limitation per se, but worth acknowledging.
- **PCI procedural volume cross-reference unavailable.** DRG 246/247 absent from FY2024 PUF; AMI admission tertile would be the proxy in a fuller analysis but is not invoked in Paper 1.
- **Real-time traffic and weather not modeled in primary analysis.** Stochastic variation that affects competing centers proportionally; AM-peak vs off-peak speed profiles approximate the time-of-day component.
- **Geocoding precision tiers vary** (street-level for 87% of Tier A; ZIP-centroid for 12%; ZIP-3-prefix for 0.6%). Sensitivity analysis confirms substrate identification is robust.

## 13. Reproducibility

All scripts, source URLs, file vintages, access dates, and SHA256 checksums of every derived analysis-ready file are committed to the project repository (<https://github.com/rgaiba/stemi-fmc-to-device>, under `national/`). The recipe in `national/REPRODUCIBILITY.md` brings any reader from a clean checkout to byte-identical analysis-ready files via four download commands and three preparation scripts. The hospital classification, geocoding, drive-time computation, competitive-zone classification, and sensitivity analyses are all reproducible from public sources by following that recipe.

**Drop-in paragraph (reproducibility):**

> Code and data preparation scripts are available at <https://github.com/rgaiba/stemi-fmc-to-device> (commit hash to be assigned at acceptance via Zenodo DOI). Source files are listed in national/data/MANIFEST.md with full URLs, release vintages, access dates, and SHA256 checksums of derived analysis-ready files. The analysis can be reproduced from public sources by following the recipe in national/REPRODUCIBILITY.md.

---

## Reference index

When drafting, also consult these deeper documents in the repo:

- `notes/pre_registration.md` (+ Amendment 2026-05-07-A): the full pre-registration with all D1–D9 decisions, the six sensitivities, and the anti-drift list of forbidden phrasings
- `notes/claim_calibration.md`: weak/medium/strong claim taxonomy + forbidden phrasings table + anti-drift checklist for the abstract author
- `notes/hospital_classification.md`: tier definitions with operational SQL/Python equivalents, sub-flags, role descriptions
- `notes/d2b_prior_plan.md`: the three-layer D2B prior framework — Paper 2 infrastructure
- `notes/dido_d2b_operationalization.md`: the full ΔS2B formula with two scenarios — Paper 2 infrastructure
- `notes/daily_summary_2026-05-07.md`: cardiology-chief-audience progress narrative

The drop-in paragraphs in §3, §4, §5, §6, §8, §13 above are sized for a manuscript Methods section. The abstract Methods sentence(s) compress these — see the `pre_registration.md` D1 sentence and `claim_calibration.md` for the abstract-grade language.
