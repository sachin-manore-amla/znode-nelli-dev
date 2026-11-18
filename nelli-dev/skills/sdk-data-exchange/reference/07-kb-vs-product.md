# Data Exchange: where the sources disagree
Answers: conflicts between KB articles, release notes, the SDK and the product, and which to follow.

| Topic | Source A | Source B | Follow |
|---|---|---|---|
| Custom processor in a multi-step exchange | Architecture article lists it as unsupported | Developer guide, SDK manifest and release 10.13.1.0 add it | Supported from 10.13.1.0. On older versions, check the environment |
| Processor deployment | Legacy article: build the solution, enter the name in Processor File Name | Developer guide: `znode deploy extension` | Both models exist (reference 05) |
| Secret variable syntax | Vault article: `{{Var.Name}}` | User guide: `{{Secret.KEY}}` for secrets | Test on the environment; syntax was aligned in 10.13.1.0 |
| Macro syntax | `{{$Step1.field}}` | `{{Step1.Field}}` in URLs | Both appear; try the documented form per location |
| Event payload | Release 10.10.1.0: codes only | Return Payload Response option returns entity | Use the option; confirm in Input Parameters |
| Copy of multi-step exchanges | Architecture article: unsupported | Copy action documented | Check |
| Page sizes and payload | 3,000 vs 5,000 maximum, 10 MB vs 1 MB | | Treat as guidance |
| Scheduling | Scheduled exchanges only if Trigger Execution is off | | Rule confirmed by two articles |
| Admin menu | "Dev Center > Commerce Connector" in most articles | "Commerce Connector > Manage Commerce Connector" in the Business Central article | Menu sits under Dev Center in the product |
| Import API from an exchange | KB Znode Import destination | | Same engine as the Imports screen |
| Time zone, retention, roles | not stated | | Ask Znode |
Rule: when the KB and an observed behaviour disagree, the product wins; when two KB articles disagree, the newer release note wins.
