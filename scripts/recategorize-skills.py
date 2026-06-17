#!/usr/bin/env python3
"""Recategorize all skills into the 49 valid categories.

Maps each skill slug to the best-fitting category from
external-index/skills.yaml based on slug, name, description,
and tags. Run once to fix the category skew (201/267 in dev-tools).
"""
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SKILLS_DIR = REPO / "skills"

# Comprehensive slug → category mapping based on content analysis.
# Categories are the 49 defined in external-index/skills.yaml.
CATEGORY_MAP: dict[str, str] = {
    # --- agent-frameworks ---
    "agent": "agent-frameworks",
    "agent-development": "agent-frameworks",
    "agent-runtime-hooks": "agent-frameworks",
    "agent-setup-maintenance": "agent-frameworks",
    "agent-signal": "agent-frameworks",
    "conversations": "agent-frameworks",
    "creating-letta-code-channels": "agent-frameworks",
    "fleet-management": "agent-frameworks",
    "heterogeneous-agent": "agent-frameworks",
    "letta-api-client": "agent-frameworks",
    "letta-configuration": "agent-frameworks",
    "orchestrate": "agent-frameworks",

    # --- observability ---
    "agent-tracing": "observability",
    "datadog": "observability",
    "datadog-query-recipes": "observability",
    "debug-issue-with-datadog": "observability",
    "deepeval-otel": "observability",
    "deepeval-tracing": "observability",
    "fetch-buildkite-logs": "observability",
    "huggingface-trackio": "observability",
    "maf-tracing": "observability",
    "sentry": "observability",

    # --- evaluation ---
    "bootstrap-realtime-eval": "evaluation",
    "deepeval": "evaluation",
    "deepeval-eval-suite": "evaluation",
    "huggingface-community-evals": "evaluation",
    "parity-testing": "evaluation",
    "promptfoo-evals": "evaluation",
    "promptfoo-provider-setup": "evaluation",
    "realtime-eval-bootstrap": "evaluation",
    "testing": "evaluation",

    # --- safety-alignment ---
    "promptfoo-redteam": "safety-alignment",
    "promptfoo-redteam-run": "safety-alignment",
    "promptfoo-redteam-setup": "safety-alignment",
    "redteam-plugin-development": "safety-alignment",

    # --- guardrails ---
    "response-compliance": "guardrails",
    "secure-code-by-language": "guardrails",
    "security-best-practices": "guardrails",
    "security-ownership-map": "guardrails",
    "security-review": "guardrails",
    "security-threat-model": "guardrails",
    "threat-modeling": "guardrails",

    # --- mcp-protocol ---
    "mcp-builder": "mcp-protocol",
    "hf-mcp": "mcp-protocol",

    # --- tool-use ---
    "builtin-tool": "tool-use",
    "develop-ai-functions-example": "tool-use",
    "huggingface-tool-builder": "tool-use",

    # --- memory ---
    "hf-mem": "memory",
    "importing-chatgpt-memory": "memory",
    "letta-filesystem-to-memfs": "memory",
    "memfs-search": "memory",
    "navigating-chatgpt-history": "memory",

    # --- embeddings ---
    "embedding-model-training": "embeddings",
    "train-sentence-transformers": "embeddings",

    # --- fine-tuning ---
    "huggingface-llm-trainer": "fine-tuning",
    "huggingface-lora-space-builder": "fine-tuning",
    "huggingface-vision-trainer": "fine-tuning",
    "model-integration": "fine-tuning",
    "trl-training": "fine-tuning",

    # --- distributed-training ---
    "ray-dependencies": "distributed-training",

    # --- llm-serving ---
    "claude-api": "llm-serving",
    "cloudflare-deploy": "llm-serving",
    "haiku": "llm-serving",
    "huggingface-gradio": "llm-serving",
    "huggingface-local-models": "llm-serving",
    "huggingface-spaces": "llm-serving",
    "huggingface-zerogpu": "llm-serving",
    "maf-online-endpoint": "llm-serving",
    "modal": "llm-serving",
    "netlify-deploy": "llm-serving",
    "render-deploy": "llm-serving",
    "update-provider-models": "llm-serving",
    "vercel-deploy": "llm-serving",

    # --- data-pipelines ---
    "data-fetching-architecture": "data-pipelines",
    "huggingface-datasets": "data-pipelines",
    "maf-prs-job": "data-pipelines",
    "promptflow-to-maf": "data-pipelines",

    # --- terminal-cli ---
    "cli": "terminal-cli",
    "cli-backend-testing": "terminal-cli",
    "cli-builder": "terminal-cli",
    "cli-creator": "terminal-cli",
    "hf-cli": "terminal-cli",
    "llamactl-qa": "terminal-cli",
    "social-cli": "terminal-cli",

    # --- browser-automation ---
    "browser-ml-in-js": "browser-automation",
    "playwright": "browser-automation",
    "playwright-interactive": "browser-automation",
    "screenshot": "browser-automation",
    "webapp-testing": "browser-automation",

    # --- multimodal (document/image processing) ---
    "docx": "multimodal",
    "pdf": "multimodal",
    "pdf-summarizer": "multimodal",
    "pdf-vision-extractor": "multimodal",
    "pptx": "multimodal",
    "slides": "multimodal",
    "spreadsheet": "multimodal",
    "xlsx": "multimodal",

    # --- image-generation ---
    "algorithmic-art": "image-generation",
    "canvas-design": "image-generation",
    "imagegen": "image-generation",

    # --- video-generation ---
    "remotion": "video-generation",

    # --- audio-speech ---
    "speech": "audio-speech",
    "transcribe": "audio-speech",

    # --- gpu-kernels ---
    "metal-kernel": "gpu-kernels",

    # --- text-to-sql ---
    "clickhouse-best-practices": "text-to-sql",
    "db-migrations": "text-to-sql",
    "sql-query-helper": "text-to-sql",

    # --- chat-uikits ---
    "chat-sdk": "chat-uikits",
    "chatgpt-apps": "chat-uikits",
    "discord": "chat-uikits",
    "slack": "chat-uikits",
    "slack-gif-creator": "chat-uikits",

    # --- documentation ---
    "adr-skill": "documentation",
    "applying-brand-guidelines": "documentation",
    "brand-guidelines": "documentation",
    "changelog-writing": "documentation",
    "doc": "documentation",
    "doc-coauthoring": "documentation",
    "docs-changelog": "documentation",
    "docstring": "documentation",
    "document-public-apis": "documentation",
    "guidelines": "documentation",
    "internal-comms": "documentation",
    "karpathy-guidelines": "documentation",
    "microcopy": "documentation",
    "notion": "documentation",
    "notion-knowledge-capture": "documentation",
    "notion-meeting-intelligence": "documentation",
    "notion-research-documentation": "documentation",
    "notion-spec-to-implementation": "documentation",
    "obsidian": "documentation",
    "visual-identity": "documentation",
    "cookbook-audit": "documentation",

    # --- translation ---
    "book-translation": "translation",
    "i18n": "translation",

    # --- finance ---
    "add-model-price": "finance",
    "analyze-cloud-costs": "finance",
    "analyzing-financial-statements": "finance",
    "creating-financial-models": "finance",
    "discount-review": "finance",
    "llm-pricing-file-update": "finance",

    # --- case-studies ---
    "ai-news": "case-studies",
    "huggingface-paper-publisher": "case-studies",
    "huggingface-papers": "case-studies",
    "weekly-production-review": "case-studies",
    "weekly-user-topics-digest": "case-studies",

    # --- official-cookbooks ---
    "openai-docs": "official-cookbooks",

    # --- prompt-libraries ---
    "compaction-prompts": "prompt-libraries",
    "define-goal": "prompt-libraries",
    "goal-definition": "prompt-libraries",
    "prompt": "prompt-libraries",
    "prompt-lookup": "prompt-libraries",

    # --- code-assistants ---
    "aspnet-core": "code-assistants",
    "drizzle": "code-assistants",
    "figma": "code-assistants",
    "figma-code-connect-components": "code-assistants",
    "figma-create-design-system-rules": "code-assistants",
    "figma-create-new-file": "code-assistants",
    "figma-generate-design": "code-assistants",
    "figma-generate-library": "code-assistants",
    "figma-implement-design": "code-assistants",
    "figma-use": "code-assistants",
    "frontend-browser-review": "code-assistants",
    "frontend-design": "code-assistants",
    "frontend-large-feature-architecture": "code-assistants",
    "frontend-skill": "code-assistants",
    "frontend-visual-design": "code-assistants",
    "migrate-to-codex": "code-assistants",
    "react": "code-assistants",
    "react-router-search-params": "code-assistants",
    "search-params": "code-assistants",
    "spa-routes": "code-assistants",
    "storybook": "code-assistants",
    "theme-factory": "code-assistants",
    "transformers-js": "code-assistants",
    "trpc-router": "code-assistants",
    "turborepo": "code-assistants",
    "typescript": "code-assistants",
    "upstash-workflow": "code-assistants",
    "use-ai-sdk": "code-assistants",
    "vercel-composition-patterns": "code-assistants",
    "vercel-react-best-practices": "code-assistants",
    "web-artifacts-builder": "code-assistants",
    "widget-generator": "code-assistants",
    "winui-app": "code-assistants",
    "write-frontend-tests": "code-assistants",
    "zustand": "code-assistants",

    # --- applications ---
    "1password": "applications",
    "app": "applications",
    "at-dispatch-v2": "applications",
    "desktop": "applications",
    "gog": "applications",
    "hatch-pet": "applications",
    "huggingface-best": "applications",
    "imsg": "applications",
    "island-rescue": "applications",
    "spotify-player": "applications",
    "yelp-search": "applications",
    "agent-signal": "applications",

    # --- dev-tools (everything else that's genuinely a dev tool) ---
    "add-function-examples": "dev-tools",
    "add-or-fix-type-checking": "dev-tools",
    "add-provider-doc": "dev-tools",
    "add-provider-package": "dev-tools",
    "add-setting-env": "dev-tools",
    "add-uint-support": "dev-tools",
    "aoti-debug": "dev-tools",
    "backend-dev-guidelines": "dev-tools",
    "capture-api-response-test-fixture": "dev-tools",
    "code-review": "dev-tools",
    "code-reviewer": "dev-tools",
    "commit-message-writer": "dev-tools",
    "debug-package": "dev-tools",
    "distributed-triage": "dev-tools",
    "fix-issue": "dev-tools",
    "gh-address-comments": "dev-tools",
    "gh-fix-ci": "dev-tools",
    "git-workflow": "dev-tools",
    "github": "dev-tools",
    "github-pr-inline-reply": "dev-tools",
    "hotkey": "dev-tools",
    "invalid-name": "dev-tools",
    "jupyter-notebook": "dev-tools",
    "linear": "dev-tools",
    "linear-bug-triage": "dev-tools",
    "lint": "dev-tools",
    "list-npm-package-content": "dev-tools",
    "local-testing": "dev-tools",
    "major-version-mode": "dev-tools",
    "minimal-skill": "dev-tools",
    "morph-warpgrep": "dev-tools",
    "open-pr": "dev-tools",
    "ownership-bus-factor": "dev-tools",
    "plugin-creator": "dev-tools",
    "pnpm-upgrade-package": "dev-tools",
    "pr": "dev-tools",
    "pr-address": "dev-tools",
    "pr-polish": "dev-tools",
    "pr-review": "dev-tools",
    "pr-test": "dev-tools",
    "pr-yeet": "dev-tools",
    "project-overview": "dev-tools",
    "pt2-bug-basher": "dev-tools",
    "pyrefly-type-coverage": "dev-tools",
    "rebuild": "dev-tools",
    "review-checklist": "dev-tools",
    "review-standards": "dev-tools",
    "scrub-issue": "dev-tools",
    "seed-test-data": "dev-tools",
    "setup-repo": "dev-tools",
    "skill": "dev-tools",
    "skill-creator": "dev-tools",
    "skill-development": "dev-tools",
    "skill-installer": "dev-tools",
    "skill-lookup": "dev-tools",
    "skill-writer": "dev-tools",
    "skills-audit": "dev-tools",
    "standards-check": "dev-tools",
    "store-data-structures": "dev-tools",
    "system-info": "dev-tools",
    "task": "dev-tools",
    "template": "dev-tools",
    "test-generator": "dev-tools",
    "token-skill": "dev-tools",
    "triaging-issues": "dev-tools",
    "valid-skill": "dev-tools",
    "version-release": "dev-tools",
    "worktree": "dev-tools",
    "yeet": "dev-tools",
}


