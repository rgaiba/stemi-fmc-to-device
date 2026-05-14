# AHA Scientific Sessions 2026 Abstract: Draft v10 (FINAL)

**Date:** 2026-05-09
**Author:** Rahul Gaiba, MD · Bayhealth Medical Center · Department of Internal Medicine
**Track:** Quality, Outcomes, and Resuscitation Sciences
**Status:** v10 FINAL; supersedes v9. Substantial register and economy revision: conventional academic-abstract voice, past-tense Results, citations moved out of inline prose, Methods and Conclusions trimmed for length and tone. Title pivots from "Competitive Catchment Zones" to "Competitive Transfer Zones" (action-oriented; names the routing decision rather than the geographic capture area).

---

## Title

**National Mapping of U.S. PCI Competitive Transfer Zones for STEMI Routing Optimization**

---

## Abstract

**Background.** Time-to-reperfusion drives STEMI outcomes. Although most U.S. adults now live within 60 minutes of a PCI-capable hospital, the geographically nearest PCI center may not provide the shortest total time to reperfusion because door-to-balloon performance varies across hospitals. The size and national distribution of the population potentially affected by this routing tradeoff have not been well quantified.

**Methods.** We performed a cross-sectional national analysis using CMS Provider of Services (December 2024), Census 2020, ACS 2019–2023 adult population estimates, and OpenStreetMap road-network data. Drive times were estimated from 238,193 continental U.S. census block-group population centroids to 4,408 active acute care hospitals, including 1,598 PCI-capable hospitals, within 90 miles. We defined competitive zones as block groups in which a second PCI-capable hospital was reachable within 15 additional minutes of the nearest PCI-capable hospital. Our primary metric was the annual number of STEMI patients living in competitive zones. Annual STEMI case counts were estimated by applying a published incidence rate (1 per 1,000 adults per year; AHA Heart Disease and Stroke Statistics, 2024) to the adult population. Sensitivity analyses were prespecified.

**Results.** 196,253 STEMI patients per year, representing 79% of estimated U.S. STEMI cases, lived in areas where a second PCI-capable hospital was reachable within 15 additional minutes of the nearest PCI hospital. This population was distributed across approximately 1,550 hospitals; the 25 hospitals serving the largest such populations accounted for 7.5% of the total. In 3.7% of these areas, the alternative PCI-capable hospital was in a different state. Findings were robust in prespecified sensitivity analyses, with estimates ranging from 157,002 to 235,504 patients annually.

**Conclusions.** A large U.S. STEMI population lives in areas where more than one PCI-capable hospital is reachable with only a modest difference in drive time. These findings define a national substrate for EMS routing strategies that incorporate both transport time and hospital-level reperfusion performance. Such routing strategies may complement institutional performance in reducing time to reperfusion. Future work should integrate observed traffic conditions, hospital door-to-balloon times, and patient-level outcomes to quantify potential mortality benefit.

---

## Word count + character estimate

- Title: 12 words / 92 characters
- Background: 72 words
- Methods: 131 words (added explicit primary-metric definition + parenthetical citation for the STEMI incidence rate)
- Results: 88 words (headline shown to actual computed value: 196,253; sensitivity range shown to actual extremes: 157,002–235,504)
- Conclusions: 72 words (Future-work sentence rewritten to "integrate ... to quantify potential mortality benefit")
- **Abstract total: ~363 words / ~2,420 characters**

Approximately 80 chars under the AHA SS 2,500-character soft limit. Comfortable; no compression needed at the moment. If portal counts strictly at submission, a single Methods compression gets us back to ~120 chars headroom.

Under the AHA SS 2,500-character soft limit (~250 chars headroom). No compression needed.

---

## Edit ledger v9 → v10

The v9 abstract was methodologically dense; every claim explicitly anchored, citations inline, sensitivity analysis described in detail. That style fits an audit-trail document; it was not the most conventional academic-abstract register. v10 retains every numerical claim and the full epistemic conservatism but presents them in cleaner abstract prose. No findings change.

