// List page: searchable + filterable grid of skill cards.
//
// Layout:
//   .hero          — large display title + sub + CTAs (rendered once
//                    when the page mounts; survives filter changes).
//   .stats         — three big numbers: total / categories / to-review.
//   .filter-bar    — search + category + platform selects.
//   .cat-group     — one block per category with grouped cards.
//
// The category color bar on each card is `--cat-color`, set inline
// from a stable category→hue map. Keeping the map in JS — not CSS
// — means we don't have to maintain N parallel .chip--<cat> rules
// and the colors are visible from one place.
//
// i18n: the page reads its strings via t() and shows the localized
// name/description from each SkillIndexEntry when the current
// locale is Chinese and the zh fields are present.

import type { SkillIndex, SkillIndexEntry } from "../types";
import { t, pickZh, pickPlatform, getLocale } from "../i18n";

// Stable hash → hue. Categories are short labels, so a tiny string
// hash is fine. We lock saturation/lightness so the bars feel like
// one family.
function categoryHue(cat: string): number {
  let h = 0;
  for (let i = 0; i < cat.length; i++) h = (h * 31 + cat.charCodeAt(i)) >>> 0;
  return h % 360;
}
function categoryColor(cat: string): string {
  return `hsl(${categoryHue(cat)} 60% 52%)`;
}

// Friendly display labels for the few categories whose raw slug
// would be confusing in a heading. Anything not in the map falls
// through to the slug, title-cased.
const CATEGORY_LABELS: Record<string, { en: string; zh: string }> = {
  "applications":        { en: "Applications",        zh: "应用" },
  "browser-automation":  { en: "Browser automation",  zh: "浏览器自动化" },
  "code-assistants":     { en: "Code assistants",     zh: "代码助手" },
  "data-pipelines":      { en: "Data pipelines",      zh: "数据流水线" },
  "dev-tools":           { en: "Developer tools",     zh: "开发工具" },
  "documentation":       { en: "Documentation",       zh: "文档" },
  "embeddings":          { en: "Embeddings",          zh: "向量嵌入" },
  "evaluation":          { en: "Evaluation",          zh: "评估" },
  "guardrails":          { en: "Guardrails & safety", zh: "护栏与安全" },
  "mcp-protocol":        { en: "MCP protocol",        zh: "MCP 协议" },
  "observability":       { en: "Observability",       zh: "可观测性" },
  "official-cookbooks":  { en: "Official cookbooks",  zh: "官方 Cookbook" },
  "safety-alignment":    { en: "Safety & alignment",  zh: "安全与对齐" },
  "terminal-cli":        { en: "Terminal & CLI",      zh: "终端与 CLI" },
  "text-to-sql":         { en: "Text-to-SQL",         zh: "Text-to-SQL" },
};
function categoryLabel(cat: string): string {
  const m = CATEGORY_LABELS[cat];
  if (m) return getLocale() === "zh" ? m.zh : m.en;
  return cat.replace(/-/g, " ").replace(/\b\w/g, c => c.toUpperCase());
}

