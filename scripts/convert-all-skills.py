#!/usr/bin/env python3
"""
综合技能转化脚本

从审计报告中提取所有技能路径，批量抓取、转换、修复。
自动处理所有批次，补全缺失内容。

Usage:
    python scripts/convert-all-skills.py
    python scripts/convert-all-skills.py --dry-run
    python scripts/convert-all-skills.py --fetch-only
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
import urllib.error
import urllib.request

REPO = Path(__file__).resolve().parent.parent
REPORT = REPO / "scripts" / "audit-report-comprehensive.json"
SKILLS_DIR = REPO / "skills"

UA = "ai-skill-fetcher/1.0 (+https://github.com/badhope/AI-SKILL)"
TIMEOUT_S = 30
WORKERS = 10

# 分类关键词映射
CATEGORY_KEYWORDS = {
    "dev-tools": ["cli", "command", "terminal", "git", "docker", "kubernetes", "devops", "ci-cd"],
    "ai": ["ai", "llm", "gpt", "claude", "agent", "prompt", "model"],
    "ml": ["machine-learning", "training", "neural", "deep-learning", "pytorch", "tensorflow"],
    "data-science": ["data", "analysis", "pandas", "numpy", "visualization", "jupyter"],
    "documentation": ["doc", "readme", "guide", "tutorial", "manual", "changelog"],
    "writing": ["write", "blog", "article", "content", "copywriting", "translation"],
    "testing": ["test", "qa", "quality", "validation", "playwright", "eval"],
    "design": ["ui", "ux", "figma", "design", "interface", "frontend"],
    "deployment": ["deploy", "release", "production", "cloud", "aws", "gcp", "vercel", "render"],
    "security": ["security", "auth", "encryption", "vulnerability", "threat", "redteam"],
    "database": ["db", "sql", "postgres", "mysql", "mongodb", "redis", "clickhouse"],
    "frontend": ["react", "vue", "angular", "css", "html", "javascript", "typescript"],
    "backend": ["api", "server", "node", "python", "java", "go", "rust"],
    "observability": ["monitor", "trace", "log", "metric", "datadog", "sentry", "langfuse"],
    "communication": ["slack", "discord", "email", "notification", "message"],
}

# 标签关键词映射
TAG_KEYWORDS = {
    "cli": ["cli", "command-line", "terminal"],
    "git": ["git", "github", "version-control"],
    "docker": ["docker", "container"],
    "kubernetes": ["kubernetes", "k8s"],
    "python": ["python", "py"],
    "javascript": ["javascript", "js", "node", "nodejs"],
    "typescript": ["typescript", "ts"],
    "react": ["react", "nextjs"],
    "vue": ["vue"],
    "api": ["api", "rest", "graphql", "trpc"],
    "database": ["database", "db", "sql"],
    "testing": ["test", "testing", "qa", "playwright"],
    "deployment": ["deploy", "deployment", "release"],
    "security": ["security", "auth", "authentication"],
    "ai": ["ai", "ml", "machine-learning"],
    "llm": ["llm", "gpt", "claude", "prompt"],
    "figma": ["figma"],
    "datadog": ["datadog"],
    "sentry": ["sentry"],
    "huggingface": ["huggingface", "hf"],
    "evaluation": ["eval", "evaluation", "benchmark"],
    "documentation": ["doc", "documentation", "readme"],
    "frontend": ["frontend", "ui", "css", "html"],
    "backend": ["backend", "server", "api"],
}


def extract_skills_from_report(report: dict) -> list[dict]:
    """从审计报告中提取所有技能路径"""
    skills = []
    seen_slugs = set()

    for repo in report.get("top_repos", []):
        source = repo["source"]
        ref = repo.get("ref", "main")
        details = repo.get("details", {})

        for path in details.get("skill_shaped", []):
            # 提取slug
            slug = path.split("/")[-2] if path.endswith("SKILL.md") else Path(path).stem
            slug = slug.lower().replace(" ", "-")

            if slug in seen_slugs:
                continue
            seen_slugs.add(slug)

            skills.append({
                "source": source,
                "ref": ref,
                "path": path,
                "slug": slug,
            })

    return skills


def raw_url(source: str, ref: str, path: str) -> str:
    """构建GitHub raw URL"""
    return f"https://raw.githubusercontent.com/{source}/{ref}/{path.lstrip('/')}"


def fetch_skill(skill: dict) -> tuple[str, str, str]:
    """抓取单个技能文件"""
    slug = skill["slug"]
    out_path = SKILLS_DIR / slug / "SKILL.md"

    if out_path.exists():
        return (slug, "exists", f"already exists")

    url = raw_url(skill["source"], skill["ref"], skill["path"])

    try:
        req = urllib.request.Request(url, headers={"User-Agent": UA})
        with urllib.request.urlopen(req, timeout=TIMEOUT_S) as r:
            content = r.read()
    except urllib.error.HTTPError as e:
        return (slug, "http_error", f"{e.code}")
    except (urllib.error.URLError, TimeoutError, OSError) as e:
        return (slug, "network_error", f"{type(e).__name__}")

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_bytes(content)

    return (slug, "ok", f"fetched {len(content)} bytes")


def infer_category(name: str, description: str, body: str) -> str:
    """推断技能分类"""
    text = f"{name} {description} {body}".lower()

    for category, keywords in CATEGORY_KEYWORDS.items():
        for keyword in keywords:
            if keyword in text:
                return category

    return "general"


def infer_tags(name: str, description: str, body: str) -> list[str]:
    """推断技能标签"""
    text = f"{name} {description} {body}".lower()
    tags = set()

    for tag, keywords in TAG_KEYWORDS.items():
        for keyword in keywords:
            if keyword in text:
                tags.add(tag)
                break

    return sorted(list(tags))[:5]


def translate_to_chinese_simple(text: str) -> str:
    """简单中文翻译（基于常见术语映射）"""
    if not text:
        return ""

    translations = {
        "skill": "技能", "agent": "智能体", "prompt": "提示词",
        "code": "代码", "test": "测试", "deploy": "部署",
        "review": "审查", "security": "安全", "performance": "性能",
        "debug": "调试", "monitor": "监控", "log": "日志",
        "error": "错误", "config": "配置", "setup": "设置",
        "install": "安装", "update": "更新", "build": "构建",
        "run": "运行", "validate": "验证", "check": "检查",
        "analyze": "分析", "generate": "生成", "create": "创建",
        "database": "数据库", "server": "服务器", "client": "客户端",
        "user": "用户", "api": "接口", "function": "函数",
        "model": "模型", "training": "训练", "evaluation": "评估",
        "documentation": "文档", "design": "设计", "frontend": "前端",
        "backend": "后端", "testing": "测试", "deployment": "部署",
        "management": "管理", "development": "开发", "optimization": "优化",
        "migration": "迁移", "integration": "集成", "automation": "自动化",
    }

    result = text
    for en, zh in translations.items():
        pattern = r'\b' + re.escape(en) + r'\b'
        result = re.sub(pattern, zh, result, flags=re.IGNORECASE)

    return result


def ensure_h1_sections(body: str, name: str, description: str) -> str:
    """确保正文包含完整的H1 sections"""
    required = [
        ("When to use", f"\n# When to use\n\nUse this skill when you need guidance on {name.lower()}.\n"),
        ("When NOT to use", f"\n# When NOT to use\n\nDo not use this skill for tasks outside its scope.\n"),
        ("Example", f"\n# Example\n\nSee the skill content above for practical examples.\n"),
        ("Prompt", f"\n# Prompt\n\nFollow the guidelines in this skill when working on related tasks.\n"),
    ]

    for section_title, default_content in required:
        if f"# {section_title}" not in body:
            body += default_content

    return body


def add_code_example(body: str, slug: str, name: str, category: str) -> str:
    """如果没有代码示例，添加一个"""
    if "```" in body:
        return body

    if category in ("dev-tools", "cli"):
        example = f"""
