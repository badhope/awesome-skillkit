# skills/

每个技能是一个目录，里头至少有一份 `SKILL.md`。

不是 awesome-list（那个在 `external-index/`）。是**真东西**——
clone 下来就能用，不需要再访问任何外部仓库。

## 怎么加一条技能

1. 复制 `skills/_TEMPLATE.md` 到 `skills/<your-slug>/SKILL.md`
2. 写 frontmatter，参考 `docs/schema.md`
3. 写正文（4 段 + 例子）
4. `python scripts/validate-skill.py` 跑一遍
5. 开 PR

CI 会校验：frontmatter 字段齐全、`path` 跟 `slug` 一致、
body 段顺序对。

## 一个技能长什么样

```
skills/
  pdf-summarizer/
    SKILL.md              # 必填
    assets/               # 可选，例子里引用的图、JSON、prompt 片段
      example-input.pdf
```

文件名**固定**叫 `SKILL.md`，不是 `skill.md` 也不是 `README.md`。
原因：`install-skill.py` 按这个名字找，rename 之后下游 install
就找不到。

## frontmatter 字段

完整列表看 `docs/schema.md`。必填的几个：

| 字段 | 类型 | 例子 |
|---|---|---|
| `slug` | kebab-case | `pdf-summarizer` |
| `name` | 句子大小写 | `PDF Summarizer` |
| `version` | semver | `0.1.0` |
| `description` | 一句话 | `5-bullet summary of a long PDF, per audience.` |
| `category` | 49 个之一 | `document-processing` |
| `tags` | 2-5 个 | `[pdf, summarization]` |
| `inputs` | object[] | 看 schema |
| `output` | object | 看 schema |
| `author` | string | GitHub handle |
| `license` | SPDX id | `MIT` |
| `created` / `updated` | date | `2026-06-10` |

## 正文 4 段 + 1 段

1. `# When to use` —— 场景，写具体
2. `# Inputs` —— 给人看的版本
3. `# Output` —— 模型要返回什么
4. `# Prompt` —— 实际 prompt
5. `# When NOT to use`（**强烈建议**）—— 边界

外加 `# Example` —— 完整 input → output，**别截断**。

## 一些原则

- **默认平台中立**。只有某段真的需要 vendor SDK 才标
  `platforms: [claude]`，并在那段开头加 `> **Claude-only**`
- **不动 prompt 文字**。哪怕是 typo，源怎么写就怎么写
- **不手动改** `stars` / `license` / `pushed_at`。sync
  脚本会刷，但只刷 `external-index/`，不刷 `skills/`
- **不合并两个技能**。哪怕看起来很像，留两份
- **example 一定给完整**。下游 agent 靠这个对齐输出

## 检查

本地：

```bash
python scripts/validate-skill.py
```

CI 跑同一条命令，过不去就红。

## 删除一条技能

1. `git rm -r skills/<slug>`
2. 从 `skills/_index.yaml` 里删对应行（如果有）
3. 提 PR

不要留空目录。
