// Pure helpers: projection, haversine distance, drive-time estimate, color ramp.

import { BLOCK_GROUPS } from '../data/blockGroups.js';

export const SVG_W = 560;
export const SVG_H = 900;
export const PAD = 38;

const ALL_HOSP_LATS = [39.6889, 39.7459, 39.1404, 38.9398, 38.7759, 38.3600, 38.7742];
const ALL_HOSP_LONS = [-75.6779, -75.5489, -75.5095, -75.4509, -75.1428, -75.5886, -76.0677];

const allLats = BLOCK_GROUPS.map((d) => d.lat).concat(ALL_HOSP_LATS);
const allLons = BLOCK_GROUPS.map((d) => d.lon).concat(ALL_HOSP_LONS);

const minLat = Math.min(...allLats) - 0.05;
const maxLat = Math.max(...allLats) + 0.05;
const minLon = Math.min(...allLons) - 0.05;
const maxLon = Math.max(...allLons) + 0.05;

const midLat = (minLat + maxLat) / 2;
const lonScale = Math.cos((midLat * Math.PI) / 180);
const lonSpan = maxLon - minLon;
const latSpan = maxLat - minLat;
const innerW = SVG_W - PAD * 2;
const innerH = SVG_H - PAD * 2;
const sx = innerW / (lonSpan * lonScale);
const sy = innerH / latSpan;
const sc = Math.min(sx, sy);
const drawW = lonSpan * lonScale * sc;
const drawH = latSpan * sc;
const offX = PAD + (innerW - drawW) / 2;
const offY = PAD + (innerH - drawH) / 2;

export function project(lat, lon) {
  return {
    x: offX + (lon - minLon) * lonScale * sc,
    y: offY + (maxLat - lat) * sc,
  };
}

export const PROJECTION_BOUNDS = { minLat, maxLat, minLon, maxLon };

// Great-circle distance in miles.
export function haversineMiles(lat1, lon1, lat2, lon2) {
  const R = 3958.8;
  const D = Math.PI / 180;
  const dL = (lat2 - lat1) * D;
  const dN = (lon2 - lon1) * D;
  const a =
    Math.sin(dL / 2) ** 2 +
    Math.cos(lat1 * D) * Math.cos(lat2 * D) * Math.sin(dN / 2) ** 2;
  return 2 * R * Math.asin(Math.sqrt(a));
}

// Approximate driving minutes: straight-line × detour factor ÷ avg speed.
const DETOUR = 1.35;
const SPEED = 45; // mph
export const MAX_MIN = 35;

export function computeAccessTimes(hospitals) {
  return BLOCK_GROUPS.map((d) => {
    let minMi = Infinity;
    let nearestIdx = 0;
    for (let i = 0; i < hospitals.length; i++) {
      const mi = haversineMiles(d.lat, d.lon, hospitals[i].lat, hospitals[i].lon);
      if (mi < minMi) {
        minMi = mi;
        nearestIdx = i;
      }
    }
    return {
      p: d.p,
      lat: d.lat,
      lon: d.lon,
      mins: (minMi * DETOUR / SPEED) * 60,
      nearestIdx,
    };
  });
}

export function summarize(timed) {
  let tot = 0, w30 = 0, b30 = 0, b60 = 0;
  for (const d of timed) {
    tot += d.p;
    if (d.mins <= 30) w30 += d.p; else b30 += d.p;
    if (d.mins > 60) b60 += d.p;
  }
  return {
    tot,
    w30Pct: ((w30 / tot) * 100).toFixed(1),
    b30,
    b60Pct: ((b60 / tot) * 100).toFixed(1),
  };
}

// Sequential color ramp green → red.
const RAMP = [
  { t: 0.0,  c: [46, 196, 130] },
  { t: 0.25, c: [163, 214, 86] },
  { t: 0.5,  c: [241, 196, 83] },
  { t: 0.75, c: [232, 122, 47] },
  { t: 1.0,  c: [220, 47, 47] },
];

const lerp = (a, b, t) => a + (b - a) * t;

export function rampColor(t) {
  const tt = t < 0 ? 0 : t > 1 ? 1 : t;
  for (let i = 0; i < RAMP.length - 1; i++) {
    const a = RAMP[i], b = RAMP[i + 1];
    if (tt >= a.t && tt <= b.t) {
      const k = (tt - a.t) / (b.t - a.t);
      return `rgb(${Math.round(lerp(a.c[0], b.c[0], k))},${Math.round(
        lerp(a.c[1], b.c[1], k)
      )},${Math.round(lerp(a.c[2], b.c[2], k))})`;
    }
  }
  return 'rgb(220,47,47)';
}

export const MAX_POP = Math.max(...BLOCK_GROUPS.map((d) => d.p));
