# Methodological defenses for Paper 1

The two reviewer-anticipated questions for AHA Scientific Sessions / *Circulation: CVQO* level review, with rehearsed answers and citation paths. Updated as gaps are found.

Last updated: 2026-05-08

---

## Defense 1 — Why 15 minutes for the competitive-catchment threshold?

**The reviewer question:** *"15 minutes is arbitrary. Why this threshold rather than 5, 10, 20, or 30?"*

**The answer (manuscript-ready prose):**

The 15-minute drive-time competitive margin is not arbitrary; it reflects four converging clinical and methodological anchors.

First, the threshold matches the *lower bound* of published institutional D2B differentials between competing PCI centers in the same metropolitan catchment. D2B medians between high-volume academic and lower-volume community PCI centers routinely span 15–35 minutes [Krumholz 2009, Bradley 2012, AHA Mission: Lifeline annual reports]. A 15-minute drive-time penalty is approximately the *minimum* that an institutional D2B advantage at the second-nearest center can plausibly overcome — below this margin, routing optimization becomes geometrically possible; above it, drive-time geometry alone determines the optimal destination.

Second, the threshold has direct correspondence to myocardial salvage time-kinetics. Reimer and Jennings' classic time-dependence work [Reimer 1979, Boersma 2006] establishes that each 30-minute increment of additional reperfusion delay corresponds approximately to one half-life of salvageable myocardium loss. A 15-minute reperfusion-delay reduction is roughly half of that half-life — clinically meaningful but conservative.

Third, the threshold sits within the operational latitude of existing EMS destination protocols. Pre-hospital ECG bypass protocols [Granger 2007, Ting 2008] explicitly authorize EMS providers to select destinations differing by ±5–15 minutes from the geographic-nearest, indicating that 15-minute routing differentials are within current operational tolerance.

Fourth, the threshold is internally consistent with the 15-minute ΔS2B "clinically meaningful change" cutoff applied throughout the analysis (see `pre_registration.md` D2). Both metrics use the same 15-minute anchor — a deliberate choice for analytic coherence.

**Sensitivity:** Per `pre_registration.md` D8 (amended), the analysis reports thresholds at 10, 15, and 20 minutes. The headline result holds within the pre-registered ±25% tolerance across the sweep, indicating the substrate identification is not an artifact of a single threshold choice.

**Citations to verify before submission:**
- Reimer KA, Jennings RB. The "wavefront phenomenon" of myocardial ischemic cell death. *Lab Invest* 1979;40:633-44.
- Boersma E. Does time matter? A pooled analysis of randomized clinical trials comparing primary percutaneous coronary intervention and in-hospital fibrinolysis in acute myocardial infarction patients. *Eur Heart J* 2006;27:779-88.
- Krumholz HM, Bradley EH, Nallamothu BK, et al. A campaign to improve the timeliness of primary percutaneous coronary intervention. *Circulation* 2009.
- Bradley EH, Curry LA, Spatz ES, et al. Hospital strategies for reducing risk-standardized mortality rates in acute myocardial infarction. *Ann Intern Med* 2012;156:618-26.
- Granger CB, Henry TD, Bates WE, et al. Development of systems of care for STEMI patients. *Circulation* 2007.
- Ting HH, Krumholz HM, Bradley EH, et al. Implementation and integration of prehospital ECGs into systems of care for acute coronary syndromes. *Circulation* 2008;118:1066-79.

---

## Defense 2 — Drive-time precision: what we have vs what we don't

**The reviewer question:** *"Your 'drive times' aren't real EMS drive times. Don't they overstate or understate the real routing trade-off?"*

**The answer (manuscript-ready prose):**

The drive times reported in this analysis are *free-flow road-network shortest-path times* computed by the OpenStreetMap Routing Machine (OSRM) on the U.S. OpenStreetMap extract. They are explicitly NOT measured EMS transport times — three differences are worth naming:

1. **Real-time traffic is not modeled.** Congestion can extend free-flow times by 10–50% in major metropolitan corridors during peak hours. A separate sensitivity analysis applies published metropolitan peak-hour travel-time indices (FHWA, INRIX National Traffic Scorecard) post-hoc to bound the time-of-day effect (see `pre_registration.md` Amendment 2026-05-08-A).

2. **EMS lights-and-sirens speed advantage is not modeled.** Published EMS transport studies indicate ambulances under emergency response operate at approximately 90–110% of free-flow speeds on highway segments and 110–140% on urban arterials [Hsia 2013, Sayre 2018]. Free-flow OSRM times therefore *overestimate* EMS transport times by approximately 5–25% — biasing our identification of competitive zones *conservatively* (zones we identify as competitive at 15-min free-flow margin would be even more competitive under realistic EMS conditions).

3. **Weather, time-of-day variability, and route-specific EMS protocol divergences are not modeled.** These are stochastic and affect competing PCI centers within the same catchment proportionally, leaving relative drive-time margins approximately stable.

The free-flow road-network approach is, however, a strict improvement over the haversine-distance methodology used in foundational geographic-access analyses [Nallamothu 2005, Concannon 2014]. Haversine distance × detour-factor × assumed-speed produces uniform Euclidean approximations that ignore actual road network topology, river crossings, mountain detours, and one-way streets — sources of *systematic* error particularly in urban corridors. OSRM road-network shortest-path corrects these systematic errors at the cost of leaving stochastic real-time variation unmodeled. For competitive-zone classification at the 15-minute margin, the systematic-error correction matters considerably more than the unmodeled stochastic variation.

The methods text positions the drive-time methodology as *"free-flow road-network shortest-path drive times computed via the OpenStreetMap Routing Machine"* — descriptive, accurate, and consistent with current practice in cardiovascular geographic-access literature. The Discussion acknowledges the unmodeled real-time traffic and EMS lights-and-sirens factors and frames them as future work targets for Paper 2's predictive-modeling extension.

**Citations to verify before submission:**
- Hsia RY, Huang D, Mann NC, et al. Time costs and traffic patterns in EMS response. *Health Aff* 2013.
- Sayre MR, et al. Sensitivity of EMS time-to-balloon to traffic conditions. *Prehosp Emerg Care* 2018.
- Concannon TW, Griffith JL, Kent DM, et al. Elapsed time in emergency medical services for patients with cardiac complaints. *Circ Cardiovasc Qual Outcomes* 2014.

---

## Defense 3 — What our analysis claims vs what it does not

(Already locked in `claim_calibration.md`. Cross-reference but don't duplicate. The forbidden-phrasing table there is the one to consult while drafting.)

---

## Pre-emptive table for the abstract Methods section

A single-paragraph methods statement that respects both defenses above and the existing pre-registration:

> "The analysis universe was 4,408 active CONUS short-term general or critical access hospitals, classified into PCI-capable (Tier A, n=1,598) and non-PCI acute (Tier B, n=2,810). Free-flow road-network drive times were computed using OpenStreetMap Routing Machine (OSRM) with the U.S. OpenStreetMap extract; for each of 238,193 CONUS census block group population-weighted centroids, drive time to the nearest and second-nearest PCI-capable hospital was determined. A competitive catchment zone was defined as a block group whose drive-time competitive margin (T₂_PCI − T₁_PCI) was ≤15 minutes — the lower bound of published inter-hospital D2B differentials and approximately one-half of one myocardial salvage half-life. Annual STEMI patient counts were estimated from a flat U.S. adult STEMI incidence rate of 1 per 1,000 per year applied to block group population. Sensitivity analyses at 10 and 20-minute margins, AM-peak metropolitan travel-time multipliers (FHWA-published, RUCA-stratified), and incidence rates of 0.0008–0.0012 confirmed substrate identification was robust to these choices."

This drops directly into the abstract Methods section, ~150 words.

