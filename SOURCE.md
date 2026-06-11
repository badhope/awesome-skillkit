# SOURCE — 上游出处与本地原创声明

## 现状

本仓库目前收录 **35 条技能**，分两类：

### 手写（5 条，无 `source:` 字段）

- `pdf-summarizer`
- `code-reviewer`
- `test-generator`
- `sql-query-helper`
- `commit-message-writer`

作者就是本仓库，不存在"上游"。

### Claude-only 平台示例（1 条）

- `pdf-vision-extractor` — `platforms: [claude]`

用来端到端验证平台标记 / chip 渲染流程。

### 从主流大厂 / 优秀项目抓取并重新模板化（29 条）

每条都标了 `source:` 字段，写明原作者、仓库、ref、commit。
**frontmatter 的 `author` 用 `"<Vendor> (downstream pack: badhope)"`
的形式** —— 既致谢上游，也标明本仓库是下游打包。

按上游仓库分组的索引：

#### [confident-ai/deepeval](https://github.com/confident-ai/deepeval) — 3 条

| Skill | 上游路径 | 改造要点 |
|---|---|---|
| `deepeval-otel` | `skills/deepeval-otel/SKILL.md` | 通用化：把"使用 deepeval"的前提去掉，写成"任何 OTLP SDK"都能用 |
| `deepeval-tracing` | `skills/deepeval-tracing/SKILL.md` | 保留框架集成列表（LangGraph / LlamaIndex / OpenAI Agents SDK） |
| `deepeval-eval-suite` | `skills/deepeval/SKILL.md` | 把整段 "deep eval workflow" 浓缩成"建一个 pytest eval 套件" |

#### [promptfoo/promptfoo](https://github.com/promptfoo/promptfoo) — 3 条

| Skill | 上游路径 | 改造要点 |
|---|---|---|
| `promptfoo-evals` | `.claude/skills/promptfoo-evals/SKILL.md` | 通用化：去 `claude` 目录依赖 |
| `promptfoo-redteam` | `.claude/skills/redteam-plugin-development/SKILL.md` | 提取 tag 协议（`<UserQuery>` / `<purpose>` / `<Output>` / `<AllowedEntities>`）和 rubric 模板 |
| `react-router-search-params` | `.claude/skills/search-params/SKILL.md` | 通用化：去 promptfoo 内部 hooks，写成"任何 `useSearchParamState` 实现" |

#### [anthropics/skills](https://github.com/anthropics/skills) — 5 条

| Skill | 上游路径 | 改造要点 |
|---|---|---|
| `mcp-builder` | `skills/mcp-builder/SKILL.md` | 几乎原样，标了 "Anthropic (downstream pack: badhope)" |
| `webapp-testing` | `skills/webapp-testing/SKILL.md` | 几乎原样 |
| `skill-creator` | `skills/skill-creator/SKILL.md` | 通用化：去 claude 专有 `eval-viewer/generate_review.py` 引用 |
| `doc-coauthoring` | `skills/doc-coauthoring/SKILL.md` | 通用化：去 "Claude" 专有，保留三阶段（Context / Refine / Reader Test） |
| `internal-comms` | `skills/internal-comms/SKILL.md` | 通用化：把 7 种 comm 类型的结构 / 语气 / 收集清单都铺开 |

#### [langfuse/langfuse](https://github.com/langfuse/langfuse) — 8 条

| Skill | 上游路径 | 改造要点 |
|---|---|---|
| `llm-pricing-file-update` | `.agents/skills/add-model-price/SKILL.md` | 去掉 Langfuse 内部路径，写成"任何 per-token 价目 JSON" |
| `clickhouse-best-practices` | `.agents/skills/clickhouse-best-practices/SKILL.md` | 保留 ClickHouse Inc 出品的 28 条核心规则，删 Langfuse 内部 `.ts` 引用；author 标"ClickHouse Inc + Langfuse" |
| `frontend-large-feature-architecture` | `.agents/skills/frontend-large-feature-architecture/SKILL.md` | 通用化：去 Langfuse `web/` 路径，写成"任何 controller + presentational 拆分" |
| `security-review` | `.agents/skills/security-review/SKILL.md` | 通用化：catalog 结构保留，topic references 改成"加载对应 reference" |
| `storybook` | `.agents/skills/storybook/SKILL.md` | 通用化：去 Langfuse tRPC API 提到"任何私有 API"，保留 CSF Next + 状态命名规则 |
| `pnpm-upgrade-package` | `.agents/skills/pnpm-upgrade-package/SKILL.md` | 通用化：去 Langfuse 路径，保留 release-age / override-prove / dedupe-churn 三条核心 |
| `turborepo` | `.agents/skills/turborepo/SKILL.md` | 通用化：去 Langfuse-specific 的 references 路径，保留 8 个 anti-patterns |
| `code-review` | `.agents/skills/code-review/SKILL.md` | 通用化：defer 模式保留，catalog 用占位符 |

