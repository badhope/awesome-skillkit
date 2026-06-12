# AI-SKILL

> A vault of agent skills, ready to copy into Claude / Codex / Cursor /
> Continue / whatever comes next. Vendor-neutral, fully local, hand-picked.

## 这是什么

一个**技能保险柜**。`skills/` 下面放真东西 —— 每个技能是一份
`SKILL.md`，frontmatter + body，clone 下来就能用。

不是 awesome-list。awesome-list 给你一个 GitHub 链接，你点
进去还得自己找文件。这个仓库的每个技能**已经把文件落盘到
本地**，不依赖任何外部仓库。

不是 vendor-bound skill pack。Claude skills 只能在 Claude 用，
Codex skills 只能在 Codex 用。这里默认所有技能**平台中立**，
在能读 Markdown 的 agent 上都能跑。少数平台相关的技能会在
`platforms:` 字段标 `claude` 之类的限定词，并在文档里写清
`**Claude-only**` disclaimer。

## Vault 里现在有什么

`267 / 0 / 0` —— 267 条技能，全部通过 `validate-skill.py --strict` 验证。

| 类别 | 数量 | 例子 |
|---|---|---|
| 手写 vendor-neutral | 5 | `pdf-summarizer`, `code-reviewer`, `test-generator`, `sql-query-helper`, `commit-message-writer` |
| Claude-only 平台示例 | 1 | `pdf-vision-extractor` |
| 抓取自大厂 + 通用化 | 261 | `mcp-builder`, `webapp-testing`, `skill-creator`, `doc-coauthoring`, `internal-comms`, `clickhouse-best-practices`, `turborepo`, `security-review`, `storybook`, `pnpm-upgrade-package`, `frontend-large-feature-architecture`, `code-review`, `deepeval-*`, `promptfoo-*`, `llm-pricing-file-update`, `realtime-eval-bootstrap`, `react-router-search-params`, `goal-definition`, `cli-builder`, `threat-modeling`, `secure-code-by-language`, `ownership-bus-factor`, `pr-yeet`, `frontend-visual-design`, `browser-ml-in-js`, `embedding-model-training`, `drizzle`, `modal`, `netlify-deploy`, `haiku`, `playwright`, `figma-*`, `huggingface-*`, `letta-*`, `vercel-*` |

抓取来源的 136 个仓库（78 个成功，58 个失败）：`openai/skills` (44) / `letta-ai/letta` (23) / `huggingface/huggingface-skills` (18) / `promptfoo/promptfoo` (12) / `langfuse/langfuse` (10) / `vercel/ai` (8) / `pytorch/pytorch` (7) / `anthropics/anthropic-skills` (6) / `deepeval/deepeval` (5) / `lobehub/lobe-chat` (4) 等。
每条抓来的技能 frontmatter 都标了 `source:` 字段，`author` 写成 `"<Vendor> (downstream pack: badhope)"`。
详见 `SOURCE.md`。

### 质量审计

所有 267 个技能通过以下检查：
- ✅ 中文翻译完整（name_zh, description_zh）
- ✅ 标签系统统一
- ✅ H1 章节完整（When to use, When NOT to use, Example, Prompt）
- ✅ 代码示例完整
- ✅ 分类明确（dev-tools: 201, ai: 66）

## 怎么用

### 浏览

打开 [AI-SKILL Pages](https://badhope.github.io/AI-SKILL)，看
列表、点详情、点下载。站点是 hash 路由，**深链可直接分享**：

```
https://badhope.github.io/AI-SKILL/#/skill/pdf-summarizer
https://badhope.github.io/AI-SKILL/#/bundle
```

或者直接看 `skills/` 目录 —— 它就是站点渲染的数据源。

**顶栏右上角可以切 EN / 中文**。除了 `SKILL.md` 正文本身
不动之外，所有辅助 / 介绍文案都会换。语言选择存在
`localStorage` 里，刷新也保留；URL 加 `?lang=zh` 也能强切。

### 装一个技能

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

# 全部
python scripts/bundle-skill.py --all -o skills-v1.zip
```

ZIP 结构跟 `skills/` 一致，解压即用。

## 目录结构

```
skills/                  主体：本地技能
external-index/          外部项目链接（旧功能，保留作发现入口）
frontend/                静态站点源码
scripts/                 工具脚本
docs/                    设计文档
bundles/                 bundle-skill.py 输出（gitignore）
```

详细看 `docs/plan.md`。

## 添加新技能

1. 复制 `skills/_TEMPLATE.md` 到 `skills/<your-slug>/SKILL.md`
2. 写 frontmatter（看 `docs/schema.md`）
3. 写 `# Prompt` 段
4. `python scripts/validate-skill.py` 跑一遍
5. 开 PR

## 仓库里的工具脚本

| 脚本 | 干啥 |
|---|---|
| `fetch-skill.py` | 从 GitHub 抓技能落到本地（v1 18 候选源全 skip，详见 `SOURCE.md`） |
| `convert-skill.py` | 原始 .md → 标准 SKILL.md |
| `extend-skill.py` | 把烂技能按 4 条规则改到能跑（看 `docs/extension-rules.md`） |
| `validate-skill.py` | CI 必跑，校验 frontmatter + body + 写 frontend 用的 JSON |
| `install-skill.py` | 装到 `~/.claude/skills` 等本地目录 |
| `bundle-skill.py` | 打包 ZIP（命令行版本；网页版走 `frontend/#/bundle`） |
| `sync-github.py` | 刷 `external-index/` 元数据（stars / license / pushed_at） |
| `check-links.py` | 检查 `external-index/` 死链 |

## 贡献

看 `CONTRIBUTING.md`。简短版：

- 单条 PR
- 不手动改 `stars` / `license` / `pushed_at`，sync 脚本会自动刷
- prompt 改了才升 version 号

## License

MIT. 收录的技能版权看各自 `source` 字段 —— 我们不动 prompt
的文字。
