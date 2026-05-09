"""Two-panel choropleth for Circ: CVQO manuscript Figure 1 (DESIGN STUB — not yet implemented).

Status: planning only. Logic outlined below; no plotting code yet. The
single-panel population-weighted choropleth (08_choropleth.py) is what
ships with the AHA Scientific Sessions abstract; this two-panel version
is the manuscript follow-up that adds depth without changing the headline.

Why two panels
--------------
The single-panel map answers one question: "where do U.S. adults live who
are inside a 15-minute PCI competitive catchment zone?" The manuscript
needs to also answer "and which PCI hospitals are the default destination
for those adults?" — because the hospital-distribution claim in Results
("approximately 1,550 hospitals... top 25 account for 7.5%") needs a
visual handle.

Panel layout
------------
Two horizontal panels, equal width.

Panel A (left): population-weighted competitive-zone choropleth.
    Identical to 08_choropleth.py output. Adult-population share by county.
    Title: "A | Adults in 15-minute competitive catchment zones"
    Provides the spatial distribution of the population the abstract
    headline talks about.

Panel B (right): top-25 PCI hospitals overlaid on the same county base.
    Same projection (Albers Equal Area Conic), same county outlines, but
    with two visual additions:
      1. Each Tier A hospital plotted as a small circle, sized by its
         competitive-zone catchment STEMI count (stemi_per_yr from
         top_hospitals.csv). Top 25 highlighted in a darker hue and
         labeled with the hospital name.
      2. Cross-state competitive-zone arcs: for the 6,849 BGs whose
         T1_PCI lies in a different state from the BG, draw a thin
         translucent line from the BG centroid to T1_PCI. Aggregate so
         lines that overlap intensify (alpha-blending). The result is a
         visualization of where state-line PCI flow occurs.
    Title: "B | Top 25 PCI hospitals by competitive-zone catchment;
            cross-state routing arcs (3.7% of competitive zones)"
    Provides the hospital-distribution and cross-state-routing claim
    visually.

Color and style choices
-----------------------
Panel A: same gold-red ramp as 08_choropleth.py (white -> tan -> red).

Panel B base: same county outlines as Panel A but pale gray fill (so the
hospital markers and arcs are the visual focus, not the county shading).

Hospital markers:
  - Top 25: filled circle, dark navy (#1A1E2E), with white halo for legibility,
            sized by sqrt(stemi_per_yr) so 800 STEMI/yr hospital is roughly
            5x the radius of a 32 STEMI/yr hospital.
  - Other Tier A: small filled circle, muted blue (#5A7AA0), no label.

Cross-state arcs: thin curves (matplotlib BezierCurve or quadratic Bezier
with control point at the midpoint offset perpendicular to the chord).
Color: warm orange (#C8A84B with alpha=0.10). Aggregate via additive
alpha so high-flow corridors (e.g., NJ-PA, DC-VA-MD) intensify.

Inputs
------
  national/data/processed/county_summary.csv         (Panel A fill data)
  national/data/processed/top_hospitals.csv          (Panel B markers)
  national/data/processed/hospitals_geocoded.parquet (Panel B marker positions; lat/lon)
  national/data/processed/zones_classified.parquet   (Panel B arcs: filter cross_state==True;
                                                       BG centroid -> T1_PCI lat/lon)
  national/data/raw/tiger_county/cb_2023_us_county_5m.zip  (county base for both panels)
  national/data/raw/cenpop2020/CenPop2020_Mean_BG.txt      (BG centroids for arc origins)

Output
------
  national/outputs/figures/choropleth_two_panel.png  (300 DPI; figsize ~ (14, 6))
  national/outputs/figures/choropleth_two_panel.svg

Connecticut treatment
---------------------
Same data-vintage gap applies. Two options:
  1. Carry the same CT note as 08_choropleth.py.
  2. Implement the 2020-county -> 2023-planning-region crosswalk first
     and produce a fully-shaded version. Census publishes the relationship
     file; the BG-to-planning-region mapping is exact (planning regions
     are unions of historical CT counties at BG resolution).
The proper fix (#2) is a 30-minute job and should land before this
two-panel figure goes into a manuscript Figure 1.

Design references
-----------------
  - Style cues taken from the user's clinical-decision-aid 4-panel figure
    upload (2026-05-09): serif bold headers, italic muted subtitles,
    monospace metrics rows, clean white card-like backgrounds, restrained
    color palette. The categorical color choices in that figure (green /
    orange / pink / blue) do not transfer to a sequential choropleth, but
    the typographic hierarchy and aesthetic discipline do.
  - ESC / JACC editorial aesthetic: white background, gold-red sequential
    ramp for Panel A, subtle county outlines, no basemap tiles.

Implementation order when picked up
-----------------------------------
  1. Add CT crosswalk preparation to 01b_prepare_acs_age.py (or a new
     01c_ct_crosswalk.py) so Panel A renders fully.
  2. Build Panel A as a callable function in 08_choropleth.py that takes
     an axes argument; refactor the script so single-panel and two-panel
     share the rendering logic.
  3. Build Panel B in this file: load top_hospitals.csv, geocode (already
     done — hospitals_geocoded.parquet), plot markers; load zones_classified
     for cross-state arcs; render bezier curves with additive alpha.
  4. Compose the two-panel figure with shared title, individual subtitles,
     shared legend strip at the bottom.

Until this is built
-------------------
The single-panel population-weighted choropleth at
`outputs/figures/choropleth_competitive_zones.png` is the current
publication figure. This file exists only as a design record so a
future session can resume from a concrete plan.
"""
from __future__ import annotations

import sys


def main():
    print("08b_choropleth_two_panel.py is a design stub; not yet implemented.")
    print("See module docstring for design notes.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
