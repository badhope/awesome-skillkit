import { defineConfig } from "vite";
import { resolve } from "path";

// Optimized Vite config:
//  - emit a flat `dist/` with code splitting for better caching
//  - ship base = "./" so the site works under
//    https://<user>.github.io/AI-SKILL/  AND
//    http://localhost:5173/  with the same index.html
//  - enable CSS code splitting for smaller initial bundles
//  - process BOTH index.html and 404.html through Vite so the
//    hashed JS/CSS asset paths are injected. 404.html is the
//    GH Pages deep-link fallback (see public/404.html's
//    redirect script for the full story).
export default defineConfig({
  base: "./",
  build: {
    outDir: "dist",
    target: "es2022",
    cssCodeSplit: true, // Enable CSS code splitting for better caching
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
        // Enable automatic code splitting for better caching
        manualChunks: undefined,
        // Optimize chunk file names for better caching
        chunkFileNames: "assets/[name]-[hash].js",
        entryFileNames: "assets/[name]-[hash].js",
        assetFileNames: "assets/[name]-[hash][extname]",
      },
    },
    // Enable minification for smaller bundles (Vite 8 uses oxc by default)
    minify: true,
    // Inline assets smaller than 4KB
    assetsInlineLimit: 4096,
  },
  server: {
    port: 5173,
    host: "127.0.0.1",
  },
});
