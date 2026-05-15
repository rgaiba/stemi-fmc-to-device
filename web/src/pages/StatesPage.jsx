import React, { useEffect, useMemo, useState } from "react";
import StateBGScatter, { computeFitView } from "../components/StateBGScatter.jsx";
import hospitals from "../data/hospitals_tier_a.json";

// Same STEMI incidence rate as Map / Strata pages -- gives us a per-BG
// "STEMI/yr at this BG" row in the tooltip while keeping the headline
// methodology identical.
const INCIDENCE_RATE = 0.001;

// In-memory cache so re-selecting a state doesn't re-fetch its JSON.
// First selection of any state pays a one-time network hit (small for
// most states, ~3.7 MB for California). The Vite build serves files from
// /data/state_bg_<fips>.json (public/ folder) so they're static assets,
// not part of the JS bundle.
const BG_CACHE = new Map();

async function loadStateBGs(fips) {
  if (BG_CACHE.has(fips)) return BG_CACHE.get(fips);
  const url = `${import.meta.env.BASE_URL}data/state_bg_${fips}.json`;
  const res = await fetch(url);
  if (!res.ok) throw new Error(`HTTP ${res.status} fetching ${url}`);
  const data = await res.json();
  BG_CACHE.set(fips, data);
  return data;
}

// Master state list: FIPS, USPS, name. Dropdown shows all 50 + DC but
// disables ones we haven't built a data file for yet. Order is
// alphabetical by name (USPS order is harder for non-power-users to scan).
const ALL_STATES = [
  ["01", "AL", "Alabama"], ["02", "AK", "Alaska"], ["04", "AZ", "Arizona"],
  ["05", "AR", "Arkansas"], ["06", "CA", "California"], ["08", "CO", "Colorado"],
  ["09", "CT", "Connecticut"], ["10", "DE", "Delaware"], ["11", "DC", "District of Columbia"],
  ["12", "FL", "Florida"], ["13", "GA", "Georgia"], ["15", "HI", "Hawaii"],
  ["16", "ID", "Idaho"], ["17", "IL", "Illinois"], ["18", "IN", "Indiana"],
  ["19", "IA", "Iowa"], ["20", "KS", "Kansas"], ["21", "KY", "Kentucky"],
  ["22", "LA", "Louisiana"], ["23", "ME", "Maine"], ["24", "MD", "Maryland"],
  ["25", "MA", "Massachusetts"], ["26", "MI", "Michigan"], ["27", "MN", "Minnesota"],
  ["28", "MS", "Mississippi"], ["29", "MO", "Missouri"], ["30", "MT", "Montana"],
  ["31", "NE", "Nebraska"], ["32", "NV", "Nevada"], ["33", "NH", "New Hampshire"],
  ["34", "NJ", "New Jersey"], ["35", "NM", "New Mexico"], ["36", "NY", "New York"],
  ["37", "NC", "North Carolina"], ["38", "ND", "North Dakota"], ["39", "OH", "Ohio"],
  ["40", "OK", "Oklahoma"], ["41", "OR", "Oregon"], ["42", "PA", "Pennsylvania"],
  ["44", "RI", "Rhode Island"], ["45", "SC", "South Carolina"], ["46", "SD", "South Dakota"],
  ["47", "TN", "Tennessee"], ["48", "TX", "Texas"], ["49", "UT", "Utah"],
  ["50", "VT", "Vermont"], ["51", "VA", "Virginia"], ["53", "WA", "Washington"],
  ["54", "WV", "West Virginia"], ["55", "WI", "Wisconsin"], ["56", "WY", "Wyoming"],
].sort((a, b) => a[2].localeCompare(b[2]));

// Per-state status. Entries not in this map are assumed AVAILABLE.
// Reasons surface in the dropdown so the gap is visible (not silently
// missing). AK and HI are excluded from the upstream pipeline entirely
// (OSRM road-network routing does not bridge oceans; the published
// CONUS abstract is the scope here). Connecticut works via a special
// proportional allocation in 10_state_bg_strata.py that bridges the
// 2020-county vs 2023-planning-region bg_id mismatch in ACS.
const STATE_STATUS = {
  "02": "non-CONUS",
  "15": "non-CONUS",
};
const DATA_AVAILABLE = new Set(
  ALL_STATES.map((s) => s[0]).filter((fips) => !STATE_STATUS[fips])
);

