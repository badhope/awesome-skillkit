// Tiny custom router. Three routes only:
//   #/         → list
//   #/skill/:slug → detail
//   #/bundle   → bundle picker
// We use hash routing because GitHub Pages serves a static
// site; clean URLs would need server rewrites.

import { renderList } from "./pages/list";
import { renderDetail } from "./pages/detail";
import { renderBundle } from "./pages/bundle";
import type { Skill, SkillIndex } from "./types";

const main = () => document.querySelector<HTMLElement>("#main")!;
let cachedIndex: SkillIndex | null = null;
let skillCache = new Map<string, Skill>();

async function loadIndex(): Promise<SkillIndex> {
  if (cachedIndex) return cachedIndex;
  // Bust cache during dev. Vite hashes the asset at build time
  // so prod gets the right behaviour automatically.
  const r = await fetch(`${import.meta.env.BASE_URL}skills.json`);
  if (!r.ok) throw new Error(`fetch skills.json: ${r.status}`);
  cachedIndex = (await r.json()) as SkillIndex;
  return cachedIndex;
}

async function loadSkill(slug: string): Promise<Skill | null> {
  if (skillCache.has(slug)) return skillCache.get(slug)!;
  // Build pipeline writes one .json per skill, named by slug.
  // encodeURIComponent keeps the path safe if SLUG_RE is ever
  // relaxed. (S6 from the prosecutor review.)
  const r = await fetch(`${import.meta.env.BASE_URL}skills/${encodeURIComponent(slug)}.json`);
  if (!r.ok) return null;
  const s = (await r.json()) as Skill;
  skillCache.set(slug, s);
  return s;
}

async function route() {
  const hash = window.location.hash || "#/";
  const mainEl = main();
  // Only show the Loading placeholder on a cold load — when the
  // index is already cached, this would flash for a single
  // microtask. (S2)
  if (cachedIndex === null) {
    mainEl.innerHTML = `<div class="empty" role="status" aria-live="polite">Loading…</div>`;
  }
  try {
    const idx = await loadIndex();
    if (hash === "#/" || hash === "#") {
      document.title = "AI-SKILL";
      await renderList(mainEl, idx);
    } else if (hash === "#/bundle") {
      document.title = "Bundle — AI-SKILL";
      await renderBundle(mainEl, idx);
    } else if (hash.startsWith("#/skill/")) {
      const slug = decodeURIComponent(hash.slice("#/skill/".length));
      const skill = await loadSkill(slug);
      if (skill) {
        document.title = `${skill.name} — AI-SKILL`;
        await renderDetail(mainEl, skill);
      } else {
        document.title = "Not found — AI-SKILL";
        mainEl.innerHTML = `<div class="empty">Skill <code>${escapeHtml(slug)}</code> not found. <a href="#/" data-link>Back to list</a>.</div>`;
      }
    } else {
      document.title = "AI-SKILL";
      mainEl.innerHTML = `<div class="empty">Unknown route. <a href="#/" data-link>Back to list</a>.</div>`;
    }
    // Scroll to top on route change (unless the user is mid-click)
    window.scrollTo({ top: 0, behavior: "instant" as ScrollBehavior });
  } catch (e) {
    document.title = "Error — AI-SKILL";
    mainEl.innerHTML = `<div class="empty">Failed to load: ${escapeHtml(String(e))}</div>`;
    console.error(e);
  }
}

function escapeHtml(s: string): string {
  return s.replace(/[&<>"']/g, c => ({
    "&": "&amp;", "<": "&lt;", ">": "&gt;",
    '"': "&quot;", "'": "&#39;",
  }[c]!));
}

// (S1: removed the dead global click handler — the browser's
// default hash navigation + the hashchange listener already do
// the right thing.)

window.addEventListener("hashchange", route);
route();
