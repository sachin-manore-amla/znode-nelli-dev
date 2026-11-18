# Code-level route: a Custom Page backed by the Custom API SDK
Answers: how to build, host and connect an admin page that shows or saves your own data, and what RegisterCustomAdminServices and RegisterCustomAdminMiddlewares do.
Tags: [S] SDK/product source, [KB] KB read in full, [I] inference.

## Pieces
| Piece | What it is |
|---|---|
| `Custom.Admin.Core` | SDK library with the admin-page plumbing and two sample controllers (`StoreController`, `CustomAccountController`) [S][KB] |
| `Engine.Custom.Api` | The SDK host. Its start-up calls `RegisterCustomAdminServices` before the app is built and `RegisterCustomAdminMiddlewares` after [S] |
| Views | `CustomAdmin/Views/<ControllerName>/<ActionName>.cshtml` inside the host project; the registration adds this location to Razor's search paths [S][KB] |
| Route | `CustomAdmin/{controller}/{action}/{id?}` [S] |
| Admin Customization entry | The Custom Page or Section whose Content Details is the full address of the action [KB] |

## What the two calls do
| Call | Effect |
|---|---|
| `RegisterCustomAdminServices` | Registers your admin dependencies (`RegisterCustomAdminDI`, empty in the template), reads the `AppSettings` key `ZnodeAdminURLCorsPolicy` (comma separated origins) and creates the CORS policy of the same name, adds MVC and controllers with views, and adds the view folder [S] |
| `RegisterCustomAdminMiddlewares` | Maps the route `CustomAdmin/{controller}/{action}/{id?}` [S] |

If `ZnodeAdminURLCorsPolicy` is empty, no policy is created and actions marked with it fail at run time [I].

## Controller pattern (from the sample)
```csharp
[ValidateAuthHeader]                    // Basic auth, see below
public class StoreController : Controller
{
    [EnableCors("ZnodeAdminURLCorsPolicy")] [HttpGet]
    public virtual ActionResult StoreDetails(string StoreCode, string PortalID) { /* decode, call APIs, return View() */ }

    [EnableCors("ZnodeAdminURLCorsPolicy")] [HttpPost]
    public virtual JsonResult StoreDetails() { /* save through your API, return Json */ }
}
```
- `ValidateAuthHeader` accepts a request only if its Basic `Authorization` header decodes to `<domain name>|<domain key>` equal to the host's own `ZnodeApiDomainName` and `ZnodeApiDomainKey` settings. Otherwise it answers 401 with `You are unauthorized to access this resource.` [S]
- Admin sends exactly that header when it fetches a `URL` content page, so the page works through the Admin. A browser opening the address directly gets 401. [S]
- The sample view builds its form action from the request (`scheme://host/CustomAdmin/Store/StoreDetails`), which the KB recommends so the parent page is not referenced. [S][KB]
- Macro values arrive as Base64: the sample decodes with a helper and shows "Contents are not properly encoded!" on failure. [S]
- The sample POST is a stub that returns JSON with `status=false` and a text saying the form was submitted. Replace it. The sample page fields (Business Unit, Region, Primary Customer Vertical, Customer Type) are placeholders; the sample does not call an ERP. [S]

## Steps
1. Copy a sample controller and view in the SDK; keep `[ValidateAuthHeader]`. Add the Admin address to `ZnodeAdminURLCorsPolicy` in the host settings (the KB says DevOps does this in a managed environment). [KB]
2. In the view, call Znode APIs or your own endpoints through the gateway and clients (KB). Do not use direct database access (`sdk-custom-api`).
3. Deploy: `Znode deploy CustomAPISDK <Environment> <optional SDK path>`. The page address is `https://<CustomAPISDKHostedURL>/CustomAdmin/<Controller>/<Action>?<name>=<value>`. [KB]
4. In **Dev Center > Admin Customizations > Add New**: choose Page or Section, Content Type `URL`, put the address with macros (for a section, `?StoreCode=#StoreCode#&PortalID=#PortalID#`), pick roles, save. [KB][S]
5. Add the Admin origin to the Admin Content Security Policy if your page posts a form or opens frames on your host (`security-and-limits.md`).
6. Test with a user holding only the chosen role.

## Displaying custom table data (KB pattern)
Create a Custom API action that reads the custom table (Custom Table API), reference it from the admin form, deploy, add the form address as a Custom Section. [KB] See `sdk-custom-tables`.

## Gaps for developers
- Only a GET view and a form POST are in the sample; there is no sample of a page that calls a Znode API (the KB says it can). [S]
- The SDK has no automated test for admin pages. [S]