### Title

| | |
|---|---|
| v9 | National Mapping of U.S. PCI Competitive **Catchment** Zones for STEMI Routing Optimization |
| v10 | National Mapping of U.S. PCI Competitive **Transfer** Zones for STEMI Routing Optimization |

"Catchment" describes the geographic capture area passively (which population a hospital draws from). "Transfer" names the operative decision (where EMS transports the patient). The abstract is fundamentally about a routing decision, so the noun should signal the decision, not the geography. "Transfer zones" is also consistent with Mission: Lifeline and STEMI Systems-of-Care literature where "transfer" denotes the destination decision.

### Background

Three structural changes:

1. **"Time-to-reperfusion drives STEMI mortality"** → **"Time-to-reperfusion drives STEMI outcomes."** Two-step revision: (a) v9 → v10 first draft softened to "is a key determinant of STEMI outcomes" (more conventional academic register); (b) v10 revision restored the stronger verb "drives" while keeping the broader noun "outcomes". Final form is direct, established, defensible; every cardiology reader treats "time-to-reperfusion drives STEMI outcomes" as canonical knowledge. "Outcomes" stays broader than "mortality" (includes surrogate measures; ejection fraction, infarct size; and process measures the field cares about); avoids overclaiming mortality specifically.
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
| "The substrate is distributed across approximately 1,550 PCI-capable hospitals rather than concentrated at flagship centers." | (dropped; already in Results) |
| "Such routing protocols would complement facility-level interventions like STEMI Receiving Center certification, addressing the between-hospital decision they cannot resolve." | "Such routing strategies may complement institutional performance in reducing time to reperfusion." (theme retained but generalised and tightened over multiple revisions. Final form is grammatically tight and semantically precise: "in reducing" frames reduction as the *shared goal* of both routing and institutional approaches, not as a consequence routing produces alone. "May complement" carries the hedge.) |
| "Dynamic routing using traffic and expected D2B awareness may improve FMC-to-reperfusion time." | "These findings define a national substrate for EMS routing strategies that incorporate both transport time and hospital-level reperfusion performance." (no longer claims improvement; just identifies the substrate as the basis for such strategies) |
| "Limitations include free-flow drive-time computation and the absence of patient-level outcomes, both planned in forthcoming work." | "Future work should integrate observed traffic conditions, hospital door-to-balloon times, and patient-level outcomes to quantify potential mortality benefit." (combines limitations + future work into one academic future-tense sentence) |

The Conclusions now does three things and only three things: (1) summarises the finding in one cleaner sentence, (2) names the policy substrate, (3) names the next-step research question. Drops the "first national mapping" claim entirely (more conservative; leaves it for reviewers to assess).

### Anti-drift cross-reference (per claim_calibration.md, v10)

Same as v9 with two additions specific to v10's language:

- ✓ "lived in areas where..."; substrate-level past-tense observation
- ✓ "may not provide the shortest total time"; properly hedged
- ✓ "Findings were robust in prespecified sensitivity analyses"; earned, not aspirational
- ✓ "These findings define a national substrate"; naming the geography, not claiming intervention works
- ✓ "Future work should evaluate"; directional, neither overclaiming nor underclaiming
- ✗ NOT claiming the routing optimization *does* save time
- ✗ NOT claiming any specific hospital is the wrong destination
- ✗ NOT claiming live D2B data infrastructure exists today (no longer mentioned)
- ✗ NOT naming a specific data system (NCDR, etc.) as implementation path
- ✗ NOT naming STEMI Receiving Center certification or other named interventions (those are manuscript Discussion content)
- ✓ Routing optimization positioned as complementary to institutional performance improvement (not competitive with it; not a substitute for it)
- ✗ NOT making the "first national mapping" priority claim

---

## Figure caption

Same as the v9 caption (figure unchanged). For consistency with v10's title shift from "catchment" to "transfer," the figure caption should likely match. Optional one-word edit; figure rendering unchanged.

