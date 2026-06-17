---
name: Realtime Eval Scaffold
name_zh: Realtime Eval 脚手架
description: 'You want to **start a new realtime eval** for an audio or'
description_zh: '引导搭建一个 realtime (音频 / 多轮) eval 文件夹 —— 选对 harness (单轮 TTS、音频回放、多轮模拟)，脚手架 prompt / tools / data 文件，最后跑 smoke + full eval 才返回。输入是一个使用场景，输出是可跑的 eval。'
category: evaluation
tags:
  - ai
  - documentation
  - evaluation
  - frontend
  - javascript
source: null
license: MIT
author: 'OpenAI (downstream pack: badhope)'
version: '0.1.0'
needs_review: false
slug: realtime-eval-bootstrap
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

You want to **start a new realtime eval** for an audio or
multi-turn scenario. The eval folder doesn't exist yet, and
the choice of harness depends on whether the test cases are
synthetic text-to-speech, replayed real audio, or full
multi-turn agent simulations.

The skill is built around three harnesses, each with a
different shape of input data and a different model of
"what's being tested":

| Harness  | Input shape               | What it measures                           |
|----------|---------------------------|--------------------------------------------|
| `crawl`  | text rows → TTS audio     | model behaviour on synthetic speech         |
| `walk`   | saved audio / TTS + noise | model behaviour on replay-quality audio     |
| `run`    | simulation scripts        | multi-turn agent with tool mocks + judges   |

The wrong harness is the most common mistake. The skill's
first job is to ask which one.

**Don't use this skill for** batch offline evals of plain text
(use a text eval framework, not realtime). And don't use it
for production monitoring — that's a tracing / observability
concern, not a scaffolded eval folder.

# Inputs

| Field | Required | Notes |
|---|---|---|
| `eval_name` | yes | Kebab-case folder name. |
| `goal` | yes | One or two sentences describing the scenario. |
| `harness` | no | `crawl` / `walk` / `run`. Pick by the table above. Ask the user if unsure. |
| `system_prompt` | no | Path or inline text. |
| `tools` | no | Path or inline descriptions (OpenAI function-calling format). |
| `data` | no | Existing CSV / JSONL. If absent, the skill authors starter rows. |
| `graders` | no | List of grader ids to apply. |

Ask for the missing inputs in one short batch. Do not infer
defaults silently — wrong defaults lead to scaffolds that
look fine but test the wrong thing.

# Output

Plain-text confirmation. Typical return:

```
Folder: examples/evals/realtime_evals/support_refund_realtime_eval/
Harness: crawl
Files created:
  README.md
  system_prompt.txt
  tools.json
  data/cases.csv    (3 rows, authored from goal)
  evals/run_eval.py
Smoke run:  pass (1/1 case, 12s)
Full run:   pass (3/3 cases, 41s)
Graders applied: transcript_accuracy, tone_professionalism
```

# Prompt

