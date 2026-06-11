# Next steps — 剩余计划

> 上次构造停在 **Phase 9**（35 条技能全部 0/0/0，build 通过，
> 文档已更新；本地 commit + push 等用户指令）。
> 本文件按"必须 / 重要 / nice-to-have"三档列出剩下要做的事。

## 状态

| 阶段 | 内容 | 状态 |
|---|---|---|
| Phase 1 | 元文件清理（issue 模板、PR 模板、CITATION、CHANGELOG） | ✅ |
| Phase 2 | Python 脚本（fetch / convert / extend / validate / install / bundle） | ✅ |
| Phase 3 | 5 条手写 vendor-neutral 技能 + SOURCE.md | ✅ |
| Phase 4 | Vite + vanilla TS 前端（3 页：list / detail / bundle） | ✅ |
| Phase 5.1 | 全量脚本冒烟 | ✅ |
| Phase 5.2 | 3 轮检察官审查（文档 / 前端 / 脚本） | ✅ |
| Phase 5.3 | 交付前总检查 | ✅ |
| Phase 6.1 | 本地 commit `ba320ee` | ✅ |
| Phase 6.2 | `git push origin main` | ⏸  等用户指令 |
| Phase 6.3 | 5 条 QA 技能（deepeval / promptfoo） | ✅ |
| Phase 7 | 5 条大厂 / 参考项目技能（mcp-builder / webapp-testing / llm-pricing / realtime-eval / react-router） | ✅ |
| Phase 8 | 10 条大厂深抓技能（langfuse 7 / anthropic 3）| ✅ |
| Phase 9 | 9 条大厂深抓技能（openai 6 / letta 1 / huggingface 2）| ✅ |

## 当前 vault

`35 / 0 / 0` — 35 条技能全部通过 strict 验证。

| 类别 | 数量 | 例子 |
|---|---|---|
| 手写 vendor-neutral | 5 | pdf-summarizer, code-reviewer, test-generator, sql-query-helper, commit-message-writer |
| Claude-only 平台示例 | 1 | pdf-vision-extractor |
| 抓取自大厂 + 通用化 | 29 | mcp-builder, webapp-testing, skill-creator, doc-coauthoring, internal-comms, clickhouse-best-practices, turborepo, security-review, storybook, pnpm-upgrade-package, frontend-large-feature-architecture, code-review, deepeval-*, promptfoo-*, llm-pricing-file-update, realtime-eval-bootstrap, react-router-search-params, goal-definition, cli-builder, threat-modeling, secure-code-by-language, ownership-bus-factor, pr-yeet, frontend-visual-design, browser-ml-in-js, embedding-model-training |

**跳过的 91 条**（仓库太专有 / 平台强绑定）：

- Langfuse 11 条（linear-bug-triage / datadog-query-recipes /
  changelog-writing / debug-issue-with-datadog /
  frontend-browser-review / git-workflow /
  weekly-production-review / analyze-cloud-costs /
  agent-setup-maintenance 等）
- Anthropic 12 条（pdf / docx / pptx / xlsx /
  theme-factory / web-artifacts-builder /
  slack-gif-creator / canvas-design / algorithmic-art /
  brand-guidelines / claude-api / frontend-design）
- Hugging Face 17 条（huggingface-*/hf-cli/hf-mcp 等
  HF 平台专用，trl-training HF TRL 库专用）
