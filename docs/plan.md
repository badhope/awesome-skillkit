# Plan

## 写在前面的废话

这个仓库一开始是个 link list —— 收集 agent 相关的 GitHub
项目，然后 fork 别人抄一抄就叫"comprehensive curated index"。

这种 awesome-list 全网有八百个，没一个能用的：
点进去是个 GitHub 链接，链接里有个子目录，子目录里有个
SKILL.md，SKILL.md 写着"summarise a PDF"，没有 prompt
没有 example 没有任何能跑的东西。

我们要做的是把这些技能**全部下载下来，落盘到本地**，改到
能用的程度。

就这样。

## 这个仓库是干嘛的

一个本地技能保险柜。`skills/` 下面全是真东西，clone
下来就能用，不需要再去 GitHub 找。

外部项目的链接列表（`external-index/`）是顺带的，
留作发现入口，主要产品是 `skills/` 本身。

## 设计原则

能用就行，别装。

- **完全本地** —— 抓下来的技能是文件，不是 URL。删掉
  源仓库也不影响使用
- **平台中立** —— 默认所有技能在 Claude / Codex / Cursor
  / Continue / 任何能读 Markdown 的地方都能跑。
  哪个真做不到，在 frontmatter 里老实标 `platforms: [claude]`
- **可直接读源码** —— 不要在 prompt 外面包 JSON 包 YAML
  包 XML 包三层
- **脚本不要玄学** —— 全部 Python 标准库 + pyyaml +
  ruamel，不引外部依赖，不引 web 框架

## 目录结构

```
.
├── skills/                  # 主体：本地技能
│   ├── _index.yaml          # 机读索引
│   ├── _TEMPLATE.md         # frontmatter 模板
│   ├── pdf-summarizer/
│   │   ├── SKILL.md
│   │   └── assets/          # 可选
│   └── ...
│
├── external-index/          # 外部项目链接列表（旧功能保留）
│   ├── skills.yaml
│   └── health.json
│
├── frontend/                # 静态站点
│   ├── src/
│   ├── public/              # skills.json 快照
│   ├── index.html
│   ├── package.json
│   └── vite.config.ts       # 详细设计见 docs/frontend-design.md
│
├── scripts/                 # 全部 Python
│   ├── fetch-skill.py       # 抓
│   ├── convert-skill.py     # 转格式
│   ├── extend-skill.py      # 补全
│   ├── validate-skill.py    # 校验
│   ├── install-skill.py     # 装到本地 ~/.claude/skills
│   ├── bundle-skill.py      # 打包 ZIP
│   ├── sync-github.py       # 刷 external-index 元数据
│   └── check-links.py       # 检查 external-index 死链
│
├── bundles/                 # bundle-skill.py 输出，gitignore
│
├── .github/workflows/
│   ├── validate-skills.yml  # 每次 push 跑 validate (--strict)
│   ├── check-links.yml      # 每周
│   ├── sync-github.yml      # 每天
│   ├── pages.yml            # push 后部署前端
│   ├── gitleaks.yml         # 扫 secrets，每次 push + PR
│   └── stale.yml            # 标记/关闭不活跃 issue
│
├── docs/
│   ├── plan.md              # 本文件
│   ├── schema.md            # frontmatter 字段说明
│   ├── extension-rules.md   # 怎么把烂技能改好
│   └── frontend-design.md   # 前端设计
│
├── README.md
├── README.zh.md             # 中文版
├── CONTRIBUTING.md
├── CHANGELOG.md
├── LICENSE
└── SOURCE.md                # 仓库里技能的来源声明
```

## 怎么用

### 我想用某个技能

```bash
git clone https://github.com/badhope/AI-SKILL
ls skills/                            # 看看有什么
cat skills/pdf-summarizer/SKILL.md    # 读一下
```

或者直接装到本地 agent：

```bash
python scripts/install-skill.py pdf-summarizer --target claude
# → ~/.claude/skills/pdf-summarizer/SKILL.md
```

或者打个包带走：

```bash
python scripts/bundle-skill.py --all -o skills-v1.zip
```

### 我想加新技能

1. 把源文件丢到 `skills/<your-slug>/SKILL.md`
2. 写好 frontmatter（看 `docs/schema.md`）
3. `python scripts/validate-skill.py` 跑一遍
4. 开 PR

