import { useMemo, useRef, useState } from 'react';
import {
  SVG_W,
  SVG_H,
  PAD,
  PROJECTION_BOUNDS,
  project,
  rampColor,
  MAX_POP,
} from '../lib/geometry.js';

const LAT_LINES = [38.5, 39.0, 39.5, 40.0];
// Response-time scale tops out at 12 min — most of the population is well
// under that, and color saturating past 12 makes the map readable.
const MAX_RESPONSE_MIN = 12;

function PostMarker({ lat, lon, label, highlight }) {
  const pt = project(lat, lon);
  const fill = highlight ? '#b8860b' : '#1a1e2e';
  return (
    <g>
      <circle cx={pt.x} cy={pt.y} r={11} fill="none" stroke={fill} strokeOpacity={0.18} strokeWidth={0.5} />
      <circle cx={pt.x} cy={pt.y} r={5} fill="#ffffff" stroke={fill} strokeWidth={1.4} />
      <circle cx={pt.x} cy={pt.y} r={2.2} fill={fill} />
      {label && (
        <text
          x={pt.x + 9}
          y={pt.y + 3}
          fontSize={8}
          fontFamily="JetBrains Mono, monospace"
          fontWeight={500}
          fill={fill}
          stroke="#f4f5f8"
          strokeWidth={2}
          strokeLinejoin="round"
          style={{ paintOrder: 'stroke' }}
        >
          {label}
        </text>
      )}
    </g>
  );
}

function Compass() {
  return (
    <g transform={`translate(${SVG_W - 38},38)`}>
      <circle r={17} fill="none" stroke="rgba(0,0,0,0.12)" strokeWidth={0.5} />
      <path d="M0,-13 L0,13" stroke="rgba(0,0,0,0.2)" strokeWidth={0.5} />
      <path d="M-13,0 L13,0" stroke="rgba(0,0,0,0.2)" strokeWidth={0.5} />
      <text y={-19} textAnchor="middle" fontSize={7} fill="#8892aa" fontFamily="JetBrains Mono, monospace">
        N
      </text>
    </g>
  );
}

export default function PostsMap({
  title,
  badgeText,
  badgeClass,
  stats,
  detail,
  posts,
  postLabels = false,
  patternId,
}) {
  const wrapRef = useRef(null);
  const svgRef = useRef(null);
  const [hover, setHover] = useState(null);

  // Sort by response time so worst-served block groups render on top.
  const sorted = useMemo(() => [...detail].sort((a, b) => a.mins - b.mins), [detail]);

  const tooltipStyle = useMemo(() => {
    if (!hover || !wrapRef.current || !svgRef.current) return { display: 'none' };
    const sr = svgRef.current.getBoundingClientRect();
    const wr = wrapRef.current.getBoundingClientRect();
    const scX = sr.width / SVG_W;
    const scY = sr.height / SVG_H;
    const px = sr.left + hover.pt.x * scX;
    const py = sr.top + hover.pt.y * scY;
    let left = px - wr.left + 12;
    let top = py - wr.top - 68;
    if (left + 170 > wr.width) left = px - wr.left - 174;
    if (top < 4) top = py - wr.top + 12;
    return { left, top, opacity: 1 };
  }, [hover]);

  return (
    <div className="map-card">
      <div className="map-card-header">
        <div className="map-card-title">{title}</div>
        <div className={`map-badge ${badgeClass}`}>{badgeText}</div>
      </div>
      <div className="map-stats-bar">
        <div className="mstat">
          <div className="mstat-n" style={{ color: '#1a7a50' }}>{stats.pct8}%</div>
          <div className="mstat-l">within 8 min</div>
        </div>
        <div className="mstat">
          <div className="mstat-n" style={{ color: '#b8860b' }}>{stats.meanMins}</div>
          <div className="mstat-l">mean min</div>
        </div>
        <div className="mstat">
          <div className="mstat-n" style={{ color: '#1a1e2e' }}>{posts.length}</div>
          <div className="mstat-l">posts</div>
        </div>
      </div>
      <div className="svg-wrap" ref={wrapRef}>
        <svg
          ref={svgRef}
          className="map-svg"
          viewBox={`0 0 ${SVG_W} ${SVG_H}`}
          xmlns="http://www.w3.org/2000/svg"
        >
          <defs>
            <pattern id={patternId} width="36" height="36" patternUnits="userSpaceOnUse">
              <path d="M 36 0 L 0 0 0 36" fill="none" stroke="rgba(0,0,0,0.045)" strokeWidth={0.5} />
            </pattern>
          </defs>
          <rect width={SVG_W} height={SVG_H} fill="#f4f5f8" />
          <rect width={SVG_W} height={SVG_H} fill={`url(#${patternId})`} />

          {LAT_LINES.map((lat) => {
            const y = project(lat, PROJECTION_BOUNDS.minLon).y;
            if (y < 6 || y > SVG_H - 6) return null;
            return (
              <g key={lat}>
                <line
                  x1={PAD - 4}
                  y1={y}
                  x2={SVG_W - PAD + 4}
                  y2={y}
                  stroke="rgba(0,0,0,0.1)"
                  strokeDasharray="2 5"
                />
                <text
                  x={SVG_W - PAD + 7}
                  y={y + 3}
                  fontSize={7}
                  fill="#8892aa"
                  fontFamily="JetBrains Mono, monospace"
                >
                  {lat.toFixed(1)}°N
                </text>
              </g>
            );
          })}

          {sorted.map((d, idx) => {
            const pt = project(d.lat, d.lon);
            const r = 1.5 + Math.sqrt(d.p / MAX_POP) * 11;
            const col = rampColor(d.mins / MAX_RESPONSE_MIN);
            const isHover = hover && hover.d === d;
            return (
              <circle
                key={idx}
                cx={pt.x}
                cy={pt.y}
                r={isHover ? r + 2 : r}
                fill={col}
                fillOpacity={0.83}
                stroke={isHover ? '#fff' : col}
                strokeOpacity={0.9}
                strokeWidth={isHover ? 1.1 : 0.3}
                style={{ cursor: 'crosshair' }}
                onMouseEnter={() => setHover({ d, pt })}
                onMouseLeave={() => setHover(null)}
              />
            );
          })}

          {posts.map((p, idx) => (
            <PostMarker
              key={p.id || `${p.lat}-${p.lon}-${idx}`}
              lat={p.lat}
              lon={p.lon}
              label={postLabels ? p.name : null}
              highlight={p.highlight}
            />
          ))}

          <Compass />
        </svg>
        <div className={`tt ${hover ? 'show' : ''}`} style={tooltipStyle}>
          {hover && (
            <>
              <div className="tt-lbl">Population</div>
              <div className="tt-pop">{hover.d.p.toLocaleString()}</div>
              <div className="tt-time">~{hover.d.mins.toFixed(1)} min response</div>
            </>
          )}
        </div>
      </div>
    </div>
  );
}
