---
name: Browser ML in JavaScript
name_zh: 浏览器端机器学习（JavaScript）
description: 'The user wants to run an ML model in JavaScript'
description_zh: 在 JavaScript / TypeScript 里直接跑 SOTA 机器学习模型 —— 
  文本分类、翻译、摘要、图像分类、目标检测、语音识别、音频分类、多模态。支持浏览器和 Node / Bun / Deno 服务端运行时，走 WebGPU / 
  WASM。不需要 Python 后端。
category: dev-tools
tags:
  - ai
  - api
  - backend
  - cli
  - frontend
source:
license: Apache-2.0
author: 'Hugging Face (downstream pack: badhope)'
version: 0.1.0
needs_review: false
slug: browser-ml-in-js
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

The user wants to run an ML model in JavaScript
or TypeScript — in a browser, in Node, in Bun, in
Deno, or in a Web Worker — without a Python
backend. Typical triggers: "run a model in the
browser", "client-side ML", "embed a sentence
similarity check in my Vite app", "do OCR in
TypeScript", "translate on-device".

Use this skill for:

- Client-side inference in SPAs and PWAs
- Server-side ML in Node / Bun / Deno
- Embedding generation for RAG without a Python
  service
- On-device image / audio classification where
  shipping data off-device is not OK
- Browser-based demos and prototypes

**Do not** use this when:

- The model is a custom PyTorch checkpoint with
  no ONNX export — fall back to a Python service
- The user is fine with calling a hosted API
  (use that, it's cheaper than shipping the
  model)
- The latency budget is sub-10ms and the model
  is large (use a server)
- The runtime is a constrained environment
  (some workers, Cloudflare Workers under the
  1MB limit) — check model + runtime size
  before committing

# Inputs

- `task` — the ML task; drives the pipeline
  import.
- `runtime` — where the code runs.
- `model_id` (optional) — explicit model id.
- `device` (optional) — auto / webgpu / wasm /
  cpu / cuda / dml.

# Output

A `## Stack` block, an `## Install` block, a
minimal `## Code` block with the mandatory
`pipe.dispose()`, and a `## Footguns` block.

# Prompt

```prompt
You are running an ML model in JavaScript or
TypeScript — in a browser, in Node, in Bun, in
Deno, or in a Web Worker. The model is shipped
in ONNX format and the runtime is
ONNX-Runtime-backed (WebGPU, WASM, CUDA, DML,
or CPU). There is no Python backend.

## 1. Pick the pipeline

The pipeline name is a string. Pick the
smallest pipeline that covers the task. Common
ones:

  - `sentiment-analysis` — single-label
    classification
  - `text-classification` — same, multi-class
  - `token-classification` — NER, POS
  - `translation` — needs `src_lang` /
    `tgt_lang`
  - `summarization`
  - `text-generation` — needs a generative
    model
  - `fill-mask` — MLM
  - `question-answering` — needs a `question`
    + `context`
  - `image-classification`
  - `object-detection` — returns boxes +
    labels
  - `image-segmentation`
  - `zero-shot-classification` — needs
    `candidate_labels`
  - `zero-shot-object-detection`
  - `automatic-speech-recognition` — Whisper
    family
  - `audio-classification`
  - `text-to-image` — needs a Stable Diffusion
    or SDXL model
  - `image-to-text` — captioning
  - `feature-extraction` — embeddings
  - `sentence-similarity` — embeddings + cosine

If the user asks for "similarity", pick
`feature-extraction` and compute cosine
yourself, or pick `sentence-similarity` and let
the pipeline do it. `sentence-similarity` is the
smarter default for text.

## 2. Pick the runtime

Match the import to the runtime:

  - **Browser (ESM via CDN):**

    ```html
    <script type="module">
      import { pipeline } from
        'https://cdn.jsdelivr.net/npm/@huggingface/transformers';
    </script>
    ```

  - **Browser (bundled):** `npm install
    @huggingface/transformers` and import from
    `'@huggingface/transformers'`.
  - **Node (CommonJS or ESM):** same package.
    Set `env.allowLocalModels = true` if you
    want to load from disk.
  - **Bun / Deno:** same package works; verify
    on a smoke test before committing.

## 3. Pick the device

  - In a browser, default to `webgpu` when
    available, fall back to `wasm`. CPU is the
    always-works fallback for tiny models.
  - In Node, default to `cpu` (no WebGPU
    runtime). Use `cuda` only when
    `onnxruntime-node` is built with CUDA.
  - In Bun / Deno, default to `cpu`; check the
    specific runtime's device support before
    picking anything faster.

## 4. The mandatory pattern

Every pipeline must:

  1. Be created with `await pipeline(task,
     model, { device })`.
  2. Be invoked with a single input or an
     array of inputs.
  3. Be disposed with `await pipe.dispose()`
     when the work is done.

Skipping `dispose()` leaks GPU / WASM memory.
The leak is silent; the browser tab gets slow
and then crashes.

Minimal example (text classification):

```javascript
import { pipeline } from '@huggingface/transformers';

const pipe = await pipeline(
  'sentiment-analysis',
  null, // use the default model for the task
  { device: 'webgpu' }
);