#### [openai/openai-cookbook](https://github.com/openai/openai-cookbook) — 1 条

| Skill | 上游路径 | 改造要点 |
|---|---|---|
| `realtime-eval-bootstrap` | `examples/evals/realtime_evals/skills/bootstrap-realtime-eval/SKILL.md` | 去掉 cookbook 内部路径，harness 三个选项（crawl / walk / run）保留 |

#### [openai/skills](https://github.com/openai/skills) — 6 条

| Skill | 上游路径 | 改造要点 |
|---|---|---|
| `goal-definition` | `skills/.curated/define-goal/SKILL.md` | 通用化：去掉 Codex `get_goal` / `create_goal` 工具调用，改成"REWRITE" / "GOAL" 两形状输出 |
| `cli-builder` | `skills/.curated/cli-creator/SKILL.md` | 通用化：去掉 Codex `~` 路径建议（"codex code-path"），改成通用的"~/.local/bin"等 |
| `threat-modeling` | `skills/.curated/security-threat-model/SKILL.md` | 几乎原样，本来就是仓库级的 AppSec 流程 |
| `secure-code-by-language` | `skills/.curated/security-best-practices/SKILL.md` | 几乎原样，触发条件是 explicit-only |
| `ownership-bus-factor` | `skills/.curated/security-ownership-map/SKILL.md` | 通用化：去掉 `python skills/skills/...` 路径，脚本接口通用化 |
| `pr-yeet` | `skills/.curated/yeet/SKILL.md` | 几乎原样，本就是 GitHub + `gh` 的通用流 |

#### [letta-ai/skills](https://github.com/letta-ai/skills) — 1 条

| Skill | 上游路径 | 改造要点 |
|---|---|---|
| `frontend-visual-design` | `tools/frontend-skill/SKILL.md` | 几乎原样，命名从 `frontend-skill` 改 `frontend-visual-design` 避免与 `frontend-large-feature-architecture` 混淆 |

#### [huggingface/skills](https://github.com/huggingface/skills) — 2 条

| Skill | 上游路径 | 改造要点 |
|---|---|---|
| `browser-ml-in-js` | `skills/transformers-js/SKILL.md` | 几乎原样，`@huggingface/transformers` 名字保留（这是 npm 包名，是事实标准） |
| `embedding-model-training` | `skills/train-sentence-transformers/SKILL.md` | 通用化：把 `sentence-transformers` Python 库的限制去掉，写成 bi-encoder / cross-encoder / sparse-encoder 三个家族的训练路由 |

## 跳过 / 没用上的抓取

### Langfuse (11 条跳过)

- `changelog-writing` — 用 Langfuse Linear issue ID
  和 `pages/changelog`，太内部。**跳过**。
- `code-review` 的 Langfuse-specific checklist
  （`packages/shared/...`）已去掉，但 skill 本身
  通用化保留。**算转了**。
- `datadog-query-recipes` — 用 `prod-us` / `prod-eu`
  / `prod-hipaa` / `prod-jp` 内部环境名。**跳过**。
- `debug-issue-with-datadog` — 用 Linear LFE-XXXX
  issue id。**跳过**。
- `frontend-browser-review` — 内部 `web/` Playwright
  MCP。**跳过**。
- `git-workflow` — 内部 production-promotion
  workflow。**跳过**。
- `linear-bug-triage` — Linear API 内部化。**跳过**。
- `weekly-production-review` — 内部 Metabase
  + Langfuse。**跳过**。
- 加上前面 3 条（analyze-cloud-costs /
  agent-setup-maintenance / 跳过的 changelog）= 11
  条。

### Anthropic (12 条跳过)

- `pdf` / `docx` / `pptx` / `xlsx` — 跟 Claude
  artifact 系统强绑定，强行 vendor-neutral 会
  丢 80% 内容。**跳过**。
- `theme-factory` / `web-artifacts-builder` /
  `slack-gif-creator` / `canvas-design` /
  `algorithmic-art` / `brand-guidelines` — Claude
  artifact 生态。**跳过**。
- `claude-api` — Claude 专有。**跳过**。
- `frontend-design` — 偏视觉设计哲学，没可程序化
  复用的 procedure。**跳过**。

### Hugging Face (17 条跳过)

`skills/` 目录里 19 条 SKILL.md，只转了 2 条。
剩下的 17 条大多是 HF 平台 / HF 工具专用，跳过理由：

- `huggingface-best` / `huggingface-zerogpu` /
  `huggingface-gradio` / `huggingface-tool-builder`
  / `huggingface-local-models` /
  `huggingface-vision-trainer` /
  `huggingface-llm-trainer` /
  `huggingface-paper-publisher` / `hf-cli` /
  `huggingface-spaces` / `huggingface-datasets` /
  `huggingface-trackio` / `huggingface-papers` /
  `huggingface-community-evals` /
  `huggingface-lora-space-builder` / `hf-mcp` —
  都是 HF 平台 / HF 工具的接口或推荐。**跳过**。
