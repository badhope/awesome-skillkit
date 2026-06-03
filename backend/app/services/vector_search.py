from __future__ import annotations

import asyncio
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

import numpy as np
from qdrant_client import QdrantClient
from qdrant_client.http import models as qdrant_models
from qdrant_client.http.exceptions import UnexpectedResponse
from sentence_transformers import SentenceTransformer

from app.core.config import settings


class BM25Scorer:
    # Pure-Python BM25 — fine for a few thousand docs. Once we cross ~10k
    # skills we'll want to swap this for a real inverted index (tantivy
    # or a Postgres GIN column) since doc_freqs gets ugly fast.
    def __init__(self, k1: float = 1.5, b: float = 0.75):
        self.k1 = k1
        self.b = b
        self.documents: Dict[str, str] = {}
        self.doc_lengths: Dict[str, int] = {}
        self.avg_doc_length: float = 0.0
        self.term_freqs: Dict[str, Dict[str, int]] = {}
        self.doc_freqs: Dict[str, int] = {}
        self.total_docs: int = 0

    def _tokenize(self, text: str) -> List[str]:
        return text.lower().split()

    def index_document(self, doc_id: str, text: str) -> None:
        tokens = self._tokenize(text)
        self.documents[doc_id] = text
        self.doc_lengths[doc_id] = len(tokens)
        self.total_docs += 1
        self.avg_doc_length = sum(self.doc_lengths.values()) / self.total_docs

        term_freq: Dict[str, int] = {}
        for token in tokens:
            term_freq[token] = term_freq.get(token, 0) + 1
        self.term_freqs[doc_id] = term_freq

        seen_terms: set = set()
        for token in tokens:
            if token not in seen_terms:
                self.doc_freqs[token] = self.doc_freqs.get(token, 0) + 1
                seen_terms.add(token)

    def remove_document(self, doc_id: str) -> None:
        if doc_id not in self.documents:
            return
        tokens = set(self._tokenize(self.documents[doc_id]))
        for token in tokens:
            if token in self.doc_freqs:
                self.doc_freqs[token] -= 1
                if self.doc_freqs[token] <= 0:
                    del self.doc_freqs[token]
        self.term_freqs.pop(doc_id, None)
        self.doc_lengths.pop(doc_id, None)
        self.documents.pop(doc_id, None)
        self.total_docs -= 1
        if self.total_docs > 0:
            self.avg_doc_length = sum(self.doc_lengths.values()) / self.total_docs
        else:
            self.avg_doc_length = 0.0

    def score(self, query: str, doc_id: str) -> float:
        if doc_id not in self.documents or self.total_docs == 0:
            return 0.0

        query_tokens = self._tokenize(query)
        doc_len = self.doc_lengths[doc_id]
        tf = self.term_freqs[doc_id]
        score = 0.0

        for token in query_tokens:
            if token not in self.doc_freqs:
                continue
            df = self.doc_freqs.get(token, 0)
            if df == 0:
                continue
            idf = np.log(1 + (self.total_docs - df + 0.5) / (df + 0.5))
            term_tf = tf.get(token, 0)
            numerator = term_tf * (self.k1 + 1)
            denominator = term_tf + self.k1 * (1 - self.b + self.b * doc_len / self.avg_doc_length)
            score += idf * numerator / denominator

        return score

    def search(self, query: str, doc_ids: Optional[List[str]] = None, limit: int = 10) -> List[tuple]:
        target_ids = doc_ids if doc_ids else list(self.documents.keys())
        scored = [(doc_id, self.score(query, doc_id)) for doc_id in target_ids]
        scored.sort(key=lambda x: x[1], reverse=True)
        return scored[:limit]