```prompt
You are scaffolding a new realtime eval. Follow the order.
Ask for the missing inputs in one batch — do not infer
silently.

1. Ask the user for the required inputs.

   Minimum to scaffold:
     - eval_name   (kebab-case)
     - goal        (one or two sentences)
     - harness     (crawl / walk / run)
     - system_prompt  (path or inline)
     - tools          (path or inline, function-calling JSON)
     - data          (path or "I'll author starter rows")
     - graders        (list of grader ids)

   If the user only gives `user_text` or a short task
   description, still ask for the missing fields. If they
   answer only partially, infer low-risk defaults, call
   out the assumptions, and make the scaffold easy to
   revise later.

2. Pick the harness.

   `crawl` — single-turn text-to-TTS. The eval text rows
             become audio via TTS, the model hears them, and
             the response is graded. Default for synthetic
             audio unless replay fidelity is the actual
             target.

   `walk`  — replay saved audio, OR generate audio from
             text rows with replay-specific characteristics
             (noise, telephony artifacts, speaker identity,
             codec artefacts). Use when the test must hear
             realistic audio fidelity.

   `run`   — multi-turn simulation. Each row is a sim_
             script with tool mocks and judge criteria.
             Use when the scenario has back-and-forth and
             tool calls.

   If the user says "synthetic audio" without specifying a
   harness, default to `crawl` (text-to-TTS). Reserve
   `walk` for cases where the generated audio must carry
   noise, telephony artefacts, or speaker identity.

3. Normalize the inputs.

   - If the user gives inline prompt or tool content, write
     it into the scaffolded folder.
   - If the user gives CSV data, inspect it (with pandas
     or `head` + a JSON dump of the first row) before
     wiring it in. The data has to be harness-shaped.
   - If the data is not harness-shaped, scaffold the
     skeleton first, then author the starter data into
     those files.
   - If the user only gave `user_text`, infer
     `example_id` values and leave optional grading
     fields blank.

4. Be proactive with starter data.

   The skill writes starter data when the user didn't
   supply any. The goal is realism, not placeholder
   boilerplate.

     - `crawl` / `walk`: author 3 starter rows covering
       one happy path and a couple of nearby variants
       or edge cases. The user must be able to see the
       eval "doing something" on day one.
     - `run`: author 2 starter simulations, not 1. A
       single simulation hides the distribution.

   Do not rely on a deterministic script-generated
   sample. Hand-author the rows from the user's use
   case — what would a real user actually say?

5. Run the scaffold script.

     python <evals_root>/skills/bootstrap-realtime-eval/
       scripts/bootstrap_realtime_eval.py \
       --name "<eval_name>" \
       --harness "<crawl|walk|run>" \
       [--prompt <path>] [--tools <path>] [--data <path>] \
       [--graders <id,id,id>]

   The script creates the folder, copies the harness
   template, and links the shared harness code (do NOT
   duplicate the harness scripts into the new folder).

6. Review the generated folder.

   - README is accurate for the chosen harness.
   - System prompt, tools, data files all point at the
     generated folder.
   - If the user supplied real data, it is wired in
     (not left as placeholders).
   - If you authored starter data, show the rows to
     the user before scaling up.

7. Enrich the scaffold.

   - For `crawl` and `walk`: make the CSV realistic. Make
     sure the expected tool columns are present. For
     `walk`, if the dataset lacks an `audio_path` column,
     wire up the shared `walk_harness/generate_audio.py`
     step from the README.
   - For `run`: make sure `simulations.csv` and the
     starter `sim_*.json` file reflect the user's
     scenario, tool mocks, and graders.

8. Validate before returning.

   a. Run a smoke eval (1 case).
   b. If smoke passes, AUTOMATICALLY run the full eval
      on all data rows in the same turn. Do not skip
      this — smoke-only validation misses dataset-wide
      and late-row failures.
   c. If smoke fails, stop and report the blocker. Do
      not run the full eval.
   d. Run the test suite:
        pytest <evals_root>/tests -q
   e. Inspect the README and at least one data file.
```

# When NOT to use

- **The use case is plain text, not audio or multi-turn.**
  This skill is for realtime (audio / multi-turn) evals.
  For text-only batch evals use a text eval framework.
- **You pick `walk` for synthetic audio without replay
  fidelity needs.** `crawl` is the right default. `walk`
  is for noise / telephony / speaker identity cases.
- **You scaffold a single starter simulation for `run`.**
  Two minimum. One hides the distribution of behaviours
  you're trying to measure.
- **You skip the smoke eval before the full eval.** The
  smoke catches wiring problems (wrong tool schema, bad
  audio path, missing grader config) that the full eval
  would also catch — but with 10× the runtime cost.
- **You declare the bootstrap complete after the smoke
  pass.** A successful smoke is not proof the full eval
  will pass. Always run the full eval too. Late-row
  failures are the most common cause of "eval worked
  yesterday, broken today" debugging.
- **You duplicate the main harness scripts into the
  generated folder.** The harness is shared. Link, do
  not copy.
- **You write generic placeholder data when the user
  gave you enough context to do better.** "Test
  customer support refund flow" is not a row. A
  plausible user utterance, with the right tool
  mocks, is.
- **The eval folder is outside `<evals_root>/`.** Keep
  the convention. Random paths break the harness
  auto-discovery.

# Example

**Input:**

```yaml
eval_name: support_refund
goal: |
  Customer calls the support line and asks for a refund on
  a recent order. The agent must verify the order, check
  refund eligibility, and either process the refund or
  explain why not.
harness: crawl
system_prompt: examples/evals/realtime_evals/shared/prompts/support_agent.txt
tools: examples/evals/realtime_evals/shared/tools/refund_tools.json
graders:
  - transcript_accuracy
  - tool_call_correctness
  - tone_professionalism
```

**Output:**

```
Folder: examples/evals/realtime_evals/support_refund_realtime_eval/
Harness: crawl

Files created:
  README.md
  system_prompt.txt     (symlink to shared support_agent.txt)
  tools.json            (symlink to shared refund_tools.json)
  data/cases.csv        (3 rows, hand-authored from goal)
  evals/run_eval.py     (links to shared crawl_harness)

Starter cases (3):
  1. happy path:    "I want a refund for order #12345"
  2. edge case:     "I want a refund but I bought it 6 months ago"
  3. abuse attempt: "Just give me a refund, I don't care about policy"

Smoke run:  pass (1/1 case, 14s)
Full run:   pass (3/3 cases, 47s)

Graders applied:
  - transcript_accuracy   (3/3 pass)
  - tool_call_correctness (3/3 pass)
  - tone_professionalism  (2/3 pass — case 3 marked "abrupt")

Blockers: none
```
