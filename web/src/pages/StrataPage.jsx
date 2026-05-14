import React, { useMemo, useState } from "react";
import CountyStrataChoropleth from "../components/CountyStrataChoropleth.jsx";
import counties from "../data/county_strata.json";

const DEFAULT_POSITION = { coordinates: [-96, 37.5], zoom: 1 };

// Single-hue sequential ramp. Same deep teal as the Map page so the two
// surfaces feel like one product. Opacity carries the per-county count.
const HUE = "#062E2A";

// Slider range and default. 15 min is the abstract's headline threshold;
// landing the slider here on first load shows the published number.
const X_MIN = 1;
const X_MAX = 30;
const X_DEFAULT = 15;

// STEMI incidence rate, identical to step 06 / step 07. Used to render the
// live STEMI/yr readout under the slider.
const INCIDENCE_RATE = 0.001;

function hexToRgb(hex) {
  const r = parseInt(hex.slice(1, 3), 16);
  const g = parseInt(hex.slice(3, 5), 16);
  const b = parseInt(hex.slice(5, 7), 16);
  return `${r}, ${g}, ${b}`;
}

// Log alpha: maps adults-under-threshold in [1, 10M] to alpha in [0.15, 1.0].
// 0 adults -> caller short-circuits to gray instead of calling this.
function alphaForCount(n) {
  if (!n || n <= 0) return 0;
  const x = Math.log10(Math.max(1, n));   // 0 .. ~7
  return Math.max(0.15, Math.min(1.0, 0.15 + x * (0.85 / 7)));
}

// CDF lookup helper: 0-indexed. cdf[X-1] = adults with margin < X minutes.
function cdfAt(entry, X) {
  if (!entry || !entry.cdf || X < 1 || X > entry.cdf.length) return 0;
  return entry.cdf[X - 1] | 0;
}

// National adult-weighted PDF across the 30 one-minute bins, precomputed
// once at module load (the data is static for the page's lifetime).
// pdfPerMinute[i] = adults across CONUS with margin in [i, i+1) minutes.
// Derived directly from the per-county CDFs by summing then differencing,
// which yields the same totals as aggregating from BG-level (verified
// against step 07b's reconciliation output).
const N_BINS = 30;
const pdfPerMinute = (() => {
  const cdfSum = new Array(N_BINS).fill(0);
  for (const fips in counties) {
    const c = counties[fips].cdf;
    if (!c) continue;
    for (let i = 0; i < N_BINS; i++) cdfSum[i] += c[i] | 0;
  }
  const pdf = new Array(N_BINS).fill(0);
  pdf[0] = cdfSum[0];
  for (let i = 1; i < N_BINS; i++) pdf[i] = cdfSum[i] - cdfSum[i - 1];
  return pdf;
})();
const pdfMax = Math.max(...pdfPerMinute);

