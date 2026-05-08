# National STEMI Routing Analysis — Day 1 Progress Summary
**Date:** 7 May 2026
**For:** Cardiology Chief review · personal records and future writing reference
**Author:** Rahul Gaiba, MD · Bayhealth Medical Center · Department of Internal Medicine

---

## Project aim

Quantify the national modifiable burden of symptom-to-balloon delay in STEMI patients attributable to suboptimal EMS routing — that is, the population-level minutes of reperfusion delay that would be eliminated if EMS providers had access to a routing decision tool that incorporated institutional D2B performance and DIDO penalties at the point of first medical contact, rather than defaulting to the geographically nearest emergency department.

The output is a ranked map: U.S. hospital systems ordered by the volume-weighted ΔS2B that EMS routing protocol adoption would deliver for the population in their catchment.

## Scope

National cross-sectional geographic analysis. Continental United States (49 states + DC). Adult STEMI presentations only. Public-source data exclusively — no patient-level data, no institutional registry data, no IRB. Targeting *Circulation: Cardiovascular Quality and Outcomes* and AHA Scientific Sessions 2026.

The unit of analysis is the U.S. census block group (n=238,193 in CONUS); each is classified by the drive-time margin between its nearest and second-nearest PCI-capable hospital. Block groups where that margin is ≤15 minutes are *competitive catchment zones* — the population where institutional D2B differentials, not distance, determine the optimal STEMI destination.

## Rationale

Time is myocardium and the bottleneck has moved upstream. Mission: Lifeline and statewide regionalization have driven median D2B at high-volume centers below 60 minutes; the leverage point in the STEMI care pathway is now the first routing decision EMS makes, before any clock at any hospital starts. That decision is currently made on proximity. Proximity is not always the same as fastest-to-balloon. In any region served by multiple PCI centers with meaningfully different D2B profiles — and there are dozens of such corridors nationally — proximity routing produces predictable, avoidable S2B penalty for patients routed to the suboptimal destination.

This problem has not been mapped at the national level. The hospitals serving these corridors have not been ranked by the magnitude of S2B improvement EMS routing optimization could deliver. The analysis is structurally tractable from public data, the methodological precedent exists (Nallamothu et al. and successors), and the deliverable — a ranked national map — directly informs Mission: Lifeline expansion priorities and prospective EMS protocol deployment.

## Position relative to Nallamothu et al.

Nallamothu, Bates, Herrin, Wang, Bradley, and Krumholz (Circulation 2005;111:761) established that geographic distance to PCI capability independently predicts STEMI outcomes and that transfer patients in particular accumulate substantial reperfusion delays. Their NRMI-3/4 analysis motivated the regionalization movement that followed: build PCI capability where it didn't exist, expand the network of PCI-capable hospitals, drive D2B down at receiving centers.

The current analysis extends that framework from *access* to *routing*. Where Nallamothu et al. asked "can the patient reach PCI?", the question here is "is the patient being routed to the right PCI center?" That is a structurally different question with a structurally different intervention. Geographic access deficit requires new infrastructure; routing suboptimality requires information systems and protocol change. The two have been conflated in the regionalization literature; separating them is the methodological contribution.

The companion Delaware prototype (a working web demonstration of the routing interface concept) provides encounter-level proof of concept; this national analysis provides the geographic evidence base for system-level deployment prioritization. Together they describe a complete research arc: identify the opportunity (national analysis), prove the tool (Delaware prototype), validate prospectively (cohort study in identified high-priority corridors).

## Accomplishments — 7 May 2026

### Data acquisition (complete for all primary sources)

**1. CMS Provider of Services file (December 2024 release).** 6,634 active continental-US short-term hospitals after applying the analysis-universe restriction to subtypes 01 (Short-Term General Hospital) and 11 (Critical Access Hospital). The subtype filter excludes 2,226 PoS-listed facilities — psychiatric, rehabilitation, long-term, children's, and religious-non-medical hospitals — that are not realistic adult STEMI destinations and that earlier versions of similar analyses have inadvertently included.

**2. CMS IPPS public-use file (FY2024).** 1,828 hospitals reporting 119,620 Medicare fee-for-service AMI admissions (DRG 280, 281, 282). 100% of IPPS-listed hospitals match an active PoS hospital — perfect cross-source consistency. Hospitals with fewer than 11 admissions per cell are suppressed under CMS de-identification policy and remain in the analysis without volume weights but are otherwise unchanged.

**3. CenPop 2020 block group centroids.** 238,193 population-weighted centroids covering 329 million continental-US residents. The 2020 vintage supersedes the 217,740 figure widely cited from 2010-decennial-era analyses.

**4. Census TIGER cartographic boundary file (2023).** 3,109 continental-US counties for choropleth aggregation.

