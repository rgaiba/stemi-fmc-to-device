"""
Figure 3 — Population distribution of T₂ − T₁: national cumulative (A)
and regional IQR (B).

ANALYTICAL DECISIONS recorded in manuscript/T2_minus_T1/ANALYTICAL_DECISIONS.md
govern this figure. Decisions 5, 7, and 8 are binding:
  - AHA Statistical Update reporting conventions (absolute counts;
    population-weighted quantiles; no naked percentages).
  - Thesis is the population-redundancy measurement: 122 million adults at
    T₂ − T₁ ≤ 5 min; 2.24 million in 1-PCI no-redundancy stratum.
  - Three primary figures, two-panel each. Figure 3 holds the population
    distribution story in two panels: national cumulative (A) and regional
    IQR (B).

Composition matches STEMI_Routing_Figure1 and ..._Figure2 exactly:
DejaVu Sans typography, NAVY primary text, MUTED subtitle prose, rounded
NAVY-bordered container per panel, common definitional footer below.
AHA Circulation double-column dimensions: 7.09 × 9.2 in.
"""
from pathlib import Path
import glob as _glob

import numpy as np
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Rectangle

# ============================================================
#  Palette / typography — IDENTICAL to figure1/2.py
# ============================================================
NAVY    = "#1A2733"
MUTED   = "#6B7280"
SLATE   = "#475569"
CO_LINE = "#D1D5DB"
BOX_FILL = "#C5DCD9"   # Panel B box fill — light teal
BOX_EDGE = "#1F4D3F"   # Panel B box edge — dark teal

# Wong / IBM colorblind-safe 4-region palette (Panel A regional overlays)
REGION_COLOR = {
    "Northeast": "#0072B2",
    "Midwest":   "#009E73",
    "South":     "#D55E00",
    "West":      "#CC79A7",
}

mpl.rcParams.update({
    "font.family":     "DejaVu Sans",
    "font.weight":     "regular",
    "axes.edgecolor":  NAVY,
    "axes.labelcolor": NAVY,
    "text.color":      NAVY,
    "pdf.fonttype":    42,
    "ps.fonttype":     42,
})

_HOST = Path("/Users/rahulgaiba/Documents/Claude/Projects/PCI times")
_sbox_matches = _glob.glob("/sessions/*/mnt/PCI times")
_SBOX = Path(_sbox_matches[0]) if _sbox_matches else Path(
    "/sessions/pensive-gifted-brahmagupta/mnt/PCI times"
)
ROOT = _HOST if _HOST.exists() else _SBOX
REPO = ROOT / "stemi-fmc-to-device"

# ============================================================
#  Data
# ============================================================
NON_CONUS = {"02", "15", "60", "66", "69", "72", "78"}

FIPS2STATE = {
    "01":"AL","04":"AZ","05":"AR","06":"CA","08":"CO","09":"CT","10":"DE","11":"DC",
    "12":"FL","13":"GA","16":"ID","17":"IL","18":"IN","19":"IA","20":"KS","21":"KY",
    "22":"LA","23":"ME","24":"MD","25":"MA","26":"MI","27":"MN","28":"MS","29":"MO",
    "30":"MT","31":"NE","32":"NV","33":"NH","34":"NJ","35":"NM","36":"NY","37":"NC",
    "38":"ND","39":"OH","40":"OK","41":"OR","42":"PA","44":"RI","45":"SC","46":"SD",
    "47":"TN","48":"TX","49":"UT","50":"VT","51":"VA","53":"WA","54":"WV","55":"WI",
    "56":"WY",
}
REGION = {
    **dict.fromkeys(["CT","ME","MA","NH","RI","VT","NJ","NY","PA"], "Northeast"),
    **dict.fromkeys(["IL","IN","MI","OH","WI","IA","KS","MN","MO","NE","ND","SD"], "Midwest"),
    **dict.fromkeys(["DE","DC","FL","GA","MD","NC","SC","VA","WV",
                     "AL","KY","MS","TN","AR","LA","OK","TX"], "South"),
    **dict.fromkeys(["AZ","CO","ID","MT","NV","NM","UT","WY","CA","OR","WA"], "West"),
}

print("Loading zones_classified.parquet ...")
z = pd.read_parquet(REPO / "national/data/processed/zones_classified.parquet")
z = z[~z["STATEFP"].isin(NON_CONUS)].copy()
z["gap_min"] = z["competitive_margin_sec"] / 60.0
z["T1_min"]  = z["drive_t1_pci_sec"] / 60.0
z["state"]   = z["STATEFP"].map(FIPS2STATE)
z["region"]  = z["state"].map(REGION)
two_pci = z[z["gap_min"].notna()].copy()

