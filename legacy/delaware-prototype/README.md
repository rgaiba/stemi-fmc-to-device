# stemi-fmc-to-device

Visualizing travel time to PCI-capable hospitals in Delaware, and the access gain from adding **Bayhealth Milford** to the network.

The mission of this project is to find ways to **decrease FMC-to-device time for patients with STEMI**. Reducing this interval is directly tied to saving heart muscle and saving lives — every 30-minute delay in reperfusion is associated with a measurable increase in 1-year mortality.

This page renders two side-by-side maps:

- **Current PCI Network** — 6 centers (Christiana, Wilmington, Bayhealth Kent, Beebe, TidalHealth MD, Shore Easton MD)
- **With Bayhealth Milford** — adding a 7th center in Milford, DE

Each dot is a 2020 census block group centroid, sized by population and colored by estimated drive time to the nearest PCI center (straight-line × 1.35 detour factor at 45 mph average — estimates only, not actual EMS response times).

## Stack

- React 18
- Vite
- Plain SVG (no chart library)

## Develop

```bash
npm install
npm run dev
```

## Build

```bash
npm run build
npm run preview
```

## Data

- U.S. Census Bureau · CenPop2020_Mean_BG10 · FIPS 10
- Hospital coordinates: hand-curated from public addresses

## Disclaimer

The drive-time numbers are first-order estimates from straight-line distance with a detour factor. They are useful for **directional comparison** between scenarios, not as an EMS planning tool. A real-world model would use a routing engine (OSRM/Valhalla/Google) and EMS dispatch data.
