import { useMemo } from 'react';
import postOptimization from '../data/postOptimization.json';
import PostsMap from '../components/PostsMap.jsx';

export default function AmbulancePostsPage() {
  const { current, optimal, nPosts, modelVersion, detourFactor, speedMph } = postOptimization;

  const meanDelta = useMemo(
    () => (current.summary.meanMins - optimal.summary.meanMins).toFixed(2),
    [current, optimal]
  );
  const meanDeltaPct = useMemo(
    () =>
      (((current.summary.meanMins - optimal.summary.meanMins) / current.summary.meanMins) * 100).toFixed(1),
    [current, optimal]
  );
  const pct8Delta = (optimal.summary.pct8 - current.summary.pct8).toFixed(1);

  return (
    <>
      <div className="hero">
        <div>
          <div className="hero-eyebrow">SSM POST-PLACEMENT MODEL · v1 (HAVERSINE) · BLOCK-GROUP DEMAND</div>
          <h1>
            Where should the <em>ambulances be parked</em>?
          </h1>
          <p className="hero-sub">
            Same number of ALS units, repositioned. Each dot is a census block group, sized by
            population, colored by estimated response time to the nearest paramedic post. Left:
            current home-station footprint. Right: theoretically optimal post locations from a{' '}
            <strong>p-median</strong> solve over a {nPosts}-post deployment.
          </p>
        </div>
        <div className="stat-row">
          <div className="stat-card">
            <div className="stat-label">
              Mean response
              <br />
              time saved
            </div>
            <div className="stat-value" style={{ color: '#1a7a50' }}>
              −{meanDelta} min
            </div>
          </div>
          <div className="stat-card">
            <div className="stat-label">
              ≤8 min coverage
              <br />
              improvement
            </div>
            <div className="stat-value" style={{ color: '#1a7a50' }}>
              +{pct8Delta} pp
            </div>
          </div>
        </div>
      </div>

      <div className="maps-wrapper">
        <div className="maps-grid">
          <div className="map-column">
            <PostsMap
              title="Current Home-Station Footprint"
              badgeText={`${current.posts.length} ALS Posts`}
              badgeClass="badge-current"
              stats={current.summary}
              detail={current.detail}
              posts={current.posts}
              postLabels={false}
              patternId="grd-posts-current"
            />
            <div className="map-column-panel">
              <div className="panel-lbl">Posts (Current)</div>
              <div className="post-grid">
                {current.posts.map((p) => (
                  <div key={p.id} className="post-row">
                    <span className="post-name">{p.name}</span>
                    <span className="post-city">{p.city.toUpperCase()}</span>
                    <span className={`post-county tag-${p.county.toLowerCase()}`}>{p.county}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
          <div className="map-column">
            <PostsMap
              title="Optimized Post Locations"
              badgeText="p-median solve"
              badgeClass="badge-scenario"
              stats={optimal.summary}
              detail={optimal.detail}
              posts={optimal.posts.map((p, idx) => ({ ...p, id: `opt-${idx}`, highlight: true }))}
              postLabels={false}
              patternId="grd-posts-optimal"
            />
            <div className="map-column-panel">
              <div className="panel-lbl">
                Improvement vs. Current
              </div>
              <div className="delta-grid">
                <div className="delta-cell">
                  <div className="delta-cell-lbl">Mean response</div>
                  <div className="delta-cell-val">
                    {current.summary.meanMins} → {optimal.summary.meanMins} min
                  </div>
                  <div className="delta-cell-sub" style={{ color: '#1a7a50' }}>
                    −{meanDelta} min ({meanDeltaPct}% faster)
                  </div>
                </div>
                <div className="delta-cell">
                  <div className="delta-cell-lbl">% within 8 min</div>
                  <div className="delta-cell-val">
                    {current.summary.pct8}% → {optimal.summary.pct8}%
                  </div>
                  <div className="delta-cell-sub" style={{ color: '#1a7a50' }}>
                    +{pct8Delta} percentage points
                  </div>
                </div>
                <div className="delta-cell">
                  <div className="delta-cell-lbl">% within 12 min</div>
                  <div className="delta-cell-val">
                    {current.summary.pct12}% → {optimal.summary.pct12}%
                  </div>
                  <div className="delta-cell-sub" style={{ color: '#1a7a50' }}>
                    +{(optimal.summary.pct12 - current.summary.pct12).toFixed(1)} percentage points
                  </div>
                </div>
              </div>
              <div className="delta-box" style={{ marginTop: 14 }}>
                <div className="delta-lbl">What this means</div>
                <div className="delta-sub">
                  Repositioning the same {nPosts} ALS units to the theoretically optimal posts —
                  no new construction, no additional vehicles — would shave {meanDelta} minutes
                  off the population-weighted mean response time and bring an additional{' '}
                  {Math.round((optimal.summary.pct8 - current.summary.pct8) / 100 * current.summary.totalPop).toLocaleString()}{' '}
                  Delawareans inside the 8-minute response standard.
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="footnote">
        <div>
          MODEL: {modelVersion.toUpperCase()} · HAVERSINE × {detourFactor} DETOUR @ {speedMph} MPH ·
          DEMAND WEIGHTED BY 2020 BLOCK-GROUP POPULATION
        </div>
        <div>
          OPTIMIZATION: P-MEDIAN OVER {' '}
          ~300 GRID CANDIDATE SITES · CBC SOLVER VIA PULP
        </div>
        <div>
          v1 IS DEMAND-DRIVEN ONLY · v2 ADDS OSRM ROAD ROUTING + AGE-STRATIFIED STEMI INCIDENCE +
          UNIT-BUSY CONSTRAINTS
        </div>
      </div>
    </>
  );
}
