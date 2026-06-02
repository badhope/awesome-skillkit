# Search pipeline

AI-SKILL uses a **hybrid retriever** for skill search. A query goes
through a lexical and a dense retriever, the two result lists are
fused with reciprocal-rank fusion, and the merged list is re-ranked
using skill metadata.

## High-level flow

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

## Step 1 — Embedding

The default model is
[`sentence-transformers/all-mpnet-base-v2`](https://huggingface.co/sentence-transformers/all-mpnet-base-v2)
(768-dim, multilingual-capable).

The model is configurable via `EMBEDDING_MODEL`. To swap:

1. Stop the backend.
2. Set `EMBEDDING_MODEL=BAAI/bge-large-en-v1.5` in `.env`.
3. Restart.
4. Reindex: `poetry run python -m app.cli index rebuild --yes`.
5. Restart again so the new index is hot.

## Step 2 — Vector search (Qdrant)

Qdrant stores the embedding for each skill. At query time we send the
embedded query and request the top-K skills by cosine similarity.

```python
# from app/services/vector_search.py
results = await qdrant.search(
    collection_name="skills",
    query_vector=embedding,           # 768-dim
    limit=50,                         # over-fetch for re-ranking
    score_threshold=0.0,              # we re-rank downstream
)
```

The Qdrant collection is auto-created on backend startup if it does
not exist, with the right dimension and a cosine similarity
configuration.

## Step 3 — Lexical search (Postgres)

In parallel, a `to_tsvector` / `plainto_tsquery` query runs against
the `name` and `description` columns. This catches exact-match
queries (function names, package names, error messages) that the
vector retriever can miss.

```sql
SELECT id, ts_rank(to_tsvector('english', name || ' ' || description),
                   plainto_tsquery('english', $1)) AS score
FROM skills
WHERE to_tsvector('english', name || ' ' || description)
      @@ plainto_tsquery('english', $1)
ORDER BY score DESC
LIMIT 50;
```

## Step 4 — Reciprocal Rank Fusion (RRF)

The two result lists are merged with RRF:

```
RRF_score(d) = Σ  1 / (k + rank_in_list_i(d))
```

with `k = 60` (the value used by the original [Cormack et al. 2009
paper](https://dl.acm.org/doi/10.1145/1571941.1572114)). RRF is
robust to different score scales between retrievers and does not
require a learned weight.

## Step 5 — Re-ranking

The fused list is re-ranked with a small set of deterministic
adjustments:

- `is_featured` skills get a +0.05 boost
- Higher `rating_avg` (above 4.0) gets a +0.02 boost
- Skills created in the last 30 days get a +0.01 boost
- `is_public = false` skills are demoted unless the requester is the
  author or an admin

The result is then trimmed to the requested `limit` (default 10,
max 100).

## Configuration

| Setting             | Default                                | Where                            |
|---------------------|----------------------------------------|----------------------------------|
| `EMBEDDING_MODEL`   | `sentence-transformers/all-mpnet-base-v2` | `.env`                       |
| `EMBEDDING_DIMENSION` | 768                                  | `.env`                           |
| `QDRANT_URL`        | `http://localhost:6333`                | `.env`                           |
| Qdrant collection   | `skills`                               | hard-coded in the service        |
| Lexical k           | 50                                     | `app.services.vector_search`     |
| Vector k            | 50                                     | `app.services.vector_search`     |
| RRF constant `k`    | 60                                     | `app.services.vector_search`     |
| Re-rank boosts      | as above                               | `app.services.vector_search`     |

## How to disable a retriever

To run with vector search only (e.g. for benchmarking), set:

```bash
QDRANT_URL=""  # empty disables the Qdrant client
```

To run with lexical search only:

```bash
# In the API, send the special header:
X-Search-Mode: lexical
```

The service then returns the BM25 results without RRF fusion.

## Where to go from here

- [ADR 002](adr/002-qdrant-vector-search.md) — why Qdrant
- [Vector search service source](https://github.com/badhope/AI-SKILL/blob/main/backend/app/services/vector_search.py)
- [Reindex script](https://github.com/badhope/AI-SKILL/blob/main/backend/app/scripts/reindex.py)
