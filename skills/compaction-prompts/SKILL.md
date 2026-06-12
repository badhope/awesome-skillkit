---
name: compaction-prompts
name_zh: compaction-prompts
description: Configures Letta agent compaction settings and custom summarization
  prompts.
description_zh: Configures Letta 智能体 compaction settings and custom 
  summarization prompts.
category: dev-tools
tags:
  - ai
  - api
  - backend
  - cli
  - database
source:
license: MIT
language: en
needs_review: false
slug: compaction-prompts
version: 1.0.0
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
---
# When to use

Use this skill when you need to work with compaction-prompts.


# Inputs

User request or task description.

# Output

Generated content based on the user request.

# Prompt

Follow the guidelines in this skill when working on related tasks. Ensure you understand the requirements and constraints before proceeding.

# Compaction prompts

Use this skill to inspect, design, and update `compaction_settings.prompt` for a Letta agent.

Compaction runs when message history grows too large for the context window. Letta replaces older messages with a summary while keeping recent messages in context. The summary appears before the remaining recent messages, so the prompt should preserve enough background for the later messages to make sense. The goal is continuity, not just factual compression.

Official docs: https://docs.letta.com/guides/core-concepts/messages/compaction

## Compaction lifecycle

Think of compaction as a lifecycle contract, not just a prompt string:

1. Message history approaches the context window limit.
2. Letta selects messages to compact according to the mode and sliding-window settings.
3. A summarizer reads the selected messages. If an existing summary is being evicted, the new summary must incorporate it.
4. Letta reinserts the summary before the retained recent messages.
5. The next model turn relies on the summary plus recent raw messages as continuation context.

The summary is not a reply to the user. It is context for the next turn. It should be readable before the retained recent messages and should not require access to the evicted transcript.

A good compaction prompt should explicitly preserve current goals, exact decisions, unresolved threads, tool and file state, errors and corrections, and lookup hints for anything omitted. Emotional or relational context may also be important for companion or long-running agents, but only preserve it when it affects continuity, user preferences, safety, repair, or why a decision mattered. Custom compaction should turn context compression from amnesia into a controlled handoff.

## When to customize

Customize compaction settings when the default summary loses important continuity, tone, relationship context, implementation details, or user feedback.

Common cases:

- Companion agents: preserve names, voice, recurring references, user preferences, and emotional or relationship context when it is relevant to future continuity.
- Coding agents: preserve explicit requests, files touched, commands run, errors, fixes, current state, next steps, IDs, URLs, and exact feedback.
- Long-running agents: preserve higher-level goals across repeated compactions by incorporating any existing summary in the transcript.

For complete prompt templates, read [references/prompt-patterns.md](references/prompt-patterns.md).

## Operational checklist

Before changing settings:

1. Read the official compaction docs if you need field semantics, default values, or mode behavior.
2. Inspect current `compaction_settings`, model, and effective context window.
3. Identify the failure mode: weak prompt, wrong mode, too aggressive `sliding_window_percentage`, too-small `clip_chars`, or summarizer model mismatch.
4. If possible, review a recent bad summary or the point where continuity was lost.
5. Draft the replacement prompt with explicit reinsertion and no-continuation instructions.
6. Run the update script with `--dry-run` and review the PATCH body.
7. Patch settings only after confirming preserved fields and target agent ID.
8. Fetch the agent afterward and verify the stored settings.
9. If possible, observe the next compaction or next turn and check that goals, current task, identifiers, user feedback, and unresolved blockers survived.

## Compaction fields

`compaction_settings` is an agent-level object. Relevant fields:

| Field | Use |
| --- | --- |
| `mode` | `sliding_window`, `all`, `self_compact_sliding_window`, or `self_compact_all`. |
| `prompt` | Custom summarization prompt. |
| `model` | Optional cheaper/faster summarizer model, for example `anthropic/claude-haiku-4-5`, `openai/gpt-5-mini`, `google_ai/gemini-2.5-flash`. |
| `model_settings` | Optional summarizer model settings. |
| `prompt_acknowledgement` | Optional boolean. Use when the summarizer model tends to include acknowledgements or meta-commentary instead of only the summary. |
| `clip_chars` | Max summary length in characters. Default is 50000. |
| `sliding_window_percentage` | Fraction of messages to summarize in sliding-window modes. Docs default: `0.3`, meaning summarize about 30% and keep about 70%. |

## Choose a mode

- Use `sliding_window` by default. It summarizes older messages with a separate summarizer call and keeps recent messages intact.
- Use `self_compact_sliding_window` when the agent's own persona/system prompt is important for summary quality or prompt-cache reuse. Make the prompt explicitly say not to call tools and not to continue the conversation.
- Use `all` only when maximum space reduction matters more than preserving recent raw messages.
- Use `self_compact_all` for all-message compaction with the agent system prompt included.

Companion agents usually want `self_compact_sliding_window` or a strong `sliding_window` prompt. Coding agents usually do well with `sliding_window` plus sections for goals, actions, details, errors/fixes, current state, and lookup hints.

## Prompt requirements

