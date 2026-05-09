# AHA Scientific Sessions 2026 Abstract — Draft v3

**Date:** 2026-05-08
**Author:** Rahul Gaiba, MD · Bayhealth Medical Center · Department of Internal Medicine
**Track:** Quality, Outcomes, and Resuscitation Sciences
**Status:** v3 — Conclusions reframed as complementary-to (not substitute-for) facility-level intervention

---

## Title

**National Mapping of U.S. PCI Competitive Catchment Zones for STEMI Routing Optimization**

*(11 words; ~88 characters)*

---

## Abstract (~370 words, structured)

**Background.** Time-to-reperfusion drives STEMI mortality. Current EMS protocols route patients to the geographically nearest hospital, but the nearest is not necessarily fastest to balloon when multiple PCI-capable centers are reachable, given documented inter-center door-to-balloon variation (Krumholz 2009, Bradley 2012). No prior national-scale analysis has identified the U.S. STEMI population for whom this routing decision is consequential.

**Methods.** Cross-sectional national geographic analysis using CMS Provider of Services (December 2024), Census 2020, and OpenStreetMap data. Road-network drive times via OSRM were computed from each of 238,193 continental U.S. census block group population centroids to all 4,408 active acute care hospitals (1,598 PCI-capable) within 90 miles. A competitive zone was defined as a block group where the second-nearest PCI-capable hospital is reachable within 15 additional minutes of drive time beyond the nearest — the threshold below which institutional door-to-balloon differences between competing PCI centers (typically 15–35 minutes) can offset additional drive time. Annual STEMI estimates used U.S. incidence 1 per 1,000 adults/year (AHA Heart Disease and Stroke Statistics 2024). Headline metric, threshold, and sensitivities were pre-specified in committed code before analytic results were generated; code is provided for reproducibility. No inferential statistical testing was performed; sensitivities are reported as effect-magnitude variations.

**Results.** Across the United States, approximately 260,000 STEMI patients per year (79% of U.S. STEMI cases) live where a second PCI-capable hospital is reachable within 15 additional minutes of drive time beyond the nearest. For these patients, the proximity-based default destination is not necessarily fastest to reperfusion. Even the 25 PCI-capable hospitals that are the default destination for the largest number of these patients together account for only 7.5% of this population; the remainder is distributed across approximately 1,550 hospitals. In approximately 3.7% of these areas, the alternative PCI-capable hospital lies in a different state from the patient, raising EMS mutual-aid considerations. Headline finding held within ±25% across all six pre-specified sensitivity analyses (range 209,000–313,000 STEMI patients/year).

**Conclusions.** This first national mapping identifies the U.S. STEMI population for whom EMS routing optimization could meaningfully alter time-to-reperfusion. The distributed substrate — across approximately 1,550 PCI-capable hospitals rather than concentrated at flagship centers — indicates that system-wide EMS routing protocols complement existing facility-level interventions (such as STEMI Receiving Center certification) by addressing the between-hospital decision that facility-level work alone cannot resolve. This is a natural next step in the regionalization framework that increased U.S. PCI access — operating between hospitals rather than within them. Limitations include free-flow drive-time computation (not real-time traffic) and absence of patient-level outcomes, both addressed in forthcoming work.

---

## Word count + character estimate

- Title: 11 words / 88 characters
- Background: 52 words
- Methods: 110 words
- Results: 125 words
- Conclusions: 84 words
- **Abstract total: ~371 words / ~2,380 characters**

AHA SS limit: 2,500 characters. **Headroom: ~120 characters.** Tight but workable; final pre-submission compression can recover characters if needed.

---

## Edit ledger v2 → v3

**One key change in Conclusions (per editorial review):**

v2 framing was *"system-wide EMS protocol design — not facility-level intervention — as the appropriate target for Mission: Lifeline expansion."* The "not facility-level" framing reads as oppositional and risks alienating reviewers and Mission: Lifeline stakeholders who have invested heavily in STEMI Receiving Center certification (a facility-level lever).

v3 reframes the relationship explicitly:
- **Complementary, not substitute** — routing protocols complement facility-level work
- **Addresses a gap** — the between-hospital decision that facility-level interventions alone cannot resolve
- **Natural next step** — builds on (rather than replaces) the regionalization movement that increased PCI access
- **Operates between hospitals rather than within them** — captures the structural difference in intervention type

This framing is more accurate to what the analysis actually shows (the substrate exists between hospitals) and politically aligned with Mission: Lifeline's existing strategic direction.

---

## Figure caption (unchanged from v2)

**Figure 1.** Geographic distribution of U.S. PCI competitive catchment zones by county. Each county is shaded by the percentage of its population living in a PCI competitive catchment zone — areas where a second PCI-capable hospital is reachable within 15 additional minutes of drive time beyond the nearest. Deep red counties (>75%) are predominantly metropolitan; pale counties (<25%) are predominantly rural; nine counties (no shading) have no PCI-capable hospital within 90 miles. Albers Equal Area Conic projection.

---

## Pre-submission verification checklist (unchanged)

- [ ] Krumholz 2009 — *Circulation* 2009;120:1851–1858
- [ ] Bradley 2012 — *Ann Intern Med* 2012;156:618–626
- [ ] AHA Heart Disease and Stroke Statistics — confirm year (2024 or 2025)
- [ ] Title format compliance
- [ ] Figure dimensions for AHA SS submission
- [ ] Co-author / cardiology-chief review pass

---

## Anti-drift cross-reference (per claim_calibration.md)

- ✅ "Could meaningfully alter time-to-reperfusion" — substrate-level, hypothesis-pointing
- ✅ "Default destination is not necessarily fastest" — statement of insufficiency, not measurement
- ✅ "Complement existing facility-level interventions" — collaborative framing, not oppositional
- ✅ "Address the between-hospital decision facility-level alone cannot resolve" — structural claim, not value judgment
- ✅ "Natural next step in regionalization framework" — positions work in lineage, not as critique
- ❌ NOT claiming any specific routing change saves N minutes
- ❌ NOT claiming any hospital is currently receiving the wrong patients
- ❌ NOT critiquing existing Mission: Lifeline strategy
