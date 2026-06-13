---
name: capture-api-response-test-fixture
name_zh: capture-接口-response-测试-fixture
description: Capture API response test fixture.
description_zh: Capture 接口 response 测试 fixture.
category: applications
tags:
  - ai
  - api
  - backend
  - frontend
  - javascript
source:
needs_review: false
slug: capture-api-response-test-fixture
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
license: MIT
---
### API Response Test Fixtures

For provider response parsing tests, we aim at storing test fixtures with the true responses from the providers (unless they are too large in which case some cutting that does not change semantics is advised).

The fixtures are stored in a `__fixtures__` subfolder, e.g. `packages/openai/src/responses/__fixtures__`. See the file names in `packages/openai/src/responses/__fixtures__` for naming conventions and `packages/openai/src/responses/openai-responses-language-model.test.ts` for how to set up test helpers.

You can use our examples under `/examples/ai-functions` to generate test fixtures.

#### generateText (doGenerate testing)

For `generateText`, log the raw response output to the console and copy it into a new test fixture.

```ts
import { openai } from '@ai-sdk/openai';
import { generateText } from 'ai';
import { run } from '../lib/run';

run(async () => {
  const result = await generateText({
    model: openai('gpt-5-nano'),
    prompt: 'Invent a new holiday and describe its traditions.',
  });

  console.log(JSON.stringify(result.response.body, null, 2));
});
```

#### streamText (doStream testing)

For `streamText`, you need to set `includeRawChunks` to `true` and use the special `saveRawChunks` helper. Run the script from the `/example/ai-functions` folder via `pnpm tsx src/stream-text/script-name.ts`. The result is then stored in the `/examples/ai-functions/output` folder. You can copy it to your fixtures folder and rename it.

```ts
import { openai } from '@ai-sdk/openai';
import { streamText } from 'ai';
import { run } from '../lib/run';
import { saveRawChunks } from '../lib/save-raw-chunks';

run(async () => {
  const result = streamText({
    model: openai('gpt-5-nano'),
    prompt: 'Invent a new holiday and describe its traditions.',
    includeRawChunks: true,
  });

  await saveRawChunks({ result, filename: 'openai-gpt-5-nano' });
});
```

# When to use

Use this skill when you need guidance on capture-api-response-test-fixture.

# Inputs

User request or task description.

# Output

Generated content based on the user request.

# Prompt

Follow the guidelines in this skill when working on related tasks.

# When NOT to use

Do not use this skill for tasks outside its scope.

# Example

See the skill content above for practical examples.
