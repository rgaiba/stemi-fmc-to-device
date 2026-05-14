import React, { useMemo } from "react";
import { ComposableMap, Geographies, Geography } from "react-simple-maps";
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

export default function CountyChoropleth({ counties, onHover }) {
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
            // us-atlas county IDs are 5-digit FIPS strings.
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
                  if (entry) onHover?.({ ...entry, fips }, evt);
                }}
                onMouseMove={(evt) => {
                  if (entry) onHover?.({ ...entry, fips }, evt);
                }}
                onMouseLeave={() => onHover?.(null)}
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
    </ComposableMap>
  );
}
