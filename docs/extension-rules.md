# 怎么把烂技能改好

`extend-skill.py` 的活儿就是把外面抓来的、写得跟流水账一样
的技能，**改到能用的程度**。4 条规则，按顺序来。
已经满足的就跳过。

## Rule 1 — 把 frontmatter 补全

外面抓来的东西十有八九缺字段。对照 `docs/schema.md`：

缺的常见几个：

- `version` —— 没就写 `0.1.0`
- `inputs` —— 看看 prompt 正文，正文里说了要什么就写什么
- `output` —— 看看 prompt 怎么说输出格式，提取出来；
  实在没提就写个 generic 的
- `category` —— 49 个分类里挑一个最接近的
- `tags` —— 从正文捞 3-5 个小写标签
- `author` —— 没具体作者就写源仓库 owner
- `license` —— 抄源仓库 LICENSE
- `created` / `updated` —— `updated` 是今天，`created`
  能查到源 commit 就写那个日期，查不到就今天

如果 `description` 都缺，写一句一行的 generic
的，**别**写"a powerful, flexible, enterprise-grade..."。
这种词越多越没人信。

凡是猜的字段，就打 `needs_review: true`。

## Rule 2 — 加一个能跑的例子

没 `# Example` 段的技能一律要补。

优先级：

1. **能抄就抄** —— 源仓库有 `examples/` 文件夹就挑一个
2. **自己拼一个** —— 按 `inputs` 里声明的字段填合理值，
   再写一段符合 `output` 形状的输出
3. **实在编不出来** —— 写个最小可用的，加一行
   `<!-- example synthesised by extend-skill.py -->`
   并且打 `needs_review: true`

例子要完整。不要写到一半"……以此类推"。

例子最重要的作用是：**让一个没读过 prompt 的人看一眼
就知道大概输出长什么样**。所以别偷懒写 "result:
a summary"。

## Rule 3 — 把 When NOT to use 写出来

不写"什么时候不要用"的技能会被错用。一定要补。

按这个套路写：

```markdown
# When NOT to use

- **太小的输入** —— 比如 PDF 不到 2 页
- **方向反了** —— 这个技能做 X，不做 Y
- **应该用隔壁那个** —— 在 vault 里如果有更合适的技能
- **绑死了 vendor 能力** —— 必须有 platform-bound 才能跑
```

至少写 3 条，越具体越好。

- ❌ "可能不适用" —— 废话
- ✅ "PDF 不到 2 页不要用" —— 边界清楚

如果实在写不出有意义的边界，**说明这技能本身太模糊**，
不要硬编。打 `needs_review: true`，加个 comment 等人来
看。

## Rule 4 — 把 I/O 契约收紧

外面抓来的 `inputs` / `output` 经常是一段自然语言。
要转成 `docs/schema.md` 里写的结构化形式。

具体怎么转：

- 看到 "URL" —— `type: url`
- 看到 "文件路径" —— `type: path`
- 看到 "数字" —— `type: integer`，有小数才 `number`
- 看到 "可选" —— `required: false`
- 看到 "默认 X" —— `default: X`
- 看到 "X、Y、Z 之一" —— `type: enum, values: [X, Y, Z]`
- 看到 "范围 3-10" —— `constraints: { min: 3, max: 10 }`
- 看到 "输出 JSON" —— `format: json` + `schema:` 块

凡是**猜不出来**的字段 —— 也就是 body 里根本没提，
你又不能凭空写一个 —— 标 `needs_review: true`，
加一行 `<!-- contract incomplete -->`。

## 哪些事情**不**做

明确写出来，划底线：

- **不**编业务知识。源技能说"summarise a PDF"，
  不知道作者想要哪种 summary，就写个 generic 的，
  打 `needs_review`。**瞎猜的 prompt 比薄技能更危险。**
- **不**加源技能没有的输入字段。源没有 `language`，
  你也别加
- **不**改 prompt 文字。prompt 是技能的心脏，
  可以移动、加空格、改 fenced block，**别动词**。
  哪怕是 typo —— 留着，那是原作者的选择
- **不**乱升 version。源说 `0.4.2` 就是 `0.4.2`。
  不因为我们补全了 frontmatter 就 bump 成 `1.0.0`
- **不**合并两个技能。哪怕两个看起来很像，留两份。
  vault 是 collection，不是 single-source-of-truth

## Review 队列

凡是触发了以下任一条，就打 `needs_review: true`：

- Rule 1 里**猜**了某个 frontmatter 字段
- Rule 2 例子是自己**编**的
- Rule 3 的 When NOT to use 写得太泛
- Rule 4 的 I/O 契约**缺信息**

带 `needs_review` 的技能还是会被 commit —— 总比
没有强 —— 但是：

- `validate-skill.py` 会 warn
- 前端在卡片上**视觉上**会标一下（前端设计里有这一条）
- 后续 PR 看了之后可以摘掉这个 flag

不带 `needs_review` 的技能是 release 时的硬要求。
v1.0.0 tag 打的时候，全 `skills/` 必须是干净的。
