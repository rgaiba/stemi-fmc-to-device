import React, { useMemo } from "react";
import { ComposableMap, Geographies, Geography, Marker } from "react-simple-maps";
import { scaleLinear } from "d3-scale";

// us-atlas 1:10M-scale CONUS counties, ~70KB, FIPS-keyed (matches our data).
// Served from jsDelivr CDN; preconnect link in index.html primes the DNS.
const COUNTIES_TOPOJSON =
  "https://cdn.jsdelivr.net/npm/us-atlas@3/counties-10m.json";

// Color ramp mirrors the matplotlib `deep_teal` palette so the web map and
// the PDF figure are visually consistent.
const colorScale = scaleLinear()
  .domain([0, 25, 50, 75, 100])
  .range(["#FFFFFF", "#C5DCD9", "#5C9690", "#1F5651", "#062E2A"])
  .clamp(true);

export default function CountyChoropleth({
  counties,
  hospitals,
  onHoverCounty,
  onHoverHospital,
}) {
  // Memoize so re-renders on hover don't re-evaluate the lookup table.
  const data = useMemo(() => counties, [counties]);

  return (
    <ComposableMap
      projection="geoAlbersUsa"
      projectionConfig={{ scale: 1100 }}
      width={900}
      height={520}
      style={{ width: "100%", height: "auto" }}
    >
      <Geographies geography={COUNTIES_TOPOJSON}>
        {({ geographies }) =>
          geographies.map((geo) => {
            const fips = geo.id;
            const entry = data[fips];
            const pct = entry ? entry.pct : null;
            const fill = pct == null ? "#EEEEEE" : colorScale(pct);

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
                  hover: {
                    outline: "none",
                    fill: pct == null ? "#DDDDDD" : colorScale(Math.min(pct + 8, 100)),
                    stroke: "#1A1E2E",
                    strokeWidth: 0.7,
                  },
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
            r={2.2}
            fill="#C8102E"
            fillOpacity={0.7}
            stroke="white"
            strokeWidth={0.4}
            style={{ pointerEvents: "all" }}
          />
        </Marker>
      ))}
    </ComposableMap>
  );
}
