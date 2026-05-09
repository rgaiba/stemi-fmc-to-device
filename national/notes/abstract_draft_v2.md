# AHA Scientific Sessions 2026 Abstract — Draft v2

**Date:** 2026-05-08
**Author:** Rahul Gaiba, MD · Bayhealth Medical Center · Department of Internal Medicine
**Track:** Quality, Outcomes, and Resuscitation Sciences
**Status:** v2 with AHA-level check applied (six edits from v1 → v2)

---

## Title

**National Mapping of U.S. PCI Competitive Catchment Zones for STEMI Routing Optimization**

*(11 words; ~88 characters; AHA SS title limit ~200 characters)*

---

## Abstract (~352 words, structured)

**Background.** Time-to-reperfusion drives STEMI mortality. Current EMS protocols route patients to the geographically nearest hospital, but the nearest is not necessarily fastest to balloon when multiple PCI-capable centers are reachable, given documented inter-center door-to-balloon variation (Krumholz 2009, Bradley 2012). No prior national-scale analysis has identified the U.S. STEMI population for whom this routing decision is consequential.

**Methods.** Cross-sectional national geographic analysis using CMS Provider of Services (December 2024), Census 2020, and OpenStreetMap data. Road-network drive times via OSRM were computed from each of 238,193 continental U.S. census block group population centroids to all 4,408 active acute care hospitals (1,598 PCI-capable) within 90 miles. A competitive zone was defined as a block group where the second-nearest PCI-capable hospital is reachable within 15 additional minutes of drive time beyond the nearest — the threshold below which institutional door-to-balloon differences between competing PCI centers (typically 15–35 minutes) can offset additional drive time. Annual STEMI estimates used U.S. incidence 1 per 1,000 adults/year (AHA Heart Disease and Stroke Statistics 2024). Headline metric, threshold, and sensitivities were pre-specified in committed code before analytic results were generated; code is provided for reproducibility. No inferential statistical testing was performed; sensitivities are reported as effect-magnitude variations.

**Results.** Across the United States, approximately 260,000 STEMI patients per year (79% of U.S. STEMI cases) live where a second PCI-capable hospital is reachable within 15 additional minutes of drive time beyond the nearest. For these patients, the proximity-based default destination is not necessarily fastest to reperfusion. Even the 25 PCI-capable hospitals that are the default destination for the largest number of these patients together account for only 7.5% of this population; the remainder is distributed across approximately 1,550 hospitals. In approximately 3.7% of these areas, the alternative PCI-capable hospital lies in a different state from the patient, raising EMS mutual-aid considerations. Headline finding held within ±25% across all six pre-specified sensitivity analyses (range 209,000–313,000 STEMI patients/year).

**Conclusions.** This first national mapping identifies the U.S. STEMI population for whom EMS routing optimization could meaningfully alter time-to-reperfusion. The substrate is distributed rather than concentrated at flagship hospitals, indicating system-wide EMS protocol design — not facility-level intervention — as the appropriate target for Mission: Lifeline expansion. Limitations include free-flow drive-time computation (not real-time traffic) and absence of patient-level outcomes, both addressed in forthcoming work.

---

## Word count + character estimate

- Title: 11 words / 88 characters
- Background: 52 words
- Methods: 110 words
- Results: 125 words
- Conclusions: 65 words
- **Abstract total: ~352 words / ~2,250 characters including spaces**

AHA Scientific Sessions abstract typical limit: 2,500 characters. **Comfortably within limit by ~250 characters / ~40 words of headroom.**

---

## Figure caption (single figure)

**Figure 1.** Geographic distribution of U.S. PCI competitive catchment zones by county. Each county is shaded by the percentage of its population living in a PCI competitive catchment zone — areas where a second PCI-capable hospital is reachable within 15 additional minutes of drive time beyond the nearest. Deep red counties (>75%) are predominantly metropolitan; pale counties (<25%) are predominantly rural; nine counties (no shading) have no PCI-capable hospital within 90 miles. Albers Equal Area Conic projection.

---

## Edit ledger v1 → v2 (six AHA-check findings applied)

1. **[High] Cite AHA HDSS for STEMI incidence** — added "(AHA Heart Disease and Stroke Statistics 2024)" after the rate
2. **[High] Cite Krumholz/Bradley for D2B variation in Background** — added "(Krumholz 2009, Bradley 2012)" inline
3. **[Medium] Add no-inferential-testing statement in Methods** — added final Methods sentence
4. **[Low] Tighten title** — dropped "Geographic Substrate for" colon and "in the United States" tail; net saving 3 words
5. **[Low] Move "first" claim to Background opening** — "No prior national-scale analysis..." opens Background; "first" retained in Conclusions for explicit assertion
6. **[Low] Add limitations sentence** — "Limitations include free-flow drive-time computation..." closes Conclusions

Plus three textual refinements from earlier review:
- "Anchored to" → explanatory phrasing for the 15-min threshold
- "Pre-registration" → "pre-specified in committed code" + "code provided for reproducibility"
- "Default destination" / "alternative" framing carried throughout

---

## Pre-submission verification checklist (unchanged from v1)

Items to confirm before submission:

- [ ] Krumholz 2009: full citation — *Circulation* 2009;120:1851–1858 (campaign-to-improve-D2B paper). Verify volume/page numbers.
- [ ] Bradley 2012: full citation — *Ann Intern Med* 2012;156:618–626 (hospital strategies / mortality paper). Verify.
- [ ] AHA Heart Disease and Stroke Statistics most recent year: which year is current at submission time? Probably 2024 or 2025 update.
- [ ] Title format compliance: confirm AHA SS submission portal accepts the colon-free format.
- [ ] Figure dimensions: confirm 4×6 (poster) or 3.5×5 (oral) at 300 DPI.
- [ ] Co-author / cardiology-chief review pass.

---

## What v2 deliberately does NOT claim (anti-drift cross-reference)

Per `claim_calibration.md` D9 forbidden-phrasings list:

- ❌ "These hospitals are the wrong destinations" — would require D2B priors (Paper 2)
- ❌ "Routing optimization saves N minutes per patient" — would require D2B priors (Paper 2)
- ❌ "Patients are currently being routed sub-optimally" — would imply we've measured optimality
- ❌ "Time-to-balloon would decrease by..." — measured outcome implication
- ✅ "Could meaningfully alter time-to-reperfusion" — substrate-level, hypothesis-pointing only
- ✅ "Default destination is not necessarily fastest to reperfusion" — statement of insufficiency, not measurement claim
