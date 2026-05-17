# Analytical decisions — T₂ − T₁ manuscript and matchable-reroute sequel

Durable record of analytical decisions for the *Drive-time gap between the nearest and second-nearest PCI-capable hospital* manuscript and its planned sequel. This file is **referable from the code**: each analysis script in this folder cites this document in its module docstring. Future manuscript-writing tasks in this project — including the matchable-reroute sequel paper — should consult this file before drafting Discussion language or proposing data acquisitions.

Decision log is append-only and dated.

---

## 2026-05-16 — Decision 1. The current paper stands on the T₂ − T₁ measurement alone

**Decision.** The submitted manuscript reports the population-weighted state- and region-level distribution of T₂ − T₁ across CONUS adults aged ≥20. It does *not* report a matchable-reroute count, does *not* attempt to estimate lives saved through EMS rerouting, and does *not* include a D2B IQR table.

**Rationale.** The contribution being claimed is the access-side measurement: a previously unreported demonstration that for half of the U.S. adult population, the second-nearest PCI hospital is reachable within a 5-minute road-network detour. This is sufficient for publication on its own and is best presented uncluttered by adjacent claims that require data we do not have at the patient level.

**How to apply.** When writing or revising the manuscript, do not add tables, figures, or paragraphs that compute or imply an absolute matchable-reroute population.

---

## 2026-05-16 — Decision 2. Do not scrape AHA Mission: Lifeline tier data for an AHA-level publication

**Decision.** No press-release scrape of AHA Mission: Lifeline STEMI Receiving Center recognition will be used in either the current paper or the planned matchable-reroute sequel.

**Rationale.** Scraped recognition data is (a) selection-biased toward hospitals that participate in the recognition program and self-disclose their tier; (b) time-bounded by annual cycles with partial reporting lag; (c) ordinal at four bands and therefore coarse relative to the continuous D2B time it imperfectly proxies; (d) editorially fragile — a reviewer at JAMA, Circulation, or NEJM is likely to identify scrape-based national tier assignment as the methods section's weakest sentence, regardless of how rigorously the assembly is performed.

**How to apply.** When proposing data sources for any paper in this project, scraped Mission: Lifeline tier data is off-limits. The legitimate routes to hospital-level D2B for AHA-level publication are: (i) the AHA Get With The Guidelines – Coronary Artery Disease (GWTG-CAD) / Mission: Lifeline registry via application + IRB, or (ii) the ACC NCDR CathPCI Registry via application + fee. The Care Compare STEMI eCQM (timeliness percentage, continuous in [0,1]) is acceptable for proxy analyses but not for a quantitative time-saved claim.

---

## 2026-05-16 — Decision 3. Direction claim in Discussion, no quantitative matchable-reroute claim

**Decision.** The Discussion section may state that the inequality D₂B₁ − D₂B₂ > T₂ − T₁ is not vacuous — i.e., that the published national distribution of inter-hospital D2B variance overlaps the distribution of T₂ − T₁ such that rerouting is a credible lever in principle. The Discussion may *not* assert how many adults, what fraction of STEMI cases, or how many lives are involved.

**Rationale.** Two acts of inference are at stake. (1) The **direction claim** — "rerouting is operationally meaningful for some non-trivial fraction of the population" — requires only that the published aggregate hospital-level D2B IQR (~20–30 min, e.g., Menees et al., NEJM 2013; DOI 10.1056/NEJMoa1208200) overlaps the empirical T₂ − T₁ distribution reported in this paper. This is standard scientific contextualization and reviewers expect it. (2) The **quantitative claim** — "X million adults have a matchable reroute" — would be an ecological inference from aggregate registry IQR to a patient-level pair-wise distribution that is conditioned on geographic proximity and on the system-of-care correlation structure across hospitals. That inference is not defensible and would overstate the matchable population. Reviewers would correctly flag it.

