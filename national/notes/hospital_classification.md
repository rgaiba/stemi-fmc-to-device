# Hospital classification

Decision document for the three-tier hospital model that drives both the current competitive-catchment analysis and the symptom-onset-to-PCI pathway extension. Lives at this path so the data model is explicit and reviewable, separate from any single analysis script.

Written 2026-05-07.

---

## Why a structured classification matters

The natural reading of the proposal is that the analysis cares about *PCI-capable hospitals*, and everything else is filtered out. That framing leads to losing critical structure:

1. **The DIDO leg of the current analysis** depends on which non-PCI hospital a patient might initially be routed to. If we drop non-PCI hospitals from our dataset, we can't compute DIDO penalties accurately.
2. **The natural extension** of this work — modeling symptom-onset-to-balloon times for the full STEMI care pathway, not just EMS routing — requires every acute-care hospital as a node in the network, not just PCI centers.
3. **Critical access hospitals** in particular are the most-affected initial-receiving facilities (longest DIDOs, smallest STEMI volumes, often the only ED in a 30-min radius). Treating them as residual is a methodological mistake.

The right data model has every hospital as a first-class citizen with an explicit role flag, not a filter that drops them.

---

## Analysis universe restriction

A non-trivial decision lurks in `prvdr_ctgry_cd='01'`. CMS classifies *all* of the following under that single category code:

| Subtype | Definition | Count in our PoS file |
|---|---|---|
| 01 | Short-Term General Hospital | 3,062 |
| 11 | Critical Access Hospital | 1,346 |
| 02 | Long-Term Hospital | 327 |
| 04 | Psychiatric | 646 |
| 05 | Rehabilitation | 391 |
| 20 | Children's | 232 |
| 06 | Religious Non-Medical | 91 |
| 03/24/25/28 | Other specialty | 50 |
| (NaN) | Missing subtype | 489 |

Only subtypes **01** and **11** are realistic EMS-routable destinations for adult STEMI. Subtypes 02/04/05/06/20/28 hospitals have no adult ED capability for STEMI care, even though they share the parent category code. Including them in the analysis universe would inflate Tier B counts with hospitals that EMS would never transport a STEMI patient to, producing phantom DIDO routings.

The classifier therefore restricts the universe to subtypes `{01, 11}` → **4,408 hospitals**. The exclusion is documented in `01_prepare_pos.py` (which keeps the broader subtype set for general PoS use) and applied in `03_classify_hospitals.py` (which defines the analysis universe).

This is the kind of decision a reviewer might surface as "did you really intend to include children's hospitals as STEMI destinations?" — the explicit subtype filter answers that question in code.

---

## Three tiers

```
                 ┌─────────────────────────────────────┐
                 │  All CMS short-term general          │
                 │  hospitals, active, CONUS           │
                 │  (PoS prvdr_ctgry_cd=01,            │
                 │   pgm_trmntn_cd=00, CONUS state)    │
                 │  N = 6,634                          │
                 └─────────────────────────────────────┘
                                 │
                ┌────────────────┼────────────────┐
                ▼                                 ▼
      ┌──────────────────┐              ┌──────────────────┐
      │ Tier A           │              │ Tier B           │
      │ PCI-capable      │              │ Non-PCI acute    │
      │                  │              │                  │
      │ on-site cath lab │              │ no on-site cath  │
      │ (PoS service     │              │ (active short-   │
      │  code 1 or 3)    │              │  term general or │
      │                  │              │  CAH)            │
      │ N = 1,598        │              │ N = 2,810        │
      └──────────────────┘              └──────────────────┘
                                                │
                                                ▼
                                       1,346 CAHs (subtype 11)
                                       16 of which are Tier A
                                       1,330 are Tier B
                │                                 │
                ▼                                 ▼
       Direct STEMI                       Initial receiving;
       receiving destination              triggers DIDO leg
       (T₁ or T₂ in                       on transfer to
       competitive zones)                 nearest Tier A
```

A third logical tier exists conceptually — **non-acute facilities** (psych, rehab, hospice, nursing) — but these are filtered out at the prvdr_ctgry_cd ≠ 01 step in `01_prepare_pos.py` before any of this matters. They're not in our universe of EMS-routable destinations.