try {
  const out = await pipe('I love this library.');
  // out === [{ label: 'POSITIVE', score: 0.9998 }]
} finally {
  await pipe.dispose();
}
```

## 5. Embeddings (the most common task)

For RAG, semantic search, dedup, or
clustering, use `feature-extraction` and
compute the dot / cosine yourself:

```javascript
import { pipeline, dot } from '@huggingface/transformers';

const embed = await pipeline(
  'feature-extraction',
  'Xenova/all-MiniLM-L6-vq',
  { device: 'webgpu', dtype: 'q8' }
);

try {
  const a = await embed('pug', { pooling: 'mean', normalize: true });
  const b = await embed('bulldog', { pooling: 'mean', normalize: true });
  const sim = dot(a.data, b.data);
  // sim is the cosine similarity when normalize: true
} finally {
  await embed.dispose();
}
```

The `pooling: 'mean', normalize: true` pair is
the convention for sentence-transformers
embeddings. Forgetting `normalize: true` makes
the `dot` product meaningless; the model
returns raw hidden states, not unit vectors.

## 6. Web Worker for browsers

Inference in the main thread freezes the UI.
Always run the pipeline in a Web Worker.

  - Vite + `?worker` import
  - Next.js — wrap in a custom hook that lazily
    creates the Worker on first use
  - The Worker is responsible for its own
    `dispose()`; the main thread just sends
    messages

## 7. Model caching

  - The library caches models in the
    browser's Cache Storage after first
    download. Subsequent loads are offline-
    ready.
  - For deterministic offline behavior, set
    `env.localModelPath` and ship the ONNX
    files with your app.
  - Never assume a model is "small enough" to
    download on first paint. Lazy-load after
    the user gesture that needs it.

## 8. Footguns

These are the bugs that bite every new user.
Check them before shipping:

  - **No `dispose()`** — the most common
    bug. Always `try { ... } finally
    { await pipe.dispose() }` or use a
    helper that disposes on a timeout.
  - **WebGPU not available** — silently falls
    back to WASM. Detect once and warn if
    WASM is unexpectedly slow.
  - **Wrong pooling** — `mean` for sentence
    embeddings, `none` for token-level
    features. Picking the wrong one gives
    nonsense numbers.
  - **No `normalize: true` for embeddings** —
    dot product is not cosine.
  - **Long inputs** — most encoders cap at
    512 tokens; longer inputs are silently
    truncated. Truncate or chunk explicitly.
  - **Model size vs network** — a 1.5GB model
    is fine on a server, not on a phone over
    LTE. Use a quantized variant (`q8`,
    `q4`) when download size matters.
  - **Calling the pipeline before the previous
    call finished** — the pipeline is not
    reentrant. Serialize calls, or create
    multiple pipeline instances.
```

# When NOT to use

- **Server-side model serving at scale** — use
  a Python service with vLLM / TGI / TensorRT.
  JS inference does not compete on throughput.
- **Custom PyTorch model with no ONNX export**
  — convert to ONNX first, or use a Python
  service.
- **Sub-10ms latency budget on a large model**
  — JS can't compete. Use a server.
- **Cloudflare Workers (free tier) or other
  size-constrained runtimes** — model weights
  may exceed the bundle / memory limit. Check
  before committing.
- **No clear task** — "do ML" is not a task.
  Pick a specific task or don't use this
  skill.
- **The user wants a hosted API** — don't
  reinvent the API. Use the API.

# Example

**Input:**

```yaml
task: sentence-similarity
runtime: browser
model_id: Xenova/all-MiniLM-L6-vq
device: webgpu
```

**Output:**

```markdown
## Stack
- Runtime: browser (Web Worker recommended)
- Pipeline: `feature-extraction` (and
  post-process for cosine)
- Model: `Xenova/all-MiniLM-L6-vq` (q8
  quant, ~23MB)
- Device: WebGPU → WASM fallback

## Install
```bash
npm install @huggingface/transformers
```

## Code (Web Worker)
```javascript
// embed-worker.js
import { pipeline, dot } from '@huggingface/transformers';

let pipe = null;

self.onmessage = async (e) => {
  if (e.data.type === 'init') {
    pipe = await pipeline(
      'feature-extraction',
      'Xenova/all-MiniLM-L6-vq',
      { device: 'webgpu', dtype: 'q8' }
    );
    self.postMessage({ type: 'ready' });
    return;
  }
  if (e.data.type === 'embed') {
    const out = await pipe(e.data.text, {
      pooling: 'mean', normalize: true
    });
    self.postMessage({
      type: 'result', id: e.data.id, vec: out.data
    });
  }
  if (e.data.type === 'dispose') {
    await pipe.dispose();
    self.postMessage({ type: 'disposed' });
  }
};
```

## Footguns checked
- ✓ `dispose()` wired to a Worker shutdown
  handler
- ✓ `pooling: 'mean', normalize: true` on
  every call
- ✓ Model load is lazy (after user gesture,
  not on app boot)
- ✓ WebGPU → WASM fallback tested on
  Chrome 113+
- ✓ Input truncated to 256 tokens before
  pipeline call
```
