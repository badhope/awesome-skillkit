/// <reference types="vite/client" />
// Skill data types — kept in sync with docs/schema.md.
// The build pipeline (scripts/sync-data.mjs) writes
// public/skills.json from the SKILL.md files in /skills/.
// We use the slim index (name, slug, category, tags) and
// fetch full SKILL.md text on demand for the detail page.

export interface SkillIndexEntry {
  slug: string;
  name: string;
  name_zh?: string;
  description: string;
  category: string;
  tags: string[];
  platforms: string[];
  needs_review: boolean;
  path: string;
}

export interface SkillIndex {
  skills: SkillIndexEntry[];
}

export interface SkillInput {
  name: string;
  type: string;
  required?: boolean;
  description?: string;
  default?: unknown;
  values?: string[];
  constraints?: { min?: number; max?: number };
}

export interface SkillOutput {
  format: string;
  description?: string;
  schema?: Record<string, unknown>;
}

export interface Skill {
  slug: string;
  name: string;
  name_zh?: string;
  version: string;
  description: string;
  description_zh?: string;
  category: string;
  tags: string[];
  platforms: string[];
  inputs: SkillInput[];
  output: SkillOutput;
  author: string;
  license: string;
  created: string;
  updated: string;
  needs_review: boolean;
  body: string; // Markdown body (everything after the `---` closer)
}