### 我想批量抓别人的技能

```bash
# 单个
python scripts/fetch-skill.py \
  --source anthropics/anthropic-skills \
  --path skills/pdf \
  --out skills/pdf-summarizer

# 批量，sources.json 写好了源
python scripts/fetch-skill.py --all --sources scripts/sources.json
```

抓下来之后跑 `convert-skill.py` 转成标准格式，
再跑 `extend-skill.py` 补全缺的字段。

## 8 个脚本

| 脚本 | 干啥 |
|---|---|
| `fetch-skill.py` | 从 GitHub 抓技能文件，**完全本地化**。连同 `SOURCE.md` 一起落盘，写明来源 |
| `convert-skill.py` | 原始 .md → 标准 SKILL.md。能识别就识别，识别不了打 `needs_review` |
| `extend-skill.py` | 见 `docs/extension-rules.md`，4 条规则把烂技能改好 |
| `validate-skill.py` | 校验 frontmatter + body 结构。CI 必跑 |
| `install-skill.py` | `cp -r skills/<slug> ~/.claude/skills/`，就这样 |
| `bundle-skill.py` | `zip` 一下，结构跟 `skills/` 一致，解压即用 |
| `sync-github.py` | 刷 `external-index/skills.yaml` 的 stars / license |
| `check-links.py` | ping `external-index` 里所有 source_url |

## Frontmatter 是关键

详细规则看 `docs/schema.md`。这里只说最重要的一点：

**frontmatter 不绑死平台**。一个技能默认在所有
agent 上都能跑。如果有部分内容只对 Claude 有效，
那一段开头写：

```markdown
> **Claude-only** — 下面这段假设 Claude 的 tool_use 格式
```

就这样，标一行，不要把所有内容都包在某种 vendor SDK 里。

## 我们**不**做的事

明确写出来：

- **不**做 marketplace / 评论 / 评分 / 收藏
- **不**执行 prompt（我们是数据仓库，不是 runtime）
- **不**做服务端（前端纯静态）
- **不**搞 per-skill 版本号，仓库级别 tag 够用
- **不**做 vendor 锁定。某天所有 agent 都换实现了，
  这些文件还能读

## 旧仓库怎么迁

旧仓库 `AI-SKILL` 之前是 link list 形态。已完成的迁移：

1. ✅ 新建 `skills/`、`external-index/`、`frontend/`、`bundles/`
2. ✅ `catalog/skills.yaml` → `external-index/skills.yaml`
3. ✅ `catalog/own_skills.yaml` → `skills/_index.yaml`（新格式）
4. ✅ `data/health.json` → `external-index/health.json`
5. ✅ 改两个 workflow 的 path（已升级到 v6 actions）
6. ✅ 跑第一波抓取：18 个候选源全部 `skip: true`（README.md
   不是 SKILL.md 形态，详见 `SOURCE.md`）
7. ✅ 跑 convert + extend（dry-run 验证可用）
8. ✅ validate 全过：`5 pass / 0 err / 0 warn`
9. ✅ build 前端：`index.html` 1.55 KB + `index.js` 114 KB
   (36 KB gzipped)
10. ✅ 写新 README + 中文版
11. ⏳ tag v1.0.0（v1.0 之前要确保：35 条技能全 0/0/0、
    `pages.yml` 部署成功一次、`SOURCE.md` 收齐 8 个上游仓库
    的 29 条技能 / 91 条跳过原因、**站点 UI 国际化完成**）
    — 阻塞：等用户 `git push` 指令（commit `ba320ee`
    之后没推）

## 怎么算做完了

- [x] `git clone` 下来断网也能用
- [x] `validate-skill.py` 0 错误 0 warning（strict 模式）
- [x] `pages.yml` 每次 push 自动部署，< 1s 加载
- [x] 装一个技能 = 一条命令
- [x] 不存在 `needs_review: true` 的技能（release 时）
- [x] 站点 UI 国际化（EN / 中文可切）—— 顶栏右上角切语言，所有辅助 / 介绍文案都换；SKILL.md 正文保持原文不动

## 写在最后

仓库是给真人看的，不是给 AI 看的，也不是给老板看
的。写得清楚点，写得有人味一点，少堆术语。

如果某段文字读起来像"Utilising our robust
leverage of synergies"那种调调，重写。
