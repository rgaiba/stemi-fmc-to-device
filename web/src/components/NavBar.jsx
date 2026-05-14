import React from "react";
import { NavLink } from "react-router-dom";

export default function NavBar() {
  return (
    <nav className="navbar" aria-label="Primary">
      <NavLink to="/" end className={({ isActive }) => "nav-link" + (isActive ? " active" : "")}>
        Map
      </NavLink>
      <NavLink to="/strata" className={({ isActive }) => "nav-link" + (isActive ? " active" : "")}>
        Strata
      </NavLink>
      <NavLink to="/about" className={({ isActive }) => "nav-link" + (isActive ? " active" : "")}>
        About
      </NavLink>
    </nav>
  );
}
