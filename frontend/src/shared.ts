// Shared utilities used across list, detail, and bundle pages.
// Kept in one place so the category labels, escape functions,
// and YAML dumper stay in sync.

import type { Skill, SkillIndexEntry } from "./types";
import { getLocale, t, pickPlatform } from "./i18n";

// ============================ category labels ============================

export const CATEGORY_LABELS: Record<string, { en: string; zh: string }> = {
  "applications":          { en: "Applications",          zh: "应用" },
  "agent-frameworks":      { en: "Agent frameworks",       zh: "Agent 框架" },
  "audio-speech":          { en: "Audio & speech",         zh: "音频与语音" },
  "awesome-lists":         { en: "Awesome lists",          zh: "精选列表" },
  "benchmarks":            { en: "Benchmarks",             zh: "基准测试" },
  "browser-automation":    { en: "Browser automation",     zh: "浏览器自动化" },
  "case-studies":          { en: "Case studies",           zh: "案例研究" },
  "chat-uikits":           { en: "Chat UI kits",           zh: "聊天 UI 套件" },
  "code-assistants":       { en: "Code assistants",        zh: "代码助手" },
  "code-llms":             { en: "Code LLMs",              zh: "代码大模型" },
  "computer-use":          { en: "Computer use",           zh: "计算机操作" },
  "customer-support":      { en: "Customer support",       zh: "客户支持" },
  "data-pipelines":        { en: "Data pipelines",         zh: "数据流水线" },
  "dev-tools":             { en: "Developer tools",        zh: "开发工具" },
  "distributed-training":  { en: "Distributed training",   zh: "分布式训练" },
  "documentation":         { en: "Documentation",          zh: "文档" },
  "education":             { en: "Education",              zh: "教育" },
  "embeddings":            { en: "Embeddings",             zh: "向量嵌入" },
  "evaluation":            { en: "Evaluation",             zh: "评估" },
  "finance":               { en: "Finance",                zh: "金融" },
  "fine-tuning":           { en: "Fine-tuning",            zh: "微调" },
  "gpu-kernels":           { en: "GPU kernels",            zh: "GPU 内核" },
  "guardrails":            { en: "Guardrails & safety",    zh: "护栏与安全" },
  "image-generation":      { en: "Image generation",       zh: "图像生成" },
  "knowledge-graphs":      { en: "Knowledge graphs",       zh: "知识图谱" },
  "legal":                 { en: "Legal",                  zh: "法律" },
  "llm-serving":           { en: "LLM serving",            zh: "LLM 部署" },
  "mcp-protocol":          { en: "MCP protocol",           zh: "MCP 协议" },
  "medical-bio":           { en: "Medical & bio",          zh: "医疗与生物" },
  "memory":                { en: "Memory & context",       zh: "记忆与上下文" },
  "model-merging":         { en: "Model merging & MoE",    zh: "模型合并与 MoE" },
  "multimodal":            { en: "Multimodal",             zh: "多模态" },
  "observability":         { en: "Observability",          zh: "可观测性" },
  "official-cookbooks":    { en: "Official cookbooks",     zh: "官方 Cookbook" },
  "privacy-federated":     { en: "Privacy & federated",    zh: "隐私与联邦学习" },
  "prompt-libraries":      { en: "Prompt libraries",       zh: "提示词库" },
  "quantization":          { en: "Quantization",           zh: "量化与压缩" },
  "rag-retrieval":         { en: "RAG & retrieval",        zh: "RAG 与检索" },
  "reasoning-models":      { en: "Reasoning models",       zh: "推理模型" },
  "robotics-embodied":     { en: "Robotics & embodied",    zh: "机器人与具身" },
  "safety-alignment":      { en: "Safety & alignment",     zh: "安全与对齐" },
  "scientific-ml":         { en: "Scientific ML",          zh: "科学机器学习" },
  "synthetic-data":        { en: "Synthetic data",         zh: "合成数据" },
  "terminal-cli":          { en: "Terminal & CLI",         zh: "终端与 CLI" },
  "text-to-sql":           { en: "Text-to-SQL",            zh: "Text-to-SQL" },
  "tool-use":              { en: "Tool use & function calling", zh: "工具使用与函数调用" },
  "translation":           { en: "Translation",            zh: "翻译" },
  "vector-databases":      { en: "Vector databases",       zh: "向量数据库" },
  "video-generation":      { en: "Video generation",       zh: "视频生成" },
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

// ============================ shared utilities ============================

/** Stable string hash → hue (0-359). Used for category/vendor color chips. */
export function stableHue(s: string): number {
  let h = 0;
  for (let i = 0; i < s.length; i++) h = (h * 31 + s.charCodeAt(i)) >>> 0;
  return h % 360;
}

/** Category color string for inline CSS. */
export function categoryColor(cat: string): string {
  return `hsl(${stableHue(cat)} 60% 52%)`;
}

/** Build platform chips HTML for a skill card / detail page. */
export function platformChipsHtml(platforms: string[] | undefined): string {
  if (!platforms || platforms.length === 0) {
    return `<span class="chip chip--all" title="${escAttr(t("vendorNeutral"))}">${escHtml(t("anyChip"))}</span>`;
  }
  return platforms.map(p => {
    const label = pickPlatform(p);
    return `<span class="chip chip--${escAttr(p)}" title="${escAttr(t("platform.tip", { p }))}">${escHtml(label)}</span>`;
  }).join(" ");
}

/** Pre-compute a lowercased search blob for a skill entry. */
export function buildSearchBlob(s: SkillIndexEntry): string {
  return `${s.slug} ${s.name} ${s.name_zh ?? ""} ${(s.tags ?? []).join(" ")} ${s.category} ${s.description} ${s.description_zh ?? ""}`.toLowerCase();
}

/** Debounce a function call by `ms` milliseconds. */
export function debounce<T extends (...a: never[]) => void>(fn: T, ms: number): T {
  let h: ReturnType<typeof setTimeout> | null = null;
  return ((...args: never[]) => {
    if (h) clearTimeout(h);
    h = setTimeout(() => fn(...args), ms);
  }) as T;
}

/** Trigger a browser download for a Blob, cleaning up the object URL. */
export function triggerBlobDownload(blob: Blob, filename: string): void {
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  setTimeout(() => URL.revokeObjectURL(url), 1000);
}

/** Convert a Skill object back to SKILL.md text, preferring rawMarkdown. */
export function skillToMarkdown(s: Skill): string {
  if (s.rawMarkdown && s.rawMarkdown.length > 0) return s.rawMarkdown;
  return dumpFrontmatter(s) + "\n" + s.body;
}
