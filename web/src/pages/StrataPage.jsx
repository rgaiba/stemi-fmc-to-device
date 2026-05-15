import React, { useMemo, useState } from "react";
import CountyStrataChoropleth from "../components/CountyStrataChoropleth.jsx";
import counties from "../data/county_strata.json";

const DEFAULT_POSITION = { coordinates: [-96, 37.5], zoom: 1 };

// Single-hue sequential ramps. Map and histogram both use the deep
// teal endpoint (#062E2A) so the strata map and the main Map share a
// color family, and the histogram bars read crisply against the light
// card surface under the map.
const HUE_MAP = "#062E2A";
const HUE_HIST = "#062E2A";

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
    const rgb = hexToRgb(HUE_MAP);
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

      <div className="map-wrap">
        <CountyStrataChoropleth
          counties={counties}
          fillFor={sliderFill}
          onHoverCounty={handleHover}
          position={position}
          onMoveEnd={setPosition}
        />
        <SequentialLegend hue={HUE_MAP} alphaFor={alphaForCount} />
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

      {/* Compact light card sitting under the map. Controls (threshold,
          slider, live readouts) stack on the left; the histogram with X
          and Y axes occupies the right. Same monospace family as the BG
          hover, but inverted to a light surface so it reads as a quiet
          companion strip rather than a dominant floating panel. */}
      <div className="strata-card">
        <div className="strata-card-controls">
          <label htmlFor="strata-threshold" className="strata-card-title">
            T2 &minus; T1 &lt;&nbsp;
            <span className="strata-card-value">{threshold}</span>
            &nbsp;min
          </label>
          <input
            id="strata-threshold"
            className="strata-card-slider"
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
          <div className="strata-card-rows">
            <div className="strata-card-row">
              <span className="lbl">Adults 20+</span>
              <span className="val">{(totals.adults / 1e6).toFixed(1)}M</span>
            </div>
            <div className="strata-card-row">
              <span className="lbl">STEMI/yr</span>
              <span className="val">~{totals.stemi.toLocaleString()}</span>
            </div>
          </div>
        </div>
        <div className="strata-card-graph">
          <StrataHistogram threshold={threshold} hue={HUE_HIST} />
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
  // Coordinate system: tight viewBox -- the card lives below the map,
  // so we keep this strip as low-profile as possible while still giving
  // both axes proper labels. ~110px tall in render at most aspect
  // ratios; bars hold their shape because pdfPerMinute is 30 bins wide.
  const VW = 360, VH = 120;
  const M = { top: 6, right: 6, bottom: 22, left: 34 };
  const plotW = VW - M.left - M.right;
  const plotH = VH - M.top - M.bottom;
  const barW = plotW / N_BINS;
  const rgb = hexToRgb(hue);

  // Y-axis: round pdfMax up to the next 10M so ticks land on clean
  // round numbers. Ticks every 10M, labeled "10M" / "20M" / ...
  const yStep = 10_000_000;
  const yMax = Math.max(yStep, Math.ceil(pdfMax / yStep) * yStep);
  const yTicks = [];
  for (let v = 0; v <= yMax; v += yStep) yTicks.push(v);

  const xScale = (i) => M.left + i * barW;
  const yScale = (v) => M.top + plotH - (v / yMax) * plotH;
  const xBase = M.top + plotH;

  return (
    <svg
      className="strata-histogram"
      viewBox={`0 0 ${VW} ${VH}`}
      preserveAspectRatio="xMidYMid meet"
      role="img"
      aria-label="Adult-weighted distribution of T2 minus T1 minutes across CONUS"
    >
      {/* Faint horizontal gridlines at each Y tick */}
      {yTicks.map((v) => (
        <line
          key={`gl-${v}`}
          x1={M.left}
          y1={yScale(v)}
          x2={M.left + plotW}
          y2={yScale(v)}
          stroke="rgba(0,0,0,0.06)"
          strokeWidth={0.6}
        />
      ))}

      {/* Bars: under-threshold bars use the page hue; bars at/above
          render as warm gray so the slider cut is visible. */}
      {pdfPerMinute.map((val, i) => {
        const y = yScale(val);
        const h = Math.max(0, xBase - y);
        const isUnder = i < threshold;
        const fill = isUnder ? `rgb(${rgb})` : "#D5D2CD";
        return (
          <rect
            key={i}
            x={xScale(i) + 0.5}
            y={y}
            width={Math.max(0, barW - 1)}
            height={h}
            fill={fill}
          />
        );
      })}

      {/* Threshold marker: dashed vertical at the slider's current X. */}
      <line
        x1={xScale(threshold)}
        y1={M.top}
        x2={xScale(threshold)}
        y2={xBase}
        stroke="rgba(0,0,0,0.55)"
        strokeWidth={1}
        strokeDasharray="2 2"
      />

      {/* Axes (clean L-shape) */}
      <line x1={M.left} y1={xBase} x2={M.left + plotW} y2={xBase}
            stroke="rgba(0,0,0,0.35)" strokeWidth={0.7} />
      <line x1={M.left} y1={M.top} x2={M.left} y2={xBase}
            stroke="rgba(0,0,0,0.35)" strokeWidth={0.7} />

      {/* Y-axis ticks and labels */}
      {yTicks.map((v) => (
        <g key={`yt-${v}`}>
          <line
            x1={M.left - 2.5}
            y1={yScale(v)}
            x2={M.left}
            y2={yScale(v)}
            stroke="rgba(0,0,0,0.35)"
            strokeWidth={0.6}
          />
          <text
            x={M.left - 4}
            y={yScale(v)}
            fontSize="7.5"
            fill="rgba(0,0,0,0.6)"
            textAnchor="end"
            dominantBaseline="middle"
            fontFamily="ui-monospace, monospace"
          >
            {v === 0 ? "0" : `${(v / 1e6).toFixed(0)}M`}
          </text>
        </g>
      ))}

      {/* X-axis ticks and labels (every 5 minutes) */}
      {[0, 5, 10, 15, 20, 25, 30].map((t) => (
        <g key={`xt-${t}`}>
          <line
            x1={xScale(t)}
            y1={xBase}
            x2={xScale(t)}
            y2={xBase + 2.5}
            stroke="rgba(0,0,0,0.35)"
            strokeWidth={0.6}
          />
          <text
            x={xScale(t)}
            y={xBase + 10}
            fontSize="7.5"
            fill="rgba(0,0,0,0.6)"
            textAnchor="middle"
            fontFamily="ui-monospace, monospace"
          >
            {t}
          </text>
        </g>
      ))}

      {/* X-axis title (compact, inline with last tick) */}
      <text
        x={M.left + plotW}
        y={VH - 2}
        fontSize="7.5"
        fill="rgba(0,0,0,0.45)"
        textAnchor="end"
        fontStyle="italic"
        fontFamily="ui-monospace, monospace"
      >
        T2 &#8722; T1 (min)
      </text>
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
            style={{ top: `${barH - (i / (ticks.length - 1)) * barH}px` }}
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
