import { defineConfig } from "vite";
import { resolve } from "path";

// Minimal Vite config. We:
//  - emit a flat `dist/` (no code-splitting chatter to debug)
//  - ship base = "./" so the site works under
//    https://<user>.github.io/AI-SKILL/  AND
//    http://localhost:5173/  with the same index.html
//  - leave CSS handling to Vite (it inlines small files)
//  - process BOTH index.html and 404.html through Vite so the
//    hashed JS/CSS asset paths are injected. 404.html is the
//    GH Pages deep-link fallback (see public/404.html's
//    redirect script for the full story).
export default defineConfig({
  base: "./",
  build: {
    outDir: "dist",
    target: "es2022",
    cssCodeSplit: false,
    sourcemap: false,
    rollupOptions: {
      input: {
        main: resolve(__dirname, "index.html"),
        // 404.html is the GH Pages deep-link fallback. We
        // list it as a second entry so Vite resolves its
        // own /src/main.ts + /src/style.css references and
        // rewrites them to the hashed asset URLs.
        fallback: resolve(__dirname, "404.html"),
      },
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
