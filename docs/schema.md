# SKILL.md schema

每个技能是一份 Markdown，开头是 YAML frontmatter，后面是
正文。`validate-skill.py` 跑这套规则，不通过就 CI 红。

## frontmatter 字段

| 字段 | 必须 | 类型 | 说明 |
|---|---|---|---|
| `slug` | ✅ | string | kebab-case，跟目录名一致，全 `skills/` 唯一 |
| `name` | ✅ | string | 显示名，sentence case |
| `name_zh` |  | string | 中文名，没有就空着 |
| `version` | ✅ | string | semver `MAJOR.MINOR.PATCH` |
| `description` | ✅ | string | 一句话，干什么、给谁用 |
| `description_zh` |  | string | 中文一句话 |
| `category` | ✅ | string | 49 个分类之一，看 `external-index/skills.yaml` |
| `tags` | ✅ | string[] | 2-5 个小写标签 |
| `platforms` |  | string[] | 平台白名单。不写 = 全平台通用 |
| `inputs` | ✅ | object[] | I/O 契约，下面有例子 |
| `output` | ✅ | object | 输出形状 |
| `source` |  | object | 抓来的技能要标来源 |
| `needs_review` |  | bool | 标了说明是 `extend-skill.py` 猜的，要人看一眼 |
| `author` | ✅ | string | GitHub handle，或 `Name <email>` |
| `license` | ✅ | string | SPDX id |
| `created` | ✅ | date | `YYYY-MM-DD` |
| `updated` | ✅ | date | `YYYY-MM-DD` |

## inputs

声明这个技能要什么。每个字段一项：

```yaml
inputs:
  - name: pdf_path
    type: path
    required: true
    description: 本地 PDF 路径，≤ 50 页
  - name: audience
    type: enum
    required: false
    values: [engineer, pm, exec]
    default: pm
    description: 摘要给谁看
  - name: length
    type: integer
    required: false
    default: 5
    constraints:
      min: 3
      max: 10
    description: 要几条 bullet
```

`type` 可以是：

- 标量：`string` `integer` `number` `boolean`
- 路径类：`path` `url` `email`
- 集合：`enum`（要带 `values:`）、`array`（要带 `items:`）

如果一个技能就是接一段自然语言问题，那就老实写一个 `question` 字段，**别**故意拆成 5 个假装结构化。

## output

```yaml
output:
  format: markdown       # markdown | json | text | code
  schema:                # 可选，json/code 输出最好带
    type: object
    required: [summary, tags]
    properties:
      summary: { type: array, items: { type: string } }
      tags: { type: array, items: { type: string } }
  description: |
    `## Summary` 下面 N 条 bullet，然后一行 `## Tags:`。
```

纯文本输出就只写 `format: markdown`，别装。

## source

从外面抓来的技能必须标：

```yaml
source:
  url: https://github.com/anthropics/anthropic-skills/tree/main/skills/pdf
  fetched_at: 2026-06-10
  commit: a1b2c3d4
  license: MIT
  original_path: skills/pdf/SKILL.md
```

手写的可以写 `{ url: "this-repo/AI-SKILL", license: "MIT" }` 或者直接不写。

## 平台中立

这是这套 schema 最想强调的事。

**默认所有技能在所有 agent 上都能跑。** Claude / Codex / Cursor / Continue / 任何能读 Markdown 的运行时都行。

只有以下情况才标 `platforms`：

- 技能必须用 Claude 的 `tool_use` 格式
- 技能必须用 OpenAI 的 function calling
- 技能必须用 Codex CLI 的某个特定行为
- 技能用了 Cursor 的 `@`-mention 之类的 IDE 语法

标了之后，**那一段正文开头**还要写：

```markdown
> **Claude-only** — 下面这段假设 Claude 的 tool_use 格式
```

一行就行。别整段都圈起来。

技能**不**应该调任何 vendor SDK。HTTP 用 `requests`，JSON 用
`json` 标准库，别 `import openai` `import anthropic` 那种东西。

## 正文结构

frontmatter 之后，body 必须是这 4 个 H1 段，按顺序：

1. `# When to use` —— 一段话，写具体的场景
2. `# Inputs` —— 人的语言再写一遍（frontmatter 是给机器看的）
3. `# Output` —— 模型要返回什么
4. `# Prompt` —— 实际 prompt，fenced code block

