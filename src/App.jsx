import { useMemo } from 'react';
import './App.css';
import { HOSPITALS_CURRENT, HOSPITALS_WITH_MILFORD } from './data/hospitals.js';
import { computeAccessTimes, summarize } from './lib/geometry.js';
import AccessMap from './components/AccessMap.jsx';
import HospitalList from './components/HospitalList.jsx';
import Legend from './components/Legend.jsx';

export default function App() {
  const dataCurrent = useMemo(() => computeAccessTimes(HOSPITALS_CURRENT), []);
  const dataMilford = useMemo(() => computeAccessTimes(HOSPITALS_WITH_MILFORD), []);

  const statsCurrent = useMemo(() => summarize(dataCurrent), [dataCurrent]);
  const statsMilford = useMemo(() => summarize(dataMilford), [dataMilford]);

  // Residents who move from >30 min to ≤30 min when Milford is added.
  const gained = statsCurrent.b30 - statsMilford.b30;
  const gainPct = ((gained / statsCurrent.tot) * 100).toFixed(1);

  return (
    <>
      <nav>
        <div className="nav-logo">Travel Time to PCI Centers, Delaware</div>
        <div className="nav-meta">CenPop 2020 · Block Group · April 2026</div>
      </nav>

      <div className="hero">
        <div>
          <div className="hero-eyebrow">U.S. Census Bureau · CenPop2020 · FIPS 10 · Delaware</div>
          <h1>
            Travel Time to <em>PCI Centers</em>, Delaware
          </h1>
          <p className="hero-sub">
            Each dot is a census block group centroid. <strong>Size</strong> = population.{' '}
            <strong>Color</strong> = estimated drive time to nearest PCI-capable hospital. Right map
            shows the effect of adding <strong>Bayhealth Milford</strong>.
          </p>
        </div>
        <div className="stat-row">
          <div className="stat-card">
            <div className="stat-label">
              Residents gaining
              <br />
              ≤30 min access
            </div>
            <div className="stat-value" style={{ color: '#1a7a50' }}>
              +{gained.toLocaleString()}
            </div>
          </div>
        </div>
      </div>

      <div className="maps-wrapper">
        <div className="maps-grid">
          <div className="map-column">
            <AccessMap
              title="Current PCI Network"
              badgeText="Without Bayhealth Milford"
              badgeClass="badge-current"
              stats={statsCurrent}
              data={dataCurrent}
              hospitals={HOSPITALS_CURRENT}
              patternId="grd-current"
            />
            <div className="map-column-panel">
              <HospitalList
                label="Current Network — 6 PCI Centers"
                hospitals={HOSPITALS_CURRENT}
              />
            </div>
          </div>
          <div className="map-column">
            <AccessMap
              title="With Bayhealth Milford"
              badgeText="+ 1 PCI Center"
              badgeClass="badge-scenario"
              stats={statsMilford}
              data={dataMilford}
              hospitals={HOSPITALS_WITH_MILFORD}
              patternId="grd-milford"
            />
            <div className="map-column-panel">
              <HospitalList
                label="With Milford — 7 PCI Centers"
                hospitals={HOSPITALS_WITH_MILFORD}
              />
              <div className="delta-box">
                <div className="delta-lbl">Access Gain</div>
                <div className="delta-val">+{gained.toLocaleString()} residents</div>
                <div className="delta-sub">(+{gainPct}% of pop.) gain ≤30 min access</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="legend-row">
        <Legend />
      </div>

      <div className="footnote">
        <div>SOURCE: U.S. CENSUS BUREAU · CENPOP2020_MEAN_BG10 · FIPS 10</div>
        <div>
          PCI CENTERS: CHRISTIANA CARE · BAYHEALTH KENT · BEEBE · TIDAL HEALTH MD · UM SHORE EASTON
          MD
        </div>
        <div>BAYHEALTH MEDICAL CENTER · DEPT. OF INTERNAL MEDICINE · APRIL 2026</div>
      </div>
    </>
  );
}
