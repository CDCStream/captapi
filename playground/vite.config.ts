import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// Dev-only console. Both targets go through the Vite proxy so the browser never
// hits the API origin directly (prod CORS only whitelists localhost:3000).
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5273,
    proxy: {
      "/local-api": {
        target: "http://localhost:8000",
        changeOrigin: true,
        rewrite: (p) => p.replace(/^\/local-api/, ""),
      },
      "/prod-api": {
        target: "https://api.captapi.com",
        changeOrigin: true,
        rewrite: (p) => p.replace(/^\/prod-api/, ""),
      },
    },
  },
});
