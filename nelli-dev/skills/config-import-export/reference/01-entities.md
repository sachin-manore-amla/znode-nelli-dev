# Import entities, templates and key columns
Answers: for each import type, the key that decides create versus update, the required and optional columns and their allowed values.
Source: KB "Bulk Importing and Updating Data" read through a summary (70-75); v2.1 API operation (90). Column names are as in the template; download the template from the screen to confirm for your version.

Common: Boolean columns use `0` or `1`. `DisplayOrder` accepts 1 to 99999. Codes (attribute, category, brand, highlight) are alphanumeric, start with a letter, no spaces or special characters. Attribute max lengths come from the PIM attribute definitions and apply to import and Admin alike; a newly required attribute becomes required in import.

| Import type | Context chosen on screen | Upsert key |
|---|---|---|
| Product | Family | SKU |
| Product Association | none | none stated (ParentSku + ChildSKU) |
| Product Attribute | none | AttributeCode (create) |
| Attribute Default Value | none | AttributeDefaultValueCode |
| Highlights | none | HighlightCode |
| Addon Association | none | SKU + AddOnSKU |
| Pricing | none (PricelistCode in file) | PricelistCode + SKU (+ tier) |
| Inventory | none | SKU + WarehouseCode |
| Category | Category family | CategoryCode |
| Category Association | none | CategoryCode + SKU |
| Catalog Category Association | Catalog | CategoryCode (+ParentCode), Action Add or Delete |
| Zip Code | Country | create only |
| Customers (Users) | Store | Username |
| Customer Address | none | Username + DisplayName |
| Accounts | Store | AccountCode |
| SEO Details | Store | Code + ImportType |
| Brands | none | Brand Code |
| Vouchers | none | VoucherNumber |
| Synonyms | Catalog | SynonymCode |
| Sales Reps | none | User Name |
| Promotions | Discount Type | PromoCode |

## Products
Required: `ProductType` (SimpleProduct, ConfigurableProduct, BundleProduct, Grouped Product), `ProductName`, `SKU`, `IsActive`, `ProductCode`, `MinimumQuantity` (more than 1), `MaximumQuantity` (more than minimum), `OutOfStockOptions` (DontTrackInventory, DisablePurchasing, AllowBackOrdering), `ShippingCostRules` (WeightBasedRate, QuantityBasedRate, FlatRatePerItem, FixedRatePerItem).
Optional: IsObsolete, Color, Size (existing option codes), HideFromSearch, IsDownloadable, long and short description, Product Specification, FeatureDescription (HTML), UPC, Assortment, Call For Pricing, Brand, Vendor, Highlights (comma separated codes), Tags, ProductImage, GalleryImages (Media Manager file names, gallery comma separated), UOM, Video1, Video2, TypicalLeadTime, DisplayVariantsOnGrid, FreeShipping, Weight, Height, Width, Length, Container, PackagingType.
SKU: alphanumeric only (reference 02). **Configurable products:** any non-blank configurable attribute column (Size, Color, Style) on a ConfigurableProduct row makes that attribute configurable; blank columns are ignored. Link variants with a Product Association import afterwards; variants must already exist.

## Product Association
Required `ParentSku`, `ChildSKU` (both exist), `DisplayOrder`, `IsDefault`. Optional `Quantity` (1 to 99999, required for bundles). For configurable, bundle and grouped parents.

## Product Attribute
Required `AttributeName`, `AttributeCode`, `AttributeType` (Date, File, Image, Label, Link, Multi Select, Number, Simple Select, Text, Text Area, Yes/No). Optional `DisplayOrder`. Create only.

## Attribute Default Value
Required `AttributeCode` (exists), `AttributeDefaultValueCode`, `AttributeDefaultValue`, `DisplayOrder`. Optional `IsDefault` (default 0), `SwatchText` (hex starting `#`), `SwatchImage` (Media file name). Do not repeat a value code in one file. Invalid attribute codes are rejected (10.13.1.0).

## Highlights
Code must already exist under Marketing > Product Highlights. Required `HighlightCode`, `HighlightName` (any value), `IsActive`, `DisplayOrder`. Optional `DisplayPopup`, `Hyperlink`, `HighlightType`, `Description` (popup = 1).

## Addon Association
Required `SKU`, `AddonGroupName` (any value), `DisplayOrder`. Optional `AddOnSKU`, `IsDefault`.

## Pricing
Template `PriceTemplate`. Required `PricelistCode` (OMS > Price Lists codes), `SKU`, `RetailPrice` (0 to 99999, decimals). Optional `TierStartQuantity`, `SalePrice`, `TierPrice`, `SKUActivationDate`, `SKUExpirationDate` (`MM/DD/YYYY`, expiration on or after activation), `Custom1` to `Custom3`, `CostPrice`. A missing PricelistCode is logged as a failure (10.10.1.0). Price list rules: `commerce-promotions-and-pricing`.

## Inventory
Required `SKU`, `Quantity` (1 to 99999; zero and negative not stated), `WarehouseCode`. Optional `ReOrderLevel`. One row per SKU and warehouse. Stock rules: `commerce-inventory`.

