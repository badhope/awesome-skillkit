// i18n — tiny in-house translator.
//
// Why this exists:
//   · Several skills have `name_zh` / `description_zh` in their
//     frontmatter; we want to show those when the user is on
//     the Chinese locale, and the English originals otherwise.
//   · The rest of the UI (hero, filter placeholders, button
//     labels, 404 text) is hard-coded in English today. This
//     module is the one place to add a Chinese variant.
//
// Design choices:
//   · Flat string key map. The set of strings is small and
//     flat-nested objects would just add ceremony.
//   · Single source of truth: `STRINGS.en` and `STRINGS.zh`.
//     `t(key)` picks the right one based on the current locale.
//     Missing translations fall through to English silently —
//     it's better to show English than to show a key.
//   · Locale is stored in localStorage. URL `?lang=zh` overrides
//     on first load so links stay shareable. The lang switch
//     in the topbar flips localStorage and re-renders the
//     current page (via the langchange event).
//   · `subscribe()` lets the router re-render the current
//     view on language change. The list page re-runs the
//     paint() loop; the detail page re-fetches the skill
//     body and re-renders the same data.

export type Locale = "en" | "zh";

const STORAGE_KEY = "ai-skill:lang";
const URL_PARAM = "lang";
const SUPPORTED: Locale[] = ["en", "zh"];

let current: Locale = detect();
const subs = new Set<() => void>();

function detect(): Locale {
  // URL takes precedence (so a shared link with ?lang=zh
  // always opens in Chinese, regardless of saved state).
  const u = new URL(window.location.href);
  const q = u.searchParams.get(URL_PARAM);
  if (q === "zh" || q === "en") {
    try { localStorage.setItem(STORAGE_KEY, q); } catch { /* sandboxed iframe etc. */ }
    return q;
  }
  // Then localStorage (sticky across reloads).
  try {
    const s = localStorage.getItem(STORAGE_KEY);
    if (s === "zh" || s === "en") return s;
  } catch { /* no storage — fine, default to en */ }
  return "en";
}

export function getLocale(): Locale { return current; }

export function setLocale(l: Locale): void {
  if (!SUPPORTED.includes(l) || l === current) return;
  current = l;
  try { localStorage.setItem(STORAGE_KEY, l); } catch { /* ignore */ }
  // Reflect into the URL so a copy-paste preserves the choice.
  const u = new URL(window.location.href);
  u.searchParams.set(URL_PARAM, l);
  history.replaceState(null, "", u.toString());
  // Notify subscribers (router re-runs the current view).
  for (const fn of subs) {
    try { fn(); } catch (e) {
      // Production: suppress detailed error logs to prevent information leakage
      if (import.meta.env.DEV) {
        console.error("[i18n] subscriber threw", e);
      }
    }
  }
}

export function toggleLocale(): void {
  setLocale(current === "en" ? "zh" : "en");
}

export function subscribe(fn: () => void): () => void {
  subs.add(fn);
  return () => subs.delete(fn);
}

// ============================ strings ============================
//
// Add a key in BOTH maps when you introduce new UI text.
// English is the source of truth; a missing `zh` falls back to
// `en` so the app never renders an empty string or a key.

