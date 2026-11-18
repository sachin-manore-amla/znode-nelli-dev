---
name: docs
description: Write the technical document and deployment guide for a finished customization from its request folder. Use when the developer runs /nelli-dev:docs with a request id.
argument-hint: "<request id>"
context: fork
agent: nelli-dev:doc-writer
---

Write the technical document and deployment guide for request: $ARGUMENTS

The request folder is `nd-work/<request id>` in the workspace; follow your instructions and the templates.
