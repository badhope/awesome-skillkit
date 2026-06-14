// Detail page: render one SKILL.md as HTML.
// - Frontmatter rendered as a small meta block
// - Body: tiny markdown renderer (no library) for the shapes
//   our skills actually use: H1/H2, paragraphs, code fences,
//   tables, ordered/unordered lists, inline code, bold.
// We deliberately don't pull in a markdown library — the
// section set is small, and adding marked.js would blow the
// 50 KB JS budget.
//
// i18n: labels come from t(); the page title (h1), lead
// paragraph, and the bilingual block all swap between the
// English and the Chinese variant based on the current locale.

import type { Skill, SkillIndex, SkillIndexEntry, SkillSource } from "../types";
import { t, getLocale, pickZh, pickPlatform } from "../i18n";
import { categoryLabel, escHtml, escAttr, dumpFrontmatter } from "../shared";

export async function renderDetail(
  root: HTMLElement,
  s: Skill,
  index: SkillIndex,
): Promise<void> {
  // Compute once, used both in the template (to disable the
  // button when the prompt section is missing) and in the click
  // handler below.
  const promptText = extractPromptText(s);
  const related = pickRelated(s, index, 3);
  const titleName = pickZh(s, "name");
  const lead = pickZh(s, "description");
  root.innerHTML = `
    <div class="container-read detail">
      <a class="back-link" href="#/" data-link>${escHtml(t("detail.back"))}</a>
      <h1>${escHtml(titleName)}</h1>
      <p class="meta-row">
        <strong>${escHtml(s.slug)}</strong>
        <span>·</span>
        <span>v${escHtml(s.version)}</span>
        <span>·</span>
        <span>${escHtml(s.license)}</span>
        <span>·</span>
        <span>${escHtml(categoryLabel(s.category))}</span>
        ${platformChips(s.platforms)}
      </p>
      <p class="detail__lead">${escHtml(lead)}</p>
      ${sourceBlock(s)}
      ${zhBlock(s)}
      ${tocBlock(s)}
      <h2 id="when-to-use">${escHtml(t("detail.wtu"))}</h2>
      <div id="wtu-body"></div>
      ${inputsTable(s)}
      ${outputBlock(s)}
      <h2 id="prompt">${escHtml(t("detail.prompt"))}</h2>
      ${promptBlock(s)}
      <div class="actions">
        <button class="btn btn--primary" id="copy-prompt" type="button"${promptText ? "" : " disabled"}>${escHtml(t("detail.copy"))}</button>
        <button class="btn" id="dl-md" type="button">${escHtml(t("detail.download"))}</button>
      </div>
      <h2 id="when-not-to-use">${escHtml(t("detail.wnot"))}</h2>
      <div id="wnot-body"></div>
      <h2 id="example">${escHtml(t("detail.example"))}</h2>
      <div id="example-body"></div>
      ${relatedBlock(related)}
    </div>
  `;
  // Wire actions
  if (promptText) {
    root.querySelector<HTMLButtonElement>("#copy-prompt")!.addEventListener("click", (ev) => {
      copyAndPulse(ev.currentTarget as HTMLButtonElement, promptText, t("detail.copied"));
    });
  }
  root.querySelector<HTMLButtonElement>("#dl-md")!.addEventListener("click", () => downloadSkill(s));
  // Body sections that come AFTER the frontmatter schema.
  // The H1 string we slice on is the canonical English one —
  // the visible label is the localized one above.
  root.querySelector<HTMLDivElement>("#wtu-body")!.innerHTML = renderH1Section(s.body, "When to use");
  root.querySelector<HTMLDivElement>("#wnot-body")!.innerHTML = renderH1Section(s.body, "When NOT to use");
  root.querySelector<HTMLDivElement>("#example-body")!.innerHTML = renderH1Section(s.body, "Example");
  // Attach a copy button to every body code block (the prompt
  // block already has a top-level "Copy prompt" button, so we
  // skip the one inside the prompt H2). N9 from the prosecutor
  // review: body code blocks were missing copy affordance.
  const copyLabel = t("detail.copyCode");
  root.querySelectorAll<HTMLButtonElement>(".codeblock__copy").forEach((btn) => {
    btn.addEventListener("click", () => {
      const code = btn.parentElement?.querySelector("code")?.textContent ?? "";
      copyAndPulse(btn, code, copyLabel);
    });
  });
}

