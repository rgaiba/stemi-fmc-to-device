# AHA Scientific Sessions 2026 Abstract — Draft v10 (FINAL)

**Date:** 2026-05-09
**Author:** Rahul Gaiba, MD · Bayhealth Medical Center · Department of Internal Medicine
**Track:** Quality, Outcomes, and Resuscitation Sciences
**Status:** v10 FINAL — supersedes v9. Substantial register and economy revision: conventional academic-abstract voice, past-tense Results, citations moved out of inline prose, Methods and Conclusions trimmed for length and tone. Title pivots from "Competitive Catchment Zones" to "Competitive Transfer Zones" (action-oriented; names the routing decision rather than the geographic capture area).

---

## Title

**National Mapping of U.S. PCI Competitive Transfer Zones for STEMI Routing Optimization**

---

## Abstract

**Background.** Time-to-reperfusion is a key determinant of STEMI outcomes. Although most U.S. adults now live within 60 minutes of a PCI-capable hospital, the geographically nearest PCI center may not provide the shortest total time to reperfusion because door-to-balloon performance varies across hospitals. The size and national distribution of the population potentially affected by this routing tradeoff have not been well quantified.

**Methods.** We performed a cross-sectional national analysis using CMS Provider of Services (December 2024), Census 2020, ACS 2019–2023 adult population estimates, and OpenStreetMap road-network data. Drive times were estimated from 238,193 continental U.S. census block-group population centroids to 4,408 active acute care hospitals, including 1,598 PCI-capable hospitals, within 90 miles. We defined competitive zones as block groups in which a second PCI-capable hospital was reachable within 15 additional minutes of the nearest PCI-capable hospital. Annual STEMI case counts were estimated by applying a published incidence rate to the adult population. The primary metric and sensitivity analyses were prespecified.

**Results.** Approximately 196,000 STEMI patients per year, representing 79% of estimated U.S. STEMI cases, lived in areas where a second PCI-capable hospital was reachable within 15 additional minutes of the nearest PCI hospital. This population was distributed across approximately 1,550 hospitals; the 25 hospitals serving the largest such populations accounted for 7.5% of the total. In 3.7% of these areas, the alternative PCI-capable hospital was in a different state. Findings were robust in prespecified sensitivity analyses, with estimates ranging from 157,000 to 236,000 patients annually.

**Conclusions.** A large U.S. STEMI population lives in areas where more than one PCI-capable hospital is reachable with only a modest difference in drive time. These findings define a national substrate for EMS routing strategies that incorporate both transport time and hospital-level reperfusion performance. Future work should evaluate observed traffic conditions, door-to-balloon times, and patient-level outcomes.

---

## Word count + character estimate

- Title: 12 words / 92 characters
- Background: 75 words
- Methods: 110 words
- Results: 88 words
- Conclusions: 57 words
- **Abstract total: ~330 words / ~2,180 characters**

Comfortably under the AHA SS 2,500-character soft limit (~320 chars headroom). No compression needed.

---

## Edit ledger v9 → v10

The v9 abstract was methodologically dense — every claim explicitly anchored, citations inline, sensitivity analysis described in detail. That style fits an audit-trail document; it was not the most conventional academic-abstract register. v10 retains every numerical claim and the full epistemic conservatism but presents them in cleaner abstract prose. No findings change.

### Title

| | |
|---|---|
| v9 | National Mapping of U.S. PCI Competitive **Catchment** Zones for STEMI Routing Optimization |
| v10 | National Mapping of U.S. PCI Competitive **Transfer** Zones for STEMI Routing Optimization |

"Catchment" describes the geographic capture area passively (which population a hospital draws from). "Transfer" names the operative decision (where EMS transports the patient). The abstract is fundamentally about a routing decision, so the noun should signal the decision, not the geography. "Transfer zones" is also consistent with Mission: Lifeline and STEMI Systems-of-Care literature where "transfer" denotes the destination decision.

### Background

Three structural changes:

1. **"Time-to-reperfusion drives STEMI mortality"** → "Time-to-reperfusion is a key determinant of STEMI outcomes." Softer, more conventional. "Outcomes" is broader than mortality and includes the surrogate (TIMI flow, ejection fraction, infarct size) and process measures the field cares about; doesn't overclaim mortality specifically.
2. **Inline citations dropped** (Krumholz 2009, Bradley 2012, Wang 2024). Conventional academic-abstract style does not cite authors inline; the supporting citations live in the submission portal's references field if available, or in the manuscript Methods. The Wang 2024 number (94% within 60 min) becomes implicit: "most U.S. adults now live within 60 minutes of a PCI-capable hospital."
3. **"The size of this population has not been quantified at the national level"** → "The size and national distribution of the population potentially affected by this routing tradeoff have not been well quantified." Adds *distribution* as a second axis (which is what the choropleth speaks to) and *potentially affected by this routing tradeoff* names the concept directly.

### Methods

Six trims (no claim changed; only abstraction level changed):

