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

    # Color ramp: single-hue deep teal sequential. Single hue varying in
    # darkness (white at low end, deep teal at high end). ACC and AHA primary
    # palettes are navy (ACC) and red (AHA); teal is the secondary accent
    # both organizations use in their journal layouts (JACC web header,
    # Circulation issue covers), which gives this figure a publication
    # idiom that fits the family without repeating the dominant Pantones.
    # Anchors:
    #   0%   white
    #   25%  pale teal-grey
    #   50%  medium teal
    #   75%  deep teal
    #   100% very deep teal (near forest)
    cmap = LinearSegmentedColormap.from_list(
        "deep_teal",
        [(0.00, "#FFFFFF"),
         (0.25, "#C5DCD9"),
         (0.50, "#5C9690"),
         (0.75, "#1F5651"),
         (1.00, "#062E2A")],
    )

    fig, ax = plt.subplots(figsize=(13, 8.5), dpi=150)
    fig.patch.set_facecolor("white")
    ax.set_facecolor("white")
    # Layout (figure-relative coordinates).
    # Subtitle moved BELOW the map. Reading flow: title (question) -> map
    # (answer) -> subtitle (stakes) -> metrics (numbers) -> sources
    # (provenance). Standard scientific-figure caption order; gives the
    # title room to breathe and lets the map expand vertically.
    #
    #   Title (2 lines)  y=0.97   (17pt serif bold; descends to ~y=0.90)
    #   Map              [0.095, 0.17, 0.725, 0.71]  (top ~y=0.88)
    #   Colorbar (V)     [0.860, 0.32, 0.020, 0.42]  (right of map; gap 0.040)
    #   Colorbar header  y=0.755  ("% of county's adults")
    #   Subtitle         y=0.135  (italic 10pt; below map, above metrics)
    #   Metrics line     y=0.080  (single line, monospace, bold)
    #   Sources          y=0.020  (two lines, monospace)
    #
    # Centering math: data is CONUS in Albers (xrange 5M, yrange 3.2M,
    # aspect 1.5625). Axes box width matches data aspect (no whitespace
    # inside axes):
    #     axes_height_in = 0.71 * 8.5 = 6.035"
    #     axes_width_in  = 6.035 * 1.5625 = 9.43"
    #     axes_width_fig = 9.43 / 13 = 0.725
    # Whole (map + 0.04 gap + 0.020 colorbar + ~0.025 tick labels) block
    # has width ~0.810; centered means map left = (1.0 - 0.810) / 2 = 0.095.
    ax.set_position([0.095, 0.17, 0.725, 0.71])

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

    # Title (serif, bold, near-black). 17pt. Hook + descriptor format split
    # across two lines: line 1 ("Where EMS routing matters in STEMI:")
    # delivers the stakes; line 2 names the underlying metric.
    fig.text(0.5, 0.97,
             "Where EMS routing matters in STEMI:\n"
             "U.S. counties by share of adults with two PCI hospitals within 15 minutes of each other",
             ha="center", va="top",
             fontsize=17, fontweight="bold",
             family="serif", color="#1A1E2E",
             linespacing=1.15)
    # Subtitle moved BELOW the map (y=0.135) per layout revision.
    # Sits between the map (bottom y=0.17) and the metrics line (y=0.080).
    fig.text(0.5, 0.135,
             "Areas where routing to the hospital with shorter "
             "door-to-balloon time may shorten time to reperfusion after STEMI",
             ha="center", va="top",
             fontsize=10, color="#4A5270", style="italic")

    # Vertical colorbar on the right side of the map. Height matches the
    # enlarged map; reads as a scale beside the data rather than a band
    # beneath it. Tick labels go on the right by matplotlib default.
    # Position: x = map_left (0.121) + map_width (0.674) + gap (0.040) = 0.835
    # Position aligned to new map: x = map_left (0.095) + map_width (0.725)
    # + gap (0.040) = 0.860. Height fits the taller map (0.71).
    legend_ax = fig.add_axes([0.860, 0.32, 0.020, 0.42])
    norm = mcolors.Normalize(vmin=0, vmax=100)
    cb = matplotlib.colorbar.ColorbarBase(legend_ax, cmap=cmap, norm=norm,
                                          orientation="vertical")
    cb.ax.tick_params(labelsize=8)
    cb.set_ticks([0, 25, 50, 75, 100])
    # Header above the vertical colorbar — centered on colorbar (x=0.870).
    fig.text(0.870, 0.755,
             "% of county's\nadults",
             ha="center", va="bottom",
             fontsize=9, color="#1A1E2E", linespacing=1.2)

    # Metrics line (monospace, single line, BOLD). Bolded so the headline
    # patient count reads as a callout. "Drive times" (was "free-flow drive
    # times") — the free-flow caveat is documented in the manuscript
    # Methods/limitations rather than in the figure. "Areas" matches the
    # subtitle's wording.
    fig.text(0.5, 0.080,
             "~196,000 STEMI patients/yr in these areas  ·  "
             "1,598 PCI-capable hospitals  ·  drive times",
             ha="center", va="bottom",
             fontsize=8.5, color="#1A1E2E", family="monospace",
             fontweight="bold")

    # Source attribution. Smaller, lighter; lives at the bottom of the figure.
    # Connecticut is rendered fully via the BG-level spatial-join crosswalk
    # (01c_ct_planning_region_crosswalk.py + 07_aggregate.py CT remap); no
    # CT-vintage-gap note needed in the figure.
    fig.text(0.5, 0.020,
             "Sources: CMS Provider of Services (Dec 2024)  ·  Census CenPop 2020  ·  "
             "ACS 2019–2023 5-year (B01001)\n"
             "OpenStreetMap (Geofabrik US, May 2026)  ·  OSRM road-network routing  ·  "
             "github.com/rgaiba/stemi-fmc-to-device",
             ha="center", va="bottom",
             fontsize=7, color="#888888", family="monospace",
             linespacing=1.7)

    out_dir = REPO / "national" / "outputs" / "figures"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_png = out_dir / "choropleth_competitive_zones.png"
    out_svg = out_dir / "choropleth_competitive_zones.svg"
    out_pdf = out_dir / "choropleth_competitive_zones.pdf"

    # NOTE: deliberately not using bbox_inches="tight" — explicit element
    # positioning above relies on figure-relative coordinates that get
    # distorted by tight cropping. Save with the figure's actual canvas.
    fig.savefig(out_png, dpi=300,
                facecolor=fig.get_facecolor(), edgecolor="none")
    fig.savefig(out_svg,
                facecolor=fig.get_facecolor(), edgecolor="none")
    fig.savefig(out_pdf,
                facecolor=fig.get_facecolor(), edgecolor="none")
    plt.close(fig)

    print(f"saved: {out_png}  ({out_png.stat().st_size/1e6:.2f} MB)")
    print(f"saved: {out_svg}  ({out_svg.stat().st_size/1e6:.2f} MB)")
    print(f"saved: {out_pdf}  ({out_pdf.stat().st_size/1e6:.2f} MB)")


if __name__ == "__main__":
    plot_choropleth()
