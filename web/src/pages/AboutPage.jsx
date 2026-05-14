import React from "react";

// Data-sources content mirrors national/notes/data_sources_table.md.
// Keep the two in sync when sources change. Source-of-truth lives in
// the .md file; this JSX is the rendered web version.

const PRIMARY = [
  {
    n: 1,
    name: "CMS Provider of Services (PoS)",
    vintage: "Dec 2024 (NBER snapshot)",
    extract: [
      "CCN, provider subtype (01 short-term general / 11 critical access)",
      "cath_lab_service_code (1 or 3 → Tier A)",
      "cath_lab_room_count (for S6 sensitivity)",
      "Facility name, full address, state FIPS, bed count",
    ],
    produces: [
      "Hospital analysis universe (n = 4,408)",
      "Tier A PCI-capable (1,598) / Tier B non-PCI acute (2,810)",
      "Critical Access Hospital flag",
      "Geocoding input addresses",
    ],
  },
  {
    n: 2,
    name: "CMS IPPS DRG Public Use File",
    vintage: "FY2024",
    extract: [
      "Provider CCN, DRG codes 280/281/282 (AMI), Tot_Dschrgs",
    ],
    produces: [
      "ami_volume_2024 per hospital (Medicare FFS-only AMI discharges)",
      "AMI volume tertile within Tier A",
      "Retained for Paper 2; excluded from top_hospitals.csv supplement",
    ],
  },
  {
    n: 3,
    name: "CMS Hospital General Information",
    vintage: "2024",
    extract: [
      "Hospital lat/lon (primary geocoding source where matched)",
    ],
    produces: [
      "Hospital coordinates for OSRM destinations",
      "Highest-precision tier (street-level) for matched hospitals",
    ],
  },
  {
    n: 4,
    name: "Census Geocoder API",
    vintage: "2026 access",
    extract: [
      "Hospital lat/lon (fallback geocoder for unmatched hospitals)",
      "Precision tier returned per result",
    ],
    produces: [
      "Coordinates via 4-pass cascade (street → ZIP+4 → ZIP → ZIP-3)",
      "S1 sensitivity (drop ZIP-centroid + ZIP-prefix tiers)",
    ],
  },
  {
    n: 5,
    name: "Census 2020 CenPop Mean BG",
    vintage: "Decennial 2020 (CenPop2020_Mean_BG.txt)",
    extract: [
      "12-digit GEOID (STATEFP + COUNTYFP + TRACTCE + BLKGRPCE)",
      "LATITUDE, LONGITUDE, all-ages POPULATION",
    ],
    produces: [
      "BG centroid coordinates → OSRM origin points",
      "238,193-BG CONUS analysis universe",
      "county_fips construction for state/county aggregations",
      "All-ages population kept as context only after Amendment 2026-05-08-C",
    ],
  },
  {
    n: 6,
    name: "ACS 2019–2023 5-year, Table B01001 (Sex by Age)",
    vintage: "Released Dec 2024 via Census Data API",
    extract: [
      "Sex-by-age bands aged 20+ summed per BG",
      "(18 male bands B01001_008..025 + 18 female bands B01001_032..049)",
    ],
    produces: [
      "adult_pop_20plus per BG — the STEMI rate denominator",
      "248.3M CONUS adults aged 20+ national total",
      "stemi_per_yr = adult_pop_20plus × 0.001",
    ],
  },
  {
    n: 7,
    name: "TIGER 2023 Cartographic Boundary Files — Counties (1:5M)",
    vintage: "2023 vintage",
    extract: [
      "County polygons (multi-part shapes), GEOID, NAME, STATEFP",
    ],
    produces: [
      "Choropleth county boundaries (matplotlib + interactive web)",
      "9 CT Planning Region polygons → BG-centroid spatial join",
      "3,109 CONUS counties incl. CT planning regions post-crosswalk",
    ],
  },
  {
    n: 8,
    name: "OpenStreetMap North America extract + OSRM",
    vintage: "Geofabrik May 2026 extract; OSRM build on EC2 r6i.8xlarge",
    extract: [
      "Road network → driving-time matrix",
      "Every (BG centroid × hospital) pair within 150-mile haversine pre-filter",
    ],
    produces: [
      "drive_times.parquet (17.6M CCN × bg_id pairs)",
      "T1_PCI, T2_PCI, T1_any per BG",
      "competitive_margin_sec = T2_PCI − T1_PCI",
      "is_competitive_15 = (margin ≤ 15 min) — the headline classifier",
      "S4 AM-peak sensitivity (post-hoc metro multiplier)",
    ],
  },
];

