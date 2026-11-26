# Nelli-Dev known limits

Please read these before relying on an answer.

## What it covers
- Customization knowledge for the Custom API SDK, the Webstore, Admin configuration and Commerce Portal configuration.
- API recommendations (which routes, in which order, with parameters and authentication) and curl commands.
- Review of your customization code, and a plan, build and test flow for approved requirements.

## What it does not cover
- **Order Payment documentation is not included.** Ask Znode support for payment questions.
- **Depth varies by module.** Product documents exist for accounts, addresses and custom tables. Other modules are covered at skill level, which is shorter and less detailed.
- **It does not replace the Znode Knowledge Base.** Check support.znode.com for anything that matters to your decision.
- **The Znode platform itself is out of scope.** If a need requires changing the Znode platform, Nelli-Dev says so and does not work around it.

## How to read an answer
- Answers state a confidence level and name their sources. Lower confidence means verify before you rely on it.
- Answers can be wrong or out of date as Znode releases new versions. Report errors (see Support and feedback in `README.md`).

## API values and calls
- Values such as ids and codes are discovered only through read-only calls to your own development gateway. If no gateway is configured, curls use placeholders.
- Calls that change data need your approval for each call. Use a development or test environment, never production.

## Platform
- Tested mainly on Windows. The gateway URL and credential are environment variables the developer sets; a variable set in another window needs a Claude Code restart to be seen. The setup commands shown are PowerShell; the Linux and macOS form is less tested.
- Slash-menu behaviour and plugin updates depend on your Claude Code version.

## Generated code
Generated code and plans must be reviewed, built and tested by you before deployment. The plugin is provided as is (see `LICENSE`).
