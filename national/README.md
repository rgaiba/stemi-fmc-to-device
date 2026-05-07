# National competitive PCI catchment analysis

Workstream for the *Circulation: CVQO* submission. Identifies U.S. census block groups where two or more PCI-capable hospitals lie within a clinically meaningful drive-time margin, and ranks hospital systems by the symptom-to-balloon improvement that EMS routing optimization would deliver.

This directory is independent of the Delaware web prototype at the repo root. The Delaware prototype validates the classification logic at small scale; this workstream scales it nationally with road-network drive times via OSRM.

## Layout

```
national/
├── data/
│   ├── raw/        # User-provided source files (gitignored — see data/README.md)
│   └── processed/  # Pipeline outputs in parquet (gitignored)
├── src/            # Pipeline scripts (01_..., 02_..., etc.)
└── outputs/
    ├── tables/     # CSV/parquet tables for the paper
    └── figures/    # Choropleth + sensitivity figures (PNG/SVG)
```

## Status

- Data scaffolding committed; user is downloading source files per `data/README.md`.
- Pipeline scripts are not yet written — waiting on confirmed data shape from uploaded files before locking parsers.

## Central contribution to protect

The central methodological contribution is the **competitive catchment classification** — for each block group, T1 (drive time to nearest PCI center) and T2 (drive time to second-nearest), and the dS2B that follows. The data-quality risk concentrates in **two places**:

1. **PCI center identification.** A false negative (missed PCI-capable hospital) creates a phantom non-competitive zone. A false positive (non-PCI hospital flagged as PCI) creates a phantom competitive zone with an inflated dS2B. Cross-referencing CMS PoS, IPPS DRG 246/247 volume, and (where available) the AHA/ACC Mission: Lifeline STEMI-receiving center registry is the mitigation.
2. **D2B priors.** Hospital-specific D2B from Mission: Lifeline where reported; type-based prior otherwise. The type-based prior is the assumption reviewers will probe hardest — keep its provenance traceable.

Everything downstream — drive times, competitive margin, dS2B, system ranking — is mechanical once these two inputs are clean.
