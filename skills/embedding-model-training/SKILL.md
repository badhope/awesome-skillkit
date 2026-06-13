---
name: Embedding Model Training
name_zh: 嵌入模型训练
description: 'The user wants to train, fine-tune, or adapt an'
description_zh: 训练或微调嵌入模型 —— 双编码器（密集句向量，用于检索 / 相似度 / 聚类 / 去重）、交叉编码器（pair 
  评分、重排、二分类）、稀疏编码器（SPLADE、可学习的稀疏向量）。覆盖损失函数选择、难负样本挖掘、评估器选择、Matryoshka / LoRA / 蒸馏
  的权衡，以及训练时最常见的坑。
category: applications
tags:
  - ai
  - backend
  - documentation
  - evaluation
  - frontend
source:
license: Apache-2.0
author: 'Hugging Face (downstream pack: badhope)'
version: 0.1.0
needs_review: false
slug: embedding-model-training
created: '2026-06-12'
updated: '2026-06-12'
inputs:
  - name: request
    type: string
    required: true
    description: User request or task description
output:
  format: markdown
  description: Generated content based on the user request
---
# When to use

The user wants to train, fine-tune, or adapt an
embedding model. Typical triggers: "fine-tune a
retrieval model on my data", "train a reranker",
"build a SPLADE index", "make sentence embeddings
that work well on our domain", "improve the
recall of our semantic search".

This skill is the **router** for embedding
training. The output is a plan: which model
class, which loss, which evaluator, which base
model, and which footguns to watch. The actual
training script comes from the per-class
template, not from this skill synthesizing
snippets.

Use this when:

- Training or fine-tuning any bi-encoder
  (sentence-transformers, E5, BGE, GTE,
  Instructor, Nomic, Qwen3-Embedding)
- Training a cross-encoder reranker
- Training a SPLADE / sparse encoder
- Adapting a public embedding model to a
  domain (legal, medical, code, support tickets)
- Adding Matryoshka, LoRA, or distillation to
  an existing training run

**Do not** use this for:

- Using a pretrained embedding model
  unchanged — pick a different skill
- Fine-tuning a generative model (LLM) — that's
  a different skill family
- Clustering / classification of unlabeled
  text — that's a different problem

# Inputs

- `encoder_type` — bi-encoder / cross-encoder /
  sparse-encoder.
- `use_case` — retrieval / similarity /
  clustering / classification / paraphrase /
  dedup / reranking / pair-classification /
  learned-sparse-retrieval.
- `data_shape` — pairs / triples /
  labeled-similarity / classification-labels.
- `training_scale` — laptop / single-gpu /
  multi-gpu / hf-jobs.

# Output

A `## Plan` block (encoder type → loss →
evaluator → base model), a `## Data shape`
block, a `## Training script skeleton` block, a
`## Footguns` block, and a `## Evaluate` block.

# Prompt

