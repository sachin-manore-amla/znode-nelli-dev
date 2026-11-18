# Znode CLI: install, connect, setup, deploy
Answers: exact commands and variants, prerequisites, token lifetime, logs and troubleshooting.
Source: KB "How to Install and Set Up Znode CLI", "Getting Started with a Znode 10 Tenant", Promotion Extensibility Developer Guide, Custom Processor Developer Guide, API and Admin Customization guides (read through summaries, 70-75). Not verified on a machine.

## Prerequisites
| Item | Detail |
|---|---|
| .NET 8.0 | Required to run the CLI (`dotnet --version`); the CLI offers to install it |
| Docker Desktop | Required by `znode deploy` (images are built and pushed); optional for `znode setup` |
| Node.js 20.0.0 or later | Webstore SDK |
| CLI token | Per developer seat, per tenant user, from Znode Support; valid one year; limits SDK and environments |
| NuGet access | Per project, from Znode Support (user name and password) |
Operating system is not stated (Windows paths in the guide).

## Install
```
dotnet nuget add source "https://nuget.znode.com/nuget" -n "NugetZnode10xCLI" -u "<username>" -p "<password>" --store-password-in-clear-text
dotnet nuget list source
dotnet nuget remove source <SourceName>
dotnet tool install Znode.CLI -g
dotnet tool update Znode.CLI -g
dotnet tool uninstall Znode.CLI -g
```
If install fails, remove and re-add the source with valid credentials. Do not commit the credentials; keep them in your own secret store.

## Commands
| Command | Purpose |
|---|---|
| `znode connect <token>` | Authenticate. Session lasts six hours; then connect again |
| `znode connect info` | Show token details (SDK access, environments). Empty output usually means an expired token |
| `znode setup` | Download the latest Webstore and Custom API SDKs |
| `znode setup --releaseVersion v10.12.1.0` or `znode setup v10.12.1.0` | A specific release (`10.12.1.0` or `V10.12.1.0`) |
| `znode setup -h` | Help |
| `znode get-updated-copy` | Fetch the latest SDK updates into the project folder |
| `znode deploy <SDKCode> <DeploymentEnvironment>` | Deploy an application. Examples `znode deploy WebStoreSDK DEV`, `znode deploy CustomAPISDK DEV` |
| `znode deploy <SDKCode> <Environment> [SourcePath] [ReleaseFolderPath]` | Optional paths; `ReleaseFolderPath` is not needed for the Webstore |
| `Znode deploy CustomAPISDK <Environment> <optional: SDK path>` | The spelling in the API Customization and Admin Customization guides (same command; the CLI executable name is `znode`, the KB capitalizes it) |
| `ZnodeDeploy` | Spelling in the legacy ERP connector setup article; treat as the same deploy (unverified) |
| `znode deploy extension "<project.csproj>"` | Build and upload one extension project |
| `znode deploy extension "<parent folder>"` | Find supported projects in the folder, build each, upload the assemblies |
Valid SDK codes beyond `CustomAPISDK` and `WebStoreSDK`, and valid environment names, are not stated (they follow your token). The extension deploy has no documented flags.

## Setup folder rules
Run `setup` and `get-updated-copy` from a dedicated folder under a drive root, for example `D:\dev\znode-10`, never the drive root, no spaces in the path. Existing files are not overwritten.

## What deploy does
Shows details for confirmation, checks token permissions for the SDK and environment, builds locally, tags an image with a timestamp, pushes it to the registry and deploys to the cluster. If your Docker uses the containerd image store, set `BUILDX_NO_DEFAULT_ATTESTATIONS=1` before deploying (attestations cause failures). Check with `docker info --format '{{.DriverStatus}}'`. If an image error appears, `docker pull` the reported tag.
The Custom API endpoint after deploy: `https://<CustomAPISDKHostedURL>/<Controller>/<Action>`; Admin custom forms: `https://<host>/CustomAdmin/<Controller>/<Action>`. Host the Custom API in the same network as the Znode API.

## Webstore local run
`npm i`, `npx nx dev webstore`, `npx nx dev page-builder` (both apps must run together). Runtime values live in each app's `.env` (`API_URL`, `API_DOMAIN`, `API_V2_DOMAIN`, `API_KEY`); the key comes from the target environment.

## Logs and troubleshooting
CLI logs: `%UserProfile%\AppData\Local\ZnodeCLILogs\`. Expired token: run `znode connect info`; if empty run `znode setup` again with a new token. WSL strain: `wsl --shutdown`, restart Docker Desktop.
