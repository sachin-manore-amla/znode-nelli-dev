---
name: config-notifications
description: "Znode email and SMS templates - the admin path and per-store enablement, the complete default template list with triggers, the macro token syntax, how to make a store-specific variant, per-store SMTP configuration and Twilio SMS setup. Use when an email is not sending, when adding or editing a template, or when looking up which template fires for an event."
user-invocable: false
---

# Znode Email & SMS Templates

Admin path: `CMS > Email & SMS Templates`

Templates are **global** but must be **explicitly enabled per store**: `Tools > Configure Email & SMS Notification` → select Store → **Add New** to associate an **Area** of Znode with a template → tick `IsActive`. The Edit icon also enables/disables a template and turns on **Blind CC**.

> **If a template is not enabled for a store, Znode sends no email at all** for that area. This is the first thing to check when "emails aren't sending".

Editor: Rich Text Box (WYSIWYG) with `Tools > Source Code` for raw HTML. A **Preview** action exists on the list.

### Making a store-specific variant

There is no per-store override on a template — you clone it:

1. Open the base template, `Tools > Source Code`, copy it.
2. `Add New`, name it distinctly (e.g. `OrderReceiptMaxwellHardware`).
3. Paste the source, edit, save.
4. `Tools > Configure Email & SMS Notification` → pick the store → edit the Area row → **point it at the new template** → save.

## Default templates by trigger

**Identity:** `ResetPasswordLink` · `NewCustomerAccountFromAdmin` · `NewUserAccountWebstore` · `AccountActivation` · `AccountVerificationRequest` / `AccountVerificationSuccessful` · `ConvertUserToAdministrator` · `RegistrationAttemptUsingExistingUsername`

**Orders:** `OrderReceipt` / `StoreOrderReceipt` · `OrderPlacedNotification` (admin) · `ShippingReceipt` · `TrackingLinks` · `CancelledOrderReceipt` · `ResendOrderReceipt` · `VendorReceipt` · `ProductKeyOrderReceipt`

**Approvals:** `PendingOrderApproval` (admin) · `PendingOrderApproved` · `PendingOrderRejected` · `PendingOrderStatusNotification` · `BillingAccountNumberAdded`

**Quotes:** `QuoteRequestAcknowledgementNotificationForCustomer` · `NewQuoteRequestNotificationForAdmin` · `QuoteInReview` · `QuoteApproved` · `QuoteRejected` · `QuoteStatusNotification` · `QuoteConvertedToOrderNotificationForCustomer`

**Returns:** `NewReturnOrderNotificationForAdmin` · `ReturnRequestNotificationForCustomer` · `ReturnOrderStatusNotificationForCustomer` · `RefundProcessedNotificationForCustomer` · `RMARequestStatus`

**Vouchers:** `NewVoucherIssuedForCustomer` · `RemainingVoucherBalance` · `ReminderToUseTheVoucherBalanceBeforeItExpires`

**Forms & contact:** `FormSubmissionNotification` · `FormSubmissionAcknowledgement` · `ContactUs` / `NewContactRequest` · `ContactAcknowledgment` · `CustomerFeedbackNotification`

**Inventory & ops:** `LowInventoryOrderNotificationTemplate` · `SendWaitingListNoticeInventory` · `ERPTaskSchedulerStatus`

**Marketing / sharing:** `ProductCompare` · `EmailAFriend` · `CustomerNewsletterOnboarding` · `NewNewsletterSignupNotification`

## Macro syntax

All macros use `#MacroName#`, replaced with live data at send time.

| Macro | Value |
|---|---|
| `#StoreName#`, `#StoreURL#`, `#StoreLogo#` | Store identity (used by ~30+ templates) |
| `#OrderId#`, `#OrderDate#` | Order identifiers |
| `#ReceiptText#` | Full receipt HTML |
| `#FirstName#`, `#LastName#`, `#CustomerName#` | Customer name |
| `#BillingAddress#`, `#ShippingAddress#` | Addresses |
| `#TrackingNumber#` | Shipment tracking |
| `#SKU#`, `#Name#`, `#Quantity#`, `#Amount#` | Line item fields |
| `#QuoteId#` | Quote ID |
| `#CardNumber#`, `#ExpirationDate#` | Voucher fields |
| `#Link#` | Password reset link |
| `#CustomerServiceEmail#`, `#CustomerServicePhoneNumber#` | CS contacts |

Not every macro applies to every template — the KB macro table maps applicability.

## SMTP (per store)

`Stores > Manage > SMTP`

| Field | Notes |
|---|---|
| SMTP Server / Port | 25, 465 or 587 |
| Server User Name / Password | Auth credentials |
| **From Email Address** | **If blank, no emails are sent at all** |
| BCC Email Address | Blind-copies every email |
| Enable SSL for SMTP | Toggle |
| Turn Off Emails | Disables all email for the store |

OAuth-based SMTP is at `Stores > Manage > SMTP > OAuth path`. V2 API: `GET/POST/PUT /v2/stores/{storeCode}/advanced-smtp`.

## SMS

Provider: **Twilio only**. `Stores > Manage > SMS Notifications`

`Provider` (Twilio) · `AccountId` (Twilio Account SID) · `Authentication Token` (Auth Token) · `Sender's Phone Number` in `+CountryCodeNumber` format, no spaces, one number per store.

Engine: `Znode.Engine.SMS`.

## Tables

`ZnodeEmailTemplate` (54) · `ZnodeEmailTemplateLocale` (72) · `ZnodeEmailTemplateMapper` (170, event → template) · `ZnodeEmailTemplateAreas` (59, modular sections) · `ZnodeEmailTemplateMessageToken` · `ZnodeEmailProvider` · `ZnodeSmsProvider`. Cleanup is driven by the `DeleteAlreadySentEmails` / `DeletePendingEmails` global settings.

## KB source

- [Managing Email & SMS Templates](https://support.znode.com/support/solutions/folders/43000598133)

## Related
`config-global-settings` · `commerce-orders` · `commerce-promotions-and-pricing`
