# AI-SKILL — 常见问题

通用问题收录于此。结构化的故障排查请见 [docs/zh/troubleshooting.md](docs/zh/troubleshooting.md)。

---

## 什么是 AI-SKILL？

AI-SKILL 是一个可自托管的平台，用于编目、发现和组合 **AI Agent 技能** —— 由 LLM 驱动的 agent 可以使用的模块化能力单元。Skill 约等于其他生态中的"插件"或"工具"。

平台内置搜索引擎、分析仪表盘、评分系统与组合构建器。

## 为什么还要一个技能库？

现存的"技能库"或"agent 库"大多数：

- **绑定单一厂商**（Anthropic、OpenAI、Microsoft）—— 技能不能跨厂商复用。
- **闭源** —— 你无法审计、审查或扩展。
- **单一语言** —— 多数只有 Python，TypeScript / Go 团队被排除在外。

AI-SKILL 是**厂商中立**、**开源**、**多语言**的。

## 默认带技能语料吗？

**不带。** 全新安装的目录是空的。平台是生产可用的；数据集有意不打包进来，这样你完全控制里面装什么。

你可以通过以下方式填充：

- 在 Web UI 中**手动编写**技能
- **导入**社区注册表中的 `skill-pack.zip`
- **编程式**调用 `POST /api/v1/skills`

## 与 LangChain / LlamaIndex / Hugging Face 相比如何？

它们是不同范畴：

| 系统         | 定位                                                |
|----------------|-----------------------------------------------------------|
| LangChain      | 用 Python/JS 写 agent 的框架                    |
| LlamaIndex     | RAG 与数据连接器框架                     |
| Hugging Face   | 模型 + 数据集 + 推理 API 中心                       |
| **AI-SKILL**   | **针对你已构建的技能的编目 + 组合工具**|

AI-SKILL 是补充，不是竞争。你可以用 LangChain **编写**技能，再用 AI-SKILL **编目**它们。

## 用什么模型做向量化？

默认是 [`sentence-transformers/all-mpnet-base-v2`](https://huggingface.co/sentence-transformers/all-mpnet-base-v2)（768 维）。模型可通过 `EMBEDDING_MODEL` 环境变量切换。其他推荐：

- `sentence-transformers/all-MiniLM-L6-v2`（384 维，更快）
- `BAAI/bge-large-en-v1.5`（1024 维，质量更高）
- `intfloat/multilingual-e5-large`（多语言）

切换模型后需要**重建 Qdrant 索引**。

## 能否不用 Qdrant？

可以 —— 把 `QDRANT_URL=""` 置空，后端会回退到 Postgres 纯词法检索（BM25 / ILIKE）。搜索质量会下降，但运行栈更简单。

## 平台能上生产吗？

当前版本**在文档范围内功能完整**，已包含：

- 输入校验
- 鉴权 + RBAC
- 限流
- 审计日志
- OWASP 安全头
- 启动期密钥校验
- `make health-check` 目标
- 备份文档

但它没有在十亿行规模下压测过。如果遇到瓶颈，欢迎提 issue。

## 许可证？

[MIT](LICENSE)。用、改、卖、闭源分发都允许，无附加条款。

## 如何贡献？

读 [CONTRIBUTING.md](CONTRIBUTING.md)。精简版：

1. Fork + 创建分支
2. 编写代码与测试
3. `make lint && make typecheck && make test`
4. 提 PR

## 我发现了一个安全问题，怎么办？

**不要在公开 issue 中提及。** 遵循 [SECURITY.md](SECURITY.md) —— 邮件联系安全负责人，或使用 GitHub 的 [private advisory](https://github.com/badhope/AI-SKILL/security/advisories/new) 表单。

## 如何寻求帮助？

- [GitHub Discussions / Q&A](https://github.com/badhope/AI-SKILL/discussions/categories/q-a) —— 通用问题
- [GitHub Issues](https://github.com/badhope/AI-SKILL/issues) —— bug 与功能请求
- 仪表盘右上角的帮助图标 —— 引导式教程
