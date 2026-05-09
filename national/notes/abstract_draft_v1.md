# AHA Scientific Sessions 2026 Abstract — Draft v1

**Date:** 2026-05-08
**Author:** Rahul Gaiba, MD · Bayhealth Medical Center · Department of Internal Medicine
**Track:** Quality, Outcomes, and Resuscitation Sciences
**Status:** First draft for editorial review

---

## Title

National Mapping of PCI Competitive Catchment Zones: Geographic Substrate for STEMI Routing Optimization in the United States

*(14 words; AHA SS title limit typically 200 characters)*

---

## Abstract (~280 words, structured)

**Background.** Time-to-reperfusion drives STEMI mortality. Current EMS protocols route patients to the geographically nearest hospital, but the nearest is not necessarily fastest to balloon when multiple PCI-capable centers are reachable. The U.S. population for whom this routing decision is consequential has not been mapped at the national level.

**Methods.** Cross-sectional national geographic analysis using CMS Provider of Services (December 2024), Census 2020, and OpenStreetMap data. Road-network drive times via OSRM were computed from each of 238,193 continental U.S. census block group population centroids to all 4,408 active acute care hospitals (1,598 PCI-capable) within 90 miles. A competitive zone was defined as a block group where the second-nearest PCI-capable hospital is reachable within 15 additional minutes of drive time beyond the nearest — anchored to published 15–35 minute institutional door-to-balloon differentials. Annual STEMI estimates used U.S. incidence 1 per 1,000 adults/year. Pre-registration of headline metric, threshold, and sensitivity analyses preceded analytic results.

**Results.** Across the United States, approximately 260,000 STEMI patients per year (79% of U.S. STEMI cases) live where a second PCI-capable hospital is reachable within 15 additional minutes of drive time beyond the nearest. For these patients, the proximity-based default destination is not necessarily fastest to reperfusion. Even the 25 PCI-capable hospitals that are the default destination for the largest number of these patients together account for only 7.5% of this population; the remainder is distributed across approximately 1,550 hospitals. In approximately 3.7% of these areas, the alternative PCI-capable hospital lies in a different state from the patient, raising EMS mutual-aid considerations. Headline finding held within ±25% across all six pre-registered sensitivity analyses (range 209,000–313,000 STEMI patients/year).

**Conclusions.** This first national mapping identifies the U.S. STEMI population for whom EMS routing optimization could meaningfully alter time-to-reperfusion. The geographic substrate is distributed rather than concentrated at flagship hospitals, indicating system-wide EMS protocol design — not facility-level intervention — as the appropriate target for Mission: Lifeline expansion.

*(approximately 280 words)*

---

## Figure caption (single figure)

**Figure 1.** Geographic distribution of U.S. PCI competitive catchment zones by county. Each county is shaded by the percentage of its population living in a PCI competitive catchment zone — areas where a second PCI-capable hospital is reachable within 15 additional minutes of drive time beyond the nearest. Deep red counties (>75%) are predominantly metropolitan; pale counties (<25%) are predominantly rural; nine counties (no shading) have no PCI-capable hospital within 90 miles. Albers Equal Area Conic projection.

---

## Word count breakdown

- Title: 14 words
- Background: 41 words
- Methods: 90 words
- Results: 130 words
- Conclusions: 35 words
- **Abstract total: ~296 words**
- Figure caption: 67 words

AHA Scientific Sessions abstract limits are typically 2,500 characters including spaces. Current draft: ~1,950 characters in the abstract body. Comfortably within limit.

---

## Editorial notes

### What this draft does well

- Headline number ("260,000 STEMI patients/year, 79% of U.S. STEMI") leads Results, immediately graspable for clinicians
- "Default destination" / "alternative" pairing introduced in headline; carries through subsequent sentences without re-explanation
- Top-25 = 7.5% finding directly motivates the Conclusion's "system-wide protocol design" recommendation
- Pre-registration mentioned in Methods + robustness shown in Results — methodological-rigor signals visible to reviewers
- Cross-state caveat acknowledges the operational ceiling without overweighting it (single sentence, ~25 words)
- Conclusions stay at the medium-claim level — "could meaningfully alter time-to-reperfusion" is hypothesis-pointing, not measurement-claiming

### What's still to verify before submission

- 15-35 minute institutional D2B differential citation: confirm with Krumholz 2009 + Bradley 2012 page numbers
- U.S. STEMI incidence 1 per 1,000 adults/year: confirm with most recent AHA Heart Disease and Stroke Statistics
- Mission: Lifeline framing in Conclusions: confirm the language doesn't conflict with current ACC/AHA position statements
- Title: AHA Sessions sometimes prefers "and" over colons; check format requirements at submission portal
- Figure SVG render: confirm legibility at AHA's required dimensions (typically 4×6 in for poster, 3.5×5 in for oral)

### What this draft does NOT claim (per claim_calibration.md anti-drift list)

- Does not claim measured outcomes (ΔS2B reduction in minutes)
- Does not claim a specific hospital is the optimal destination for any specific population
- Does not claim routing optimization is feasible — only that the substrate exists where it could be
- Does not extend beyond the descope (Paper 1 = drive-time geometry only)

### Co-author / mentor review checklist

When sending to your cardiology chief / co-authors:

1. Does the headline number feel right against their clinical experience? (Sanity check: 79% of U.S. STEMI in zones-where-routing-matters)
2. Is the "default destination" / "alternative" framing accessible to the AHA audience?
3. Is the Conclusions' Mission: Lifeline expansion claim acceptable? (Optional: soften to "EMS-system-level protocol design as a target for STEMI care quality improvement")
4. Any single phrase you'd cut or rephrase for the cardiology audience?
5. Title preferences — keep current or rework?

---

## Provenance and reproducibility statement

For the manuscript version (CVQO submission, not the abstract):

> "Code and data preparation scripts are available at https://github.com/rgaiba/stemi-fmc-to-device. Source files (CMS Provider of Services file, Census 2020 CenPop, U.S. OpenStreetMap extract via Geofabrik dated May 2026, Census Gazetteer 2020 ZCTA file) are listed in the project MANIFEST with full URLs, accessed dates, and SHA256 checksums of derived analysis-ready files. The analysis is fully reproducible from public sources following the recipe in REPRODUCIBILITY.md."