function tocBlock(s: Skill): string {
  // Build a small table of contents. Skip a section if it
  // wouldn't render anything (no inputs / no When-NOT-to-use /
  // no Example body). Output is always present; When to use
  // is required by the schema.
  const has = {
    wtu: true,
    inputs: (s.inputs?.length ?? 0) > 0,
    output: true,
    prompt: extractPromptText(s).length > 0,
    wnot: hasH1Section(s.body, "When NOT to use"),
    example: hasH1Section(s.body, "Example"),
  };
  const items: { id: string; label: string }[] = [];
  if (has.wtu)      items.push({ id: "when-to-use",      label: t("detail.wtu") });
  if (has.inputs)   items.push({ id: "inputs",           label: t("detail.inputs") });
  if (has.output)   items.push({ id: "output",           label: t("detail.output") });
  if (has.prompt)   items.push({ id: "prompt",           label: t("detail.prompt") });
  if (has.wnot)     items.push({ id: "when-not-to-use",  label: t("detail.wnot") });
  if (has.example)  items.push({ id: "example",          label: t("detail.example") });
  if (items.length <= 3) return "";  // not useful for very short pages
  return `
    <nav class="toc" aria-label="${escAttr(t("detail.toc"))}">
      <strong>${escHtml(t("detail.toc"))}</strong>
      <ol>${items.map(i => `<li><a href="#${i.id}" data-link>${escHtml(i.label)}</a></li>`).join("")}</ol>
    </nav>
  `;
}

function hasH1Section(body: string, h1: string): boolean {
  return body.split("\n").some(l => l.trim() === `# ${h1}`);
}

function platformChips(p: string[] | undefined): string {
  if (!p || p.length === 0) {
    return `<span class="chip chip--all" title="${escAttr(t("vendorNeutral"))}">${escHtml(t("anyChip"))}</span>`;
  }
  return p.map(x => {
    const label = pickPlatform(x);
    return `<span class="chip chip--${escAttr(x)}" title="${escAttr(t("platform.tip", { p: x }))}">${escHtml(label)}</span>`;
  }).join(" ");
}

// Bilingual block. We always render this when the skill has
// *any* zh field, and we open it by default in Chinese mode
// (otherwise a Chinese user sees a collapsed "中文" details
// box they have to click — annoying). In English mode we keep
// it collapsed as a "show original Chinese" reference.
function zhBlock(s: Skill): string {
  if (!s.name_zh && !s.description_zh) return "";
  const open = getLocale() === "zh";
  return `
    <details class="detail__zh"${open ? " open" : ""}>
      <summary>${escHtml(t("detail.bilingual"))}</summary>
      ${s.name_zh ? `<p><strong>${escHtml(s.name_zh)}</strong></p>` : ""}
      ${s.description_zh ? `<p>${escHtml(s.description_zh)}</p>` : ""}
    </details>
  `;
}

