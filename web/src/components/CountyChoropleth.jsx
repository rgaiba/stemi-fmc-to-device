import React, { useMemo } from "react";
import { ComposableMap, Geographies, Geography, Marker, ZoomableGroup } from "react-simple-maps";
import { scaleLinear } from "d3-scale";

// us-atlas 1:10M-scale CONUS counties, ~70KB, FIPS-keyed (matches our data).
// Served from jsDelivr CDN; preconnect link in index.html primes the DNS.
const COUNTIES_TOPOJSON =
  "https://cdn.jsdelivr.net/npm/us-atlas@3/counties-10m.json";

// Color ramp: original brighter teal palette, but now keyed to log10 of
// the absolute number of adults living within 15 min of a second PCI
// hospital instead of percent. Keeping the five-stop gradient preserves
// the visual identity of the headline map; switching the input from pct
// to log(count) addresses the denominator-neglect concern -- a county
// with a million CZ residents looks much darker than one with a thousand,
// regardless of the within-county share. Counties with zero CZ residents
// at the threshold (the 411 ge30 counties) render light gray; routing has
// no leverage there.
const colorScale = scaleLinear()
  .domain([0, 2, 4, 6, 7])      // log10(1), log10(100), log10(10K), log10(1M), log10(10M+)
  .range(["#FFFFFF", "#C5DCD9", "#5C9690", "#1F5651", "#062E2A"])
  .clamp(true);

const NO_COUNT_FILL = "#E5E5E5";
const THRESHOLD_BIN = 15;       // adults with margin < 15 min => cdf[14]

function fillForEntry(entry) {
  if (!entry || !entry.cdf) return NO_COUNT_FILL;
  const n = entry.cdf[THRESHOLD_BIN - 1] | 0;
  if (n <= 0) return NO_COUNT_FILL;
  return colorScale(Math.log10(n));
}

export default function CountyChoropleth({
  counties,
  hospitals,
  onHoverCounty,
  onHoverHospital,
  position,
  onMoveEnd,
}) {
  // Memoize so re-renders on hover don't re-evaluate the lookup table.
  const data = useMemo(() => counties, [counties]);

  // Adjust marker radius and stroke width inversely with zoom so dots stay
  // legible without becoming oversized blobs at high zoom levels.
  const zoom = position?.zoom ?? 1;
  const markerR = Math.max(0.8, 2.2 / Math.sqrt(zoom));
  const markerStroke = Math.max(0.15, 0.4 / Math.sqrt(zoom));

  return (
    <ComposableMap
      projection="geoAlbersUsa"
      projectionConfig={{ scale: 1100 }}
      width={900}
      height={520}
      style={{ width: "100%", height: "auto" }}
    >
      <ZoomableGroup
        center={position?.coordinates ?? [-96, 37.5]}
        zoom={zoom}
        onMoveEnd={onMoveEnd}
        minZoom={1}
        maxZoom={8}
      >
        <Geographies geography={COUNTIES_TOPOJSON}>
        {({ geographies }) =>
          geographies.map((geo) => {
            const fips = geo.id;
            const entry = data[fips];
            const fill = fillForEntry(entry);

            return (
              <Geography
                key={geo.rsmKey}
                geography={geo}
                fill={fill}
                stroke="#888"
                strokeWidth={0.18}
                onMouseEnter={(evt) => {
                  if (entry) onHoverCounty?.({ ...entry, fips }, evt);
                }}
                onMouseMove={(evt) => {
                  if (entry) onHoverCounty?.({ ...entry, fips }, evt);
                }}
                onMouseLeave={() => onHoverCounty?.(null)}
                style={{
                  default: { outline: "none", transition: "fill 120ms" },
                  hover:   { outline: "none", stroke: "#1A1E2E", strokeWidth: 0.7 },
                  pressed: { outline: "none" },
                }}
              />
            );
          })
        }
      </Geographies>

      {/* PCI-capable hospital markers. Plotted above counties in SVG z-order
          so hover events on markers take precedence. AHA-brand red, small,
          thin white halo, alpha 0.7 — same visual idiom as the matplotlib
          PDF figure. */}
      {hospitals && hospitals.map((h) => (
        <Marker
          key={h.ccn}
          coordinates={[h.lon, h.lat]}
          onMouseEnter={(evt) => onHoverHospital?.(h, evt)}
          onMouseMove={(evt) => onHoverHospital?.(h, evt)}
          onMouseLeave={() => onHoverHospital?.(null)}
          style={{
            default: { cursor: "pointer" },
            hover:   { cursor: "pointer" },
            pressed: { cursor: "pointer" },
          }}
        >
          <circle
            r={markerR}
            fill="#C8102E"
            fillOpacity={0.7}
            stroke="white"
            strokeWidth={markerStroke}
            style={{ pointerEvents: "all" }}
          />
        </Marker>
      ))}
      </ZoomableGroup>
    </ComposableMap>
  );
}
