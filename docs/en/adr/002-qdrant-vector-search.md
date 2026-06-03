# ADR 002 — Qdrant for vector search

- **Status**: Accepted
- **Date**: 2026-06-01

## Context

We need a vector database that supports:

- 768-dim embeddings (Sentence-BERT) out of the box
- Cosine + dot-product similarity
- Persistent storage
- Self-hostable AND managed (Qdrant Cloud)
- Reasonable operational complexity

## Decision

Adopt **Qdrant 1.9+** as the primary vector store.

## Alternatives considered

| Option    | Why not                                                         |
|-----------|-----------------------------------------------------------------|
| pgvector  | Tight Postgres coupling; slower for kNN at our scale            |
| Milvus    | Heavier ops; less ergonomic Rust + Python client                |
| Weaviate  | Bigger dependency graph; GraphQL-first which we do not need     |
| Pinecone  | Managed-only; vendor lock-in; cost                              |

## Consequences

- Qdrant is docker-friendly, can be added to our existing Compose
  stack with one container.
- The model dimension is configurable (`EMBEDDING_MODEL` env var) so
  we can swap to a smaller model for self-hosted with no code change
  beyond reindexing.
- The vector_search service is the only place that imports
  `qdrant-client`, so we keep the option to add a backend abstraction
  in v1.2.
