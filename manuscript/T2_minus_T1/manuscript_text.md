# Manuscript text — T₂ − T₁ drive-time gap to PCI-capable hospitals

*Drop-in paragraphs for the Methods and Results sections, written to AHA / Circulation style. Number formatting follows the AHA Statistical Update conventions: integers for counts (with thousands separators), one decimal place for time in minutes, and 95% confidence intervals reported in parentheses.*

*Companion file `ANALYTICAL_DECISIONS.md` (same folder) records the analytical decisions that govern this manuscript and its planned matchable-reroute sequel: the scope of the contribution being claimed (Decision 1), the rejection of scraped Mission: Lifeline data (Decision 2), the direction-only Discussion claim with no quantitative matchable-reroute inference (Decision 3), the registry-based design for the sequel (Decision 4), the AHA Statistical Update reporting conventions (Decision 5), Circ:CVQO as the locked target venue (Decision 6), the narrowed central thesis (Decision 7), the locked figure and table list (Decision 8), and the population-weighting methodological frame (Decision 9). Consult that file before rewriting or extending the Discussion.*

---

## Discussion paragraph (anchored, do not overwrite without consulting Decision 3)

Two interpretations of T₂ − T₁ are possible. The conservative reading is that 5 minutes is a small geographic margin and that the nearest PCI center is the appropriate destination for nearly all U.S. STEMI patients. The operational reading is that 5 minutes is a budget within which the second-nearest center, if known to be faster on door-to-balloon time, would lower total ischemic time. Whether the second reading is empirically justified depends on the distribution of hospital-level D2B times — specifically, on whether the door-to-balloon advantage at the second-nearest hospital can exceed the transport tax T₂ − T₁ + Δ_transfer. The national CathPCI Registry literature (Menees et al., 2013) and successor analyses have repeatedly documented inter-hospital D2B variation on the order of 20 to 30 minutes, well in excess of the 5-minute national median T₂ − T₁ reported here. The size of the matchable population, however, requires the patient-level pair-wise D2B distribution; an ecological inference from aggregate registry IQR would substantially overstate it. We therefore frame T₂ − T₁ not as evidence that EMS rerouting is beneficial, but as the access-side prerequisite that rerouting would not impose a meaningful ischemic penalty. The complementary matching-side measurement, using GWTG-CAD or NCDR CathPCI data, is the natural sequel.

---

## Methods (sub-section: *Redundancy of PCI coverage*)

For each U.S. block group, we identified the nearest (T₁) and second-nearest (T₂) percutaneous-coronary-intervention–capable hospital and computed the drive-time gap T₂ − T₁ as a measure of coverage redundancy. A small gap indicates that a STEMI patient whose closest cath lab is on diversion, occupied, or otherwise unavailable can be diverted to a second center at minimal incremental ischemic time; a large gap identifies populations for whom the nearest center is effectively a single point of failure.

Drive times were estimated from the population-weighted centroid of each block group along the OSRM road network (free-flow). The hospital roster (n = 4,408) was derived from the CMS Provider of Services file; PCI capability (n = 1,598) was assigned from CMS MedPAR 2024 AMI–PCI billing volume. Adult denominators (≥20 years) were taken from the American Community Survey 2019–2023 five-year estimates; Connecticut block groups were reconciled across the 2022 county-to-planning-region transition by proportional allocation on CenPop2020 population shares.

State and regional summaries are population-weighted medians; 95% confidence intervals were obtained by a block-group–level nonparametric bootstrap (500 replicates; seed 2026). Census-region definitions are those of the U.S. Census Bureau. Block groups whose centroid lay outside the 90-mile haversine envelope of every PCI-capable hospital (n = 970 BGs; 0.74 million adults ≥20) were excluded; block groups with only one PCI-capable hospital within that envelope (n = 2,533 BGs; 2.24 million adults ≥20) were tabulated separately as a "no-redundancy" stratum and excluded from the T₂ − T₁ rate calculations.

**Population weighting (Methods sub-section).** All summary statistics — medians, interquartile ranges, regional aggregates, state estimates, cumulative population curves, and bootstrap confidence intervals — are weighted by the ACS 2019–2023 five-year adult population aged ≥20 within each block group. Because U.S. block groups vary by more than an order of magnitude in adult count (rural and frontier block groups frequently contain <300 adults; urban block groups contain 1,500–4,000), unweighted block-group-level summaries would describe the typical *block group* rather than the typical *adult*, and would shift the median toward the longer rural-tail values. The population-weighted median is the smallest T₂ − T₁ at which the cumulative population weight reaches half of the total denominator (type-7 quantile with linear interpolation inside the bin). Bootstrap confidence intervals were generated by block-group-level (cluster) resampling with replacement, preserving each block group's adult-population weight, consistent with the AHA Heart Disease and Stroke Statistics Update and CDC Surveillance for Cardiovascular Disease reporting conventions. County-level choropleths (Figure 2) are inherently area-weighted by their visual unit (the geographic polygon); the population-weighted complement appears in Tables 1 and 2 and in Figure 3.

## Results (paragraph)