**How to apply.** The committed Discussion paragraph for this manuscript is reproduced in `manuscript_text.md` and in the project memory file `project_d2b_match_study.md`. Any rewrite that adds an absolute matchable-reroute count, a state-by-state matchable fraction, or a lives-saved estimate is a violation of this decision and must be reversed before submission.

---

## 2026-05-16 — Decision 4. The sequel is a registry paper, not a proxy paper

**Decision.** The follow-on matchable-reroute analysis will be designed around AHA GWTG-CAD or NCDR CathPCI patient-level data. The application should be filed in parallel with the submission of the current paper so the sequel has a real data path.

**Rationale.** A Care Compare STEMI eCQM proxy analysis is publishable but is one tier below the quality of evidence the question deserves. The matchable-reroute estimate is operationally policy-relevant — it directly informs EMS routing protocols, Mission: Lifeline regional planning, and state cardiac system regulation. Policy-relevant point estimates require patient-level, continuously-distributed time data. A proxy paper based on a binary timeliness rate would underwrite a recommendation that policymakers, EMS medical directors, and STEMI receiving systems would be asked to act on; the proxy is not strong enough to bear that weight.

**How to apply.** When starting the sequel, the first action is the GWTG-CAD application packet, not a code scaffold. Code for the patient-level matching arithmetic can be drafted in parallel using synthetic data while the application is in review.

---

## 2026-05-16 — Decision 5. Reporting standard: AHA Statistical Update conventions

**Decision.** All tables and figures use AHA / Circulation reporting standards: integers with thousands separators for counts, one decimal place for time in minutes, 95% confidence intervals in parentheses, bootstrap CIs at 500 replicates (seed 2026) for population-weighted medians, denominator-honest (numerator/denominator) framing with no naked percentages, and methods footnotes including data vintage, exclusions, and the Connecticut planning-region crosswalk.

**Rationale.** Cross-paper consistency in this project. Project memory `feedback_absolute_counts.md` already commits to absolute counts over percentages; this decision extends the same commitment to CI reporting, weighting, and methods transparency.

**How to apply.** Tables produced by `build_workbook.py` and `t2_minus_t1_analysis.py` already conform. Future tables in this project should reuse the helper functions in `t2_minus_t1_analysis.py` (specifically `wq()` for weighted quantiles and `boot_ci_wq()` for bootstrap CIs).

---

## 2026-05-16 — Decision 6. Target venue locked: Circulation: Cardiovascular Quality and Outcomes

**Decision.** The current paper is targeted at *Circulation: Cardiovascular Quality and Outcomes* (Circ:CVQO), not at *NEJM*, *JAMA*, or *Circulation* (parent). The figure and table package is locked accordingly: 3 figures, 2 tables, plus supplement.

**Rationale.** We do not have, and will not acquire for this submission, patient-level door-to-balloon data (GWTG-CAD, NCDR CathPCI) nor clinical outcome data (STEMI mortality, ischemic-time linkage). Without those, the manuscript cannot defend a clinical-impact or matchable-reroute claim at the top-tier general-medical or top-tier cardiology level. *Circ:CVQO* is the correct fit for an access-geometry quality measurement paper.

**How to apply.** Frame the paper as a methods-and-measurement contribution in the quality-of-care lane, not as an outcomes paper. Discussion may forward-reference the matchable-reroute sequel using peer-reviewed registry aggregates only; it must not assert quantitative reroute benefits in the current paper.

---

## 2026-05-16 — Decision 7. Central thesis (revised, narrower)

**Decision.** The committed central thesis for this manuscript is:

> *"For half of all contiguous U.S. adults aged ≥20, the second-nearest PCI-capable hospital is reachable within an additional 5-minute road-network detour from the nearest. This redundancy is a previously uncharacterized structural feature of U.S. STEMI access geography. It distinguishes a near-universal first-hospital access topology from a heterogeneous, frontier-concentrated residual of 2.24 million adults whose nearest PCI-capable hospital is — by definition — a single point of failure."*