---

## Tier definitions (operational)

### Tier A — PCI-capable

A hospital is classified Tier A if it satisfies *all* of:

- `prvdr_ctgry_cd == "01"` (short-term general)
- `pgm_trmntn_cd == "00"` (active)
- `state_cd in CONUS_WHITELIST`
- `crdc_cthrtztn_lab_srvc_cd in {"1", "3"}` (on-site cath lab service)

Optional augmentation (Tier A+) for higher-confidence subset:

- `crdc_cthrtztn_prcdr_rooms_cnt >= 1` (cath lab room actually present)
- `Rndrng_Prvdr_CCN` appears in IPPS PUF DRG 280-282 (has measurable AMI volume)

The base Tier A definition is what enters the competitive-zone analysis (1,635 hospitals). The Tier A+ subset (~1,129 concordant on both PoS signals + present in IPPS) feeds sensitivity analyses where we want a stricter PCI definition.

### Tier B — non-PCI acute

A hospital is classified Tier B if it satisfies the first three Tier A criteria but **not** the cath lab service code requirement:

- `prvdr_ctgry_cd == "01"` (short-term general)
- `pgm_trmntn_cd == "00"` (active)
- `state_cd in CONUS_WHITELIST`
- `crdc_cthrtztn_lab_srvc_cd not in {"1", "3"}` (no on-site cath lab, OR cath lab is off-site/under-arrangement)

These hospitals are the **initial-receiving facilities** for STEMI patients whose nearest hospital lacks PCI capability. They are NOT excluded from the analysis. They appear in the DIDO leg as the T₀ hospital.

Sub-flag of interest:

- `bed_cnt < 25` AND rural (RUCA ≥ 7) → critical access hospital (CAH) candidate. CAHs have characteristic DIDO profiles in the literature (often longer due to staffing and transport coordination overhead). Worth tagging for type-stratified DIDO priors.

### Sub-flags within tiers (downstream attributes, not classification)

- `is_academic` — bed_cnt ≥ 300 AND urban RUCA ≤ 3 AND member of Council of Teaching Hospitals (future enrichment)
- `is_critical_access` — bed_cnt < 25 AND RUCA ≥ 7
- `has_ami_volume_in_puf` — CCN matches IPPS DRG 280–282 record
- `ami_volume_tertile` — within-tier-A tertile of summed DRG 280–282 discharges (used for D2B-prior stratification)

---

## Roles in the current analysis

For each block group centroid in CenPop2020:

| Variable | Computed using | Tier source |
|---|---|---|
| T₁ | nearest hospital | Tier A ∪ Tier B |
| T₂ | second-nearest hospital | Tier A ∪ Tier B |
| T₁_PCI | nearest *PCI-capable* hospital | Tier A only |
| T₂_PCI | second-nearest *PCI-capable* hospital | Tier A only |
| competitive_margin | T₂_PCI − T₁_PCI | Tier A only |
| ΔS2B | f(D2B_T₁_PCI, D2B_T₂_PCI, DIDO if T₁ is Tier B) | both tiers |

The `T₁ ∈ Tier B` case is the DIDO trigger. If the *nearest* hospital is non-PCI (Tier B), the patient is initially routed there, accumulates DIDO time, then transfers to T₁_PCI (the nearest PCI-capable). The ΔS2B for that block group then becomes:

```
ΔS2B = [D2B(T₂_PCI)] − [DIDO(T₁_Tier_B) + transfer_drive(T₁_Tier_B → T₁_PCI) + D2B(T₁_PCI)]
```

If ΔS2B > 0, routing optimization (skip the Tier B initial stop, go straight to the second-nearest PCI center directly) produces faster S2B than the DIDO chain. This is exactly the routing question the paper asks.

**Without keeping Tier B hospitals in the dataset, this calculation is impossible.**

---

## Roles in future-work extensions

### Extension 1 — Symptom-onset to balloon optimization

The current analysis starts from EMS first medical contact (FMC). Patients can also self-present (walk-in) to any acute hospital. The full pathway:

```
[symptom onset]
       │
       ▼
[patient call 911]  OR  [patient self-presents to ED]
       │                          │
       ▼                          ▼
[EMS arrival, FMC]            [Tier A or Tier B walk-in]
       │                          │
       ▼                          ▼
[EMS routes to                [if Tier B, DIDO + transfer]
 Tier A or Tier B]                │
       │                          ▼
       └─────────────────────► [Tier A]
                                  │
                                  ▼
                              [balloon]
```

Modeling this requires every Tier A and Tier B hospital as a network node with: location, D2B distribution (Tier A), DIDO distribution (Tier B), transfer-time matrix (Tier B → Tier A).

The current dataset already captures everything needed for this extension — provided we classify and persist Tier B hospitals rather than dropping them.

### Extension 2 — Mobile-stroke-unit-style mobile cath lab optimization

The mission-update memo (2026-05-07) noted that the broader workstream is symptom-to-device, with mobile ambulance posts as the first siting optimization. A natural follow-up is mobile cath labs sited based on competitive-zone geometry. That analysis will need both Tier A and Tier B hospitals as the existing-network baseline against which mobile capacity is compared.

### Extension 3 — Pre-hospital ECG transmission models

Pre-hospital ECG diagnosis allows EMS to bypass Tier B and go direct to Tier A even when Tier B is closer. Modeling the value of pre-hospital ECG protocols requires knowing how often Tier B is currently the closest hospital — which is exactly the data we'd lose if we filtered it out.

---

## Implementation

A new prep script `national/src/03_classify_hospitals.py` produces the canonical classified dataset:

```
input:  national/data/raw/cms_pos/cms_pos_2024-12.csv  (6,634 active CONUS short-term general)
        national/data/raw/cms_ipps/cms_ipps_drg_FY2024.csv  (3,408 hospital × DRG records)

output: national/data/processed/hospitals_classified.parquet

columns:
  ccn                          (str)  primary key
  fac_name                     (str)
  st_adr, city, state, zip     (str)  for geocoding
  fips_state_cd                (str)  joins to CenPop2020 STATEFP
  bed_cnt                      (int)
  ruca                         (int|null)
  tier                         (str)  "A" | "B"
  is_pci_capable               (bool) tier == "A"
  pci_signal_concordant        (bool) cath lab service AND room count both signal PCI
  is_critical_access_candidate (bool) bed_cnt < 25 AND RUCA >= 7
  has_ami_volume_in_puf        (bool) CCN matches IPPS PUF
  ami_volume_2024              (int)  sum of DRG 280-282 Tot_Dschrgs (or null if not in PUF)
  ami_volume_tertile           (int)  1/2/3 within Tier A; null if not in PUF
```

Every downstream script joins on `ccn` and selects on `tier`.

### Actual classifier output (from 03_classify_hospitals.py, FY2024 data):

```
total in analysis universe:              4,408
  Tier A (PCI-capable):                  1,598
  Tier B (non-PCI acute):                2,810
  PCI signal concordant (A only):        1,104
  Critical access hospitals (subtype 11): 1,346
    Tier A (PCI-capable CAH):              16
    Tier B (non-PCI CAH):               1,330
  With AMI volume in PUF:                1,828

Tier A AMI volume tertiles:
  tertile 1 (low):  range 11–37 admissions, median 22  (n=453)
  tertile 2 (mid):  range 38–73 admissions, median 54  (n=448)
  tertile 3 (high): range 74–786 admissions, median 109 (n=449)
  not in PUF (suppressed): n=248 — D2B prior defaults to community tier
```
 No filter inline; the structure is the filter.

---

## Anticipated question

**Q: If you keep Tier B hospitals in the dataset, won't they contaminate competitive-zone calculations?**

A: No. Competitive zones are defined over Tier A only (T₁_PCI, T₂_PCI). Tier B hospitals never enter the competitive-margin calculation directly. They enter ΔS2B only when T₁ (nearest hospital, of any tier) is Tier B — i.e., the DIDO case — which is exactly when including them is methodologically essential. A reviewer asking "why didn't you model what happens when EMS routes to the nearest hospital and it isn't PCI-capable?" would be asking for exactly this structure.
