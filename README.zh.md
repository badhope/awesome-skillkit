# AI-SKILL

> 一个 agent 技能保险柜。能直接装到 Claude / Codex / Cursor /
> Continue / 任何下一代 agent。平台中立、完全本地、人工挑选。

## 这是什么

`skills/` 下面放真东西 —— 每个技能是一份 `SKILL.md`，有
frontmatter + body，clone 下来就能用。

**不是** awesome-list。awesome-list 给你一个 GitHub 链接，你
点进去还得自己找文件。这个仓库的每个技能**已经把文件落盘到
本地**，不依赖任何外部仓库。

**不是** vendor-bound skill pack。Claude skills 只能在 Claude
用，Codex skills 只能在 Codex 用。这里默认所有技能**平台中立**，
在能读 Markdown 的 agent 上都能跑。

## 怎么用

### 浏览

打开 [AI-SKILL Pages](https://badhope.github.io/AI-SKILL)，看
列表、点详情、点下载。

或者直接看 `skills/` 目录 —— 它就是站点渲染的数据源。

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
| `fetch-skill.py` | 从 GitHub 抓技能落到本地 |
| `convert-skill.py` | 原始 .md → 标准 SKILL.md |
| `extend-skill.py` | 把烂技能按 4 条规则改到能跑 |
| `validate-skill.py` | CI 必跑，校验 frontmatter + body |
| `install-skill.py` | 装到 `~/.claude/skills` 等本地目录 |
| `bundle-skill.py` | 打包 ZIP |
| `sync-github.py` | 刷 `external-index/` 元数据 |
| `check-links.py` | 检查 `external-index/` 死链 |

## 贡献

看 `CONTRIBUTING.md`。简短版：

- 单条 PR
- 不手动改 `stars` / `license` / `pushed_at`，sync 脚本会自动刷
- prompt 改了才升 version 号

## License

MIT. 收录的技能版权看各自 `source` 字段 —— 我们不动 prompt
的文字。
