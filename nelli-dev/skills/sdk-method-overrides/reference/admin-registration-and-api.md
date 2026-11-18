# Registering a method override
What this answers: the Admin steps, field labels, validation messages and API routes for registering, verifying and managing a hook.
Source: Admin source and resource strings (95), release notes 10.2.1 (80).

## Admin steps
Menu: **Dev Center > Method Override**, page title "Manage Method Override Configurations". The list shows Module Name, Method Name, Webhook URL, Is Active and an Action column (Edit, Delete, Enable/Disable).
1. Click **Add New** ("Method for Override").
2. **Module Name** (required): pick the module. Help: "Select the module that includes the method that needs to be overridden."
3. **Method Name** (required): pick the method. A description, a **Sample Request JSON** link and a **Sample Response JSON** link appear.
4. **Is Active** (Yes/No): "Toggle to enable or disable sending this event to the configured webhook URL."
5. **Webhook Url** (required): full URL, HTTP POST target.
6. **Authorization** (optional): "included in the Authorization header exactly as provided (for example Bearer token or API key)".
7. Click **Verify**. Admin POSTs the method's sample request to your URL with your Authorization value and checks the reply has non-empty `responsePayload` and `eventPayload`, and a `skipExecution` value, and that the response payload has the same format as the sample. Success text: "The URL is verified successfully." If module or method is not chosen: "Please select Module name and Method name." Otherwise the URL is reported invalid.
8. **Save** or **Save and Close**. Save and Close stays disabled until Verify succeeds.
On edit, Module and Method are read-only. After saving, Znode clears its hook cache.

## Fields and validations
| Field | Rule | Message |
|---|---|---|
| Module Name | required, max 200 | "{0} is required." / "EventName cannot exceed 200 characters." |
| Method Name | required, max 100 | "EventModule cannot exceed 100 characters." |
| Webhook Url | required; must match `http(s)://host.tld[/path]`, max 1000 | "Webhook Url should be a proper URL." / "Webhook Url cannot exceed 1000 characters." |
| Authorization | optional, max 1000 | "Authorization cannot exceed 1000 characters." |
Other messages: "Record created successfully.", "Updated successfully.", "Failed to update record.", "Record deleted successfully.", "Status successfully changed to Active." / "...to Inactive.".
A host without a dot (a cluster-internal name such as `http://custom-api`) fails the Admin URL pattern; use a fully qualified name or register through the API.
Verify disables itself when the URL is empty. Verify uses the platform's request timeout; certificate errors are ignored by Verify only (not by the runtime call).

## API (Customer API v2, see `api-catalog`)
| Operation | Route |
|---|---|
| List hooks | `GET /v2/methods-list` |
| Create | `POST /v2/methods` |
| Get | `GET /v2/methods/{methodName}/{moduleName}` |
| Update | `PUT /v2/methods/{methodName}/{moduleName}` |
| Delete | `DELETE /v2/methods/{methodName}/{moduleName}` |
| Enable/disable | `PUT /v2/methods/{methodName}/{moduleName}/{isActive}` |
| Module names | `GET /v2/methods` |
| Methods of a module | `GET /v2/methods/{moduleName}` (each with sample request/response JSON and a description) |
`{moduleName}` is the module **display name** (for example "Calculate Cart"), not the code. Create body fields: `ModuleDisplayName, MethodName, WebhookUrl, IsActive, AuthorizationHeader`. Verify the exact schema with `nd_query_spec.py`. Errors: "Invalid MethodName - '...' or ModuleDisplayName - '...'", "Webhook is already configured for the MethodName - '...'".

## Deploy order for a customization
1. Build and deploy the receiver (Custom API SDK) and note its URL.
2. Register in Admin on a development environment first; verify.
3. Test with real carts (`building-a-receiver.md`).
4. Register the same hook on the next environment. Hooks are environment data, not code: they do not travel with a deployment.
5. To roll back: set Is Active to No (immediate).

## Release history
10.1.1 (2025-06-23) first override for email template binding. 10.2.1 (2025-08-08) Method Override menu, only the two Quote methods. 10.10.0 (2026-04-28) shopping cart calculation override. The Commerce Portal calculate hook and the tax-code hook were added in 10.x after that; confirm availability on your environment in the Module list.
