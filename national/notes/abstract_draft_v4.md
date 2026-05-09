# AHA Scientific Sessions 2026 Abstract — Draft v4

**Date:** 2026-05-08
**Author:** Rahul Gaiba, MD · Bayhealth Medical Center · Department of Internal Medicine
**Track:** Quality, Outcomes, and Resuscitation Sciences
**Status:** v4 — Conclusions reframed as conditional ("can complement") with live-D2B integration named as candidate next step. No em dashes throughout.

---

## Title

**National Mapping of U.S. PCI Competitive Catchment Zones for STEMI Routing Optimization**

---

## Abstract

**Background.** Time-to-reperfusion drives STEMI mortality. Current EMS protocols route patients to the geographically nearest hospital, but the nearest is not necessarily fastest to balloon when multiple PCI-capable centers are reachable, given documented inter-center door-to-balloon variation (Krumholz 2009, Bradley 2012). No prior national-scale analysis has identified the U.S. STEMI population for whom this routing decision is consequential.

**Methods.** Cross-sectional national geographic analysis using CMS Provider of Services (December 2024), Census 2020, and OpenStreetMap data. Road-network drive times via OSRM were computed from each of 238,193 continental U.S. census block group population centroids to all 4,408 active acute care hospitals (1,598 PCI-capable) within 90 miles. A competitive zone was defined as a block group where the second-nearest PCI-capable hospital is reachable within 15 additional minutes of drive time beyond the nearest, the threshold below which institutional door-to-balloon differences between competing PCI centers (typically 15–35 minutes) can offset additional drive time. Annual STEMI estimates used U.S. incidence 1 per 1,000 adults/year (AHA Heart Disease and Stroke Statistics 2024). Headline metric, threshold, and sensitivities were pre-specified in committed code before analytic results were generated; code is provided for reproducibility. No inferential statistical testing was performed; sensitivities are reported as effect-magnitude variations.

**Results.** Across the United States, approximately 260,000 STEMI patients per year (79% of U.S. STEMI cases) live where a second PCI-capable hospital is reachable within 15 additional minutes of drive time beyond the nearest. For these patients, the proximity-based default destination is not necessarily fastest to reperfusion. Even the 25 PCI-capable hospitals that are the default destination for the largest number of these patients together account for only 7.5% of this population; the remainder is distributed across approximately 1,550 hospitals. In approximately 3.7% of these areas, the alternative PCI-capable hospital lies in a different state from the patient, raising EMS mutual-aid considerations. Headline finding held within ±25% across all six pre-specified sensitivity analyses (range 209,000–313,000 STEMI patients/year).

**Conclusions.** This first national mapping identifies the U.S. STEMI population for whom EMS routing optimization could meaningfully alter time-to-reperfusion. The substrate is distributed across approximately 1,550 PCI-capable hospitals rather than concentrated at flagship centers. System-wide EMS routing protocols can therefore complement STEMI Receiving Center certification and similar facility-level interventions, addressing the between-hospital decision that facility-level work alone cannot resolve. Real-time integration of institutional door-to-balloon performance into EMS dispatch is a candidate next step toward measurable improvements in time-to-reperfusion. Limitations include free-flow drive-time computation and absence of patient-level outcomes, both addressed in forthcoming work.

---

## Word count + character estimate

- Title: 11 words / 88 characters
- Background: 52 words
- Methods: 116 words
- Results: 125 words
- Conclusions: 94 words
- **Abstract total: ~387 words / ~2,470 characters**

AHA SS limit: 2,500 characters. Headroom: ~30 characters. Tight. Pre-submission compression possible if portal counts strictly.

---

## Edit ledger v3 → v4

**Conclusions paragraph fully rewritten.** Four substantive shifts:

1. **"Complement" → "can complement"** — conditional, not assertive. We have not demonstrated that system-wide routing protocols *do* complement facility-level work; we have shown the geometric substrate where they *could*. The conditional verb tracks the analytic warrant.

2. **Live D2B integration named as the candidate next step** — the technologist-audience hint at what should be built next. Real-time institutional door-to-balloon data integrated into EMS dispatch decisions is the operational lever that converts the geographic substrate into measurable improvements. Implicitly references the Paper 2 and Paper 3 research program without overcommitting Paper 1's claim.

3. **No em dashes anywhere in the abstract.** Replaced em dashes with commas, semicolons, or sentence breaks throughout. The original v3 used em dashes in Conclusions and Methods. Both removed.

4. **"Geographic substrate ... measurable improvements in time-to-reperfusion"** — closes the loop from substrate identification (Paper 1) to outcome measurement (Paper 2/3) without claiming we have measured the outcome ourselves.

The collaborative-not-substitute framing for facility-level work is preserved from v3 and tightened.

---

## Figure caption (unchanged from v2)

**Figure 1.** Geographic distribution of U.S. PCI competitive catchment zones by county. Each county is shaded by the percentage of its population living in a PCI competitive catchment zone, areas where a second PCI-capable hospital is reachable within 15 additional minutes of drive time beyond the nearest. Deep red counties (>75%) are predominantly metropolitan; pale counties (<25%) are predominantly rural; nine counties (no shading) have no PCI-capable hospital within 90 miles. Albers Equal Area Conic projection.

(Note: figure caption em dash removed for v4 consistency.)

---

## Pre-submission verification checklist

- [ ] Krumholz 2009 — *Circulation* 2009;120:1851–1858 (verify volume/page numbers)
- [ ] Bradley 2012 — *Ann Intern Med* 2012;156:618–626
- [ ] AHA Heart Disease and Stroke Statistics — confirm year (2024 or 2025 update)
- [ ] Title format compliance with AHA SS submission portal
- [ ] Figure dimensions (300 DPI; ~3.5×5 in for oral, 4×6 in for poster)
- [ ] Co-author / cardiology-chief review pass
- [ ] Final character count against AHA SS portal limit (2,500 char typical)

---

## Anti-drift cross-reference (per claim_calibration.md, updated for v4)

- ✅ "Could meaningfully alter time-to-reperfusion" — substrate-level, hypothesis-pointing
- ✅ "Default destination is not necessarily fastest to reperfusion" — statement of insufficiency
- ✅ "Can complement" — conditional, not asserted
- ✅ "Candidate next step" — names a future direction without claiming demonstration
- ✅ "Toward measurable improvements" — directional, not quantified
- ❌ NOT claiming that routing optimization *does* complement (would require demonstration)
- ❌ NOT claiming any specific minutes saved per patient
- ❌ NOT claiming any specific hospital is the wrong destination
- ❌ NOT critiquing existing Mission: Lifeline strategy
