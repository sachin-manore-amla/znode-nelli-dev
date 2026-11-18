# Behaviours to know, and version notes

What this answers: the behaviours that surprise people and the version history of custom table changes, so Nelli-Dev can warn early and ask which Znode version applies.

State each as a behaviour of the product, give the workaround, and check it on the customer's version: several were observed on builds before 10.14.0.0, which tightened API request validation, and some may have changed.

## Behaviours

| # | Behaviour | Workaround |
|---|---|---|
| 1 | The date type value is lowercase `datetime`. | send exactly `datetime` |
| 2 | The Admin "Number" label creates `Numeric` (a decimal); `Number` (integer) cannot be created from Admin or the API. | `Numeric` with scale 0, for example `10,0` |
| 3 | Boolean over the API rejects `yes`/`no`/`Y`/`N`; CSV import accepts `Yes`/`No`. Any non-zero number stores True. | send `true`/`false` or `1`/`0` |
| 4 | An empty date inserted through the API becomes `1900-01-01`; via import it is NULL. | filter out 1900 in reports; or use import |
| 5 | `/records` returns every row, unpaged. | use the paged data route, or cache |
| 6 | Some GET responses are double-encoded JSON. | parse again when the first parse gives a string |
| 7 | `record-exists` returns `IsSuccess: true` when rows exist. | read it as "has rows" |
| 8 | A row update returns 201. | accept 200 and 201 |
| 9 | `/CustomTable/Create` is a 404 in Admin; the working page is `CreateCustomTable`. | click through from the list |
| 10 | A blank Global Setting removes the length ceiling. | enter values |
| 11 | Text values keep leading and trailing spaces. | trim before sending |
| 12 | Re-importing into a table with no unique field duplicates rows. | add a unique field before the first import |
| 13 | The advisory limits (15 columns, 50,000 rows, one import an hour) are not enforced. | design to them anyway |
| 14 | Deleting a system table returns 404, not 403. | read the message text |
| 15 | Creating fields needs a JSON array even for one field; a bare object gives a misleading 400/500. | always send an array |
| 16 | A partial import reports success. | read View Import Logs every time |
| 17 | Export has no usable download name from the API. | use the Export screen |
| 18 | Admin silently drops Is Unique when the table already has rows. | add the unique field before data |
| 19 | Two delete paths: the row menu has a plain confirm; bulk delete needs you to type "delete". | use bulk delete deliberately |
| 20 | Changing a Field Code or Type through the API is not blocked and can corrupt data. | never do it |

## Version notes (release notes, support.znode.com)

| Version | Date | Custom table change |
|---|---|---|
| 10.5.1 | 2025-12-10 | custom table related change listed (see the notes) |
| 10.6.2.0 | 2026-01-23 | listed with the system table `ProductInformationOverrides` |
| 10.9.1.0 | 2026-04-13 | custom table related change listed |
| 10.11.0.0 | 2026-05-28 | custom table related change listed |
| 10.12.1.0 | 2026-07-10 | Field API no longer depends on `TableId`; clearer messages for missing or invalid field length (Text, TextArea, Numeric); you stay on Manage Fields after saving; long values wrap; blob file imports process supported files; PPUI Logo Library custom table search fixed |
| 10.13.0.0 | 2026-07-24 | imports no longer fail with database errors when numeric values exceed precision and scale; sorting on the Size column in the Custom Table Data API fixed; Custom Table Settings validation messages aligned |
| 10.13.1.0 | 2026-08-14 | custom table related change listed |
| 10.14.0.0 | 2026-09-04 | enhanced request validation for the Custom Tables APIs; improved validation and documentation when updating custom table data |
| 10.14.0.6 | 2026-10-13 | JSON values in narrow columns displayed more clearly |

Only some of those notes were read in full; the others matched a search for "custom table". Read the note before relying on a row.

## Always ask

"Which Znode version is the environment on?" and, for any edge case, run the case on that environment before committing a design to it.

## Sources

Observed 2026-10-05 and 2026-10-08 on development environments; release notes via https://support.znode.com/support/search?term=custom+table; KB Managing Custom Tables (43000757107).
