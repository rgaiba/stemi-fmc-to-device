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

// Per-state view configuration. Each entry: lon/lat center for the
// ComposableMap projection, plus a default zoom so the state fills the
// canvas. Adding a new state means adding a row here + dropping its
// state_bg_<fips>.json file into web/src/data/.
const STATE_VIEW = {
  "10": { center: [-75.5, 39.0], zoom: 24 },   // Delaware
};

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
  const view = STATE_VIEW[stateFips] || { center: [-96, 37.5], zoom: 4 };
  const effectivePos = position || { coordinates: view.center, zoom: view.zoom };

  // Marker sizing. Two encodings:
  //  - BG dot AREA is proportional to adult_pop (so radius = sqrt(pop));
  //    color carries T2-T1 separately. Population-weighted dots are more
  //    honest about who actually lives in each BG -- a 200-adult rural
  //    centroid and a 5,000-adult urban centroid should not read as the
  //    same visual weight.
  //  - Hospital dots are a single small radius, deliberately smaller than
  //    they were on the Map page so they don't dominate the BG layer.
  // Both are scaled inversely with sqrt(zoom) so they stay legible at any
  // zoom level. r_unzoomed = 0.5 + 0.04 * sqrt(pop) gives:
  //   pop=0:    r_unz ~= 0.5  (smallest BG still has a visible dot)
  //   pop=200:  r_unz ~= 1.07
  //   pop=1k:   r_unz ~= 1.77 (Delaware median ~1000 adults; matches v1's
  //                            fixed-size dot footprint)
  //   pop=5k:   r_unz ~= 3.33
  //   pop=6k:   r_unz ~= 3.60 (largest Delaware BGs ~2x v1 footprint)
  // Coefficients tuned so the median BG matches the prior fixed-size
  // version's visual weight; size variation reads but doesn't overwhelm.
  const zoom = effectivePos.zoom ?? view.zoom;
  const zoomFactor = Math.sqrt(zoom);
  const bgStroke = Math.max(0.03, 0.15 / zoomFactor);
  const hospR = Math.max(0.3, 1.3 / zoomFactor);
  const hospStroke = Math.max(0.05, 0.25 / zoomFactor);
  const bgRadius = (pop) => {
    const p = Math.max(0, pop || 0);
    const rUnz = 0.5 + 0.04 * Math.sqrt(p);
    return Math.max(0.1, rUnz / zoomFactor);
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
        maxZoom={64}
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

// Re-exported so the page can pass an initial position keyed off the
// state's default view without duplicating the lookup table.
export function defaultPositionForState(fips) {
  const v = STATE_VIEW[fips] || { center: [-96, 37.5], zoom: 4 };
  return { coordinates: v.center, zoom: v.zoom };
}