export default function StrataPage() {
  const [threshold, setThreshold] = useState(X_DEFAULT);
  const [hovered, setHovered] = useState(null);
  const [position, setPosition] = useState(DEFAULT_POSITION);

  const handleZoomIn  = () => setPosition((p) => ({ ...p, zoom: Math.min(p.zoom * 1.5, 8) }));
  const handleZoomOut = () => setPosition((p) => ({ ...p, zoom: Math.max(p.zoom / 1.5, 1) }));
  const handleResetView = () => setPosition(DEFAULT_POSITION);

  const handleHover = (entry, evt) => {
    if (entry && evt) {
      setHovered({ data: entry, x: evt.clientX, y: evt.clientY });
    } else {
      setHovered(null);
    }
  };

  // Per-county fill at the current threshold. Memoized on `threshold` so
  // we don't rebuild the closure each render unless the slider moved.
  const sliderFill = useMemo(() => {
    const rgb = hexToRgb(HUE);
    return (entry) => {
      const n = cdfAt(entry, threshold);
      if (n <= 0) return "#E5E5E5";
      const a = alphaForCount(n);
      return `rgba(${rgb}, ${a.toFixed(3)})`;
    };
  }, [threshold]);

  // National totals at the current threshold (live readout under slider).
  const totals = useMemo(() => {
    let adults = 0;
    for (const fips in counties) {
      adults += cdfAt(counties[fips], threshold);
    }
    const stemi = Math.round(adults * INCIDENCE_RATE);
    return { adults, stemi };
  }, [threshold]);

  return (
    <>
      <h1 className="title">
        <span className="title-hook">STEMI patient burden by routing window:</span>
        adults living within X minutes of a second PCI hospital, slider-driven
      </h1>

      <div className="strata-slider">
        <label htmlFor="strata-threshold" className="strata-slider-label">
          T2 &minus; T1 &lt;&nbsp;
          <span className="strata-slider-value">{threshold}</span>
          &nbsp;min
        </label>
        <input
          id="strata-threshold"
          className="strata-slider-input"
          type="range"
          min={X_MIN}
          max={X_MAX}
          step={1}
          value={threshold}
          onChange={(e) => setThreshold(parseInt(e.target.value, 10))}
          aria-valuemin={X_MIN}
          aria-valuemax={X_MAX}
          aria-valuenow={threshold}
        />
        <div className="strata-slider-readout">
          <span className="strata-slider-readout-val">{(totals.adults / 1e6).toFixed(1)}M</span>
          <span className="strata-slider-readout-lbl">adults</span>
          <span className="strata-slider-readout-sep">&middot;</span>
          <span className="strata-slider-readout-val">~{totals.stemi.toLocaleString()}</span>
          <span className="strata-slider-readout-lbl">STEMI/yr</span>
        </div>
        <StrataHistogram threshold={threshold} hue={HUE} />
      </div>

      <div className="map-wrap">
        <CountyStrataChoropleth
          counties={counties}
          fillFor={sliderFill}
          onHoverCounty={handleHover}
          position={position}
          onMoveEnd={setPosition}
        />
        <SequentialLegend hue={HUE} alphaFor={alphaForCount} />
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

      <p className="subtitle">
        Each county is shaded by the number of adults whose nearest two PCI hospitals
        are within {threshold} minutes of each other. Opacity is log-scaled so rural counties stay
        visible without urban counties losing their visual weight. Gray means no part of
        the county has a second PCI hospital within {threshold} minutes; routing has no leverage there.
      </p>

      <p className="strata-foot">
        Threshold uses strict less-than (T2 &minus; T1 &lt; X min). The abstract's published
        headline of 196,253 STEMI/yr uses T2 &minus; T1 &le; 15 min and differs by 34 patients
        (~0.02%) due to boundary inclusion at exactly 15.0 min.
      </p>

      <p className="sources">
        Sources: CMS Provider of Services (Dec 2024)&nbsp;&middot;&nbsp;Census CenPop 2020&nbsp;&middot;&nbsp;
        ACS 2019-2023 5-year (B01001)<br />
        OpenStreetMap (Geofabrik US, May 2026)&nbsp;&middot;&nbsp;OSRM road-network routing&nbsp;&middot;&nbsp;
        <a href="https://github.com/rgaiba/stemi-fmc-to-device" target="_blank" rel="noreferrer">
          github.com/rgaiba/stemi-fmc-to-device
        </a>
      </p>

      {hovered && <SliderTooltip data={hovered.data} x={hovered.x} y={hovered.y} threshold={threshold} />}
    </>
  );
}

