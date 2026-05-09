import { NavLink } from 'react-router-dom';

export default function NavBar() {
  return (
    <nav>
      <div className="nav-logo">PCI Times — Delaware STEMI Access</div>
      <div className="nav-links">
        <NavLink
          to="/access"
          className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}
        >
          Hospital Access
        </NavLink>
        <NavLink
          to="/posts"
          className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}
        >
          Ambulance Posts
        </NavLink>
      </div>
      <div className="nav-meta">CenPop 2020 · Block Group · April 2026</div>
    </nav>
  );
}