可选第 5 段：

5. `# When NOT to use` —— 边界、反例、常见误用。**写得
   越具体越好**。"可能不适用" 这种废话不要写

可选第 6 段：

6. `# Example` —— 完整的 input → output。强烈建议加

## 一个最小例子

```markdown
---
slug: pdf-summarizer
name: PDF Summarizer
name_zh: PDF 摘要
version: 0.1.0
description: 给 PDF 出 N 条 bullet 摘要，分受众。
description_zh: 给 PDF 出 N 条 bullet 摘要。
category: document-processing
tags: [pdf, summarization, document]
inputs:
  - name: pdf_path
    type: path
    required: true
    description: 本地 PDF 路径
  - name: audience
    type: enum
    required: false
    values: [engineer, pm, exec]
    default: pm
output:
  format: markdown
  description: |
    `## Summary` 下面 N 条 bullet，N 由调用方指定。
author: badhope
license: MIT
created: 2026-06-10
updated: 2026-06-10
---

# When to use

读者想要一份 PDF 的简明摘要。受众明确（engineer / pm / exec），
长度明确（3-10 条 bullet）。**不**用于：短文档、逐字
引用、需要全文检索的场景。

# Inputs

PDF 路径、受众、bullet 数。受众决定口吻和术语密度，
bullet 数决定输出长度。

# Output

Markdown 文本：

- `## Summary` 标题，下面正好 N 条 bullet
- `## Tags` 标题，一行逗号分隔的关键词

# Prompt

\`\`\`prompt
You are a senior analyst writing for the requested audience.

Audience voice:
- engineer: precise, technical, uses domain terms
- pm: outcomes-first, no jargon, quantifies where possible
- exec: 1-2 sentences per bullet, decisions and risks only

Process:
1. Read cover, abstract, intro, conclusion, key tables/figures
2. Identify the 1-3 findings the audience needs to act on
3. Distill to exactly N bullets
4. Order by importance, not by appearance

Output format:

## Summary
1. <bullet>
2. <bullet>
…

## Tags
comma, separated, keywords
\`\`\`

# When NOT to use

- **PDF 不到 2 页** —— 直接看就行了，跑这个浪费
- **需要原文逐字** —— 用 `pdf-extractor` 那个
- **要图表识别 / OCR** —— 这里是纯文本
- **音频/视频转录后的"PDF"** —— 那是另一种东西

# Example

**Input:**

\`\`\`
pdf_path: ./q2-roadmap.pdf
audience: exec
length: 4
\`\`\`

**Output:**

\`\`\`markdown
## Summary
1. Q2 主力是 federated-search 重写，比 v1 快 3 倍，
   集群成本砍半，同时下线 v1 search API
2. 招聘延迟是最大风险 —— 4 个 HC 到 half 还有 2 个空着
3. 董事会问 Anthropic vs. OpenAI 用哪家，
   结论是继续多 vendor 混用，AWS Bedrock 当主
4. ARR 实际比 plan 高 8%，主要拉动力是新 enterprise 套餐

## Tags
search, hiring, vendor, arr
\`\`\`
```

## 版本号规则

- prompt 改了导致输出**不一样** —— 升版本号
- 只是改了几个字、修了 typo —— 不升版本号，但 `updated`
  字段要改
- 输入或输出 schema 变了 —— 升 major，`CHANGELOG.md`
  写一笔

## 字段该写多少字

凭直觉，不教条：

- `description` 一句话，**不超过 100 字**
- `# When to use` 1-2 段
- `# Inputs` 跟 `# Output` 看复杂程度，1-3 段
- `# Prompt` 这里是重头，写详细点没关系，30-100 行都行
- `# When NOT to use` 至少 3 条，越具体越好
- `# Example` 至少 1 个，多了不限

`description` 写 200 字那种"comprehensive
solution for..."全是水。
