import React, { useMemo } from "react";
import {
  ComposableMap,
  Geographies,
  Geography,
  Marker,
  ZoomableGroup,
} from "react-simple-maps";
import { scaleLinear } from "d3-scale";

// Same county topojson the Map page uses. We filter geographies by the
// state FIPS prefix on `geo.id` (5-digit county FIPS = 2-digit state FIPS
// + 3-digit county FIPS) so a single dataset serves every state without
// extra fetches.
const COUNTIES_TOPOJSON =
  "https://cdn.jsdelivr.net/npm/us-atlas@3/counties-10m.json";

// Brighter-teal gradient ported verbatim from MapPage so the two pages
// share a visual identity. Domain is keyed to log10(routing-leverage
// index) -- see scoreForDelta below.
const colorScale = scaleLinear()
  .domain([-1.5, 0, 0.5, 1.0, 1.5])
  .range(["#FFFFFF", "#C5DCD9", "#5C9690", "#1F5651", "#062E2A"])
  .clamp(true);

const NO_DELTA_FILL = "#E5E5E5";

// Routing-leverage score. Semantics match the Strata page: smaller T2-T1
// = MORE leverage = darker dot. We map delta -> log10(30 / delta), which
// pegs delta = 0.5 min near the dark end of the gradient and delta = 30
// min near the white end. Clipped via the colorScale's .clamp(true).
function scoreForDelta(delta) {
  if (delta == null || !isFinite(delta)) return null;
  const d = Math.max(0.1, delta);
  return Math.log10(30 / d);
}

// CONUS-wide fallback view (Albers USA centroid + zoom 1) used as the
// default until a state's data is loaded and computeFitView produces a
// real per-state framing. Effectively the same view the Map page uses.
const FALLBACK_VIEW = { coordinates: [-96, 37.5], zoom: 1 };

// Derive a {coordinates, zoom} that frames the given block-group cloud
// inside the 900x520 ComposableMap viewport. Uses a simple lon/lat
// bounding box (no projection-aware math) which works for the CONUS
// states. Alaska and Hawaii are excluded from the upstream pipeline
// (OSRM cannot bridge oceans) so this function never sees them.
//
// Tuning constants: at zoom=1 the geoAlbersUsa projection (scale 1100)
// spans roughly 58 deg longitude across the 900px width and ~25 deg
// latitude across 520px, so ~15.5 px/lon-deg and ~21 px/lat-deg.
// Target framing fills 80% of the viewport to leave breathing room.
const LON_PX_AT_Z1 = 15.5;
const LAT_PX_AT_Z1 = 21.0;
const FRAME_FRACTION = 0.8;

export function computeFitView(bgs) {
  if (!bgs || bgs.length === 0) return FALLBACK_VIEW;
  // Pull bounds from BG centroids. Skip records with nullish coords.
  let minLon = Infinity, maxLon = -Infinity, minLat = Infinity, maxLat = -Infinity;
  for (const b of bgs) {
    if (typeof b.lon !== "number" || typeof b.lat !== "number") continue;
    if (b.lon < minLon) minLon = b.lon;
    if (b.lon > maxLon) maxLon = b.lon;
    if (b.lat < minLat) minLat = b.lat;
    if (b.lat > maxLat) maxLat = b.lat;
  }
  if (!isFinite(minLon)) return FALLBACK_VIEW;

  const centerLon = (minLon + maxLon) / 2;
  const centerLat = (minLat + maxLat) / 2;
  const spanLon = Math.max(0.1, maxLon - minLon);
  const spanLat = Math.max(0.1, maxLat - minLat);
  const zoomLon = (900 * FRAME_FRACTION) / (LON_PX_AT_Z1 * spanLon);
  const zoomLat = (520 * FRAME_FRACTION) / (LAT_PX_AT_Z1 * spanLat);
  // Cap at the ZoomableGroup's maxZoom (128) so the position state and
  // the actually-rendered zoom stay in sync. Without this cap, very
  // small entities like DC produce computed zooms above 128 (~221), the
  // map clamps to 128 silently, and per-dot sizing math that uses the
  // uncapped value gets mismatched.
  const zoom = Math.max(1.5, Math.min(zoomLon, zoomLat, 128));
  return { coordinates: [centerLon, centerLat], zoom };
}

