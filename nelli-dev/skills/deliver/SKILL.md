---
name: deliver
description: Deliver a customization end to end - verdict (Supported, Customizable, Restricted, Needs platform change), solution proposal and plan, your approval, then build, test, performance and security checks, and handover. Use when the developer runs /nelli-dev:deliver with a requirement or FSD.
argument-hint: "<requirement text or FSD path>"
context: fork
agent: nelli-dev:nelli-dev
---

Mode: **Deliver**. The developer's requirement or FSD (text or a path):

$ARGUMENTS

Follow your Deliver workflow from the start-of-run steps. Stop for the developer's approval of the plan before any code change.
