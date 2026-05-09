# Pre-registration — analysis decisions locked before OSRM run
**Date:** 7 May 2026
**Purpose:** Lock the headline metric, ΔS2B threshold, drive-time engine, and sensitivity-analysis design *before* any drive-time computation begins. Pre-analysis lock is the safeguard against post-hoc cherry-picking the most flattering metric. Anyone who wants to verify methodological honesty checks: does the published headline match what's in this file at commit-date?

This document is **not editable after the first OSRM run.** Subsequent changes go through dated amendments at the bottom (with rationale), not edits to the original.

---

## D1 — Headline metric (the single number that anchors the abstract)

**Annual STEMI patients residing in census block groups where EMS routing optimization would reduce symptom-to-balloon time by ≥15 minutes.**

Computation:
```
headline_n_patients = Σ over BG where ΔS2B(BG) ≥ 15 min:
                       population(BG) × 0.004
```

Where 0.004 is the published U.S. STEMI incidence rate (4 per 1,000 adults per year). The choice of an absolute patient-count metric — rather than a percentage of the population, or a system-level minute-aggregate — is deliberate: a clinical audience at AHA Scientific Sessions reads "~Y thousand STEMI patients per year" more directly than "~M% of CONUS residents." Patient-counts also resist the "but those are mostly in zones with already-good D2B" critique because the count is conditional on ΔS2B ≥ threshold.

The reported figure will be **rounded to two significant figures** in the abstract (e.g., "approximately 240,000 STEMI patients per year"). The unrounded computation lives in the analysis outputs; the rounding is editorial only.

## D2 — ΔS2B threshold (clinical-meaningfulness cutoff)

**ΔS2B ≥ 15 minutes** for the headline.

Rationale: a 15-minute reperfusion-delay reduction matches one half-life of myocardial salvage in published infarct-modeling work; D2B differentials between high- and low-volume centers routinely exceed 15 min in registry data; and the threshold matches the 15-minute competitive-margin cutoff used throughout the proposal for internal consistency.

Sensitivity sweep at 10 and 30 min reported in the abstract Results sentence as a single parenthetical (e.g., "ranging from N₁ to N₂ patients across thresholds of 10–30 minutes").

## D3 — Competitive-margin threshold