**5. Census 2020 Gazetteer ZCTA centroids.** Geocoding fallback for institutional ZIPs (33,145 ZCTAs).

### Hospital classification

The 4,408 analysis-universe hospitals were classified into a two-tier model:

- **Tier A — PCI-capable:** 1,598 hospitals identified by on-site cardiac catheterization service code (CMS PoS field). Of these, 1,129 had concordant signals from both the cath lab service code and the cath lab room count, providing a high-confidence subset for sensitivity analyses.
- **Tier B — non-PCI acute:** 2,810 hospitals. These are not residual; they are first-class analytic nodes that appear in the modifiable-S2B calculation as initial-receiving facilities for the DIDO leg whenever the geographically nearest hospital lacks PCI capability.
- **Critical access hospitals:** 1,346 (subtype 11). Of these, 16 are PCI-capable — a notable rural-PCI-success-story population profiled in the Blankenship JACC 2011 paper and worth following in subgroup analyses.

PCI procedure volume cross-reference (CMS DRG 246/247) is unavailable in the FY2024 public-use file due to post-2018 outpatient billing migration of uncomplicated PCI under the 2-midnight rule. AMI admission tertile within the Tier A set substitutes as a published-correlated proxy for the D2B-prior stratification role those DRGs would have served.

### Geocoding

A four-pass cascade — Census Geocoder Batch street-level (87% of Tier A), Census Gazetteer ZIP centroid (12%), and ZIP-3-prefix fallback for institutional ZIPs at academic medical centers (0.6%) — yielded 100% coverage with per-hospital precision tier preserved for sensitivity analysis. Alternatives considered and ruled out: AHA Annual Survey (paywalled, license-restricted), CMS Hospital General Information (bulk download contains no coordinates), HIFLD Hospitals dataset (current canonical URL returns 404 as of 7 May 2026).

### Reproducibility infrastructure

All scripts, source URLs, file vintages, access dates, and SHA256 checksums of every derived analysis-ready file are committed to the project repository (github.com/rgaiba/stemi-fmc-to-device, under `national/`). The recipe in `REPRODUCIBILITY.md` brings any reader from a clean checkout to byte-identical analysis-ready files via four download commands and three preparation scripts. The hospital classification and D2B prior strategies are documented in repository decision notes (`national/notes/`) so that any reviewer can trace each numerical claim in the methods to the script that produces it.

## Reproducibility statement *(for clinical audience)*

Every input file used in this analysis is publicly downloadable from a federal government source (CMS, U.S. Census Bureau) without registration or fee. Every transformation from raw input to analysis-ready data is performed by a numbered script in the project's GitHub repository. Every analysis-ready file has a recorded SHA256 checksum so that any reader re-running the same scripts on the same source files arrives at byte-identical outputs. There is no hidden processing step, no manual data entry, and no patient-level data. A clinician without programming experience cannot re-run the pipeline directly, but a clinician collaborating with a data scientist or biostatistician can independently verify every claim in the manuscript by reading the methods, opening the repository, and comparing checksums.

## Generalizability statement *(for clinical audience)*

The analysis covers all PCI-capable and non-PCI acute care hospitals in the continental United States that participate in the Medicare program — 4,408 hospitals across 49 states and the District of Columbia. The STEMI exposure denominator is Medicare fee-for-service admission volume, which under-counts younger adults and Medicare Advantage enrollees but does not bias the geometry of the routing analysis (proximity and D2B differentials affect Medicare and non-Medicare patients identically within any given catchment). Real-time traffic and weather are not modeled in the primary analysis; their effects are stochastic at national cross-sectional scale and affect competing PCI centers proportionally within any single competitive zone, leaving relative drive-time margins approximately stable. A time-of-day sensitivity analysis using OSRM speed profiles for AM peak versus off-peak hours is part of the planned analysis. The methodology — population-centroid catchment classification with a two-tier first-receiving-facility / definitive-care-facility node model — translates directly to acute stroke (mothership-vs-drip-and-ship routing), trauma (Level I trauma center catchment), and obstetric care (high-acuity maternal transfer) without structural modification.

## What's not yet done

Drive-time computation via OpenStreetMap Routing Machine (OSRM); competitive zone classification with the 15-minute primary threshold; ΔS2B estimation per block group; hospital system ranking; the choropleth figure; sensitivity analyses (uniform D2B prior, Mission: Lifeline-only subset, time-of-day, competitive margin threshold robustness at 10 and 20 min); manuscript draft.

The intended order is: drive-time matrix → competitive zone classification → ΔS2B → system ranking → figure → abstract → manuscript, with sensitivity analyses interleaved at each step that produces a numerical output.
