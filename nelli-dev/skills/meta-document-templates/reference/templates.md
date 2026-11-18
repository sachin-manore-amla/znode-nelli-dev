# Nelli-Dev document templates

Copy the block, fill every section, delete none (write "None" instead).

## T1 requirements.md

```
# Requirements — <REQUEST-ID>: <title>
Requested by · Date · Znode version · Environment · Source (chat / FSD path)
## Business objective
## Functional requirements
| # | Requirement | Source (FSD section / developer message) |
## Acceptance criteria
| AC | Criterion (testable) | Must-pass |
## Constraints (performance, security, compliance, deadlines, existing customizations)
## Assumptions (each with confidence)
## Open questions (each with the options offered)
```

## T2 discovery.md

```
# Discovery — <REQUEST-ID>
## Registry lookups (nd_registry.py find/show: query → entries)
## Knowledge Base articles (title · link · what it settles)
## API operations (spec key · METHOD /route · purpose · VERIFIED | NOT VERIFIED)
## Existing code reviewed (path:line · what it does · reuse?)
## Samples reused
## Gaps (what could not be found and where was searched)
```

## T3 solution-proposal.md

```
# Solution proposal — <REQUEST-ID>: <title>
## Verdict: Supported | Customizable | Restricted | Needs platform change   (applies to Znode <version>)
Evidence for the verdict: <registry id(s) + KB/API link or file:line>
## Options considered
| Option | How | Pros | Cons / risks | Verdict |
## Recommended approach
Why this option. Where the logic lives and why (consistency across listing, cart, checkout where relevant).
## Design
Components and files · data flow (numbered steps, incl. each API call) · API contracts (request/response fields) · configuration · security and tenancy design · caching
## Impact on existing functionality
## Out of scope
## Limitations and upgrade risk (Webstore source changes: state the merge risk)
## Effort estimate (for a developer new to Znode) and risks
## Open questions / items needing confirmation
```

## T4 platform-change-request.md

```
# Platform change request — <REQUEST-ID>
## Requirement that cannot be met
## What was checked (registry entries, KB articles, API operations) and why none reaches it
## Exact capability needed (API field, hook, extension point, behaviour)
## Business impact if not provided
## Workaround (if any) and its limits
## Suggested change for Znode
```

## T5 implementation-plan.md

```
# Implementation plan — <REQUEST-ID>
## Changes
| # | Repo/project | File | Change | Depends on |
## Contracts (endpoints, models, events)
## Branch plan (repo · current branch · clean? · new branch name)
## Configuration and deployment (settings, env vars, registration lines, Ocelot routes, deployment order, rollback)
## Security, performance and logging considerations
## Risks and rollback
```

## T6 test-plan.md

```
# Test plan — <REQUEST-ID>
| TC | AC | Level (unit/integration/functional/regression) | Scenario | Data / steps | Expected | Must-pass | Needs data change? | Status |
Sections: acceptance criteria · negative and boundary · authorization and ownership · multi-store/locale/currency · B2B · regression · performance · data and backward compatibility
```

## T7 change-log.md

```
# Change log — <REQUEST-ID>
| File | Change | Why (plan item #) | Build/test after change |
```

## T8 performance-report.md

```
# Performance report — <REQUEST-ID>
## Scan (command, leads, confirmed or dismissed with reason)
## Call budget per user action (before / after)
## Measurements (tool, settings, environment, date, p50/p95, error rate) or "not measured"
## Findings and fixes
## Verdict: no blocking findings from these checks | blockers: <list>
```

## T9 security-report.md

```
# Security report — <REQUEST-ID>
## Scans run (commands, tools, versions) and what was NOT scanned
## Findings
| ID | Severity | Location (file:line) | Finding | Status: fixed / false positive (why) / accepted by <name, date> |
## Znode-specific checks (authentication, authorization, ownership, tenancy, validation, data protection, secrets, CORS, webhooks, dependencies)
## Verdict: no Critical or High findings from these checks | open items: <list>
```

## T10 handover/technical-document.md

```
# Technical document — <REQUEST-ID>: <title>
## Purpose and requirement
## Solution summary and verdict
## Implementation details (per file/class/method: what and why)
## API contracts (new endpoints; request/response; auth; errors)
## Configuration and environment variables (names only, never values)
## Deployment steps and order · rollback
## Test evidence (summary + path to test-results.md)
## Security and performance summary (+ paths)
## Limitations, assumptions, upgrade risk
## Recommendations and follow-ups
## Version stamp
```