**T₂ − T₁ ≤ 15 minutes** for primary classification of competitive catchment zones, with sensitivity at 10 and 20 min reported in the supplement (or the supplement's equivalent for an abstract).

Same 15-minute value as D2 by construction — the metric is calibrated to the institutional D2B differential range (~15–35 min between competing centers in the literature) over which routing optimization can plausibly reverse the optimal-destination recommendation.

## D4 — STEMI incidence rate

**0.004 (4 per 1,000 adults per year)** applied as a flat rate to all CONUS block group populations. Sources: AHA Heart Disease and Stroke Statistics (most-recent year). Acknowledged limitation: the rate varies by age structure, sex, and socioeconomic factors; we don't model that variation. Sensitivity at 0.003 and 0.005 covers ±25%.

## D5 — DIDO type stratification

Per `notes/dido_d2b_operationalization.md`:

| Tier B subtype | DIDO median |
|---|---|
| Academic ED (bed_cnt ≥ 300, RUCA ≤ 3) | 60 min |
| Community ED (bed_cnt 100–299) | 68 min |
| Critical access (PoS subtype 11) | 90 min |
| Specialty / freestanding | excluded from analysis |

## D6 — D2B prior

Three-layer cascade per `notes/d2b_prior_plan.md`:
1. AHA Mission: Lifeline reported median (where available)
2. Type-based prior (academic 68, community 79, low-volume 91 min)
3. Sensitivity at uniform 80 min for all Tier A hospitals

## D7 — Drive-time engine

**Local OSRM via Docker on user's machine** with the North America OSM extract (Geofabrik). Public-demo OSRM server is not used for the production run (rate-limited at ~1 req/s, would take >8 hours of wall time and fail intermittently). The Delaware prototype's haversine × 1.35 / 45 mph approximation is acceptable for the validation gate (Delaware concordance check) but not for the national headline.

## D8 — Sensitivity analyses required for any reported headline

The headline (`D1` count above) must hold to within ±25% under at least 4 of the following 6 sensitivities. If it doesn't, the headline is considered fragile and the analysis returns to methods iteration before submission.

1. Uniform DIDO (68 min for all Tier B, regardless of subtype)
2. Uniform D2B (80 min for all Tier A, regardless of size/RUCA/AMI tertile)
3. CAH DIDO swept across {60, 90, 120} min
4. Drop hospitals with `precision_tier ∈ {zip_centroid, zip_prefix}` (street-level-geocoded only)
5. Threshold sweep (ΔS2B threshold at 10, 15, 30 min)
6. Population 1 (Tier A vs Tier A choice) and Population 2 (Tier B bypass) reported separately

The sensitivity_table.csv produced by the analysis must show all six rows; the abstract Results sentence may compress to a single range.

## D9 — Pre-registration of what the headline is *not*

To prevent the natural drift toward the most flattering aggregation:

- **Not** "X% of CONUS population" (less clinical immediacy)
- **Not** "Top hospital systems account for Y% of burden" (the system-ranking number is reportable as a *secondary* result, not the headline)
- **Not** "Mean ΔS2B in competitive zones" (does not communicate population-scale impact)

The headline is annual patient count. Other aggregations may appear in the abstract but only after the headline.

---

## Amendments

*(Dated additions go here if the analysis necessitates a deviation from the above. None at present.)*

---

## Amendment 2026-05-07-A — Descope to drive-time geometry only

**Rationale:** Reviewer-attack-surface analysis, conducted before OSRM runs but after the rest of the pre-registration was locked, identified a structural simplification. Paper 1 stands cleaner if it limits its claim to what's deterministically computable from public-source drive-time geometry — leaving DIDO and D2B prior modeling to a forthcoming Paper 2. The descope eliminates the largest single attack surface (D2B prior assumptions) without weakening the central contribution (national mapping of competitive PCI catchment zones). Always easier to upscope a Phase 1 finding than to defend an over-scoped one.

The original D1 headline metric quantified routing-optimization S2B improvement in terms of a D2B-prior-dependent ΔS2B. The amended D1 quantifies the geographic substrate for routing optimization — the population in zones where institutional differences could plausibly determine optimal destination — without claiming to know what those differences are.

### D1 (amended) — Headline metric

**Annual STEMI patients residing in census block groups whose drive-time-nearest and second-drive-time-nearest PCI-capable hospital are within 15 minutes of each other** (i.e., the competitive-margin definition from the original §4 of the proposal, applied with traffic-aware OSRM drive times).

Computation:
```
headline_n_patients = Σ over BG where drive_time(T₂_PCI) − drive_time(T₁_PCI) ≤ 15 min:
                       population(BG) × 0.004
```

Interpretation: the population in zones where two PCI-capable hospitals are within a clinically meaningful drive-time margin and the optimal routing destination therefore cannot be determined by proximity alone. Whether the optimal destination differs from the proximity destination — and by how many minutes — depends on institutional D2B and DIDO, which Paper 2 will quantify. Paper 1 establishes the geographic substrate.

### D5 (deferred) — DIDO type stratification

Deferred to Paper 2. The DIDO type-stratified priors documented in `notes/dido_d2b_operationalization.md` remain methodologically defensible and will be used in Paper 2; they are not invoked in Paper 1.

### D6 (deferred) — D2B prior

Deferred to Paper 2. The three-layer D2B prior documented in `notes/d2b_prior_plan.md` remains methodologically defensible and will be used in Paper 2; it is not invoked in Paper 1.

### D8 (amended) — Sensitivity analyses for Paper 1

The Paper 1 headline (amended D1 count) must hold to within ±25% under at least 4 of the following 6 sensitivities. The set is restructured to focus on what's relevant to the descoped scope:

1. Drop hospitals with `precision_tier ∈ {zip_centroid, zip_prefix}` (street-level-geocoded only)
2. Competitive-margin threshold sweep: report at 10 / 15 / 20 min
3. STEMI incidence sweep: 3 / 4 / 5 per 1,000 per year
4. Time-of-day flip (AM peak speed profile): how many additional BGs enter or leave the competitive-zone classification at AM peak
5. Same-state-only subset (exclude BGs whose top-2 PCI candidates span a state line)
6. Tier A inclusion criterion: cath lab service code (1 or 3) versus the more restrictive concordant subset (service code AND room count ≥ 1)

### D9 (amended) — Anti-drift list, descoped

The Paper 1 headline is **the population-and-patient-count of competitive-margin zones**. It is **not**:

- ΔS2B in minutes per patient (deferred to Paper 2)
- "Routing optimization saves N hours per year" (deferred to Paper 2)
- A specific hospital system's S2B-minutes recoverable (deferred to Paper 2)

If the abstract Results sentence drifts toward any of those during writing, it has wandered into Paper 2 territory and the descope is no longer respected.

---


## Amendment 2026-05-08-A — Time-of-day analysis approach

**Rationale:** Amendment 2026-05-07-A promoted time-of-day flip (AM peak vs off-peak) from sensitivity analysis to primary result, on the assumption that OSRM with the OpenStreetMap U.S. extract supports time-aware routing natively. That assumption was wrong — vanilla OSRM with the `car.lua` profile produces free-flow drive times only. Real time-aware routing requires either commercial traffic data (INRIX, HERE) layered onto OSRM via custom edge speeds, or a switch to Valhalla's time-aware routing. Both are out of scope for the Paper 1 abstract timeline.

The amended approach: **Apply published metropolitan peak-hour travel-time indices (FHWA, INRIX National Traffic Scorecard) post-hoc to the free-flow drive-time matrix as a sensitivity bound, not a primary result.**

Multipliers (literature-based):

| Geographic class | RUCA tier | AM peak factor |
|---|---|---|
| Urban core | RUCA 1 | 1.30 |
| Suburban | RUCA 2–4 | 1.15 |
| Rural | RUCA 5–10 | 1.05 |

For each block group, the AM-peak drive time is approximated as `free_flow_time × peak_factor(RUCA_of_BG)`. The competitive zone classification is re-run with these adjusted times; we report "X% of competitive zones flip classification at AM peak" as a sensitivity.

**Implication for Paper 1's primary result:** Time-of-day is now a **sensitivity analysis**, not a primary result. The headline metric (D1) is unchanged — it's computed at free-flow times. The Methods section will note: *"Time-of-day sensitivity was estimated via published metropolitan peak-hour travel-time indices applied post-hoc to the free-flow drive-time matrix; rigorous time-aware routing using real-time traffic data is deferred to forthcoming work."*

**D8 (sensitivities) updated:** sensitivity #4 redefined from "AM peak speed profile" (which we couldn't run) to "AM-peak metro-multiplier" (which we can).

## Amendment 2026-05-08-B — STEMI incidence rate correction

**Rationale:** D4 originally locked the incidence rate at 0.004 (4 per 1,000 adults per year), citing "AHA Heart Disease and Stroke Statistics." That figure is the **AMI rate** (heart attacks of all types — STEMI plus NSTEMI plus unspecified), not the STEMI-specific rate. The pre-registration document mistakenly conflated the two.

The Paper 1 analysis is about PCI routing for STEMI specifically — the time-critical reperfusion case. Using an AMI-grade incidence rate inflates the headline patient count by approximately 3× without the underlying analytic substrate including non-STEMI events.

Caught at run-time during `06_classify_zones.py` summary review, before any numbers were published or shared externally. Filing this amendment to lock the corrected rate.

### D4 (amended) — STEMI incidence rate

**0.001 (1 per 1,000 adults per year)** applied as a flat rate to all CONUS block group populations.

Source: AHA Heart Disease and Stroke Statistics — most-recent year. U.S. annual STEMI events: ~250,000–350,000 in a CONUS adult population of ~250M ≈ 1.0–1.4 per 1,000/yr. Using the conservative end (1.0/1,000) for the headline.

Sensitivity sweep: 0.0008, 0.0010, 0.0012 (covers ±20% of the central rate). Substitutes for the original D4 sensitivity sweep at 0.003 / 0.004 / 0.005 (which were AMI-rate values).

### Implication for the headline

The pre-registration's locked headline language is unchanged — *"annual STEMI patients residing in census block groups whose drive-time-nearest and second-drive-time-nearest PCI-capable hospital are within 15 minutes of each other."* What changes is the multiplier, and consequently the magnitude of the count. With the corrected rate:

```
headline_n_patients = Σ over BG where T2_PCI - T1_PCI ≤ 15 min:
                       population(BG) × 0.001
```

Approximate value (computed from the 06_classify_zones.py output): ~260,000 STEMI patients per year in 15-min competitive zones. This is essentially the entire U.S. annual STEMI burden — a clinically intuitive number that reviewers can sanity-check against the published U.S. STEMI count.

### Note on disclosure

The original 0.004 rate was a methodological calibration error introduced when drafting the pre-registration; it was caught before any external publication or claim. The amendment is filed transparently for the reproducibility audit trail. The methods sentence in the manuscript will read: *"STEMI events were estimated from a flat U.S. adult STEMI incidence rate of 1 per 1,000 per year applied to CONUS census block group populations."*

## Amendment 2026-05-08-C — STEMI rate denominator correction (per-adult × ACS 20+)

**Rationale:** Amendment B locked the rate at 0.001 per adult per year (the AHA-published per-adult value) but applied it to the all-ages CONUS block-group population from CenPop2020. Multiplying a per-adult rate against a denominator that includes children was internally inconsistent. The implied national STEMI count from the Amendment-B configuration was ~329,000/yr — materially above the AHA *Heart Disease and Stroke Statistics 2024* range (~250,000–280,000/yr) — and the gap was approximately the under-20 population share (~25%), which made the source of the inflation unambiguous.

The error was caught at run-time during the 07_aggregate.py headline summary review, before any numbers were published or shared externally.

**Two-step resolution, same day:**

*Interim (briefly used, superseded):* recalibrate the rate to **0.0008 per all-ages person/year**, chosen so the implied national count matched the published range while keeping the existing all-ages denominator. Rejected within the day on the reasoning that "rate × calibrated rate" is awkward to defend in Methods, and the right fix is to correct the denominator the rate references rather than rescale the rate. The 0.0008 value is preserved only as the low end of the rate-sweep sensitivity in S3.

*Adopted (current):* apply **0.001 per adult aged 20+ per year × block-group adult population aged 20+** sourced from ACS 2019–2023 5-year detailed table B01001 (Sex by Age). Adult cutoff is 20+, matching the NHANES adult definition that AHA uses to anchor STEMI rates. The adult population denominator is supplied by a new script, `national/src/01b_prepare_acs_age.py`, which pulls B01001 at block-group resolution from the Census Data API for 49 CONUS entities (48 contiguous states + DC), sums the 36 male+female age bands aged 20+, and writes a per-BG `adult_pop_20plus` column joined onto `zones_classified.parquet` in 06.

### D4 (amended-C) — STEMI rate and denominator

**0.001 STEMI per adult aged 20+ per year (AHA HDSS 2024) × adult population aged 20+ per block group (ACS 2019–2023 5-year, table B01001).**

```
headline_n_patients = Σ over BG where T2_PCI − T1_PCI ≤ 15 min:
                       adult_pop_20plus(BG) × 0.001
```

Sensitivity sweep on the rate at 0.0008, 0.0010, 0.0012 per adult/yr (covers ±20%) reported in S3 of the sensitivity table.

### Implication for the headline

National denominator: **248.3M CONUS adults aged 20+** → **248,269 implied STEMI/yr at 0.001**. This sits at the low edge of the AHA HDSS 2024 published 250–280k range (1,731 below the lower bound, 0.7% short), well inside the ±2% reproducibility-audit tolerance band. No calibration constant is in the chain; the rate and the denominator each come from independent published sources, and their product reproduces the published count without tuning.

Competitive-zone count (15-min margin): **196,253 STEMI/yr (79.0% of national STEMI)**. The 79.0% proportion is rate-invariant and carries through unchanged from earlier draft headlines.

### Bug caught and fixed pre-merge

The first run of `01b_prepare_acs_age.py` undercounted adults 20+ by approximately 10M nationally because the male and female age-band ranges started at B01001_010E and B01001_034E, silently dropping the single-year-of-age cohorts at 20 and 21 (B01001_008E/009E for males and B01001_032E/033E for females). The error surfaced as an implausibly low adult fraction (0.726 vs expected ~0.75). Same run also pulled all 50 states + DC, including Alaska and Hawaii, which the competitive-zone analysis universe excludes from CONUS. Both issues were fixed before the file was merged into `zones_classified.parquet`. The script docstring carries the variable-layout gotcha so a future editor does not reintroduce the off-by-two.

### Files affected

- New: `national/src/01b_prepare_acs_age.py`, `national/data/raw/acs5_2023/README.md` (with checksum), MANIFEST.md §5
- Modified: `national/src/06_classify_zones.py` (joins ACS adult population, uses it as the rate denominator), `07_aggregate.py` (state, county, hospital rollups now compute STEMI from adult population)
- Re-derived: `zones_classified.parquet`, `state_summary.csv`, `county_summary.csv`, `top_hospitals.csv`. Sensitivity table re-derivation is the next step (Amendment-D scope).

### Note on disclosure

The Amendment-B configuration (0.001 × all-ages) and the Amendment-C-interim configuration (0.0008 × all-ages) were each in the code for less than a working day and were never published or shared externally. They are recorded transparently because the audit trail's value depends on the absence of selective amnesia about methodological drafts.

## Amendment 2026-05-08-D — External validity locked

**Rationale:** Two facts about the pipeline must be defensible against the published U.S. literature, otherwise the competitive-zone claim built on them is not defensible: (1) the implied national STEMI count from rate × denominator must match the AHA HDSS-published range; (2) the drive-time engine must produce population-weighted access numbers that match the published Wang (2024) / Concannon (2014) estimates of the share of U.S. adults within a given drive-time of a PCI hospital. Both checks are now run automatically at the end of `06_classify_zones.py` with bands and a three-tier verdict scheme (`[OK]` inside the published band, `[OK*]` inside ±2% / ±2pp tolerance band, `[WARN]` outside both).

This amendment locks the validity-anchor numbers as a methodological commitment so they cannot be quietly revised after the headline is finalized.

### D10 (new) — External validity anchors

**Implied national STEMI count.** Computed = (adult_pop_20plus_total) × (rate). Published reference = AHA *Heart Disease and Stroke Statistics 2024*, 250,000–280,000/yr. Tolerance band ±2% = 240,000–285,000. Current value: **248,269/yr** (low edge of band, 1,731 from lower bound).

**Drive-time PCI access ladder.** Computed = % CONUS adults 20+ whose nearest Tier A hospital is within N min by OSRM drive time. Published references: Concannon et al. *Circ CVQO* 2014 (~80% within 30 min); Wang et al. *Circulation* 2024 (91–95% within 60 min); follow-on access studies (~96–98% within 90 min).

| Threshold | Computed | Published band | Tolerance band | Verdict |
|---|---|---|---|---|
| ≤ 30 min | **80.6%** | 78–82% | 75–85% | inside published band |
| ≤ 60 min | **94.2%** | 91–95% | 89–97% | inside published band |
| ≤ 90 min | **98.1%** | 96–98% | 94–99% | concordant; 0.1pp above published upper bound, well inside tolerance |

Median nearest-PCI drive time: **13.0 min** (IQR 7.6–26.5 min). Inside the published 11–15-min metro-weighted summary range.

The numbers above are locked. If a future change moves any of them outside its tolerance band, the validity check emits a `[WARN]` and the analyst must reconcile via either a methodological correction or a manuscript-text update. The check is in code (06_classify_zones.py) and the narrative record is in `notes/external_validity.md`.

### Implication for the manuscript

These two anchors are referenced in the abstract Background (the access-expansion narrative arc — Wang 2024) and in the Methods external-validity sentence. A reviewer at *Circulation: Cardiovascular Quality and Outcomes* who recomputes either anchor from the published sources will arrive at numbers within tolerance of ours.

### Files affected

- New: `national/notes/external_validity.md` (manuscript-ready narrative + Introduction and Methods text)
- Modified: `national/src/06_classify_zones.py` (External Validity Checks block at end of run); `REPRODUCIBILITY.md` (new D12 row pointing to both)