export default function StatesPage() {
  const [stateFips, setStateFips] = useState("10");
  const [bgs, setBgs] = useState([]);
  const [loadStatus, setLoadStatus] = useState("loading");   // "loading" | "ready" | "error"
  const [hovered, setHovered] = useState(null);
  const [showHospitals, setShowHospitals] = useState(true);
  const [position, setPosition] = useState(null);   // computed from BG bounds once loaded

  // Fetch the selected state's payload whenever the dropdown changes.
  // Effect-driven loading keeps the page reactive to navigation and
  // avoids blocking the first render on Delaware's network roundtrip.
  useEffect(() => {
    let cancelled = false;
    setLoadStatus("loading");
    loadStateBGs(stateFips)
      .then((data) => {
        if (cancelled) return;
        setBgs(data);
        setPosition(computeFitView(data));
        setLoadStatus("ready");
        setHovered(null);
      })
      .catch((err) => {
        if (cancelled) return;
        console.error(err);
        setLoadStatus("error");
      });
    return () => {
      cancelled = true;
    };
  }, [stateFips]);

  // CCN -> hospital lookup built once at mount. Used by the BG tooltip
  // to resolve ccn1/ccn2 into human-readable hospital names without
  // bloating the per-state JSON.
  const hospitalsByCcn = useMemo(() => {
    const m = new Map();
    for (const h of hospitals) m.set(h.ccn, h);
    return m;
  }, []);

  // Restrict the hospital overlay to hospitals that any BG in the
  // current state actually uses as its nearest or second-nearest. This
  // keeps the visual focus on relevant hospitals rather than every PCI
  // center in the country -- but neighboring-state hospitals stay
  // visible if a BG routes to them (DE BGs hitting MD/NJ centers,
  // West Virginia BGs hitting PA/OH centers, etc.).
  const relevantHospitals = useMemo(() => {
    if (!showHospitals) return null;
    const ccns = new Set();
    for (const b of bgs) {
      if (b.ccn1) ccns.add(b.ccn1);
      if (b.ccn2) ccns.add(b.ccn2);
    }
    return hospitals.filter((h) => ccns.has(h.ccn));
  }, [bgs, showHospitals]);

  const handleHoverBG = (bg, evt) => {
    if (bg && evt) setHovered({ type: "bg", data: bg, x: evt.clientX, y: evt.clientY });
    else setHovered(null);
  };
  const handleHoverHospital = (h, evt) => {
    if (h && evt) setHovered({ type: "hospital", data: h, x: evt.clientX, y: evt.clientY });
    else setHovered(null);
  };

  const handleStateChange = (e) => {
    // The effect on stateFips handles the fetch + view recompute.
    setStateFips(e.target.value);
  };

  const handleZoomIn = () =>
    setPosition((p) => (p ? { ...p, zoom: Math.min(p.zoom * 1.5, 128) } : p));
  const handleZoomOut = () =>
    setPosition((p) => (p ? { ...p, zoom: Math.max(p.zoom / 1.5, 1) } : p));
  const handleResetView = () => setPosition(computeFitView(bgs));

  // Totals readout: adults in the state, plus how many live in BGs
  // where T2-T1 < 5 min (high routing leverage). Numbers are absolute
  // counts per the project's denominator-honesty convention.
  const totals = useMemo(() => {
    let totalAdults = 0;
    let leverageAdults = 0;
    let bgsLeverage = 0;
    for (const b of bgs) {
      totalAdults += b.adult_pop || 0;
      if (b.delta_min != null && b.delta_min < 5) {
        leverageAdults += b.adult_pop || 0;
        bgsLeverage += 1;
      }
    }
    return { totalAdults, leverageAdults, bgsLeverage, bgsTotal: bgs.length };
  }, [bgs]);

  const stateName = ALL_STATES.find((s) => s[0] === stateFips)?.[2] || "—";

  return (
    <>
      <h1 className="title">
        <span className="title-hook">Where EMS routing has the most leverage:</span>
        block-group centroids by the gap between the two nearest PCI hospitals, by state
      </h1>

      <div className="states-picker">
        <label htmlFor="states-select" className="states-picker-label">
          State
        </label>
        <select
          id="states-select"
          className="states-picker-select"
          value={stateFips}
          onChange={handleStateChange}
        >
          {ALL_STATES.map(([fips, usps, name]) => {
            const status = STATE_STATUS[fips];
            return (
              <option key={fips} value={fips} disabled={!!status}>
                {name} ({usps}){status ? ` — ${status}` : ""}
              </option>
            );
          })}
        </select>
        <div className="states-readout">
          {loadStatus === "loading" && (
            <span className="states-readout-lbl">Loading {stateName}&hellip;</span>
          )}
          {loadStatus === "error" && (
            <span className="states-readout-lbl" style={{ color: "#C8102E" }}>
              Couldn&rsquo;t load {stateName} data.
            </span>
          )}
          {loadStatus === "ready" && (
            <>
              <span className="states-readout-val">{totals.totalAdults.toLocaleString()}</span>
              <span className="states-readout-lbl">adults 20+ in {stateName}</span>
              <span className="states-readout-sep">&middot;</span>
              <span className="states-readout-val">{totals.leverageAdults.toLocaleString()}</span>
              <span className="states-readout-lbl">
                in BGs with T2&minus;T1 &lt; 5 min
              </span>
              <span className="states-readout-sep">&middot;</span>
              <span className="states-readout-val">~{Math.round(totals.leverageAdults * INCIDENCE_RATE).toLocaleString()}</span>
              <span className="states-readout-lbl">STEMI/yr there</span>
            </>
          )}
        </div>
      </div>

      <div className="map-wrap">
        <StateBGScatter
          stateFips={stateFips}
          bgs={bgs}
          hospitals={relevantHospitals}
          onHoverBG={handleHoverBG}
          onHoverHospital={handleHoverHospital}
          position={position}
          onMoveEnd={setPosition}
        />
        <LeverageLegend />
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
        <BGSizeLegend />
      </div>

      <p className="subtitle">
        Each dot is a block-group population centroid. Dot <em>size</em> shows the adult population in
        the BG; dot <em>color</em> shows the gap between the nearest two PCI hospitals -- darker dots are
        BGs where routing decisions have the most leverage. Hover a dot for the two hospitals involved.
      </p>

      <p className="sources">
        Sources: CMS Provider of Services (Dec 2024)&nbsp;&middot;&nbsp;Census CenPop 2020&nbsp;&middot;&nbsp;
        ACS 2019&ndash;2023 5-year (B01001)<br />
        OpenStreetMap (Geofabrik US, May 2026)&nbsp;&middot;&nbsp;OSRM road-network routing&nbsp;&middot;&nbsp;
        <a href="https://github.com/rgaiba/stemi-fmc-to-device" target="_blank" rel="noreferrer">
          github.com/rgaiba/stemi-fmc-to-device
        </a>
      </p>

      {hovered && hovered.type === "bg" && (
        <BGTooltip data={hovered.data} x={hovered.x} y={hovered.y} hospitalsByCcn={hospitalsByCcn} />
      )}
      {hovered && hovered.type === "hospital" && (
        <HospitalTooltip data={hovered.data} x={hovered.x} y={hovered.y} />
      )}
    </>
  );
}

