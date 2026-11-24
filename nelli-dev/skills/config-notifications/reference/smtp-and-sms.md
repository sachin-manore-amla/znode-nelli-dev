# SMTP and SMS
What this answers: how a store sends email and SMS, and the order in which to check when nothing arrives.
Sources: KB Configuring SMTP for Store Transactional Emails, Configuring SMS Notifications, Managing Email Templates (read 2026-11-23); advanced SMTP (OAuth) not read. Confidence 85.

## SMTP (Stores and Reps > Stores > Manage > SMTP)
| Field | Purpose |
|---|---|
| SMTP Port | server port (25, 465, 587) |
| SMTP Server | address, for example smtp.gmail.com |
| SMTP Server User Name / Password | login |
| From Display Name | name shown in the email |
| From Email Address | sender for customer emails |
| BCC Email Address | copy of every customer email |
| Enable SSL for SMTP | secure connection; must be enabled at both ends |
| Turn Off Emails | stops email sending for the store |
Ports: 25 clear text; 465 SSL (not TLS); 587 TLS negotiated after connecting, SSL options off.
All store emails go through this one server. SMTP must be configured before notification emails send.
Blank fields: From Email Address blank: sent from the store admin address (Stores > General Settings > Store Contact Information). Both blank: **no transactional email**. Others: not documented.
SendGrid note in the article: enable two-factor authentication, verify a single sender, authenticate the domain (provider-side steps, not Znode fields).
OAuth variant: "Configuring Advanced SMTP (Using OAuth Authentication) for Store Transactional Emails" exists in the Stores folder; read it before using Microsoft or Google OAuth (unverified).

## SMS (Stores & Reps > Stores > Manage Store > SMS Notifications)
Provider (Twilio), AccountId, Authentication Token, Sender's Phone Number (`+` country code and number, no spaces). Twilio must be integrated first. One sender number per store covers one country or region; messages to other countries may cost more. The article says admins can create SMS templates and trigger messages on events or actions but gives no steps (unverified).

## When nothing arrives: check in this order
1. Turn Off Emails off? 2. From Email Address or store contact email present? 3. SMTP server, port, user, password, SSL correct for the provider? 4. Template linked to the Area for this store and IsActive (Tools > Configure Email & SMS Notification)? 5. Template content and macros valid (preview)? 6. Provider spam or sender authentication (SendGrid domain authentication)? 7. Customer email address correct.

## Customization
Per-store sender and provider are configuration. A different delivery mechanism per event needs your own service plus an event or webhook (`sdk-events-and-webhooks`). Log and retry behaviour of failed sends: not documented.