one_pci_adults = int(z.loc[z["gap_min"].isna() & z["T1_min"].notna(),
                            "adult_pop_20plus"].sum())
no_pci_adults  = int(z.loc[z["T1_min"].isna(), "adult_pop_20plus"].sum())
total_adults   = int(z["adult_pop_20plus"].sum())

print(f"  CONUS adults ≥20      : {total_adults:,}")
print(f"  two-PCI stratum       : {int(two_pci['adult_pop_20plus'].sum()):,}")
print(f"  one-PCI (no-redundancy): {one_pci_adults:,}")
print(f"  no-PCI                : {no_pci_adults:,}")


# ============================================================
#  Helper functions
# ============================================================
def cumulative(df: pd.DataFrame) -> tuple[np.ndarray, np.ndarray]:
    s = df[["gap_min", "adult_pop_20plus"]].sort_values("gap_min")
    x = s["gap_min"].to_numpy()
    y = np.cumsum(s["adult_pop_20plus"].to_numpy()) / 1e6
    return x, y


def cum_at(x, y, threshold):
    idx = np.searchsorted(x, threshold, side="right") - 1
    return float(y[idx]) if idx >= 0 else 0.0


def wq(x: np.ndarray, w: np.ndarray, q: float) -> float:
    if len(x) == 0 or w.sum() <= 0:
        return np.nan
    order = np.argsort(x, kind="mergesort")
    xs, ws = x[order], w[order]
    cw = np.cumsum(ws)
    target = q * cw[-1]
    i = np.searchsorted(cw, target, side="left")
    if i == 0:    return float(xs[0])
    if i >= len(xs): return float(xs[-1])
    lo, hi = cw[i - 1], cw[i]
    if hi == lo: return float(xs[i])
    return float(xs[i - 1] + (target - lo) / (hi - lo) * (xs[i] - xs[i - 1]))


# ============================================================
#  Compute Panel A data
# ============================================================
x_nat, y_nat = cumulative(two_pci)
cum_5  = cum_at(x_nat, y_nat, 5.0)
cum_15 = cum_at(x_nat, y_nat, 15.0)
cum_30 = cum_at(x_nat, y_nat, 30.0)

REGION_CURVES = {r: cumulative(two_pci[two_pci["region"] == r])
                 for r in ["Northeast", "Midwest", "South", "West"]}


# ============================================================
#  Compute Panel B data (population-weighted quantiles per region)
# ============================================================
REGIONS = ["Northeast", "Midwest", "South", "West"]
stats = {}
for r in REGIONS:
    g = two_pci[two_pci["region"] == r]
    w = g["adult_pop_20plus"].to_numpy(float)
    x = g["gap_min"].to_numpy(float)
    stats[r] = dict(
        p05=wq(x, w, 0.05), p25=wq(x, w, 0.25), p50=wq(x, w, 0.50),
        p75=wq(x, w, 0.75), p95=wq(x, w, 0.95),
        adults=int(g["adult_pop_20plus"].sum()),
    )
nat_w = two_pci["adult_pop_20plus"].to_numpy(float)
nat_x = two_pci["gap_min"].to_numpy(float)
nat_med = wq(nat_x, nat_w, 0.5)


# ============================================================
#  Figure canvas — AHA Circulation double-column, two-panel vertical
#  stack matching figure1.py / figure2.py.
# ============================================================
fig = plt.figure(figsize=(7.09, 9.2), dpi=150)
fig.patch.set_facecolor("white")

LEFT    = 0.030
CON_X   = 0.070
CON_X_R = 0.930
CON_W   = CON_X_R - CON_X

# Vertical rhythm matched to Figures 1 and 2.
# NOTE: the PA_*/PB_* labels below refer to the CODE BLOCKS in this file
# (Panel A code = cumulative; Panel B code = regional IQR), but the
# *visible* panel markers and the geometry are now flipped so that the
# regional IQR (the primitive distributional view) renders at the TOP and
# the cumulative curve (the derived view) renders at the BOTTOM. Visible
# markers: regional = "A", cumulative = "B". The internal variable names
# (PA_/PB_, axA/axB, containerA/containerB) keep their original
# associations with the code blocks for clarity of maintenance.
# Layout matched to Figure 1: both containers 0.390 fig tall, equal
# caption-to-container gaps, breathing room above the top heading.
PA_TITLE_Y = 0.490    # cumulative code block -> BOTTOM slot title
PA_SUBT_Y  = 0.475    # (subtitle removed)
PA_CON_TOP = 0.460    # gap below title = 0.030
PA_CON_BOT = 0.070    # Panel B height = 0.390
                       # → Figure 3B caption placed at y=0.060

