# Default templates and macros
What this answers: which default template fires for which event, and which macros it uses.
Source: KB Understanding Default Email Templates and Configuring an Email & SMS Template (read 2026-11-23). Confidence 80: the KB lists have typos and inconsistent spellings; macro lists are abbreviated here to the ones that matter. A macro is written `#Name#` and replaced at send time.

## Macro categories (Configuring an Email & SMS Template)
- Order: `#ReceiptText#`, `#OrderId#`, `#OrderDate#`, `#ShipmentNo#`, `#ShipTo#`, `#Amount#`, `#TotalCost#`, `#TrackingMessage#`, `#TrackingNumber#`, `#ShippingName#`, `#ShippingAddress#`, `#PromotionCode#`, `#PaymentName#`, `#CardTransactionID#`, `#CardTransactionLabel#`, `#PONumber#`, `#PurchaseNumberLabel#`
- Products: `#SKU#`, `#Name#`, `#ProductName#`, `#ShortDescription#`, `#Quantity#`, `#ExtendedPrice#`, `#Price#`, `#ProductLink#`, `#Image#`, `#CatalogName#`
- Customer and account: `#CustomerName#`, `#FirstName#`, `#LastName#`, `#BillingFirstName#`, `#BillingLastName#`, `#BillingAddress#`, `#BillingEmailId#`, `#Address#`, `#DisplayName#`, `#City#`, `#State#`, `#Email#`, `#EmailAddress#`, `#PhoneNumber#`, `#CompanyName#`, `#UserId#`, `#UserName#`, `#AccountName#`, `#Password#`, `#Title#`
- Store and contact: `#StoreLogo#`, `#StoreName#`, `#SiteName#`, `#StoreURL#`, `#LogInUrl#`, `#Url#`, `#Link#`, `#CustomerServiceEmail#`, `#CustomerServicePhoneNumber#`, `#ContactNo#`, `#DepartmentName#`, `#DepartmentAddress#`, `#DepartmentEmail#`
- Gift cards and vouchers: `#GCNotification#`, `#CardNumber#` (voucher number), `#ExpirationDate#`, `#VoucherNumber#`
- Messages and feedback: `#Message#`, `#EmailMessage#`, `#CustomerNotification#`, `#ShareFeedback#`, `#FeedBack#`, `#Comments#`, `#AdditionalInstructLabel#`, `#AdditionalInstructions#`, `#ErrorMessage#`
- Scheduler and jobs: `#SchedulerName#`, `#SchedulerStatus#`, `#TouchPointName#`, `#JobName#`
- Other: `#Custom1#`, `#QuoteId#`