## Category
Required `CategoryCode`, `CategoryName`, `CategoryTitle`, `DisplayOrderCategory`. Optional descriptions (HTML), `AdditionalDescription`, `CategoryBanner`, `CategoryImage`, `ImageAltText`, `HideCategoryMenu` (blank uses the system default since 10.12.1.0).

## Catalog Category Association
Required `CategoryCode`, `DisplayOrder`, `Action` (Add creates or updates; Delete removes the association). Optional `ParentCode` (path with `/`, up to 100 characters, blank is root). Process parents before children.

## Category Association (SKU to category)
Required `CategoryCode`, `SKU` (exists in PIM), `IsActive`, `DisplayOrder`. No delete action.

## Zip Code
All required: CountryCode, CountryFIPS, CityName, CityType, StateCode, StateFIPS, Zip, ZipType, Latitude, Longitude, MSACode, TimeZone, UTC, DST.

## Customers
Required `Username`, `FirstName`, `LastName`, `Email`, `PhoneNumber`, `EmailOptIn`, `SMSOptIn`, `IsActive`. Optional `ExternalId`, `CreatedDate`, `ProfileName`, `AccountCode`, `DepartmentName`, `RoleName` (User, Administrator, Manager; required when AccountCode is given), `CP Roles`, `SalesRepUsername`, `PerOrderLimit`, `PerOrderAnnualLimit`, `BillingAccountNumber`, `EnableUserShippingAddressSuggestion`, `EnablePowerBIReportOnWebStore`, `Custom1` to `Custom5`. Username rules changed in 10.13.1.0 (email-format check removed, new username rules, failing rows rejected); unsafe script content in usernames is blocked (10.14.0.0). The flag `RestrictCentralizedLogin_Store`: value 1 as before, 11 merges store associations without duplicating; one file cannot mix 1 and 11 (10.12.0.0).

## Customer Address
Username must exist. One row per address, unique `DisplayName`. Required Username, DisplayName, CompanyName, FirstName, LastName, Address1, CountryName (associated with the store), StateName, CityName, PostalCode, PhoneNumber, IsDefaultBilling, IsDefaultShipping, IsActive. Optional Address2, ExternalID.

## Accounts
Required `AccountName` (100), `AccountCode`, `CatalogCode` (exists), address fields (the template column for company is spelled `ComanyName`), `IsDefaultBilling`, `IsDefaultShipping` (both 1 for a new account). Optional `ParentAccountCode`, `ExternalID`, `Address2`.

## SEO Details
Settings mode: `ImportType` (Product or Category), `Code` (SKU or category code), `SEOUrl` (no store URL, no leading slash, unique across SEO entities), `IsActive`; optional MetaInformation, SEOTitle, description, keywords, `CanonicalURL`, `RobotTag` (INDEX_FOLLOW, NOINDEX_FOLLOW, INDEX_NOFOLLOW, NOINDEX_NOFOLLOW). Redirect mode: `IsRedirects` = 1, `RedirectFrom`, `RedirectTo`, `Enable Redirection` = 1. See `commerce-search-seo`.

## Brands
Required `Brand Code`, `IsActive`, `SEOFriendlyPageName` (unique, no slash). Optional BrandDescription (300), SEO description (300), SEOTitle (200), URLKey (200), BrandLogo, `Custom1` to `Custom5`. Descriptions with script, style or event-handler markup can be blocked by the web application firewall and fail the import or redirect to sign-in: use plain text.

## Vouchers
Required `StoreCode`, `VoucherName` (100), `VoucherAmount` (0.01 to 99999), `RemainingAmount` (equals VoucherAmount), `RestrictVoucherToCustomer`, `IsActive`. Optional `VoucherNumber` (10 alphanumeric, generated if blank), `Username` (required when restricted). See `commerce-promotions-and-pricing`.

## Synonyms
Required `Catalog Code`, `SynonymCode`. Optional `RenameSynonymCode`, `OriginalTerm` and `ReplacedBy` (pipe separated, up to 20 values of 100 characters), `IsBidirectional` (required on create).

## Sales Reps
Required Store Code (or all stores), User Name (email, 100), External ID/Code (numeric), First Name, Last Name; Email Address column added 10.13.1.0. Optional Phone Number. Cannot clear fields by import.

## Promotions
Required for new: `PromoCode` (200), `Name`, `StartDate`, `EndDate`, `DisplayOrder` (1 to 999), `Store` (code or All stores), `Profile` (code or All Profiles), `IsCouponRequired`; with a coupon: `IsAllowedWithOtherCoupons`, `PromotionalMessage` (300 or 150: the KB differs), `CouponCode` (20), `AvailableQuantity` (1 to 9999). Optional Description, Catalog, Category, Shipping, Brand, ProductsToDiscount, RequiredProducts (one SKU each), DiscountAmount, MinimumOrderAmount, MinimumQuantity. Cannot change after creation: Store Code, Promotion Code, Coupon Code, Requires A Coupon, Is Allowed With Other Coupons. Required fields vary by discount type (Brand, Catalog, Categories need minimum quantity, minimum order amount and the target; Order needs minimum order amount; Products needs minimum quantity, minimum order amount, product to discount; X if Y needs minimum quantity, product to discount, required product, product quantity).
