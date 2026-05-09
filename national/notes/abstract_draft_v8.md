# AHA Scientific Sessions 2026 Abstract — Draft v8

**Date:** 2026-05-08
**Author:** Rahul Gaiba, MD · Bayhealth Medical Center · Department of Internal Medicine
**Track:** Quality, Outcomes, and Resuscitation Sciences
**Status:** v8 — Background reframed around the access-expansion narrative arc; Conclusions S4 simplified (drop "no infrastructure" framing as implicit)

---

## Title

**National Mapping of U.S. PCI Competitive Catchment Zones for STEMI Routing Optimization**

---

## Abstract

**Background.** Time-to-reperfusion drives STEMI mortality. Door-to-balloon time varies substantially between U.S. PCI hospitals (Krumholz 2009, Bradley 2012). Expanded PCI access has placed most U.S. residents within drive-time competitive distance of multiple PCI-capable hospitals; for this population, the geographically nearest hospital is not necessarily the fastest to balloon. The size of this population has not been quantified at the national level.

**Methods.** Cross-sectional national analysis using CMS Provider of Services (December 2024), Census 2020, and OpenStreetMap data. Road-network drive times via OSRM were computed from 238,193 continental U.S. census block group population centroids to all 4,408 active acute care hospitals (1,598 PCI-capable) within 90 miles. Competitive zones were block groups where the second-nearest PCI-capable hospital was within 15 additional minutes of drive time beyond the nearest, a threshold below which institutional door-to-balloon differences between competing PCI centers can offset additional drive time. Annual STEMI estimates used U.S. incidence 1 per 1,000 adults/year (AHA Heart Disease and Stroke Statistics 2024). Headline metric, threshold, and sensitivities were pre-specified in code before analytic results were generated; code is provided for reproducibility. No inferential testing was performed; sensitivities are reported as effect magnitudes.

**Results.** Across the United States, approximately 260,000 STEMI patients per year (79% of U.S. STEMI cases) live where a second PCI-capable hospital is reachable within 15 additional minutes of drive time beyond the nearest. For these patients, the proximity-based default destination is not necessarily fastest to reperfusion. Even the 25 PCI-capable hospitals that are the default destination for the largest number of these patients together account for only 7.5% of this population; the remainder is distributed across approximately 1,550 hospitals. In approximately 3.7% of these areas, the alternative PCI-capable hospital lies in a different state from the patient, raising EMS mutual-aid considerations. Headline finding held within ±25% across all six pre-specified sensitivity analyses (range 209,000–313,000 STEMI patients/year).

**Conclusions.** This first national mapping identifies the U.S. STEMI population for whom EMS routing optimization could meaningfully alter time-to-reperfusion. The substrate is distributed across approximately 1,550 PCI-capable hospitals rather than concentrated at flagship centers. Such routing protocols would complement facility-level interventions like STEMI Receiving Center certification, addressing the between-hospital decision they cannot resolve. Integrating institutional door-to-balloon performance into EMS dispatch decisions, potentially through the National Cardiovascular Data Registry, is a candidate next step toward measurable improvements in time-to-reperfusion. Limitations include free-flow drive-time computation and absence of patient-level outcomes, both addressed in forthcoming work.

---

## Word count + character estimate

- Title: 11 words / 88 characters
- Background: 57 words (was 73 in v6, 58 in v7)
- Methods: 110 words (unchanged from v7)
- Results: 125 words (unchanged)
- Conclusions: 89 words (was 95 in v7)
- **Abstract total: ~392 words / ~2,505 characters**

AHA SS 2,500-char limit: ~5 chars over. Effectively at the limit; final compression options below if portal counts strictly.

---

## Edit ledger v7 → v8

**Two structural moves.**

### 1. Background reframed around the access-expansion arc

**v7 Background sentence 3:** "Current EMS protocols route patients to the geographically nearest hospital, which is not necessarily fastest to balloon when multiple PCI-capable centers are reachable."

**v8 Background sentence 3:** "Expanded PCI access has placed most U.S. residents within drive-time competitive distance of multiple PCI-capable hospitals; for this population, the geographically nearest hospital is not necessarily the fastest to balloon."

The v7 framing was passive ("when multiple PCI-capable centers are reachable") and didn't explain *why* the multi-center situation is now widespread. v8 frames it actively as the consequence of two decades of regionalization-driven PCI expansion, positioning Paper 1 as the natural quantification step that follows from the access expansion. The narrative arc is: (1) time-to-reperfusion matters, (2) D2B varies between hospitals, (3) PCI access expansion now means most people have multiple options, (4) so nearest may not be fastest, (5) we have not yet quantified this population — and Paper 1 fills that gap.

### 2. Conclusions S4 simplified

**v7:** "No infrastructure currently delivers institutional door-to-balloon performance to EMS dispatch; building such a system, potentially through the National Cardiovascular Data Registry, is a candidate next step toward measurable improvements in time-to-reperfusion." (29 words)

**v8:** "Integrating institutional door-to-balloon performance into EMS dispatch decisions, potentially through the National Cardiovascular Data Registry, is a candidate next step toward measurable improvements in time-to-reperfusion." (24 words)

The v7 "No infrastructure currently delivers..." opener stated the obvious. Any reader of an AHA abstract on this topic will assume there is no real-time D2B feed to EMS dispatch today. Stating it explicitly used 9 words to no effect. v8 simply states the candidate next step (integrating D2B into EMS dispatch), naming NCDR as the existing data foundation it could be built on. The reader infers the gap from the "candidate next step" framing. Saves 5 words and reads more confidently.

---

## Pre-submission compression options (if AHA portal counts strictly)

Currently ~5 chars over the 2,500 limit. Smallest viable compression:

| Where | Compression | Saves |
|---|---|---|
| Conclusions | "potentially through the National Cardiovascular Data Registry" → "potentially via NCDR" | ~40 chars |
| Methods | Drop "(AHA Heart Disease and Stroke Statistics 2024)" if portal allows separate citation field | ~50 chars |

Either compression alone brings v8 firmly under 2,500 chars.

---

## Figure caption (unchanged)

**Figure 1.** Geographic distribution of U.S. PCI competitive catchment zones by county. Each county is shaded by the percentage of its population living in a PCI competitive catchment zone, areas where a second PCI-capable hospital is reachable within 15 additional minutes of drive time beyond the nearest. Deep red counties (>75%) are predominantly metropolitan; pale counties (<25%) are predominantly rural; nine counties (no shading) have no PCI-capable hospital within 90 miles. Albers Equal Area Conic projection.

---

## Anti-drift cross-reference (per claim_calibration.md, v8)

- ✅ Background frames PCI access expansion as the structural driver of competitive geometry
- ✅ "Could meaningfully alter time-to-reperfusion" — substrate-level
- ✅ "Default destination is not necessarily fastest" — statement of insufficiency
- ✅ "Such routing protocols would complement..." — conditional verb tracks analytic warrant
- ✅ "Integrating ... is a candidate next step" — directional, points at solution without claiming demonstration
- ✅ "Toward measurable improvements" — directional language; explicitly does not measure outcome
- ❌ NOT claiming the routing optimization *does* save time
- ❌ NOT claiming any specific hospital is the wrong destination
- ❌ NOT claiming live D2B data infrastructure exists today (now implicit rather than explicit)
