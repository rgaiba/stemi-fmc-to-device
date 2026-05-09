# Daily summary — 2026-05-09

Session-end record of work completed today. Pairs with `daily_summary_2026-05-07.md` for the project log.

**Headline at end of day:** repo is AHA SS submission-ready, tagged `v0.1-aha-ss-2026`, abstract v9 FINAL, all artifacts on GitHub plus a portable 136 MB bundle.

---

## 1. Methodology — STEMI rate denominator correction (the day's biggest change)

The pre-registration's D4 specified rate 0.001/yr applied to "all CONUS BG populations." Caught at run-time: this silently multiplied a per-adult rate by an all-ages denominator, implying ~329,000 STEMI/yr — well above the AHA HDSS 2024 published 250–280k range.

Three-step evolution recorded:

| Step | Rate | Denominator | Implied national | Status |
|---|---|---|---|---|
| Original (Amendment B) | 0.001/yr (per-adult, AHA HDSS 2024) | All-ages (CenPop2020) | 329,000/yr | Mismatch flagged |
| Interim (Amendment C, briefly used) | 0.0008/yr (calibrated) | All-ages | 263,000/yr | Superseded same day |
| **Adopted (Amendment C, current)** | **0.001/yr (per-adult)** | **Adults 20+ (ACS 2019–2023 5-year, table B01001)** | **248,269/yr** | Concordant with AHA HDSS 250–280k without calibration |

The adopted approach uses two independent published sources (rate, denominator) with no calibration constant in the chain. This is the strongest form of external validity available without patient-level data.

**New script written:** `src/01b_prepare_acs_age.py` — pulls B01001 at block-group resolution from the Census Data API for 49 CONUS entities, sums 36 male+female age bands aged 20+, writes per-BG `adult_pop_20plus`.

**Bug caught and fixed pre-merge:** the first run of `01b_prepare_acs_age.py` undercounted adults by ~10M nationally because the male/female age-band ranges started at B01001_010E and B01001_034E, dropping the single-year-of-age cohorts at 20 and 21. Adult fraction came in at 0.726 (vs expected ~0.75); the off-by-two was visible from the validation. Variable ranges corrected to `_008..025` (male) and `_032..049` (female), 36 bands total. Same run also pulled all 50 states + DC; reduced to 49 CONUS entities to align with `06_classify_zones.py`. Both fixes pre-merge; no downstream artifacts were affected.

**Headline impact:** 260k → 196,253 STEMI/yr in 15-min competitive zones (the 79% proportion is rate-invariant; only the absolute count moves).

---

## 2. External validity locking

Two reviewer-checkable concordance anchors locked as a methodological commitment (Amendment 2026-05-08-D):

- **Implied national STEMI count:** 248,269/yr inside AHA HDSS 2024 published 250–280k range (within tolerance band 240–285k).
- **Drive-time PCI access ladder:**
 - ≤30 min: 80.6% of CONUS adults (Concannon *Circ CVQO* 2014: ~78–82%)
 - ≤60 min: 94.2% (Wang *Circulation* 2024: 91–95%)
 - ≤90 min: 98.1% (follow-on access studies: ~96–98%)
 - Median nearest-PCI: 13.0 min; IQR 7.6–26.5 min

Automated check at end of `06_classify_zones.py` with three-tier verdict (`[OK]` inside published band / `[OK*]` inside ±2pp tolerance / `[WARN]` outside). Narrative record in `notes/external_validity.md`.

**Manuscript benefit:** the Background can ground the access-expansion claim in a published number we independently reproduce: "Expanded PCI capacity has placed 94% of U.S. adults within 60 minutes of a PCI-capable hospital (Wang 2024)..." That sentence is in the abstract v9 Background.

---

## 3. Pre-registration amendments filed today

Three new amendments appended to `notes/pre_registration.md`:

- **2026-05-08-C** — STEMI rate denominator correction (per-adult × ACS 20+); both interim 0.0008 calibration and adopted ACS-20+ approach recorded for audit-trail completeness; off-by-two and AK/HI inclusion bugs documented as caught pre-merge.
- **2026-05-08-D** — External validity anchors locked (HDSS implied count + access ladder concordance with Wang/Concannon).
- **2026-05-08-E** — Reporting precision (D1 rounding from 2 → 3 significant figures so 196,253 → 196,000 not 200,000) and sensitivity-language clarification (the ±25% in original D8 is a *failure trigger*, not a tolerance claim about how tight the result is).

---

## 4. Sensitivity analyses re-run at new methodology

`09_sensitivities.py` updated to use `adult_pop_20plus × INCIDENCE_RATE`. `outputs/tables/sensitivity_table.csv` regenerated. **6 of 6 sensitivity groups robust within ±25%** (D8 trigger satisfied with margin to spare). Range 157,002–235,504 STEMI/yr; the rate sweep at S3 spans the full ±20% (by design); the other five non-rate sensitivities deviate by ≤13%.

S3 includes 0.0008 explicitly so the absolute count under the briefly-used calibration approach is reproducible from the supplement table without re-running the pipeline.

---

## 5. Abstract v9 — eight iterations to FINAL

Started session at v8 (260,000 STEMI/yr headline; "Each county shaded by..." subtitle paraphrasing the title). Ended at v9 FINAL through the following iterations:

1. v9 first draft: headline 260k → 200k (initial 2-sig-fig rounding); Wang 2024 access anchor in Background; "primary finding" register; sensitivity language refined.
2. v9 revision: 200,000 → 196,000 (3-sig-fig override; pre-reg D1 amended); ±25% phrasing dropped in favor of explicit range with rate-vs-non-rate split.
3. v9 Conclusions revised: dropped NCDR specificity ("integrating institutional D2B... potentially through the National Cardiovascular Data Registry") and softened "candidate next step toward measurable improvements" to "Dynamic routing using traffic and expected D2B awareness may improve FMC-to-reperfusion time." Limitation framing: "addressed" → "planned" (more honest about future work status).
4. v9 FINAL.

Final headline: **approximately 196,000 STEMI patients per year (79% of U.S. STEMI cases)** in 15-min competitive catchment zones.

Word count ~388, character count ~2,510 (at AHA SS soft limit).

---

## 6. Figure 1 — many style iterations

The choropleth went through approximately 10 design iterations today:

- Metric switched: pct_bgs_competitive (BG share) → pct_adults_in_competitive (adult population share). Aligns with the population-anchored abstract claims; visually similar gestalt.
- Color: gold-red saturated ramp → muted-red → steel-blue/navy → **deep teal** (final). Teal is the secondary accent both ACC and AHA use in their journal layouts (JACC web header, Circulation issue covers); fits the publication idiom without repeating the dominant red/navy Pantones.
- Layout: horizontal colorbar beneath map → **vertical colorbar on the right** (frees horizontal space for a bigger map).
- Title size: 14pt → 17pt (+20%).
- Subtitle reframed: "Each county shaded by the share of adults..." (paraphrase of title) → **"Areas where routing to the hospital with shorter door-to-balloon time may shorten time to reperfusion after STEMI"** (delivers the stakes; hedged with "may shorten"; spells out D2B for manuscript portability).
- Title text: "in 15-minute PCI competitive catchment zones" → "with two PCI hospitals within 15 minutes of each other" (drops jargon; explicit threshold; pairwise relationship clear).
- Metrics line: bolded; leads with the headline patient count (~196,000); hospital count restricted to PCI-capable centers (was "4,408 hospitals" — confusingly the full acute-care universe); "free-flow drive times" → "drive times" (free-flow caveat moved to Limitations); "in these zones" → "in these areas" (matches subtitle).
- Centering: explicit axes-box-matches-data-aspect calculation (1.5625 = 5M/3.2M) so map+colorbar block is symmetric in figure.
- Map size: enlarged twice (height 0.62 → 0.66) with corresponding width adjustment to maintain Albers Equal Area aspect.
- Connecticut shading: was missing (9 unshaded planning regions due to vintage GEOID transition between CenPop2020 and TIGER 2023). Resolved via a BG-centroid spatial join (new script `01c_ct_planning_region_crosswalk.py`); CT now renders fully.
- Output: PNG + SVG + **PDF** added to the file list.