| Dropped from v9 | v10 |
|---|---|
| ", a threshold below which institutional door-to-balloon differences between competing PCI centers can offset additional drive time" | (the threshold is named without the rationale; rationale lives in manuscript Methods) |
| "Road-network drive times via OSRM" → "OSRM" brand mention | "Drive times were estimated from..." (engine name lives in manuscript Methods) |
| "Annual STEMI estimates applied published U.S. incidence (1 per 1,000 adults/year; AHA Heart Disease and Stroke Statistics 2024) to block-group adult population from the American Community Survey 2019–2023" | "Annual STEMI case counts were estimated by applying a published incidence rate to the adult population." (specific rate and citation move to manuscript Methods) |
| "Headline metric, threshold, and sensitivities were pre-specified in code before analytic results were generated" | "The primary metric and sensitivity analyses were prespecified." (more concise; "in code" detail moves to Methods) |
| "code is provided for reproducibility" | (the GitHub URL lives in the figure source line and the supplement; doesn't need to be in the abstract Methods) |
| "No inferential testing was performed; sensitivities are reported as effect magnitudes" | (this caveat moves to manuscript Methods; conventional abstracts do not need to disclaim absence of inferential testing) |

Voice change: "Cross-sectional national analysis..." → "**We performed** a cross-sectional national analysis..." First-person plural is the standard in clinical abstracts.

ACS named explicitly in the data sources list: "Census 2020, ACS 2019–2023 adult population estimates, and OpenStreetMap..." Reader sees the adult-population denominator without needing to read the rate sentence to find out where it came from.

### Results

Three changes:

1. **Past tense throughout** ("lived" not "live", "was reachable" not "is reachable", "was distributed" not "is distributed"). Conventional Results-section voice in formal abstracts.
2. **Drops the standalone sentence** "For these patients, the proximity-based default destination is not necessarily fastest to reperfusion." This was a Background-style restatement inside Results; redundant given the Background already establishes the same idea.
3. **Sensitivity sentence dramatically compressed:**
 - v9: "Primary finding was robust across all six pre-specified sensitivity analyses (range 157,000–236,000 STEMI patients/year; the pre-specified incidence rate sweep at ±20% accounted for the full spread, with all five non-rate sensitivities deviating by ≤13%)."
 - v10: "Findings were robust in prespecified sensitivity analyses, with estimates ranging from 157,000 to 236,000 patients annually."
 - The rate-sweep-vs-non-rate split is preserved in `outputs/tables/sensitivity_table.csv` and the supplement; the abstract just gives the range.

Drops "raising EMS mutual-aid considerations" from the cross-state sentence. Keeps the 3.7% figure neutral; lets the reader draw the policy inference.

### Conclusions

Substantial rewrite, much tighter:

| v9 | v10 |
|---|---|
| "This first national mapping identifies the U.S. STEMI population for whom EMS routing optimization could meaningfully alter time-to-reperfusion." | "A large U.S. STEMI population lives in areas where more than one PCI-capable hospital is reachable with only a modest difference in drive time." |
| "The substrate is distributed across approximately 1,550 PCI-capable hospitals rather than concentrated at flagship centers." | (dropped — already in Results) |
| "Such routing protocols would complement facility-level interventions like STEMI Receiving Center certification, addressing the between-hospital decision they cannot resolve." | (dropped from abstract; this is a manuscript Discussion claim, not an abstract claim) |
| "Dynamic routing using traffic and expected D2B awareness may improve FMC-to-reperfusion time." | "These findings define a national substrate for EMS routing strategies that incorporate both transport time and hospital-level reperfusion performance." (no longer claims improvement; just identifies the substrate as the basis for such strategies) |
| "Limitations include free-flow drive-time computation and the absence of patient-level outcomes, both planned in forthcoming work." | "Future work should evaluate observed traffic conditions, door-to-balloon times, and patient-level outcomes." (combines limitations + future work into one academic future-tense sentence) |

The Conclusions now does three things and only three things: (1) summarises the finding in one cleaner sentence, (2) names the policy substrate, (3) names the next-step research question. Drops the "first national mapping" claim entirely (more conservative — leaves it for reviewers to assess).

### Anti-drift cross-reference (per claim_calibration.md, v10)

Same as v9 with two additions specific to v10's language:

- ✓ "lived in areas where..." — substrate-level past-tense observation
- ✓ "may not provide the shortest total time" — properly hedged
- ✓ "Findings were robust in prespecified sensitivity analyses" — earned, not aspirational
- ✓ "These findings define a national substrate" — naming the geography, not claiming intervention works
- ✓ "Future work should evaluate" — directional, neither overclaiming nor underclaiming
- ✗ NOT claiming the routing optimization *does* save time
- ✗ NOT claiming any specific hospital is the wrong destination
- ✗ NOT claiming live D2B data infrastructure exists today (no longer mentioned)
- ✗ NOT naming a specific data system (NCDR, etc.) as implementation path
- ✗ NOT naming STEMI Receiving Center certification or other named interventions (those are manuscript Discussion content)
- ✗ NOT making the "first national mapping" priority claim

---

## Figure caption

Same as the v9 caption (figure unchanged). For consistency with v10's title shift from "catchment" to "transfer," the figure caption should likely match. Optional one-word edit; figure rendering unchanged.

**Figure 1.** U.S. counties by share of adults with two PCI-capable hospitals within 15 minutes of each other by drive time — areas where routing to the hospital with shorter door-to-balloon time may shorten time to reperfusion after STEMI. Each county is shaded by the percentage of its adult population aged 20+ in such a competitive transfer zone, defined as a block group in which the second-nearest PCI-capable hospital is reachable within 15 additional minutes beyond the nearest. Deep teal counties (>75%) are predominantly metropolitan; pale counties (<25%) are predominantly rural. Connecticut block groups are remapped from the historical-county Census 2020 vintage to the 2023 TIGER planning-region vintage via a block-group-centroid spatial join (`src/01c_ct_planning_region_crosswalk.py`). Drive times computed via OSRM on the U.S. OpenStreetMap extract, free-flow profile (live traffic not modelled; addressed in Limitations). Albers Equal Area Conic projection.

---

## Note on supersession

Abstract drafts v1 through v9 are preserved as separate files in `notes/`. v9 was marked FINAL on 2026-05-08; this v10 supersedes it on 2026-05-09 with a register/economy revision (no findings changed, no methodology changed, no claims withdrawn). v9's status header should be updated from "FINAL" to "SUPERSEDED by v10" so a reader scanning the file tree does not assume v9 is the current version.