**Figure 1.** U.S. counties by share of adults with two PCI-capable hospitals within 15 minutes of each other by drive time; areas where routing to the hospital with shorter door-to-balloon time may shorten time to reperfusion after STEMI. Each county is shaded by the percentage of its adult population aged 20+ in such a competitive transfer zone, defined as a block group in which the second-nearest PCI-capable hospital is reachable within 15 additional minutes beyond the nearest. Deep teal counties (>75%) are predominantly metropolitan; pale counties (<25%) are predominantly rural. Connecticut block groups are remapped from the historical-county Census 2020 vintage to the 2023 TIGER planning-region vintage via a block-group-centroid spatial join (`src/01c_ct_planning_region_crosswalk.py`). Drive times computed via OSRM on the U.S. OpenStreetMap extract, free-flow profile (live traffic not modelled; addressed in Limitations). Albers Equal Area Conic projection.

---

## Subsequent v10 revisions (chronological, after v10 first draft)

The v10 first draft was committed as FINAL on 2026-05-09. Subsequent same-day revisions documented here:

1. **Conclusions sentence-3 added**; "Such strategies may complement institutional performance improvement by addressing the between-hospital decision that facility-level efforts cannot resolve." Restored the v3-v9 complement-not-substitute theme that the v10 first draft had tightened out.

2. **Conclusions sentence-3 tightened**; "Such routing strategies may complement institutional performance, reducing time to reperfusion." Compressed the wordier earlier formulation; "may complement" carries the hedge.

3. **Conclusions sentence-3 reframed**; "Such routing strategies may complement institutional performance in reducing time to reperfusion." "In reducing" (vs comma + "reducing") frames reduction as the *shared goal* of routing and institutional approaches, not as a consequence routing produces alone. Less hedge work for "may" to do; semantically more precise.

4. **Background sentence-1 verb restored**; "Time-to-reperfusion drives STEMI outcomes." Reverted the v9→v10-first-draft softening from "drives" to "is a key determinant of"; restores the canonical-knowledge declarative voice while keeping the broader noun "outcomes" (vs the earlier "mortality").

5. **Methods; primary metric defined explicitly + STEMI rate cited**; Added "Our primary metric was the annual number of STEMI patients living in competitive zones." Added parenthetical citation "(1 per 1,000 adults per year; AHA Heart Disease and Stroke Statistics, 2024)" inside the STEMI estimation sentence. The closing prespecification sentence reduced from "The primary metric and sensitivity analyses were prespecified" to "Sensitivity analyses were prespecified" to avoid the duplicate "primary metric" mention.

6. **Results; headline shown to exact computed values**; "Approximately 196,000 STEMI patients per year" → "196,253 STEMI patients per year"; sensitivity range "157,000 to 236,000" → "157,002 to 235,504." Pre_registration D1's three-sig-fig rule overridden in the abstract per user direction; reasoning: the rate × denominator product is a population estimate with internal arithmetic precision, the sensitivity range bounds the analytic uncertainty, and an explicit value reads more rigorous to a reviewer than a rounded one. The unrounded values were always in `outputs/tables/sensitivity_table.csv`.

7. **Conclusions Future-work sentence rewritten**; "Future work should evaluate observed traffic conditions, door-to-balloon times, and patient-level outcomes." → "Future work should integrate observed traffic conditions, hospital door-to-balloon times, and patient-level outcomes to quantify potential mortality benefit." "Integrate" (vs "evaluate") names the next-step methodology; "hospital" specifies the D2B level; "to quantify potential mortality benefit" names the research goal directly. "Potential" carries the hedge so the mortality-benefit claim stays appropriately tentative.

After these revisions, v10 is the standing FINAL.

---

## Note on supersession

Abstract drafts v1 through v9 are preserved as separate files in `notes/`. v9 was marked FINAL on 2026-05-08; this v10 supersedes it on 2026-05-09 with a register/economy revision (no findings changed, no methodology changed, no claims withdrawn). v9's status header should be updated from "FINAL" to "SUPERSEDED by v10" so a reader scanning the file tree does not assume v9 is the current version.
