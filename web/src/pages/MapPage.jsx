import React, { useState } from "react";
import CountyChoropleth from "../components/CountyChoropleth.jsx";
import counties from "../data/county_strata.json";
import hospitals from "../data/hospitals_tier_a.json";

// STEMI incidence rate, identical to step 06 / 07 / 07b conventions.
const INCIDENCE_RATE = 0.001;
// Headline threshold: adults living within 15 min of a second PCI hospital.
const HEADLINE_BIN = 15;

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
        U.S. counties shaded by adults living within 15 minutes of a second PCI hospital
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
          <button type="button" onClick={handleZoomIn} aria-label="Zoom in" title="Zoom in">
            <ZoomIcon variant="plus" />
          </button>
          <button type="button" onClick={handleZoomOut} aria-label="Zoom out" title="Zoom out">
            <ZoomIcon variant="minus" />
          </button>
          <button type="button" onClick={handleResetView} aria-label="Reset view" title="Reset view">
            <ZoomIcon variant="reset" />
          </button>
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

// Inline SVGs for the three zoom-control buttons. Drawing them in SVG
// rather than using Unicode glyphs (＋, −, ⟳) keeps every icon the same
// optical weight and bounding box so the three buttons read as a matched
// set. All three share: a 16x16 viewBox, currentColor strokes, 2px
// round-capped stroke weight, geometry centered on (8, 8).
function ZoomIcon({ variant }) {
  const common = {
    width: 16,
    height: 16,
    viewBox: "0 0 16 16",
    fill: "none",
    stroke: "currentColor",
    strokeWidth: 2,
    strokeLinecap: "round",
    strokeLinejoin: "round",
    "aria-hidden": true,
  };
  if (variant === "plus") {
    return (
      <svg {...common}>
        <line x1="8" y1="3.5" x2="8" y2="12.5" />
        <line x1="3.5" y1="8" x2="12.5" y2="8" />
      </svg>
    );
  }
  if (variant === "minus") {
    return (
      <svg {...common}>
        <line x1="3.5" y1="8" x2="12.5" y2="8" />
      </svg>
    );
  }
  // reset: a circular refresh arrow centered at (8, 8). Three-quarter arc
  // with a small arrowhead at the open end. Arc radius 4.5 matches the
  // half-extent of the plus/minus strokes so visual weight is consistent.
  return (
    <svg {...common}>
      <path d="M12.5 8 A 4.5 4.5 0 1 1 8 3.5" />
      <polyline points="8.2,1.6 8,3.5 9.9,3.7" />
    </svg>
  );
}

// Original brighter teal gradient, now applied to log decade breakpoints
// of adults at the <15 min threshold. Visual identity stays the same as
// the published abstract figure; the input changes from share to absolute
// count. Tick labels read in the natural "1, 100, 10K, 1M, 10M+" decades
// rather than 0-100% percentages.
function Colorbar() {
  const ticks = [
    { label: "1" },
    { label: "100" },
    { label: "10K" },
    { label: "1M" },
    { label: "10M+" },
  ];
  const barH = 220;
  return (
    <div className="colorbar" aria-hidden="true">
      <div className="colorbar-header">
        adults<br />in county
      </div>
      <div
        className="colorbar-track"
        style={{
          background:
            "linear-gradient(to top, #FFFFFF 0%, #C5DCD9 25%, #5C9690 50%, #1F5651 75%, #062E2A 100%)",
        }}
      />
      <div className="colorbar-ticks" style={{ position: "absolute", left: 30, top: 26, height: barH }}>
        {ticks.map((t, i) => (
          <span
            key={t.label}
            className="colorbar-tick"
            style={{ top: `${barH - (i / (ticks.length - 1)) * barH}px` }}
          >
            {t.label}
          </span>
        ))}
      </div>
    </div>
  );
}

function CountyTooltip({ data, x, y }) {
  const { name, state, adult_pop, cdf } = data;
  const under = cdf ? (cdf[HEADLINE_BIN - 1] || 0) : 0;
  const stemi = Math.round(under * INCIDENCE_RATE);
  return (
    <div className="tooltip" style={{ left: x, top: y }}>
      <div className="ttitle">{name} County, {state}</div>
      <div className="trow"><span className="lbl">Adults 20+</span><span className="val">{adult_pop.toLocaleString()}</span></div>
      <div className="trow"><span className="lbl">At &lt;{HEADLINE_BIN} min</span><span className="val">{under.toLocaleString()}</span></div>
      <div className="trow"><span className="lbl">STEMI/yr (here)</span><span className="val">~{stemi.toLocaleString()}</span></div>
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
