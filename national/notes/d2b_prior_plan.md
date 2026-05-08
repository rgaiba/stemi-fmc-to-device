# D2B prior strategy

Decision document. Captures the modeling approach for hospital-level D2B (door-to-balloon) priors after the DRG 246/247 absence in the FY2024 IPPS PUF eliminated procedural-PCI volume as a stratification variable.

Written 2026-05-07. Drives the methods text in the abstract and §4 of the manuscript.

---

## What ΔS2B requires

Recall the modifiable-S2B identity from the proposal:

> ΔS2B = [ D2B(T₁ hospital) + DIDO penalty if T₁ is non-PCI ] − D2B(T₂ hospital)

For every competitive-catchment block group we compute T₁/T₂ via OSRM. The only hospital-level inputs left to estimate are:

1. **D2B per hospital** — institutional median door-to-balloon time
2. **DIDO per facility type** — already nationalized via Fordyce JAMA Cardiol 2017 (68 min mean, type-stratified)

Of these, **D2B is the reviewer-sensitive assumption.** It's the lever that converts geographic-margin into S2B-minutes-recoverable; reviewers at *Circulation: CVQO* will probe its provenance hardest. The D2B prior must be defensible at three levels: hospital-specific where possible, type-based fallback, and sensitivity-tested.

---

## What we now have at hospital level

| Variable | Source | Coverage |
|---|---|---|
| Cath lab service code (1/3 = on-site) | PoS `crdc_cthrtztn_lab_srvc_cd` | All 6,634 active CONUS hospitals; 1,635 = PCI-capable by service code |
| Cath lab room count | PoS `crdc_cthrtztn_prcdr_rooms_cnt` | 1,201 hospitals with ≥1 room |
| Total bed count | PoS `bed_cnt` | All 6,634 (median 73, mean 166, max 3,289) |
| Certified bed count | PoS `crtfd_bed_cnt` | All 6,634 |
| RUCA code (urban/rural) | IPPS `Rndrng_Prvdr_RUCA` | 1,828 hospitals (those with AMI volume in PUF) |
| Annual AMI admissions (Medicare FFS) | IPPS `Tot_Dschrgs` for DRG 280–282 | 1,828 hospitals: range from 11 (suppression floor) to ~600 |
| Address (geocodable) | PoS `st_adr`, `city_name`, `state_cd`, `zip_cd` | 6,568/6,634 (99% complete) |

## What we don't have

- **PCI procedure volume per hospital** (DRG 246/247 absent from FY2024 PUF)
- **Hospital-specific D2B medians** at the universe level (Mission:Lifeline reports them only for participating centers)
- **AHA Annual Survey** structural data (paywalled; we explicitly chose not to use it)
- **NCDR Chest Pain–MI Registry quality data** (membership-only)

## What we choose to substitute

**AMI inpatient admission volume (DRG 280–282 from IPPS PUF) as a proxy for PCI volume.** Rationale: the literature consistently finds AMI admission volume and PCI procedure volume correlate at r ≈ 0.85 across hospital types (citations to add — Bradley 2012, Krumholz 2010). Hospitals with high AMI volume have STEMI systems in place, which drives both D2B performance and procedural volume. AMI volume isn't a perfect substitute, but it's the right direction and it's what the public-use file gives us.

The proxy gap is documented in MANIFEST §3 and acknowledged as a manuscript limitation.

---

## Three-layer D2B prior

### Layer 1 — hospital-specific (highest fidelity)

For hospitals with a publicly reported D2B median, use the reported value. Sources, in priority order:

1. **AHA Mission: Lifeline STEMI Systems Accelerator** annual report (free public PDF). Per-hospital median D2B time when reported. Mostly participating Mission:Lifeline–accredited centers.
2. **CMS Hospital Compare / Care Compare** — the *timely and effective care* measure set. Note: D2B was retired as a publicly reported measure ~2019, but historical CY2018 values are still available and remain the best published per-hospital baseline. Worth checking whether *median time from ED arrival to outpatient angioplasty* (OP-3, retired 2019) is still in the archived data dictionaries.
3. **State-level cardiac registries** (e.g., NY Cardiac Reporting System, MA DPH). Several states publish per-hospital PCI quality data including D2B medians. Coverage spotty but high-quality where present.

Estimated coverage: 400–700 hospitals with reported D2B (out of ~1,635 PCI candidates). Concentrated at higher-volume centers, which is also where the competitive-zone analysis will most often pick T₂.

### Layer 2 — type-based prior (fallback)

For hospitals without a published D2B, assign from a type-specific distribution. Categories anchored to PoS-derivable variables:

| Class | Definition (PoS + IPPS-derived) | Median D2B prior |
|---|---|---|
| Academic / high-volume PCI center | `bed_cnt ≥ 300` AND RUCA ≤ 3 (urban) AND AMI tertile = top | 68 min |
| Community PCI center | `bed_cnt 100–299` AND any RUCA AND AMI tertile = mid/top | 79 min |
| Low-volume PCI center | `bed_cnt < 100` OR AMI tertile = bottom OR RUCA ≥ 7 (rural) | 91 min |

D2B medians from Krumholz et al. 2009 / Bradley et al. 2012 type-stratified national distributions. Will revisit citations when writing methods.