```prompt
You are routing an embedding-model training task.
Pick the right combination of (encoder type,
loss, evaluator, base model) for the user's
data and use case. Do not synthesize a training
script from snippets — start from the per-class
production template and copy it as the starting
point. The templates contain load-bearing
scaffolding (autocast helper, model-card class,
logger silencing list, `force=True`, `seed`,
TF32, version-compatible imports, named-
evaluator metric handling) that prior agent runs
have repeatedly missed when rolling their own.

## 1. Pick the encoder type

  - **bi-encoder** — each input encoded
    independently. Use for retrieval,
    similarity, clustering, classification,
    paraphrase mining, dedup. Default for most
    "I need embeddings" tasks.
  - **cross-encoder** — pair encoded jointly.
    Use for reranking, pair classification.
    Slow at query time (no index), but
    higher accuracy.
  - **sparse-encoder** — SPLADE / learned-
    sparse. Use for inverted-index backends
    (Elasticsearch, OpenSearch, Lucene) where
    sparse vectors are a fit.

Tiebreakers when the request is ambiguous:

  - "embedding model" / "vector search" /
    "similarity" → **bi-encoder**
  - "rerank" / "ranker" / "two-stage" →
    **cross-encoder**
  - "SPLADE" / "sparse" / "inverted index" →
    **sparse-encoder**

If still unclear, ask one question.

## 2. Pick the loss (bi-encoder)

Map data shape to loss family:

  - **triples** (anchor, positive, negative) →
    `MultipleNegativesRankingLoss` (default),
    or `CachedMultipleNegativesRankingLoss`
    for large batches
  - **pairs with binary label** → `CoSENTLoss`
    (similarity regression) or
    `ContrastiveLoss`
  - **labeled similarity** (continuous) →
    `CoSENTLoss` or `CosineSimilarityLoss`
  - **classification labels** →
    `SoftMaxLoss`

Footguns:

  - `MultipleNegativesRankingLoss` requires
    `BatchSamplers.NO_DUPLICATES` — otherwise
    positive appears in the negatives.
  - `Cached*` losses are incompatible with
    `gradient_checkpointing`. Pick one.

## 3. Pick the loss (cross-encoder)

  - **single label** → `CrossEntropyLoss`
  - **pointwise score** → `CoSENTLoss` or
    `MarginMSELoss`
  - **pairwise** → `ContrastiveLoss` /
    `SoftContrastiveLoss`
  - **listwise** → `ListNetLoss` /
    `ListMLELoss`
  - **distillation from a stronger reranker** →
    `DistillKLDivergenceLoss`

Footgun: non-BCE losses need
`activation_fn=Identity()`. With sigmoid +
non-BCE, the eval rank silently collapses.

## 4. Pick the loss (sparse-encoder)

  - `SpladeLoss` (wrapper around
    `FlopsLoss` + `SparseMultipleNegativesRankingLoss`)

Footgun: the FLOPS regularizer weight is the
single biggest knob. Too high → model is sparse
but useless. Too low → model is dense, defeats
the point. Start at 1e-4 and tune.

## 5. Pick the evaluator

Map task to evaluator:

  - **bi-encoder retrieval** →
    `InformationRetrievalEvaluator`
  - **bi-encoder similarity** →
    `EmbeddingSimilarityEvaluator`
  - **bi-encoder classification** →
    `ClassificationEvaluator`
  - **cross-encoder reranking** →
    `CrossEncoderRerankingEvaluator`
  - **sparse-encoder retrieval** →
    `SparseNanoBEIREvaluator` (English) or the
    in-domain alternative

Named-evaluator key format for
`load_best_model_at_end`:
`eval_{name}_{primary_metric}`. The metric
**name** (e.g. `ndcg@10`) and the metric
**key** (e.g. `cosine_ndcg@10`) are different
strings. Get them right or `metric_for_best_model`
will reference a missing key and the run will
crash on save.

## 6. Pick the base model

  - **bi-encoder, general English** —
    `sentence-transformers/all-MiniLM-L6-v2`
    (fast baseline), `BAAI/bge-base-en-v1.5`
    (stronger), `intfloat/e5-base-v2`
  - **bi-encoder, multilingual** —
    `intfloat/multilingual-e5-base`,
    `BAAI/bge-m3`
  - **bi-encoder, code** —
    `microsoft/codebert-base`,
    `jinaai/jina-embeddings-v2-base-code`
  - **bi-encoder, prompt-tuned** (E5, BGE,
    Instructor, Nomic, Qwen3-Embedding) — must
    add the `query: ` / `passage: ` prefix
    rules
  - **cross-encoder** —
    `cross-encoder/ms-marco-MiniLM-L-6-v2`
    (fast), `BAAI/bge-reranker-base`
    (stronger)
  - **sparse-encoder** —
    `naver/splade-cocondenser-ensembled-
    distil`

Footgun: ModernBERT-family bases need
`max_seq_length=8192` for the long-context
behaviour, not the default 512. Pick the right
value before training.

## 7. The training script skeleton

Every embedding training run shares this shape:

```python
from sentence_transformers import SentenceTransformer, losses
from sentence_transformers import InputExample, SentencesDataset
from torch.utils.data import DataLoader

model = SentenceTransformer('base-model-id')
train_examples = [
    InputExample(texts=['anchor', 'positive', 'negative']),  # triples
    # ... or pairs: texts=['a', 'b'], label=0.8
]
train_dataset = SentencesDataset(train_examples, model)
train_loader = DataLoader(
    train_dataset,
    shuffle=True,
    batch_size=64,
    drop_last=True  # required for MNRL
)
train_loss = losses.MultipleNegativesRankingLoss(model)