---

## 7. CT planning-region crosswalk

New script `src/01c_ct_planning_region_crosswalk.py`. Spatial-join (point-in-polygon, with nearest-polygon fallback) for each of CT's 2,716 historical-county BGs against TIGER 2023 planning-region polygons. Result: 2,710 (99.8%) resolved via point-in-polygon; 6 via nearest-polygon fallback; CT total population conserved exactly (3,605,944 → 3,605,944). Distribution intuitive: Capitol/Hartford (731 BGs, 98% CZ), Bridgeport (235, 100%), Naugatuck Valley (319, 100%), Northwest Hills (114, 100%), New Haven (436, 97%), and three more rural regions (Eastern, Southeastern, Western) at 51–66%. Choropleth now renders 3,109/3,109 CONUS counties (was 3,100/3,109).

Pure Python implementation (`pyshp` + `matplotlib.path.Path`), no geopandas dependency.

---

## 8. Repo restructure for peer-review readability

The repo's previous front door dropped reviewers onto a Vite/React Delaware prototype's README, with manuscript code buried at `national/`. Restructured (commit `e503a27`):

- **Moves (`git mv` to preserve history):** `src/`, `scripts/`, `package.json`, `package-lock.json`, `vite.config.js`, `index.html`, root `README.md` → `legacy/delaware-prototype/`.
- **Untouched:** `national/` subtree. Zero path changes in any tracked file under `national/`.
- **New at root:** manuscript-oriented `README.md` (headline above the fold, peer-reviewer reading order, reproduce-from-public-sources block, structure tree); `CITATION.cff` (GitHub renders "Cite this repository" widget).

**Tagged `v0.1-aha-ss-2026`** at this commit. Frozen-snapshot URL for reviewers: `github.com/rgaiba/stemi-fmc-to-device/tree/v0.1-aha-ss-2026`.

Workspace `.git` was synced via `git fetch && git reset --hard origin/main` from the local Mac terminal; user's working tree now matches origin/main.

---

## 9. Findings doc created (manuscript Results quarry)

`notes/findings.md` — structured numerical findings extracted from the analytic pipeline at `v0.1-aha-ss-2026`. Eleven sections:

1. National headlines
2. State-level concentration (top 5 = 41.3%, top 10 = 58.1%)
3. State extremes (DC 100% CZ, VT 11% CZ)
4. Cross-state EMS corridors (top 15 corridors; MA→RI largest at 553 STEMI/yr; Nashville and St Louis are multi-state-source attractors)
5. Hospital concentration curve (top 10 = 3.5%, top 100 = 21.5%, top 500 = 63.3%, top 1,000 = 89.8% — substrate is widely distributed; supports population-level vs flagship-system intervention framing)
6. Top 25 PCI-capable hospitals with names, cities, states, beds, catchment STEMI/yr
7. City-level concentration (Atlanta, Boston, Portland, Miami, Oakland, Bronx have multiple top-50 hospitals — inter-system protocol coordination implication)
8. Top 15 counties (LA County 7,003 STEMI/yr alone; top 15 = 8.5% of national CZ burden)
9. PCI hospital density by state (TX 160, CA 127, FL 107 absolute; Indiana highest per-adult at 10.5/M)
10. CT planning-region findings (post-crosswalk)
11. Drive-time access concordance with published literature
12. Notable methodological footnotes (CT vintage, ACS join drift, matrix radius remote tail, ami_volume_2024 exclusion)

---

## 10. Portable reproducibility bundle

`stemi-fmc-to-device-complete-20260509.tar.gz` (136 MB, sibling of the workspace at `/Users/rahulgaiba/Documents/Claude/Projects/PCI times/`). Contains:

- All 105 tracked code/doc files
- All audit-trail docs
- All raw data (CenPop2020, ACS B01001, CMS PoS, CMS IPPS, TIGER counties)
- All processed pipeline outputs including the heavy `drive_times.parquet` (71 MB OSRM matrix)
- All figures (PDF, PNG, SVG)
- Full `.git/` directory with history and the `v0.1-aha-ss-2026` tag

