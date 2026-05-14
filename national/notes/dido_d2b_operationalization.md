# DIDO and D2B in the analysis; operational spec

> **Scope note (added 2026-05-07):** This document specifies the operational framework for **forthcoming Paper 2** in the research program (DIDO and D2B predictive modeling and integration with the routing decision). It is referenced in the Paper 1 abstract methods only as the prior-modeling step that the traffic-aware drive-time geography establishes the substrate for. The Paper 1 headline does not invoke any of the formulas, type-stratifications, or priors specified below. The document is preserved here because the methodology is sound and the work is the natural follow-up.



How door-in-door-out and door-to-balloon enter the modifiable-S2B (ΔS2B) calculation for every block group. Lives separately from `d2b_prior_plan.md` (which covers the *priors*; where the D2B numbers come from); this doc covers the *formula*; how those numbers are combined to produce ΔS2B per block group.

Written 2026-05-07.

---

## The Nallamothu decomposition we operate on

For a single STEMI patient at incident location P, the symptom-to-balloon (S2B) interval is:

```
S2B = T_symptom + T_FMC + T_transport_1 + (DIDO + T_transfer + T_intake)? + D2B
```

Where the parenthesized group applies only when the first hospital is a non-PCI facility. Nallamothu et al. (2005) measured each segment empirically; we treat them as deterministic given the input network.

For our analysis we compress to:

- **T_symptom + T_FMC + T_intake** are *constant across routing choices for the same patient*. They cancel out in any comparison. We don't model them.
- **T_transport_1** is the EMS drive time from incident to first hospital. Computed via OSRM.
- **T_transfer** is the inter-facility drive time from first hospital (Tier B) to receiving Tier A. Also via OSRM.
- **DIDO** is the time spent at the first hospital before departure for the PCI center. Plugged in from a type-stratified prior (below).
- **D2B** is the time from PCI-center arrival to balloon inflation. Plugged in from the three-layer prior in `d2b_prior_plan.md`.

---

## Two scenarios per block group

For each block group centroid, we compute two routing outcomes:

### Scenario A; Direct routing to nearest Tier A

Patient transported straight from incident to nearest Tier A hospital, bypassing any closer Tier B.

```
S2B_direct(BG) = drive(BG → T1_PCI) + D2B(T1_PCI)
```

Where `T1_PCI` is the nearest Tier A hospital to the block group.

### Scenario B; Proximity routing (current EMS default)

Patient transported to nearest hospital, regardless of tier. If that hospital is Tier B, DIDO + transfer drive + D2B at the receiving Tier A follow.

```
if nearest(BG) is Tier A:
    S2B_proximity = drive(BG → nearest) + D2B(nearest)
    # equals S2B_direct; routing optimization adds nothing here

if nearest(BG) is Tier B:
    S2B_proximity = drive(BG → nearest_B) + DIDO(nearest_B) + drive(nearest_B → nearest_A_from_B) + D2B(nearest_A_from_B)
```

`nearest_A_from_B` is the nearest Tier A hospital from the *Tier B intermediate stop*; not necessarily the same as `T1_PCI` from the patient's location.

---

## The headline metric

```
ΔS2B(BG) = S2B_proximity(BG) − S2B_direct(BG)
```

Three regions in (S2B_proximity, S2B_direct) space:

- **ΔS2B = 0**; nearest is Tier A. No routing decision; no opportunity. (Most of the population in metropolitan PCI corridors.)
- **ΔS2B > 0**; nearest is Tier B and the DIDO chain takes longer than direct transport to the nearest Tier A. *Routing optimization helps here.* This is the modifiable-burden population.
- **ΔS2B < 0**; nearest is Tier B but DIDO + short transfer is faster than direct transport (because the nearest Tier A is far). *Current proximity routing is already optimal.* Important: don't rule against the existing protocol where it's actually right.

The headline finding is the population-weighted sum of `ΔS2B(BG) × population(BG) × STEMI_incidence_rate` across all BGs where ΔS2B ≥ a clinically meaningful threshold (15 min primary).

---

## Two distinct competitive populations

The proposal language sometimes blurs these; explicit separation here:

### Population 1; Tier A vs Tier A choice

Block groups where both T1 (nearest hospital) and T2 (second-nearest) are Tier A and the drive-time difference is ≤15 min. The routing question is *which PCI center*; answered by D2B differential between the two candidates.

