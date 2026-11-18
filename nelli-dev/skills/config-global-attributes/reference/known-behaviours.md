# Known behaviours
Things about user-defined fields that surprise people. Each is stated neutrally with how sure we are.
Read it before you design, test or answer a customer.

| # | Behaviour to know | Confidence |
|---|---|---|
| 1 | Entity type, attribute type and code cannot be changed after the field is created | 90, Admin form |
| 2 | The v2 API has no call to edit a field definition. Edits are Admin only | 85, source routes |
| 3 | A new Simple or Multi Select field starts inactive and becomes active when its first option is saved | 90, source |
| 4 | Options must be saved after the field. The Admin says `Please save attribute before Saving its default values.` | 90 |
| 5 | The v2 value write rejects blank values. You cannot clear a value with it. It also checks Date, Number and select values only, not Required, length, pattern, range or uniqueness | 90, source |
| 6 | The v2 write validates the record against the first field's entity type. Send one entity type per request | 85 |
| 7 | The `Unique Value` check on Text fields is a pre-save check run by the Admin. It builds its lookup from naming conventions and ignores any failure, so it can answer "no duplicate" for entities where it cannot run. For brands it never finds a duplicate. Do not rely on it as a constraint | 85 module guide, 80 source |
| 8 | Entity names: the attribute create call needs the name as listed (`Price List`). The value write accepts it without spaces (`PriceList`) | 85 |
| 9 | An attribute can be in one group only (v2). Group and attribute must share the entity type | 90 |
| 10 | Deleting a field, group or family that is in use is refused. Unassign first | 90 |
| 11 | A group with no name in the default language may not show in some lists | 70, module guide |
| 12 | Values on an entity screen without a language switch are saved in the default language | 85 |
| 13 | Last save wins. Two admins editing the same record overwrite each other silently | 85 |
| 14 | Opening a record, leaving the page open and saving later can overwrite newer values with old page values | 85 |
| 15 | Label type shows its default text and takes no input | 90 |
| 16 | Multi Select values are stored as a comma-separated list of option codes. Labels must not contain a comma | 90 |
| 17 | A Date default or value is shown in the display time zone and saved in the saving time zone. Test around midnight | 70, source |
| 18 | UDF values are not covered by the XSS validation added in 10.13.1.0 | 85, source reading |
| 19 | The v2 value write raises no domain event. The Admin save does | 85 |
| 20 | Deleting a brand removes its UDF values first. If the brand delete then fails, the brand remains without its values | 85 module guide |
| 21 | The public spec copy lacks several v2 routes that exist in the product (marked SRC in api-and-values.md) | 90 |
| 22 | The File field extension list in the product includes video and audio extensions, which contradicts an older note that video is not allowed. Confirm on your environment | 70 |
| 23 | Content Containers must have a family. `POST /v2/content-containers` fails validation without `FamilyCode` | 90 |
| 24 | For the Account entity the built-in fields (voucher reminder days, business identification number, price list inheritance) sit next to custom groups. A blank account value falls back to the store value for voucher reminders | 80, KB |

## Where the Knowledge Base differs from the product

| Topic | KB says | Product shows | Wins |
|---|---|---|---|
| Entities that support UDFs | 28 entity types | The product creates more (Order, Quote, Pending Order, Return, Line Item and line items) and the Admin has UDF sections for Order, Quote and Return | Product |
| "Dynamic Schema" menu | Article names `Dev Center > User-Defined Fields` | Menu text `User-defined Fields` with Attributes, Attribute Groups, Attribute Families, Entity Attributes | Same, case differs |
| Additional Attributes live without publish | "Additional Attributes ... live immediately" | The store publish also snapshots store UDFs, and the KB store article says some store flags need a store publish | Test per field; treat store flags as needing a store publish |
| UDF XSS | Release note 10.13.1.0 mentions product attributes only | Same | Product |
| Forms | KB: "For forms, use the Content Container type" | Forms have their own entity (Form Builder). The KB sentence is unclear (GAPS) | Product |

KB URLs: Dynamic Schema Overview 43000757209, User Defined Fields Groups and Families 43000757197, Managing Attribute Groups 43000761422, Additional Account Attributes 43000756947, Additional User Attributes 43000756955, Additional Store Attributes 43000756904, Custom Forms 43000756968, Content Container 43000757216, What Requires Publishing 43000757211, all at `https://support.znode.com/support/solutions/articles/<id>`.