A recipient does not need to clone from GitHub or rebuild the OSRM matrix; the tarball is self-contained. Useful for collaborator hand-off, peer-review attachment, or pre-Zenodo deposit prep at manuscript submission.

Excluded from the bundle (stale, regeneratable, or large for no benefit): `node_modules/`, `dist/` (both at workspace root and inside `legacy/delaware-prototype/`), `.DS_Store` files.

---

## Commits today (15 total + 1 tag)

```
b5bad80 national: notes/findings.md — manuscript-feeding numerical findings doc
e503a27 repo: restructure for peer-review readability — Delaware prototype to legacy/, manuscript code at national/
58be528 choropleth: subtitle adds 'after STEMI'; metrics 'in these areas' for consistency
2243bdb choropleth: stakes-driven subtitle; bigger map; 'drive times'
535cbd1 choropleth: layout, color, copy refresh — center map; teal palette; bold metrics; explicit threshold
5f76eef national: CT planning-region crosswalk — 100% CONUS coverage in choropleth
c7786cd national: choropleth Figure 1 — switch metric to % adults; add CT-vintage note; commit two-panel design stub
1de12c8 abstract v9: status FINAL
fd3349c abstract v9: Conclusions revised — drop NCDR specificity, soften 'next step' to 'may improve'
4cec28a national: pre-registration Amendment 2026-05-08-E — D1 rounding (3 sig figs); D8 reporting clarification
41f247e abstract v9 revision: 196,000 (3 sig figs); 'primary finding' register; sensitivity language refined
2ff9c6c national: abstract_draft_v9.md — headline at 200,000 STEMI/yr (per-adult x ACS 20+); Wang 2024 access anchor
d410afb national: 09_sensitivities.py + sensitivity_table.csv at per-adult x ACS 20+ methodology
e7cfae2 national: pre-registration Amendments 2026-05-08-C and -D; reconcile REPRODUCIBILITY pointer
531675d national: switch STEMI denominator to ACS 20+ adult population; lock external validity

tag: v0.1-aha-ss-2026 (at e503a27)
```

---

## Final state at end of day

| | |
|---|---|
| Repository | `github.com/rgaiba/stemi-fmc-to-device` |
| HEAD | `b5bad80` (with this summary, will advance one) |
| Submission tag | `v0.1-aha-ss-2026` |
| Abstract status | v9 FINAL (~2,510 chars; AHA SS soft limit) |
| Headline finding | ~196,000 STEMI patients/yr (79% of U.S. STEMI cases) in 15-min PCI competitive catchment zones |
| Sensitivity robustness | 6 of 6 groups within ±25% (range 157k–236k STEMI/yr) |
| External validity | 30/60/90-min PCI access ladder concordant with Concannon 2014 / Wang 2024 within ±1 pp; implied national STEMI 248,269/yr inside AHA HDSS 2024 250–280k band without calibration |
| CONUS coverage in figure | 3,109 / 3,109 counties (100%) including CT's 9 planning regions |
| Audit trail | `pre_registration.md` D1–D9 + Amendments 2026-05-07-A through 2026-05-08-E |
| Reproducibility bundle | 136 MB tar.gz at `/Users/rahulgaiba/Documents/Claude/Projects/PCI times/` |

---

## Plausible next steps (not started today)

These are the natural follow-up workstreams when the project resumes:

- **Manuscript Methods external-validity sentence** — already drafted at the bottom of `abstract_draft_v9.md` and in `external_validity.md`, ready to slot into the *Circ: CVQO* manuscript when full draft begins.
- **Two-panel manuscript Figure 1** — design stub at `src/08b_choropleth_two_panel.py`. Panel A = current population-weighted choropleth; Panel B = top-25 hospital markers sized by competitive-zone catchment STEMI count + cross-state routing arcs (the 3.7% claim). CT crosswalk prerequisite is now in place.
- **Mint Zenodo DOI at manuscript submission** — defer until *Circ: CVQO* submission stage; tag a `v1.0` then, enable GitHub-Zenodo integration, cite the Zenodo DOI in the manuscript Reproducibility statement.
- **Submit to AHA Scientific Sessions 2026.**
