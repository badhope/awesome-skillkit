# SOURCE — 上游出处与本地原创声明

## 现状

本仓库目前收录的 5 条技能全部是**手写**（`pdf-summarizer`,
`code-reviewer`, `test-generator`, `sql-query-helper`,
`commit-message-writer`）。它们的 frontmatter 故意没带
`source:` 字段，因为作者就在这个仓库里，不存在"上游"。

## 计划中的上游抓取

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
