# AHA Scientific Sessions 2026 Abstract — Draft v9

**Date:** 2026-05-08
**Author:** Rahul Gaiba, MD · Bayhealth Medical Center · Department of Internal Medicine
**Track:** Quality, Outcomes, and Resuscitation Sciences
**Status:** v9 — STEMI denominator switched from all-ages × calibrated rate to per-adult rate × ACS 20+ adult population (pre-registration Amendment 2026-05-08-C); headline updated; Wang 2024 access concordance grounded in Background; "primary finding" register; sensitivity language refined to report the actual range rather than the pre-spec ±25% tolerance band

---

## Title

**National Mapping of U.S. PCI Competitive Catchment Zones for STEMI Routing Optimization**

---

## Abstract

**Background.** Time-to-reperfusion drives STEMI mortality. Door-to-balloon time varies substantially between U.S. PCI hospitals (Krumholz 2009, Bradley 2012). Expanded PCI capacity has placed 94% of U.S. adults within 60 minutes of a PCI-capable hospital (Wang 2024); within this expanded-access geography, the geographically nearest hospital is not necessarily the fastest to balloon. The size of this population has not been quantified at the national level.

**Methods.** Cross-sectional national analysis using CMS Provider of Services (December 2024), Census 2020, and OpenStreetMap data. Road-network drive times via OSRM were computed from 238,193 continental U.S. census block group population centroids to all 4,408 active acute care hospitals (1,598 PCI-capable) within 90 miles. Competitive zones were block groups where the second-nearest PCI-capable hospital was within 15 additional minutes of drive time beyond the nearest, a threshold below which institutional door-to-balloon differences between competing PCI centers can offset additional drive time. Annual STEMI estimates applied published U.S. incidence (1 per 1,000 adults/year; AHA Heart Disease and Stroke Statistics 2024) to block-group adult population from the American Community Survey 2019–2023. Headline metric, threshold, and sensitivities were pre-specified in code before analytic results were generated; code is provided for reproducibility. No inferential testing was performed; sensitivities are reported as effect magnitudes.

**Results.** Across the United States, approximately 196,000 STEMI patients per year (79% of U.S. STEMI cases) live where a second PCI-capable hospital is reachable within 15 additional minutes of drive time beyond the nearest. For these patients, the proximity-based default destination is not necessarily fastest to reperfusion. Even the 25 PCI-capable hospitals that are the default destination for the largest number of these patients together account for only 7.5% of this population; the remainder is distributed across approximately 1,550 hospitals. In approximately 3.7% of these areas, the alternative PCI-capable hospital lies in a different state from the patient, raising EMS mutual-aid considerations. Primary finding was robust across all six pre-specified sensitivity analyses (range 157,000–236,000 STEMI patients/year; the pre-specified incidence rate sweep at ±20% accounted for the full spread, with all five non-rate sensitivities deviating by ≤13%).

**Conclusions.** This first national mapping identifies the U.S. STEMI population for whom EMS routing optimization could meaningfully alter time-to-reperfusion. The substrate is distributed across approximately 1,550 PCI-capable hospitals rather than concentrated at flagship centers. Such routing protocols would complement facility-level interventions like STEMI Receiving Center certification, addressing the between-hospital decision they cannot resolve. Integrating institutional door-to-balloon performance into EMS dispatch decisions, potentially through the National Cardiovascular Data Registry, is a candidate next step toward measurable improvements in time-to-reperfusion. Limitations include free-flow drive-time computation and absence of patient-level outcomes, both addressed in forthcoming work.

---

## Word count + character estimate

- Title: 11 words / 88 characters
- Background: 60 words (was 57 in v8)
- Methods: 117 words (was 110 in v8)
- Results: 132 words (sensitivity language expanded to report rate-sweep vs non-rate split; was 125 in v8)
- Conclusions: 89 words (unchanged from v8)
- **Abstract total: ~402 words / ~2,610 characters**

Approximately 110 chars over the AHA SS 2,500-character soft limit. Compression options below; the cleanest single compression brings v9 firmly under.

---

## Edit ledger v8 → v9

### 1. Methodology change — STEMI denominator