export async function renderList(
  root: HTMLElement,
  index: SkillIndex,
): Promise<void> {
  // Initial filter state from URL
  const url = new URL(window.location.href);
  const initialQ = url.searchParams.get("q") ?? "";
  const initialCat = url.searchParams.get("category") ?? "";
  const initialPlat = url.searchParams.get("platform") ?? "";
  const initialGroup = url.searchParams.get("group") ?? "1";

  const totalSkills = index.skills.length;
  const totalCategories = new Set(index.skills.map(s => s.category)).size;
  const toReview = index.skills.filter(s => s.needs_review).length;
  const vendorNeutral = index.skills.filter(s => s.platforms.length === 0).length;

  root.innerHTML = `
    <section class="hero">
      <div class="hero__eyebrow">
        <span>${escHtml(t("eyebrow.tag"))}</span>
        <span aria-hidden="true">·</span>
        <span>${escHtml(t("eyebrow.version"))}</span>
      </div>
      <h1 class="hero__title">
        ${totalSkills} <em>SKILL.md</em><br/>
        ${escHtml(t("hero.title1"))}
      </h1>
      <p class="hero__sub">${escHtml(t("hero.sub"))}</p>
      <div class="hero__cta">
        <a class="btn btn--primary" href="#/bundle" data-link>${escHtml(t("hero.cta.bundle"))}</a>
        <a class="btn" href="https://github.com/badhope/AI-SKILL" rel="noopener noreferrer" target="_blank">${escHtml(t("hero.cta.gh"))}</a>
      </div>
      <div class="hero__mark-glyph" aria-hidden="true">▮ AI-SKILL</div>
    </section>

    <div class="stats" aria-label="${escAttr(t("aria.vaultStats"))}">
      <div class="stat" aria-label="${escAttr(t("stat.total.label"))}">
        <span class="stat__num">${totalSkills}<em>${escHtml(t("stat.total.suffix"))}</em></span>
        <span class="stat__label">${escHtml(t("stat.total.label"))}</span>
      </div>
      <div class="stat" aria-label="${escAttr(t("stat.categories.label"))}">
        <span class="stat__num">${totalCategories}<em>${escHtml(t("stat.cat.suffix"))}</em></span>
        <span class="stat__label">${escHtml(t("stat.categories.label"))}</span>
      </div>
      <div class="stat" aria-label="${escAttr(t("stat.neutral.label"))}">
        <span class="stat__num">${vendorNeutral}<em>${escHtml(t("stat.neutral.suffix", { n: totalSkills }))}</em></span>
        <span class="stat__label">${escHtml(t("stat.neutral.label"))}</span>
      </div>
      <div class="stat" aria-label="${escAttr(t("stat.review.label"))}">
        <span class="stat__num">${toReview}<em>${escHtml(t("stat.review.suffix"))}</em></span>
        <span class="stat__label">${escHtml(t("stat.review.label"))}</span>
      </div>
    </div>

    <div class="container-wide">
      <div class="filter-bar">
        <input type="search" id="filter-q" placeholder="${escAttr(t("filter.search.ph"))}" value="${escAttr(initialQ)}" />
        <select id="filter-cat" aria-label="${escAttr(t("filter.cat.label"))}">
          <option value="">${escHtml(t("filter.cat.all"))}</option>
        </select>
        <select id="filter-plat" aria-label="${escAttr(t("filter.plat.label"))}">
          <option value="">${escHtml(t("filter.plat.all"))}</option>
          <option value="all">${escHtml(t("filter.plat.any"))}</option>
          <option value="claude">${escHtml(t("filter.plat.claude"))}</option>
          <option value="codex">${escHtml(t("filter.plat.codex"))}</option>
          <option value="cursor">${escHtml(t("filter.plat.cursor"))}</option>
          <option value="continue">${escHtml(t("filter.plat.continue"))}</option>
        </select>
        <label class="group-toggle" title="${escAttr(t("filter.group"))}">
          <input type="checkbox" id="filter-group" ${initialGroup === "1" ? "checked" : ""} />
          <span>${escHtml(t("filter.group"))}</span>
        </label>
      </div>
      <div id="cards"></div>
    </div>
  `;

  // Populate the category dropdown
  const catSel = root.querySelector<HTMLSelectElement>("#filter-cat")!;
  const cats = Array.from(new Set(index.skills.map(s => s.category))).sort();
  for (const c of cats) {
    const o = document.createElement("option");
    o.value = c; o.textContent = categoryLabel(c);
    if (c === initialCat) o.selected = true;
    catSel.appendChild(o);
  }
  const platSel = root.querySelector<HTMLSelectElement>("#filter-plat")!;
  platSel.value = initialPlat;
  const groupCb = root.querySelector<HTMLInputElement>("#filter-group")!;

  const qInput = root.querySelector<HTMLInputElement>("#filter-q")!;
  const cards = root.querySelector<HTMLDivElement>("#cards")!;

  function paint() {
    const q = qInput.value.trim().toLowerCase();
    const cat = catSel.value;
    const plat = platSel.value;
    const grouped = groupCb.checked;
    const filtered = index.skills.filter(s => match(s, q, cat, plat));
    // Update URL (no reload) so links share state
    const u = new URL(window.location.href);
    u.searchParams.set("q", q);
    u.searchParams.set("category", cat);
    u.searchParams.set("platform", plat);
    u.searchParams.set("group", grouped ? "1" : "0");
    history.replaceState(null, "", u.toString());

    if (filtered.length === 0) {
      cards.innerHTML = `<div class="empty">${escHtml(t("empty.noMatch"))}</div>`;
      return;
    }
    if (grouped && !cat) {
      // Group by category, ordered by descending count.
      const byCat = new Map<string, SkillIndexEntry[]>();
      for (const s of filtered) {
        const arr = byCat.get(s.category) ?? [];
        arr.push(s);
        byCat.set(s.category, arr);
      }
      const order = Array.from(byCat.entries()).sort((a, b) => b[1].length - a[1].length);
      let i = 0;
      cards.innerHTML = order.map(([c, list]) => `
        <section class="cat-group">
          <header class="cat-group__head">
            <h2 class="cat-group__title">${escHtml(categoryLabel(c))}</h2>
            <span class="cat-group__count">${escHtml(t(list.length === 1 ? "categoryCount.one" : "categoryCount.other", { n: list.length }))}</span>
          </header>
          <div class="cards">
            ${list.map(s => cardHtml(s, i++)).join("")}
          </div>
        </section>
      `).join("");
    } else {
      let i = 0;
      cards.innerHTML = `<div class="cards">${filtered.map(s => cardHtml(s, i++)).join("")}</div>`;
    }
  }

  qInput.addEventListener("input", debounce(paint, 80));
  catSel.addEventListener("change", paint);
  platSel.addEventListener("change", paint);
  groupCb.addEventListener("change", paint);

  paint();
  qInput.focus();
}

