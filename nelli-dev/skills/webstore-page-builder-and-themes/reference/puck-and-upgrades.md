# Puck editor version and upgrade notes

What this answers: which Puck version the editor uses, what changed in 0.21.1, what custom widgets must change, and how page JSON migration works.
Confidence: KB "Puck Plugin Upgrade (v0.21.1)" read in full (80), release note 10.9.1.0, Webstore source (90).

| Item | Value |
|---|---|
| Package | `@puckeditor/core` 0.21.1 (replaced `@measured/puck` 0.17.4) |
| Release | 10.9.1.0 (April 13, 2026) |
| New | plugin rail, Delete and Backspace shortcuts, resizable sidebars, existing widgets can be dragged into Container, improved outline focus, slot architecture |

## Steps the KB gives for custom code

1. Replace the package and all imports from `@measured/puck` with `@puckeditor/core`.
2. Replace `usePuck()` with `useGetPuck()` (the Webstore wraps it in a safe helper because the storefront renders without the editor context).
3. Replace each `<Dropzone zone="Container" />` with a slot: add `Container: { type: "slot" }` to `fields` and render `<Container />`.
4. Update layout mappings; remove wrapper classes that add an extra div and move styling to the layout config.

Failure to update gives broken layouts, rendering issues or data incompatibility. Common errors: module not found (old package), deprecated hook, Dropzone breaking change, extra DOM node.

In the current source, `extend-config.tsx` still uses `DropZone` for the `disabled` root (header and footer editors). Do not copy that for new widgets.

## JSON migration

`migrateLegacyPageStructure` and `migrateLegacyData` in `packages/page-builder/src/utils/common.ts` convert legacy zones to the new structure; they run only when legacy zones are detected and are called by the editor and the storefront renderer, so no manual action is needed. A separate versioned pipeline (`lib/migrations`, `CURRENT_JSON_VERSION`, 2 in this source) migrates page JSON between structure versions. Custom widgets that change saved props incompatibly need their own migration.

## Effects on customizers

- Pin `@puckeditor/core` to the version in the source; a newer Puck can change the API.
- Re-test every custom widget in the editor after taking a Webstore upgrade.
- Release 10.4.0.0 added automatic page JSON updates when Znode widgets change; your widgets are not covered.
