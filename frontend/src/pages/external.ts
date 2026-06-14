// External-repos page: a curated directory of upstream
// repositories that publish SKILL.md files. Each card is a link
// the user can click to jump to the source repo — we don't try
// to mirror everything, just point to where the rest of the
// world keeps their skills.
//
// Data lives in frontend/public/external-repos.json and is
// loaded lazily on first navigation. Build pipeline keeps it
// up to date as contributors add entries.
//
// Layout:
//   .external-hero        — short title + intro
//   .external-list        — one card per repo
//   .external-card        — vendor / repo / category / description / link
//
// The cards group loosely by vendor (Anthropic, OpenAI, …) but
// the visual divider is just CSS — no separate section wrapper
// needed, since vendors are listed in order and the eye picks
// them up.

import { t, getLocale } from "../i18n";
import { escHtml, escAttr } from "../shared";

interface ExternalRepo {
  vendor: string;
  repo: string;
  url: string;
  ref: string;
  license: string;
  skill_count_hint?: string;
  category: string;
  description_en: string;
  description_zh: string;
  tags: string[];
}

let cache: ExternalRepo[] | null = null;

async function loadRepos(): Promise<ExternalRepo[]> {
  if (cache) return cache;
  // The JSON sits in public/ so vite copies it as a static asset
  // and we fetch it with a relative URL at runtime.
  const r = await fetch(`${import.meta.env.BASE_URL}external-repos.json`);
  if (!r.ok) throw new Error(`fetch external-repos.json: ${r.status}`);
  const data = await r.json();
  cache = (data.repos ?? []) as ExternalRepo[];
  return cache;
}

export async function renderExternal(root: HTMLElement): Promise<void> {
  // Set the doc title early so the tab shows the right text
  // before the cards finish rendering.
  document.title = `${t("external.title")} — AI-SKILL`;
  root.innerHTML = `
    <div class="container-wide">
      <h1 class="external__title">${escHtml(t("external.title"))}</h1>
      <p class="external__subtitle">${escHtml(t("external.subtitle"))}</p>
      <div id="external-list" class="external-list" aria-busy="true">
        <div class="empty" role="status" aria-live="polite">${escHtml(t("loading"))}</div>
      </div>
      <p class="external__hint">${escHtml(t("external.hint"))}</p>
    </div>
  `;
  const list = root.querySelector<HTMLDivElement>("#external-list")!;
  try {
    const repos = await loadRepos();
    list.removeAttribute("aria-busy");
    if (repos.length === 0) {
      list.innerHTML = `<div class="empty">${escHtml(t("external.empty"))}</div>`;
      return;
    }
    const zh = getLocale() === "zh";
    list.innerHTML = repos.map(r => cardHtml(r, zh)).join("");
  } catch (e) {
    list.removeAttribute("aria-busy");
    list.innerHTML = `<div class="empty" role="alert">${escHtml(t("external.errorLoad"))} <code>${escHtml(String(e))}</code></div>`;
    // Production: suppress detailed error logs to prevent information leakage
    if (import.meta.env.DEV) {
      console.error(e);
    }
  }
}

function cardHtml(r: ExternalRepo, zh: boolean): string {
  // The description is bilingual in the JSON; pick the right
  // variant and fall back to the other one if the requested
  // locale is missing (defensive — both should always exist).
  const desc = zh
    ? (r.description_zh || r.description_en)
    : r.description_en;
  // Build a stable inline accent from the vendor name so the
  // user can scan the list visually and find the same vendor
  // twice. Saturated, locked L, varied H.
  const hue = stableHue(r.vendor);
  const tags = r.tags.slice(0, 4).map(tg =>
    `<span class="external-card__tag">#${escHtml(tg)}</span>`
  ).join("");
  return `
    <article class="external-card" style="--vendor-hue: ${hue};">
      <header class="external-card__head">
        <div class="external-card__vendor-row">
          <span class="external-card__vendor">${escHtml(r.vendor)}</span>
          <span class="external-card__repo">${escHtml(r.repo)}</span>
        </div>
        <a class="external-card__link" href="${escAttr(r.url)}" rel="noopener noreferrer" target="_blank">
          ${escHtml(t("external.visit"))} ↗
        </a>
      </header>
      <p class="external-card__desc">${escHtml(desc)}</p>
      <dl class="external-card__meta">
        <div><dt>${escHtml(t("external.category"))}</dt><dd>${escHtml(r.category)}</dd></div>
        <div><dt>${escHtml(t("external.skills"))}</dt><dd>${escHtml(r.skill_count_hint ?? "—")}</dd></div>
        <div><dt>${escHtml(t("external.license"))}</dt><dd>${escHtml(r.license)}</dd></div>
        <div><dt>${escHtml(t("external.ref"))}</dt><dd><code>${escHtml(r.ref)}</code></dd></div>
      </dl>
      <div class="external-card__tags">${tags}</div>
    </article>
  `;
}

function stableHue(s: string): number {
  // Same family as list.ts's categoryHue — a 32-bit string hash
  // mapped into 0..359. Locked L/S so the chips feel consistent
  // across vendors.
  let h = 0;
  for (let i = 0; i < s.length; i++) h = (h * 31 + s.charCodeAt(i)) >>> 0;
  return h % 360;
}