PB_TITLE_Y = 0.975    # top margin = 0.025
PB_SUBT_Y  = 0.955    # (subtitle removed)
PB_CON_TOP = 0.945    # gap below title = 0.030
PB_CON_BOT = 0.555    # Panel A height = 0.390 (identical to Panel B)
                       # → Figure 3A caption placed at y=0.545

# ============================================================
#  PANEL B (bottom slot) — National cumulative curve
# ============================================================
fig.text(LEFT, PA_TITLE_Y, "B",
         ha="left", va="top", fontsize=18, color=NAVY,
         family="DejaVu Sans", weight="bold")
fig.text(LEFT + 0.045, PA_TITLE_Y,
         "Cumulative U.S. Adult Population by Drive-Time Gap (T₂ − T₁)",
         ha="left", va="top", fontsize=13, color=NAVY,
         family="DejaVu Sans", weight="bold")
# (Panel B subtitle moved to bottom legend block as Figure 3B.)

containerA = FancyBboxPatch(
    (CON_X, PA_CON_BOT), CON_W, PA_CON_TOP - PA_CON_BOT,
    boxstyle="round,pad=0.0,rounding_size=0.012",
    transform=fig.transFigure,
    fc="none", ec=CO_LINE, lw=0.8, zorder=10,
)

# Uniform interior padding inside the container. Panel B's y-tick labels
# are wider (3 chars for "245" vs 2 chars for "50" in Panel A), which
# would push its y-axis label closer to the container border; we shift
# the axes right by 0.011 fig (~0.08 in) so the y-label gap matches
# Panel A's gap exactly.
A_LEFT  = CON_X + 0.111
A_RIGHT = CON_X_R - 0.060
A_BOT   = PA_CON_BOT + 0.077
# Top inset 0.060 (vs 0.045 prior) gives the legend a breathing band
# between the axes top and the container top — closer in proportion to
# the 0.077 bottom inset that the x-axis labels occupy.
A_TOP   = PA_CON_TOP - 0.060
axA = fig.add_axes([A_LEFT, A_BOT, A_RIGHT - A_LEFT, A_TOP - A_BOT])

# Reference vertical lines
for t in [5.0, 15.0, 30.0]:
    axA.axvline(t, ls=":", lw=0.7, color="#9CA3AF", zorder=1)

# Clip curve data to the visible x-range (0 to 60 min). Without this,
# matplotlib's tight bbox uses the FULL Line2D extent (>100 min) and
# inflates the saved canvas width by ~2x.
X_VIS_MAX = 60.0


def _clip(xv, yv):
    mask = xv <= X_VIS_MAX
    if mask.all():
        return xv, yv
    # Include the first point > X_VIS_MAX so the line reaches the edge,
    # then trim. Equivalent to a visual clip at x=X_VIS_MAX.
    idx = int(np.argmax(~mask))  # first False index
    return xv[: idx + 1], yv[: idx + 1]


# Regional overlays
for r, (xv, yv) in REGION_CURVES.items():
    xv_c, yv_c = _clip(xv, yv)
    axA.plot(xv_c, yv_c, color=REGION_COLOR[r], lw=1.2, zorder=2, label=r)

# National curve
x_nat_c, y_nat_c = _clip(x_nat, y_nat)
axA.plot(x_nat_c, y_nat_c, color=NAVY, lw=2.4, zorder=3, label="National")

# Annotated callouts (horizontal, white masking bboxes)
CALLOUT_OFFSETS = {5: (3.5, 0), 15: (4.0, 0), 30: (4.0, -22)}
for t, cumv in [(5, cum_5), (15, cum_15), (30, cum_30)]:
    pct = cumv * 1e6 / total_adults * 100
    dx, dy = CALLOUT_OFFSETS[t]
    axA.scatter([t], [cumv], s=22, color=NAVY, zorder=5, clip_on=False)
    axA.annotate(
        f"{cumv:.0f} M ({pct:.0f}%)",
        xy=(t, cumv),
        xytext=(t + dx, cumv + dy),
        fontsize=9, color=NAVY, family="DejaVu Sans", weight="semibold",
        ha="left", va="center",
        arrowprops=dict(arrowstyle="-", color=NAVY, lw=0.6,
                        shrinkA=2, shrinkB=2),
        bbox=dict(facecolor="white", edgecolor="none", pad=1.8),
        zorder=6,
    )

