# Babyglee: landing page

Kids' sneakers sold on a three-step landing page, built for phones (visitors come from Facebook ads in Bangladesh). Everything is in English; prices are in taka (৳) with a US$ line.

| Step | File | What happens |
|---|---|---|
| 1 | `index.html` | Hero, five products (colour, photo gallery, sizes EU 21–36, add several to the cart), why sneakers for kids, why Babyglee, sole details, size finder, customer reviews, how ordering works, FAQ |
| 2 | `checkout.html` | Edit the cart, name, +88 mobile number, district, address, Cash on Delivery, place order |
| 3 | `thank-you.html` | Order confirmation; the `purchase` event fires here once |

Plus `shipping-returns.html`, `privacy.html`, `terms.html`.

## How it is built

- Pages are generated: edit `tools/build.py`, then run `python3 tools/build.py`. Do not hand-edit the generated `.html` files.
- `assets/main.js` (behaviour), `assets/style.css` (design), `assets/tracking.js` (GTM data layer, see `docs/gtm-tracking.md`).
- Backend: PHP 7.4+/8 + MySQL on cPanel hosting: `api/` (orders, live data, incomplete orders, optional Meta Conversions API) and `admin/` (orders, status, invoices, stickers, ads/UTM, stock, staff logins, reviews, photo gallery). Setup: `docs/backend-setup.md`.
- Without the backend (for example GitHub Pages) the site still works as a demo: orders are kept only in the visitor's browser and a demo notice is shown.

## Content you need to supply

- **Customer reviews:** Admin → Reviews (text or a screenshot of a real review). The section stays hidden until you add one. No reviews or statistics are made up.
- **More product photos:** Admin → Products → a product → *More photos*.
- Placeholders to confirm: price ৳1,290 (list ৳1,800), US$15, delivery ৳80 inside / ৳130 outside Dhaka, WhatsApp number (Admin → Settings).

## Rules

See `CLAUDE.md`: record every change below, back up before changing, mobile first, never commit `api/config.php`.

## Changelog

### 2026-11-15: Size finder, menu, hero and checkout bar
- Size recommendations now follow the live product guide: insole length = foot length + 1 cm (a 15 cm foot gives EU 26). The size table shows foot length, insole length and age for EU 21–36 from that chart; a "wide feet or thick socks" option moves one size up.
- Size guide is now a full-width "Find the right size" button on every product card, above the EU sizes. The sheet has 3 measuring steps, a centimetre field, the suggested size and "Select EU xx". The same finder is in the Size guide section.
- Mobile menu fixed: the panel is now full height (the header blur made the fixed panel only as tall as the header); a dark backdrop shows, and tapping outside closes it.
- Hero is compact on phones: headline, shoes, price and the two buttons fit the first screen (also at 360x640); the intro paragraph and badge are hidden there.
- Persistent bottom bar "Checkout · ৳1,290" (total follows the cart) with a small cart button for the cart sheet; it replaces the floating bag icon. WhatsApp stays on the right above it.
- Tests: 43 new (size logic against every chart row, hero, menu, bar) + 35 demo + 52 backend + 12 dataLayer pass.
- Backup before this change: `backups/site-2026-11-15-before-size-menu-hero.zip`.
- Files: `tools/build.py`, `assets/main.js`, `assets/style.css`, regenerated `index.html`.

### 2026-11-15: Complete dataLayer for GTM / Meta (server-side GTM)
- Every e-commerce event now carries `event_id`, `event_time`, `event_source_url`, `external_id`, `fbp`, `fbc`, UTMs/click IDs and a ready-made `meta_custom_data` (content_ids = SKUs, contents, num_items, value, BDT).
- New `generate_lead` event (incomplete order) when a valid mobile number is typed in checkout; carries the hashed customer data and cart. Works with or without the backend.
- `_fbp` is created by the site when the Pixel has not made it yet; `_fbc` keeps its case.
- Admin → Settings: the Meta Conversions API box now says to leave it empty when server-side GTM sends the events.
- New `docs/meta-tracking.md` (events, fields, what the server container adds, EMQ checklist, how to test); `docs/gtm-tracking.md` updated.
- Tests: 12 new dataLayer checks (hashing, identifiers, custom_data, lead, purchase) + the earlier 32 + 49 pass.
- Backup before this change: `backups/site-2026-11-15-before-meta-tracking.zip`.
- Files: `assets/tracking.js`, `assets/main.js`, `admin/index.php`, `docs/`.

### 2026-11-15: Mobile polish (flag, floating cart, receipt, footer)
- Bangladesh flag icon replaces the "BD" badge (header country button, country menu, phone and country fields).
- WhatsApp button moved to the right; a floating cart button sits above it (shown when the cart has items). Tapping it, or the bag in the header, opens a cart sheet with names, sizes, quantities, edit/remove, total and Checkout. The old bottom cart bar is removed.
- Thank-you page redesigned for phones: stacked receipt (items with quantity on the right, delivery address, amount to pay).
- Footer made shorter on phones: brand row, two-column links, two-column contact details.
- Backup before this change: `backups/site-2026-11-15-before-mobile-polish.zip`.
- Files: `tools/build.py`, `assets/main.js`, `assets/style.css`, regenerated `.html`. Tests: 32 (demo) + 49 (backend) pass.

### 2026-11-15: New landing-page site (this repository)
- Rebuilt the earlier store site as a three-step landing page: choose products and sizes on page 1 (several products in one cart, sticky cart bar), checkout on page 2 (Cash on Delivery), thank-you on page 3.
- Page 1 content: hero with ৳ and US$ price, trust strip, product cards with photo gallery and size chips, size guide sheet, why sneakers for kids, why Babyglee, sole anatomy with hotspots, size finder, reviews section (hidden until reviews exist), 3-step ordering, FAQ.
- Backend adapted (schema v6): product photo gallery (`products.images`), reviews table and Admin → Reviews page (text or screenshot), `assets/reviews.js` served from the database, backup JSON includes reviews, products seeded with the landing-page URL.
- Tracking: `view_item_list`, `select_item`, `add_to_cart`, `view_cart`, `begin_checkout` (page 2), `purchase` on the thank-you page (once, with `event_id`, hashed customer data).
- Tested with Playwright: 32 checks in demo mode and 49 against the PHP backend (multi-product order, admin, reviews, gallery, stock, incomplete orders), no overflow at 1360/820/390/360px.
- Backup of the previous store site: `backups/babyglee-store-site-2026-11-15-source.zip`.
- Files: everything (new repository). Removed: store pages (shop, product, cart), the five separate ad pages, About/Contact pages.
