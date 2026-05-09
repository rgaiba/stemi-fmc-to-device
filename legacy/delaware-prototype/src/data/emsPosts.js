// Delaware ALS paramedic posts (current state).
// Source: county EMS websites (NCC EMS, Kent County EMS, Sussex County EMS),
// compiled May 2026. Coordinates are approximate (~0.5 mi accuracy) — good
// enough for block-group-level response-time modeling; refine with a proper
// geocoder before publishing results.
//
// Each entry is the location where a paramedic unit "lives" between calls.
// In SSM (System Status Management) terminology these are post locations.
// Some are full-time (year-round, 24/7); others are peak-shift only.

export const CURRENT_POSTS = [
  // New Castle County (NCC EMS) ─────────────────────────────────────────────
  { id: 'ncc-hq',       name: 'NCC EMS HQ',                 city: 'New Castle',     county: 'NCC', lat: 39.689, lon: -75.598, shift: 'full' },
  { id: 'ncc-wfd2',     name: 'Wilmington FD Station 2',    city: 'Wilmington',     county: 'NCC', lat: 39.728, lon: -75.555, shift: 'full' },
  { id: 'ncc-2',        name: 'NCC EMS Station 2',          city: 'New Castle',     county: 'NCC', lat: 39.660, lon: -75.601, shift: 'full' },
  { id: 'ncc-kirklib',  name: 'Kirkwood Highway Library',   city: 'Wilmington',     county: 'NCC', lat: 39.735, lon: -75.660, shift: 'full' },
  { id: 'ncc-brandy',   name: 'Brandywine Hundred FC',      city: 'Wilmington',     county: 'NCC', lat: 39.770, lon: -75.500, shift: 'full' },
  { id: 'ncc-5',        name: 'NCC EMS Station 5 (Potter)', city: 'Middletown',     county: 'NCC', lat: 39.451, lon: -75.715, shift: 'full' },
  { id: 'ncc-6',        name: 'NCC EMS Station 6',          city: 'Newark',         county: 'NCC', lat: 39.612, lon: -75.731, shift: 'full' },
  { id: 'ncc-cranston', name: 'Cranston Heights FC',        city: 'Wilmington',     county: 'NCC', lat: 39.730, lon: -75.620, shift: 'full' },
  { id: 'ncc-mt',       name: 'M&T Bank Plaza',             city: 'Wilmington',     county: 'NCC', lat: 39.748, lon: -75.547, shift: 'peak' },
  { id: 'ncc-aetna',    name: 'Aetna Station 8',            city: 'Newark',         county: 'NCC', lat: 39.692, lon: -75.737, shift: 'full' },
  { id: 'ncc-odessa',   name: 'Odessa FC Station 4',        city: 'Middletown',     county: 'NCC', lat: 39.470, lon: -75.665, shift: 'full' },

  // Kent County EMS ─────────────────────────────────────────────────────────
  { id: 'kent-hq',      name: 'Kent EMS HQ',                city: 'Dover',          county: 'KENT', lat: 39.183, lon: -75.501, shift: 'full' },
  { id: 'kent-6',       name: 'Kent EMS 6',                 city: 'Smyrna',         county: 'KENT', lat: 39.243, lon: -75.601, shift: 'full' },
  { id: 'kent-8',       name: 'Kent EMS 8',                 city: 'Harrington',     county: 'KENT', lat: 38.924, lon: -75.578, shift: 'full' },
  { id: 'kent-9',       name: 'Kent EMS 9',                 city: 'Dover',          county: 'KENT', lat: 39.150, lon: -75.570, shift: 'full' },
  { id: 'kent-10',      name: 'Kent EMS 10',                city: 'Frederica',      county: 'KENT', lat: 38.992, lon: -75.467, shift: 'full' },

  // Sussex County EMS ───────────────────────────────────────────────────────
  { id: 'sus-hq',       name: 'Sussex EMS HQ',              city: 'Georgetown',     county: 'SUS',  lat: 38.690, lon: -75.385, shift: 'full' },
  { id: 'sus-101',      name: 'Sussex 101',                 city: 'Lincoln',        county: 'SUS',  lat: 38.881, lon: -75.418, shift: 'full' },
  { id: 'sus-102',      name: 'Sussex 102',                 city: 'Laurel',         county: 'SUS',  lat: 38.555, lon: -75.572, shift: 'full' },
  { id: 'sus-103',      name: 'Sussex 103',                 city: 'Dagsboro',       county: 'SUS',  lat: 38.547, lon: -75.243, shift: 'full' },
  { id: 'sus-104',      name: 'Sussex 104',                 city: 'Rehoboth Beach', county: 'SUS',  lat: 38.720, lon: -75.140, shift: 'full' },
  { id: 'sus-105',      name: 'Sussex 105',                 city: 'Frankford',      county: 'SUS',  lat: 38.521, lon: -75.226, shift: 'full' },
  { id: 'sus-106',      name: 'Sussex 106',                 city: 'Millsboro',      county: 'SUS',  lat: 38.591, lon: -75.293, shift: 'full' },
  { id: 'sus-107',      name: 'Sussex 107',                 city: 'Bridgeville',    county: 'SUS',  lat: 38.745, lon: -75.602, shift: 'full' },
  { id: 'sus-108',      name: 'Sussex 108',                 city: 'Georgetown',     county: 'SUS',  lat: 38.690, lon: -75.385, shift: 'full' },
  { id: 'sus-109',      name: 'Sussex 109',                 city: 'Selbyville',     county: 'SUS',  lat: 38.461, lon: -75.220, shift: 'full' },
  { id: 'sus-110',      name: 'Sussex 110',                 city: 'Seaford',        county: 'SUS',  lat: 38.642, lon: -75.611, shift: 'full' },
  { id: 'sus-111',      name: 'Sussex 111',                 city: 'Milton',         county: 'SUS',  lat: 38.776, lon: -75.314, shift: 'full' },
  { id: 'sus-114',      name: 'Sussex 114',                 city: 'Dewey Beach',    county: 'SUS',  lat: 38.692, lon: -75.075, shift: 'seasonal' },
];

export const FULL_TIME_POSTS = CURRENT_POSTS.filter((p) => p.shift === 'full');
