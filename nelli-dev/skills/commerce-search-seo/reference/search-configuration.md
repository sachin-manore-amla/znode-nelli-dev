# Search configuration
What this answers: every search setting, its path, defaults, limits and publish needs.
Sources: KB articles listed in the skill (read 2026-11-23). Confidence 85 unless marked.

## Indexes
- **PIM index** (Marketing > Site Search > Manage PIM Indexes): history per published catalog, two indexes each (Production URL, Preview URL), edit and delete icons for index settings. Buttons: **Create Index**, **Create Schedule**, Add new (Add Search Index Settings).
- Global index setting **All**: editable, not deletable. Ngram controller default fields Product Name and SKU; Min Gram 3, Max Gram 20; character filter replaces tilde, underscore, hyphen, parentheses, period, asterisk, colon, plus, semicolon, ampersand.
- Catalog-specific index settings: select catalog; Ngram Controller (fields with Is Used in Search = TRUE); Min and Max Gram whole numbers 1 to 99 ("A value between 1 and 99 is allowed"); Character Filter mappings (case-sensitive; mapping to empty string allowed, from empty not; some characters need Unicode such as  ). **Save** stores, **Publish** stores and creates the index. Edit: catalog selection disabled. Delete (Yes to confirm) reverts the catalog to the All setting.
- Analyzer (Elasticsearch Configuration Used During Indexing): Standard analyzer on text fields; character filter removes underscores, dashes, hyphens, minus; tokenizer; token filters in order Lowercase, Synonyms, Stopwords, Ngram (Product Name, SKU, Brand), Shingle. Ngram length stated there as 1 to 40 (conflicts with the PIM Index article; check the screen).
- **CMS content index** (Marketing > Site search): choose Store; **Create Index** (production and preview); optional index name (changing it creates a new index); **Enable CMS Based Search** in Stores generates indexes automatically on CMS and Blog/News publish; results show Pages and Products tabs.
- Index status values: not described.

## Search profile (Marketing > Site Search > Search Profiles)
- Add New: unique name, catalog; Delete per row or bulk via Tools. Mark one **Default**; one profile per catalog is active; applies to the stores associated with it.
- Deleting only the profile leaves the index; deleting with published data publishes the system profile.
- Three parts: searchable fields (Boost Score 1 to 999, applied at query time), relevance ranking (Price, Rating, Total Reviews), query properties.
- Query type Multi-Match: **Best** = all keywords in one field; **Cross** = across fields. Operator **AND** or **OR**. Autocorrect max 2 characters, not with Cross.
- Behaviour examples (P1 "Belkin 12-Outlet Surge Protector" SKU "578-0000"; P2 "DeWalt 3-Tool Combo Kit" SKU "Z-12345"): "Belkin 578": Cross+AND P1, Best+AND none; "Bel Z-12": Cross+AND none, Cross+OR P1 and P2, Best+AND P1; "Belkin 79": only OR returns P1; "Be": nothing.
- Admin can preview results in the admin application.

## Facets, triggers
- Facets: Edit Search Profile > Facets tab > Associate Facets > select > save > **publish the profile**. Order by attribute Display Order, tie falls back to database order. Facet types and attribute requirements not in that article.
- Triggers: Edit Search Profile > Triggers: User Profiles (multi-select), Keywords (optional); Add New, Edit, Delete (confirmation), Save. (The article is for 9.8; treat as 70.)

## Synonyms, boost, redirects
- Synonyms: select catalog > Add New; original term and replaced-by term(s); "Bi-directional" checkbox (default); mandatory fields marked *; Publish Synonyms. Failed token-filter update: index creation does not start, old synonyms stay.
- Boost & Bury: catalog; Add New; Rule Name (unique), Start Date, End Date, Boost Value, Item Values (keywords), **Apply To All Search For The Catalog**, operator ANY (OR) or ALL (AND), Pause and Restart. Message: "Boost Value between 1.01 and 999 or 0 and 0.99 is required". Inputs: integers (not 1) or decimals up to two places; test values, ranking also depends on other factors.
- Keyword Redirects: catalog > Add New > Keywords, URL > Save > test in the storefront search bar.

## Did You Mean
Path: Manage PIM Indexes > index > PIM Index Settings > Search Behavior. Enable (off by default), Maximum Suggestions (up to 5), DYM attributes (Product Name, SKU, Brand with Use In Search = Yes; align with the profile). Rebuild fully after any change. Suggestions come from indexing; frequently used ones are cached. Tested on about 11,000 products: index about 3 percent larger, publish about 1 minute longer, higher indexing CPU.

## Search Settings (Marketing > Search Settings)
Scope All Stores (default) or store override. Enable Voice Search (microphone icon); Enable Barcode Scanning & Search (needs UPC or QR data in products); Enable CMS Search; Enable Hydrated Search (My Searches, Popular Products, Popular Brands, Popular Searches, Popular Categories; each up to 10, default 5; scheduler one-time or recurring Cron; data from per-store orders); Enable Enhanced Typeahead Search (Search Suggestions, Category Facets up to 10 each; Product Recommendations grid of 3, 6 or 9). Toggle defaults not stated. Whether saving needs a reindex: not stated.
Typeahead (Stores > store > Search Settings per the Typeahead article): at least 3 characters; suggestions show names, images, categories.

## Ranking
Okapi BM25: term frequency (diminishing returns), inverse document frequency (rarer words weigh more), document length normalization (short focused titles can win). Examples: "Blue Oxford Shirt" outranks long descriptions for "Blue Shirt". Boost logic is in Boost and Bury; "How Search Results are Sorted" not read.

## Not documented
Index status values, trigger types, redirect matching rules, search API routes, sitemap, whether Search Settings saves need reindex.
