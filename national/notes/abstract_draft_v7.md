# AHA Scientific Sessions 2026 Abstract — Draft v7

**Date:** 2026-05-08
**Author:** Rahul Gaiba, MD · Bayhealth Medical Center · Department of Internal Medicine
**Track:** Quality, Outcomes, and Resuscitation Sciences
**Status:** v7 — Background simplified (drop IQR/extreme numbers); Conclusions tightened on facility-level sentence; live-D2B reframed as "build such infrastructure (potentially through NCDR)" since the data delivery system does not yet exist

---

## Title

**National Mapping of U.S. PCI Competitive Catchment Zones for STEMI Routing Optimization**

---

## Abstract

**Background.** Time-to-reperfusion drives STEMI mortality. Door-to-balloon time varies substantially between U.S. PCI hospitals (Krumholz 2009, Bradley 2012). Current EMS protocols route patients to the geographically nearest hospital, which is not necessarily fastest to balloon when multiple PCI-capable centers are reachable. No prior analysis has identified the U.S. STEMI population for whom this routing decision is consequential.

**Methods.** Cross-sectional national analysis using CMS Provider of Services (December 2024), Census 2020, and OpenStreetMap data. Road-network drive times via OSRM were computed from 238,193 continental U.S. census block group population centroids to all 4,408 active acute care hospitals (1,598 PCI-capable) within 90 miles. Competitive zones were block groups where the second-nearest PCI-capable hospital was within 15 additional minutes of drive time beyond the nearest, a threshold below which institutional door-to-balloon differences between competing PCI centers can offset additional drive time. Annual STEMI estimates used U.S. incidence 1 per 1,000 adults/year (AHA Heart Disease and Stroke Statistics 2024). Headline metric, threshold, and sensitivities were pre-specified in code before analytic results were generated; code is provided for reproducibility. No inferential testing was performed; sensitivities are reported as effect magnitudes.

**Results.** Across the United States, approximately 260,000 STEMI patients per year (79% of U.S. STEMI cases) live where a second PCI-capable hospital is reachable within 15 additional minutes of drive time beyond the nearest. For these patients, the proximity-based default destination is not necessarily fastest to reperfusion. Even the 25 PCI-capable hospitals that are the default destination for the largest number of these patients together account for only 7.5% of this population; the remainder is distributed across approximately 1,550 hospitals. In approximately 3.7% of these areas, the alternative PCI-capable hospital lies in a different state from the patient, raising EMS mutual-aid considerations. Headline finding held within ±25% across all six pre-specified sensitivity analyses (range 209,000–313,000 STEMI patients/year).

**Conclusions.** This first national mapping identifies the U.S. STEMI population for whom EMS routing optimization could meaningfully alter time-to-reperfusion. The substrate is distributed across approximately 1,550 PCI-capable hospitals rather than concentrated at flagship centers. Such routing protocols would complement facility-level interventions like STEMI Receiving Center certification, addressing the between-hospital decision they cannot resolve. No infrastructure currently delivers institutional door-to-balloon performance to EMS dispatch; building such a system, potentially through the National Cardiovascular Data Registry, is a candidate next step toward measurable improvements in time-to-reperfusion. Limitations include free-flow drive-time computation and absence of patient-level outcomes, both addressed in forthcoming work.

---

## Word count + character estimate

- Title: 11 words / 88 characters
- Background: 58 words (was 73 in v6)
- Methods: 110 words (was 109)
- Results: 125 words (unchanged)
- Conclusions: 95 words (S3 tightened from 27→18 words; S4 expanded with infrastructure framing 20→29 words; net -3)
- **Abstract total: ~398 words / ~2,540 characters**

AHA SS 2,500-char limit: ~40 chars over. Pre-submission compression options below.

---

## Edit ledger v6 → v7

**Three substantive changes per editorial review.**

### 1. Background simplified