function inputsTable(s: Skill): string {
  if ((s.inputs?.length ?? 0) === 0) return "";
  const rows = (s.inputs ?? []).map(i => {
    const reqText = i.required
      ? t("input.required")
      : (i.default !== undefined ? t("input.default", { v: String(i.default) }) : t("input.optional"));
    return `
    <tr>
      <td><code>${escHtml(i.name)}</code></td>
      <td><code>${escHtml(i.type)}</code></td>
      <td>${escHtml(reqText)}</td>
      <td>${escHtml(i.description ?? "")}${i.values ? `<br/><small>${escHtml(t("input.values", { v: i.values.join(", ") }))}</small>` : ""}${i.constraints ? (i.constraints.min !== undefined || i.constraints.max !== undefined ? `<br/><small>${escHtml(t("input.range", { min: i.constraints.min ?? "−∞", max: i.constraints.max ?? "+∞" }))}</small>` : "") : ""}</td>
    </tr>
  `;
  }).join("");
  return `
    <h2 id="inputs">${escHtml(t("detail.inputs"))}</h2>
    <table>
      <thead><tr><th>${escHtml(t("table.name"))}</th><th>${escHtml(t("table.type"))}</th><th>${escHtml(t("table.required"))}</th><th>${escHtml(t("table.description"))}</th></tr></thead>
      <tbody>${rows}</tbody>
    </table>
  `;
}

function outputBlock(s: Skill): string {
  return `
    <h2 id="output">${escHtml(t("detail.output"))}</h2>
    <p><code>${escHtml(t("output.format", { f: s.output.format }))}</code>${s.output.description ? ` — ${escHtml(s.output.description)}` : ""}</p>
  `;
}

function promptBlock(s: Skill): string {
  // Prompt section body is in s.body between "# Prompt" and the next H1
  const text = extractPromptText(s);
  return `
    <pre><code>${escHtml(text)}</code></pre>
  `;
}

