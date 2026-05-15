import React, { useMemo } from "react";
import { ComposableMap, Geographies, Geography, ZoomableGroup } from "react-simple-maps";

// us-atlas 1:10M-scale CONUS counties, FIPS-keyed. Same source as the Map
// page so the two views are geometrically identical. Served locally from
// public/data/ rather than a CDN.
const COUNTIES_TOPOJSON =
  `${import.meta.env.BASE_URL}data/counties-10m.json`;

// Bivariate choropleth: dominant T2-T1 stratum drives hue, total
// competitive-zone resident count drives alpha (log-scaled). Counties whose
// nearest two PCI hospitals are both >=30 min apart (or with no second PCI
// reachable) render in neutral gray; routing optimization is a
// non-question in those geographies.
export default function CountyStrataChoropleth({
  counties,
  fillFor,
  onHoverCounty,
  position,
  onMoveEnd,
}) {
  const data = useMemo(() => counties, [counties]);
  const zoom = position?.zoom ?? 1;

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
              const fill = fillFor(entry);

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
      </ZoomableGroup>
    </ComposableMap>
  );
}
