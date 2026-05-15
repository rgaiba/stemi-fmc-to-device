# web/ — Interactive U.S. PCI Competitive Transfer Zones map

Companion web app for the AHA Scientific Sessions 2026 abstract. Renders the same choropleth as `national/outputs/figures/choropleth_competitive_zones.pdf`, with per-county hover tooltips (county name, FIPS, adult population, % adults in a competitive zone, estimated STEMI patients/year).

**Live URL:** https://stemifast.org

## Stack

- React 18 + Vite
- `react-simple-maps` (D3-geo wrapper, Albers Equal Area Conic projection)
- `us-atlas` 1:10M counties TopoJSON (loaded from jsDelivr CDN)
- `d3-scale` for the color ramp (5-stop sequential teal — matches the matplotlib figure)

## Deployed via GitHub Actions

A push to `main` that touches anything under `web/` (or the deploy workflow itself) builds the site and publishes it to GitHub Pages. The workflow lives at `.github/workflows/deploy-web.yml`.

One-time setup on a fresh repo: enable Pages in repo settings → **Source: GitHub Actions** (not "Deploy from a branch"). After that, every push deploys automatically.

## Local development

```bash
cd web
npm install
npm run dev      # http://localhost:5173/
npm run build    # outputs to web/dist/
npm run preview  # serves the production build locally
```

## Data source

`src/data/county_values.json` is generated from `national/data/processed/zones_classified.parquet` and the TIGER 2023 county shapefile. Keys are 2020-vintage 5-digit county FIPS so that `us-atlas` lookups resolve (us-atlas uses 2020 FIPS; the Connecticut planning-region transition is handled separately in the matplotlib pipeline only).

To regenerate after a pipeline re-run, the generator snippet is in the project history (search for `web/src/data/county_values.json` in commit messages).

## Visual consistency with the print figure

The web app intentionally mirrors the matplotlib PDF — same title text, same subtitle, same metrics callout, same teal palette anchors (`#FFFFFF → #C5DCD9 → #5C9690 → #1F5651 → #062E2A`), same Albers Equal Area projection. The interactivity (per-county tooltips) is the value-add of the web version; the static composition matches the publication figure.
