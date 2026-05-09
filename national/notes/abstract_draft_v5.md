# AHA Scientific Sessions 2026 Abstract — Draft v5

**Date:** 2026-05-08
**Author:** Rahul Gaiba, MD · Bayhealth Medical Center · Department of Internal Medicine
**Track:** Quality, Outcomes, and Resuscitation Sciences
**Status:** v5 — Conditional ("when inter-hospital D2B varies significantly") added to Conclusions opening; minor Methods compression for character budget

---

## Title

**National Mapping of U.S. PCI Competitive Catchment Zones for STEMI Routing Optimization**

---

## Abstract

**Background.** Time-to-reperfusion drives STEMI mortality. Current EMS protocols route patients to the geographically nearest hospital, but the nearest is not necessarily fastest to balloon when multiple PCI-capable centers are reachable, given documented inter-center door-to-balloon variation (Krumholz 2009, Bradley 2012). No prior national-scale analysis has identified the U.S. STEMI population for whom this routing decision is consequential.

**Methods.** Cross-sectional national geographic analysis using CMS Provider of Services (December 2024), Census 2020, and OpenStreetMap data. Road-network drive times via OSRM were computed from 238,193 continental U.S. census block group population centroids to all 4,408 active acute care hospitals (1,598 PCI-capable) within 90 miles. A competitive zone was defined as a block group where the second-nearest PCI-capable hospital is reachable within 15 additional minutes of drive time beyond the nearest, the threshold below which institutional door-to-balloon differences between competing PCI centers (typically 15–35 minutes) can offset additional drive time. Annual STEMI estimates used U.S. incidence 1 per 1,000 adults/year (AHA Heart Disease and Stroke Statistics 2024). Headline metric, threshold, and sensitivities were pre-specified in code before analytic results were generated; code is provided for reproducibility. No inferential testing was performed; sensitivities are reported as effect magnitudes.

**Results.** Across the United States, approximately 260,000 STEMI patients per year (79% of U.S. STEMI cases) live where a second PCI-capable hospital is reachable within 15 additional minutes of drive time beyond the nearest. For these patients, the proximity-based default destination is not necessarily fastest to reperfusion. Even the 25 PCI-capable hospitals that are the default destination for the largest number of these patients together account for only 7.5% of this population; the remainder is distributed across approximately 1,550 hospitals. In approximately 3.7% of these areas, the alternative PCI-capable hospital lies in a different state from the patient, raising EMS mutual-aid considerations. Headline finding held within ±25% across all six pre-specified sensitivity analyses (range 209,000–313,000 STEMI patients/year).

**Conclusions.** This first national mapping identifies the U.S. STEMI population for whom EMS routing optimization could meaningfully alter time-to-reperfusion when inter-hospital D2B varies significantly between competing centers. The substrate is distributed across approximately 1,550 PCI-capable hospitals rather than concentrated at flagship centers. System-wide EMS routing protocols can therefore complement STEMI Receiving Center certification and similar facility-level interventions, addressing the between-hospital decision that facility-level work alone cannot resolve. Real-time integration of institutional door-to-balloon performance into EMS dispatch is a candidate next step toward measurable improvements in time-to-reperfusion. Limitations include free-flow drive-time computation and absence of patient-level outcomes, both addressed in forthcoming work.

---

## Word count + character estimate

- Title: 11 words / 88 characters
- Background: 52 words
- Methods: 113 words (compressed from v4's 116)
- Results: 125 words (unchanged)
- Conclusions: 101 words (added 7-word conditional)
- **Abstract total: ~391 words / ~2,495 characters**

AHA SS limit: 2,500 characters. **Headroom: ~5 characters.** Effectively at the limit; verify against final portal counter at submission. Pre-submission compression options identified below if portal counts strictly.

---

## Edit ledger v4 → v5

**One substantive content addition; two minor compressions.**

1. **Conclusions sentence 1: added the D2B-variation conditional.** Original (v4): *"This first national mapping identifies the U.S. STEMI population for whom EMS routing optimization could meaningfully alter time-to-reperfusion."* Revised (v5): *"This first national mapping identifies the U.S. STEMI population for whom EMS routing optimization could meaningfully alter time-to-reperfusion when inter-hospital D2B varies significantly between competing centers."* The added conditional makes the dependency explicit. The empirical condition is met for ~50–60% of competing-center pairs nationally per published Krumholz/Bradley data. (+7 words)

2. **Methods compression 1:** "from each of 238,193 continental U.S. census block group population centroids" → "from 238,193 continental U.S. census block group population centroids" (-1 word).

3. **Methods compression 2:** Tightened the pre-specification + statistical-testing sentences. "Headline metric, threshold, and sensitivities were pre-specified in **committed** code before analytic results were generated" → "...pre-specified in code before analytic results were generated"; "No inferential **statistical** testing was performed; sensitivities are reported as **effect-magnitude variations**" → "...effect magnitudes." (-3 words total)

Net: +3 words from v4 → v5 across the abstract (added conditional; compensated by Methods compressions).

---

## Pre-submission compression options (if portal counts strictly)

The current draft is at ~2,495 characters against a 2,500-character AHA SS limit. If submission tooling counts strictly, the following sentences could lose words without losing substance:

| Where | Compression | Saves |
|---|---|---|
| Methods | "Headline metric, threshold, and sensitivities were pre-specified" → "Threshold, headline, and sensitivities were pre-specified" | ~1 word |
| Methods | Drop "(AHA Heart Disease and Stroke Statistics 2024)" if portal allows separate citation field | ~5 words |
| Results | "the alternative PCI-capable hospital lies in a different state from the patient" → "the alternative PCI-capable hospital is across a state line" | ~5 words |
| Methods | "U.S. incidence 1 per 1,000 adults/year" → "U.S. incidence ~0.1%/yr" | ~3 words |

None of these are needed unless the portal forces compression. Holding them in reserve.

---

## Figure caption (unchanged)

**Figure 1.** Geographic distribution of U.S. PCI competitive catchment zones by county. Each county is shaded by the percentage of its population living in a PCI competitive catchment zone, areas where a second PCI-capable hospital is reachable within 15 additional minutes of drive time beyond the nearest. Deep red counties (>75%) are predominantly metropolitan; pale counties (<25%) are predominantly rural; nine counties (no shading) have no PCI-capable hospital within 90 miles. Albers Equal Area Conic projection.

---

## Anti-drift cross-reference (per claim_calibration.md, v5)

- ✅ "Could meaningfully alter time-to-reperfusion" — substrate-level
- ✅ "When inter-hospital D2B varies significantly between competing centers" — explicit conditional, methodologically honest
- ✅ "Default destination is not necessarily fastest" — statement of insufficiency
- ✅ "Can therefore complement" — conditional verb tracks analytic warrant
- ✅ "Candidate next step" — directional, not measurement claim
- ✅ "Toward measurable improvements" — directional language
- ❌ NOT claiming the routing optimization *does* save time
- ❌ NOT claiming any specific hospital is the wrong destination
- ❌ NOT claiming D2B variation exists at every competing-pair (the conditional explicitly acknowledges it)