axA.set_xlim(0, 60)
axA.set_xticks([0, 5, 10, 15, 20, 25, 30, 40, 50, 60])
axA.set_xlabel("Drive-time gap to second-nearest PCI-capable hospital, T₂ − T₁ (min)",
               fontsize=10, color=NAVY, labelpad=6)
axA.set_ylim(0, 290)
axA.set_yticks([0, 50, 100, 150, 200, 245])
axA.set_yticklabels(["0", "50", "100", "150", "200", "245"])
axA.set_ylabel("Adults aged ≥20 (millions)",
               fontsize=10, color=NAVY, labelpad=6)

for s in ("top", "right"):
    axA.spines[s].set_visible(False)
for s in ("left", "bottom"):
    axA.spines[s].set_color(NAVY)
    axA.spines[s].set_linewidth(0.8)
axA.tick_params(colors=NAVY, labelsize=9)

leg = axA.legend(
    loc="upper center", bbox_to_anchor=(0.50, 1.08),
    frameon=False, fontsize=8.5,
    handlelength=1.4, handletextpad=0.4, ncol=5,
    columnspacing=1.3,
)
for text in leg.get_texts():
    text.set_color(NAVY)
    text.set_family("DejaVu Sans")

fig.patches.append(containerA)


# ============================================================
#  PANEL A (top slot) — Regional T₂ − T₁ box-and-whisker
# ============================================================
fig.text(LEFT, PB_TITLE_Y, "A",
         ha="left", va="top", fontsize=18, color=NAVY,
         family="DejaVu Sans", weight="bold")
fig.text(LEFT + 0.045, PB_TITLE_Y,
         "Regional Distribution of T₂ − T₁",
         ha="left", va="top", fontsize=13, color=NAVY,
         family="DejaVu Sans", weight="bold")
# (Panel A subtitle moved to bottom legend block as Figure 3A.)

containerB = FancyBboxPatch(
    (CON_X, PB_CON_BOT), CON_W, PB_CON_TOP - PB_CON_BOT,
    boxstyle="round,pad=0.0,rounding_size=0.012",
    transform=fig.transFigure,
    fc="none", ec=CO_LINE, lw=0.8, zorder=10,
)

# Uniform interior padding matched to Panel B for visual consistency.
B_LEFT  = CON_X + 0.100
B_RIGHT = CON_X_R - 0.060
B_BOT   = PB_CON_BOT + 0.077
# Top inset 0.060 mirrors Panel B (axA) for consistent vertical rhythm.
B_TOP   = PB_CON_TOP - 0.060
axB = fig.add_axes([B_LEFT, B_BOT, B_RIGHT - B_LEFT, B_TOP - B_BOT])

x_pos = np.arange(len(REGIONS))
box_half_width = 0.28
cap_half = 0.10

# National median reference (population-weighted, two-PCI stratum).
# Horizontal dotted line in a callout-orange that does not collide with
# the Wong palette region colors above; legend entry below labels it.
# Drawn at zorder=6 so it overlays the boxes for direct visual comparison.
NAT_MED_COLOR = "#F28E2B"
nat_med_line = axB.axhline(
    nat_med, ls=":", lw=1.5, color=NAT_MED_COLOR, zorder=6,
    label=f"National median ({nat_med:.1f} min)",
)

for i, r in enumerate(REGIONS):
    s = stats[r]
    xc = x_pos[i]
    # Whiskers
    axB.plot([xc, xc], [s["p05"], s["p25"]], color=BOX_EDGE, lw=1.1, zorder=3)
    axB.plot([xc, xc], [s["p75"], s["p95"]], color=BOX_EDGE, lw=1.1, zorder=3)
    axB.plot([xc - cap_half, xc + cap_half], [s["p05"], s["p05"]],
             color=BOX_EDGE, lw=1.1, zorder=3)
    axB.plot([xc - cap_half, xc + cap_half], [s["p95"], s["p95"]],
             color=BOX_EDGE, lw=1.1, zorder=3)
    # Box (Q1–Q3)
    rect = Rectangle((xc - box_half_width, s["p25"]),
                     2 * box_half_width, s["p75"] - s["p25"],
                     facecolor=BOX_FILL, edgecolor=BOX_EDGE,
                     linewidth=1.1, zorder=4)
    axB.add_patch(rect)
    # Median line
    axB.plot([xc - box_half_width, xc + box_half_width],
             [s["p50"], s["p50"]], color=BOX_EDGE, lw=2.0, zorder=5)
    # Label above the upper whisker
    axB.annotate(
        f"Med {s['p50']:.1f}\nIQR {s['p25']:.1f}–{s['p75']:.1f}",
        xy=(xc, s["p95"]),
        xytext=(xc, s["p95"] + 2.5),
        fontsize=8.0, color=NAVY, family="DejaVu Sans",
        ha="center", va="bottom",
        weight="semibold",
        linespacing=1.30,
    )