model.fit(
    train_objectives=[(train_loader, train_loss)],
    epochs=2,
    warmup_steps=100,           # not warmup_ratio, deprecated
    evaluator=dev_evaluator,    # optional but recommended
    evaluation_steps=500,
    save_best_model=True,
    output_path='./output',
    # NB: load_best_model_at_end requires
    # save_steps to be a multiple of eval_steps
)
```

## 8. Footguns (cross-cutting)

  - **Never load with `torch_dtype=bfloat16`** —
    always load in fp32, then autocast bf16 /
    fp16 in the training step. Loading in bfloat16
    silently degrades loss.
  - **`save_steps` must be a multiple of
    `eval_steps`** when `load_best_model_at_end=True`.
    Mismatched values cause a "missing
    checkpoint" error at the end of training.
  - **Hub push fails when the model card is
    missing required fields** — fill in
    `language`, `license`, `tags`, and the
    `pipeline_tag` of `feature-extraction`.
  - **Hub push fails when the model is in a
    private org** — set `private=True` or
    `public=True` explicitly. Default has
    changed across `huggingface_hub` versions.
  - **Quantized base model** — do not load a
    `q8` or `q4` model and then train. The
    quantization breaks gradient flow. Load
    fp32, train, quantize after.
  - **Hard-negative mining is the single
    biggest quality lever** — random negatives
    plateau quickly. Mine from a baseline
    retrieval index; cap false negatives by
    cosine threshold.
  - **Matryoshka dims require MatryoshkaLoss
    wrapper** — `MatryoshkaLoss` around
    `MultipleNegativesRankingLoss`. Forgetting
    the wrapper trains a normal model.
  - **LoRA requires `PeftModel` wrapping** —
    `sentence-transformers` does not pick up
    LoRA adapters from `LoraConfig` alone.
    Use the `peft`-aware training helpers.
```

# When NOT to use

- **Use a pretrained model unchanged** — no
  training needed. This skill is for
  fine-tuning.
- **Fine-tune a generative LLM** — that's a
  different skill family (use
  `transformers.Trainer` or TRL).
- **Cluster or classify unlabeled text** —
  this skill assumes you have training pairs
  / triples / labels. Unsupervised clustering
  uses different code paths.
- **You don't have evaluation data** — without
  a dev set you cannot pick the right loss /
  evaluator combination. Stop and ask for
  one.
- **The base model is too large for the
  hardware** — pick a smaller base, not a
  smaller batch. Quantization happens after
  training, not before.
- **Hard-negative mining has never been done**
  on the domain — start with random negatives
  to get a baseline, *then* mine. Mining on
  day one with no baseline produces nonsense
  negatives.

# Example

**Input:**

```yaml
encoder_type: bi-encoder
use_case: retrieval
data_shape: triples
training_scale: single-gpu
```

**Output:**

```markdown
## Plan
- Encoder: bi-encoder
- Base model: `BAAI/bge-base-en-v1.5`
- Loss: `MultipleNegativesRankingLoss` (with
  `BatchSamplers.NO_DUPLICATES`)
- Evaluator:
  `InformationRetrievalEvaluator` (NDCG@10,
  MRR@10, MAP@10) on a held-out dev set
- Training: 2 epochs, batch 64, fp32 +
  autocast bf16, save_best_model=True

## Data shape
- Triples: (anchor, positive, negative) per
  row
- Negative source: BM25 top-100 minus
  positives, capped at 7 per anchor
- Eval set: 1000 (query, positive, hard
  negatives) triples

## Training script skeleton
Start from
`scripts/train_bi_encoder_retrieval_template.py`
(copy, do not synthesize). Required
non-default arguments:

  - `save_steps=1000`, `eval_steps=500`
    (multiple of)
  - `warmup_steps=100` (not ratio)
  - `load_best_model_at_end=True`,
    `metric_for_best_model='cosine_ndcg@10'`
  - `save_total_limit=3`

## Footguns
- ✓ load fp32, autocast bf16
- ✓ BM25-mined hard negatives (not random)
- ✓ `BatchSamplers.NO_DUPLICATES`
- ✓ `max_seq_length=512` (BGE default; do
  not change unless on long-doc task)
- ✓ Hub model card filled with `pipeline_tag`
  = `feature-extraction`, `language=en`,
  `license=apache-2.0`

## Evaluate
- Primary: NDCG@10 (cosine)
- Secondary: MRR@10, MAP@10
- Sanity: distribution of cosine scores
  between random pairs (should be 0.0-0.3)
- Quality: ratio of dev-set positives in
  top-10 of a BM25 hybrid (should be > 0.6
  before training; track delta after)
```
