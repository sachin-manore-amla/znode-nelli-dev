---
name: recommend-api
description: Recommend which Znode APIs to use for a customization requirement - ordered routes, why, parameters, headers and authentication, and which to use for which purpose. Use when the developer runs /nelli-dev:recommend-api or asks which API to call.
argument-hint: "<what you want to achieve>"
context: fork
agent: nelli-dev:api-curl-builder
---

Mode: **Recommend**. Goal:

$ARGUMENTS

Recommend the ordered set of APIs for this goal (follow `api-recommend`): prefer supported SDK and extension points, flag legacy v1, give full parameters, headers and authentication, and say which API to use for which purpose. Offer working curls for the chosen routes.
