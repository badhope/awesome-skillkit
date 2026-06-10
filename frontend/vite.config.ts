import { defineConfig } from "vite";

// Minimal Vite config. We:
//  - emit a flat `dist/` (no code-splitting chatter to debug)
//  - ship base = "./" so the site works under
//    https://<user>.github.io/AI-SKILL/  AND
//    http://localhost:5173/  with the same index.html
//  - leave CSS handling to Vite (it inlines small files)
export default defineConfig({
  base: "./",
  build: {
    outDir: "dist",
    target: "es2022",
    cssCodeSplit: false,
    sourcemap: false,
    rollupOptions: {
      output: {
        // Single bundle file. Simpler, no surprise chunk fetches.
        manualChunks: undefined,
      },
    },
  },
  server: {
    port: 5173,
    host: "127.0.0.1",
  },
});