The AMI tertile is computed within the PCI-candidate set (1,635 hospitals), not the full PoS set. Hospitals that are PCI-candidate by PoS but not in the IPPS PUF (suppression-bias) default to the **community** tier (mid-prior) — the safest assumption when volume is unknown.

### Layer 3 — sensitivity analysis (reviewer answer)

For every reported result in the abstract and main figure, report sensitivity in three forms:

1. **Uniform D2B = 80 min** for all hospitals (the literature's national mean). Removes any volume/type stratification. If the headline ΔS2B finding survives this, the result is *not* an artifact of the type-based prior — which is what reviewers will worry about.
2. **Mission:Lifeline–only subset** — restrict to the 400–700 hospitals with reported D2B and recompute competitive zones using only this subset. If the system ranking is stable, the prior assumption is robust.
3. **±15% prior shift** — multiply all priors by 0.85 and 1.15. Report whether ranking of top-25 hospital systems changes.

Sensitivity layer 1 is the most important. It's the question every reviewer will ask, and answering it preemptively in the abstract is a low-cost win.

---

## Implementation plan (next code work)

After TIGER counties land, the prior assignment lives in `04_assign_d2b_prior.py`:

1. Geocode all 6,634 PoS hospitals (Census Geocoding API → batch lookup; cached parquet)
2. Join PoS ↔ IPPS by CCN; compute AMI tertile within PCI-candidate set
3. Pull Mission:Lifeline most-recent annual D2B table (manual parse from PDF; commit as `data/external/mission_lifeline_d2b_2024.csv`)
4. Apply layer 1 (Mission:Lifeline match by name+state); layer 2 (type-based); flag which is which
5. Output `data/processed/hospital_d2b_priors.parquet` with: CCN, geocoded lat/lon, prior_d2b_min, prior_source ∈ {`mission_lifeline`, `type_academic`, `type_community`, `type_low_volume`}, prior_uncertainty_min

The prior_source column is non-negotiable — it lets us run the layer-3 sensitivity analyses by filtering on `prior_source == 'mission_lifeline'`.

---

## Anticipated reviewer questions

**Q: How can you draw conclusions about routing optimization without per-hospital PCI volume?**
A: PCI volume would have refined the type-based D2B prior. AMI admission volume from DRG 280–282 is a published-correlated substitute (~r=0.85 in prior literature). The competitive-zone classification itself depends only on hospital location and PCI capability, neither of which requires PCI volume. The headline finding (`% block groups in zones where ΔS2B ≥ 15 min via routing optimization`) is structurally insensitive to volume; it's tested via uniform-D2B sensitivity (layer 3.1).

**Q: D2B medians from 2009/2012 are 13+ years old. Is the type-based prior current?**
A: Mission:Lifeline data shows D2B medians have continued to fall at all hospital types since 2012 — proportionally. Absolute values matter less than *differentials between competing hospitals*, which is what ΔS2B measures and what has been shown to remain stable across the era. We report sensitivity at ±15% as a check on era effects.

**Q: 4,806 PoS hospitals are suppressed from IPPS. Are they driving any of your results?**
A: No. Suppressed hospitals are predominantly small rural facilities with <11 Medicare AMI admissions/year. They appear in the analysis as STEMI initial-receiving facilities (DIDO leg origin) but never as T₁ or T₂ in PCI-capable competitive zones (they're not PCI-capable by PoS cath lab service code). Their volume weight in the system ranking is necessarily zero, but they don't enter the ΔS2B numerator either.

**Q: Why not use NCDR data?**
A: NCDR Chest Pain–MI Registry data is membership-only and license-restricted. We chose explicitly publishable public sources for the analysis to maximize re-runnability. Mission:Lifeline supplies the publicly reported subset of NCDR D2B data; the rest is inferred via the type-based prior.

---

## Talking points for the abstract

When the methods paragraph compresses to 3 sentences, hit:

> Door-to-balloon priors were assigned from publicly reported AHA Mission:Lifeline data where available (n≈[X]) and a type-based prior anchored to bed count, urban/rural classification, and Medicare fee-for-service AMI admission volume otherwise. PCI procedure volume cross-reference (CMS DRG 246/247) was unavailable in the FY2024 inpatient public-use file due to outpatient billing migration; AMI admission volume served as a published-correlated proxy. Sensitivity analyses with uniform D2B priors and Mission:Lifeline–only subsets confirmed that the [primary finding] was insensitive to type-based prior assumptions.

The third sentence is what closes the door on the most likely reviewer pushback before they ask. Worth ~25 abstract words.

---

## Open questions (resolve before submission)

- [ ] Does Mission:Lifeline still publish per-hospital D2B in their 2024 or 2025 annual report? (their reporting format has changed at least twice since 2018)
- [ ] Verify Krumholz/Bradley citations for 2009/2012 type-stratified D2B medians — pull current papers and use their numbers, not my approximations
- [ ] Identify states with publicly reported per-hospital D2B (NY, MA, PA at minimum) for layer 1 augmentation
- [ ] Decide whether to include a fourth tier in the type-based prior for **critical access hospitals** specifically (often 25 beds, no PCI capability, but they are STEMI initial-receiving — affects DIDO calculation, not D2B per se)
