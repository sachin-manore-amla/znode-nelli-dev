---
name: review
description: Review Znode customization code - Custom API SDK implementations, Webstore customizations and extensions - for SDK compatibility, Znode API usage, security, performance and Znode package compatibility. Znode-specific only; not a general code-quality review. Read-only. Use when the developer runs /nelli-dev:review with a path, branch or diff.
argument-hint: "<path, branch or diff>"
context: fork
agent: nelli-dev:code-reviewer
---

Mode: **Review** (read-only, Znode customizations only). Target (a path, a branch or a diff base; empty means the recorded projects as a whole):

$ARGUMENTS

Steps:
1. Plan the review with `nd_review.py plan`, then run `python ${CLAUDE_PLUGIN_ROOT}/scripts/nd_review_scope.py <files, folder or --git-diff <base>> --request "<the developer's words>" --json`. Its classification is a lead: confirm each file by reading it.
2. Review only ZNODE-RELEVANT items (SDK extension points and the Capability Registry, event consumers and method overrides, Znode API usage, Webstore customization patterns, tenancy and ownership, authentication on custom endpoints including a client-supplied identity header, caching and publish handling, secrets, Znode package edits, bypassing Znode, version compatibility), inside the developer's recorded folders.
3. If the request or the whole file set is generic (style, naming, formatting, language idioms, "review my C#/React code", architecture unrelated to Znode), reply with exactly: "Nelli-Dev reviews Znode customizations only (SDK extension points, Webstore customizations, Znode API usage, security and performance of those). For general code quality, style or language review, please use your own code review tools." Then still review any Znode-relevant parts, and list the files you skipped under "out of scope: generic". Never give generic style findings, not even as Suggestions.
4. Return the graded report (Blocker, Should fix, Suggestion, each with file and line and the Znode rule or knowledge source it rests on), the verdict, and a short "Not reviewed" section.
