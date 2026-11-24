# Product reviews and ratings
What this answers: how reviews are moderated, edited, shown and used by search; what is not documented.
Sources: KB Managing Product Reviews, Editing a Product Review, Configuring A Search Profile, Znode Storefront Caching Architecture and Performance Guide (read 2026-11-23). Confidence 85 unless marked.

## Admin
- **Marketing > Product Reviews**: edit or remove customer reviews. The article names no other actions, filters or grid columns.
- Edit screen (Marketing > Product Reviews > Edit): Product Name (not editable), Headline, Comments, Username, User Location, Rating, Review Status, Created Date (not editable). Save or Save & Close. Status values not listed (Published and Pending are expected, unverified).

## Moderation (store level)
Manage Store > General tab > **Default Customer Review Status**:
- **Publish Immediately**: shows on the product detail page without approval.
- **Do Not Publish Require Moderator Approval**: stays off the page until approved.
Storefront shows a review only if published immediately or approved.

## Storefront
Reviews appear on the product detail page. A shopper submits from the product page. Pages for submitting or reading reviews, "Review History" in My Account and the write-review page: earlier notes exist; the articles read today do not describe them (unverified). "write-review" is a reserved SEO keyword.

## Search and caches
- Search profile relevance ranking can sort by **Rating** (average rating) or **Total Reviews** (number of reviews), ascending or descending.
- A review update triggers invalidation of the product pages named in the publish event (page structures); see `config-caching`.
- Elasticsearch indexing of review text is not documented.

## Customization
| Need | Notes |
|---|---|
| Custom star display | Read rating data on the server in a Webstore component; do not cache per-user data |
| Auto-approve trusted buyers | Not documented as a setting: custom logic needs an API call to change review status (route unverified) |
| Anti-spam | CAPTCHA pattern from the KB ReCaptcha article (not read), rate limiting in your BFF route |
| Review notification email | No review template in the default list; a custom email needs a template plus a trigger (event not documented) |

## Not documented (say "not documented")
Rating average formula; purchase verification; spam controls; bulk moderation; review events; API routes for reviews.
