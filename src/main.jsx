import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import { HashRouter, Routes, Route, Navigate } from 'react-router-dom';
import App from './App.jsx';
import HospitalAccessPage from './pages/HospitalAccessPage.jsx';
import AmbulancePostsPage from './pages/AmbulancePostsPage.jsx';

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <HashRouter>
      <Routes>
        <Route path="/" element={<App />}>
          <Route index element={<Navigate to="/access" replace />} />
          <Route path="access" element={<HospitalAccessPage />} />
          <Route path="posts" element={<AmbulancePostsPage />} />
        </Route>
      </Routes>
    </HashRouter>
  </StrictMode>
);
