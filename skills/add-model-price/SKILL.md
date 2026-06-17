---
name: add-model-price
name_zh:
description: 'Use when editing worker/src/constants/default-model-prices.json, packages/shared/src/server/llm/types.ts,
  pricing tiers, tokenizer IDs, or matchPattern regexes for OpenAI, Anthropic, Bedrock,
  Verte...'
description_zh:
category: finance
tags:
  - ai
  - backend
  - documentation
  - evaluation
  - frontend
needs_review: false
source:
slug: add-model-price
version: '1.0.0'
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
author: AI-SKILL
license: MIT
---
# When to use

Use this skill when you need guidance on add-model-price.

# Inputs

User request or task description.

# Output

Generated content based on the user request.

# Prompt

Follow the guidelines in this skill when working on related tasks.

# Add Model Price

Use this skill for model pricing changes in `worker/` and shared LLM type
updates in `packages/shared/`.

## When to Apply

- Editing `worker/src/constants/default-model-prices.json`
- Editing `packages/shared/src/server/llm/types.ts`
- Adding a new priced model
- Updating provider prices, cache pricing, or tier conditions
- Expanding regex coverage for Bedrock, Vertex, Azure, or provider-prefixed
  model names

## How to Read This Skill

- Use this `SKILL.md` as the high-level workflow and helper index.
- Open only the specific reference file that matches the task.

## Quick Start Checklist

### Adding a New Model

- Gather official pricing from the provider documentation.
- Generate a lowercase UUID for the model entry.
- Create a `matchPattern` that covers supported provider formats.
- Add at least one default pricing tier.
- Insert the pricing entry into `worker/src/constants/default-model-prices.json`.
- Update `packages/shared/src/server/llm/types.ts` if the model should be
  selectable in playground or evaluation flows.
- Validate the JSON after editing.

### Updating an Existing Model

- Update the relevant prices, keys, tiers, or regexes.
- Refresh `updatedAt` to today's ISO-8601 timestamp.
- Validate the JSON after editing.

## Reference Map

| Topic                           | Read this when                                                                        | File                                                                                           |
| ------------------------------- | ------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------- |
| Schema and tier rules           | You need the entry shape or pricing-tier invariants                                   | [references/schema-and-tiers.md](references/schema-and-tiers.md)                               |
| Provider sources and price keys | You need official pricing URLs, per-token conversion, or provider-specific usage keys | [references/provider-sources-and-price-keys.md](references/provider-sources-and-price-keys.md) |
| Match patterns                  | You are editing `matchPattern` regexes or provider coverage                           | [references/match-patterns.md](references/match-patterns.md)                                   |
| Workflow and validation         | You are applying the end-to-end edit process or checking common mistakes              | [references/workflow-and-validation.md](references/workflow-and-validation.md)                 |

## Deterministic Helpers

- Pricing file validator:
  `node .agents/skills/add-model-price/scripts/validate-pricing-file.mjs`
- Match-pattern tester:
  `node .agents/skills/add-model-price/scripts/test-match-pattern.mjs --model <modelName> --accept <sample...> --reject <sample...>`
- Direct regex tester:
  `node .agents/skills/add-model-price/scripts/test-match-pattern.mjs --pattern '(?i)^(openai/)?(gpt-4o)$' --accept gpt-4o openai/gpt-4o --reject gpt-4o-mini`

# When NOT to use

Do not use this skill for tasks outside its scope.

# Example

See the skill content above for practical examples.


# Example

```python
# Use the add-model-price skill
from skill_loader import load_skill

skill = load_skill("add-model-price")
result = skill.execute(params={"key": "value"})
print(result)
```

