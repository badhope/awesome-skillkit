---
name: PDF Summarizer
name_zh:
description: number of bullets in the summary
description_zh:
category: multimodal
tags:
  - ai
  - api
  - documentation
  - frontend
  - llm
source:
license: MIT
author: badhope
version: '1.0.0'
needs_review: false
slug: pdf-summarizer
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

The user has handed you a PDF (paper, report, contract, README-as-PDF) and wants the gist without reading 50 pages. You have access to a PDF reader.

# Inputs

A `pdf_path` is mandatory. `audience` and `length` are optional with sensible defaults (PM, 5 bullets).

# Output

Markdown with:

1. A one-line TL;DR
2. N bullets (3-10) covering the main points
3. A "What's missing" line — be honest about what you couldn't tell from the PDF

# Prompt

```prompt
You are a careful reader, not a bullshitter. The user has handed you a PDF.

Step 1: Read the first 2 pages and the headings of the rest. If the PDF
        is purely a scanned image (no extractable text), say so and stop.

Step 2: Write a one-line TL;DR. No more than 20 words. If you can't,
        the user needs to know.

Step 3: Write N bullets. Each bullet = one claim, ≤ 25 words. Order
        by importance, not by appearance in the text. The first
        bullet is the most important thing in the document.

Step 4: Add a "What's missing" line. What would a careful reader
        still want to know that you didn't cover? Examples:
        methodology, sample size, counter-arguments, code, screenshots.

Rules:
- Never invent numbers, authors, dates, or citations.
- If the PDF is in a language you don't read, say so.
- If a section is irrelevant to the audience, drop it.
- Do not include "In conclusion" or "In this document".
```

# When NOT to use

- The user wants a literal extract, not a summary. Use a different skill.
- The PDF is a fillable form, code, or a presentation slide deck — those need a different tool.
- The user asked "is this real?" or "is this legal?" — that's fact-checking, not summarising. Out of scope.
- The PDF is over 200 pages. Split it first, or warn the user you'll take a long time.

# Example

**Input:**

```yaml
pdf_path: /tmp/q3-earnings.pdf
audience: exec
length: 4
```

**Output:**

```markdown
**TL;DR:** Q3 revenue beat consensus by 4%, driven by enterprise; full-year guidance unchanged.

- Enterprise ARR grew 28% YoY, the strongest segment this quarter
- Gross margin compressed 1.2 pp due to a one-time cloud cost
- Cash burn slowed to $8M/month; runway extended to 22 months
- Hiring freeze remains in place; 2 open reqs in engineering

**What's missing:** cohort retention numbers, customer concentration, full P&L
```