**v6:** "Inter-hospital door-to-balloon variation between U.S. PCI hospitals is documented and persistent, with interquartile ranges of approximately 20–25 minutes and extreme differentials reaching 50–60 minutes between high- and low-performing centers (Krumholz 2009, Bradley 2012)."

**v7:** "Door-to-balloon time varies substantially between U.S. PCI hospitals (Krumholz 2009, Bradley 2012)."

D2B variation is a well-established fact in cardiology; specific IQR and extreme-differential numbers are unnecessary precision in the Background of an abstract aimed at clinicians familiar with the field. The simpler inferential phrasing relies on the citations to carry the rigor. Saves 19 words.

### 2. Conclusions S3 tightened

**v6:** "System-wide EMS routing protocols can therefore complement STEMI Receiving Center certification and similar facility-level interventions, addressing the between-hospital decision that facility-level work alone cannot resolve." (27 words)

**v7:** "Such routing protocols would complement facility-level interventions like STEMI Receiving Center certification, addressing the between-hospital decision they cannot resolve." (18 words)

Tightens by 9 words while preserving the structural insight (routing addresses what facility-level work cannot).

### 3. Conclusions S4 reframed for honest infrastructure claim

**v6:** "Real-time integration of institutional door-to-balloon performance into EMS dispatch is a candidate next step toward measurable improvements in time-to-reperfusion." (20 words)

**v7:** "No infrastructure currently delivers institutional door-to-balloon performance to EMS dispatch; building such a system, potentially through the National Cardiovascular Data Registry, is a candidate next step toward measurable improvements in time-to-reperfusion." (29 words)

The v6 framing implied the data-delivery infrastructure exists. It does not. v7 acknowledges the gap (no such infrastructure exists today), names the candidate solution (build such a system), and points at the existing data foundation (NCDR) where the institutional D2B data lives. More defensible because it does not assume real-time D2B feeds to EMS dispatch as a given. Adds 9 words but the rhetorical honesty is worth it.

---

## Pre-submission compression options (if AHA portal counts strictly)

Currently ~40 chars over the 2,500-char limit. Options in priority order:

| Where | Compression | Saves |
|---|---|---|
| Methods | Drop "(AHA Heart Disease and Stroke Statistics 2024)" if portal allows separate citation field | ~50 chars |
| Methods | "active acute care hospitals" → "active acute hospitals" | ~5 chars |
| Methods | "all 4,408 active acute care hospitals" → "all 4,408 acute hospitals" | ~10 chars |
| Conclusions | "potentially through the National Cardiovascular Data Registry" → "potentially via NCDR" | ~40 chars |

Combined available compression: ~105 chars. Comfortable buffer once portal-specific limit is verified.

---

## Figure caption (unchanged)

**Figure 1.** Geographic distribution of U.S. PCI competitive catchment zones by county. Each county is shaded by the percentage of its population living in a PCI competitive catchment zone, areas where a second PCI-capable hospital is reachable within 15 additional minutes of drive time beyond the nearest. Deep red counties (>75%) are predominantly metropolitan; pale counties (<25%) are predominantly rural; nine counties (no shading) have no PCI-capable hospital within 90 miles. Albers Equal Area Conic projection.

---

## Anti-drift cross-reference (per claim_calibration.md, v7)

- ✅ "Could meaningfully alter time-to-reperfusion" — substrate-level
- ✅ Background establishes D2B variation as documented premise via simpler citation-anchored language
- ✅ "Default destination is not necessarily fastest" — statement of insufficiency
- ✅ "Such routing protocols would complement..." — collaborative framing, conditional verb
- ✅ "No infrastructure currently delivers..." — acknowledges current gap honestly
- ✅ "Building such a system... is a candidate next step" — names the solution direction without claiming demonstration
- ✅ "Potentially through the National Cardiovascular Data Registry" — points at existing data foundation where institutional D2B data lives
- ❌ NOT claiming the routing optimization *does* save time
- ❌ NOT claiming live D2B infrastructure exists today
- ❌ NOT specifying when or how a real-time NCDR-EMS bridge would be built (correct scope for next-paper / implementation work)