Three sub-claims, each mapped to data we have:
1. 122 million adults, 49% of CONUS, T₂ − T₁ ≤ 5 min (median 5.083 min; 95% CI 5.0–5.1).
2. T₂ − T₁ as a novel population-scale measurement (Figures 1 and 2; no prior national paper at BG resolution).
3. 2.24 million-adult no-redundancy stratum, geographically concentrated (Table 1, Figure 2B).

**Rationale.** Supersedes the earlier "binding constraint" framing in `project_binding_constraint_framing.md`. The binding-constraint formulation requires patient-level D2B variance to defend; we do not have it. The revised thesis is what the current data can carry alone.

**How to apply.** All Discussion language must be checkable against these three sub-claims. The matchable-reroute sentence is a forward-reference to the planned sequel and is bounded by the published aggregate D2B IQR (Menees 2013); it is not a quantitative claim in this paper.

---

## 2026-05-16 — Decision 8. Figure and table list locked

**Decision.** The following package is final for the Circ:CVQO submission. No additional primary figures or tables without revisiting these decisions.

**Figures:**
- **Figure 1.** Concept and exemplar (existing). Panel A: schematic of T₁, T₂, and the T₂ − T₁ ≤ 15 min "competitive routing zone" definition. Panel B: North Carolina BG centroids colored by T₂ − T₁, PCI hospitals overlaid. Source: `figure1.py`.
- **Figure 2.** National geography (existing). Panel A: county-level T₁ choropleth. Panel B: county-level T₂ − T₁ choropleth. Stemifast palette, dark = concerning (problem counties). Source: `figure2.py`.
- **Figure 3.** Population distribution. Single panel: population-weighted cumulative distribution curve of T₂ − T₁. National curve in NAVY, four Census-region overlays in Wong/IBM palette. Vertical reference lines at 5, 15, 30 min with annotated cumulative adult counts. Right-margin annotation for the 2.24 M no-redundancy adults. Source: `figure3.py` (to build).

**Tables:**
- **Table 1.** State-level population-weighted T₁, T₂, T₂ − T₁ with 95% CIs, IQR, p90, adult counts, 1-PCI stratum counts. 49 jurisdictions, sorted alphabetically. Source: `table1_state_T2_minus_T1.csv`.
- **Table 2.** Census-region summary: population-weighted median T₂ − T₁ (95% CI), IQR, p90, lowest and highest state within region. Source: `table2_region_T2_minus_T1.csv`.

**Supplement:**
- **Figure S1.** Sorted state-level dumbbell of T₁ → T₂ with 95% CI on the gap (the earlier figure superseded by Figure 2). Source: `figure_2a_dumbbell.py`.
- **Table S1.** Detailed exclusion accounting (970 BGs / 741,166 adults in no-PCI stratum; 2,533 BGs / 2,237,857 adults in 1-PCI stratum; CT crosswalk allocation per planning region).
- **Methods supplement.** OSRM pipeline, 90-mile haversine prefilter, ACS adult denominator, bootstrap CI procedure.

**Rationale.** Three figures, three jobs (concept → geography → population distribution). Two tables, two summaries (state, region). Locked to the narrowed thesis (Decision 7).

**How to apply.** Adding a Figure 4 or a Table 3 requires explicit reversal of this decision. If a reviewer requests an additional analysis, prefer placing it in the Supplement.

---

## 2026-05-17 — Decision 9. Population weighting is the inferential frame; every summary statistic uses adult-population weights

**Decision.** Every summary statistic in the manuscript and supplement — median, IQR, percentile, regional aggregate, state estimate, cumulative population curve, and bootstrap confidence interval — is **population-weighted by ACS 2019–2023 adults aged ≥20**. The block group is the *sampling unit* but the adult is the *unit of inference*. The Methods section, Figure 3 caption, and Tables 1 and 2 captions must each state explicitly that estimates are population-weighted.

