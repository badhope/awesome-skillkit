# AI-SKILL

> An open-source, community-driven index of AI agent skill repositories.
> MIT licensed. No tracking. No signup. Just markdown and links.

## 这是什么

AI-SKILL 是一个**开源社区驱动的 AI 技能仓库索引**。我们的目标不是
做又一个 awesome-list，而是做一个**可搜索、多维度分类、技能级细化**
的索引，让用户能快速找到最适合自己需求的技能仓库。

- **928+ 个外部仓库**已索引，覆盖 OpenAI、Anthropic、Hugging Face、
  LangChain、LlamaIndex 等大厂与社区项目
- **38 个本地精选 SKILL.md**，可直接 drop 进 Claude / Codex / Cursor /
  Continue 或任何读 Markdown 的 agent
- **多维度分类**：按功能领域（9 大类）、按厂商类型（大厂 / 热门社区 /
  社区 / 个人）、按子分类（49 类）、按星标分层
- **技能级索引**：每个仓库卡片列出它提供的具体能力，搜"RAG"就能
  找到所有支持 RAG 的仓库
- **前端可搜索**：按名称、厂商、标签、描述、技能搜索，实时筛选

## License

**MIT**。我们不做商业化，做社区化、开源化。所有本地技能均为 MIT
协议；外部仓库的协议看各自卡片上的 `license` 字段。

## 怎么用

### 浏览仓库索引（主要功能）

