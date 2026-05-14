import React, { useState } from "react";
import CountyChoropleth from "../components/CountyChoropleth.jsx";
import counties from "../data/county_values.json";

export default function MapPage() {
  const [hovered, setHovered] = useState(null);
  const [pointer, setPointer] = useState({ x: 0, y: 0 });

  const handleHover = (entry, evt) => {
    if (entry && evt) {
      setPointer({ x: evt.clientX, y: evt.clientY });
    }
    setHovered(entry);
  };

  return (
    <>
      <h1 className="title">
        <span className="title-hook">Where EMS routing matters in STEMI:</span>
        U.S. counties by share of adults with two PCI hospitals within 15 minutes of each other
      </h1>

      <div className="map-wrap">
        <CountyChoropleth counties={counties} onHover={handleHover} />
        <Colorbar />
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

      {hovered && (
        <Tooltip data={hovered} x={pointer.x} y={pointer.y} />
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

function Tooltip({ data, x, y }) {
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
