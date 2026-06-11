---
slug: llm-pricing-file-update
name: LLM Model Pricing File Update
name_zh: LLM 模型价目文件更新
version: 0.1.0
description: Add or update an LLM model's entry in a per-token pricing JSON — matchPattern regex for cross-provider IDs, pricing tiers, cache pricing, tokenizer alignment, and the schema validation that has to run before the change ships.
description_zh: 在 per-token 价目 JSON 里新增/修改 LLM 模型条目 —— 跨 provider ID 的 matchPattern regex、定价 tier、缓存价格、tokenizer 对齐，以及变更上线前要跑的 schema 校验。

category: observability
tags: [pricing, llm, cost, monitoring, ops]
platforms: []

inputs:
  - name: pricing_file
    type: path
    required: true
    description: |
      Absolute path to the JSON file that holds the per-model price
      entries. The schema is repo-specific (a single `models` array,
      each entry with `id`, `matchPattern`, `tiers`, `tokenizer`,
      `updatedAt`).
  - name: action
    type: enum
    required: true
    values: [add, update]
    description: |
      `add` for a brand-new model; `update` for changing prices,
      tiers, tokenizer, or regex on an existing entry.
  - name: model_spec
    type: object
    required: true
    description: |
      The model spec. Fields:
        - `id`: canonical model id, e.g. `gpt-4o`, `claude-opus-4-5`
        - `provider_prefixes`: list of strings the regex must
          accept (e.g. `['openai/gpt-4o', 'gpt-4o-2024-08-06']`)
        - `provider`: one of openai / anthropic / bedrock / vertex
          / azure / gemini
        - `tokenizer`: the tokenizer name/id used to convert usage
          to tokens (e.g. `o200k_base`, `claude`, `gemini`)
        - `tiers`: list of pricing tiers; at least one default tier
          with `input_cost_per_1m_tokens`,
          `output_cost_per_1m_tokens`, optional
          `cache_read_cost_per_1m_tokens`
        - `source_url`: official pricing URL from the provider
  - name: types_file
    type: path
    required: false
    description: |
      Optional path to the TS type module that lists selectable
      models. If your playground / eval flow only allows whitelisted
      models, update this file too.

output:
  format: text
  description: |
    Confirmation of the diff applied to the pricing file (and
    types file, if any), the regex self-check result against
    the supplied sample names, and a list of any downstream
    consumers that might need a refresh.
  schema:
    type: object
    properties:
      diff_summary: { type: string, description: "What changed: id, fields, timestamps" }
      regex_self_check: { type: object, description: "{accept: [names accepted], reject: [names rejected]}" }
      validation_result: { type: string, enum: [pass, fail] }
      downstream_consumers: { type: array, items: { type: string } }

author: "Langfuse (downstream pack: badhope)"
license: MIT
source:
  url: https://github.com/langfuse/langfuse/tree/main/.agents/skills/add-model-price
  ref: main
  commit: latest
created: 2026-06-10
updated: 2026-06-10
---

# When to use

You maintain an internal **per-token LLM pricing data file** —
a JSON your product reads to convert raw token usage into USD
for cost dashboards, billing, and budget alerts. New model
releases, price drops, and tokenizer changes mean the file is
never done.

The work splits into three concerns:

1. **Coverage.** A new model id like `gpt-4.1-turbo` arrives
   under many names: `gpt-4.1-turbo`, `openai/gpt-4.1-turbo`,
   `azure/gpt-4.1-turbo-2025-04`, `gpt-4.1-turbo-2025-04-15`.
   Your `matchPattern` regex needs to catch the canonical id
   and the per-provider variants without catching lookalikes
   (`gpt-4.1`, `gpt-4.1-turbo-mini`).
2. **Pricing accuracy.** Pull prices from the provider's
   official page. Per-million-token input / output / cache
   read. Optional tier conditions (volume discounts, batch
   pricing, prompt-cache writes). Convert to the unit your
   file uses (per-token, per-1k, per-1m — pick one and stick
   with it).
3. **Validation.** A regex that matches nothing is silent
   death — usage falls through to a default tier (or zero
   cost) and the dashboard lies. A regex that matches too much
   is wrong attribution. Run the regex tester against a
   known-accept list and a known-reject list before shipping.

