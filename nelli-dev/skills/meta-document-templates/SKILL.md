---
name: meta-document-templates
description: The fixed document set Nelli-Dev produces for every customization request - requirements, discovery, solution proposal, implementation plan, test plan, results, security and performance reports, platform change request and the handover pack - with the template for each. Use whenever writing or reviewing a request's documents.
user-invocable: false
---

# Document templates

Templates are in [reference/templates.md](reference/templates.md). Every request writes its documents to `<workspace>\nd-work\<REQUEST-ID>\`.

| File | Written in phase | Template |
|---|---|---|
| `progress.md` | every phase (by `nd_progress.py`) | generated |
| `requirements.md` | 1 Requirements | T1 |
| `discovery.md` | 2 Discovery | T2 |
| `solution-proposal.md` | 3 Architecture | T3 |
| `platform-change-request.md` | 3, when the verdict is Needs platform change | T4 |
| `implementation-plan.md` and `test-plan.md` | 4 Plan | T5, T6 |
| `approval.json` | the Approval gate (by `nd_approve.py`) | generated |
| `change-log.md` | 5 Implement | T7 |
| `test-results.md` | 6 Test | `quality-testing` |
| `performance-report.md` | 7 Performance | T8 |
| `security-report.md` | 8 Security | T9 |
| `handover\technical-document.md` (+ `.html`) and `handover\deployment.md` | 9 Handover | T10 |

## Rules for every document

1. **Evidence on every claim.** An API, extension point or behaviour is followed by its source: a registry entry id, an API operation (`METHOD /route`, spec key), a KB article link, or a `file:line`. No source means "NOT VERIFIED" in the text.
2. **Confidence.** Mark any statement below 85% confidence `⚠ needs confirmation (NN%)` and list it under Open questions. Scores: verified in code or spec with a reference 90-100; seen live on the environment 85-90; KB article 70-85; skill only 50-70; inference below 50.
3. **Checked line.** Every document ends with:
   `Checked: references re-checked — yes | partly (<which not>) · verified live — yes (<environment>, <date>) | no · gaps — <list, or none>`
4. **Version stamp.** Documents that describe code end with the output of `nd_version_stamp.py --repo <sdk> --repo <webstore> --env "<environment>"`.
5. **No secrets and no internal references** in any document (run `nd_scan_customer_safety.py` over the folder before handover).
6. Write the document as soon as its phase finishes and mark it in the progress file; do not hold everything back to the end.