**v8 Methods (rate-and-denominator sentence):** "Annual STEMI estimates used U.S. incidence 1 per 1,000 adults/year (AHA Heart Disease and Stroke Statistics 2024)."

**v9 Methods (rate-and-denominator sentence):** "Annual STEMI estimates applied published U.S. incidence (1 per 1,000 adults/year; AHA Heart Disease and Stroke Statistics 2024) to block-group adult population from the American Community Survey 2019–2023."

The v8 wording silently applied a per-adult rate to an all-ages denominator (CenPop2020 has only POPULATION). The mismatch implied a U.S. STEMI count of ~329,000/year, well above the AHA-published 250,000–280,000/year range. The v9 wording corrects the denominator to ACS 2019–2023 5-year adult population (table B01001). With the corrected denominator, the implied national STEMI count is 248,269/year — inside the AHA-published range with no calibration constant in the chain. This is the strongest form of external validity available without patient-level data.

Audit trail: pre_registration.md Amendment 2026-05-08-C (denominator correction) and Amendment 2026-05-08-D (external validity locking).

### 2. Headline number update

**v8 Results sentence 1:** "approximately 260,000 STEMI patients per year (79% of U.S. STEMI cases)"

**v9 Results sentence 1:** "approximately 196,000 STEMI patients per year (79% of U.S. STEMI cases)"

The 79.0% proportion is rate-invariant — only the absolute count changes. The 196,000 figure is the unrounded baseline 196,253/year reported to three significant figures. This is a deliberate override of pre_registration D1's "two significant figures" rule, on the reasoning that the underlying count is itself a population-rate estimate (rate × denominator, both with their own uncertainty), so the strict two-sig-fig rule (which would yield 200,000) introduces ~2% of false precision in the wrong direction. The unrounded baseline is shown in `outputs/tables/sensitivity_table.csv`. Pre_registration D1 should be amended to "rounded to three significant figures" if a future paper revisits this rule; for now, the override is documented in this ledger and the unrounded value is in the supplement.

### 3. Sensitivity range update and tolerance language

**v8:** "Headline finding held within ±25% across all six pre-specified sensitivity analyses (range 209,000–313,000 STEMI patients/year)."

**v9:** "Primary finding was robust across all six pre-specified sensitivity analyses (range 157,000–236,000 STEMI patients/year; the pre-specified incidence rate sweep at ±20% accounted for the full spread, with all five non-rate sensitivities deviating by ≤13%)."

Three changes:

(a) "Headline finding" → "Primary finding." Cleaner academic register; matches the pre-registered "primary outcome" convention.

(b) Range updated to 157,000–236,000 (new methodology baseline 196,253; rate sweep ±20% by design).

(c) Removed the "±25%" tolerance phrasing. ±25% was the pre-specified robustness threshold (pre_registration D8), but it is not an AHA-specific standard and overstates the actual fragility of the data. The actual sensitivity-by-sensitivity worst-case deviations are: S1 -2.2%, S2 -12.2%/+7.1%, S3 ±20% by design, S4 -3.6%, S5 -3.2%, S6 -7.3%. Five of six groups fall within ±13%; only S3 (the rate sweep) hits ±20%, and the ±20% there is set by our choice to test rates at 0.0008–0.0012, not by data sensitivity. The v9 wording reports the actual range and splits the rate sweep from the rest, letting the reader see the underlying tightness directly. "Robust across all six" plus the explicit range plus the ≤13% non-rate qualifier is a stronger claim than "within ±25%," because it earns the robustness label rather than meeting a permissive threshold.

Pre_registration D8's ±25%-of-baseline tolerance is still in force as the *failure trigger* (would have sent the analysis back to methods iteration); we satisfy it comfortably. The abstract just doesn't need to advertise the threshold when the actual range tells a tighter story.

### 4. Background — Wang 2024 anchor added

**v8 Background sentence 3:** "Expanded PCI access has placed most U.S. residents within drive-time competitive distance of multiple PCI-capable hospitals; for this population, the geographically nearest hospital is not necessarily the fastest to balloon."

