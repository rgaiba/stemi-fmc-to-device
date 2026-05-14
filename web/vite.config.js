import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// GitHub Pages serves the project site at /<repo-name>/ — set base to match
// so all asset URLs resolve correctly on the deployed site.
export default defineConfig({
  plugins: [react()],
  base: "/stemi-fmc-to-device/",
  build: {
    outDir: "dist",
    sourcemap: false,
  },
});
