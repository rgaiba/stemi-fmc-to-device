#!/usr/bin/env python3
"""
optimize_posts.py — p-median optimization of ambulance post locations
for population-weighted minimum response time across Delaware census
block groups.

This is the System Status Management (SSM) framing: we are NOT siting
new fixed stations. We are choosing where to *post* mobile ambulances
between calls to minimize expected response time. The candidate site
set is a coarse grid over Delaware; the model picks N grid points to
serve as posts.

The output is a JSON file that the React app reads to render the
"current vs optimal" comparison.

Usage:
    pip install pulp --break-system-packages
    python scripts/optimize_posts.py

The script writes:
    src/data/postOptimization.json
"""

from __future__ import annotations

import json
import math
import re
from pathlib import Path

# ── load the demand layer (block groups) ────────────────────────────────────
ROOT = Path(__file__).resolve().parent.parent
BG_PATH = ROOT / 'src' / 'data' / 'blockGroups.js'
POSTS_PATH = ROOT / 'src' / 'data' / 'emsPosts.js'
OUT_PATH = ROOT / 'src' / 'data' / 'postOptimization.json'


def parse_js_array_of_triples(text: str, name: str) -> list[tuple[float, float, float]]:
    """Pull `export const NAME = [[a,b,c],[...]];` and return [(a,b,c),...]."""
    m = re.search(rf'export const {name}\s*=\s*\[(.*?)\];', text, re.DOTALL)
    if not m:
        raise RuntimeError(f'could not find {name} in JS source')
    body = m.group(1)
    triples = re.findall(r'\[(-?\d+\.?\d*),(-?\d+\.?\d*),(-?\d+\.?\d*)\]', body)
    return [(float(a), float(b), float(c)) for a, b, c in triples]


def parse_posts(text: str) -> list[dict]:
    posts = []
    for m in re.finditer(
        r"\{\s*id:\s*'([^']+)',\s*name:\s*'([^']+)',\s*city:\s*'([^']+)',\s*"
        r"county:\s*'([^']+)',\s*lat:\s*(-?\d+\.\d+),\s*lon:\s*(-?\d+\.\d+),\s*"
        r"shift:\s*'([^']+)'\s*\}",
        text,
    ):
        posts.append({
            'id': m.group(1),
            'name': m.group(2),
            'city': m.group(3),
            'county': m.group(4),
            'lat': float(m.group(5)),
            'lon': float(m.group(6)),
            'shift': m.group(7),
        })
    return posts


bg_text = BG_PATH.read_text()
posts_text = POSTS_PATH.read_text()

bg_triples = parse_js_array_of_triples(bg_text, 'RAW_BLOCK_GROUPS')
demand = [{'p': int(p), 'lat': lat, 'lon': lon} for p, lat, lon in bg_triples]
all_posts = parse_posts(posts_text)
current_posts = [p for p in all_posts if p['shift'] == 'full']

print(f'Loaded {len(demand)} block groups, {len(all_posts)} posts ({len(current_posts)} full-time)')


# ── distance + time model ───────────────────────────────────────────────────
def haversine_miles(lat1, lon1, lat2, lon2):
    R = 3958.8
    D = math.pi / 180
    dL = (lat2 - lat1) * D
    dN = (lon2 - lon1) * D
    a = math.sin(dL / 2) ** 2 + math.cos(lat1 * D) * math.cos(lat2 * D) * math.sin(dN / 2) ** 2
    return 2 * R * math.asin(math.sqrt(a))


# v1 driving model: haversine × 1.35 detour @ 45 mph average
DETOUR = 1.35
SPEED = 45  # mph


def drive_minutes(lat1, lon1, lat2, lon2):
    return haversine_miles(lat1, lon1, lat2, lon2) * DETOUR / SPEED * 60


# ── STEMI incidence weighting ───────────────────────────────────────────────
# We don't have block-group-level age data here, so demand weight = population.
# (Refining to age-stratified incidence is a follow-up; the relative ranking
# of optimal posts is dominated by population density at this scale.)

for d in demand:
    d['weight'] = d['p']

total_weight = sum(d['weight'] for d in demand)


# ── candidate site grid ─────────────────────────────────────────────────────
# Coarse grid covering Delaware land area. Filter to points within ~5 mi of
# any existing block-group centroid (drops over-water and out-of-state cells).
GRID_STEP = 0.05  # ~3.5 mi N-S, ~2.7 mi E-W at this latitude

bg_lats = [d['lat'] for d in demand]
bg_lons = [d['lon'] for d in demand]
min_lat = min(bg_lats) - 0.05
max_lat = max(bg_lats) + 0.05
min_lon = min(bg_lons) - 0.05
max_lon = max(bg_lons) + 0.05

raw_grid = []
lat = min_lat
while lat <= max_lat:
    lon = min_lon
    while lon <= max_lon:
        raw_grid.append((lat, lon))
        lon += GRID_STEP
    lat += GRID_STEP


def near_demand(lat, lon, max_mi=5.0):
    for d in demand:
        if haversine_miles(lat, lon, d['lat'], d['lon']) < max_mi:
            return True
    return False