**Rationale.** U.S. block groups are dramatically unequal in adult population: urban block groups typically contain 1,500–4,000 adults; rural and frontier block groups frequently contain fewer than 300. Critically, the rural and frontier block groups, which are *more numerous geographically per unit population*, also have the **longest T₂ − T₁ values**. Without population weighting:

- Unweighted estimates would describe the *typical block group*, not the *typical adult*.
- The rural tail would dominate the median, overstating the population-level access problem.
- Summary statistics would no longer translate into clinical or policy claims about *adults* (e.g., lives potentially affected by EMS protocol change).

The manuscript's central claim — *"half of all contiguous U.S. adults aged ≥20 live within a 5-minute additional road-network detour of a second PCI-capable hospital"* — is a population-level claim. Only the population-weighted median (5.083 min; 95% CI 5.0–5.1) supports this claim. An unweighted block-group-level median would yield a different number that does not bear on the claim.

This is also the convention of the AHA Heart Disease and Stroke Statistics Update, the CDC's Surveillance for Cardiovascular Disease reports, and the Dartmouth Atlas — all of which default to population-weighted estimates for state-level and regional summaries.

**How to apply:**

1. **Manuscript Methods section** must contain a paragraph that:
   - States the weighting variable: ACS 2019–2023 five-year adult population aged ≥20 per block group.
   - Defines the weighted quantile estimator: sort block groups by T₂ − T₁, compute cumulative weighted population, take the smallest T₂ − T₁ at which cumulative weight ≥ q × total weight (type-7 quantile with linear interpolation inside the bin).
   - States the bootstrap procedure: block-group-level (cluster) resampling with replacement preserving each block group's adult-population weight; 500 replicates; seed = 2026.
   - Acknowledges the choropleth caveat (Figure 2 is area-weighted by construction; population-weighted estimates are reported in Tables 1 and 2 and in Figure 3).

2. **Figure 3 caption** already notes "Population-weighted T₂ − T₁ by region" and "Population-weighted cumulative distribution of T₂ − T₁ across contiguous U.S. adults aged ≥20." These statements must remain.

3. **Tables 1 and 2 captions** must state "Medians are weighted by ACS 2019–2023 adults aged ≥20."

4. **Supplement methods note**: a one-paragraph technical methods note in the Supplement (under "Statistical Analysis") should explain the weighted-quantile and cluster-bootstrap procedures in formal notation. The narrative explanation written for this decision can be condensed into ~150 words for the Supplement.

5. **Discussion**: when reporting headline numbers, always include the population-weighted qualifier on first mention (e.g., "*the population-weighted median T₂ − T₁ was 5.1 minutes [95% CI 5.0–5.1]*"). Subsequent mentions in the same paragraph may drop the qualifier.

**The one exception, explicitly flagged**: Figure 2 (county-level choropleths) is inherently area-weighted because the visual unit is the geographic polygon. The Methods text and Figure 2 caption must state this and direct readers to Tables 1, 2, and Figure 3 for the population-weighted complement. This is the only artifact in the manuscript that does not use population weighting, and the asymmetry must be acknowledged.

---

## 2026-05-17 — Decision 10. AHA Scientific Sessions abstract is the locked scope-and-narrative reference for the full manuscript

**Decision.** The AHA Scientific Sessions abstract committed to `AHA_abstract.md` (this folder) on 2026-05-17 is the locked scope-and-narrative reference for the full *Circulation: Cardiovascular Quality and Outcomes* manuscript. Title, paragraph sequence (Background → Methods → Results → Conclusions), and the four claim moves it contains define what the manuscript argues. Any future manuscript draft starts from this abstract and elaborates within its scope; it does not depart from it.

Specific editorial controls flowing from the locked abstract — each supersedes prior language in this file and in the project memory where conflicting:

(a) **Headline framing is "additional drive time to a second PCI-capable hospital."** Not "T₂ − T₁," not "redundancy," not "binding constraint," not "matchable reroute." T₂ − T₁ notation remains in code module names and in the supplementary methods for reproducibility; it does not appear in the manuscript narrative or in figure titles.

