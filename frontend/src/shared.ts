// Shared utilities used across list, detail, and bundle pages.
// Kept in one place so the category labels, escape functions,
// and YAML dumper stay in sync.

import type { Skill } from "./types";
import { getLocale } from "./i18n";

// ============================ category labels ============================

export const CATEGORY_LABELS: Record<string, { en: string; zh: string }> = {
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

export function categoryLabel(cat: string): string {
  const m = CATEGORY_LABELS[cat];
  if (m) return getLocale() === "zh" ? m.zh : m.en;
  return cat.replace(/-/g, " ").replace(/\b\w/g, c => c.toUpperCase());
}

// ============================ HTML escaping ============================

export function escHtml(s: string): string {
  return s.replace(/[&<>"']/g, c => ({
    "&": "&amp;", "<": "&lt;", ">": "&gt;",
    '"': "&quot;", "'": "&#39;",
  }[c]!));
}

export function escAttr(s: string): string {
  return escHtml(s);
}

// ============================ YAML dumper ============================

export function dumpFrontmatter(s: Skill): string {
  const lines: string[] = ["---"];
  const set = (k: string, v: unknown, indent = 0) => {
    const pad = " ".repeat(indent);
    if (v === undefined || v === null) return;
    if (Array.isArray(v)) {
      if (v.length === 0) { lines.push(`${pad}${k}: []`); return; }
      lines.push(`${pad}${k}:`);
      for (const x of v) {
        if (x !== null && typeof x === "object" && !Array.isArray(x)) {
          lines.push(`${pad}  -`);
          for (const [kk, vv] of Object.entries(x)) set(kk, vv, indent + 4);
        } else {
          lines.push(`${pad}  - ${formatScalar(x)}`);
        }
      }
      return;
    }
    if (typeof v === "object") {
      lines.push(`${pad}${k}:`);
      for (const [kk, vv] of Object.entries(v)) {
        if (vv === undefined) continue;
        set(kk, vv, indent + 2);
      }
      return;
    }
    lines.push(`${pad}${k}: ${formatScalar(v)}`);
  };
  set("slug", s.slug);
  set("name", s.name);
  set("name_zh", s.name_zh);
  set("version", s.version);
  set("description", s.description);
  set("description_zh", s.description_zh);
  set("category", s.category);
  set("tags", s.tags);
  set("platforms", s.platforms);
  set("inputs", s.inputs);
  set("output", s.output);
  set("author", s.author);
  set("license", s.license);
  set("created", s.created);
  set("updated", s.updated);
  set("needs_review", s.needs_review);
  return lines.join("\n") + "\n---\n";
}

function formatScalar(v: unknown): string {
  if (typeof v === "string") return JSON.stringify(v);
  if (typeof v === "number" || typeof v === "boolean") return String(v);
  return JSON.stringify(v);
}