- `trl-training` — HF TRL 库专用。**跳过**。
- `transformers-js` (已转) /
  `train-sentence-transformers` (已转)。

### Letta (41 条跳过)

`letta/` + `tools/` + `meta/` 一共 42 条 SKILL.md，
只转了 1 条。剩下的 41 条大多绑死 Letta 平台或
具体工具：

- `letta/agent-development` /
  `letta/compaction-prompts` /
  `letta/conversations` /
  `letta/creating-letta-code-channels` /
  `letta/fleet-management` /
  `letta/importing-chatgpt-memory` /
  `letta/letta-api-client` /
  `letta/letta-configuration` /
  `letta/letta-filesystem-to-memfs` /
  `letta/navigating-chatgpt-history` — 全部
  Letta 内部 SDK / 数据流。**跳过**。
- `meta/skill-development` — 跟 `skill-creator`
  高度重叠。**跳过**（保留 `skill-creator`）。
- `tools/1password` / `ai-news` / `datadog` /
  `discord` / `doc` / `figma` / `github` /
  `gog` / `imsg` / `jupyter-notebook` /
  `linear` / `mcp-builder` / `memfs-search` /
  `morph-warpgrep` / `notion` / `obsidian` /
  `pdf` / `playwright` / `remotion` /
  `screenshot` / `sentry` / `slack` / `slides`
  / `social-cli` / `speech` /
  `spotify-player` / `spreadsheet` /
  `transcribe` / `visual-identity` /
  `yelp-search` — 单一工具专用脚本。**跳过**。
- `tools/frontend-skill` (已转) /
  `tools/mcp-builder` (跟 anthropics/skills 的
  `mcp-builder` 重叠，已转 anthropic 那份)。

### OpenAI skills (33 条跳过)

`skills/.curated/` + `skills/.system/` 一共 44
条 SKILL.md，只转了 6 条。剩下的 33 条几乎全部
绑死 Codex / 单一工具：

- `skills/.curated/aspnet-core` / `chatgpt-apps`
  / `cli-creator` (已转) / `cloudflare-deploy`
  / `define-goal` (已转) / `figma-*` (×7) /
  `gh-address-comments` / `gh-fix-ci` /
  `hatch-pet` / `jupyter-notebook` /
  `linear` / `migrate-to-codex` /
  `netlify-deploy` /
  `notion-knowledge-capture` /
  `notion-meeting-intelligence` /
  `notion-research-documentation` /
  `notion-spec-to-implementation` /
  `openai-docs` / `pdf` /
  `playwright-interactive` / `playwright` /
  `render-deploy` / `screenshot` /
  `security-best-practices` (已转) /
  `security-ownership-map` (已转) /
  `security-threat-model` (已转) /
  `sentry` / `speech` / `transcribe` /
  `vercel-deploy` / `winui-app` / `yeet`
  (已转) — 单一工具 / 单一平台专用。**跳过**。
- `skills/.system/imagegen` /
  `openai-docs` / `plugin-creator` /
  `skill-creator` / `skill-installer` —
  Codex 内部 / 跟 anthropics/skills 重叠。**跳过**。

## 计划中的上游抓取（未完成）

`scripts/sources.json` 里登记了 18 个 GitHub 仓库的 README.md
作为抓取目标。这是一轮**探索性抓取**：我们想看看上游 README
是否已经是 SKILL.md 的形态（带 frontmatter + 4 个 H1 section）。

实际跑下来发现：18 个仓库的 README.md **都不是** SKILL.md
形态 —— 它们是普通的项目 README（badge、TOC、安装步骤）。
`convert-skill.py` 能加上 frontmatter，但 body 结构（badge、
div、## Contents）跟 SKILL.md 的 4 段式不兼容。所以这 18 条
目前**全部跳过**，需要先到上游仓库里人工找到真正的
`skills/<name>/SKILL.md` 路径，再更新 sources.json。

详见 `scripts/sources.json` 的 `_meta` 段。

> 上面 29 条**已经**找到了真正的 `skills/<name>/SKILL.md`
> 路径并完成抓取，是 18 个 `skip` 仓库之外的额外收获。

## 许可证兼容

我们仓库本身 MIT 发布。**所有收录的技能必须**：

- 自己是 MIT / Apache-2.0 / BSD / 公有领域，**或**
- 上游明确允许再分发

GPL / AGPL / 商业限制 (CC-BY-NC) 的技能**不收**。

## 致谢

每个**抓取自上游**的技能文件，frontmatter 的 `source` 字段
会写原作者和 commit。如果原作者不希望自己的技能出现在这里，
issue 或者直接发邮件，开个 PR 删掉就行。

手写技能的 `source` 字段故意省略 —— 作者就是本仓库。