const STRINGS = {
  // ----- list page -----
  "eyebrow.tag":     { en: "vendor-neutral skill vault",        zh: "厂商中立 · 技能库" },
  "eyebrow.version": { en: "v1.0.0",                            zh: "v1.0.0" },
  "hero.title1":     { en: "files, ready to drop in.",          zh: "个文件，开箱即用。" },
  "hero.sub":        {
    en: "Markdown prompts for Claude, Codex, Cursor, Continue — and any agent that reads a folder. Sourced from deepeval, promptfoo, langfuse, OpenAI, Anthropic, Hugging Face, Letta, and a handful of hand-written ones. No tracking. No signup.",
    zh: "面向 Claude、Codex、Cursor、Continue 以及所有能读文件夹的智能体的 Markdown 提示词。来源覆盖 deepeval、promptfoo、langfuse、OpenAI、Anthropic、Hugging Face、Letta，外加少量手写。无追踪、无注册。",
  },
  "hero.cta.bundle": { en: "Pick a bundle →",                   zh: "挑个合集 →" },
  "hero.cta.gh":     { en: "View on GitHub",                    zh: "在 GitHub 上看" },

  "stat.total.label":      { en: "SKILL.md",                zh: "SKILL.md" },
  "stat.categories.label": { en: "Categories",              zh: "分类" },
  "stat.neutral.label":    { en: "Vendor-neutral",          zh: "厂商中立" },
  "stat.review.label":     { en: "Needs review",            zh: "待复审" },
  "stat.total.suffix":     { en: "files",                   zh: "个文件" },
  "stat.cat.suffix":       { en: "groups",                  zh: "个分组" },
  "stat.neutral.suffix":   { en: "of {n}",                  zh: "共 {n}" },
  "stat.review.suffix":    { en: "flagged",                 zh: "已标记" },

  "filter.search.ph":     { en: "Search by name, slug, tag, description…", zh: "按名称 / slug / 标签 / 描述搜索…" },
  "filter.cat.label":     { en: "Category",                       zh: "分类" },
  "filter.cat.all":       { en: "All categories",                 zh: "全部分类" },
  "filter.plat.label":    { en: "Platform",                       zh: "平台" },
  "filter.plat.all":      { en: "All platforms",                  zh: "全部平台" },
  "filter.plat.any":      { en: "Any (vendor-neutral)",           zh: "任意（厂商中立）" },
  "filter.plat.claude":   { en: "Claude",                         zh: "Claude" },
  "filter.plat.codex":    { en: "Codex",                          zh: "Codex" },
  "filter.plat.cursor":   { en: "Cursor",                         zh: "Cursor" },
  "filter.plat.continue": { en: "Continue",                       zh: "Continue" },
  "filter.group":         { en: "group",                          zh: "分组" },
  "empty.noMatch":        { en: "No skills match. Try a different search or clear filters.", zh: "没有匹配的技能。换个关键词或清空筛选条件。" },

  // ----- detail page -----
  "detail.back":        { en: "← back to list",                  zh: "← 返回列表" },
  "detail.bilingual":   { en: "中文",                            zh: "中文" },
  "detail.bilingualEn": { en: "English",                         zh: "English" },
  "detail.source":      { en: "source",                          zh: "来源" },
  "detail.origin":      { en: "origin",                          zh: "来源" },
  "detail.noCommit":    { en: "no commit",                       zh: "无 commit" },
  "detail.fetched":     { en: "fetched {d}",                     zh: "拉取于 {d}" },
  "detail.local":       { en: "no upstream · hand-written",      zh: "无上游 · 手工编写" },
  "detail.wtu":         { en: "When to use",                     zh: "何时使用" },
  "detail.wnot":        { en: "When NOT to use",                 zh: "何时不要用" },
  "detail.example":     { en: "Example",                         zh: "示例" },
  "detail.toc":         { en: "On this page",                    zh: "本页目录" },
  "detail.inputs":      { en: "Inputs",                          zh: "输入" },
  "detail.output":      { en: "Output",                          zh: "输出" },
  "detail.prompt":      { en: "Prompt",                          zh: "Prompt" },
  "detail.copy":        { en: "Copy prompt",                     zh: "复制 Prompt" },
  "detail.copied":      { en: "Copied",                          zh: "已复制" },
  "detail.download":    { en: "Download .md",                    zh: "下载 .md" },
  "detail.copyCode":    { en: "Copy",                            zh: "复制" },
  "detail.related":     { en: "More from {cat}",                 zh: "同分类更多" },

  // ----- bundle page -----
  "bundle.title":      { en: "Bundle — pick skills, get a zip",  zh: "合集 — 勾选技能，下载 zip" },
  "bundle.intro":      { en: "Tick the skills you want. The zip is built in your browser, nothing is uploaded.", zh: "勾选你想要的技能。zip 在浏览器内打包，没有任何上传。" },
  "bundle.filter.ph":  { en: "Filter skills…",                   zh: "筛选技能…" },
  "bundle.selectAll":  { en: "Select all",                       zh: "全选" },
  "bundle.clear":      { en: "Clear",                            zh: "清空" },
  "bundle.selected":   { en: "Selected:",                        zh: "已选：" },
  "bundle.download":   { en: "Download .zip",                    zh: "下载 .zip" },
  "bundle.building":   { en: "Building…",                        zh: "打包中…" },
  "bundle.failed":     { en: "Bundle failed: {msg}",             zh: "打包失败：{msg}" },

  // ----- 404 / not found -----
  "nf.code":        { en: "404 · skill not found",               zh: "404 · 找不到该技能" },
  "nf.title":       { en: "No skill called {slug}",              zh: "没有名为 {slug} 的技能" },
  "nf.sub":         { en: "It may have been renamed, or the link could be from an older version of the vault. Try the list, or check the spelling below.", zh: "可能已改名，或链接来自旧版本。回列表看看，或检查下面的拼写建议。" },
  "nf.suggest":     { en: "did you mean",                        zh: "你是不是想看" },
  "nf.back":        { en: "← back to the list",                  zh: "← 返回列表" },
  "nf.bundle":      { en: "open the bundle picker",              zh: "打开合集选择器" },

  // ----- generic -----
  "loading":        { en: "Loading…",                            zh: "加载中…" },
  "unknownRoute":   { en: "Unknown route.",                      zh: "未知路径。" },
  "backToList":     { en: "Back to list",                        zh: "返回列表" },
  "errorPrefix":    { en: "Failed to load:",                     zh: "加载失败：" },
  "language.label": { en: "EN",                                  zh: "中" },
  "language.title": { en: "Switch language",                     zh: "切换语言" },
  "vendorNeutral":  { en: "Vendor-neutral — works on any agent", zh: "厂商中立 — 适用于任何智能体" },
  "anyChip":        { en: "any",                                 zh: "任意" },
  "platformChip":   { en: "{p}",                                 zh: "{p}" },
  // ----- topbar / nav -----
  "nav.bundle":       { en: "Bundle",                            zh: "合集" },
  "nav.external":     { en: "External",                          zh: "外部仓库" },
  "nav.gh":           { en: "GitHub",                            zh: "GitHub" },
  "footer.tagline":   { en: "MIT · vendor-neutral · no tracking · static site", zh: "MIT · 厂商中立 · 无追踪 · 静态站点" },
  "footer.source":    { en: "Source on GitHub",                  zh: "在 GitHub 上查看" },
  "footer.sources":   { en: "SOURCE.md",                         zh: "SOURCE.md" },
  "footer.contrib":   { en: "Contributing",                      zh: "贡献指南" },
  "footer.changelog": { en: "Changelog",                         zh: "更新日志" },

  // ----- list group counts -----
  "categoryCount.one":   { en: "{n} skill",                       zh: "{n} 个技能" },
  "categoryCount.other": { en: "{n} skills",                      zh: "{n} 个技能" },

  // ----- detail extras (table headers, source, related) -----
  "table.name":        { en: "name",          zh: "名称" },
  "table.type":        { en: "type",          zh: "类型" },
  "table.required":    { en: "required",      zh: "必填" },
  "table.description": { en: "description",   zh: "说明" },
  "output.format":     { en: "format: {f}",   zh: "格式：{f}" },
  "input.required":    { en: "required",      zh: "必填" },
  "input.optional":    { en: "optional",      zh: "可选" },
  "input.default":     { en: "default: {v}",  zh: "默认：{v}" },
  "input.values":      { en: "values: {v}",   zh: "取值：{v}" },
  "input.range":       { en: "range: {min} … {max}", zh: "范围：{min} … {max}" },
  "reviewDot.title":   { en: "needs_review",  zh: "待复审" },

  // ----- platform chips -----
  // We translate the *display* label but keep the slug
  // (`chip--claude` etc.) untouched so the CSS color tokens
  // still match. Tooltip is the localized name + " (vendor: …)".
  "platform.claude":   { en: "Claude",                       zh: "Claude" },
  "platform.codex":    { en: "Codex",                        zh: "Codex" },
  "platform.cursor":   { en: "Cursor",                       zh: "Cursor" },
  "platform.continue": { en: "Continue",                     zh: "Continue" },
  "platform.tip":      { en: "platform: {p}",                zh: "平台：{p}" },

  // ----- aria / accessibility / misc -----
  "aria.vaultStats":   { en: "vault statistics",             zh: "技能库统计" },
  "aria.related":      { en: "related skills",               zh: "相关技能" },
  "aria.copyCode":     { en: "Copy code",                    zh: "复制代码" },
  "aria.langToggle":   { en: "Switch language",              zh: "切换语言" },

  // ----- version / license display -----
  "meta.version":      { en: "v{n}",                         zh: "v{n}" },
  "meta.license":      { en: "{l}",                          zh: "{l}" },
  "meta.slug":         { en: "{s}",                          zh: "{s}" },
  "meta.category":     { en: "{c}",                          zh: "{c}" },

  // ----- external repos page -----
  "external.title":      { en: "External repositories",           zh: "外部仓库索引" },
  "external.subtitle":   { en: "We don't have every skill in the world — here are the upstream repos we pull from. Click through to grab anything we don't vendored.", zh: "我们没把全世界的技能都收齐 —— 这里列出我们抓取过的上游仓库。没收录的，可以自己去原仓库挑。" },
  "external.vendor":     { en: "Vendor",                          zh: "厂商" },
  "external.skills":     { en: "skills",                          zh: "条技能" },
  "external.category":   { en: "Category",                        zh: "分类" },
  "external.license":    { en: "License",                         zh: "许可证" },
  "external.ref":        { en: "ref",                             zh: "ref" },
  "external.visit":      { en: "Visit on GitHub",                 zh: "在 GitHub 上查看" },
  "external.hint":       { en: "Each card links to the upstream repo. SKILL.md files inside the repo use the same shape we vendor; you can drop them in directly.", zh: "每张卡片链向上游仓库。仓库里的 SKILL.md 用的是我们采用的同一种格式，可以直接拿去用。" },
  "external.empty":      { en: "No external repositories registered yet.", zh: "还没有登记外部仓库。" },
  "external.errorLoad":  { en: "Could not load the repo list. Try reloading the page.", zh: "加载仓库列表失败，刷新页面重试。" },

  // ----- footer brand / glyphs (no translation, but kept here for symmetry) -----
  "brand.glyph":       { en: "▮ AI-SKILL",                   zh: "▮ AI-SKILL" },
  "brand.markOnly":    { en: "▮",                            zh: "▮" },

  // ----- accessibility & noscript fallback (used by index.html /
  //       404.html static shell, applied by applyStaticTranslations) -----
  "a11y.skip":         { en: "Skip to content",              zh: "跳到正文" },
  "noscript.line1":    { en: "This page is a small JavaScript app — without JS you only get this notice.", zh: "本站是个小 JavaScript 应用 —— 关闭 JS 只会显示这条提示。" },
  "noscript.line2":    { en: "Enable JavaScript, or",        zh: "请打开 JavaScript，或者" },
  "noscript.link":     { en: "browse the source on GitHub",  zh: "去 GitHub 浏览源文件" },
  "noscript.line3":    { en: "for plain SKILL.md files.",    zh: "拿原始的 SKILL.md。" },

  // ----- document-level metadata (mirrored to <title>,
  //       <meta name="description">, and the og:* family
  //       when the locale flips, so link previews, browser tabs,
  //       and search-result snippets all match the user's
  //       language) -----
  "meta.title":        { en: "AI-SKILL · vendor-neutral skill vault",         zh: "AI-SKILL · 跨平台技能库" },
  "meta.description":  { en: "A vendor-neutral vault of agent skills. SKILL.md files sourced from deepeval, promptfoo, langfuse, openai, letta, huggingface, anthropics, and hand-written. Drop into Claude, Codex, Cursor, or any Markdown-reading agent.", zh: "一个中立的 agent 技能库，SKILL.md 收录自 deepeval / promptfoo / langfuse / openai / letta / huggingface / anthropics 以及自写。可直接放进 Claude / Codex / Cursor 或任何读 Markdown 的 agent。" },
  "meta.ogTitle":      { en: "AI-SKILL · vendor-neutral skill vault",         zh: "AI-SKILL · 跨平台技能库" },
  "meta.ogDescription":{ en: "SKILL.md files. No tracking. No signup. Just markdown.", zh: "SKILL.md，无追踪、无注册，就是 markdown。" },
} as const satisfies Record<string, Record<Locale, string>>;

