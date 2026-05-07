import { rampColor } from '../lib/geometry.js';

export default function Legend() {
  const stops = [0, 0.25, 0.5, 0.75, 1].map((t) => rampColor(t));
  const gradient = `linear-gradient(90deg, ${stops.join(',')})`;

  return (
    <div>
      <div className="panel-lbl">Drive Time to Nearest PCI Center</div>
      <div className="legend-bar" style={{ background: gradient }} />
      <div className="legend-ticks">
        <span>0</span>
        <span>9</span>
        <span>18</span>
        <span>26</span>
        <span>35+ min</span>
      </div>
      <div className="legend-note">
        DOT SIZE = BLOCK GROUP POPULATION (2020 CENSUS)
        <br />
        COLOR = STRAIGHT-LINE × 1.35 DETOUR · 45 MPH AVG
        <br />
        ESTIMATES ONLY — NOT ACTUAL EMS RESPONSE TIMES
      </div>
    </div>
  );
}
