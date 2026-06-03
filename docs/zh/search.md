# 搜索流水线

AI-SKILL 在技能搜索中使用了**混合检索器**。一条查询会同时经过
词法与稠密两个检索器，两路结果通过倒数排名融合（RRF）合并，
最后再用技能元数据对合并结果进行重排。

## 整体流程

```
                  ┌──────────────┐
   query ───────► │   embed      │ ────► vector (768d)
                  └──────────────┘
                        │
                        ▼
                  ┌──────────────┐
                  │  Qdrant kNN  │ ────► dense top-K
                  └──────────────┘
                        │
                        ▼
                  ┌──────────────┐
                  │   Postgres   │ ────► BM25 top-K (tsvector)
                  │  full-text   │
                  └──────────────┘
                        │
                        ▼
                  ┌──────────────┐
                  │     RRF      │ ────► fused top-N
                  └──────────────┘
                        │
                        ▼
                  ┌──────────────┐
                  │  re-rank     │ ────► final results
                  └──────────────┘
```

## 第 1 步 —— Embedding

默认模型为
[`sentence-transformers/all-mpnet-base-v2`](https://huggingface.co/sentence-transformers/all-mpnet-base-v2)
（768 维，支持多语言）。

模型可通过 `EMBEDDING_MODEL` 配置。切换步骤：

1. 停掉后端。
2. 在 `.env` 中设置 `EMBEDDING_MODEL=BAAI/bge-large-en-v1.5`。
3. 重启。
4. 重建索引：`poetry run python -m app.cli index rebuild --yes`。
5. 再次重启，让新索引生效。

## 第 2 步 —— 向量搜索（Qdrant）

Qdrant 存储每个技能的嵌入向量。查询时，发送查询向量并按余弦
相似度请求 top-K 个技能。

```python
# 摘自 app/services/vector_search.py
results = await qdrant.search(
    collection_name="skills",
    query_vector=embedding,           # 768 维
    limit=50,                         # 多取一些，供重排用
    score_threshold=0.0,              # 后续会重排
)
```

后端启动时，若集合不存在，会自动以正确的维度与余弦相似度配置
创建 Qdrant 集合。

## 第 3 步 —— 词法搜索（Postgres）

同时，针对 `name` 与 `description` 列执行
`to_tsvector` / `plainto_tsquery` 查询。它能覆盖向量检索容易
漏掉的精确匹配（函数名、包名、错误信息等）。

```sql
SELECT id, ts_rank(to_tsvector('english', name || ' ' || description),
                   plainto_tsquery('english', $1)) AS score
FROM skills
WHERE to_tsvector('english', name || ' ' || description)
      @@ plainto_tsquery('english', $1)
ORDER BY score DESC
LIMIT 50;
```

## 第 4 步 —— 倒数排名融合（RRF）

两路结果通过 RRF 合并：

```
RRF_score(d) = Σ  1 / (k + rank_in_list_i(d))
```

其中 `k = 60`（与 [Cormack 等人 2009 论文](https://dl.acm.org/doi/10.1145/1571941.1572114)
中的取值一致）。RRF 对不同检索器之间的评分尺度差异很鲁棒，
且无需学习权重。

## 第 5 步 —— 重排

合并后的列表会经过一组确定性的微调：

- `is_featured` 的技能 +0.05
- `rating_avg` ≥ 4.0 +0.02
- 30 天内新建的技能 +0.01
- `is_public = false` 的技能会被降权，除非请求者是作者或管理员

最终结果按请求的 `limit`（默认 10，最大 100）截断。

## 配置

| 设置                 | 默认值                                       | 位置                              |
|----------------------|----------------------------------------------|-----------------------------------|
| `EMBEDDING_MODEL`    | `sentence-transformers/all-mpnet-base-v2`    | `.env`                            |
| `EMBEDDING_DIMENSION`| 768                                          | `.env`                            |
| `QDRANT_URL`         | `http://localhost:6333`                       | `.env`                            |
| Qdrant collection    | `skills`                                     | 在 service 中硬编码               |
| Lexical k            | 50                                           | `app.services.vector_search`      |
| Vector k             | 50                                           | `app.services.vector_search`      |
| RRF 常数 `k`         | 60                                           | `app.services.vector_search`      |
| 重排加成             | 见上                                         | `app.services.vector_search`      |

## 如何关闭某个检索器

若仅使用向量搜索（例如基准测试），可设置：

```bash
QDRANT_URL=""  # 留空将禁用 Qdrant 客户端
```

若仅使用词法搜索：

```bash
# 在 API 中发送特殊头部：
X-Search-Mode: lexical
```

服务会直接返回 BM25 结果，跳过 RRF 融合。

## 接下来去哪里

- [ADR 002](adr/002-qdrant-vector-search.md) —— 为何选择 Qdrant
- [向量搜索服务源码](https://github.com/badhope/AI-SKILL/blob/main/backend/app/services/vector_search.py)
- [重建索引脚本](https://github.com/badhope/AI-SKILL/blob/main/backend/app/scripts/reindex.py)
