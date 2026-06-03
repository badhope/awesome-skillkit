# AI-SKILL

> 一个可自托管的 AI Agent 技能库 — 用来存放、检索、版本化、并组合
> 你的提示词、工具定义和小型可复用工作流。
>
> 我们造它是因为每个项目都在重写同一堆 prompt 胶水代码。
> 把它开源出来，让你不用再重写一遍。

[![License: MIT](https://img.shields.io/github/license/badhope/AI-SKILL)](https://github.com/badhope/AI-SKILL/blob/main/LICENSE)
[![Build](https://img.shields.io/github/actions/workflow/status/badhope/AI-SKILL/ci.yml?branch=main&label=build)](https://github.com/badhope/AI-SKILL/actions/workflows/ci.yml)
[![Release](https://img.shields.io/github/v/release/badhope/AI-SKILL?include_prereleases)](https://github.com/badhope/AI-SKILL/releases)
[![Issues](https://img.shields.io/github/issues/badhope/AI-SKILL)](https://github.com/badhope/AI-SKILL/issues)

[📖 GitHub 仓库](https://github.com/badhope/AI-SKILL) ·
[🚀 快速开始](getting-started/quickstart/) ·
[🧱 架构](architecture/) ·
[📦 部署](deployment/) ·
[🛠️ 运维](operations/) ·
[🤝 参与贡献](community/contributing/)

> 翻译约定：保留所有英文代码块、命令、URL、徽章、文件名、品牌名不译。

---

## 这是什么？

AI-SKILL 是一个小巧的 Web 服务 + UI，用来把 **skill（技能）** ——
也就是 prompt 文本、工具 schema、给 agent 的指令片段 ——
集中存到一个可检索的库里。可以理解为团队 prompt 工具箱的
"私有 Hugging Face"。

一个 skill 本质上就是一个带 YAML frontmatter 的 Markdown 文件：

```yaml
---
name: Summarize a URL
description: Fetches a URL and returns a 3-bullet summary.
tags: [summarization, web]
---

# Summarize a URL
…
```

你可以把它发布到库里、做版本化、加 tag、声明对其它 skill 的依赖，
然后通过搜索栏或 HTTP API 让你的 agent 找到它。

## 为什么要做这个？

我们接触过的大多数团队都会踩同一个坑：Notion 上放着一页
"已审批 prompt"，从来没人更新，里头一半的内容被复制粘贴进了错误
的项目。AI-SKILL 是这个问题的无聊解 ——
git 追踪、版本化、可检索、有正经的 API。

我们不打算替代你的 agent 框架，只是补上**共享技能库**这块
大多数 agent 栈里缺失的拼图。

## 谁会用它？

- **个人开发者**：想找一个地方把跨项目复用的 prompt 集中存好。
- **小团队**：需要一个共享的"已审批"技能库，配上一个非工程师
  也能翻的 UI。
- **工具作者**：想要一个带类型的 Python / TypeScript SDK，
  不用再手撸 REST 调用。

如果你是大型企业、需要商业级的 prompt 管理平台，那大概不是它 —
这种需求市面上有专门的厂商，名单放在
[常见问题 → 替代方案](community/faq/#替代方案) 里。

## 你能拿到什么 {#architecture}

一个可自托管的栈：Web UI、REST API、SDK。全部组件拆解在
[architecture/](architecture/)，技术决策记录在 [adr/](adr/)。

- 浏览、搜索、评分的 Web UI。
- REST API（带 OpenAPI 文档），用程序化方式创建、版本化、拉取技能。
- 混合搜索：向量（Sentence-BERT + Qdrant）+ BM25 关键词，
  权重可按请求调整。
- 每个 skill 走 semver，保留完整的修改审计记录。
- 技能依赖，支持循环检测和 semver 约束。
- Python SDK 和 TypeScript SDK，都带类型。
- JWT 认证、基于角色的访问、按 IP 限流、审计日志。
- Docker Compose 编排，一台机器就能把整套拉起来。

## 快速开始

最快的路径是 Docker：

```bash
git clone https://github.com/badhope/AI-SKILL.git
cd AI-SKILL
cp .env.example .env
docker compose up -d
```

| 服务         | 地址                          |
|--------------|-------------------------------|
| Web UI       | http://localhost:3000         |
| 后端 API     | http://localhost:8000         |
| API 文档     | http://localhost:8000/docs    |
| ReDoc        | http://localhost:8000/redoc   |

第一个注册的用户自动成为管理员。完整走查见
[getting-started/quickstart/](getting-started/quickstart/)。
想一步步来，看 [getting-started/installation/](getting-started/installation/)。

## 五分钟走一遍

栈起来之后，最短的有用闭环长这样：

```python
from skill_sdk import SkillClient

client = SkillClient(base_url="http://localhost:8000")
client.login(email="you@example.com", password="hunter2")

results = client.skills.search(q="summarize a long article", limit=5)
for r in results:
    print(f"{r.score:.2f}  {r.skill.name}")
```

```typescript
import { SkillClient } from "@skill-library/sdk";

const client = new SkillClient({ baseUrl: "http://localhost:8000" });
await client.login({ email: "you@example.com", password: "hunter2" });

const results = await client.skills.search({ q: "summarize a long article", limit: 5 });
for (const r of results) {
  console.log(`${r.score.toFixed(2)}  ${r.skill.name}`);
}
```

纯 HTTP 调用的版本在
[examples/rest/skills.http](https://github.com/badhope/AI-SKILL/blob/main/examples/rest/skills.http) 里。
Postman 集合在 [examples/postman/](https://github.com/badhope/AI-SKILL/tree/main/examples/postman/)。

## 哪些稳，哪些还在打磨

我们尽量在 [路线图](community/roadmap/) 里写得诚实，简要版：

**1.0.0 里比较稳的**

- 技能 CRUD、版本化、依赖、评分。
- 几千条规模内的混合搜索。
- 按 IP 限流（Redis 挂了会自动降级，不影响主流程）。
- 请求级 locale 解析和错误信息本地化（en / zh）。
- 单机 Docker Compose 部署。

**还在打磨的**

- 分析仪表盘是进程内内存的。跑超过一个后端副本的话，数字会
  互相覆盖。
- 没有 SSO、没有团队级隔离。
- TypeScript SDK 的类型是手写的，没从 OpenAPI 自动生成。

## 接下来看哪里

| 想要…                                  | 去…                                        |
|----------------------------------------|--------------------------------------------|
| 5 分钟把它跑起来                       | [快速开始](getting-started/quickstart/)    |
| 搞清各部件怎么串起来                   | [架构](architecture/)                      |
| 部署到正式环境                         | [部署](deployment/)                        |
| 日常运维（日志、备份、安全）           | [运维](operations/)                        |
| 看 SDK 文档                             | [Python SDK](sdks/python/) · [TypeScript SDK](sdks/typescript/) |
| 找可运行的代码                         | [示例](examples/)                          |
| 看我们改了什么                         | [更新日志](community/changelog/)            |
| 报 bug 或提需求                        | [Issue 列表](https://github.com/badhope/AI-SKILL/issues) |
| 帮我们把文档翻译成新语言               | [参与贡献 → 翻译](community/contributing/#翻译) |

## 参与贡献

欢迎贡献。请先扫一眼
[community/contributing/](community/contributing/) ——
不长，里头写了分支命名规范、commit 风格、以及 PR 前必须绿的
测试命令。

容易上手的几个入口：

- [`good first issue`](https://github.com/badhope/AI-SKILL/issues?q=is%3Aissue+is%3Aopen+label%3A%22good+first+issue%22) —
  范围小、有人 review 很快。
- 翻译。文档和 UI 现在是中英双语（en / zh）。
  加一种新语言基本上就是拷一份 `docs/<locale>/`，
  然后在 `docs/mkdocs.yml` 加一行。详见
  [参与贡献 → 翻译](community/contributing/#翻译)。
- 打了 [`help wanted`](https://github.com/badhope/AI-SKILL/issues?q=is%3Aissue+is%3Aopen+label%3A%22help+wanted%22)
  标签的 issue ——
  这些是希望有人搭把手的地方。

## 许可证

MIT — 见 [LICENSE](https://github.com/badhope/AI-SKILL/blob/main/LICENSE)。