axB.set_xlim(-0.6, len(REGIONS) - 0.4)
axB.set_xticks(x_pos)
axB.set_xticklabels(REGIONS, fontsize=10, color=NAVY)
axB.set_xlabel("Census region", fontsize=10, color=NAVY, labelpad=6)

# Small negative margin so the low-percentile whisker caps (p05 ≈ 0.2–0.3
# min) render clearly above the x-axis line rather than overlapping it.
axB.set_ylim(-1.5, 50)
# Omit the "5" y-tick: the orange dotted national-median line already
# marks that level, and the tick label would crowd "0" only 5 units below.
axB.set_yticks([0, 10, 20, 30, 40, 50])
axB.set_ylabel("Drive-time gap T₂ − T₁ (minutes)",
               fontsize=10, color=NAVY, labelpad=6)

for s in ("top", "right"):
    axB.spines[s].set_visible(False)
for s in ("left", "bottom"):
    axB.spines[s].set_color(NAVY)
    axB.spines[s].set_linewidth(0.8)
axB.tick_params(colors=NAVY, labelsize=9)
# Remove x-axis tick marks for Panel A — the region category labels alone
# carry the categorical x-axis information; ticks are visual clutter.
axB.tick_params(axis="x", length=0)

# Legend for the orange dotted national-median reference, geometrically
# mirroring Panel B's legend: anchored at axes-fraction (0.50, 1.08) so
# it sits in the gap between the axes top and the rounded container top,
# directly under the panel title. Frameless, NAVY text, DejaVu Sans, with
# Panel B's handlelength and handletextpad values.
leg_b = axB.legend(
    handles=[nat_med_line],
    loc="upper center", bbox_to_anchor=(0.50, 1.08),
    frameon=False, fontsize=8.5,
    handlelength=1.4, handletextpad=0.4,
)
for text in leg_b.get_texts():
    text.set_color(NAVY)
    text.set_family("DejaVu Sans")

fig.patches.append(containerB)

# ============================================================
#  Common definitional footer — wrapped to lines that fit within the
#  AHA double-column width (7.09 in). Single fig.text block with \n
#  line breaks; placed at the same y-coordinate as Figures 1 and 2.
# ============================================================
# Figure 3A caption — placed directly below Panel A's container.
fig.text(CON_X, 0.545,
         "Figure 3A. Population-weighted T₂ − T₁ by Census region.  "
         "Boxes show interquartile range with\n"
         "median line; whiskers span the 5th–95th percentiles.",
         ha="left", va="top", fontsize=8.5, color=NAVY,
         family="DejaVu Sans", linespacing=1.35)

# Figure 3B caption + abbreviations — placed directly below Panel B's
# container.
fig.text(CON_X, 0.060,
         "Figure 3B. Cumulative U.S. adult population by T₂ − T₁; "
         "reference lines drawn at 5, 15, and 30 minutes.\n"
         "T₁, T₂ = drive time to nearest and second-nearest PCI hospital.  "
         "PCI = percutaneous coronary intervention.",
         ha="left", va="top", fontsize=8.5, color=NAVY,
         family="DejaVu Sans", linespacing=1.35)

# ============================================================
#  Save
# ============================================================
out_png = ROOT / "STEMI_Routing_Figure3.png"
out_pdf = ROOT / "STEMI_Routing_Figure3.pdf"
# Force the saved canvas to exactly the figsize so the dimensions match
# Figures 1 and 2 byte-for-byte regardless of any off-canvas extents.
from matplotlib.transforms import Bbox as _Bbox
_full = _Bbox.from_bounds(0, 0, *fig.get_size_inches())
fig.savefig(out_png, dpi=600, bbox_inches=_full,
            facecolor="white", pad_inches=0)
fig.savefig(out_pdf,           bbox_inches=_full,
            facecolor="white", pad_inches=0)
print("Wrote:", out_png)
print("Wrote:", out_pdf)