打开 [AI-SKILL Pages](https://badhope.github.io/AI-SKILL/#/external)，
按以下方式查找：

1. **搜索**：在搜索框输入关键词（如 `RAG`、`agent`、`fine-tuning`），
   会同时匹配仓库名、厂商、标签、描述和**技能列表**
2. **切换视角**：四个 tab 切换分组方式
   - **By Domain** — 按功能领域（基础设施 / 智能体 / RAG / 评估安全 / 开发工具 / 应用 / 多模态 / 内容文档 / 研究训练）
   - **By Vendor Type** — 按厂商类型（大厂官方 / 热门社区 / 社区 / 个人项目）
   - **By Category** — 按 49 个子分类
   - **By Stars** — 按星标分层（100k+ / 50k+ / 10k+ / 1k+ / <1k）
3. **厂商筛选**：下拉框筛选特定厂商类型
4. **查看技能**：每张卡片列出该仓库提供的具体技能（如 `tool use`、
   `structured output`、`RAG`），帮你判断是否需要
5. **直达源头**：点 "Visit on GitHub ↗" 跳转到上游仓库

### 浏览本地精选技能

打开 [首页](https://badhope.github.io/AI-SKILL)，看 38 个本地
`SKILL.md` 文件。这些是我们自己制作或从大厂抓取并通用化的技能，
clone 下来就能用。

```
https://badhope.github.io/AI-SKILL/#/skill/pdf-summarizer
https://badhope.github.io/AI-SKILL/#/bundle
```

**顶栏右上角可以切 EN / 中文**。语言选择存在 `localStorage` 里，
刷新也保留；URL 加 `?lang=zh` 也能强切。

### 装一个本地技能

```bash
# 装到 Claude (默认 ~/.claude/skills)
python scripts/install-skill.py pdf-summarizer --target claude

# 装到 Codex
python scripts/install-skill.py pdf-summarizer --target codex

# 装到任意目录
python scripts/install-skill.py pdf-summarizer --target /opt/my-agent/skills
```

### 打个包

```bash
# 单条
python scripts/bundle-skill.py pdf-summarizer -o pdf.zip

# 全部本地技能
python scripts/bundle-skill.py --all -o skills-v1.zip
```

## 分类体系

### 9 大功能领域（Domain）

| Domain | 说明 | 典型仓库 |
|---|---|---|
| Infrastructure & Serving | LLM 推理、分布式训练、量化、GPU 内核 | vllm, llama.cpp, DeepSpeed |
| Agent & Tooling | Agent 框架、工具调用、MCP 协议 | langchain, autogpt, mcp-servers |
| RAG & Knowledge | RAG 管道、向量库、知识图谱 | llamaindex, chroma, langchain |
| Evaluation & Safety | 评估、基准、护栏、对齐 | deepeval, promptfoo, guardrails |
| Development Tools | SDK、CLI、代码助手、终端 | continue, aider, ohmyzsh |
| Applications | 聊天 UI、工作流编排、数据分析 | n8n, lobe-chat, flowise |
| Multimodal | 视觉、图像生成、视频、音频 | whisper, stable-diffusion, bark |
| Content & Docs | Cookbook、Prompt 库、教程 | anthropic-cookbook, openai-cookbook |
| Research & Training | 微调、合成数据、论文 | axolotl, unsloth, lit-gpt |

### 4 种厂商类型（Vendor Type）

| Type | 说明 |
|---|---|
| Big Corp / Official | 大厂官方（OpenAI、Anthropic、Google、Meta 等） |
| Popular Community | 热门社区项目（10k+ stars） |
| Community | 一般社区项目 |
| Indie / Personal | 个人项目 |

### 49 个子分类（Category）

详见 `external-index/skills.yaml` 的 `categories` 段，涵盖
`official-cookbooks`、`prompt-libraries`、`agent-frameworks`、
`rag-retrieval`、`vector-databases`、`embeddings`、`evaluation`、
`benchmarks`、`tool-use`、`mcp-protocol`、`llm-serving`、
`fine-tuning`、`distributed-training`、`quantization`、
`model-merging`、`guardrails`、`safety-alignment`、
`privacy-federated`、`observability`、`memory`、`knowledge-graphs`、
`synthetic-data`、`data-pipelines`、`dev-tools`、`code-llms`、
`code-assistants`、`terminal-cli`、`browser-automation`、
`computer-use`、`multimodal`、`image-generation`、`video-generation`、
`audio-tts`、`speech-recognition`、`translation`、`chat-ui`、
`workflow-orchestration`、`data-analysis`、`document-processing`、
`knowledge-management`、`education`、`research-papers`、
`awesome-lists`、`tutorials`、`templates-starters`、`case-studies` 等。

## 目录结构

```
skills/                  本地精选技能（38 个 SKILL.md）
external-index/          外部仓库索引源数据（skills.yaml，928 条）
  └─ skills.yaml         ← 索引的 source of truth
frontend/                静态站点源码（TypeScript + Vite）
  ├─ src/pages/external.ts   仓库索引页（搜索 + 4 视角 + 技能级展示）
  └─ public/external-repos.json  运行时数据（由 sync 脚本生成）
scripts/                 工具脚本
  ├─ sync-external-index.py   skills.yaml → external-repos.json
  ├─ enrich-skills-field.py   为每个仓库派生 skills 字段
  ├─ validate-skill.py        校验本地技能 + 自动触发 sync
  ├─ install-skill.py         装到 ~/.claude/skills 等
  ├─ bundle-skill.py          打包 ZIP
  ├─ sync-github.py           刷 external-index 元数据
  └─ check-links.py           检查死链
docs/                    设计文档
```

## 添加新仓库到索引

编辑 `external-index/skills.yaml`，在 `skills:` 段加一条：

```yaml
- slug: my-awesome-repo
  title: My Awesome Repo
  title_zh: 我的仓库
  source: user/repo
  source_url: https://github.com/user/repo
  category: agent-frameworks      # 49 个子分类之一
  domain: agents                  # 9 大领域之一
  vendor_type: community          # big-corp / popular-community / community / indie
  tags: [agent, planning, memory]
  summary: One-line description.
  summary_zh: 一句话描述。
  stars: 1234
  license: MIT
  pushed_at: '2026-06-01'
  skills:                          # 该仓库提供的具体技能
    - multi-step agents
    - planning
    - memory
```

然后跑：

```bash
python scripts/sync-external-index.py   # 重新生成 JSON
```

`validate-skill.py` 也会自动触发 sync。

## 添加新本地技能

1. 复制 `skills/_TEMPLATE.md` 到 `skills/<your-slug>/SKILL.md`
2. 写 frontmatter（看 `docs/schema.md`）
3. 写 `# Prompt` 段
4. `python scripts/validate-skill.py` 跑一遍
5. 开 PR

## 仓库里的工具脚本

| 脚本 | 干啥 |
|---|---|
| `sync-external-index.py` | skills.yaml → frontend/public/external-repos.json |
| `enrich-skills-field.py` | 为每个仓库派生 skills 字段（基于 category + tags + summary） |
| `validate-skill.py` | CI 必跑，校验 frontmatter + body + 写 frontend JSON + 触发 sync |
| `install-skill.py` | 装到 `~/.claude/skills` 等本地目录 |
| `bundle-skill.py` | 打包 ZIP（命令行版本；网页版走 `frontend/#/bundle`） |
| `sync-github.py` | 刷 `external-index/` 元数据（stars / license / pushed_at） |
| `check-links.py` | 检查 `external-index/` 死链 |

## 贡献

看 `CONTRIBUTING.md`。简短版：

- 单条 PR
- 不手动改 `stars` / `license` / `pushed_at`，sync 脚本会自动刷
- 新增仓库索引请填全 `domain` / `vendor_type` / `skills` 字段
- prompt 改了才升 version 号

## License

MIT. 本地技能均为 MIT；外部仓库的协议看各自卡片上的 `license` 字段。
