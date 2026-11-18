# Data Exchange: scheduling, history, notifications, limits, release history
Answers: how to schedule an exchange, what the numbers are, what the module does not do, and which version added what.
Confidence: KB architecture article and release notes (75). The numbers are the article's general best practice, not enforced limits, unless stated.

## Scheduled Data Exchanges
Path: Dev Center > Commerce Connector > Scheduled Data Exchanges, add new (top right). Steps: search and select an enabled exchange; Frequency **One-Time** or **Recurring**; Run Date `MM/DD/YYYY`; Run Time `hh:mm` (for example `12:00 AM`); recurring uses a **Cron Expression** (a "Commonly Used Cron Expressions" list is on screen). Scheduler types in the guidance: Scheduled, OnDemand, RealTime.
Rules: only active, enabled exchanges; Trigger Execution (HTTP) must be off. Disabling an exchange keeps its schedule (visible, inactive) and editing a disabled exchange no longer creates a job (10.12.0.0). The cron setting changes appear in the scheduler dashboard at once (10.14.0.0). Time zone of the run time is not stated (GAPS). The job runs on the platform's shared background queue.

## Recommended frequencies (10.10.1.0)
| Exchange | Frequency |
|---|---|
| Inventory sync | every 15 minutes |
| Order export | every 15 to 30 minutes |
| Price sync | every 4 hours |
| Product import | daily |
| Full catalog sync | weekly |
Never below 5 minutes (a 30-second cron can saturate the queue). Run large exchanges off-peak.

## Page sizes (API source with Reiterate)
| Data | Recommended | Maximum |
|---|---|---|
| Inventory | 500 | 5,000 |
| Orders | 200 | 3,000 |
| Products | 250 | 3,000 |
| Prices | 1,000 | 5,000 |
| Customers | 250 | 3,000 |
Above 1,000 can cause memory pressure; very small pages add HTTP overhead. Always paginate API sources.

## Import and export volumes
Batch sizes per import: Product 1,000 to 10,000; Price and Inventory 2,500 to 10,000; Category 500 to 1,000 (the article also says 2,000 per batch); Promotions 500. Files under 50 MB; prefer Blob or SFTP for high volume. Export: 5,000 records per file, 50 MB, 3 concurrent export jobs per server. Payload 10 MB.
The article contradicts itself in three places (product page maximum 3,000 vs a general 5,000 cap; payload 10 MB vs 1 MB target; product batch ranges). Treat the figures as guidance and load-test.

## Known limitations (architecture article)
No hard record limit per exchange (memory pressure on large runs); real-time is synchronous; event queues may be temporary (events lost on restart); no dead-letter queue; shared background queue (long jobs block short ones); some pagination retry counts hard-coded; SQL parser timeouts on huge parses; no real-time rate limiting; SFTP reconnects per file; no advanced retry monitoring UI; no step-level data logging; no advanced monitoring dashboards beyond the Dashboard.

## Notifications
Path: Dev Center > Commerce Connector > Notification Configuration. Select a **Store** (its SMTP settings send the mail, only configured stores appear), **Add New**, choose an exchange not yet configured, enter one or more recipient emails, confirm with the check mark. Mail goes on execution notices and on failure. Templates: CMS > Email & SMS Templates (macros such as exchange name and start time).

## Infrastructure sizing (guidance)
Small 1 vCPU 2 GB; mid-market 2 vCPU 4 GB, 2 instances; enterprise 3+ vCPU 8 to 16 GB, 3+ instances. Hosted tenants: not a customer decision.

## Release history
| Version (date) | Change |
|---|---|
| 10.3.0.0 (Aug 2025) | Data Exchanges beta, add from library or scratch |
| 10.5.0.0 (Nov 2025) | Data Exchange module in Dev Center; one-time, cron, on-demand; Znode Import destination; notifications; copy; YAML mapping; publish webhooks for Product, Category, Catalog, Content Page, Store |
| 10.6.0.0 (Dec 2025) | Download processor file code for native and custom exchanges |
| 10.6.1.0 (Jan 2026) | Per-exchange timeout |
| 10.10.1.0 (May 2026) | Multi-step, event and callback triggers, guidance numbers |
| 10.12.0.0 (Jun 2026) | Commerce Connector 2.0: separate request per record; transmission type at exchange level; schedule kept when disabled |
| 10.12.1.0 (Jul 2026) | Remove step; record counts fixed; custom execution logs no longer duplicated |
| 10.13.0.0 (Jul 2026) | Token expiration error in exchanges fixed |
| 10.13.1.0 (Aug 2026) | Dashboard, Credential Vault, custom processor in multi-step, five native Finance and Supply Chain exchanges (Create Sales Order, Create Account, Create Customer, Get Order History, Get Order Details; simple and configurable products only, no tax, shipping, discounts or coupons) |
| 10.14.0.0 (Sep 2026) | Execution history fix, stored credentials no longer auto-fill in SFTP and API modes |
| 10.14.0.6 (Oct 2026) | Request-timeout fix for a product exchange job; Commerce Connector page access fix |
Native Business Central exchanges (Import Product, User, Price, Inventory, Category) need Environment URL, Tenant ID, Client ID, Client Secret, Company ID, Environment Name.
