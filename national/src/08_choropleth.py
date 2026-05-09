"""County-level choropleth: % of CONUS adults in 15-minute PCI competitive catchment zones.

The single figure for the AHA Scientific Sessions abstract.

Metric (per pre_registration.md Amendment 2026-05-08-C):
    pct_adults_in_competitive = competitive_adult_pop / total_adult_pop x 100
    where adult_pop = ACS 2019-2023 5-year, table B01001, ages 20+, summed
    over all CONUS BGs in each county.

This is the population-weighted equivalent of the earlier `pct_bgs_competitive`
metric. The two are visually similar (both mostly red in metros, mostly tan
in rural areas) but the population-weighted version is the metric the v9
abstract anchors to ('79% of U.S. STEMI cases'); it is also what the
abstract's Results sentence makes claims about. Switching from BG-share to
adult-share aligns the supporting figure with the headline.

Inputs:
  national/data/processed/county_summary.csv         (3,108 CONUS counties; columns
                                                       total_adult_pop and competitive_adult_pop)
  national/data/raw/tiger_county/cb_2023_us_county_5m.zip (TIGER cartographic boundary)

Outputs:
  national/outputs/figures/choropleth_competitive_zones.png  (300 DPI)
  national/outputs/figures/choropleth_competitive_zones.svg  (vector)

Design choices:
  - Gold -> red ramp on white background (per proposal §5 Figure 1 specification;
    sequential variable maps best to a sequential ramp)
  - Albers Equal Area Conic projection (standard for CONUS thematic mapping)
  - No basemap tiles (clean, publishable, no third-party visual dependency)
  - Serif title; italic muted subtitle; monospace-style sources line; clean
    white background and thin county boundaries
  - Legend with explicit cutoff bins (0, 25, 50, 75, 100)
"""
from __future__ import annotations

import io
import zipfile
from pathlib import Path

import matplotlib
matplotlib.use("Agg")  # headless
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import matplotlib.patches as mpatches
from matplotlib.colors import LinearSegmentedColormap
import numpy as np
import pandas as pd
import shapefile  # pyshp
from pyproj import Transformer

REPO = Path(__file__).resolve().parents[2]

NON_CONUS_FIPS = {"02", "15", "60", "66", "69", "72", "78"}


def load_counties_with_data():
    """Load TIGER counties, project to Albers Equal Area, attach county_summary."""
    zip_path = REPO / "national" / "data" / "raw" / "tiger_county" / "cb_2023_us_county_5m.zip"
    csv_path = REPO / "national" / "data" / "processed" / "county_summary.csv"

    summary = pd.read_csv(csv_path, dtype={"county_fips": str})
    # Population-weighted metric (Amendment 2026-05-08-C). Counties with zero
    # adult population (rare; effectively never in CONUS) would divide by zero;
    # mask them as NaN so they render unshaded rather than as 0 or inf.
    with pd.option_context("mode.chained_assignment", None):
        denom = summary["total_adult_pop"].replace(0, np.nan)
        summary["pct_adults_in_competitive"] = (
            summary["competitive_adult_pop"] / denom * 100
        ).round(2)
    summary_dict = dict(zip(summary["county_fips"], summary["pct_adults_in_competitive"]))

    # Albers Equal Area Conic for CONUS
    transformer = Transformer.from_crs(
        "EPSG:4269",  # NAD83 (TIGER)
        "+proj=aea +lat_1=29.5 +lat_2=45.5 +lat_0=37.5 +lon_0=-96 +x_0=0 +y_0=0 +datum=NAD83 +units=m +no_defs",
        always_xy=True,
    )

    counties = []
    state_polys = {}  # statefp -> list of polygon rings (for state outlines)

    with zipfile.ZipFile(zip_path) as z:
        shp = io.BytesIO(z.read("cb_2023_us_county_5m.shp"))
        shx = io.BytesIO(z.read("cb_2023_us_county_5m.shx"))
        dbf = io.BytesIO(z.read("cb_2023_us_county_5m.dbf"))
        sf = shapefile.Reader(shp=shp, shx=shx, dbf=dbf)
        fields = [f[0] for f in sf.fields[1:]]

        for shape_rec in sf.shapeRecords():
            d = dict(zip(fields, shape_rec.record))
            statefp = d["STATEFP"]
            if statefp in NON_CONUS_FIPS:
                continue
            geoid = d["GEOID"]
            value = summary_dict.get(geoid, np.nan)

            # Project the polygon's points
            pts = np.array(shape_rec.shape.points)
            if len(pts) == 0:
                continue
            x, y = transformer.transform(pts[:, 0], pts[:, 1])
            projected_pts = np.column_stack([x, y])
            parts = list(shape_rec.shape.parts) + [len(pts)]

            polygons = []
            for i in range(len(parts) - 1):
                ring = projected_pts[parts[i]:parts[i + 1]]
                polygons.append(ring)

            counties.append({
                "geoid": geoid,
                "statefp": statefp,
                "polygons": polygons,
                "value": value,
            })

            state_polys.setdefault(statefp, []).extend(polygons)

    return counties, state_polys