type Key = keyof typeof STRINGS;

/**
 * t("hero.title1") → "files, ready to drop in." (en)
 * t("hero.title1") → "个文件，开箱即用。"        (zh)
 * t("nf.title", {slug: "foo"}) → "No skill called foo"
 *
 * Missing keys fall through to English so a half-translated
 * app still works. `{name}`-style placeholders use a single
 * `String#replace` per match; nested braces aren't supported.
 */
export function t(key: Key, vars?: Record<string, string | number>): string {
  const entry = STRINGS[key] as Record<Locale, string> | undefined;
  let s = entry?.[current] ?? entry?.en ?? String(key);
  if (vars) {
    for (const [k, v] of Object.entries(vars)) {
      s = s.replace(new RegExp(`\\{${k}\\}`, "g"), String(v));
    }
  }
  return s;
}

/**
 * Update the text content of every element with `data-i18n="<key>"`.
 * Run on subscribe() so the static parts of the shell (topbar
 * nav, footer) swap in place when the user toggles language.
 *
 * Also handles `data-i18n-aria` and `data-i18n-title` for
 * accessibility and tooltip strings on the same elements.
 *
 * The element's existing text is left in place as a fallback
 * for the brief moment between the toggle and the next paint.
 */
export function applyStaticTranslations(): void {
  document.querySelectorAll<HTMLElement>("[data-i18n]").forEach(el => {
    const key = el.dataset.i18n as Key | undefined;
    if (key) el.textContent = t(key);
  });
  document.querySelectorAll<HTMLElement>("[data-i18n-aria]").forEach(el => {
    const key = el.dataset.i18nAria as Key | undefined;
    if (key) el.setAttribute("aria-label", t(key));
  });
  document.querySelectorAll<HTMLElement>("[data-i18n-title]").forEach(el => {
    const key = el.dataset.i18nTitle as Key | undefined;
    if (key) el.setAttribute("title", t(key));
  });
  // Also reflect the language into <html lang="…"> for screen
  // readers and CSS hooks (e.g. `:lang(zh)` if we ever need it).
  document.documentElement.lang = current;
  // Update the <title> + <meta name="description"> + og:* fields
  // so link previews / browser tab / search results match the
  // current locale. These come from i18n keys so adding a new
  // locale doesn't require touching this function.
  const titleEl = document.querySelector<HTMLElement>("title[data-i18n]");
  if (titleEl) titleEl.textContent = t(titleEl.dataset.i18n as Key);
  const descEl = document.querySelector<HTMLMetaElement>('meta[name="description"][data-i18n]');
  if (descEl) descEl.setAttribute("content", t(descEl.dataset.i18n as Key));
  document
    .querySelectorAll<HTMLMetaElement>('meta[property^="og:"][data-i18n]')
    .forEach((el) => {
      const key = el.dataset.i18n as Key | undefined;
      if (key) el.setAttribute("content", t(key));
    });
}

/** Pick the localized version of a skill name/description. */
export function pickZh<T extends { name: string; name_zh?: string; description: string; description_zh?: string }>(
  obj: T,
  field: "name" | "description",
): string {
  if (current === "zh") {
    const zh = field === "name" ? obj.name_zh : obj.description_zh;
    if (zh) return zh;
  }
  return obj[field];
}

/**
 * Translate a platform slug (claude / codex / cursor / continue)
 * to its display label. Falls back to the slug itself for any
 * platform we don't have a translation for — that way a new
 * platform added in the frontmatter still renders something.
 */
export function pickPlatform(platform: string): string {
  const key = `platform.${platform}` as Key;
  const entry = STRINGS[key] as Record<Locale, string> | undefined;
  return entry?.[current] ?? entry?.en ?? platform;
}
