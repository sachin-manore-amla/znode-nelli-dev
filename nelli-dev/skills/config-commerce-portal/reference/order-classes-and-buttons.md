# Order classes and class change buttons
Answers: how to edit order numbering and the buttons that move an order to another class.
Tags: [S] source, [KB] KB read in full, [M] catalogue.

## Where
Admin: **System Settings > Commerce Settings > Order Classes** [M]. The KB says "Commerce Portal Settings > Manage Order Classes" and "Commerce Portal Settings (under Dev Center)": the three paths are not reconciled; look under System Settings and Dev Center. [KB]

## Order classes list
Columns **Class Code**, **Class Name**, **Next Number**, **Number Format**. Edit only; no delete. KB: the classes are defined by Znode and in 9.9 only Orders is supported. [KB]

| Field | Rule |
|---|---|
| Class Code, Class Name | read-only |
| **Next Number** | required, whole number 1 or more: `Number must be greater than or equal to 1` [S] |
| **Digit Length** | required, 1 to 20: `Please Enter Numeric Value Only`. Length 5, next 1 gives `00001` [S][KB] |
| **Number Format** | required, max 35: `Number format must be within a range of 01-35`; duplicate: `The number format is already used in one of the existing order classes.` Help: use a unique format per class [S] |
Macros: `<MM>` month, `<DD>` day, `<YY>` two-digit year, `<YYYY>` four-digit year, `<Number>` next number. Example `AMLA-<MM>-<DD>-<YY>-<Number>`. [KB]

## Class change buttons
Section on the class edit page. Columns **Button Text**, **When Status Is**, **To Class**, **Set Status To**, **Display Order**. Empty: `No records found`. [KB]
| Field | Rule |
|---|---|
| Button Text | max 15: `Button Text can not exceed 15 characters` [S] |
| When Status Is | statuses associated with the class; the button shows on the order only in this status |
| To Class | any class |
| Set Status To | statuses of the chosen class |
| Display Order | 1 to 99999 [S] |
In Commerce Portal the order shows the buttons for its status; clicking moves it, with the completeness and flag checks of the target status. [M]
Class operations (Internal in the API): `GET /Classes`, `PUT /Classes`, `GET/POST/PUT /ClassChangeButtons`. [S]
