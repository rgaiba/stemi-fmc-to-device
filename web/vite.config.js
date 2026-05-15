import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// Custom domain (stemifast.org) is configured via web/public/CNAME, so
// GitHub Pages serves the site from the root path. Assets resolve from
// "/", not "/stemi-fmc-to-device/" as they did on the rgaiba.github.io
// project URL.
export default defineConfig({
  plugins: [react()],
  base: "/",
  build: {
    outDir: "dist",
    sourcemap: false,
  },
});