(b) **Background.** The clinical anchor is *time to reperfusion* — not FMC-to-balloon, not symptom-to-device, not door-to-balloon. *Time to reperfusion* is the broadest defensible outcome statement and avoids privileging a single interval. Subsequent mentions of door-to-balloon variation in the Conclusions are framed as one component of that broader interval, not as the outcome itself.

(c) **Results.** Population-cumulative thresholds — 122 M / 196 M / 226 M adults at 5 / 15 / 30 additional minutes — and a STEMI-incidence translation (≈122,000 / 196,000 / 226,000 STEMI patients per year, conditioned on the explicit assumption of 1 STEMI per 1,000 adults per year) are part of the locked abstract. The STEMI-incidence translation is the only inferential step in the abstract; keep it explicitly conditional so the assumption is auditable.

(d) **Conclusions are hedged.** The abstract does not name GWTG-CAD or NCDR CathPCI as the sequel data path. It does not assert that EMS triage to a faster-D2B center "may shorten total ischemic time." It states only that further work is needed to determine whether incorporating hospital-level performance into destination selection may improve reperfusion timeliness or clinical outcomes. The matchable-reroute sequel design (Decision 4) is unchanged but is held entirely out of the abstract text. The full manuscript Discussion *may* name GWTG-CAD / NCDR CathPCI as the registry path (per Decision 4); the abstract does not.

(e) **The no-redundancy stratum (2.24 M single-PCI adults) is held out of the abstract** to keep the headline narrative on the choice question. It re-enters in the full manuscript via Table 1 / Figure 2 and as a Discussion paragraph framing the residual access problem (per Decision 7, sub-claim 3).

**Rationale.** The user finalized this abstract text on 2026-05-17 after iterative revision focused on clinical and policy reader voice, active construction, scientific modesty, and the removal of project-internal scaffolding terms ("competitive zones," "redundancy," "binding constraint") that the audience does not share. The hedged Conclusions reflect (i) the absence of patient-level D2B data in this paper, (ii) the AHA Sessions reviewer audience preferring conservative directional language over inferential leaps, and (iii) the editorial standard of *Circ:CVQO* (Decision 6), where overclaiming in a precursor abstract would prejudice the full manuscript review.

**How to apply.**
1. Before drafting any section of the full manuscript, re-read `AHA_abstract.md` in this folder. It is the source-of-truth for what the paper argues.
2. Do not reintroduce "T₂ − T₁" notation, "redundancy," "binding constraint," or "matchable reroute" framing into manuscript narrative text. They persist in code, supplement, and this decisions file for historical clarity only.
3. The full manuscript Discussion may name GWTG-CAD / NCDR CathPCI as the sequel data path (Decision 4); the abstract does not.
4. The STEMI-incidence translation (≈1 per 1,000 adults per year) is the only quantitative inferential step in the abstract — keep it explicitly conditional in the full manuscript as well, and footnote the source (HCUP NIS / AHA EpiHeart range).
5. When future chats open a manuscript-writing task on this project, the first read is this Decision 10 entry plus `AHA_abstract.md`.

---

## Pointers

- **Locked AHA Scientific Sessions abstract** (scope-and-narrative source-of-truth): `AHA_abstract.md` (same folder).
- Manuscript draft text: `manuscript_text.md` (same folder). To be re-aligned with the locked abstract before submission.
- Tables and figure artifacts: `T2_minus_T1_tables.xlsx`, `figure_state_T2_minus_T1.{pdf,png}`, `figure_region_T2_minus_T1.{pdf,png}`.
- Reproducibility scripts: `t2_minus_t1_analysis.py`, `figure_t2_minus_t1.py`, `build_workbook.py`.
- Sequel study plan in project memory: `project_d2b_match_study.md`.
- Manuscript framing line in project memory: `project_binding_constraint_framing.md` (superseded by Decision 10 for abstract scope).
