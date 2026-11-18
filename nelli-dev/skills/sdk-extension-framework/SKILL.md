---
name: sdk-extension-framework
description: The Znode CLI (install, token, connect, setup, deploy and get-updated-copy with every documented syntax variant), deploying the Custom API SDK, extensions and the Webstore, the extension manifest (extension.manifest.json fields, what supportedContracts means), Extension Observability (registry, Sync, execution logs), Manage Extensions (upload, load, rollback, enable, disable, remove), which things are extensions (promotion types, Commerce Connector processors) and how each is registered in Admin, versioning and rollback. Use when deploying or updating any customization, or when an extension does not load.
user-invocable: false
---

# Znode CLI and extension framework

## What it is
The **Znode CLI** is the tool customers use to download the SDK sources and deploy their customizations to the hosted Znode environment. An **extension** is a compiled class library (not a web application) that the platform loads at runtime: promotion types and Commerce Connector processors. The **Custom API SDK** and the **Webstore** are deployed as applications. Terms people confuse: *deploy* (upload your build) versus *Sync* (tell the platform to register and load what was uploaded) versus *register* (create the Admin record that points at your class).

## Use / do not use
| Need | Verdict |
|---|---|
| Add logic to promotions | Supported: promotion extension (reference 03) |
| Add a data transformation to an exchange | Supported: processor extension (`sdk-data-exchange`) |
| New endpoint, event consumer, ERP touch point, plugin | Custom API SDK application: `znode deploy CustomAPISDK` |
| Change the Webstore | Source customization: `znode deploy WebStoreSDK` (upgrade merge risk) |
| Change Admin screens | Admin Customizations (iframe pages from the Custom API), reference 04 |
| Load an arbitrary DLL into the core API | Not supported |
| Roll back a customization | Redeploy the previous build; use Manage Extensions for extensions |

## The facts that matter most
1. Requirements: .NET 8, Docker Desktop for `deploy`, Node.js 20 or later for the Webstore, a CLI token and NuGet credentials (both from Znode Support; tokens are per developer seat, valid one year, sessions six hours).
2. Install: `dotnet tool install Znode.CLI -g` after adding the Znode NuGet source (reference 01).
3. Sign in: `znode connect <token>`; check with `znode connect info`. Tokens may be limited to an SDK and to environments (DEV, QA, PROD).
4. Download sources: `znode setup` (latest) or `znode setup --releaseVersion v10.12.1.0` / `znode setup v10.12.1.0`; update with `znode get-updated-copy`. Run in a folder at the root of a drive without spaces in the path.
5. Deploy applications: `znode deploy <SDKCode> <Environment> [SourcePath] [ReleaseFolderPath]`, for example `znode deploy CustomAPISDK DEV`, `znode deploy WebStoreSDK DEV`. Builds locally, pushes an image, deploys to the cluster.
6. Deploy extensions: `znode deploy extension "<path to .csproj>"` or `znode deploy extension "<parent folder>"`.
7. After deploying an extension: **Sync** in Dev Center > Extension Observability. Deployment alone does not activate it.
8. `extension.manifest.json` carries name, version, platform range and `supportedContracts` (reference 02).
9. Extensions are versioned by folder; the platform never overwrites an existing version, and can roll back automatically when a new version fails to load.
10. There is no processor or Custom API log viewer in Extension Observability for processors; use platform logs.

## Decision guide for Nelli-Dev
| Requirement | Verdict and approach |
|---|---|
| Deploy a new custom endpoint | Supported: `znode deploy CustomAPISDK <env>`; add the route to the Custom Ocelot file (`api-consumption`) |
| Deploy a promotion type | Supported: build class library, `znode deploy extension`, Sync, register the type in Dev Center > Promotion Settings, create promotions |
| Roll back a bad extension | Supported: Manage Extensions > version History > Load an earlier version, or redeploy the previous build and Sync |
| Roll back the Custom API | Redeploy the previous source version with the CLI (no CLI rollback command is documented) |
| CI/CD | Customizable: the CLI has a GitHub Action guide (not read); deploy needs Docker on the runner |
| Prod deployment | Follow Znode Support guidance; tokens limit environments |
| Hot-fix without downtime | Extensions can be managed without interrupting service (10.3.1.0); applications redeploy as pods |

## Reference files
- `reference/01-cli.md` install, token, connect, setup, deploy variants, logs, troubleshooting
- `reference/02-manifest.md` manifest fields, validation, supportedContracts
- `reference/03-observability-and-versions.md` Extension Observability, Manage Extensions, versioning and rollback
- `reference/04-what-is-an-extension.md` promotion extensions, processors, admin customizations, Custom API: registration of each

Related: `sdk-custom-api`, `sdk-data-exchange`, `commerce-promotions-and-pricing`, `quality-logging`.