const REFERENCES = [
  {
    n: 9,
    name: "AHA Heart Disease and Stroke Statistics 2024 (Tsao/Martin et al., Circulation)",
    vintage: "Published Jan 2024",
    extract: ["Published U.S. STEMI incidence rate referenced to adults aged 20+"],
    produces: [
      "INCIDENCE_RATE = 0.001 STEMI per adult/yr",
      "Cited in abstract Methods",
      "External validity check #1: implied national STEMI 248,269/yr inside published 250–280k range",
    ],
  },
  {
    n: 10,
    name: "Wang et al., Circulation 2024",
    vintage: "Published 2024",
    extract: ["Published 60-min PCI access estimate (91–95% of U.S. adults)"],
    produces: [
      "External validity check #2 in 06_classify_zones.py",
      "Compared to our 94.2% (concordant within published band)",
      "Cited implicitly in abstract Background",
    ],
  },
  {
    n: 11,
    name: "Concannon et al., Circ: Cardiovascular Quality and Outcomes 2014",
    vintage: "Published 2014",
    extract: ["Published 30-min PCI access estimate (~80% of U.S. adults)"],
    produces: [
      "External validity check #3 in 06_classify_zones.py",
      "Compared to our 80.6% (matches within 1 pp)",
    ],
  },
];

const DERIVED = [
  {
    artifact: "hospitals_classified.parquet",
    builtFrom: "(1) + (2) + (3) + (4)",
    purpose: "Canonical hospital frame: CCN, name, geocoded lat/lon, tier (A/B), AMI volume, critical access flag, geocoding precision tier",
  },
  {
    artifact: "zones_classified.parquet",
    builtFrom: "(5) + (6) + (7) + (8) + hospitals_classified",
    purpose: "Canonical per-BG analytic file. One row per CONUS BG with population, adult_pop_20plus, T1_PCI / T2_PCI / T1_any, competitive_margin_sec, is_competitive_10/15/20, cross_state flag",
  },
  {
    artifact: "state_summary.csv, county_summary.csv, top_hospitals.csv",
    builtFrom: "Aggregations over zones_classified.parquet",
    purpose: "State, county, and hospital rollups feeding abstract Results and supplement tables",
  },
  {
    artifact: "sensitivity_table.csv",
    builtFrom: "09_sensitivities.py over zones + drive_times",
    purpose: "Six pre-registered sensitivity analyses; basis for the 'robust within ±25%' robustness claim",
  },
];