export default function StateBGScatter({
  stateFips,
  bgs,
  hospitals,
  onHoverBG,
  onHoverHospital,
  position,
  onMoveEnd,
}) {
  const data = useMemo(() => bgs, [bgs]);
  const effectivePos = position || FALLBACK_VIEW;

  // Marker sizing. Two encodings:
  //  - BG dot AREA is proportional to adult_pop (so radius = sqrt(pop));
  //    color carries T2-T1 separately. Population-weighted dots are more
  //    honest about who actually lives in each BG -- a 200-adult rural
  //    centroid and a 5,000-adult urban centroid should not read as the
  //    same visual weight.
  //  - Hospital dots are a single small radius, deliberately smaller than
  //    they were on the Map page so they don't dominate the BG layer.
  // Both divide by zoom (not sqrt(zoom)) so each dot keeps a constant
  // SCREEN size regardless of how zoomed-in the state is. Without this,
  // Delaware (default zoom ~14) and California (default zoom ~3.5) would
  // render the same 1,000-adult BG at different visual sizes -- which
  // looks like an encoding inconsistency rather than a zoom artifact.
  // On-screen target pixel sizes; divided by zoom to convert to SVG units
  // so the ZoomableGroup's zoom transform brings them back to the target
  // at render time. NO Math.max floors in SVG units -- a previous
  // Math.max(0.2, rUnz/zoom) floor accidentally produced 20+ px dots in
  // DC (auto-fit zoom ~99) because 0.2 SVG units * 99 zoom = 19.8 screen
  // px. The formulas below already produce reasonable target values at
  // any zoom; no floor is needed.
  //   pop=0:    r ~= 1.5 px on screen
  //   pop=200:  r ~= 2.6 px
  //   pop=1k:   r ~= 4.0 px
  //   pop=5k:   r ~= 7.2 px
  const zoom = effectivePos.zoom ?? 1;
  const bgStroke = 0.35 / zoom;
  const hospR = 3.2 / zoom;
  const hospStroke = 0.5 / zoom;
  const bgRadius = (pop) => {
    const p = Math.max(0, pop || 0);
    const rScreen = 1.5 + 0.08 * Math.sqrt(p);
    return rScreen / zoom;
  };

  // Render order: state outline + neighboring counties (light gray) ->
  // BG dots -> hospital dots. Hospital z-order is highest so their
  // tooltips win over BG tooltips on visual overlap.
  return (
    <ComposableMap
      projection="geoAlbersUsa"
      projectionConfig={{ scale: 1100 }}
      width={900}
      height={520}
      style={{ width: "100%", height: "auto" }}
    >
      <ZoomableGroup
        center={effectivePos.coordinates}
        zoom={zoom}
        onMoveEnd={onMoveEnd}
        minZoom={1}
        maxZoom={128}
      >
        <Geographies geography={COUNTIES_TOPOJSON}>
          {({ geographies }) =>
            geographies.map((geo) => {
              const inState = String(geo.id).startsWith(stateFips);
              return (
                <Geography
                  key={geo.rsmKey}
                  geography={geo}
                  fill={inState ? "#F5F2EC" : "#FAFAFA"}
                  stroke={inState ? "#999" : "#DDD"}
                  strokeWidth={inState ? 0.22 : 0.12}
                  style={{
                    default: { outline: "none" },
                    hover: { outline: "none" },
                    pressed: { outline: "none" },
                  }}
                />
              );
            })
          }
        </Geographies>

        {/* Block-group dots, colored by routing-leverage score. */}
        {data.map((bg) => {
          const score = scoreForDelta(bg.delta_min);
          const fill = score == null ? NO_DELTA_FILL : colorScale(score);
          return (
            <Marker
              key={bg.bg}
              coordinates={[bg.lon, bg.lat]}
              onMouseEnter={(evt) => onHoverBG?.(bg, evt)}
              onMouseMove={(evt) => onHoverBG?.(bg, evt)}
              onMouseLeave={() => onHoverBG?.(null)}
              style={{
                default: { cursor: "pointer" },
                hover: { cursor: "pointer" },
                pressed: { cursor: "pointer" },
              }}
            >
              <circle
                r={bgRadius(bg.adult_pop)}
                fill={fill}
                fillOpacity={0.9}
                stroke="#444"
                strokeWidth={bgStroke}
                style={{ pointerEvents: "all" }}
              />
            </Marker>
          );
        })}

        {/* PCI-capable hospital overlay. Drawn last so SVG z-order puts
            hover events here first. Same red as the Map page. */}
        {hospitals &&
          hospitals.map((h) => (
            <Marker
              key={h.ccn}
              coordinates={[h.lon, h.lat]}
              onMouseEnter={(evt) => onHoverHospital?.(h, evt)}
              onMouseMove={(evt) => onHoverHospital?.(h, evt)}
              onMouseLeave={() => onHoverHospital?.(null)}
              style={{
                default: { cursor: "pointer" },
                hover: { cursor: "pointer" },
                pressed: { cursor: "pointer" },
              }}
            >
              <circle
                r={hospR}
                fill="#C8102E"
                fillOpacity={0.85}
                stroke="white"
                strokeWidth={hospStroke}
                style={{ pointerEvents: "all" }}
              />
            </Marker>
          ))}
      </ZoomableGroup>
    </ComposableMap>
  );
}

