# Paper 1; claim calibration

What Paper 1's analysis can and cannot honestly claim, given the descope to traffic-aware drive-time geometry only (`pre_registration.md` Amendment 2026-05-07-A). Filed to prevent drift during abstract drafting toward stronger claims than the analysis supports.

Written 2026-05-07.

---

## The three claim levels

### Weak claim; *supported by drive-time matrix alone*

> "Proximity-based routing is limited. The drive-time-shortest hospital is not always the geographically-closest hospital."

**What it requires:** the OSRM drive-time matrix. Nothing else.

**Why it's defensible:** OSRM operates on public OSM road network data; the drive-time computation is deterministic given the input. The claim is a tautology of the data: by construction, drive-time and proximity rankings differ for some block groups.

**What it doesn't say:** anything about *whether* routing to the alternative is operationally feasible, *whether* the alternative is clinically superior, or *how much* time savings would result.

### Medium claim; *supported by drive-time + Tier A classification + cross-state flagging*

> "A clinically meaningful population of U.S. STEMI patients resides in zones where the proximity-routing assumption misclassifies the drive-time-optimal destination among PCI-capable hospitals; the geographic substrate where institutional differences could plausibly determine optimal destination."

**What it requires:** drive-time matrix + Tier A status of both candidates + cross-state flag + STEMI incidence rate.

**Why it's defensible:** We restrict the analysis to PCI-capable hospitals only (Tier A by both candidates), so clinical equivalence at the routing level is assumed by construction. We separately report the cross-state subset, which clarifies the operational ceiling. We do not claim feasibility; we claim the substrate.

**What it doesn't say:** whether routing optimization is operationally implementable in any specific zone, whether the alternative center has D2B/capacity that justifies the route change, or what the actual ΔS2B would be once institutional performance is accounted for.

### Strong claim; *NOT supported by Paper 1's analysis alone*

> "Routing optimization in N% of U.S. competitive zones would reduce symptom-to-balloon time by an average of M minutes."

**What it would additionally require:** D2B and DIDO priors for every Tier A and Tier B hospital; exactly the work descoped to Paper 2.

**Why we don't make this claim in Paper 1:** the priors carry an attack surface (Mission:Lifeline coverage limits, type-based assumptions, the AMI-volume-as-PCI-volume substitution forced by the DRG 246/247 PUF gap). The descoped Paper 1 stands without those defenses.

---

## The headline sentence of Paper 1's Results

The abstract Results sentence(s) will quote *the medium claim*; not the weak claim, not the strong claim:

> "Across the United States, approximately [M] STEMI patients per year ([P]% of U.S. STEMI cases) live where a second PCI-capable hospital is reachable within 15 additional minutes of drive time beyond the nearest. For these patients, the default destination under current EMS proximity routing is not necessarily the fastest to reperfusion. In approximately [J]% of these areas, the alternative PCI-capable hospital is in a different state from the patient, where EMS mutual-aid agreements determine operational implementability."

(Note 2026-05-08: Earlier draft included an AM-peak flip sentence as a primary result; per Amendment 2026-05-08-A in `pre_registration.md`, time-of-day is reported as a sensitivity analysis only. Real time-aware routing is deferred to Paper 2.)

This frames the contribution at the medium-claim level: substrate + bounded operational subset + traffic dynamics.

## The Conclusion sentence

> "A clinically meaningful U.S. STEMI population (approximately [M] patients/year, [P]% of U.S. STEMI cases) lives where a second PCI-capable hospital is reachable within 15 additional minutes of drive time beyond their default destination, with implications for both EMS protocol design and Mission: Lifeline expansion targeting. Whether routing optimization is operationally feasible in any specific corridor depends on protocol authority, mutual-aid agreements, and institutional door-to-balloon and door-in-door-out performance; addressable in forthcoming work that integrates predictive models of these factors with the geographic substrate identified here."

Three pieces:
1. *What the analysis shows* (substrate exists, population is meaningful)
2. *What it implies* (EMS protocol + Mission: Lifeline targeting are appropriate audiences)
3. *What it does not show, with a clear handoff* (feasibility deferred to forthcoming work; Paper 2)

## What the abstract will *not* say

These are claims we explicitly do NOT make in Paper 1:

| Forbidden phrasing | Why |
|---|---|
| "EMS routing optimization would reduce mortality" | Causal claim outside the substrate analysis |
| "The optimal destination is hospital X for population Y" | Requires D2B priors (Paper 2) |
| "Routing optimization saves an average of N minutes per patient" | Requires D2B and DIDO priors |
| "Hospital systems should adopt routing protocols incorporating..." | Implementation recommendation outside our evidence base |
| "Patients are currently being routed sub-optimally" | Implies feasibility we have not established |
| "Time-to-balloon would decrease by ..." | Requires D2B priors |
| "The current routing system fails ..." | Implies blame for an outcome we have not measured |

The corresponding allowed phrasing in each case is the substrate-language form; "the substrate exists for X" rather than "X happens"; and is what the abstract uses.

## Anti-drift checklist for the abstract author (you, me, or future-you)

Before any Results or Conclusion sentence is finalized, ask:

1. Does this sentence's truth-value depend on D2B prior assumptions? If yes, it's Paper 2.
2. Does this sentence claim operational feasibility (would EMS actually do this)? If yes, it's outside the substrate analysis.
3. Does this sentence imply a measured outcome? If yes, it's a prospective study (Paper 3), not a substrate analysis.

If any answer is yes, rewrite to substrate-language form ("the substrate exists for...", "the population in zones where..., 'where institutional differences could plausibly determine...'").