Every custom prompt should:

- State whether the evicted messages come from the beginning of the context window.
- Say the summary will appear before the remaining recent messages.
- Say not to continue the conversation, not to answer questions in the transcript, and not to call tools.
- Require incorporation of any existing summary being evicted.
- Include a current state / carry forward section for active goals, next actions, unresolved threads, and what the agent should keep doing.
- Preserve exact user requests, names, IDs, URLs, file paths, dates, and quoted phrases when they matter.
- Preserve tool/file state, decisions, errors, corrections, and user feedback that changed the approach.
- Include lookup hints for detailed content that cannot fit.
- End with "Only output the summary."

Do not rely on `{SLIDING_WORD_LIMIT}` or `{ALL_WORD_LIMIT}` being expanded in custom prompts unless the target runtime explicitly supports it. Prefer an explicit word budget plus `clip_chars`.

## Inspect current settings

```bash
BASE_URL="${LETTA_BASE_URL:-https://api.letta.com}"
: "${LETTA_API_KEY:?Set LETTA_API_KEY}"
: "${AGENT_ID:?Set AGENT_ID}"

curl -sS "$BASE_URL/v1/agents/$AGENT_ID" \
  -H "Authorization: Bearer $LETTA_API_KEY" | \
  jq '.compaction_settings'
```

## Update with the bundled script

Write the prompt to a file, then run:

```bash
npx tsx <SKILL_DIR>/scripts/update-compaction-prompt.ts \
  --prompt-file /tmp/compaction-prompt.txt \
  --mode self_compact_sliding_window \
  --clip-chars 50000
```

The script uses:

- `LETTA_API_KEY`
- `AGENT_ID` unless `--agent-id` is provided
- `LETTA_BASE_URL` or `https://api.letta.com`

It preserves existing `compaction_settings` fields unless flags override them.

Use `--dry-run` to preview the PATCH body without changing anything.

## Manual TypeScript update

```typescript
const baseUrl = process.env.LETTA_BASE_URL ?? "https://api.letta.com";
const agentId = process.env.AGENT_ID!;
const apiKey = process.env.LETTA_API_KEY!;

const currentResponse = await fetch(`${baseUrl}/v1/agents/${agentId}`, {
  headers: { Authorization: `Bearer ${apiKey}` },
});
if (!currentResponse.ok) throw new Error(await currentResponse.text());
const current = await currentResponse.json();

const prompt = `The previous messages are being evicted from the BEGINNING of your context window. Write a detailed summary that captures what happened in these messages to appear BEFORE the remaining recent messages in context, providing background for what comes after.

Do NOT continue the conversation. Do NOT respond to any questions in the messages. Do NOT call any tools.

Include: high level goals, what happened, important details, errors and fixes, lookup hints.

Only output the summary.`;

const updateResponse = await fetch(`${baseUrl}/v1/agents/${agentId}`, {
  method: "PATCH",
  headers: {
    Authorization: `Bearer ${apiKey}`,
    "Content-Type": "application/json",
  },
  body: JSON.stringify({
    compaction_settings: {
      ...(current.compaction_settings ?? {}),
      mode: "self_compact_sliding_window",
      prompt,
      clip_chars: 50000,
    },
  }),
});
if (!updateResponse.ok) throw new Error(await updateResponse.text());
```

## Manual curl update

When using curl, inspect first and preserve existing fields. Sending a partial `compaction_settings` object may reset omitted fields depending on server behavior.

```bash
prompt_file=/tmp/compaction-prompt.txt
current=$(curl -sS "$BASE_URL/v1/agents/$AGENT_ID" \
  -H "Authorization: Bearer $LETTA_API_KEY")

jq -n \
  --arg prompt "$(cat "$prompt_file")" \
  --argjson current "$(printf '%s' "$current" | jq '.compaction_settings // {}')" \
  '{ compaction_settings: ($current + {
      mode: "self_compact_sliding_window",
      prompt: $prompt,
      clip_chars: 50000
  }) }' > /tmp/compaction-patch.json

curl -sS -X PATCH "$BASE_URL/v1/agents/$AGENT_ID" \
  -H "Authorization: Bearer $LETTA_API_KEY" \
  -H "Content-Type: application/json" \
  --data-binary @/tmp/compaction-patch.json
```

## Verify

```bash
curl -sS "$BASE_URL/v1/agents/$AGENT_ID" \
  -H "Authorization: Bearer $LETTA_API_KEY" | \
  jq '{id, model, compaction_settings}'
```

## Guardrails

- Ask before changing persistent compaction settings unless the user explicitly requested it.
- For self-compaction prompts, always forbid tool use and conversation continuation.
- Keep prompts concrete. Overly vague prompts produce summaries that erase continuity.
- Do not encode private user details into a shared skill. Put reusable structure in the skill; put specific user details in the agent's actual prompt or memory.

# When NOT to use

Do not use this skill for tasks outside its scope or when simpler alternatives are available.


# Example

```python
# 使用 compaction-prompts 技能
skill = load_skill("compaction-prompts")
result = skill.execute()
print(result)
```