candidates = [(lat, lon) for lat, lon in raw_grid if near_demand(lat, lon)]
print(f'Candidate grid: {len(candidates)} points (from {len(raw_grid)} raw, after near-demand filter)')


# ── solve p-median ──────────────────────────────────────────────────────────
# Minimize sum_i sum_j w_i * d(i, j) * x_{ij}  subject to:
#   sum_j y_j = N
#   sum_j x_{ij} = 1   for each demand i
#   x_{ij} <= y_j      for each i,j
#   x, y in {0,1}
#
# This LP-relaxes well; CBC handles it in seconds for our scale.
N_POSTS = len(current_posts)
print(f'Optimizing for N = {N_POSTS} posts')

try:
    import pulp
except ImportError:
    raise SystemExit('PuLP not installed. Run: pip install pulp --break-system-packages')


prob = pulp.LpProblem('post_placement', pulp.LpMinimize)

# Decision vars
y = pulp.LpVariable.dicts('y', range(len(candidates)), cat='Binary')
# Continuous assignment is fine for p-median (LP relaxation is integer-valued at optimum)
x = pulp.LpVariable.dicts('x',
                          ((i, j) for i in range(len(demand)) for j in range(len(candidates))),
                          lowBound=0, upBound=1, cat='Continuous')

# Precompute distances
dist = [[drive_minutes(d['lat'], d['lon'], c[0], c[1]) for c in candidates] for d in demand]

# Objective
prob += pulp.lpSum(
    demand[i]['weight'] * dist[i][j] * x[(i, j)]
    for i in range(len(demand))
    for j in range(len(candidates))
)

# N posts
prob += pulp.lpSum(y[j] for j in range(len(candidates))) == N_POSTS

# Each demand assigned somewhere
for i in range(len(demand)):
    prob += pulp.lpSum(x[(i, j)] for j in range(len(candidates))) == 1

# Assignment only to opened posts
for i in range(len(demand)):
    for j in range(len(candidates)):
        prob += x[(i, j)] <= y[j]

print('Solving (CBC, may take 30-90 sec)...')
solver = pulp.PULP_CBC_CMD(msg=0, timeLimit=300)
prob.solve(solver)
print(f'Status: {pulp.LpStatus[prob.status]}, obj = {pulp.value(prob.objective):.0f} weighted-min-mi-min')

optimal_posts = [
    {'lat': candidates[j][0], 'lon': candidates[j][1]}
    for j in range(len(candidates))
    if pulp.value(y[j]) > 0.5
]
print(f'Selected {len(optimal_posts)} optimal post locations')


# ── compute mean response time for both layouts ─────────────────────────────
def assign_and_score(posts):
    detail = []
    total_weighted = 0.0
    for d in demand:
        best = min(drive_minutes(d['lat'], d['lon'], p['lat'], p['lon']) for p in posts)
        detail.append({'lat': d['lat'], 'lon': d['lon'], 'p': d['p'], 'mins': best})
        total_weighted += d['weight'] * best
    mean = total_weighted / total_weight
    return mean, detail


current_mean, current_detail = assign_and_score(current_posts)
optimal_mean, optimal_detail = assign_and_score(optimal_posts)

print(f'Mean response time — current: {current_mean:.2f} min')
print(f'Mean response time — optimal: {optimal_mean:.2f} min')
print(f'Delta: {current_mean - optimal_mean:.2f} min ({(current_mean - optimal_mean) / current_mean * 100:.1f}%)')


# ── save ────────────────────────────────────────────────────────────────────
def summarize_layout(detail):
    """Return percent within thresholds (8 and 12 minutes)."""
    tot_w = sum(d['p'] for d in detail)
    w8 = sum(d['p'] for d in detail if d['mins'] <= 8)
    w12 = sum(d['p'] for d in detail if d['mins'] <= 12)
    return {
        'meanMins': round(sum(d['p'] * d['mins'] for d in detail) / tot_w, 2),
        'pct8': round(w8 / tot_w * 100, 1),
        'pct12': round(w12 / tot_w * 100, 1),
        'totalPop': tot_w,
    }


output = {
    'modelVersion': 'v1-haversine',
    'detourFactor': DETOUR,
    'speedMph': SPEED,
    'gridStepDeg': GRID_STEP,
    'nPosts': N_POSTS,
    'current': {
        'posts': [
            {'id': p['id'], 'name': p['name'], 'city': p['city'], 'county': p['county'],
             'lat': p['lat'], 'lon': p['lon']}
            for p in current_posts
        ],
        'summary': summarize_layout(current_detail),
        'detail': [
            {'lat': round(d['lat'], 4), 'lon': round(d['lon'], 4), 'p': d['p'], 'mins': round(d['mins'], 2)}
            for d in current_detail
        ],
    },
    'optimal': {
        'posts': [{'lat': round(p['lat'], 4), 'lon': round(p['lon'], 4)} for p in optimal_posts],
        'summary': summarize_layout(optimal_detail),
        'detail': [
            {'lat': round(d['lat'], 4), 'lon': round(d['lon'], 4), 'p': d['p'], 'mins': round(d['mins'], 2)}
            for d in optimal_detail
        ],
    },
}

OUT_PATH.write_text(json.dumps(output, indent=2))
print(f'Wrote {OUT_PATH}')