// Vertical sequential color bar matching the Map page's structure, but
// labeled in delta-minutes (the variable the dot color encodes) instead
// of adult counts. Bottom of bar = large T2-T1 (no leverage, near-white);
// top of bar = small T2-T1 (high leverage, near-black teal).
// Inline mini-legend for BG dot size. Three reference circles at
// population checkpoints (200, 1,000, 5,000 adults). Dots are sized to
// match the on-screen radii rendered by StateBGScatter (constant
// regardless of zoom), so the legend reads as literal-size.
function BGSizeLegend() {
  const stops = [200, 1000, 5000];
  // Match StateBGScatter's rUnz formula (1.5 + 0.08*sqrt(pop)):
  //   pop=200: 2.6, pop=1k: 4.0, pop=5k: 7.2.
  const radii = [2.6, 4.0, 7.2];
  const W = 175;
  const H = 30;
  const centers = [18, 60, 115];
  return (
    <span className="bg-size-legend" aria-label="Dot size encodes adult population">
      <svg width={W} height={H} viewBox={`0 0 ${W} ${H}`}>
        {stops.map((p, i) => (
          <g key={p}>
            <circle
              cx={centers[i]}
              cy={H / 2 - 2}
              r={radii[i]}
              fill="#5C9690"
              fillOpacity={0.9}
              stroke="#444"
              strokeWidth={0.3}
            />
            <text
              x={centers[i]}
              y={H - 2}
              fontSize="8"
              textAnchor="middle"
              fill="#666"
              fontFamily="ui-monospace, monospace"
            >
              {p.toLocaleString()}
            </text>
          </g>
        ))}
        <text x={145} y={H / 2} fontSize="9" fill="#666" fontFamily="ui-sans-serif, sans-serif">adults</text>
      </svg>
    </span>
  );
}

