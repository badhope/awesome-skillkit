---
name: PDF Vision Extractor
name_zh: PDF 视觉抽取器
description: 从扫描版 PDF 抽取发票号、日期、金额等字段，靠 Claude vision。
description_zh: 从扫描版 PDF 抽取发票号、日期、金额等字段，靠 Claude vision。
category: multimodal
tags:
  - ai
  - documentation
  - javascript
  - llm
  - typescript
source: null
license: MIT
author: badhope
version: '0.1.0'
platforms:
  - claude
needs_review: false
slug: pdf-vision-extractor
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

> **Claude-only** — 这个技能假设模型有 vision 能力读 PDF 里的图像。
> Codex / GPT-4o vision 也能跑，但 prompt 是按 Claude 调的；
> Cursor / Continue 走纯文本路径时直接挂。

文档是**扫描版或图像版**（不是带文本层的 PDF），你需要从里面
抽几个结构化字段。典型场景：发票号 + 日期 + 金额、合同里的甲乙
双方 + 金额、收据的商户名 + 流水号。

schema 由调用方指定，所以同一份 prompt 适配不同表单 —— 发票、
合同、收据、HSE 报告都能套。

**不**用于：

- 文本 PDF（用 `pdf-summarizer` 或者直接抽文本）
- 不规则手写（识别率低，超出 v1 范围）
- 多语种混排小语种（>10 个不同字体时，vision 容易串）

# Inputs

| 字段 | 说明 |
|---|---|
| `pdf_path` | 扫描版 PDF 的本地路径 |
| `schema` | 你要抽什么字段。**必填** —— 不传 schema 这个技能不知道该抽什么 |
| `pages` | 只看哪几页，省略 = 通读 |

`schema` 的形状：

```yaml
schema:
  invoice_no: { type: string, description: 发票号 }
  total:      { type: number, description: 含税总额 }
  currency:   { enum: [CNY, USD, EUR] }
  issued_at:  { type: string, description: YYYY-MM-DD }
```

模型不严格按 schema 类型返回 —— 数字字段可能返回字符串，
需要上游 `float()` 转换。这是已知边界，不在 v1 处理。

# Output

JSON，shape：

```json
{
  "extracted": { /* 按 schema 填，没找到的字段省略 */ },
  "confidence": 0.85,
  "missing": ["currency"]
}
```

`confidence` 是模型自评的 0-1 数，**不可信**。仅供排序 / 筛选用。
真要校验请用 schema 校验 + 业务规则（金额 > 0、日期合法等）。

# Prompt

```prompt
You have vision. The user will give you a PDF (scanned / image-based)
and a JSON schema. Look at every page they allow you to see, then
extract the requested fields.

Rules:

- Read top-to-bottom, left-to-right. Tables come in row order.
- Numbers: drop thousand separators, keep decimal point.
  "$1,234.50" → 1234.50, "￥1.234,50" → 1234.50.
- Dates: always emit YYYY-MM-DD. "March 5, 2024" → 2024-03-05.
- Enum fields: pick the closest enum value, even if the doc says
  it slightly differently. "RMB" → CNY.
- Missing fields: don't guess. If the doc doesn't show the field,
  omit it from `extracted` and add it to `missing`.
- Multi-page: aggregate across all allowed pages, prefer the
  canonical / summary line over individual line items.

Output JSON only, no prose. Schema:

{
  "extracted": <object with extracted fields, matching input schema>,
  "confidence": <number 0-1, your self-assessed certainty>,
  "missing": [<field names you couldn't find>]
}

Be terse in confidence — 0.9+ only when the field is clearly
printed; 0.5-0.8 when partially obscured; <0.5 when you're guessing.
```

# When NOT to use

- **PDF 有文本层** —— 直接 `pdftotext` 抽出来更准，跑 vision 是浪费钱
- **表格横跨多页且每页重复表头** —— vision 可能重复抽取，需要预处理裁切
- **手写笔记 / 医生处方** —— 字符识别率 60-70%，不是这个技能的目标场景
- **要 100% 准确** —— vision 永远不是 100% 准，要这种保证就上 OCR + 人工复核
- **要原图坐标 / bounding box** —— 这个技能不返回坐标，要用专门的文档理解模型

# Example

**Input:**

```yaml
pdf_path: ./invoices/2024-03-acme.pdf
schema:
  invoice_no: { type: string, description: 发票号 }
  issued_at:  { type: string, description: 开票日期 YYYY-MM-DD }
  total:      { type: number, description: 含税总额 }
  currency:   { enum: [CNY, USD, EUR] }
  vendor:     { type: string, description: 销方名称 }
```

**Output:**

```json
{
  "extracted": {
    "invoice_no": "INV-2024-03381",
    "issued_at":  "2024-03-15",
    "total":      12750.00,
    "currency":   "CNY",
    "vendor":     "上海某某科技有限公司"
  },
  "confidence": 0.88,
  "missing": []
}
```
