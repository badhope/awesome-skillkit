# ADR 004 — `skills.content` 与 `compositions.items` 的存储形式

- **状态**：已采纳
- **日期**：2026-06-01

## 背景

技能拥有一个自由格式的 `content` 字段（Markdown、代码、引用、参数）。
组合（composition）描述了一个有序的技能列表与对应参数。两者都是用户编写的，
且结构会持续演化。

## 决策

`skills.content` 以 **Postgres JSONB** 形式存储，读取与写入时由 Pydantic v2
校验形状。组合项则放进专用的 `skill_composition_items` 表
（外键指向 `skill_compositions`，加 `skill_id`、`sort_order`、`notes`），
而不是 JSONB 列 —— 关系形式更贴合需求，因为组合项会被查询、排序、手动重排。

## 候选方案

| 方案            | 原因未选                                          |
|-----------------|--------------------------------------------------|
| 纯关系型        | 太僵化；每加一个字段都要迁移                       |
| MongoDB         | 引入第二数据库；与 Postgres 失去 ACID             |
| Text blob       | 无法建索引；无法查询                              |

## 后果

- 在 Pydantic 中添加新 `content` 字段无需数据库迁移。
- 借助 JSONB 的 GIN 索引即可廉价地做"JSON 包含 X"的查询。
- Pydantic v2 保持为 content 模式的单一事实来源。
- 在 composition 中增删/重排条目就是普通的 SQL UPDATE —— 无需 JSON 重写。
- 折衷：任何绕过 Pydantic 的代码（裸 SQL、临时报表）需要自行重新实现校验。
