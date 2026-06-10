// List page: searchable + filterable grid of skill cards.

import type { SkillIndex, SkillIndexEntry } from "../types";

export async function renderList(
  root: HTMLElement,
  index: SkillIndex,
): Promise<void> {
  // Initial filter state from URL
  const url = new URL(window.location.href);
  const initialQ = url.searchParams.get("q") ?? "";
  const initialCat = url.searchParams.get("category") ?? "";
  const initialPlat = url.searchParams.get("platform") ?? "";

  root.innerHTML = `
    <div class="container-wide">
      <p class="meta-line">
        <span><strong>${index.skills.length}</strong> skills</span>
        <span>·</span>
        <span><strong>${new Set(index.skills.map(s => s.category)).size}</strong> categories</span>
        <span>·</span>
        <span><strong>${index.skills.filter(s => s.needs_review).length}</strong> to review</span>
      </p>
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
      </div>
      <div id="cards"></div>
    </div>
  `;

  // Populate the category dropdown
  const catSel = root.querySelector<HTMLSelectElement>("#filter-cat")!;
  const cats = Array.from(new Set(index.skills.map(s => s.category))).sort();
  for (const c of cats) {
    const o = document.createElement("option");
    o.value = c; o.textContent = c;
    if (c === initialCat) o.selected = true;
    catSel.appendChild(o);
  }
  const platSel = root.querySelector<HTMLSelectElement>("#filter-plat")!;
  platSel.value = initialPlat;

  const qInput = root.querySelector<HTMLInputElement>("#filter-q")!;
  const cards = root.querySelector<HTMLDivElement>("#cards")!;

  function paint() {
    const q = qInput.value.trim().toLowerCase();
    const cat = catSel.value;
    const plat = platSel.value;
    const filtered = index.skills.filter(s => match(s, q, cat, plat));
    // Update URL (no reload) so links share state
    const u = new URL(window.location.href);
    u.searchParams.set("q", q);
    u.searchParams.set("category", cat);
    u.searchParams.set("platform", plat);
    history.replaceState(null, "", u.toString());

    if (filtered.length === 0) {
      cards.innerHTML = `<div class="empty">No skills match. Try a different search or clear filters.</div>`;
      return;
    }
    cards.innerHTML = filtered.map((s, i) => cardHtml(s, i % 2 === 0)).join("");
  }

  qInput.addEventListener("input", debounce(paint, 80));
  catSel.addEventListener("change", paint);
  platSel.addEventListener("change", paint);

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

function cardHtml(s: SkillIndexEntry, even: boolean): string {
  const platChips = s.platforms.length === 0
    ? `<span class="chip chip--all" title="Vendor-neutral — works on any agent">any</span>`
    : s.platforms.map(p => `<span class="chip chip--${escAttr(p)}" title="${escAttr(p)}">${escAttr(p)}</span>`).join(" ");
  return `
    <a class="skill-card ${even ? "" : "skill-card--alt"}" href="#/skill/${escAttr(s.slug)}" data-link>
      <div class="skill-card__head">
        <span class="skill-card__slug">${escHtml(s.slug)}${s.needs_review ? ` <span class="skill-card__review-dot" title="needs_review" aria-label="needs review"></span>` : ""}</span>
        <span class="skill-card__name">${escHtml(s.name)}</span>
      </div>
      <p class="skill-card__desc">${escHtml(s.description)}</p>
      <div class="skill-card__meta">
        <span>${escHtml(s.category)}</span>
        ${platChips}
        <span>${s.tags.map(escHtml).join(" · ")}</span>
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
