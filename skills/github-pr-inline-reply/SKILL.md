---
name: github-pr-inline-reply
name_zh: github-pr-inline-reply
description: 'Reply to inline PR review comments on GitHub pull requests using the GitHub API. Use this skill when you need to respond to individual review comments on a PR, acknowledge feedback, or mark comment...'
description_zh: 'Reply to inline PR 审查 comments on GitHub pull requests using the GitHub 接口. Use this 技能 when you need to respond to individual 审查 comments on a PR, acknowledge feedback, or mark comments as resolve...'
category: dev-tools
tags:
  - api
  - backend
  - cli
  - database
  - frontend
source: null
needs_review: false
slug: github-pr-inline-reply
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

Use this skill when replying to inline PR review comments on GitHub pull requests.

- Replying to individual PR review comments
- Acknowledging reviewer feedback on specific lines of code
- Marking review comments as addressed with a reply

## API Endpoint

To reply to an inline PR comment, use:

```http
POST /repos/{owner}/{repo}/pulls/{pull_number}/comments/{comment_id}/replies
```

With body:

```json
{
  "body": "Your reply message"
}
```

## Using gh CLI

```bash
gh api repos/{owner}/{repo}/pulls/{pull_number}/comments/{comment_id}/replies \
  -X POST \
  -f body="Your reply message"
```

## Workflow

1. **Get PR comments**: First fetch the PR review comments to get their IDs:

   ```bash
   gh api repos/{owner}/{repo}/pulls/{pull_number}/comments
   ```

2. **Identify comment IDs**: Each comment has an `id` field. For threaded comments, use the root comment's `id`.

3. **Post replies**: For each comment you want to reply to:

   ```bash
   gh api repos/{owner}/{repo}/pulls/{pull_number}/comments/{comment_id}/replies \
     -X POST \
     -f body="Fixed in commit abc123"
   ```

## Example Replies

For accepted changes:

- "Fixed in {commit_sha}"
- "Accepted - fixed in {commit_sha}"

For rejected changes:

- "Rejected - {reason}"
- "Won't fix - {explanation}"

For questions:

- "Good catch, addressed in {commit_sha}"

## Notes

- The `comment_id` is the numeric ID from the comment object, NOT the `node_id`
- Replies appear as threaded responses under the original comment
- You can reply to any comment, including bot comments (like Copilot reviews)

## Resolving Conversations

To resolve (mark as resolved) PR review threads, use the GraphQL API:

1. **Get thread IDs**: Query for unresolved threads:

   ```bash
   gh api graphql -f query='
   query {
     repository(owner: "{owner}", name: "{repo}") {
       pullRequest(number: {pull_number}) {
         reviewThreads(first: 50) {
           nodes {
             id
             isResolved
             comments(first: 1) {
               nodes { body path }
             }
           }
         }
       }
     }
   }'
   ```

2. **Resolve threads**: Use the `resolveReviewThread` mutation:

   ```bash
   gh api graphql -f query='
   mutation {
     resolveReviewThread(input: {threadId: "PRRT_xxx"}) {
       thread { isResolved }
     }
   }'
   ```

3. **Resolve multiple threads at once**:

   ```bash
   gh api graphql -f query='
   mutation {
     t1: resolveReviewThread(input: {threadId: "PRRT_xxx"}) { thread { isResolved } }
     t2: resolveReviewThread(input: {threadId: "PRRT_yyy"}) { thread { isResolved } }
   }'
   ```

The thread ID starts with `PRRT_` and can be found in the GraphQL query response.

Note: This skill can be removed once the GitHub MCP server has added built-in support for replying to PR review comments and resolving threads.
See:
https://github.com/github/github-mcp-server/issues/1323
https://github.com/github/github-mcp-server/issues/1768

# Inputs

User request or task description.

# Output

Generated content based on the user request.

# Prompt

Follow the guidelines in this skill when working on related tasks.

# GitHub PR Inline Reply Skill

This skill enables replying directly to inline review comments on GitHub pull requests.

# When NOT to use

Do not use this skill for tasks outside its scope.

# Example

See the "Example Replies" and "Workflow" sections above for practical examples of replying to PR comments and resolving conversations.
