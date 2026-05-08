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
