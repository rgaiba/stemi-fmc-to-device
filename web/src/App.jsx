import React from "react";
import { HashRouter, Routes, Route } from "react-router-dom";
import NavBar from "./components/NavBar.jsx";
import MapPage from "./pages/MapPage.jsx";
import StrataPage from "./pages/StrataPage.jsx";
import StatesPage from "./pages/StatesPage.jsx";
import AboutPage from "./pages/AboutPage.jsx";

// HashRouter (vs BrowserRouter) keeps client-side routing working on
// GitHub Pages without any 404.html fallback gymnastics. URLs look like
// rgaiba.github.io/stemi-fmc-to-device/#/about ; slightly less elegant
// than path-based routes but bulletproof on static hosts.
export default function App() {
  return (
    <HashRouter>
      <div className="page">
        <NavBar />
        <Routes>
          <Route path="/" element={<MapPage />} />
          <Route path="/strata" element={<StrataPage />} />
          <Route path="/states" element={<StatesPage />} />
          <Route path="/about" element={<AboutPage />} />
        </Routes>
      </div>
    </HashRouter>
  );
}