**Don't use this skill for** the API call to the model itself
(that's normal client code), or for invoice reconciliation
(that's a separate process against the bill from your
provider). And don't use it for cost allocation across
teams — that's tagging, not pricing.

# Inputs

| Field | Required | Notes |
|---|---|---|
| `pricing_file` | yes | Absolute path to the JSON price file. |
| `action` | yes | `add` for a new model, `update` for changes. |
| `model_spec` | yes | The model data: id, prefixes, provider, tokenizer, tiers, source URL. |
| `types_file` | no | TS module listing selectable models (if applicable). |

# Output

Plain-text confirmation. Typical return:

```
Diff applied to worker/src/constants/default-model-prices.json:
  + gpt-4.1-turbo
    matchPattern: (?i)^(openai/|azure/)?(gpt-4\.1-turbo)(-[0-9]{4}-[0-9]{2}-[0-9]{2})?$
    tokenizer: o200k_base
    tiers: [{ input: 2.50, output: 10.00, cache_read: 1.25 }]
    updatedAt: 2026-06-10

Diff applied to packages/shared/src/server/llm/types.ts:
  + "gpt-4.1-turbo"

Regex self-check:
  accept: gpt-4.1-turbo, openai/gpt-4.1-turbo, azure/gpt-4.1-turbo-2025-04
  reject: gpt-4.1, gpt-4.1-turbo-mini, gpt-4.1-turbo-32k
  all 3 / 3 accept, 0 / 3 false-positive

Schema validation: pass
Downstream consumers that may need a refresh:
  - playground model selector
  - eval cost rollup job
  - monthly budget alert thresholds
```

# Prompt

```prompt
You are updating a per-token LLM pricing data file. Follow the
order. Do not skip the regex self-check — a regex that matches
nothing is silent death.

1. Decide: add or update?

   `add`    — the model id does not appear in the file at all
   `update` — the id exists, but prices, tiers, regex, or
              tokenizer change

2. For `add`: gather the model spec.

   - Canonical id (what the provider calls the model in their
     official pricing page).
   - Provider prefixes: list the strings your platform will
     see in the wild. At minimum:
       - bare:         `gpt-4.1-turbo`
       - with prefix:  `openai/gpt-4.1-turbo`
       - per-provider: `azure/gpt-4.1-turbo-2025-04-15`
       - per-dated:    `gpt-4.1-turbo-2025-04-15`
   - Provider: openai | anthropic | bedrock | vertex | azure
     | gemini. Drives which pricing conventions apply
     (cache read vs cache write, batch discount, etc.).
   - Tokenizer: the actual tokenizer name the model uses,
     not the model name. `o200k_base`, `claude`, `gemini`,
     `p50k_base`. Mismatches here silently under- or
     over-count tokens.
   - Source URL: the official pricing page. REQUIRED.
     Do not invent prices.

3. Write the entry.

   Shape (one entry per model):

     {
       "id": "gpt-4.1-turbo",
       "matchPattern": "(?i)^(openai/|azure/)?(gpt-4\\.1-turbo)(-[0-9]{4}-[0-9]{2}-[0-9]{2})?$",
       "tokenizer": "o200k_base",
       "tiers": [
         {
           "name": "default",
           "input_cost_per_1m_tokens": 2.50,
           "output_cost_per_1m_tokens": 10.00,
           "cache_read_cost_per_1m_tokens": 1.25
         }
       ],
       "updatedAt": "2026-06-10"
     }

   Rules:
     - `matchPattern` MUST anchor with `^` and `$` so
       `gpt-4.1` does NOT match `gpt-4.1-turbo`.
     - Use `(?i)` for case insensitivity unless the
       provider is strict-case.
     - Always include the dated variant as optional
       (`(-[0-9]{4}-[0-9]{2}-[0-9]{2})?$`).
     - At least one tier, named `default`.
     - `updatedAt` is today's ISO-8601 date.

4. For `update`: only change what changed.

   Do NOT rewrite the entry. Update prices, regex, tokenizer,
   or tier names in place. Always refresh `updatedAt`.

5. Update the types file (if applicable).

   If your product has a TypeScript union / enum of allowed
   model ids, append the new id. Do not alphabetize for
   the sake of alphabetizing — preserve the order of
   existing entries; new entries go at the end.

6. Run the regex self-check.

   Use the supplied tester. Pass at least:
     - 3 accept samples (canonical, prefixed, dated)
     - 3 reject samples (predecessor, suffix variant,
       unrelated model in the same family)

   If any accept fails → regex is wrong, fix it.
   If any reject passes → regex is greedy, tighten it.

7. Validate the JSON file.

   Run the file's validator (a node script in your repo
   that re-parses the JSON and checks tier invariants:
   non-negative prices, `input < output` is NOT enforced —
   some providers charge more for input, e.g. Claude
   Opus with prompt caching, but the validator should
   check `>= 0`).

8. List downstream consumers.

   Ask: "If I add `gpt-4.1-turbo` to the pricing file, who
   else needs to know?"
     - Playground model selector (UI)
     - Eval cost rollup job (uses prices to convert usage
       to USD)
     - Budget alert thresholds (manager-configured per
       team / per project)
     - Self-hosted customers' dashboards (need to pull
       the new prices via upgrade)
   Do not auto-update these. Just list them so the user
   can decide.

9. Commit the diff in one PR.

   Pricing file change + types file change (if any) +
   validation script run + a short CHANGELOG entry.
   Do not split the change across two PRs — the pricing
   and the type must land together or the build is
   broken.
```

# When NOT to use

- **The model has a per-request surcharge** (e.g.
  web-search, image generation) that is NOT per-token.
  Pricing files handle per-token cost only. Per-request
  costs go in a separate cost-addendum file.
- **You don't have an official source URL.** Do not
  invent prices. If the provider has not published
  pricing yet, defer the entry — an inaccurate price
  is worse than no price (the dashboard will show $0
  cost, which is loud; a wrong price silently charges
  the wrong number, which is quiet and dangerous).
- **The model is deprecated.** Do not add a new entry
  for a deprecated model. Update the existing entry's
  `tiers` to mark it as deprecated, set prices to zero,
  and let the dashboard filter it out.
- **The regex is `.*`.** That is a footgun. A regex
  without anchors matches everything. The validator
  will (or should) reject unanchored patterns.
- **You use a tokenizer that does not match the
  model.** `claude` tokenizer on a Gemini model will
  under-count, and `o200k_base` on an older `p50k_base`
  model will over-count. The pricing file is only as
  good as the tokenizer alignment.
- **The price is in a unit other than USD-per-million
  tokens.** Convert at the source. Pricing files
  assume one currency, one exponent.
- **The model is region-scoped** (e.g. AWS Bedrock
  inference profiles). Add a per-region tier, not a
  per-model override. Cross-region inference profiles
  have separate prices.
- **You want to update prices in production without
  alerting anyone.** Cost dashboards are read by
  finance. A price change is a finance-visible event.
  Write a CHANGELOG entry.

# Example

**Input:**

```yaml
pricing_file: worker/src/constants/default-model-prices.json
action: add
model_spec:
  id: gpt-4.1-turbo
  provider_prefixes: [gpt-4.1-turbo, openai/gpt-4.1-turbo, gpt-4.1-turbo-2025-04-15]
  provider: openai
  tokenizer: o200k_base
  tiers:
    - name: default
      input_cost_per_1m_tokens: 2.50
      output_cost_per_1m_tokens: 10.00
      cache_read_cost_per_1m_tokens: 1.25
  source_url: https://openai.com/api/pricing/
types_file: packages/shared/src/server/llm/types.ts
```

**Output:**

```
Diff applied to worker/src/constants/default-model-prices.json:
  + gpt-4.1-turbo
    matchPattern: (?i)^(openai/)?(gpt-4\.1-turbo)(-[0-9]{4}-[0-9]{2}-[0-9]{2})?$
    tokenizer: o200k_base
    tiers: [{ input: 2.50, output: 10.00, cache_read: 1.25 }]
    updatedAt: 2026-06-10

Diff applied to packages/shared/src/server/llm/types.ts:
  + "gpt-4.1-turbo" appended to ModelId union

Regex self-check:
  accept (3/3 pass):
    gpt-4.1-turbo                          → match
    openai/gpt-4.1-turbo                   → match
    gpt-4.1-turbo-2025-04-15               → match
  reject (3/3 pass):
    gpt-4.1                                → no match
    gpt-4.1-turbo-mini                     → no match
    gpt-4o                                 → no match

Schema validation: pass
  - JSON parses
  - all prices >= 0
  - all matchPatterns anchored
  - updatedAt is a valid ISO-8601 date

Downstream consumers that may need a refresh:
  - frontend playground model selector
  - eval cost rollup (nightly job)
  - budget alert thresholds (manual config)
  - customer-facing changelog (1-line entry: "+gpt-4.1-turbo")
```
