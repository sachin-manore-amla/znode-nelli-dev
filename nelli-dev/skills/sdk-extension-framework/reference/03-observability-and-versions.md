# Extension Observability and Manage Extensions
Answers: the Admin screens that show and manage deployed extensions, Sync, logs, versioning and rollback.
Source: Admin and API source (90); the screens ship with the 10.10 database script (Extension Observability menu); the version-management screens are in the Admin source and may not exist in older releases (GAPS). KB Promotion Extensibility guide (75).

## Extension Observability
Path: **Dev Center > Extension Observability**. Header buttons **Sync Versions** and **View Logs**. Summary: Total, Loaded, Failed, Last refreshed (UTC). Grid: Status (Loaded, Reloaded, Failed), Extension Name, Class, Version, Environment, Last Loaded (UTC), Message, Logs (and a link to the version history). Empty state: "No extensions are currently registered. Start the CommercePortal API and load at least one extension."
Logs page ("Extension Execution Logs"): filters Extension, Status / Level (Success, Failed, Warning, Information, Error), From and To (UTC dates), Correlation ID (GUID), Filter and Clear; a log entry has a detail page. API: extension status `GET /api/v1/extensions/{extensionId}/status` and execution logs in the Commerce API (internal routes `/extensions/logs`).
**Sync** after every deploy: rescans the extension storage for version folders not yet registered (for example deployed by the CLI), registers them and reloads. Deployment alone does not activate.

## Manage Extensions (versions)
Reached from Extension Observability (Versions link) and listed at "Manage Extensions". Summary: Total, Active, Disabled, Removed. Columns: Status (Active, Disabled, Removed), Extension, Active Version, Registered, Actions (History, Enable or Disable). Empty state: "No extensions are registered. Deploy an extension via the ZNode CLI, then use Sync on the Extension Observability page to register it here."
Version history ("<name> - Version History"): Status (Active, Failed, Inactive), Version, Upload Date, Uploaded By, Path, Actions **Load** (force-activate that version, overriding the current), **Remove** (permanently deletes that version's folder; never shown for the active version), **Unload** (stop serving; no version active until you Load one).
**Upload Extension Version** form: Extension Name (must match the manifest), Package (ZIP with `extension.manifest.json` at the root), button "Upload & Activate".

## Version rules
- Folder layout per extension: one folder per version; the active version is the one served.
- Upload never overwrites an existing version.
- New version is registered Inactive, loaded, then promoted; on load failure it is marked Failed and the previous version is reactivated automatically ("Extension Rolled Back (Auto)" in the logs).
- Manual rollback: Load an earlier version (an earlier version stays on disk until removed).
- Enable and Disable an extension; Remove deletes it.
- Use semantic versions and keep release notes per deployment (KB). Avoid breaking changes in minor releases.

## Rollback paths
| Case | Action |
|---|---|
| New extension version fails to load | Automatic return to the previous version; read the log message |
| New version loads but behaves wrongly | Manage Extensions > History > Load the previous version |
| Version folder missing | Redeploy the previous build with the CLI, then Sync |
| Custom API application | Redeploy the previous source with `znode deploy CustomAPISDK` |

## Behaviour to know
The registry is held by the Commerce Portal API; with several instances, Sync and Load apply to the storage they share. Data Exchange processors are loaded by a different mechanism and are not shown here (KB: no extension observability, sync or log viewer for processors).
