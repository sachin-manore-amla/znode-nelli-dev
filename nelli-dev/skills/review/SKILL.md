---
name: review
description: Review customization code - Custom API SDK implementations, Webstore customizations and extensions - for quality, SDK compatibility, security, performance, API usage and dependencies. Read-only. Use when the developer runs /nelli-dev:review with a path, branch or diff.
argument-hint: "<path, branch or diff>"
context: fork
agent: nelli-dev:code-reviewer
---

Mode: **Review** (read-only). Target (a path, a branch or a diff base; empty means the recorded projects as a whole):

$ARGUMENTS

Plan the review with `nd_review.py plan`, review only the developer's recorded customization folders, confirm every lead, and return the graded report (Blocker, Should fix, Suggestion) with a verdict.