function extractPromptText(s: Skill): string {
  // Find the "Prompt" H1 and return everything until the next H1
  const lines = s.body.split("\n");
  const start = lines.findIndex(l => /^#\s+Prompt\s*$/.test(l));
  if (start === -1) return "";
  let end = lines.length;
  for (let i = start + 1; i < lines.length; i++) {
    if (/^#\s+/.test(lines[i]!)) { end = i; break; }
  }
  // Strip leading/trailing blank lines; the source prompt is
  // already inside a fenced block which we render as <pre><code>.
  return lines.slice(start + 1, end).join("\n").replace(/^\n+|\n+$/g, "");
}

function renderH1Section(body: string, h1: string): string {
  const lines = body.split("\n");
  const start = lines.findIndex(l => l.trim() === `# ${h1}`);
  if (start === -1) return "";
  let end = lines.length;
  for (let i = start + 1; i < lines.length; i++) {
    if (/^#\s+/.test(lines[i]!)) { end = i; break; }
  }
  const sectionBody = lines.slice(start + 1, end).join("\n");
  return mdToHtml(sectionBody);
}

// Tiny markdown subset: H1, H2, p, ul/ol, code fences, tables, inline code/bold.
function mdToHtml(src: string): string {
  const lines = src.split("\n");
  let out = "";
  let i = 0;
  while (i < lines.length) {
    const line = lines[i]!;
    if (line.startsWith("```")) {
      const lang = line.slice(3).trim();
      const buf: string[] = [];
      i++;
      while (i < lines.length && !lines[i]!.startsWith("```")) {
        buf.push(lines[i]!);
        i++;
      }
      i++; // skip closer
      // Wrap in a codeblock div with a per-block copy button.
      // The handler is attached after innerHTML is set in
      // renderDetail(). N9: body code blocks had no copy affordance
      // (only the dedicated prompt block did).
      out += `<div class="codeblock"><pre><code data-lang="${escAttr(lang)}">${escHtml(buf.join("\n"))}</code></pre><button class="codeblock__copy" type="button" aria-label="${escAttr(t("aria.copyCode"))}">${escHtml(t("detail.copyCode"))}</button></div>`;
      continue;
    }
    if (/^#{1,6}\s+/.test(line)) {
      const raw = line.match(/^#+/)?.[0].length ?? 1;
      const level = Math.min(raw, 6);
      const text = line.replace(/^#+\s+/, "");
      out += `<h${level + 2}>${inlineMd(text)}</h${level + 2}>`; // +2 because H1 is page title
      i++;
      continue;
    }
    if (/^\s*\|/.test(line) && i + 1 < lines.length && /^\s*\|[\s\-:|]+\|\s*$/.test(lines[i + 1]!)) {
      // Table
      const head = lines[i]!.split("|").slice(1, -1).map(c => c.trim());
      i += 2;
      const rows: string[][] = [];
      while (i < lines.length && /^\s*\|/.test(lines[i]!)) {
        rows.push(lines[i]!.split("|").slice(1, -1).map(c => c.trim()));
        i++;
      }
      out += `<table><thead><tr>${head.map(h => `<th>${inlineMd(h)}</th>`).join("")}</tr></thead><tbody>${rows.map(r => `<tr>${r.map(c => `<td>${inlineMd(c)}</td>`).join("")}</tr>`).join("")}</tbody></table>`;
      continue;
    }
    if (/^[-*]\s+/.test(line)) {
      const items: string[] = [];
      while (i < lines.length && /^[-*]\s+/.test(lines[i]!)) {
        items.push(lines[i]!.replace(/^[-*]\s+/, ""));
        i++;
      }
      out += `<ul>${items.map(it => `<li>${inlineMd(it)}</li>`).join("")}</ul>`;
      continue;
    }
    if (/^\d+\.\s+/.test(line)) {
      const items: string[] = [];
      while (i < lines.length && /^\d+\.\s+/.test(lines[i]!)) {
        items.push(lines[i]!.replace(/^\d+\.\s+/, ""));
        i++;
      }
      out += `<ol>${items.map(it => `<li>${inlineMd(it)}</li>`).join("")}</ol>`;
      continue;
    }
    if (line.trim() === "") {
      i++;
      continue;
    }
    // Paragraph: collect until blank
    const buf: string[] = [line];
    i++;
    while (i < lines.length && lines[i]!.trim() !== "" && !/^([-*]\s|\d+\.\s|```|#|\|)/.test(lines[i]!)) {
      buf.push(lines[i]!);
      i++;
    }
    out += `<p>${inlineMd(buf.join(" "))}</p>`;
  }
  return out;
}

function inlineMd(s: string): string {
  return s
    .replace(/`([^`]+)`/g, (_, x) => `<code>${escHtml(x)}</code>`)
    .replace(/\*\*([^*]+)\*\*/g, (_, x) => `<strong>${escHtml(x)}</strong>`)
    .replace(/\*([^*]+)\*/g, (_, x) => `<em>${escHtml(x)}</em>`)
    // Add link support: [text](url)
    .replace(/\[([^\]]+)\]\(([^)]+)\)/g, (_, text, url) => {
      // Validate URL to prevent javascript: and data: URLs
      const safeUrl = url.trim();
      if (/^(https?:\/\/|\/|#|mailto:)/.test(safeUrl)) {
        return `<a href="${escAttr(safeUrl)}" rel="noopener noreferrer" target="_blank">${escHtml(text)}</a>`;
      }
      // For relative or unknown schemes, escape and render as text
      return `[${escHtml(text)}](${escHtml(safeUrl)})`;
    });
}

async function copyAndPulse(btn: HTMLButtonElement, text: string, successLabel: string): Promise<void> {
  try {
    await navigator.clipboard.writeText(text);
  } catch {
    // Fallback: select-and-execCommand
    const ta = document.createElement("textarea");
    ta.value = text;
    ta.style.position = "fixed"; ta.style.opacity = "0";
    document.body.appendChild(ta);
    ta.select();
    try { document.execCommand("copy"); } finally { document.body.removeChild(ta); }
  }
  const old = btn.textContent;
  btn.textContent = successLabel;
  btn.classList.add("btn--pulse");
  setTimeout(() => {
    btn.textContent = old;
    btn.classList.remove("btn--pulse");
  }, 1500);
}

function downloadSkill(s: Skill): void {
  // Prefer the byte-for-byte original we vendored from the source
  // repo. Fall back to a re-emitted frontmatter + body if the
  // build pipeline was run without the raw field (defensive —
  // shouldn't happen in normal CI, but keeps the button working
  // if a contributor hand-writes a per-skill JSON).
  const text = s.rawMarkdown && s.rawMarkdown.length > 0
    ? s.rawMarkdown
    : dumpFrontmatter(s) + "\n" + s.body;
  const blob = new Blob([text], { type: "text/markdown" });
  const a = document.createElement("a");
  a.href = URL.createObjectURL(blob);
  a.download = `${s.slug}.md`;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  setTimeout(() => URL.revokeObjectURL(a.href), 1000);
}

// ============================ source block ============================
//
// Show the upstream provenance inline: vendor + commit + url + license.
// This is the part that makes the vault trustworthy — every skill
// can be traced back to a specific upstream commit.
//
// If `source` is missing entirely (hand-written skill, or older
// skill that pre-dates the field), we render a quieter "origin:
// local" block instead of nothing.

function sourceBlock(s: Skill): string {
  const src = s.source;
  if (!src) {
    return `
      <div class="source-block">
        <span class="source-block__label">${escHtml(t("detail.origin"))}</span>
        <span class="source-block__author">${escHtml(s.author || "local")}</span>
        <span class="source-block__commit">${escHtml(t("detail.local"))}</span>
      </div>
    `;
  }
  const host = sourceHost(src.url);
  const commit = src.commit && src.commit !== "n/a" ? src.commit : null;
  const shortCommit = commit ? commit.slice(0, 7) : null;
  // commitLinkHtml uses the narrowed `commit` value directly,
  // keeping the type checker happy without an extra non-null `!`.
  const commitLinkHtml = commit && shortCommit
    ? `<a class="source-block__commit" href="${escAttr(commitUrl(src))}" rel="noopener noreferrer" target="_blank" title="${escAttr(commit)}">${escHtml(shortCommit)}</a>`
    : `<span class="source-block__commit">${escHtml(t("detail.noCommit"))}</span>`;
  return `
    <div class="source-block">
      <span class="source-block__label">${escHtml(t("detail.source"))}</span>
      <a class="source-block__author" href="${escAttr(src.url)}" rel="noopener noreferrer" target="_blank">${escHtml(host)}</a>
      ${commitLinkHtml}
      ${src.license ? `<span class="source-block__commit">${escHtml(src.license)}</span>` : ""}
      ${src.fetched_at ? `<span class="source-block__commit">${escHtml(t("detail.fetched", { d: src.fetched_at }))}</span>` : ""}
    </div>
  `;
}

function sourceHost(url: string): string {
  // Try to extract a clean host. e.g. "https://github.com/foo/bar/tree/main/..."
  // → "github.com/foo/bar". Fall back to the raw url.
  try {
    const u = new URL(url);
    const parts = u.pathname.split("/").filter(Boolean);
    if (parts.length >= 2) return `${u.hostname}/${parts[0]}/${parts[1]}`;
    return u.hostname;
  } catch {
    return url;
  }
}

function commitUrl(src: SkillSource): string {
  // We don't have a generic "blob at commit" URL — it depends on
  // the host. For GitHub we know the pattern; for anything else
  // we link the repo root. The original_path (if any) is captured
  // in the frontmatter but we don't try to splice it in client-side
  // — getting it wrong is worse than getting it absent.
  const url = src.url;
  if (!src.commit || src.commit === "n/a") return url;
  if (url.includes("github.com")) {
    // If the URL already has /tree/<ref>/, replace <ref> with the
    // commit; otherwise append /tree/<commit>.
    const m = url.match(/^(https?:\/\/github\.com\/[^/]+\/[^/]+)(\/.*)?$/);
    if (m) {
      return `${m[1]}/tree/${src.commit}${m[2] ?? ""}`;
    }
  }
  return url;
}

// ============================ related skills ============================
//
// Pick up to N other skills in the same category, excluding the
// current one. Sorted to keep the order stable across renders.
// The point is "if you liked this, you'll probably want one of
// these" — a light recommendation, not a heavy graph.

function pickRelated(s: Skill, index: SkillIndex, n: number): SkillIndexEntry[] {
  const out: SkillIndexEntry[] = [];
  for (const e of index.skills) {
    if (e.slug === s.slug) continue;
    if (e.category !== s.category) continue;
    out.push(e);
  }
  return out.slice(0, n);
}

function relatedBlock(related: SkillIndexEntry[]): string {
  if (related.length === 0) return "";
  const cards = related.map(e => {
    const name = pickZh(e, "name");
    return `
    <a class="skill-card skill-card--inline" href="#/skill/${escAttr(e.slug)}" data-link>
      <div class="skill-card__head">
        <span class="skill-card__slug">${escHtml(e.slug)}</span>
        <span class="skill-card__name">${escHtml(name)}</span>
      </div>
    </a>
  `;
  }).join("");
  return `
    <section class="related" aria-label="${escAttr(t("aria.related"))}">
      <h2 class="related__title">${escHtml(t("detail.related", { cat: related[0]!.category.replace(/-/g, " ") }))}</h2>
      <div class="related__grid">${cards}</div>
    </section>
  `;
}

// ============================ 404 / not-found ============================
//
// Rendered when the URL hash points at a skill slug that isn't
// in skills.json. The page makes a best-effort to suggest
// similar slugs so a typo doesn't dead-end the user.

export function renderNotFound(root: HTMLElement, slug: string, index: SkillIndex): void {
  const suggestions = suggestSlugs(slug, index.skills, 5);
  const sugHtml = suggestions.length === 0
    ? ""
    : `
      <div class="notfound__suggest">
        <span class="notfound__suggest-label">${escHtml(t("nf.suggest"))}</span>
        ${suggestions.map(s => `<a class="notfound__chip" href="#/skill/${escAttr(s.slug)}" data-link>${escHtml(s.slug)}</a>`).join(" ")}
      </div>
    `;
  root.innerHTML = `
    <div class="notfound">
      <div class="notfound__glyph" aria-hidden="true">▮</div>
      <div class="notfound__code">${escHtml(t("nf.code"))}</div>
      <h1 class="notfound__title">${escHtml(t("nf.title", { slug }))}</h1>
      <p class="notfound__sub">${escHtml(t("nf.sub"))}</p>
      ${sugHtml}
      <div class="actions" style="justify-content: center;">
        <a class="btn btn--primary" href="#/" data-link>${escHtml(t("nf.back"))}</a>
        <a class="btn" href="#/bundle" data-link>${escHtml(t("nf.bundle"))}</a>
      </div>
    </div>
  `;
}

function suggestSlugs(needle: string, haystack: SkillIndexEntry[], n: number): SkillIndexEntry[] {
  const lower = needle.toLowerCase();
  // Cheap two-pass: prefix matches first, then contains, then
  // Levenshtein-ish via shared bigrams. We bail early at n.
  const scored: { e: SkillIndexEntry; s: number }[] = [];
  for (const e of haystack) {
    const hay = e.slug.toLowerCase();
    let s = 0;
    if (hay === lower) s = 100;             // exact
    else if (hay.startsWith(lower)) s = 50; // prefix
    else if (hay.includes(lower)) s = 25;   // contains
    else s = sharedBigrams(lower, hay);     // fuzzy
    if (s > 0) scored.push({ e, s });
  }
  scored.sort((a, b) => b.s - a.s);
  return scored.slice(0, n).map(x => x.e);
}

function sharedBigrams(a: string, b: string): number {
  // Count of two-character windows present in both. Bounded —
  // 0 means "nothing in common", higher means closer. Used only
  // for ordering, not for display.
  if (a.length < 2 || b.length < 2) return 0;
  const set = new Set<string>();
  for (let i = 0; i < a.length - 1; i++) set.add(a.slice(i, i + 2));
  let n = 0;
  for (let i = 0; i < b.length - 1; i++) if (set.has(b.slice(i, i + 2))) n++;
  return n;
}
