// Tiny custom router. Three routes only:
//   #/         → list
//   #/skill/:slug → detail
//   #/bundle   → bundle picker
// We use hash routing because GitHub Pages serves a static
// site; clean URLs would need server rewrites.

// Lazy-load page components for better code splitting and performance.
// Each page is only loaded when the user navigates to its route.
import type { Skill, SkillIndex } from "./types";
import { applyStaticTranslations, getLocale, setLocale, subscribe, t } from "./i18n";
import { escHtml } from "./shared";

const main = () => document.querySelector<HTMLElement>("#main")!;
let cachedIndex: SkillIndex | null = null;
let skillCache = new Map<string, Skill>();
// Route ID counter to prevent race conditions when the user
// rapidly switches routes. Each route() call increments the
// counter; if the counter changes during an async operation,
// the stale render is aborted.
let routeId = 0;

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
  const thisRouteId = ++routeId;
  const hash = window.location.hash || "#/";
  const mainEl = main();
  // Only show the Loading placeholder on a cold load — when the
  // index is already cached, this would flash for a single
  // microtask. (S2)
  if (cachedIndex === null) {
    mainEl.innerHTML = `<div class="empty" role="status" aria-live="polite">${escHtml(t("loading"))}</div>`;
  }
  try {
    const idx = await loadIndex();
    // Abort if the user navigated away while we were loading
    if (thisRouteId !== routeId) return;
    if (hash === "#/" || hash === "#") {
      document.title = "AI-SKILL";
      const { renderList } = await import("./pages/list");
      await renderList(mainEl, idx);
    } else if (hash === "#/bundle") {
      document.title = `${t("bundle.title")} — AI-SKILL`;
      const { renderBundle } = await import("./pages/bundle");
      await renderBundle(mainEl, idx);
    } else if (hash === "#/external") {
      document.title = `${t("external.title")} — AI-SKILL`;
      const { renderExternal } = await import("./pages/external");
      await renderExternal(mainEl);
    } else if (hash.startsWith("#/skill/")) {
      const slug = decodeURIComponent(hash.slice("#/skill/".length));
      const skill = await loadSkill(slug);
      // Abort if the user navigated away while we were loading
      if (thisRouteId !== routeId) return;
      if (skill) {
        // Use the localized name in the document title so the
        // browser tab also reflects the language choice.
        const titleName = getLocale() === "zh" && skill.name_zh ? skill.name_zh : skill.name;
        document.title = `${titleName} — AI-SKILL`;
        const { renderDetail } = await import("./pages/detail");
        await renderDetail(mainEl, skill, idx);
      } else {
        document.title = `${t("nf.code")} — AI-SKILL`;
        const { renderNotFound } = await import("./pages/detail");
        renderNotFound(mainEl, slug, idx);
      }
    } else {
      document.title = "AI-SKILL";
      mainEl.innerHTML = `<div class="empty">${escHtml(t("unknownRoute"))} <a href="#/" data-link>${escHtml(t("backToList"))}</a>.</div>`;
    }
    // Scroll to top on route change (unless the user is mid-click)
    window.scrollTo({ top: 0, behavior: "instant" as ScrollBehavior });
  } catch (e) {
    document.title = "Error — AI-SKILL";
    mainEl.innerHTML = `<div class="empty">${escHtml(t("errorPrefix"))} ${escHtml(String(e))}</div>`;
    // Production: suppress detailed error logs to prevent information leakage
    // Development: keep console.error for debugging
    if (import.meta.env.DEV) {
      console.error(e);
    }
  }
}

// ============================ i18n wiring ============================
//
// The topbar's lang-toggle is declared in index.html with a
// pair of <span data-lang-opt> children. We sync aria-pressed
// to the current locale and bind a click handler that toggles
// the language. The subscribe() callback re-runs the current
// route — that's how a single toggle re-paints the list, the
// detail, or the bundle page in place.

function syncLangToggle() {
  const cur = getLocale();
  document.querySelectorAll<HTMLElement>("[data-lang-opt]").forEach(el => {
    const opt = el.dataset.langOpt as "en" | "zh" | undefined;
    el.setAttribute("aria-pressed", opt === cur ? "true" : "false");
  });
}

function bindLangToggle() {
  const btn = document.querySelector<HTMLButtonElement>("#lang-toggle");
  if (!btn) return;
  // Each pill inside the button is clickable; clicking either
  // one sets the locale to that language (rather than toggling
  // every time), which is what users expect from a segmented
  // control.
  btn.querySelectorAll<HTMLElement>("[data-lang-opt]").forEach(opt => {
    opt.addEventListener("click", (ev) => {
      ev.stopPropagation();
      const target = (opt as HTMLElement).dataset.langOpt as "en" | "zh" | undefined;
      if (target) setLocale(target);
    });
  });
  syncLangToggle();
}

subscribe(() => {
  applyStaticTranslations();
  syncLangToggle();
  // Re-run the current route. We don't need to clear the skill
  // cache — the data is identical, only the rendering changes.
  route();
});

bindLangToggle();
// Translate the static topbar/footer before the first route
// runs, so the shell is consistent with the page.
applyStaticTranslations();

window.addEventListener("hashchange", route);
route();