export default function AboutPage() {
  return (
    <article className="about">
      <h1 className="about-title">About this analysis</h1>

      <p className="about-lede">
        This is a cross-sectional national analysis of U.S. PCI competitive transfer zones —
        areas where a second PCI-capable hospital is reachable within 15 additional minutes
        of the nearest, and where EMS routing to the hospital with shorter door-to-balloon
        time may shorten time to reperfusion after STEMI. The map at <NavLinkInline path="/" label="/" /> is
        a county-level summary; this page documents the data sources behind it.
      </p>

      <section>
        <h2>Headline finding</h2>
        <p>
          196,253 STEMI patients per year — about 79% of estimated U.S. STEMI cases — live
          in 15-min competitive zones, distributed across approximately 1,550 PCI-capable
          hospitals. Findings hold across all six pre-specified sensitivity analyses (range
          157,002 to 235,504 patients/year). External validity: implied national STEMI count
          (248,269/yr) sits inside the AHA Heart Disease and Stroke Statistics 2024 published
          range of 250,000–280,000/yr without calibration; the drive-time engine reproduces
          published 30-, 60-, and 90-minute PCI-access estimates to within 1 percentage point.
        </p>
      </section>

      <section>
        <h2>Primary datasets</h2>
        <p>Each dataset, what we extract from it, and the calculation step or downstream metric those fields produce.</p>
        <div className="table-wrap">
          <table className="data-table">
            <thead>
              <tr>
                <th>#</th>
                <th>Dataset</th>
                <th>Vintage</th>
                <th>What we extract</th>
                <th>What it produces</th>
              </tr>
            </thead>
            <tbody>
              {PRIMARY.map((d) => (
                <tr key={d.n}>
                  <td className="cell-num">{d.n}</td>
                  <td className="cell-name"><strong>{d.name}</strong></td>
                  <td className="cell-vintage">{d.vintage}</td>
                  <td>
                    <ul>{d.extract.map((x, i) => <li key={i}>{x}</li>)}</ul>
                  </td>
                  <td>
                    <ul>{d.produces.map((x, i) => <li key={i}>{x}</li>)}</ul>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>

      <section>
        <h2>Published references used as constants or validity anchors</h2>
        <div className="table-wrap">
          <table className="data-table">
            <thead>
              <tr>
                <th>#</th>
                <th>Reference</th>
                <th>Year</th>
                <th>What we use</th>
                <th>What it produces</th>
              </tr>
            </thead>
            <tbody>
              {REFERENCES.map((d) => (
                <tr key={d.n}>
                  <td className="cell-num">{d.n}</td>
                  <td className="cell-name"><strong>{d.name}</strong></td>
                  <td className="cell-vintage">{d.vintage}</td>
                  <td>
                    <ul>{d.extract.map((x, i) => <li key={i}>{x}</li>)}</ul>
                  </td>
                  <td>
                    <ul>{d.produces.map((x, i) => <li key={i}>{x}</li>)}</ul>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>

      <section>
        <h2>Derived analytic artifacts</h2>
        <p>Not external datasets but the canonical intermediates the analysis relies on.</p>
        <div className="table-wrap">
          <table className="data-table">
            <thead>
              <tr>
                <th>Artifact</th>
                <th>Built from</th>
                <th>Purpose</th>
              </tr>
            </thead>
            <tbody>
              {DERIVED.map((d, i) => (
                <tr key={i}>
                  <td className="cell-name"><code>{d.artifact}</code></td>
                  <td>{d.builtFrom}</td>
                  <td>{d.purpose}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>

      <section className="about-footer">
        <p>
          SHA256 checksums, exact column-level field references, and per-source download URLs are documented in{" "}
          <a href="https://github.com/rgaiba/stemi-fmc-to-device/blob/main/national/data/MANIFEST.md" target="_blank" rel="noreferrer">
            <code>national/data/MANIFEST.md</code>
          </a>. The methodological audit trail (decisions D1–D12 and Amendments 2026-05-07-A through 2026-05-08-E) lives in{" "}
          <a href="https://github.com/rgaiba/stemi-fmc-to-device/blob/main/national/notes/pre_registration.md" target="_blank" rel="noreferrer">
            <code>national/notes/pre_registration.md</code>
          </a>. The external validity record is at{" "}
          <a href="https://github.com/rgaiba/stemi-fmc-to-device/blob/main/national/notes/external_validity.md" target="_blank" rel="noreferrer">
            <code>national/notes/external_validity.md</code>
          </a>.
        </p>
      </section>
    </article>
  );
}

// Inline NavLink for use inside prose. (Direct import would cause a circular
// dependency in some setups; a local re-import is fine.)
function NavLinkInline({ path, label }) {
  return (
    <a
      href={`#${path}`}
      onClick={(e) => {
        e.preventDefault();
        window.location.hash = path;
      }}
      style={{ color: "inherit", textDecoration: "underline" }}
    >
      {label}
    </a>
  );
}