function LeverageLegend() {
  const ticks = [
    { label: "30+ min" },
    { label: "10 min" },
    { label: "5 min" },
    { label: "2 min" },
    { label: "<1 min" },
  ];
  const barH = 220;
  return (
    <div className="colorbar" aria-hidden="true">
      <div className="colorbar-header">
        T2&minus;T1<br />gap
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

function BGTooltip({ data, x, y, hospitalsByCcn }) {
  const { bg, adult_pop, t1_min, t2_min, delta_min, ccn1, ccn2 } = data;
  const h1 = ccn1 ? hospitalsByCcn.get(ccn1) : null;
  const h2 = ccn2 ? hospitalsByCcn.get(ccn2) : null;
  const stemi = Math.round((adult_pop || 0) * 0.001);
  return (
    <div className="tooltip" style={{ left: x, top: y }}>
      <div className="ttitle">Block group {bg}</div>
      <div className="trow"><span className="lbl">Adults 20+</span><span className="val">{(adult_pop || 0).toLocaleString()}</span></div>
      <div className="trow"><span className="lbl">STEMI/yr (here)</span><span className="val">~{stemi.toLocaleString()}</span></div>
      <div className="trow"><span className="lbl">T1 (nearest)</span>
        <span className="val">
          {t1_min != null ? `${t1_min.toFixed(1)} min` : "n/a"}
          {h1 && <> &middot; {titleCase(h1.name)}</>}
        </span>
      </div>
      <div className="trow"><span className="lbl">T2 (second)</span>
        <span className="val">
          {t2_min != null ? `${t2_min.toFixed(1)} min` : "n/a"}
          {h2 && <> &middot; {titleCase(h2.name)}</>}
        </span>
      </div>
      <div className="trow"><span className="lbl">T2 &minus; T1</span>
        <span className="val">{delta_min != null ? `${delta_min.toFixed(1)} min` : "n/a"}</span>
      </div>
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

// CMS PoS names are ALL CAPS; soften without losing fidelity. Acronyms
// (USA / UC / VA) stay all-caps via the 2-char short-token allowlist.
function titleCase(s) {
  if (!s) return "";
  return s
    .split(/\s+/)
    .map((w) => (w.length <= 2 ? w : w[0] + w.slice(1).toLowerCase()))
    .join(" ");
}

// Same matched-icon set the Map and Strata pages use.
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
  return (
    <svg {...common}>
      <path d="M12.5 8 A 4.5 4.5 0 1 1 8 3.5" />
      <polyline points="8.2,1.6 8,3.5 9.9,3.7" />
    </svg>
  );
}