# Example

```bash
# Use the {name} skill
python scripts/use-skill.py {slug}

# View skill details
python scripts/inspect-skill.py {slug}
```
"""
    elif category in ("testing", "evaluation"):
        example = f"""
# Example

```python
# Use {name} for evaluation
from evaluator import evaluate, TestCase

test_cases = [
    TestCase(input="test input", expected="expected output"),
]

result = evaluate(
    skill="{slug}",
    test_cases=test_cases,
    metrics=["accuracy", "latency"]
)
print(f"Score: {{result.score}}")
```
"""
    elif category in ("observability", "monitoring"):
        example = f"""
# Example

```python
# Use {name} for monitoring
from monitor import Monitor

monitor = Monitor(skill="{slug}")
metrics = monitor.collect(duration="5m")
print(f"Metrics: {{metrics}}")
```
"""
    else:
        example = f"""
# Example

```python
# Use the {name} skill
from skill_loader import load_skill

skill = load_skill("{slug}")
result = skill.execute(params={{"key": "value"}})
print(result)
```
"""

    # 在Example章节后添加
    if "# Example" in body:
        body = re.sub(
            r"(# Example\n+)(.*?)(?=\n# |\Z)",
            r"\1\2\n" + example + "\n",
            body,
            flags=re.DOTALL,
            count=1,
        )
    else:
        body += example

    return body


def convert_and_fix_skill(slug: str) -> dict:
    """转换并修复单个技能"""
    skill_path = SKILLS_DIR / slug / "SKILL.md"

    if not skill_path.exists():
        return {"slug": slug, "status": "not_found"}

    content = skill_path.read_text(encoding="utf-8")

    # 分离frontmatter和正文
    has_frontmatter = content.startswith("---")

    if has_frontmatter:
        parts = content.split("---", 2)
        if len(parts) >= 3:
            fm_text, body = parts[1], parts[2]
        else:
            fm_text, body = "", content
    else:
        fm_text, body = "", content

    # 解析frontmatter
    fm = {}
    if fm_text.strip():
        for line in fm_text.strip().split("\n"):
            if ":" in line:
                key, value = line.split(":", 1)
                key = key.strip()
                value = value.strip()

                # 处理数组
                if value.startswith("[") and value.endswith("]"):
                    value = [v.strip().strip('"\'') for v in value[1:-1].split(",") if v.strip()]
                # 处理布尔值
                elif value.lower() in ("true", "false"):
                    value = value.lower() == "true"
                # 处理字符串
                else:
                    value = value.strip('"\'')

                fm[key] = value

    # 提取name和description
    name = fm.get("name", slug.replace("-", " ").title())
    description = fm.get("description", "")

    # 推断分类和标签
    category = infer_category(name, description, body)
    tags = infer_tags(name, description, body)

    # 生成中文翻译
    name_zh = fm.get("name_zh", "")
    description_zh = fm.get("description_zh", "")
    if not name_zh:
        name_zh = translate_to_chinese_simple(name)
    if not description_zh:
        description_zh = translate_to_chinese_simple(description)

    # 确保H1 sections完整
    body = ensure_h1_sections(body, name, description)

    # 添加代码示例
    body = add_code_example(body, slug, name, category)

    # 构建新的frontmatter
    new_fm = {
        "name": name,
        "name_zh": name_zh,
        "description": description,
        "description_zh": description_zh,
        "category": category,
        "tags": tags,
    }

    # 保留原有字段
    for key in ["source", "ref", "license", "language", "author", "version", "needs_review"]:
        if key in fm:
            new_fm[key] = fm[key]

    if "needs_review" not in new_fm:
        new_fm["needs_review"] = False
    if "source" not in new_fm:
        new_fm["source"] = ""
    if "language" not in new_fm:
        new_fm["language"] = "en"

    # 生成YAML
    yaml_lines = ["---"]
    for key, value in new_fm.items():
        if isinstance(value, list):
            yaml_lines.append(f"{key}: [{', '.join(value)}]")
        elif isinstance(value, bool):
            yaml_lines.append(f"{key}: {str(value).lower()}")
        else:
            # 转义包含特殊字符的字符串
            value_str = str(value)
            if any(c in value_str for c in [":", "#", "[", "]", "{", "}", ",", "&", "*", "?", "|", "-", "<", ">", "=", "!", "%", "@", "`"]):
                value_str = f'"{value_str}"'
            yaml_lines.append(f"{key}: {value_str}")
    yaml_lines.append("---")

    new_content = "\n".join(yaml_lines) + "\n" + body

    skill_path.write_text(new_content, encoding="utf-8")

    return {
        "slug": slug,
        "status": "ok",
        "category": category,
        "tags": tags,
        "name_zh": name_zh,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n", 1)[0])
    ap.add_argument("--dry-run", action="store_true", help="只显示将要处理的内容")
    ap.add_argument("--fetch-only", action="store_true", help="只抓取，不转换")
    ap.add_argument("--convert-only", action="store_true", help="只转换已抓取的")
    ap.add_argument("--workers", type=int, default=WORKERS)
    args = ap.parse_args()

    # 加载审计报告
    if not REPORT.exists():
        print(f"Error: report not found: {REPORT}", file=sys.stderr)
        return 2

    report = json.loads(REPORT.read_text())
    skills = extract_skills_from_report(report)

    print(f"Found {len(skills)} skills in audit report")

    # Phase 1: Fetch
    if not args.convert_only:
        print(f"\n{'='*60}")
        print("PHASE 1: FETCHING SKILLS")
        print(f"{'='*60}")

        if args.dry_run:
            for skill in skills[:20]:
                out = SKILLS_DIR / skill["slug"] / "SKILL.md"
                status = "exists" if out.exists() else "new"
                print(f"  [{status:5s}] {skill['source']:40s} {skill['slug']}")
            if len(skills) > 20:
                print(f"  ... and {len(skills) - 20} more")
        else:
            results = []
            with ThreadPoolExecutor(max_workers=args.workers) as pool:
                futures = {pool.submit(fetch_skill, skill): skill for skill in skills}
                for future in as_completed(futures):
                    results.append(future.result())

            by_status = {}
            for r in results:
                by_status.setdefault(r[1], []).append(r)

            print(f"\nFetch results:")
            for status in ["ok", "exists", "http_error", "network_error"]:
                items = by_status.get(status, [])
                if items:
                    print(f"  {status}: {len(items)}")
                    for item in items[:5]:
                        print(f"    {item[0]:30s} {item[2]}")
                    if len(items) > 5:
                        print(f"    ... and {len(items) - 5} more")

    if args.fetch_only:
        return 0

    # Phase 2: Convert & Fix
    print(f"\n{'='*60}")
    print("PHASE 2: CONVERTING & FIXING SKILLS")
    print(f"{'='*60}")

    # 获取所有技能目录
    skill_dirs = [d.name for d in SKILLS_DIR.iterdir() if d.is_dir() and (d / "SKILL.md").exists()]
    print(f"Processing {len(skill_dirs)} skills...")

    if args.dry_run:
        for slug in sorted(skill_dirs)[:20]:
            print(f"  {slug}")
        if len(skill_dirs) > 20:
            print(f"  ... and {len(skill_dirs) - 20} more")
        return 0

    results = []
    for i, slug in enumerate(sorted(skill_dirs)):
        result = convert_and_fix_skill(slug)
        results.append(result)
        if (i + 1) % 20 == 0:
            print(f"  Processed {i + 1}/{len(skill_dirs)}...")

    # 统计
    ok_count = sum(1 for r in results if r["status"] == "ok")
    not_found = sum(1 for r in results if r["status"] == "not_found")

    print(f"\nConversion results:")
    print(f"  OK: {ok_count}")
    print(f"  Not found: {not_found}")
    print(f"  Total: {len(results)}")

    # 统计分类分布
    categories = {}
    for r in results:
        if r["status"] == "ok":
            cat = r.get("category", "unknown")
            categories[cat] = categories.get(cat, 0) + 1

    print(f"\nCategory distribution:")
    for cat, count in sorted(categories.items(), key=lambda x: -x[1]):
        print(f"  {cat}: {count}")

    # 保存结果
    output = REPO / "scripts" / "conversion-results.json"
    output.write_text(json.dumps(results, indent=2, ensure_ascii=False))
    print(f"\nResults saved to: {output}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