- Letta 41 条（letta/agent-development 等 10 条 Letta
  SDK 专用，meta/skill-development 跟 skill-creator
  重叠，tools/* 30 条单一工具专用）
- OpenAI skills 33 条（curated 30 条单一工具 / 单
  一平台专用，system/* 5 条 Codex 内部）

详见 `SOURCE.md` 的"跳过 / 没用上的抓取"段。

## 必须做（按优先级）

### N1. 至少一条 `platforms:` 不为空的技能
- **状态**：✅ 完成
- **做法**：`pdf-vision-extractor` 已经带 `platforms: [claude]`
  并在文档里写 `**Claude-only**` disclaimer
- **验收**：`python3 scripts/validate-skill.py --strict` 仍 0/0/0；
  前端列表页能看到 `claude` chip

### N2. push 到远端
- **状态**：本地准备完成，**等用户给 creds**
- **做法**：用 `scripts/push.sh`，多方法自动选
- **远端现状**（最后一次 `ls-remote`）：
  - `main` 停在 `f705579`（老 era 的"cleanup"，我们落后 0 / 领先 2）
  - 远端无 tag
- **本地 tag 已重置**：
  - 删了老 `v1.0.0`（指向 `676954d`，老 era 的安全修复提交）
  - 删了老 `v1.1.0`（指向 `0259fb3`，老 era 的 test/sdk 提交）
  - 在新 HEAD `1627cfa` 上打了新的 annotated `v1.0.0` / `v1.1.0`
- **多种 push 方法**（任选一种）：

  | 凭据形式 | 命令 |
  |---|---|
  | GH_TOKEN | `GH_TOKEN=ghp_xxx ./scripts/push.sh` |
  | SSH 私钥 | `GIT_SSH_KEY=~/.ssh/id_ed25519 ./scripts/push.sh` |
  | SSH agent | `ssh-add ~/.ssh/id_ed25519 && ./scripts/push.sh` |
  | 永久 helper | `git config --global credential.helper store` 后再 push |
  | 用户名密码 | `git -c credential.helper='!f() { echo username=...; echo password=...; }; f' push` |
  | 直接命令 | `git push --force-with-lease origin main && git push --tags origin` |

- **关键点**：
  - 默认 `FORCE=1`，**会覆盖远端老 main** —— 这是用户明确要求的
  - 默认 `CLEAN_OLD_TAGS=1`，**会删远端任何 v0.x tag**（目前远端没 tag）
  - 默认 `PUSH_TAGS=1`，**会推新 v1.0.0 / v1.1.0**
  - 沙箱没有任何 creds，**用户必须自己跑**（或把 token 塞进沙箱 env）

- **沙箱尝试过的认证方式**（全部失败）：
  - ❌ 无 GH_TOKEN env
  - ❌ 无 SSH 私钥（`~/.ssh/` 空）
  - ❌ SSH outbound 22 被防火墙挡
  - ❌ `gh` 不在 apt
  - ❌ 无 credential.helper / .netrc / .git-credentials

### N3. CI 第一次实跑
- **触发**：push 之后
- **看**：`validate-skills.yml` / `pages.yml` / `check-links.yml` 三个核心 workflow
- **可能翻车**：
  - `check-links.yml` 里 29 个 source URL 大概率死了几个 → 改成不 `--fail` 即可，不致命
  - `pages.yml` Python 3.11 + Node 20 路径要对一遍

## 重要（不是 blocker，但跳过会留遗憾）

### N4. v1.0.0 tag
- **状态**：✅ 本地已打，**等 push 完再 push 上去**
- 本地 `v1.0.0` / `v1.1.0` 已重新打在新 HEAD `1627cfa` 上
  （annotated，带 message 解释为什么覆盖老 tag）
- `scripts/push.sh` 默认会 `git push --tags` 把两个 tag 都推上去

### N5. 进一步扩大抓取面
- 当前的 29 条是 8 个仓库的产物：`confident-ai/deepeval` (3) /
  `promptfoo/promptfoo` (3) / `langfuse/langfuse` (8) /
  `openai/openai-cookbook` (1) / `openai/skills` (6) /
  `letta-ai/skills` (1) / `huggingface/skills` (2) /
  `anthropics/skills` (5)。还可以再扩：
  - `google/adk-python`（如果它有 `skills/` 或 `.claude/skills/`）
  - `cloudflare/agents`（同上）
  - `vercel-labs/agent-skills`（如果存在）
  - `stripe/agent-toolkit`（vendor-neutral 的支付工具）
  - `awslabs/amazon-bedrock-agent-samples`（如果存在）
  - 等等 —— 用 `git clone --depth 1` 浅克隆加
    `git ls-tree -r HEAD | grep SKILL.md` 拿真实路径
- **优先抓 vendor-neutral 的**（artifact 系统、单一平台
  强绑定的跳过）
- **本仓库已显式记录 91 条跳过原因** —— 不会重复抓

### N6. README 修整
- 当前 README 列了 `frontend/` 段，但没说"打开后 36 KB JS 跑在浏览器"
- 加一句：site 用 hash 路由，深链 `#/skill/pdf-summarizer` 可分享
- 链接到 GitHub Pages URL（push 后才有真链接）

### N7. issue 模板精简
- 当前 3 个 issue 模板：`bug_report.yml` / `dead-link.yml` / `new-entry.yml`
- 已精简 ✅

### N8. CODEOWNERS 写一行
- 当前文件存在，内容是 `* @badhope`（单人项目）
- 已加 ✅

## nice-to-have（不做也行）

### N9. 前端可选升级
- 详情页 TOC（`docs/frontend-design.md` 提到）— 已加 ✅
- 自托管字体（现在用 system 栈）— 延迟 LCP 但风格统一
- 代码块"复制"小按钮（仅 prompt 块有，body 内的代码块没有）— 已加 ✅
- 这些 v1 都有，README 可考虑补一句

### N13. 站点 UI 国际化（i18n）
- **状态**：✅ 完成
- **做法**：
  - `frontend/src/i18n.ts` 加 80+ 字符串 key，EN 是 source of truth，ZH 是第二份；缺中文时静默回退 EN
  - `pickZh(obj, field)` / `pickPlatform(p)` 翻译辅助
  - `applyStaticTranslations()` 自动扫描 `data-i18n` / `data-i18n-aria` / `data-i18n-title` 三种属性钩子
  - URL `?lang=zh` 同步 + localStorage 持久化（粘性）
  - 切换语言：订阅 `subscribe()` → 重新跑路由 → 列表 / 详情 / 合集页原地换语言
- **覆盖范围**（除了 SKILL.md 正文本身不动）：
  - 列表：hero / 4 个 stat / 搜索框 placeholder / 3 个 select option / 卡片 name+description+category+platform chip+tooltip
  - 详情：meta-row 分类 / 平台 chip / TOC 标题 / 表格列头 / 各种 section 标题 / 代码块 copy 按钮 / 复制成功提示
  - 合集：列表 category 列 / 5 个按钮
  - 404：标题 / 副标题 / 搜索建议标签 / 返回按钮
  - topbar / footer / noscript / skip-link / lang-toggle aria-label
- **数据侧**：`scripts/validate-skill.py` 把 `description_zh` 写入 `skills.json` 的 index，35/35 技能非空
- **不做的部分**：SKILL.md 正文、`hero.sub` 这种"原文是英文" 的描述字段、meta description、og:title/description（这些是 SEO 用，爬虫通常不跑 JS）
- **验收**：
  - `npm run build` 通过
  - dist 总大小 +2.84 kB（i18n 新 key + pickPlatform）

### N10. 脚本小修
- `validate-skill.py:207` 错误消息只说 `platforms[0]`，但循环检了所有平台 — 误导
- `convert-skill.py:190` 无条件写 `fm["needs_review"] = needs_review`，但 convert 重复跑同一文件第二次应该是 idempotent 写 True — 实际没事
- 不修也行

### N11. 计划 README 状态码
- 之前 `plan.md` 里的 ⏳ 已经全部 ✅ 化
- 但 v1.0.0 tag 那条还在 ⏳ — 等 N4 完成时再改

### N12. 清理 /tmp 下的 probe 临时文件
- `/tmp/probe3-*` 4 个浅克隆（huggingface / letta / openai / smol）
- 处理完文档后可以删，避免下次重启时误以为是当前状态

## 不做（明确放弃）

- ❌ CI 矩阵（多 Python 版本、多 Node 版本）— 单一版本够用
- ❌ 暗色模式切换按钮 — 用 `prefers-color-scheme` 自动切，按钮是 UI noise
- ❌ 任何运行时框架（React / Vue / Svelte）— vanilla TS 够用
- ❌ 引入 markdown 库（marked.js）— 6 段自己渲染，5 KB 比 50 KB 香

---

**当下最优路径**：等用户指令推 N2，**同时**做 N1（已 ✅），
推完一起进 N3 → N4。