function match(s: SkillIndexEntry, q: string, cat: string, plat: string): boolean {
  if (cat && s.category !== cat) return false;
  if (plat) {
    if (plat === "all") {
      // vendor-neutral: empty platforms OR platforms includes "any"
      if (s.platforms.length > 0) return false;
    } else {
      if (!s.platforms.includes(plat)) return false;
    }
  }
  if (q) {
    // Search the localized blob too — so a Chinese query like
    // "浏览器" still finds browser-ml-in-js via its name_zh.
    const blob = `${s.slug} ${s.name} ${s.name_zh ?? ""} ${s.tags.join(" ")} ${s.category} ${s.description} ${s.description_zh ?? ""}`.toLowerCase();
    if (!blob.includes(q)) return false;
  }
  return true;
}

function cardHtml(s: SkillIndexEntry, i: number): string {
  const platChips = s.platforms.length === 0
    ? `<span class="chip chip--all" title="${escAttr(t("vendorNeutral"))}">${escHtml(t("anyChip"))}</span>`
    : s.platforms.map(p => {
        const label = pickPlatform(p);
        return `<span class="chip chip--${escAttr(p)}" title="${escAttr(t("platform.tip", { p }))}">${escHtml(label)}</span>`;
      }).join(" ");
  // The --i custom property drives the stagger animation defined
  // in style.css. Inline style is the only way to set a custom
  // property from a string template without a CSS per-card rule.
  const name = pickZh(s, "name");
  const desc = pickZh(s, "description");
  return `
    <a class="skill-card" style="--cat-color: ${escAttr(categoryColor(s.category))}; --i: ${i % 16};" href="#/skill/${escAttr(s.slug)}" data-link>
      <div class="skill-card__head">
        <span class="skill-card__slug">${escHtml(s.slug)}${s.needs_review ? ` <span class="skill-card__review-dot" title="${escAttr(t("reviewDot.title"))}" aria-label="${escAttr(t("reviewDot.title"))}"></span>` : ""}</span>
        <span class="skill-card__name">${escHtml(name)}</span>
      </div>
      <p class="skill-card__desc">${escHtml(desc)}</p>
      <div class="skill-card__meta">
        <span>${escHtml(categoryLabel(s.category))}</span>
        ${platChips}
        <span>${s.tags.slice(0, 4).map(escHtml).join(" · ")}</span>
      </div>
    </a>
  `;
}

function debounce<T extends (...a: unknown[]) => void>(fn: T, ms: number): T {
  let h: ReturnType<typeof setTimeout> | null = null;
  return ((...args: unknown[]) => {
    if (h) clearTimeout(h);
    h = setTimeout(() => fn(...args), ms);
  }) as T;
}

function escHtml(s: string): string {
  return s.replace(/[&<>"']/g, c => ({
    "&": "&amp;", "<": "&lt;", ">": "&gt;",
    '"': "&quot;", "'": "&#39;",
  }[c]!));
}
function escAttr(s: string): string {
  return escHtml(s);
}
