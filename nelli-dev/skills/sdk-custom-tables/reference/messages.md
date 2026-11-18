# Messages and when they appear

What this answers: the exact text of Admin and API messages for custom tables, fields, records and import/export, and the condition behind each. Verified on a development environment and in source (2026-10); a few texts differ slightly by build, shown in brackets.

## Tables (Admin)

| Message | When |
|---|---|
| *The Table Key field is required.* | Table Key empty |
| *Table Key can not exceed 100 characters.* | key over 100 |
| *The Table Key must start with a letter and contain only alphanumeric characters (A-Z, a-z, 0-9). Spaces and special characters are not allowed.* | invalid key |
| *The Table Name field is required.* · *Table Name can not exceed 100 characters.* | name empty or over 100 |
| *The Table Name must start with a letter and can contain only alphanumeric characters, spaces between words, underscores, and hyphens.* | invalid name |
| *Table Key Already Exist* | a table with that key exists (case-insensitive) |
| *Record created successfully.* · *Failed to create record.* | create result |
| *Record updated successfully.* · *Failed to update record.* | edit result (success text can show even if the back end failed) |
| *The selected table(s) may have data associated with it. Proceeding with this action will delete the table and its associated data (if any). To confirm the deletion, please type 'Delete' in the text box below:* · title *Confirm Delete?* | bulk delete dialog |
| *Invalid keyword entered, please try again.* | anything but "delete" typed |
| *Record deleted successfully.* · *Failed to delete the record.* | delete result |
| *No Data Available to Export.* | Export on an empty table |
| Note popup about needing a unique field | Add a Record or Import on a table with no unique field |

## Tables (API)

| Message | When |
|---|---|
| *The requested table does not exist* | key matches no (non-system) table |
| *Deleting System Tables is not allowed* | delete of a system table (HTTP 404) |
| *TableKey can not be null or empty.* | bulk delete with a blank key |
| *Id cannot be less than 1.* | missing key or non-positive id on delete or update |
| *Table Key can only contain letters and numbers.* · *Table Key cannot exceed 100 characters.* | invalid key on a route |
| *The TableId is required.* | table update without an id |
| *Custom table deleted successfully.* · *Failed to delete custom table.* | per key in bulk delete |

## Fields

| Message | When |
|---|---|
| *Field Code Already Exist* | code already in the table (case-insensitive) |
| *Multiple fields cannot be set as Unique.* | more than one unique field |
| *The field cannot be added or modified with a UNIQUE constraint after data has been inserted into the custom table.* | add unique when rows exist (API; Admin silently saves it as not unique) |
| *The field code 'ID' is reserved and cannot be used. Please choose a different code.* | code `Id` |
| *Input value must not exceed the maximum character limit of N.* [*...the character limit of N.*] | length over the Global Setting |
| *Input value must not exceed the maximum limit of precision: P and scale: S.* | Numeric over the Global Setting |
| *FieldLength for field '{code}' must be a positive integer.* | length missing, zero or negative |
| *FieldLength for field '{name}' must include both precision and scale (e.g., "10,2").* · *Invalid format for numeric field '{name}'. Use 'precision, scale'.* · *FieldLength for field '{name}' is invalid: precision must be > 0 and scale must be between 0 and precision.* | Numeric length format |
| *The field set as unique cannot be deleted.* (Admin) · *A unique field cannot be changed as data associated with the table.* (API) | delete or edit a unique field |
| *Display order can not be less than one* (API) · *Display Order should be between 1 and 500.* (Admin) | display order |
| *The Field Name is required.* · *The Field Code is required.* · *The Field Type is required.* · *The Field Type can not exceed 10 characters.* | blanks and over-long type |
| *Only alphanumeric characters are allowed.* · *Field Code can not exceed 100 characters.* · *Field Name can not exceed 100 characters.* | code and name rules |
| *Key not found* · *Id can not be less than one* | field delete with a bad table key or empty parameters |
| *The definition for column 'X' must include a data type.* (raw database text inside the field list) | unrecognised field type |

## Records

| Message | When |
|---|---|
| *Record created successfully.* · *Failed to create.* | Admin create |
| *A record with this unique key already exists. Please ensure that the value entered for the unique key column is distinct.* | Admin create hits a unique conflict |
| *A record with the value "EAST" already exists. "RegionCode" must be unique.* | API create with a duplicate unique value (observed) |
| *Record saved successfully.* · *Failed to update record.* | Admin edit (the edit path does not name unique conflicts) |
| *You cannot save an empty record. Please enter a value in at least one field before saving.* | Admin form with all fields empty |
| *Input cannot exceed the maximum character limit of N.* | Admin client check |
| *The numeric value should fall within the range of (P,S)* | Numeric out of range (Admin and API) |
| *FieldValue is required for Unique Field: {FieldCode}* · *Input is required.* | unique field blank, or a unique Numeric field equal to 0 |
| *No records were found for the requested row id.* · *Row Id must be a positive integer.* | row id not found or invalid |
| *Table does not have unique column.* · *Unique column not found* · *Unique column does not contains provided unique values* | unique lookup or bulk update on a table without a unique field, or no match |
| *Table not found* · *Invalid column* | bulk operations: table or column unknown |
| *The requested object contains more than one record.* | `/insert` with more than one object |
| *The input is invalid. Please provide a JSON array containing valid objects.* · *Please provide a non-empty JSON array.* | bad bulk or single-insert body |
| *Model cannot be null.* | empty model (also shown when an update affects 0 rows) |
| *The operation could not be completed...* (generic) | type or length violation on a single-row API write |

## Import and export

| Message | When |
|---|---|
| *Only select a CSV file.* · *Please select file with .csv extension only* · *File not present.* | file chosen wrongly or missing |
| *Filename cannot exceed the 200 characters.* | long CSV name |
| *CSV does not contain any data.* · *No data found in the CSV file.* | empty CSV |
| *Update process has been initiated.* [with a link to import logs] · *Import has been initiated. Click here or redirect to the Imports screen to view more details.* | upload accepted |
| *Import process failed. Please review the logs for more details.* | import failed |
| *Data column must be mapped with the template.* | a column is not a field (whole import) |
| *Unique column must be included in the import/update file.* | unique column missing (whole import) |
| *Duplicate records must be excluded from the import/update file.* | duplicate unique values in one file |
| *The input cannot be added as it already exists in the database.* · *Input cannot be updated because of its unavailability in database.* | unique value exists or is missing for the mode |
| *Input value must either be True/1/Yes or False/0/No.* | Boolean value |
| *Input must include a valid date and time.* | date |
| *Input value must not exceed the maximum character limit of N* · *The numeric value should fall within the range of ...* | length or precision |
| *All column data in the provided row is empty.* | blank row |
| *Import failed due to database error.* | unexpected database error |
| *The file does not exist or you don't have file access rights.* | file not readable in blob storage |
| *Export has been initiated. Please wait, this may take a few minutes.* · *Export has been initiated. Click here or redirect to the Exports screen to view more details.* | export queued |
| *No Data To Export the Custom Table* | export of an empty table |