Among 234,690 block groups (245.3 million adults ≥20) with two PCI-capable hospitals reachable, the population-weighted median T₂ − T₁ was **5.1 minutes (95% CI, 5.0–5.1)** (Figure A). Half of all U.S. adults therefore live within a 5-minute road-network detour of a second PCI option — a margin small enough that, in operational terms, the system can absorb routine cath-lab unavailability without imposing meaningful additional ischemia. The gap was tightly bounded in the urban Northeast (median 4.3 minutes; 95% CI, 4.2–4.3) and Midwest (4.7 minutes; 4.6–4.7), wider in the West (4.9 minutes; 4.8–5.0), and widest in the South (6.0 minutes; 5.9–6.1) (Table 2).

The interquartile range, however, conceals a marked rural tail. The 90th percentile of T₂ − T₁ exceeded 28 minutes in all four regions and reached **104.8 minutes in Wyoming** — meaning that 1 in 10 Wyoming adults living near a PCI center is, in effect, served by a single facility for which the nearest backup is more than 1 hour and 40 minutes away. Within-region heterogeneity was greatest in the West, where the population-weighted median ranged from 0.8 minutes in New Mexico (Albuquerque-metro clustering) to **46.8 minutes (95% CI, 45.0–47.7) in Wyoming**; the Northeast spanned 2.7 minutes (Maine) to 37.5 minutes (Vermont); the Midwest 2.2 minutes (Iowa) to 6.6 minutes (Kansas); and the South 3.4 minutes (District of Columbia) to 12.1 minutes (Alabama) (Table 1, Figure B).

A further **2,237,857 adults ≥20 reside in block groups with only one PCI-capable hospital within road-network reach**, concentrated in the West (1.31 million) and the Midwest (0.81 million). For this population, the operational concept of a second-nearest PCI center does not apply: any disruption to the single reachable cath lab translates one-to-one into helicopter-dependent transfer or non-PCI reperfusion. This stratum, more than the median T₂ − T₁ itself, identifies the catchments where station-placement and air-medical investment are most likely to convert into avoided STEMI deaths.

---

## Suggested figure legends

**Figure A.** Population-weighted median drive-time gap between the nearest and second-nearest PCI-capable hospital (T₂ − T₁), by state, with 95% confidence intervals. States are sorted by ascending median; bars are colored by U.S. Census region. The dashed line marks the national pop-weighted median (5.1 minutes). Adults ≥20 in block groups with only one reachable PCI hospital (n = 2.24 million) and adults in block groups with no reachable PCI hospital (n = 0.74 million) are excluded from the displayed estimates and are tabulated separately in Table 1.

**Figure B.** Census-region summary of T₂ − T₁ with 95% confidence intervals. Within-region range is documented in Table 2.

---

## Supplement — Statistical Analysis (technical methods note)

Population weighting was applied at the level of the block group, with weights equal to the ACS 2019–2023 five-year count of adults aged ≥20 within each block group (denoted *w*ᵢ for block group *i*). Let *x*ᵢ denote the block group's T₂ − T₁ value in minutes. The population-weighted q-quantile was computed as a type-7 quantile on the weighted empirical distribution: block groups were sorted in ascending order of *x*, the cumulative weight *W*(*k*) = Σᵢ≤ₖ *w*ᵢ was computed, and the target weight *T* = *q* × *W*(*n*) was located. The quantile estimate was *x*ⱼ + ((*T* − *W*(*j*−1)) / *w*ⱼ) × (*x*ⱼ − *x*ⱼ₋₁) where *j* is the smallest index with *W*(*j*) ≥ *T*. This estimator reduces to the standard quantile when all weights are equal and is the population-level analogue of the type-7 quantile used by R's `quantile()` and NumPy's `numpy.quantile(interpolation="linear")`. Confidence intervals were generated by a block-group-level (cluster) nonparametric bootstrap: 500 replicates were drawn with replacement from the set of *n* block groups, each carrying its original weight *w*ᵢ, and the weighted quantile was re-computed on each replicate; the reported 95 % CI is the 2.5–97.5 percentile range of the bootstrap distribution. This procedure preserves the block group as the sampling unit while reporting estimates and inference at the adult-population level — the standard convention in the AHA Heart Disease and Stroke Statistics Update, the CDC Surveillance for Cardiovascular Disease reports, and the Dartmouth Atlas of Health Care.

The county-level choropleths in Figure 2 are inherently area-weighted by their visual unit (the geographic county polygon) and do not carry population weights; the population-weighted complement appears in Tables 1 and 2 and in Figure 3, consistent with the convention that maps describe geography while tabular summaries describe populations.

---

## Files

- `T2_minus_T1_tables.xlsx` — three-sheet workbook (Table 1 state, Table 2 region, Table 3 region × nearest-tier).
- `figure_state_T2_minus_T1.pdf` / `.png` — Figure A (state-ranked, with 95% CIs).
- `figure_region_T2_minus_T1.pdf` / `.png` — Figure B (regional forest plot).
- `table1_state_T2_minus_T1.csv`, `table2_region_T2_minus_T1.csv`, `table3_region_x_tier.csv` — raw tables.
- `national_summary.txt` — single-number summary.
- `t2_minus_t1_analysis.py`, `figure_t2_minus_t1.py`, `build_workbook.py` — reproducibility scripts.
