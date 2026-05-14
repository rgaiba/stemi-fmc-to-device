import React, { useState } from "react";
import CountyChoropleth from "../components/CountyChoropleth.jsx";
import counties from "../data/county_values.json";
import hospitals from "../data/hospitals_tier_a.json";

// Default map view: full CONUS, zoom 1, centered on the conventional
// continental US centroid that Albers USA projection uses.
const DEFAULT_POSITION = { coordinates: [-96, 37.5], zoom: 1 };

export default function MapPage() {
  // Single hover state with a 'type' discriminator; only one tooltip at a time.
  const [hovered, setHovered] = useState(null);
  // Hospital marker visibility — off by default per user spec. When enabled,
  // 1,588 small red dots overlay the choropleth; hover any dot for details.
  const [showHospitals, setShowHospitals] = useState(false);
  // Map pan/zoom state. Controlled by ZoomableGroup; updated on
  // onMoveEnd (drag-pan / wheel-zoom / pinch) and by the explicit
  // +/-/reset buttons below.
  const [position, setPosition] = useState(DEFAULT_POSITION);

  const handleZoomIn = () =>
    setPosition((p) => ({ ...p, zoom: Math.min(p.zoom * 1.5, 8) }));
  const handleZoomOut = () =>
    setPosition((p) => ({ ...p, zoom: Math.max(p.zoom / 1.5, 1) }));
  const handleResetView = () => setPosition(DEFAULT_POSITION);

  const handleHoverCounty = (entry, evt) => {
    if (entry && evt) {
      setHovered({ type: "county", data: entry, x: evt.clientX, y: evt.clientY });
    } else {
      setHovered(null);
    }
  };

  const handleHoverHospital = (entry, evt) => {
    if (entry && evt) {
      setHovered({ type: "hospital", data: entry, x: evt.clientX, y: evt.clientY });
    } else {
      setHovered(null);
    }
  };

  return (
    <>
      <h1 className="title">
        <span className="title-hook">Where EMS routing matters in STEMI:</span>
        U.S. counties by share of adults with two PCI hospitals within 15 minutes of each other
      </h1>

      <div className="map-wrap">
        <CountyChoropleth
          counties={counties}
          hospitals={showHospitals ? hospitals : null}
          onHoverCounty={handleHoverCounty}
          onHoverHospital={handleHoverHospital}
          position={position}
          onMoveEnd={setPosition}
        />
        <Colorbar />
        <div className="zoom-controls" role="group" aria-label="Map zoom">
          <button type="button" onClick={handleZoomIn} aria-label="Zoom in" title="Zoom in">＋</button>
          <button type="button" onClick={handleZoomOut} aria-label="Zoom out" title="Zoom out">−</button>
          <button type="button" onClick={handleResetView} aria-label="Reset view" title="Reset view">⟳</button>
        </div>
      </div>

      <div className="map-controls">
        <button
          type="button"
          className={`toggle-pill ${showHospitals ? "active" : ""}`}
          onClick={() => setShowHospitals((v) => !v)}
          aria-pressed={showHospitals}
        >
          <span className="toggle-dot" aria-hidden="true" />
          PCI-capable
        </button>
      </div>

      <p className="subtitle">
        Areas where routing to the hospital with shorter door-to-balloon time may
        shorten time to reperfusion after STEMI.
      </p>

      <p className="metrics">
        ~196,000 STEMI patients/yr in these areas&nbsp;&nbsp;·&nbsp;&nbsp;
        1,598 PCI-capable hospitals&nbsp;&nbsp;·&nbsp;&nbsp;
        drive times
      </p>

      <p className="sources">
        Sources: CMS Provider of Services (Dec 2024)&nbsp;·&nbsp;Census CenPop 2020&nbsp;·&nbsp;
        ACS 2019–2023 5-year (B01001)<br />
        OpenStreetMap (Geofabrik US, May 2026)&nbsp;·&nbsp;OSRM road-network routing&nbsp;·&nbsp;
        <a href="https://github.com/rgaiba/stemi-fmc-to-device" target="_blank" rel="noreferrer">
          github.com/rgaiba/stemi-fmc-to-device
        </a>
      </p>

      {hovered && hovered.type === "county" && (
        <CountyTooltip data={hovered.data} x={hovered.x} y={hovered.y} />
      )}
      {hovered && hovered.type === "hospital" && (
        <HospitalTooltip data={hovered.data} x={hovered.x} y={hovered.y} />
      )}
    </>
  );
}

function Colorbar() {
  return (
    <div className="colorbar" aria-hidden="true">
      <div className="colorbar-header">
        % of county's<br />adults
      </div>
      <div
        className="colorbar-track"
        style={{
          background:
            "linear-gradient(to top, #FFFFFF 0%, #C5DCD9 25%, #5C9690 50%, #1F5651 75%, #062E2A 100%)",
        }}
      />
      <div className="colorbar-ticks" style={{ position: "absolute", left: 30, top: 26, height: 220 }}>
        {[0, 25, 50, 75, 100].map((v) => (
          <span
            key={v}
            className="colorbar-tick"
            style={{ bottom: `${(v / 100) * 220 - 6}px` }}
          >
            {v}
          </span>
        ))}
      </div>
    </div>
  );
}

function CountyTooltip({ data, x, y }) {
  const { name, state, adult_pop, pct, stemi_per_yr, fips } = data;
  return (
    <div className="tooltip" style={{ left: x, top: y }}>
      <div className="ttitle">
        {name} County, {state}
      </div>
      <div className="trow"><span className="lbl">FIPS</span><span className="val">{fips}</span></div>
      <div className="trow"><span className="lbl">Adults 20+</span><span className="val">{adult_pop.toLocaleString()}</span></div>
      <div className="trow"><span className="lbl">% in CZ</span><span className="val">{pct.toFixed(1)}%</span></div>
      <div className="trow"><span className="lbl">STEMI/yr</span><span className="val">{stemi_per_yr.toLocaleString()}</span></div>
    </div>
  );
}

function HospitalTooltip({ data, x, y }) {
  const { name, city, st, beds, ccn } = data;
  return (
    <div className="tooltip" style={{ left: x, top: y }}>
      <div className="ttitle">{titleCase(name)}</div>
      <div className="trow"><span className="lbl">City</span><span className="val">{titleCase(city)}, {st}</span></div>
      <div className="trow"><span className="lbl">CCN</span><span className="val">{ccn}</span></div>
      {beds != null && (
        <div className="trow"><span className="lbl">Beds</span><span className="val">{beds.toLocaleString()}</span></div>
      )}
      <div className="trow"><span className="lbl">Tier</span><span className="val">PCI-capable</span></div>
    </div>
  );
}

// CMS PoS names come in ALL CAPS; soften for readability without losing
// the data fidelity. Acronyms like USA / UC / VA stay all-caps via the
// length-2 short-token allowlist; everything else gets Title Case.
function titleCase(s) {
  if (!s) return "";
  return s.split(/\s+/).map((w) => {
    if (w.length <= 2) return w; // keep acronyms / connectors
    return w[0] + w.slice(1).toLowerCase();
  }).join(" ");
}