## Templates by topic
| Topic | Template | Audience | Key macros |
|---|---|---|---|
| Accounts | Reset Password Link | customer | `#FirstName#`, `#Link#`, `#Url#`, `#StoreName#`, `#StoreLogo#` |
| | New Customer Account from Admin | customer | `#FirstName#`, `#LastName#`, `#UserName#`, `#Link#`, `#CustomerServiceEmail#` |
| | New Customer Account from Webstore | customer | `#FirstName#`, `#Url#`, `#StoreName#` |
| | Customer Account Activation | customer | `#CustomerName#`, `#Url#` |
| | Convert User To Administrator | user | `#DisplayName#`, `#ContactNo#`, `#LoginURL#` |
| | Registration Attempt Using Existing Username | customer | `#FirstName#`, `#LastName#`, `#Link#` |
| | Account Verification Request / in progress / successful | admin / customer | `#UserName#`, `#StoreName#` |
| | 2FANewVerificationCode, 2FAVerificationCode | user | `#Username#`, `#CODE#`, `#OTPExpirationTime#` |
| Orders | Order Receipt | customer | `#ReceiptText#`, `#OrderId#`, `#OrderDate#`, `#BillingAddress#`, `#ShippingAddress#`, `#PONumber#`, `#PaymentName#`, `#VoucherNumber#`, `#JobName#`, totals |
| | Cancelled Order Receipt | customer | `#OrderId#`, addresses, line macros |
| | Resend Order Receipt | customer | receipt macros, includes returned item details |
| | Shipping Receipt | customer | `#TrackingNumber#`, `#TrackingMessage#`, `#ShippingName#` |
| | Order Placed Notification | administrator | receipt macros, `#ShipTo#`, `#ShipmentNo#` |
| Approvals | Pending Order Approval | admin or manager | `#ApproveLink#`, `#OrderId#`, `#CustomerName#`, `#ApproverComments#` |
| | Pending Order Approved / Rejected / Status Notification | customer | `#QuoteId#`, `#ApproverComments#`, `#StoreName#` |
| | Billing Account Number Added | customer | `#CustomerName#`, `#StoreURL#` |
| Quotes | New Quote Request Notification For Admin | admin | `#QuoteId#`, `#QuoteStatus#`, `#QuoteDate#`, `#ExpirationDate#`, `#QuoteName#`, totals |
| | Quote Converted To Order Notification For Customer | customer | `#OrderId#`, `#QuoteId#` |
| | Quote Request Acknowledgement Notification For Customer | customer | `#QuoteId#`, `#UserName#` |
| Returns | New Return Order Notification for Admin | admin | `#OrderNumber#`, `#ReturnTotalExpectedQty#`, `#CustomerName#` |
| | Return Order Status Notification For Customer | customer | `#StoreName#`, `#OrderId#`, `#CustomerName#`, `#QuoteStatus#` |
| | Return Request Notification For Customer | customer | `#OrderNumber#`, `#ReturnTotalExpectedQty#` |
| | Refund Processed Notification For Customer | customer | `#StoreName#`, `#ReturnNumber#`, `#UserFullName#` |
| Contact and forms | Contact Us, Customer Feedback Notification, New Contact Request, Contact Acknowledgement, Service Request Message, Form Submission Acknowledgement, Form Submission Notification | admin or customer | `#FirstName#`, `#LastName#`, `#Comments#`, `#ShareFeedback#`, `#EmailMessage#` |
| Vouchers | New Voucher Issued For Customer | customer | `#CustomerName#`, `#CardNumber#`, `#Amount#`, `#StartDate#`, `#ExpirationDate#`, `#VoucherName#` |
| | Remaining Voucher Balance | customer | `#Remaining Amount#`, `#VoucherAmountUsed#`, `#CardNumber#` |
| | Reminder To Use The Voucher Balance Before It Expires | customer | `#ExpirationDate#`, `#CardNumber#` |
| Inventory | Low Inventory Order Notification | admin | `#SKU#`, `#Quantity#`, `#OrderId#` |
| | Send Waiting List Notice In Inventory | customer | `#ProductName#`, `#ProductLink#`, `#SKU#` |
| Vendors | Vendor Receipt | vendor | receipt macros |
| Marketing | Product Compare, Email a Friend | recipient list | `#ProductName#`, `#Price#`, `#Variants#`, `#ProductLink#` |
| | Product Key Order Receipt | customer | `#SKU#`, `#Name#`, `#Keys#` |
| | Customer Newsletter Onboarding, New Newsletter Signup Notification | customer / admin | `#Email#`, `#SignUpDate#` |
| Integration | ERP Task Scheduler Status | customer | `#SchedulerStatus#`, `#ErrorMessage#` |
| | Data Exchange Error Notification, Data Exchange Info Notification | configured addresses | `#DataExchangeName#`, `#SchedulerStatus#`, `#LogMessages#`, `#StartTime#`, `#EndTime#` |

## Known KB defects
A B Store registration template's description matches another template; one Pending Order Approval macro has a stray character; one macro is missing its leading `#`; scheduler macro spelled `#SchedularStatus#` and `#SchedulerStatus#`; one macro list truncated. Always preview and send a test.

## Rules
- Macros are replaced with the matching value for each recipient; macros depend on the feature that supplies the data, so not every macro works in every template.
- Subject and Content both accept macros.
- Locale: the default language is preselected; localized variants are per locale.
