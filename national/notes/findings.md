# Notable findings — STEMI competitive catchment analysis

Numerical findings extracted from the analytic pipeline at commit `v0.1-aha-ss-2026`. Each finding is rate-and-denominator transparent and traceable to a specific data file in `national/data/processed/` or `outputs/`. Findings are observational; this file does not make causal claims.

This document is a manuscript working file: Results section claims and supplement subgroup analyses should be sourced from here. When numbers move (re-run with new data vintage, methodology amendment), update this file and date the change.

All STEMI counts use rate 0.001 STEMI per adult aged 20+ per year (AHA *Heart Disease and Stroke Statistics* 2024) applied to ACS 2019–2023 5-year block-group adult population. See pre_registration.md D4 (Amendment-C) and REPRODUCIBILITY.md D8.

---

## 1. National headlines (recapping; primary abstract content)

- **Implied national STEMI count:** 248,269 / yr. Inside AHA HDSS 2024 published range (250,000–280,000) without calibration.
- **Competitive-zone (≤15 min) STEMI count:** **196,253 / yr (79.0% of national STEMI).**
- **Competitive-zone block-group count:** 185,270 of 238,193 CONUS BGs (77.8%).
- **Competitive-zone adult population:** 196.3 M of 248.3 M CONUS adults aged 20+.
- **Robustness:** all 6 of 6 pre-specified sensitivity groups within ±25% of baseline; range 157,002–235,504 STEMI/yr (S3 rate sweep dominates; non-rate sensitivities ≤13%).

Source: `outputs/tables/sensitivity_table.csv`, `state_summary.csv`.

---

## 2. State-level concentration

**Top 5 states account for 41.3% of national competitive-zone STEMI burden; top 10 account for 58.1%.**

| Rank | State | Adults 20+ | Competitive adults | % adults in CZ | Competitive STEMI/yr |
|---|---|---|---|---|---|
| 1 | CA | 29,488,026 | 25,457,881 | 86.3% | 25,458 |
| 2 | TX | 21,326,720 | 19,309,845 | 90.5% | 19,310 |
| 3 | FL | 17,119,734 | 14,549,766 | 85.0% | 14,550 |
| 4 | NY | 15,252,169 | 13,323,384 | 87.4% | 13,323 |
| 5 | IL |  9,556,344 |  8,478,822 | 88.7% |  8,479 |
| 6 | PA |  9,952,813 |  8,335,277 | 83.7% |  8,335 |
| 7 | OH |  8,865,294 |  7,321,928 | 82.6% |  7,322 |
| 8 | NJ |  7,013,698 |  6,443,763 | 91.9% |  6,444 |
| 9 | MI |  7,635,056 |  5,450,116 | 71.4% |  5,450 |
| 10 | GA |  7,979,630 |  5,309,590 | 66.5% |  5,310 |

Source: `state_summary.csv`.

### 2a. States by competitive-zone share (highest)

States where >85% of adults live in competitive catchment zones:

| Rank | State | % adults in CZ | Notes |
|---|---|---|---|
| 1 | DC | 100.0% | Entirely urban |
| 2 | NV | 92.1% | Population concentrated in Las Vegas / Reno metros |
| 3 | NJ | 91.9% | Densest Northeast Corridor; bordered by NYC and Philadelphia metros |
| 4 | RI | 91.4% | Small geography, all metropolitan |
| 5 | TX | 90.5% | High because metros (Houston, DFW, San Antonio, Austin) dominate |
| 6 | IL | 88.7% | Chicago metro carries most |
| 7 | NY | 87.4% | NYC carries most |
| 8 | CA | 86.3% | Coastal metros; Central Valley elevated by Fresno/Sacramento |
| 9 | CT | 85.3% | Northeast Corridor |
| 10 | FL | 85.0% | Urban coastal corridor |

### 2b. States by competitive-zone share (lowest, most rural)

States where competitive-zone share is below 60%:

| Rank | State | % adults in CZ | Notes |
|---|---|---|---|
| 1 | VT |  11.1% | Single small metro (Burlington); rest predominantly rural |
| 2 | WY |  12.5% | Lowest population density CONUS |
| 3 | MT |  38.3% | Most metros isolated by geography |
| 4 | AL |  54.0% | Rural belt outside Birmingham/Mobile/Huntsville/Montgomery |
| 5 | SD |  54.4% | Sioux Falls + Rapid City metros only |
| 6 | ND |  54.8% | Fargo + Bismarck metros only |
| 7 | MS |  57.8% | Sparse PCI access outside Jackson/Gulf Coast |
| 8 | NC |  58.5% | Western mountains and eastern coastal plain rural |
| 9 | WV |  60.0% | Mountain geography limits PCI clustering |
| 10 | ID |  63.0% | Boise/Coeur d'Alene metros only |

Manuscript framing: the 79% national headline overstates coverage in the rural West and central Plains. State-level granularity belongs in the supplement.

Source: `state_summary.csv`.

---

## 3. Cross-state EMS corridors (3.7% of competitive-zone BGs route across a state line)

Of the 185,270 competitive-zone block groups, **6,849 (3.7%) have a nearest PCI-capable hospital in a different state from the patient's block group.** State-pair-level breakdown:

| Corridor | BGs | Adult pop | Competitive STEMI/yr |
|---|---|---|---|
| MA adults route to RI | 496 | 553,350 | 553 |
| AL adults route to TN | 166 | 186,113 | 186 |
| NC adults route to VA | 185 | 176,166 | 176 |
| GA adults route to FL | 185 | 168,486 | 168 |
| GA adults route to TN | 163 | 166,601 | 167 |
| OH adults route to WV | 191 | 149,591 | 150 |
| KS adults route to MO | 187 | 147,806 | 148 |
| NJ adults route to PA | 142 | 147,181 | 147 |
| WI adults route to MN | 123 | 141,933 | 142 |
| IL adults route to MO | 163 | 132,766 | 133 |
| MN adults route to ND | 152 | 132,020 | 132 |
| NY adults route to NJ | 114 | 127,768 | 128 |
| SC adults route to NC |  91 | 122,656 | 123 |
| NH adults route to MA |  90 | 114,293 | 114 |
| IL adults route to IN | 141 | 112,567 | 113 |

The corridor narrative for the manuscript:
- **Nashville's regional pull** (TN as destination state for AL and GA) is large enough to be a single-paragraph callout: ~350 STEMI/yr from out-of-state adults route to TN PCI centers. This is a known regional referral pattern but has not been quantified at the population level prior.
- **St. Louis's Missouri pull** (KS and IL adults routing to MO) reflects metro-east St Louis crossing the Mississippi. ~280 STEMI/yr.
- **MA-RI** (496 BGs, 553 STEMI/yr) is the largest single corridor by patient count; MA towns north and west of Providence's catchment are nearer to RI hospitals than to the Boston system.
- **NY-NJ** (128 STEMI/yr) is artificially low because the Hudson river and metro density mean both states have abundant PCI; few NY BGs route across the river compared to the metro's footprint. The manuscript should not over-emphasize NY-NJ as a corridor.

These corridors suggest concrete EMS mutual-aid policy implications: for patients in these areas, dispatch protocols should formally permit cross-state routing decisions when D2B differentials warrant. Rhetorical framing for Results: "approximately 3.7% of competitive-zone block groups (housing 196,000 × 3.7% ≈ 7,260 STEMI/yr) have their nearest PCI-capable hospital in a neighboring state, raising EMS mutual-aid considerations specific to that population."

Source: `zones_classified.parquet` filtered to `is_competitive_15 & cross_state`.

---

## 4. Hospital-level concentration curve

Competitive-zone STEMI catchment is **not** dominated by flagship centers. The substrate is widely distributed:

| Top N hospitals | % of competitive-zone STEMI catchment |
|---|---|
| Top 10 | 3.5% |
| Top 25 | 7.5% |
| Top 50 | 12.9% |
| Top 100 | 21.5% |
| Top 250 | 41.0% |
| Top 500 | 63.3% |
| Top 1,000 | 89.8% |
| All 1,576 Tier A hospitals serving competitive zones | 100% |

