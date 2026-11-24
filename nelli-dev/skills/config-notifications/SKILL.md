---
name: config-notifications
description: Znode email and SMS notifications - the CMS Email & SMS Templates screen, enabling a template per store through Configure Email & SMS Notification (area, IsActive, Blind CC), making a store-specific variant, the default templates by topic with the macros each uses, the macro syntax, per-store SMTP and advanced SMTP (OAuth) settings, per-store SMS with Twilio, why no email is sent, and the customization verdict per need (new trigger, extra data in an email, third-party email service). Load it for any transactional email or SMS requirement, a template wording or branding change, an email that does not send, or a macro question.
user-invocable: false
---

# Email and SMS notifications

Sources: Znode Knowledge Base articles Managing Email Templates, Understanding Default Email Templates, Configuring an Email & SMS Template, Configuring SMTP for Store Transactional Emails, Configuring SMS Notifications, Managing Vouchers, Managing Returns (read 2026-11-23); Configuring Advanced SMTP (Using OAuth Authentication) listed, **not read**. No exported API spec was available. Confidence 85 for template and SMTP behaviour.

## How it works
Templates are global content under **CMS > Email & SMS Templates**. A template sends only when it is **linked to an Area for a store** and active. Sending goes through the **store's SMTP server**. Macros (`#Name#`) are replaced with live values per recipient. SMS uses Twilio per store.

## Twelve facts that matter
1. **A template not enabled for a store sends no email** for that area. First check when "emails are not sending". (KB 85)
2. Enable: CMS > Email & SMS Templates > **Tools > Configure Email & SMS Notification** > choose store > **Add New** (link Area to template) > tick **IsActive** > Save. The **Edit** icon enables or disables and turns on **Blind CC**. (KB 85)
3. List actions: Add New, Preview, Edit, Save. Editor: rich text with **Tools > Source Code**. (KB 85)
4. Template fields: Locale (default language preselected), Template Name, Description (optional), Subject (macros allowed), Content (macros allowed). (KB 85)
5. There is no per-store override on a template: **clone** it (copy Source Code, Add New with a variant name such as OrderReceiptMaxwellHardware, paste, save), then point the store's Area at the new template via the Configure page. (KB 85)
6. SMTP is per store (Stores and Reps > Stores > Manage > SMTP): SMTP Port, SMTP Server, SMTP Server User Name, SMTP Server Password, From Display Name, From Email Address, BCC Email Address, Enable SSL for SMTP, Turn Off Emails. (KB 85)
7. If **From Email Address** is blank, mail goes from the store admin address (Stores > General Settings > Store Contact Information); if both are blank **no transactional email is sent**. (KB 85)
8. Ports: 25 clear-text, 465 SSL, 587 TLS (negotiated after connecting; SSL options off). (KB 85)
9. SMS (Stores & Reps > Stores > Manage Store > SMS Notifications): Provider (Twilio), AccountId, Authentication Token, Sender's Phone Number as `+` country code and number, no spaces; one sender number per store. Twilio must be integrated first. (KB 85)
10. Which macros work depends on the template: "only certain macros work with certain templates". (KB 85)
11. Order, return, voucher, inventory, quote, approval and form emails use fixed default templates: you edit their content, you do not rename the trigger. (KB 80)
12. The KB's macro lists have typos and inconsistent spellings (for example a scheduler macro spelled two ways): test each macro in a real send or preview. (KB 80)

## Default templates by topic (display names)
Full list with macros: `reference/templates-and-macros.md`.
- Accounts: Reset Password Link, New Customer Account from Admin, New Customer Account from Webstore, Customer Account Activation, Convert User To Administrator, Registration Attempt Using Existing Username, B Store Registration Request for Verification, Account Verification Request (and in progress, successful), two-factor verification codes.
- Orders: Order Receipt, Cancelled Order Receipt, Resend Order Receipt, Shipping Receipt, Order Placed Notification (admin).
- Approvals: Pending Order Approval, Approved, Rejected, Status Notification; Billing Account Number Added.
- Quotes: New Quote Request Notification For Admin, Quote Converted To Order Notification For Customer, Quote Request Acknowledgement Notification For Customer.
- Returns: New Return Order Notification for Admin, Return Order Status Notification For Customer, Return Request Notification For Customer, Refund Processed Notification For Customer.
- Vouchers: New Voucher Issued For Customer, Remaining Voucher Balance, Reminder To Use The Voucher Balance Before It Expires.
- Inventory: Low Inventory Order Notification, Send Waiting List Notice In Inventory.
- Forms and contact: Contact Us, Customer Feedback Notification, New Contact Request, Contact Acknowledgement, Service Request Message, Form Submission Acknowledgement and Notification.
- Marketing: Product Compare, Email a Friend, Customer Newsletter Onboarding, New Newsletter Signup Notification, Product Key Order Receipt, Vendor Receipt.
- Integration: ERP Task Scheduler Status, Data Exchange Error and Info Notification.

## Nelli-Dev decision guide
| Requirement | Verdict | Route |
|---|---|---|
| Rebrand the order receipt per store | Supported | Clone the template, edit, point the store's Area at it |
| Add a field (PO number, job name) to the receipt | Supported if a macro exists | Use the macro (`#PONumber#`, `#JobName#`); otherwise Customizable via method override on the email template hooks (`sdk-method-overrides`) |
| Change the receipt totals section | Customizable | Method override hook for the order or quote template content |
| A new kind of email on a custom event | Customizable | Your own service sends it (SMTP or provider), triggered by an event or webhook (`sdk-events-and-webhooks`); a new Znode trigger area is a platform change |
| Use SendGrid or another mail service | Supported | Point the store SMTP at it (the KB includes SendGrid authentication notes); OAuth variant in the advanced SMTP article (not read) |
| Different sender per store | Supported | SMTP and From settings are per store |
| SMS on order shipped | Partly | Twilio per store; the KB says admins can create SMS templates and trigger on events but gives no steps: unverified |
| Plain-text version of emails | Not documented | |
| Email on every product review | Not documented | No review template in the default list |
| Stop all email for a store | Supported | Turn Off Emails |

## Pitfalls
- Template saved but never linked to the store's Area (no mail).
- Blank From Email and blank store contact email (no mail).
- Wrong port or SSL setting for the provider (587 with SSL on).
- Editing the base template instead of cloning, changing every store using it.
- Macro not valid for that template renders empty.
- Testing only the preview: send a real one.

## Reference files
- `reference/templates-and-macros.md` – default templates with their macros, macro categories and rules.
- `reference/smtp-and-sms.md` – SMTP and SMS fields, blank-field behaviour, ports, troubleshooting order.

Related: `config-store`, `config-global-settings`, `commerce-orders`, `commerce-returns`, `commerce-vouchers`, `sdk-events-and-webhooks`, `sdk-method-overrides`.