```
ΔS2B = D2B(T1_A) − D2B(T2_A)         if D2B(T1_A) > D2B(T2_A) by enough
                                       to overcome the small drive-time penalty
```

This is the "competitive catchment zone" framing in §4 of the proposal. Driven by D2B differential. Modest individual ΔS2B (typically 10–25 min); large aggregate effect because of the population concentration in multi-PCI metros.

### Population 2; Tier B bypass to direct Tier A

Block groups where T1 (nearest) is Tier B and T1_PCI (nearest Tier A) is reachable directly within a clinically reasonable transport time. The routing question is *whether to bypass the closer non-PCI hospital*; answered by DIDO + transfer drive vs direct transport plus D2B.

```
ΔS2B = DIDO(T1_B) + drive(T1_B → T1_A_from_B) − [drive(BG → T1_A) − drive(BG → T1_B)] − D2B_diff
```

In practice the DIDO term dominates; field-ECG-eligible STEMI patients in this population gain ~30–60 min by direct routing.

This is the larger ΔS2B per patient but smaller population. Often rural/suburban; the corridors where pre-hospital ECG protocols make a difference.

The analysis reports ΔS2B aggregates separately for the two populations so the policy implications stay distinct: Population 1 needs hospital-D2B-aware routing protocols; Population 2 needs pre-hospital ECG + bypass authority.

---

## DIDO type stratification

DIDO is plugged in by hospital type. Values from Fordyce et al. JAMA Cardiol 2017 and supporting literature:

| First-hospital type | DIDO median (min) |
|---|---|
| Academic ED (bed_cnt ≥ 300, urban RUCA ≤ 3) | 60 |
| Community ED (bed_cnt 100–299, any RUCA) | 68 |
| Critical access hospital (subtype 11) | 90 |
| Free-standing ED, specialty hospital | excluded from analysis |

The 90-minute CAH DIDO reflects the literature on rural-hospital STEMI transfer: longer because of helicopter/ground EMS coordination overhead, smaller staff pools, and longer pre-transfer stabilization. The 60-minute academic figure reflects the Fordyce subset where hospitals had explicit STEMI-transfer protocols.

Sensitivity analysis: re-run with uniform DIDO = 68 min for all Tier B hospitals.

## D2B layered prior

Cross-reference: see `d2b_prior_plan.md`. Three-layer cascade:

1. AHA Mission: Lifeline reported median where available
2. Type-based prior anchored to bed count + RUCA + AMI tertile
3. Sensitivity at uniform 80 min

---

## Sensitivity analyses required for any reported ΔS2B finding

1. **Uniform DIDO** (68 min for all Tier B); does the headline ΔS2B survive without the type-stratified DIDO?
2. **Uniform D2B** (80 min for all Tier A); does it survive without the layered D2B prior?
3. **CAH DIDO at 60, 90, 120 min**; three-point sensitivity on the largest single tier-stratification value
4. **Drop ΔS2B contribution from `precision_tier in {zip_centroid, zip_prefix}`**; does the headline survive on street-level-geocoded hospitals only?
5. **Threshold sweep**; competitive margin at 10 / 15 / 20 min; ΔS2B threshold at 10 / 15 / 30 min for the headline count
6. **Population 1 and Population 2 reported separately**; do both populations yield a positive routing-optimization opportunity, or is the headline driven by one of them?

The point of running all six is that the abstract sentence; "*N* million U.S. residents live in zones where EMS routing optimization would shorten symptom-to-device time by ≥15 minutes"; should hold under at least four of the six. If it doesn't, the headline is a fragile artifact of one assumption.

---

## What this lets us write in the abstract

> "Two routing-optimization populations were identified: block groups where two PCI-capable hospitals lie within a 15-minute drive of each other and the institutional D2B differential exceeds a clinically meaningful threshold (Population 1, 'competitive catchment zones'), and block groups where the geographically nearest hospital lacks PCI capability and direct transport to a Tier A center would bypass the door-in-door-out interval (Population 2, 'DIDO-bypass zones'). Population-weighted ΔS2B was computed for each, with DIDO and D2B values from Fordyce et al. and AHA Mission: Lifeline respectively, and sensitivity analyses confirming the result is robust to the prior-assignment strategy."

That sentence answers "how does the analysis use DIDO and D2B" without spending more than 100 words.
