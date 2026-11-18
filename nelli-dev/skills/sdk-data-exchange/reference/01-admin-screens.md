# Data Exchange: Admin screens and base definition
Answers: where each Commerce Connector screen is and what every base-definition field means.
Confidence: KB articles read through summaries (70-80); menu placement checked in product source (90).

## Menu paths
| Screen | Path |
|---|---|
| Data Exchanges list | Dev Center > Commerce Connector > Data Exchanges |
| Scheduled Data Exchanges | Dev Center > Commerce Connector > Scheduled Data Exchanges |
| Credential Vault | Commerce Connector > Credential Vault |
| Notification Configuration | Dev Center > Commerce Connector > Notification Configuration |
| Dashboard | Commerce Connector > Dashboard (from 10.13.1.0) |
| Legacy ERP Connector | Dev Center > Commerce Connector > Legacy ERP Connector (see reference 06) |
The Admin opens the Commerce Connector inside the Admin page; the Admin passes a connector token and session. Behaviour to know: the Data Exchange screens are not an Admin-native page, so they follow the Commerce Connector release, not only the Admin release.

## Create an exchange
Buttons: **Add New** (blank, you configure everything) and **Add from Library** (native exchanges: two-step and multi-step; Dynamics 365 Business Central and Finance and Supply Chain exchanges are here).

## Base definition fields
| Field | Required | Meaning |
|---|---|---|
| Exchange Name | Yes | Unique, cannot change after creation |
| Exchange Code | Yes | Unique, cannot change after creation. Custom processors address the exchange by this code |
| Source | Yes | System sending the data (free label) |
| Destination | No | System receiving the data. If omitted, the caller receives the result as API output |
| Version | Yes | Version number of the exchange |
| Custom Processing Required | Checkbox | When on, **Processor File Name** is required |
| Processor File Name | When above is on | Name of the deployed processor (reference 05) |
| Trigger Origin | Yes | System that starts the exchange |
| Tags | No | Labels |
| Timeout | No | Maximum run seconds before automatic termination (configurable timeout added in 10.6.1.0) |
| Description | No | Text |
| Enable | No | Enabled or disabled. An exchange enabled with incomplete configuration fails and logs the failure |
Default values, allowed values and the maximum timeout are not stated in the KB (GAPS).

## Trigger Execution (HTTP)
A switch on the exchange. On: real-time (event or callback), **cannot be scheduled**. Off: manual or scheduled. See reference 03.

## List actions
Edit (pencil), Run (play, runs immediately), Enable or Disable, History, Copy (name and code can be changed; the copy records which exchange it was extended from), Delete (confirm Ok). The grid has an **Integration Type** column: Two-Step (legacy) or Multi-Step. Copy of multi-step exchanges was listed as unsupported in the architecture article; the Copy action exists in the two-step article. Check on the environment.

## Configuration Change History
Per exchange audit: Field, Old Value, New Value, Changed Date, Username.

## Execution History (multi-step only)
Columns: Status, Start Time, End Time, Duration, Records Processed, Records Succeeded, Records Failed, Steps, Error Summary, Actions (View opens the detailed log). Not available for exchanges that use a custom processor.

## Dashboard (10.13.1.0)
Filters: Date Range (Last 24 Hours, Last 7 Days, Last 30 Days, custom), Show Duration In (Seconds, Minutes, Hours), Refresh. Cards: Successful Runs, Failed Runs, Total Runs, Total Run Time, Successful Execution Time, Failed Execution Time. Grid "Failed Workflow Executions": Exchange Name, Start Time, Duration, Records, Workflow Steps (View). Execution detail: Execution Id, Status, Trigger (Znode, Scheduler, Event, API), Triggered By, times, record counts, Error Summary categories (HTTP status failures, dependency step failures, validation failures, processing exceptions), and a step timeline with step status (Succeeded, Failed, Skipped), HTTP status, duration, records, request headers (secrets masked), request body, response.

## Validation checklist before production (KB)
Base definition complete; schedule saved; source connectivity test passes; destination connectivity test passes; mapping validated; notification recipients set; exchange enabled; a test run succeeded. Use **Test Connectivity** in SFTP and BLOB modes.