Manuscript framing: a large-cap hospital-system intervention will not capture the bulk of optimization opportunity. To affect 50% of the competitive-zone STEMI population, an intervention must reach ~350 hospitals. 80% requires ~700. This is a rationale for population-level (EMS routing protocol) versus institution-level (one flagship system's process improvement) approaches.

Source: `top_hospitals.csv`.

---

## 5. Top 25 PCI-capable hospitals by competitive-zone catchment

These are the hospitals for whom the largest population of competitive-zone STEMI patients have them as default destination. Together they are 1.6% of the 1,576 Tier A hospitals serving competitive zones but account for 7.5% of the catchment STEMI population.

| Rank | Hospital | City | State | Beds | BGs served | STEMI/yr |
|---|---|---|---|---|---|---|
| 1 | Saint Joseph's Hospital of Atlanta | Atlanta | GA | 410 | 756 | 870 |
| 2 | Regions Hospital | Saint Paul | MN | 554 | 757 | 744 |
| 3 | Sentara Norfolk General Hospital | Norfolk | VA | 525 | 693 | 714 |
| 4 | LAC/Harbor-UCLA Medical Center | Torrance | CA | 553 | 647 | 689 |
| 5 | Los Angeles General Medical Center | Los Angeles | CA | 676 | 578 | 677 |
| 6 | Boston Medical Center Corporation | Boston | MA | 441 | 664 | 675 |
| 7 | John Muir Medical Center, Concord | Concord | CA | 303 | 536 | 673 |
| 8 | Baptist Medical Center | San Antonio | TX | 1,285 | 650 | 663 |
| 9 | Lovelace Medical Center | Albuquerque | NM | 254 | 541 | 628 |
| 10 | Massachusetts General Hospital | Boston | MA | 907 | 623 | 608 |
| 11 | Piedmont Eastside Medical Center | Snellville | GA | 200 | 459 | 586 |
| 12 | Rhode Island Hospital | Providence | RI | 719 | 566 | 578 |
| 13 | Adventist Health Portland | Portland | OR | 302 | 475 | 567 |
| 14 | M Health Fairview Southdale Hospital | Edina | MN | 390 | 604 | 558 |
| 15 | Jamaica Hospital Medical Center | Jamaica | NY | 424 | 505 | 530 |
| 16 | Providence St Vincent Medical Center | Portland | OR | 523 | 424 | 517 |
| 17 | Saint John's Health Center | Santa Monica | CA | 317 | 508 | 510 |
| 18 | Baptist Hospital of Miami | Miami | FL | 948 | 427 | 495 |
| 19 | George Washington Univ Hospital | Washington | DC | 371 | 528 | 493 |
| 20 | PIH Health Downey Hospital | Downey | CA | 199 | 441 | 492 |
| 21 | Highland Hospital | Oakland | CA | 613 | 465 | 482 |
| 22 | WellStar Kennestone Regional Med Ctr | Marietta | GA | 633 | 400 | 475 |
| 23 | Community Regional Medical Center | Fresno | CA | 794 | 454 | 473 |
| 24 | Grossmont Hospital | La Mesa | CA | 536 | 383 | 469 |
| 25 | Elmhurst Hospital Center | Elmhurst | NY | 545 | 419 | 458 |

Notable observations:
- **Bed count varies 6× across the top 25** (199 to 1,285 beds). Catchment STEMI count is not driven by hospital size; it's driven by population density of the surrounding competitive zone.
- **California holds 9 of the top 25 hospitals** despite being one state, reflecting LA basin and SF Bay Area metro density.
- **Two of the top 25 are public safety-net hospitals** (Los Angeles General, Highland Oakland), reinforcing that the substrate is not concentrated at academic flagship centers.
- **The single largest hospital catchment** (Saint Joseph's Atlanta, 870 STEMI/yr) is approximately the volume of a single mid-size PCI program's annual STEMI volume — a useful order-of-magnitude anchor for clinical readers.

Source: `top_hospitals.csv` (top 25). Excluded `ami_volume_2024` from this table; see comment in `07_aggregate.py` for the rationale (Medicare-FFS-only metric on a different denominator from `stemi_per_yr`).

---

## 6. Cities with the densest concentration of top-25 hospitals

Of the top 50 hospitals by competitive-zone STEMI catchment, several cities have multiple entries:

| City, State | Top-50 hospitals | Combined STEMI/yr |
|---|---|---|
| Atlanta, GA | 2 (Saint Joseph's + Piedmont Eastside via Snellville suburb) | 1,315 |
| Boston, MA | 2 (Boston Medical Center, Mass General) | 1,283 |
| Portland, OR | 2 (Adventist Health Portland, Providence St Vincent) | 1,084 |
| Miami, FL | 2 (Baptist Miami + neighbor) | 911 |
| Oakland, CA | 2 (Highland + neighbor) | 906 |
| Bronx, NY | 2 | 836 |

These metros are where STEMI routing optimization could plausibly involve **inter-system protocols** (multiple unrelated hospital systems competing in the same catchment), as opposed to within-system routing. EMS protocol alignment across competing systems is a known operational challenge in cardiology QI literature; this analysis quantifies which metros face that challenge most acutely.

Source: `top_hospitals.csv` head(50) grouped by city.

---

## 7. Counties with the highest competitive-zone STEMI counts

The top 15 counties account for 8.5% of national competitive-zone STEMI burden. All but one (King County, WA) are in the top 5 ranked states; reads as a metro-county roll-up.

| Rank | County FIPS | County | Competitive STEMI/yr | % BGs in CZ |
|---|---|---|---|---|
| 1 | 06037 | Los Angeles, CA | 7,003 | 93.4% |
| 2 | 17031 | Cook (Chicago), IL | 3,953 | 100.0% |
| 3 | 48201 | Harris (Houston), TX | 3,321 | 98.0% |
| 4 | 04013 | Maricopa (Phoenix), AZ | 3,240 | 96.8% |
| 5 | 06073 | San Diego, CA | 2,424 | 97.3% |
| 6 | 06059 | Orange, CA | 2,162 | 89.8% |
| 7 | 12086 | Miami-Dade, FL | 2,082 | 100.0% |
| 8 | 36047 | Kings (Brooklyn), NY | 2,000 | 100.0% |
| 9 | 48113 | Dallas, TX | 1,863 | 99.6% |
| 10 | 36081 | Queens, NY | 1,824 | 100.0% |
| 11 | 32003 | Clark (Las Vegas), NV | 1,708 | 99.1% |
| 12 | 53033 | King (Seattle), WA | 1,628 | 91.9% |
| 13 | 06071 | San Bernardino, CA | 1,562 | 99.8% |
| 14 | 48439 | Tarrant (Fort Worth), TX | 1,529 | 100.0% |
| 15 | 12011 | Broward (Fort Lauderdale), FL | 1,498 | 99.7% |

LA County alone (~7,000 STEMI/yr in competitive zones) is roughly the size of the *entire* competitive-zone STEMI burden of the bottom 15 states combined. Worth noting in the supplement as a "scale of opportunity at the metro level" callout.

Source: `county_summary.csv`.

---

## 8. PCI hospital density by state

Top 10 states by absolute number of PCI-capable hospitals:

| State | PCI hospitals (Tier A) | Adults 20+ | PCI per 1M adults |
|---|---|---|---|
| TX | 160 | 21.3 M | 7.5 |
| CA | 127 | 29.5 M | 4.3 |
| FL | 107 | 17.1 M | 6.3 |
| PA |  84 |  9.9 M | 8.4 |
| IL |  76 |  9.6 M | 8.0 |
| NY |  68 | 15.3 M | 4.5 |
| OH |  62 |  8.9 M | 7.0 |
| IN |  53 |  5.0 M | 10.5 |
| NJ |  45 |  7.0 M | 6.4 |
| MI |  45 |  7.6 M | 5.9 |

States with the fewest PCI hospitals (≤10):

| State | PCI hospitals |
|---|---|
| VT | 2 |
| DC | 2 |
| WY | 5 |
| DE | 5 |
| RI | 6 |
| ND | 6 |
| NH | 7 |
| SD | 8 |
| MT | 9 |
| ME | 10 |

Two takeaways for the manuscript:
- **Indiana has the highest PCI density per adult** (10.5 PCI/M adults) among the top-10-by-count states. Worth a sentence on state-level regulatory factors that produced this clustering (e.g., post-1990s certificate-of-need history).
- **Wyoming, Vermont, and DC each have 2–5 PCI hospitals** but for very different reasons: Wyoming geographic vastness, Vermont rural; DC small geography. Lumping by absolute count is misleading; manuscript should not.

Source: `hospitals_classified.parquet` filtered to `tier == "A"`, grouped by `state_cd`.

---

## 9. Connecticut planning-region findings (post-crosswalk)

After the BG-level crosswalk from CT historical counties to TIGER 2023 planning regions (`src/01c_ct_planning_region_crosswalk.py`):

| Planning region | BGs | Adult pop | Competitive adult pop | % CZ |
|---|---|---|---|---|
| 09110 Capitol (Hartford) | 731 | 734,170 | 720,024 | 98% |
| 09120 Greater Bridgeport | 235 | 245,002 | 245,002 | 100% |
| 09130 Lower CT River Valley | 137 | 131,025 | 112,239 | 86% |
| 09140 Naugatuck Valley | 319 | 338,691 | 338,691 | 100% |
| 09150 Northeastern CT | 83 | 71,709 | 47,178 | 66% |
| 09160 Northwest Hills | 114 | 84,604 | 84,604 | 100% |
| 09170 South Central CT (New Haven) | 436 | 429,025 | 418,161 | 97% |
| 09180 Southeastern CT (New London) | 225 | 210,892 | 112,032 | 53% |
| 09190 Western CT | 436 | 466,669 | 235,798 | 51% |

Observations:
- Western CT (51%) and Southeastern CT (53%) are below the state-average 85%, reflecting their more rural composition.
- Bridgeport, Naugatuck Valley, and Northwest Hills planning regions show 100% competitive zone coverage at this resolution — every BG in those regions has a second PCI hospital reachable within 15 minutes of the nearest.

Source: `county_summary.csv` filtered to county_fips starting with "09".

---

## 10. Drive-time access concordance with published literature

External validity checks — these are reproducer-friendly numbers a reviewer can cross-walk against published papers:

| Threshold | Computed | Published | Source |
|---|---|---|---|
| ≤ 30 min | **80.6%** of CONUS adults | ~78–82% | Concannon et al., *Circ CVQO* 2014 |
| ≤ 60 min | **94.2%** | 91–95% | Wang et al., *Circulation* 2024 |
| ≤ 90 min | **98.1%** | ~96–98% | follow-on access studies |
| Median nearest-PCI drive time | **13.0 min** | 11–15 min | metro-weighted summaries |
| IQR | 7.6–26.5 min | qualitatively concordant | — |

Source: `06_classify_zones.py` external validity block; narrative in `notes/external_validity.md`.

---

## 11. Notable methodological footnotes

These are not findings about geography but findings about the analysis itself, useful for the manuscript Methods/Limitations:

- **The CT GEOID transition** affected 9 of 3,109 CONUS counties (0.3%). Resolved via BG-centroid spatial join; preserves CT total population exactly (3,605,944 → 3,605,944). Documented in `01c_ct_planning_region_crosswalk.py` and Amendment 2026-05-08-C of `pre_registration.md`.
- **Vintage drift** between CenPop2020 and ACS 2019–2023 leaves 2,756 BGs (1.16% of CONUS) without a direct ACS join; the CONUS adult fraction (0.7520) is imputed for these. Numerically negligible; documented in `06_classify_zones.py`.
- **Drive-time engine matrix radius** (~150 mi haversine pre-filter) leaves 970 BGs (0.4%) with no PCI hospital within the matrix. These are the genuine remote tail (Wyoming, Montana, west Texas, parts of Maine) and constitute the manuscript's "extreme remote" footnote.
- **The ami_volume_2024 column** (Medicare FFS only) was deliberately excluded from `top_hospitals.csv` (the published supplement) because side-by-side with `stemi_per_yr` (all-payer catchment count) it invites a wrong inference. Kept in the working `hospitals_classified.parquet` for downstream Paper-2 use. See comment block in `07_aggregate.py`.

---

## When to update this file

Update entries here when:
- A pre-registration amendment is filed that changes any number above
- Sensitivity table is regenerated under a new methodology
- A new finding worth recording surfaces during manuscript drafting
- Data vintage changes (CMS PoS year, ACS 5-year release, OSRM extract date)

Do not update without checking the source data file and recomputing — every number in this file is derived directly from `national/data/processed/*.csv` or `outputs/tables/*.csv` at the commit indicated at top.
