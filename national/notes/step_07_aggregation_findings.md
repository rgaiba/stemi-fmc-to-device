# Step 7; Aggregation findings and abstract-locked secondary results

Date: 2026-05-08

## What ran

`07_aggregate.py` against `zones_classified.parquet` (238,193 BGs) and
`hospitals_classified.parquet` (4,408 hospitals).

Outputs (all in `national/data/processed/`):

- `state_summary.csv`; per-state competitive-zone breakdown (49 rows)
- `county_summary.csv`; per-county BG counts and competitive-zone % (3,108 CONUS counties)
- `top_hospitals.csv`; Tier A hospitals ranked by competitive-zone STEMI catchment

## Headline numbers (confirmed at this step, all using 0.001 STEMI rate per Amendment 2026-05-08-B)

- **Total CONUS:** 238,193 BGs · 329.3 M population · 329,260 STEMI/yr
- **In 15-min competitive zones:** 185,270 BGs (77.8%) · 260.5 M (79.1%) · ~260,549 STEMI/yr
- **Cross-state competitive zones:** 6,849 (3.7% of 15-min zones); operational caveat for EMS mutual-aid

## Per-state findings

Top 5 states by competitive-zone STEMI/yr (account for 41.4% of national substrate):

| State | % of state pop in zones | STEMI/yr in zones | Cross-state BGs |
|---|---|---|---|
| CA | 86.1% | 34,052 | 254 |
| TX | 90.6% | 26,403 | 72 |
| FL | 85.1% | 18,335 | 51 |
| NY | 87.4% | 17,660 | 244 |
| IL | 88.8% | 11,374 | **553** |

Cross-state subset clusters predictably: IL (553) > GA (549) > OH (502) > PA (360) > NY (244). These are state-line corridors where Chicago/Atlanta/Cincinnati metros span borders.

NJ has the highest *percentage* (92.1%); densest competitive geography in the country.

## County-level distribution (feeds choropleth)

Bimodal:
- p25: 10.5%
- p50: 66.7%
- p75–p100: 100%

Most counties are either nearly fully in competitive zones (urban/suburban) or have <10% (exurban/rural). The choropleth will show striking gold/red density in metro corridors and pale empty space in between; methodologically clean visual.

## The top-25 hospitals finding (locked for abstract Option A)

**Top 25 PCI-capable hospitals serve only 7.5% of competitive-zone STEMI catchment** (~19,500 of 260,549 STEMI/yr).

The other 92.5% is distributed across the remaining ~1,550 Tier A hospitals serving competitive zones.

This is the central methodological-and-policy finding beyond the headline. It rebuts the "concentrate intervention at top systems" interpretation and supports the broader policy message: *system-wide EMS routing protocol design; every PCI hospital needs the routing-aware protocol, not just the famous ones.*

## Decision: Option A; include the top-25 finding as abstract Results sentence

Drop-in sentence (~50 words):

> "Even the 25 PCI-capable hospitals that are the default destination for the largest number of these patients together account for only 7.5% of this national population; the remainder is distributed across approximately 1,550 hospitals. System-wide EMS routing protocol design; rather than facility-level intervention at flagship hospitals; is the natural target for Mission: Lifeline expansion."

This becomes the second sentence of the Results paragraph in the abstract draft. Preempts the "you just identified zones near the academic centers" reviewer challenge with empirical force.

## What's locked for downstream steps

- Headline metric: ~260,000 STEMI/yr in 15-min competitive zones (79% of national STEMI)
- Secondary: 7.5% top-25 concentration → distributed-substrate finding
- Cross-state subset: 6,849 BGs (3.7%) for the operational-caveat footnote
- County-level data ready for choropleth
- Top-state ranking (CA/TX/FL/NY/IL) for the geographic-anchor sentence

## Anti-drift check

Verifying against `pre_registration.md` D9 forbidden phrasings:

- ✓ Headline phrased as substrate identification, not routing recommendation
- ✓ "7.5% of catchment" framed as geographic distribution, not "top hospitals are the targets"
- ✓ No causal claim about S2B reduction (Paper 2)
- ✓ No operational-feasibility implication beyond the cross-state caveat

All clear.
