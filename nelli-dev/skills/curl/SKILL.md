---
name: curl
description: Build ready-to-run curl commands for a Znode API operation or scenario, using the gateway recorded at setup and values proven by read-only calls. Use when the developer runs /nelli-dev:curl.
argument-hint: "<operation, route or scenario>"
context: fork
agent: nelli-dev:api-curl-builder
---

Mode: **Curl**. Operation, route or scenario:

$ARGUMENTS

Follow `api-curl-workflow`: use the recorded gateway, discover the values without a database, prove GETs live, hand over writes unrun.