class VectorSearchService:
    # QDRANT_URL is read from settings but the import is local so the
    # rest of the app can boot without qdrant_client installed (used in
    # unit tests that mock the search service entirely).

    def __init__(
        self,
        qdrant_url: Optional[str] = None,
        qdrant_api_key: Optional[str] = None,
        collection_name: str = "skills",
        embedding_model: Optional[str] = None,
        vector_size: Optional[int] = None,
    ):
        # Pull defaults from settings so the index, the search service,
        # and any external scripts (`rebuild-index`, `semantic` CLI) all
        # agree on the same embedding model + vector dimension. Hard-coding
        # these caused a long-running bug where indexed vectors had a
        # different shape from the ones used at query time.
        self.collection_name = collection_name
        self.embedding_model_name = embedding_model or settings.EMBEDDING_MODEL
        self.vector_size = vector_size or settings.EMBEDDING_DIMENSION

        qdrant_url = qdrant_url or getattr(settings, "QDRANT_URL", "http://localhost:6333")
        qdrant_api_key = qdrant_api_key or getattr(settings, "QDRANT_API_KEY", None)

        if qdrant_api_key:
            self.client = QdrantClient(url=qdrant_url, api_key=qdrant_api_key)
        else:
            self.client = QdrantClient(url=qdrant_url)

        self.encoder = SentenceTransformer(self.embedding_model_name, device="cpu")
        self._ensure_collection()

        self.bm25 = BM25Scorer()

    # ---- async wrappers -------------------------------------------------
    # qdrant_client.QdrantClient is sync, and sentence_transformers.encode
    # can be 50-300ms per call. Running them straight from an async route
    # would block the event loop and stall every other request. We
    # push them to a thread pool via asyncio.to_thread; the sync methods
    # are kept for CLI commands that don't care.

    async def asearch_skills(self, *args, **kwargs):
        return await asyncio.to_thread(self.search_skills, *args, **kwargs)

    async def afind_similar_skills(self, *args, **kwargs):
        return await asyncio.to_thread(self.find_similar_skills, *args, **kwargs)

    async def aindex_skill(self, *args, **kwargs):
        return await asyncio.to_thread(self.index_skill, *args, **kwargs)

    async def aindex_skills_batch(self, *args, **kwargs):
        return await asyncio.to_thread(self.index_skills_batch, *args, **kwargs)

    async def adelete_skill_index(self, *args, **kwargs):
        return await asyncio.to_thread(self.delete_skill_index, *args, **kwargs)

    async def arebuild_index(self, *args, **kwargs):
        return await asyncio.to_thread(self.rebuild_index, *args, **kwargs)

    async def ahybrid_search(self, *args, **kwargs):
        return await asyncio.to_thread(self.hybrid_search, *args, **kwargs)

    async def aget_search_suggestions(self, *args, **kwargs):
        return await asyncio.to_thread(self.get_search_suggestions, *args, **kwargs)

    async def aget_collection_info(self, *args, **kwargs):
        return await asyncio.to_thread(self.get_collection_info, *args, **kwargs)

    def _ensure_collection(self) -> None:
        try:
            self.client.get_collection(self.collection_name)
        except UnexpectedResponse:
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=qdrant_models.VectorParams(
                    size=self.vector_size,
                    distance=qdrant_models.Distance.COSINE,
                ),
            )

            self.client.create_payload_index(
                collection_name=self.collection_name,
                field_name="category_id",
                field_schema=qdrant_models.PayloadSchemaType.KEYWORD,
            )
            self.client.create_payload_index(
                collection_name=self.collection_name,
                field_name="is_public",
                field_schema=qdrant_models.PayloadSchemaType.BOOL,
            )
            self.client.create_payload_index(
                collection_name=self.collection_name,
                field_name="name",
                field_schema=qdrant_models.PayloadSchemaType.TEXT,
            )
            self.client.create_payload_index(
                collection_name=self.collection_name,
                field_name="description",
                field_schema=qdrant_models.PayloadSchemaType.TEXT,
            )
            self.client.create_payload_index(
                collection_name=self.collection_name,
                field_name="tags",
                field_schema=qdrant_models.PayloadSchemaType.KEYWORD,
            )

    def _generate_embedding(self, text: str) -> List[float]:
        embedding = self.encoder.encode(text, normalize_embeddings=True)
        return embedding.tolist()

    def _skill_to_text(self, skill: Dict[str, Any]) -> str:
        parts = [
            skill.get("name", ""),
            skill.get("description", ""),
            " ".join(skill.get("tags", [])),
            skill.get("category", ""),
            skill.get("content", ""),
        ]
        return " ".join(p for p in parts if p)

    def _build_payload(self, skill: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "skill_id": str(skill.get("id", "")),
            "name": skill.get("name", ""),
            "description": skill.get("description", ""),
            "category_id": str(skill.get("category_id", "")),
            "tags": skill.get("tags", []),
            "is_public": skill.get("is_public", True),
            "version": skill.get("version", "1.0.0"),
            "author": skill.get("author", ""),
            "usage_count": skill.get("usage_count", 0),
            "rating": skill.get("rating", 0.0),
            "created_at": skill.get("created_at", datetime.now(timezone.utc).isoformat()),
            "updated_at": skill.get("updated_at", datetime.now(timezone.utc).isoformat()),
        }

    def index_skill(self, skill: Dict[str, Any]) -> str:
        skill_id = str(skill.get("id", uuid.uuid4()))
        text = self._skill_to_text(skill)
        vector = self._generate_embedding(text)
        payload = self._build_payload(skill)

        # Use the skill_id as the point id so re-indexing is idempotent
        # (the old `uuid.uuid4()` produced a new id every time → Qdrant
        # accumulated duplicate points for the same skill). Qdrant
        # accepts both UUID and integer ids; a string skill_id is fine
        # and matches what `delete_skill_index` queries by.
        self.client.upsert(
            collection_name=self.collection_name,
            points=[
                qdrant_models.PointStruct(
                    id=skill_id,
                    vector=vector,
                    payload=payload,
                )
            ],
        )

        self.bm25.index_document(skill_id, text)
        return skill_id

    def index_skills_batch(self, skills: List[Dict[str, Any]]) -> List[str]:
        indexed_ids: List[str] = []
        points: List[qdrant_models.PointStruct] = []

        for skill in skills:
            skill_id = str(skill.get("id", uuid.uuid4()))
            text = self._skill_to_text(skill)
            vector = self._generate_embedding(text)
            payload = self._build_payload(skill)

            points.append(
                qdrant_models.PointStruct(
                    id=skill_id,
                    vector=vector,
                    payload=payload,
                )
            )

            self.bm25.index_document(skill_id, text)
            indexed_ids.append(skill_id)

        if points:
            self.client.upsert(
                collection_name=self.collection_name,
                points=points,
            )

        return indexed_ids

    def search_skills(
        self,
        query: str,
        limit: int = 10,
        category_id: Optional[str] = None,
        only_public: bool = True,
    ) -> List[Dict[str, Any]]:
        query_vector = self._generate_embedding(query)

        must_conditions: List[qdrant_models.Condition] = []
        if only_public:
            must_conditions.append(
                qdrant_models.FieldCondition(
                    key="is_public",
                    match=qdrant_models.MatchValue(value=True),
                )
            )
        if category_id:
            must_conditions.append(
                qdrant_models.FieldCondition(
                    key="category_id",
                    match=qdrant_models.MatchValue(value=category_id),
                )
            )

        query_filter = None
        if must_conditions:
            query_filter = qdrant_models.Filter(must=must_conditions)

        results = self.client.search(
            collection_name=self.collection_name,
            query_vector=query_vector,
            limit=limit,
            query_filter=query_filter,
        )

        output: List[Dict[str, Any]] = []
        for hit in results:
            item = dict(hit.payload or {})
            item["score"] = hit.score
            output.append(item)

        return output

    def find_similar_skills(self, skill_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        filter_condition = qdrant_models.Filter(
            must=[
                qdrant_models.FieldCondition(
                    key="skill_id",
                    match=qdrant_models.MatchValue(value=skill_id),
                )
            ]
        )

        source_points = self.client.scroll(
            collection_name=self.collection_name,
            scroll_filter=filter_condition,
            limit=1,
            with_vectors=True,
        )[0]

        if not source_points:
            return []

        source_vector = source_points[0].vector

        results = self.client.search(
            collection_name=self.collection_name,
            query_vector=source_vector,
            limit=limit + 1,
        )

        output: List[Dict[str, Any]] = []
        for hit in results:
            if str(hit.payload.get("skill_id", "")) == skill_id:
                continue
            item = dict(hit.payload or {})
            item["score"] = hit.score
            output.append(item)
            if len(output) >= limit:
                break

        return output

    def delete_skill_index(self, skill_id: str) -> bool:
        filter_condition = qdrant_models.Filter(
            must=[
                qdrant_models.FieldCondition(
                    key="skill_id",
                    match=qdrant_models.MatchValue(value=skill_id),
                )
            ]
        )

        points = self.client.scroll(
            collection_name=self.collection_name,
            scroll_filter=filter_condition,
            limit=100,
        )[0]

        if not points:
            return False

        point_ids = [p.id for p in points]
        self.client.delete(
            collection_name=self.collection_name,
            points_selector=qdrant_models.PointIdsList(points=point_ids),
        )

        self.bm25.remove_document(skill_id)
        return True

    def rebuild_index(self, skills: List[Dict[str, Any]]) -> None:
        self.client.delete_collection(self.collection_name)
        self._ensure_collection()

        self.bm25 = BM25Scorer()

        self.index_skills_batch(skills)

    def hybrid_search(
        self,
        query: str,
        limit: int = 10,
        filters: Optional[Dict[str, Any]] = None,
        vector_weight: float = 0.7,
    ) -> List[Dict[str, Any]]:
        query_vector = self._generate_embedding(query)

        must_conditions: List[qdrant_models.Condition] = []
        if filters:
            if filters.get("only_public"):
                must_conditions.append(
                    qdrant_models.FieldCondition(
                        key="is_public",
                        match=qdrant_models.MatchValue(value=True),
                    )
                )
            if filters.get("category_id"):
                must_conditions.append(
                    qdrant_models.FieldCondition(
                        key="category_id",
                        match=qdrant_models.MatchValue(value=filters["category_id"]),
                    )
                )

        query_filter = None
        if must_conditions:
            query_filter = qdrant_models.Filter(must=must_conditions)

        vector_limit = min(limit * 3, 100)
        vector_results = self.client.search(
            collection_name=self.collection_name,
            query_vector=query_vector,
            limit=vector_limit,
            query_filter=query_filter,
        )

        candidates: Dict[str, Dict[str, Any]] = {}
        for hit in vector_results:
            skill_id = str(hit.payload.get("skill_id", ""))
            item = dict(hit.payload or {})
            item["vector_score"] = hit.score
            candidates[skill_id] = item

        candidate_ids = list(candidates.keys())
        bm25_results = self.bm25.search(query, doc_ids=candidate_ids, limit=len(candidate_ids))
        bm25_scores: Dict[str, float] = {doc_id: score for doc_id, score in bm25_results}

        max_bm25 = max(bm25_scores.values()) if bm25_scores else 1.0

        for skill_id, item in candidates.items():
            norm_bm25 = (bm25_scores.get(skill_id, 0.0) / max_bm25) if max_bm25 > 0 else 0.0
            vector_score = item.get("vector_score", 0.0)
            combined = vector_weight * vector_score + (1 - vector_weight) * norm_bm25
            item["score"] = combined
            item["bm25_score"] = norm_bm25

        ranked = sorted(candidates.values(), key=lambda x: x["score"], reverse=True)
        return ranked[:limit]

    def get_search_suggestions(self, prefix: str, limit: int = 10) -> List[str]:
        # 设计要点:
        # 1) `name` 字段是 TEXT 索引 (在 _ensure_collection 里建的), 用 MatchText
        #    做全文本 token 匹配, 比全表 scroll 强几个数量级, 且没有 1000 截断.
        # 2) `tags` 字段是 KEYWORD 索引, Qdrant 不支持前缀过滤, 只能 scroll 拉.
        #    用分页 + 早停 (凑够 limit 就返回), 且给一个 max_pages 安全上限.
        # 3) tag 本身在生产里数量级有限 (几百个), 但和 skill 文档数线性挂钩;
        #    旧实现一次 scroll 1000 在数据多的时候会漏, 切到分页是必须.
        if not prefix:
            return []

        prefix_lower = prefix.lower()
        candidates: set = set()

        # ---- name: 用 TEXT 索引的 MatchText 走索引 ----
        name_filter = qdrant_models.Filter(
            must=[
                qdrant_models.FieldCondition(
                    key="name",
                    match=qdrant_models.MatchText(text=prefix_lower),
                )
            ]
        )
        try:
            name_hits, _ = self.client.scroll(
                collection_name=self.collection_name,
                scroll_filter=name_filter,
                limit=max(limit * 2, 50),
                with_payload=["name"],
            )
        except UnexpectedResponse:
            name_hits = []
        for hit in name_hits:
            name = hit.payload.get("name", "")
            if name and name.lower().startswith(prefix_lower):
                candidates.add(name)

        # ---- tags: 分页 scroll, 凑够 limit 早停 ----
        tag_suggestions: set = set()
        seen_tags: set = set()
        next_offset = None
        page_size = 200
        max_pages = 20  # 20 * 200 = 4000 文档, 远超典型 tag 集合

        for _ in range(max_pages):
            try:
                points, next_offset = self.client.scroll(
                    collection_name=self.collection_name,
                    limit=page_size,
                    offset=next_offset,
                    with_payload=["tags"],
                )
            except UnexpectedResponse:
                break
            if not points:
                break
            for point in points:
                for tag in point.payload.get("tags", []):
                    if tag in seen_tags:
                        continue
                    if str(tag).lower().startswith(prefix_lower):
                        seen_tags.add(tag)
                        tag_suggestions.add(f"tag:{tag}")
                        if len(tag_suggestions) >= limit:
                            break
                if len(tag_suggestions) >= limit:
                    break
            if next_offset is None:
                break

        candidates.update(tag_suggestions)
        return sorted(candidates)[:limit]

    def get_collection_info(self) -> Dict[str, Any]:
        info = self.client.get_collection(self.collection_name)
        count_result = self.client.count(
            collection_name=self.collection_name,
            count_filter=None,
            exact=True,
        )
        return {
            "name": self.collection_name,
            "vectors_count": count_result.count,
            "vector_size": info.config.params.vectors.size,
            "distance": str(info.config.params.vectors.distance),
        }
