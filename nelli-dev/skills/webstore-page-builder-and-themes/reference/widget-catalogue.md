# Widget catalogue

What this answers: every widget the base Page Builder registers, its group, editable attributes, data source and empty-state message.
Confidence: attribute names from the KB "Page Builder - UI Widgets / Znode Widgets / Layout Widgets" (80) cross-checked with the field keys in the widget config files of the Webstore source (90). Messages are KB text.

## Layout widgets (group Layout)

| Widget (key) | Purpose | Attributes |
|---|---|---|
| Container (`Container`, formerly Flex) | holds other widgets (slot) for grid and flex layouts | layout, flex properties, alignment, max width, height, rigid view, background image, margin, padding, border (sides, width, colour, radius, style) |
| Column (`Column`) | multi-column layout | distribution, columns, gap, margin |
| Vertical Space (`VerticalSpacing`) | space between components | size |

## UI widgets (group UI Widgets)

| Widget | Attributes |
|---|---|
| Text | text, size (small, medium), weight (normal, semibold, bold, extrabold), align, colour (default, muted), padding |
| Heading | text, optional ID for anchor links, size (3XL to XS), HTML level H1 to H6, align, background and text colour, border, margin, padding |
| Button Group | align, direction (horizontal, vertical), padding, margin, vertical alignment (10.8.1.0); each button: label, href (URL or `#anchor`), target (same or new tab), style (Primary, Secondary); several buttons per group |
| Text Image | padding, margin, heading, description, button (label, href, target, style), layout order (text first or image first), image ratio (small, large), image from Media Explorer with alt text |
| Dynamic Widget | HTML, CSS and JavaScript through the Open Dynamic Widget pop-up (gear icon) |
| Rich Text Widget | formatted text through the Open Rich Text Widget pop-up |

## Znode widgets (group Znode Widgets)

| Widget (key) | Data source | Attributes | Empty-state message |
|---|---|---|---|
| Banner Slider (`BannerSlider`) | banner slider from CMS > Banner Sliders (Select Banner in the gear pop-up) | scroll axis, thumbnails, arrows, start from selected item, infinite loop, interval (ms), indicators, auto play, transition time (ms), swipe scroll tolerance, pagination, stop on hover, swipeable, keyboard arrows, emulate touch, auto focus | "The Banner Slider widget has no content. Configure the widget by selecting the settings icon in the toolbar. If the data is already configured, publish the page to reflect the changes." |
| Offer Banner (`OfferBanner`) | banner slider (Select Slider) | card space, slides per view, navigation, indicators, grid | similar message for Offer Banner |
| Categories Carousel (`CategoriesCarousel`) | categories associated in the pop-up (Associate Category, search, filters, system views) | card space, max cards per view, navigation, indicators, grid | similar |
| Products Carousel (`ProductsCarousel`) | products associated in the pop-up | same carousel attributes | similar |
| Brands Carousel (`BrandsCarousel`) | brands associated in the pop-up | Hide Brand Names, plus carousel attributes | similar |
| Ad Space (`AdSpace`) | content container "Ad Space" (CMS > Containers) | none in the editor | "Please check if the Ad Space container is configured. If it is already configured, publish the page to reflect the changes." |
| Homepage Promo (`HomePagePromo`) | content container "Homepage Promo" | none | "Please check if the Homepage Promo container is configured. ..." |
| Image (`Image`) | Media Explorer | Select Image, Alt, Link URL, Target (same or new tab), Layout (Fixed, Responsive, Full Width), Width, Height, Alignment, Border Radius | "No image has been added to this widget yet. Please use the "Select Image" attribute to upload an image." |
| Video (`Video`) | Media Explorer | Select Video, Video Control, Auto Play | "No Video has been added to this widget yet. ..." |
| Newsletter (`NewsLetter`) | built-in subscription | Label, Placeholder, button text, align, padding, margin (padding added 10.8.1.0) | form shown with defaults |
| Link Panel (`LinkPanel`) | links entered in the gear pop-up per locale (Icon, Title, URL, Display Order, Open in New Tab) | orientation (vertical, horizontal), custom class | "The Link Panel widget has no content. ..." |
| Form Widget (`FormWidget`) | forms from CMS > Manage Forms | Select Form, Form Title, Action on Form Submission (Text Message or Redirect URL), Text Message, Redirect URL, Submit label, Notification Email Address, Notification Email Template | "The Form Widget has no content. ..." |
| Content Block (`ContentBlock`) | content block records; available in the content block editor | none documented | not documented |
| Ticker (`Ticker`) | home page ticker container; header editor only | none | header configuration message |

Other keys present in the source but not in the panel: `Header`, `Footer` (header and footer editors), page widgets for the fixed pages, `TextEditor` (config exists, not registered), `Card`, `Hero`, `Logo` (folders exist, registration commented out).

## How the data reaches the widget

Admin stores the selection in a widget record (key and code). On the server the Webstore asks the API for that data per store, locale and mapping (portal or content page) and passes it to the widget as `response.data`. After changing the Admin data, publish the page so the widget shows it; Banner Slider and Ad Space and Homepage Promo changes also raise their own cache events.

## Multi-locale per widget

See `multi-locale.md`.

## Adding your own widgets

They appear in the panel only after developers register them and map them to a group (`webstore-customization`). Their attributes edit in the right panel; the Admin gear pop-ups exist only for the built-in data widgets.