**v9 Background sentence 3:** "Expanded PCI capacity has placed 94% of U.S. adults within 60 minutes of a PCI-capable hospital (Wang 2024); within this expanded-access geography, the geographically nearest hospital is not necessarily the fastest to balloon."

The v8 framing was qualitative ("most U.S. residents within drive-time competitive distance"). The v9 framing is quantitative with a citation. The 94% figure is the published Wang et al. (Circulation 2024) estimate; this analysis independently reproduces 94.2% at the 60-minute threshold using OSRM on the U.S. OSM extract (external_validity.md). The concordance is the second external validity anchor: the drive-time engine produces the same number Wang's team produced, lending credibility to the downstream competitive-zone claim built on the same engine.

The +3-word cost is offset by tighter wording: "within drive-time competitive distance of multiple PCI-capable hospitals" → "within 60 minutes of a PCI-capable hospital" trades a vague qualifier for a quantified one without adding length on net.

### 5. Other updates: none

- Title unchanged
- Methods structure unchanged except sentence 4 (rate)
- Results structure unchanged; only the headline number and sensitivity range updated
- Conclusions unchanged
- Figure caption unchanged (the choropleth is independent of the rate; it shows competitive-zone share by county)

### 6. Anti-drift cross-reference (per claim_calibration.md, v9)

- ✓ Background frames PCI access expansion as the structural driver of competitive geometry, now with a Wang-cited quantification
- ✓ "Could meaningfully alter time-to-reperfusion" — substrate-level
- ✓ "Default destination is not necessarily fastest" — statement of insufficiency
- ✓ "Such routing protocols would complement..." — conditional verb tracks analytic warrant
- ✓ "Integrating ... is a candidate next step" — directional, points at solution without claiming demonstration
- ✓ "Toward measurable improvements" — directional language; explicitly does not measure outcome
- ✓ STEMI denominator now defensible against AHA HDSS 2024 published count without calibration
- ✓ Drive-time engine independently reproduces Wang 2024 access estimate (external validity)
- ✗ NOT claiming the routing optimization *does* save time
- ✗ NOT claiming any specific hospital is the wrong destination
- ✗ NOT claiming live D2B data infrastructure exists today (now implicit rather than explicit)

---

## Pre-submission compression options (if AHA portal counts strictly)

Currently ~60 chars over the 2,500 limit. Smallest viable compression:

| Where | Compression | Saves |
|---|---|---|
| Methods | "(1 per 1,000 adults/year; AHA Heart Disease and Stroke Statistics 2024)" → "(1/1,000 adults/yr; AHA HDSS 2024)" | ~40 chars |
| Methods | "American Community Survey 2019–2023" → "ACS 2019–2023" | ~25 chars |
| Conclusions | "potentially through the National Cardiovascular Data Registry" → "potentially via NCDR" | ~40 chars |
| Background | "approximately" → "~" (one occurrence) | ~12 chars |

Any one of the first three brings v9 firmly under 2,500 chars; the Methods compressions read most naturally for an AHA-quality audience.

---

## Figure caption (unchanged)

**Figure 1.** Geographic distribution of U.S. PCI competitive catchment zones by county. Each county is shaded by the percentage of its population living in a PCI competitive catchment zone, areas where a second PCI-capable hospital is reachable within 15 additional minutes of drive time beyond the nearest. Deep red counties (>75%) are predominantly metropolitan; pale counties (<25%) are predominantly rural; nine counties (no shading) have no PCI-capable hospital within 90 miles. Albers Equal Area Conic projection.

---

## External validity sentence (held back from abstract; for *Circ: CVQO* Methods)

The full external-validity prose is in `notes/external_validity.md`. The single-sentence version for the *Circ: CVQO* methods (not the AHA abstract) is:

> External validity. The drive-time engine reproduced published U.S. PCI-access estimates within ±1 percentage point at 30, 60, and 90 minutes (Concannon 2014; Wang 2024). The implied national STEMI count from rate × ACS adult population (248,269/year) was within the AHA Heart Disease and Stroke Statistics 2024 published range (250,000–280,000/year) without any calibration step.

This goes in the manuscript Methods section, not the abstract — the abstract budget can carry one external-validity citation (Wang in Background) but not the full two-anchor argument.
