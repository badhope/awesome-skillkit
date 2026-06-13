---
name: trpc-router
name_zh: trpc-router
description: TRPC router development guide. Use when creating or modifying 
  apps/server/src/routers,
description_zh: TRPC router 开发 guide. Use when creating or modifying 
  apps/服务器/src/routers,
category: dev-tools
tags:
  - ai
  - api
  - backend
  - cli
  - database
source:
needs_review: false
slug: trpc-router
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
# When to use

Use this skill when you need to work with trpc-router.


# Inputs

User request or task description.

# Output

Generated content based on the user request.

# Prompt

Follow the guidelines in this skill when working on related tasks. Ensure you understand the requirements and constraints before proceeding.

# TRPC Router Guide

## File Location

- Routers: `apps/server/src/routers/lambda/<domain>.ts`
- Helpers: `apps/server/src/routers/lambda/_helpers/`
- Schemas: `apps/server/src/routers/lambda/_schema/`

## Router Structure

### Imports

```typescript
import { TRPCError } from '@trpc/server';
import { z } from 'zod';

import { SomeModel } from '@/database/models/some';
import { authedProcedure, router } from '@/libs/trpc/lambda';
import { serverDatabase } from '@/libs/trpc/lambda/middleware';
```

### Middleware: Inject Models into ctx

**Always use middleware to inject models into `ctx`** instead of creating `new Model(ctx.serverDB, ctx.userId)` inside every procedure.

```typescript
const domainProcedure = authedProcedure.use(serverDatabase).use(async (opts) => {
  const { ctx } = opts;
  return opts.next({
    ctx: {
      fooModel: new FooModel(ctx.serverDB, ctx.userId),
      barModel: new BarModel(ctx.serverDB, ctx.userId),
    },
  });
});
```

Then use `ctx.fooModel` in procedures:

```typescript
// Good
const model = ctx.fooModel;

// Bad - don't create models inside procedures
const model = new FooModel(ctx.serverDB, ctx.userId);
```

**Exception**: When a model needs a different `userId` (e.g., watchdog iterating over multiple users' tasks), create it inline.

### Procedure Pattern

```typescript
export const fooRouter = router({
  // Query
  find: domainProcedure.input(z.object({ id: z.string() })).query(async ({ input, ctx }) => {
    try {
      const item = await ctx.fooModel.findById(input.id);
      if (!item) throw new TRPCError({ code: 'NOT_FOUND', message: 'Not found' });
      return { data: item, success: true };
    } catch (error) {
      if (error instanceof TRPCError) throw error;
      console.error('[foo:find]', error);
      throw new TRPCError({
        cause: error,
        code: 'INTERNAL_SERVER_ERROR',
        message: 'Failed to find item',
      });
    }
  }),

  // Mutation
  create: domainProcedure.input(createSchema).mutation(async ({ input, ctx }) => {
    try {
      const item = await ctx.fooModel.create(input);
      return { data: item, message: 'Created', success: true };
    } catch (error) {
      if (error instanceof TRPCError) throw error;
      console.error('[foo:create]', error);
      throw new TRPCError({
        cause: error,
        code: 'INTERNAL_SERVER_ERROR',
        message: 'Failed to create',
      });
    }
  }),
});
```

### Aggregated Detail Endpoint

For views that need multiple related data, create a single `detail` procedure that fetches everything in parallel:

```typescript
detail: domainProcedure.input(idInput).query(async ({ input, ctx }) => {
  const item = await resolveOrThrow(ctx.fooModel, input.id);

  const [children, related] = await Promise.all([
    ctx.fooModel.findChildren(item.id),
    ctx.barModel.findByFooId(item.id),
  ]);

  return {
    data: { ...item, children, related },
    success: true,
  };
}),
```

This avoids the CLI or frontend making N sequential requests.

## Conventions

- Return shape: `{ data, success: true }` for queries, `{ data?, message, success: true }` for mutations
- Error handling: re-throw `TRPCError`, wrap others with `console.error` + new `TRPCError`
- Input validation: use `zod` schemas, define at file top
- Router name: `export const fooRouter = router({ ... })`
- Procedure names: alphabetical order within the router object
- Log prefix: `[domain:procedure]` format, e.g. `[task:create]`

# When NOT to use

Do not use this skill for tasks outside its scope or when simpler alternatives are available.


# Example

```python
# 使用 trpc-router 技能
skill = load_skill("trpc-router")
result = skill.execute()
print(result)
```