def update_category(path: Path, new_cat: str) -> bool:
    """Update the category: field in a SKILL.md frontmatter."""
    text = path.read_text(encoding="utf-8")
    # Match `category: <value>` in the frontmatter (before the closing ---)
    m = re.match(r'^(---\s*\n)(.*?)(\n---\s*\n)', text, re.DOTALL)
    if not m:
        return False
    fm = m.group(2)
    new_fm = re.sub(
        r'^category:\s*.*$',
        f'category: {new_cat}',
        fm,
        count=1,
        flags=re.MULTILINE,
    )
    new_text = text[:m.start()] + m.group(1) + new_fm + m.group(3) + text[m.end():]
    if new_text != text:
        path.write_text(new_text, encoding="utf-8")
        return True
    return False


def main() -> int:
    changed = 0
    skipped = 0
    for slug, new_cat in sorted(CATEGORY_MAP.items()):
        skill_md = SKILLS_DIR / slug / "SKILL.md"
        if not skill_md.exists():
            print(f"  SKIP  {slug}: SKILL.md not found", file=sys.stderr)
            skipped += 1
            continue
        if update_category(skill_md, new_cat):
            print(f"  OK    {slug:40s} → {new_cat}")
            changed += 1
        else:
            print(f"  SAME  {slug:40s} (already {new_cat})")

    # Check for skills not in the map
    all_slugs = {p.parent.name for p in SKILLS_DIR.glob("*/SKILL.md")}
    unmapped = all_slugs - set(CATEGORY_MAP.keys())
    if unmapped:
        print(f"\nWARNING: {len(unmapped)} skills not in map:", file=sys.stderr)
        for s in sorted(unmapped):
            print(f"  {s}", file=sys.stderr)

    print(f"\n== {changed} changed / {skipped} skipped / {len(CATEGORY_MAP)} total ==")
    return 0


if __name__ == "__main__":
    sys.exit(main())
