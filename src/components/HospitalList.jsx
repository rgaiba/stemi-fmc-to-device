function HospitalIcon({ color }) {
  return (
    <svg width="14" height="14" viewBox="0 0 14 14" style={{ flexShrink: 0 }}>
      <circle cx="7" cy="7" r="6" fill="#ffffff" stroke={color} strokeWidth="1.3" />
      <rect x="3.5" y="6.3" width="7" height="1.4" fill={color} />
      <rect x="6.3" y="3.5" width="1.4" height="7" fill={color} />
    </svg>
  );
}

export default function HospitalList({ label, hospitals }) {
  return (
    <>
      <div className="panel-lbl">{label}</div>
      <div>
        {hospitals.map((h) => {
          const strokeColor = h.highlight ? '#b8860b' : '#1a1e2e';
          const nameStyle = h.highlight ? { color: '#b8860b' } : undefined;
          const tagClass = h.state === 'DE' ? 'tag-de' : 'tag-md';
          return (
            <div className="hosp-row" key={h.short}>
              <HospitalIcon color={strokeColor} />
              <div style={{ flex: 1, minWidth: 0 }}>
                <div className="hosp-name" style={nameStyle}>
                  {h.short}
                </div>
                <div className="hosp-city">{h.city.toUpperCase()}</div>
              </div>
              <div className={`state-tag ${tagClass}`}>{h.state}</div>
            </div>
          );
        })}
      </div>
    </>
  );
}