// Live distribution histogram anchored beneath the slider. 30 one-minute
// bars showing the adult-weighted PDF of T2-T1 across CONUS; bars whose
// minute index is < threshold (i.e., inside the current slider window) use
// the page hue, bars at or beyond render dimmed. A dashed vertical line
// marks where the slider currently cuts the distribution. Shape detail:
// CONUS adult distribution of T2-T1 is strongly right-skewed (~14% live
// in BGs with margin < 1 min), nothing close to normal — the histogram
// makes that visible at a glance and turns the slider into a guided
// reading of the distribution.
function StrataHistogram({ threshold, hue }) {
  const W = 600;
  const H = 56;
  const barW = W / N_BINS;
  const rgb = hexToRgb(hue);
  return (
    <svg
      className="strata-histogram"
      viewBox={`0 0 ${W} ${H + 18}`}
      preserveAspectRatio="xMidYMid meet"
      role="img"
      aria-label="Adult-weighted distribution of T2 minus T1 minutes across CONUS"
    >
      {pdfPerMinute.map((val, i) => {
        const h = (val / pdfMax) * (H - 2);
        const x = i * barW;
        const y = H - h;
        const isUnder = i < threshold;
        const fill = isUnder ? `rgb(${rgb})` : "#D5D2CD";
        return <rect key={i} x={x + 0.5} y={y} width={barW - 1} height={h} fill={fill} />;
      })}
      {/* Threshold marker: dashed vertical at the slider's current X. */}
      <line
        x1={threshold * barW}
        y1={0}
        x2={threshold * barW}
        y2={H}
        stroke={`rgb(${rgb})`}
        strokeWidth={1.2}
        strokeDasharray="2 2"
      />
      {/* X-axis ticks every 5 minutes. */}
      {[0, 5, 10, 15, 20, 25, 30].map((t) => (
        <g key={t}>
          <line x1={t * barW} y1={H} x2={t * barW} y2={H + 3} stroke="#888" strokeWidth={0.5} />
          <text
            x={t * barW}
            y={H + 14}
            fontSize="8"
            textAnchor="middle"
            fill="#666"
            fontFamily="ui-monospace, monospace"
          >
            {t}
          </text>
        </g>
      ))}
    </svg>
  );
}

// Sequential color bar: vertical strip from low-alpha to full-alpha at the
// page's single hue. Mirrors the Map page's colorbar structure so the two
// pages share a visual vocabulary.
function SequentialLegend({ hue, alphaFor }) {
  const rgb = hexToRgb(hue);
  // Stops for the gradient at log-breakpoint positions, so the visual
  // gradient is honest about being log-scaled.
  const stops = [1, 100, 10_000, 1_000_000, 10_000_000];
  const grad = stops
    .map((v, i) => {
      const a = alphaFor(v);
      const pct = (i / (stops.length - 1)) * 100;
      return `rgba(${rgb}, ${a.toFixed(3)}) ${pct}%`;
    })
    .join(", ");
  // Tick labels at decade marks across the bar's height (220px). Position
  // is computed bottom-up; bar bottom = 0 adults (faintest), top = 10M+.
  const ticks = [
    { val: 1,         label: "1" },
    { val: 100,       label: "100" },
    { val: 10_000,    label: "10K" },
    { val: 1_000_000, label: "1M" },
    { val: 10_000_000, label: "10M+" },
  ];
  const barH = 220;
  return (
    <div className="colorbar" aria-hidden="true">
      <div className="colorbar-header">
        adults<br />in county
      </div>
      <div
        className="colorbar-track"
        style={{ background: `linear-gradient(to top, ${grad})` }}
      />
      <div className="colorbar-ticks" style={{ position: "absolute", left: 30, top: 26, height: barH }}>
        {ticks.map((t, i) => (
          <span
            key={t.label}
            className="colorbar-tick"
            style={{ bottom: `${(i / (ticks.length - 1)) * barH - 6}px` }}
          >
            {t.label}
          </span>
        ))}
      </div>
    </div>
  );
}

function SliderTooltip({ data, x, y, threshold }) {
  const { name, state, adult_pop, cdf } = data;
  const under = cdf ? (cdf[threshold - 1] || 0) : 0;
  const stemi = Math.round(under * INCIDENCE_RATE);
  return (
    <div className="tooltip" style={{ left: x, top: y }}>
      <div className="ttitle">{name} County, {state}</div>
      <div className="trow"><span className="lbl">Adults 20+</span><span className="val">{adult_pop.toLocaleString()}</span></div>
      <div className="trow"><span className="lbl">At &lt;{threshold} min</span><span className="val">{under.toLocaleString()}</span></div>
      <div className="trow"><span className="lbl">STEMI/yr (here)</span><span className="val">~{stemi.toLocaleString()}</span></div>
    </div>
  );
}

// Matched-symmetry icons, ported verbatim from MapPage.
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
