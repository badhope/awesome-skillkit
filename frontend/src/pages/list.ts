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
// from a stable category→hue map (CATEGORY_COLORS). Keeping the map
// in JS — not CSS — means we don't have to maintain N parallel
// .chip--<cat> rules and the colors are visible from one place.

import type { SkillIndex, SkillIndexEntry } from "../types";

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
const CATEGORY_LABELS: Record<string, string> = {
  "applications": "Applications",
  "browser-automation": "Browser automation",
  "code-assistants": "Code assistants",
  "data-pipelines": "Data pipelines",
  "dev-tools": "Developer tools",
  "documentation": "Documentation",
  "embeddings": "Embeddings",
  "evaluation": "Evaluation",
  "guardrails": "Guardrails & safety",
  "mcp-protocol": "MCP protocol",
  "observability": "Observability",
  "official-cookbooks": "Official cookbooks",
  "safety-alignment": "Safety & alignment",
  "terminal-cli": "Terminal & CLI",
  "text-to-sql": "Text-to-SQL",
};
function categoryLabel(cat: string): string {
  return CATEGORY_LABELS[cat] ?? cat.replace(/-/g, " ").replace(/\b\w/g, c => c.toUpperCase());
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
        <span>vendor-neutral skill vault</span>
        <span aria-hidden="true">·</span>
        <span>v1.0.0</span>
      </div>
      <h1 class="hero__title">
        ${totalSkills} <em>SKILL.md</em><br/>
        files, ready to drop in.
      </h1>
      <p class="hero__sub">
        Markdown prompts for Claude, Codex, Cursor, Continue — and any
        agent that reads a folder. Sourced from deepeval, promptfoo,
        langfuse, OpenAI, Anthropic, Hugging Face, Letta, and a
        handful of hand-written ones. No tracking. No signup.
      </p>
      <div class="hero__cta">
        <a class="btn btn--primary" href="#/bundle" data-link>Pick a bundle →</a>
        <a class="btn" href="https://github.com/badhope/AI-SKILL" rel="noopener noreferrer" target="_blank">View on GitHub</a>
      </div>
      <div class="hero__mark-glyph" aria-hidden="true">▮ AI-SKILL</div>
    </section>

    <div class="stats" aria-label="vault statistics">
      <a class="stat" href="#/" data-link aria-label="Total skills">
        <span class="stat__num">${totalSkills}<em>files</em></span>
        <span class="stat__label">SKILL.md</span>
      </a>
      <a class="stat" href="#/" data-link aria-label="Categories">
        <span class="stat__num">${totalCategories}<em>groups</em></span>
        <span class="stat__label">Categories</span>
      </a>
      <a class="stat" href="#/" data-link aria-label="Vendor-neutral skills">
        <span class="stat__num">${vendorNeutral}<em>of ${totalSkills}</em></span>
        <span class="stat__label">Vendor-neutral</span>
      </a>
      <a class="stat" href="#/" data-link aria-label="To review">
        <span class="stat__num">${toReview}<em>flagged</em></span>
        <span class="stat__label">Needs review</span>
      </a>
    </div>

    <div class="container-wide">
      <div class="filter-bar">
        <input type="search" id="filter-q" placeholder="Search by name, slug, tag, description…" value="${escAttr(initialQ)}" />
        <select id="filter-cat" aria-label="Category">
          <option value="">All categories</option>
        </select>
        <select id="filter-plat" aria-label="Platform">
          <option value="">All platforms</option>
          <option value="all">Any (vendor-neutral)</option>
          <option value="claude">Claude</option>
          <option value="codex">Codex</option>
          <option value="cursor">Cursor</option>
          <option value="continue">Continue</option>
        </select>
        <label class="group-toggle" title="Group cards by category">
          <input type="checkbox" id="filter-group" ${initialGroup === "1" ? "checked" : ""} />
          <span>group</span>
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
      cards.innerHTML = `<div class="empty">No skills match. Try a different search or clear filters.</div>`;
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
            <span class="cat-group__count">${list.length} ${list.length === 1 ? "skill" : "skills"}</span>
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
    const blob = `${s.slug} ${s.name} ${s.tags.join(" ")} ${s.category} ${s.description}`.toLowerCase();
    if (!blob.includes(q)) return false;
  }
  return true;
}

function cardHtml(s: SkillIndexEntry, i: number): string {
  const platChips = s.platforms.length === 0
    ? `<span class="chip chip--all" title="Vendor-neutral — works on any agent">any</span>`
    : s.platforms.map(p => `<span class="chip chip--${escAttr(p)}" title="${escAttr(p)}">${escAttr(p)}</span>`).join(" ");
  // The --i custom property drives the stagger animation defined
  // in style.css. Inline style is the only way to set a custom
  // property from a string template without a CSS per-card rule.
  return `
    <a class="skill-card" style="--cat-color: ${escAttr(categoryColor(s.category))}; --i: ${i % 16};" href="#/skill/${escAttr(s.slug)}" data-link>
      <div class="skill-card__head">
        <span class="skill-card__slug">${escHtml(s.slug)}${s.needs_review ? ` <span class="skill-card__review-dot" title="needs_review" aria-label="needs review"></span>` : ""}</span>
        <span class="skill-card__name">${escHtml(s.name)}</span>
      </div>
      <p class="skill-card__desc">${escHtml(s.description)}</p>
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
