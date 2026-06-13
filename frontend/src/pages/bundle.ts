// Bundle page: pick a subset of skills, download as one zip.
// v1 implementation: we already have the full Skill JSON
// cached for any skill the user has visited. For unvisited
// skills we fetch the .json on demand. The zip is built
// entirely client-side via JSZip — no backend.

import JSZip from "jszip";
import type { Skill, SkillIndex } from "../types";
import { t } from "../i18n";
import { categoryLabel, escHtml, escAttr, dumpFrontmatter } from "../shared";

export async function renderBundle(
  root: HTMLElement,
  index: SkillIndex,
): Promise<void> {
  root.innerHTML = `
    <div class="container-wide">
      <h2 class="bundle__title">${escHtml(t("bundle.title"))}</h2>
      <p class="meta-line">
        <span>${escHtml(t("bundle.intro"))}</span>
      </p>
      <div class="filter-bar">
        <input type="search" id="b-q" placeholder="${escAttr(t("bundle.filter.ph"))}" />
      </div>
      <ul class="bundle-list" id="b-list"></ul>
      <div class="actions" style="display: flex; gap: var(--s-2); align-items: center; flex-wrap: wrap;">
        <button class="btn" id="b-select-all" type="button">${escHtml(t("bundle.selectAll"))}</button>
        <button class="btn" id="b-clear" type="button">${escHtml(t("bundle.clear"))}</button>
        <span class="meta-line" style="margin: 0;">
          <span>${escHtml(t("bundle.selected"))} <strong id="b-count">0</strong></span>
        </span>
        <button class="btn btn--primary" id="b-download" type="button" disabled>${escHtml(t("bundle.download"))}</button>
      </div>
    </div>
  `;

  const listEl = root.querySelector<HTMLUListElement>("#b-list")!;
  const qInput = root.querySelector<HTMLInputElement>("#b-q")!;
  const countEl = root.querySelector<HTMLElement>("#b-count")!;
  const dlBtn = root.querySelector<HTMLButtonElement>("#b-download")!;
  const selAllBtn = root.querySelector<HTMLButtonElement>("#b-select-all")!;
  const clearBtn = root.querySelector<HTMLButtonElement>("#b-clear")!;

  // Build a checkbox list, preserving filter + checked state
  function paint() {
    const q = qInput.value.trim().toLowerCase();
    const filtered = index.skills.filter(s => {
      if (!q) return true;
      const blob = `${s.slug} ${s.name} ${s.name_zh ?? ""} ${s.description} ${s.description_zh ?? ""} ${s.category} ${(s.tags ?? []).join(" ")}`.toLowerCase();
      return blob.includes(q);
    });
    // Snapshot which slugs are checked before re-rendering, so a
    // filter that hides then re-shows a row doesn't drop the
    // selection. (W4 from the prosecutor review.)
    const stillChecked = new Set(
      Array.from(
        listEl.querySelectorAll<HTMLInputElement>("input[type=checkbox]:checked"),
      ).map(c => c.dataset.slug!),
    );
    listEl.innerHTML = filtered.map(s => `
      <li>
        <input type="checkbox" data-slug="${escAttr(s.slug)}" id="chk-${escAttr(s.slug)}"${stillChecked.has(s.slug) ? " checked" : ""} />
        <label for="chk-${escAttr(s.slug)}" class="bundle-list__slug">${escHtml(s.slug)}</label>
        <span class="bundle-list__cat">${escHtml(categoryLabel(s.category))}</span>
        ${s.needs_review ? `<span class="skill-card__review-dot" title="${escAttr(t("reviewDot.title"))}"></span>` : ""}
      </li>
    `).join("");
  }
  // Bind the change listener once on listEl — re-binding inside
  // paint() was leaking a handler per keystroke. (B1)
  listEl.addEventListener("change", () => updateCount());

  function updateCount() {
    const n = listEl.querySelectorAll<HTMLInputElement>("input[type=checkbox]:checked").length;
    countEl.textContent = String(n);
    dlBtn.toggleAttribute("disabled", n === 0);
  }

  qInput.addEventListener("input", () => paint());
  selAllBtn.addEventListener("click", () => {
    listEl.querySelectorAll<HTMLInputElement>("input[type=checkbox]").forEach(c => { c.checked = true; });
    updateCount();
  });
  clearBtn.addEventListener("click", () => {
    listEl.querySelectorAll<HTMLInputElement>("input[type=checkbox]").forEach(c => { c.checked = false; });
    updateCount();
  });
  dlBtn.addEventListener("click", async () => {
    const slugs = Array.from(listEl.querySelectorAll<HTMLInputElement>("input[type=checkbox]:checked"))
      .map(c => c.dataset.slug!)
      .filter(Boolean);
    if (slugs.length === 0) return;
    const buildingLabel = t("bundle.building");
    const downloadLabel = t("bundle.download");
    dlBtn.textContent = buildingLabel;
    dlBtn.setAttribute("disabled", "true");
    try {
      const zip = new JSZip();
      for (const slug of slugs) {
        // encodeURIComponent for the same reason as main.ts: keep
        // the path safe if SLUG_RE is ever relaxed. (S6)
        const r = await fetch(`${import.meta.env.BASE_URL}skills/${encodeURIComponent(slug)}.json`);
        if (!r.ok) throw new Error(`fetch ${slug}: ${r.status}`);
        const s = (await r.json()) as Skill;
        zip.file(`${slug}/SKILL.md`, reEmit(s));
      }
      const blob = await zip.generateAsync({ type: "blob" });
      const stamp = new Date().toISOString().slice(0, 10).replace(/-/g, "");
      const a = document.createElement("a");
      a.href = URL.createObjectURL(blob);
      a.download = `ai-skill-${slugs.length}-${stamp}.zip`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      setTimeout(() => URL.revokeObjectURL(a.href), 1000);
    } catch (e) {
      // Render the error inline instead of using alert(); the
      // page already has the .empty shape, and alert() is blocked
      // in some embedded contexts. (W8)
      listEl.insertAdjacentHTML(
        "beforebegin",
        `<div class="empty" role="alert" style="color: var(--err);">${escHtml(t("bundle.failed", { msg: e instanceof Error ? e.message : String(e) }))}</div>`,
      );
    } finally {
      dlBtn.textContent = downloadLabel;
      dlBtn.removeAttribute("disabled");
    }
  });

  paint();
  updateCount();
}

function reEmit(s: Skill): string {
  // Prefer the original vendored text. If a per-skill JSON was
  // produced without the rawMarkdown field, fall back to a
  // synthesized frontmatter + body so the bundle still works.
  if (s.rawMarkdown && s.rawMarkdown.length > 0) return s.rawMarkdown;
  return dumpFrontmatter(s) + "\n\n" + s.body;
}