def build_state_outlines(state_polys):
    """Dissolve county boundaries within each state into outer state outlines.

    Quick approximation: use a fine grid + matplotlib.path; cheap alternative
    is just to plot the union of county polygons with a transparent fill and
    a thicker stroke. Simpler: use TIGER state shapefile if available.
    For this figure, we'll plot all county boundaries thinly and overlay
    state-level boundary by drawing the union of polygons that share a state
    edge. Simplification: just draw all county outlines very thin, then
    redraw the state boundary by detecting county-county boundaries that
    cross state lines... too complex. Easier: load the state shapefile.

    For this version we'll use a simple approach: draw counties in light-gray
    edges, then nothing else for state boundaries — visually OK at this scale.
    """
    return None


def plot_choropleth():
    print("loading counties + projecting...")
    counties, state_polys = load_counties_with_data()
    print(f"  {len(counties)} CONUS county shapes loaded and projected to Albers")

    # Color ramp: white → gold → red
    # Anchor stops align to the abstract finding visually
    cmap = LinearSegmentedColormap.from_list(
        "white_gold_red",
        [(0.0, "#FFFFFF"),
         (0.25, "#FAEEDC"),
         (0.50, "#C8A84B"),  # gold (per proposal aesthetic)
         (0.75, "#A0431F"),
         (1.00, "#C62828")],  # red (per proposal aesthetic)
    )

    fig, ax = plt.subplots(figsize=(13, 8.5), dpi=150)
    fig.patch.set_facecolor("white")
    ax.set_facecolor("white")

    # Plot county polygons colored by competitive %
    n_with_data = 0
    for c in counties:
        v = c["value"]
        if pd.notna(v):
            color = cmap(v / 100)
            n_with_data += 1
        else:
            color = "#EEEEEE"
        for ring in c["polygons"]:
            patch = mpatches.Polygon(ring, closed=True, facecolor=color,
                                      edgecolor="#999999", linewidth=0.15)
            ax.add_patch(patch)

    print(f"  {n_with_data} counties with summary data, {len(counties) - n_with_data} without")

    # Set extent to CONUS bounds in Albers EA
    ax.set_xlim(-2_500_000, 2_500_000)
    ax.set_ylim(-1_700_000, 1_500_000)
    ax.set_aspect("equal")
    ax.axis("off")

    # Title (serif, bold, near-black) and subtitle (italic, muted blue-gray)
    fig.text(0.5, 0.95,
             "U.S. counties by share of adults in 15-minute PCI competitive catchment zones",
             ha="center", va="top",
             fontsize=14, fontweight="bold",
             family="serif", color="#1A1E2E")
    fig.text(0.5, 0.91,
             "Free-flow road-network drive-time geometry  ·  4,408 hospitals  ·  248 million CONUS adults aged 20+",
             ha="center", va="top",
             fontsize=10, color="#4A5270", style="italic")

    # Legend / colorbar
    legend_ax = fig.add_axes([0.22, 0.10, 0.56, 0.022])
    norm = mcolors.Normalize(vmin=0, vmax=100)
    cb = matplotlib.colorbar.ColorbarBase(legend_ax, cmap=cmap, norm=norm,
                                          orientation="horizontal")
    cb.set_label("% of county's adults in 15-min competitive zone",
                 fontsize=9, color="#1A1E2E", labelpad=4)
    cb.ax.tick_params(labelsize=8)
    cb.set_ticks([0, 25, 50, 75, 100])

    # Source attribution. Monospace family echoes the upload-style "metrics"
    # line aesthetic and signals "data provenance" rather than narrative prose.
    # Connecticut is now rendered fully via the BG-level spatial-join crosswalk
    # (national/src/01c_ct_planning_region_crosswalk.py + 07_aggregate.py CT
    # remap); no CT-vintage-gap note needed in the figure.
    fig.text(0.5, 0.030,
             "Sources: CMS Provider of Services (Dec 2024)  ·  Census CenPop 2020  ·  "
             "ACS 2019–2023 5-year (B01001)\n"
             "OpenStreetMap (Geofabrik US, May 2026)  ·  OSRM road-network routing  ·  "
             "github.com/rgaiba/stemi-fmc-to-device",
             ha="center", va="bottom",
             fontsize=7.5, color="#777777", family="monospace",
             linespacing=1.6)

    out_dir = REPO / "national" / "outputs" / "figures"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_png = out_dir / "choropleth_competitive_zones.png"
    out_svg = out_dir / "choropleth_competitive_zones.svg"

    fig.savefig(out_png, dpi=300, bbox_inches="tight",
                facecolor=fig.get_facecolor(), edgecolor="none")
    fig.savefig(out_svg, bbox_inches="tight",
                facecolor=fig.get_facecolor(), edgecolor="none")
    plt.close(fig)

    print(f"saved: {out_png}  ({out_png.stat().st_size/1e6:.2f} MB)")
    print(f"saved: {out_svg}  ({out_svg.stat().st_size/1e6:.2f} MB)")


if __name__ == "__main__":
    plot_choropleth()
