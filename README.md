# Babyglee: landing page

Kids' sneakers sold on a three-step landing page, built for phones (visitors come from Facebook ads in Bangladesh). Everything is in English; prices are in taka (৳) with a € international price line.

| Step | File | What happens |
|---|---|---|
| 1 | `index.html` | Hero, five products (colour, photo gallery, sizes EU 21–36, add several to the cart), why Babyglee® (benefits with the photo), size finder, customer reviews, how ordering works, FAQ |
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
- Placeholders to confirm: price ৳1,290 (list ৳1,800), €35, delivery ৳80 inside / ৳130 outside Dhaka, WhatsApp number (Admin → Settings).

## Rules

See `CLAUDE.md`: record every change below, back up before changing, mobile first, never commit `api/config.php`.

## Changelog

### 2026-11-17: International price €35, bKash info only, new product names, new Grey photo
- Backup of the live site before the changes: `backups/site-2026-11-17-before-euro-grey-update.zip`.
- **International price is now €35** (hero line and product cards show "€35"). The database field (`price_usd`) and the JSON key (`priceUsd`) keep their old names to avoid breaking anything; the admin label reads "International price (€)". Schema v9 sets it to 35 only for products still at an old default (15 or 30); a price you set yourself is kept.
- **Payment: bKash is information only, no card.** Where the site mentioned card payment (FAQ, order steps, checkout, Shipping & Returns, Terms) the card wording is removed. bKash merchant account 01974974973 (Payment option) is shown as information; the order itself is still recorded as Cash on Delivery.
- **Product names from the backend code:** schema v9 renames the five products by slug (`bounce-sky-blue`, `bounce-blue-beige`, `bounce-grey`, `bounce-navy-brown`, `bounce-black`) to "Sneaker – Multi Color", "Sneaker – Blue & Beige", "Sneaker – Charcoal Grey", "Sneaker – Dark Navy", "Sneaker – Black" (colour names without the prefix). Slugs, SKUs and photos stay, so GA4/Meta item IDs do not change. The migration runs once, on the first request after the deploy; names edited later in Admin → Products are kept. The fresh-install seed and the static fallback use the same names.
- **New photo for the Grey product (`img/grey.webp`):** the supplied photo with the grey studio background and floor shadows removed (transparent, like the other four photos, so the card colour shows through), cropped and resized to 900 px wide (60 KB).
- Partner logos: not added. They are not on the main babygleebd.com pages (checked `/`, `/shop`, `/shop/bangladesh`, `/welcome/Bangladesh`); the section appears as soon as the four logo files are placed in `img/partners/`.
- Tests: schema migration on a copy of an old database (names and colours renamed, 30 → 35, a custom price 40 kept, schema_version 9, fresh install seeds the new names) and a browser check at 360, 390 and 1280 px (title, "€35" in the hero and on the card, no console errors).
- Files: `tools/build.py` (generated pages and `assets/products.js`), `api/lib.php`, `admin/index.php`, `assets/main.js`, `assets/config.js`, `img/grey.webp`, `docs/backend-setup.md`, `README.md`.

### 2026-11-17: Tracking tidy-up (dataLayer only, no key renames)
- Backup of the live site before the changes: `backups/site-2026-11-17-before-datalayer-update.zip`.
- **`external_id`:** the visitor UUID lives in the first-party cookie `bg_uid`, renewed on every visit (asked for 730 days; Chrome caps script-set cookies at 400 days, Safari is shorter). A copy in localStorage restores the cookie when it expires or is cleared, so the value stays the same on every page and visit.
- **Purchase once per order:** the order id is stored in sessionStorage and localStorage (`bg_purchased`, last 50 orders) and is checked again in the same moment the event is pushed, so a reload, back/forward or a later visit to the thank-you page sends nothing. The event_id stays `purchase_<orderId>`.
- Checked, no change needed: `meta_user_data` on `purchase` already holds SHA-256 hashes of the phone (digits with country code, `8801700000000`), first name, last name, city, country and external_id (first name and city are lowercased and stripped of punctuation and spaces, as Meta specifies). Every other event's `event_id` is unique per event (tested over a browsing session).
- Not possible as asked: `begin_checkout` fires when the checkout page opens, before the visitor has typed anything, so it has no name, phone or city to hash. The first events that carry `meta_user_data` are `add_shipping_info`, `add_payment_info`, `generate_lead` and `purchase`.
- Decided by the owner: `ecommerce.value` stays the product price without delivery (1290); delivery stays in `ecommerce.shipping` (`order_total` is sent next to it).
- Files: `assets/tracking.js`, `assets/main.js`, `docs/gtm-tracking.md`, `docs/meta-tracking.md`, `README.md`.

### 2026-11-17: Copy update from the team's "Landing page" review document
- Backup of the live site before the changes: `backups/site-2026-11-17-before-copy-update.zip`.
- **Announcement bar:** "Available in Bangladesh · Designed for European markets · Cash on Delivery · 72-Hour Easy Exchanges" plus a tap-to-call number; on phones it shows "Available in Bangladesh" and the number. Nav: Why Babyglee®, Size Guide, Shop Now.
- **Hero:** new headline and text ("Designed for active, healthy feet development."), the "International brand" pill is gone, "(Cash on Delivery)" next to the price, chip "Soft cushioning". The four trust badges under the hero are removed; only the delivery line stays.
- **Delivery everywhere is now "2–3 days"** (no "working days"): delivery line, order steps, FAQ, Shipping & Returns, thank-you page, cart pop-up.
- **Products:** section text "Choose your size, fill your cart, and check out all at once."; seed/fallback names are now Multi Color, Blue & Beige, Charcoal Grey, Dark Navy, Black. The live names come from Admin → Products and must be renamed there.
- **"Why Babyglee®" and "The details that matter" are one section:** new headline and text, the sneaker photo with numbered points next to six benefits (Breathable Microfiber, Soft & Comfortable Cushioning, Easy Front-Lock Strap, Anti-Slip Rubber Sole, Zero Toxic Chemicals, European Design).
- **Size guide:** the insole length is shown in cm and inches (table and the size finder note).
- **Order steps** reworded ("Three-Step Order Process"); a line with the payment options (Cash on Delivery, bKash merchant 01974974973, card via WhatsApp). The checkout shows the same options as information; the order itself is still recorded as Cash on Delivery.
- **FAQ** ("Got Questions? We've Got Answers.") and the **Shipping & Returns, Privacy and Terms** pages use the content of the main babygleebd.com pages, adapted to this site where the main store text does not apply (no customer accounts, Bangladesh delivery in 2–3 days, 72-hour exchange, payment options, size advice = insole = foot + 1 cm).
- **Footer:** "Ready for Healthy Growing Feet?", new blurb ("available in Bangladesh"), columns Customer Care / Shop / Company / Reach Us, office hours 11 AM – 9 PM (BST).
- **New: "Added to your cart" pop-up** after every add to cart (product, size, cart total, Continue shopping / Checkout).
- **New: partner logos section** (ToguMogu, Shishu Poribohon, Prelegant Mall, Rokomari). It appears only for logo files placed in `img/partners/` (`togumogu`, `shishu-poribohon`, `prelegant-mall`, `rokomari`, as `.svg`, `.webp`, `.png` or `.jpg`); no logos are invented.
- Fixed: the `size_guide_open` event was swallowed by a comment in `assets/main.js` and never fired.
- Not done (needs the owner): customer reviews from Facebook (add real reviews in Admin → Reviews; none are copied or invented), the international price "35 Euro" (the site still shows US$30, see the open questions), a bKash/card payment choice that is saved on the order.
- Files: `tools/build.py`, `assets/main.js`, `assets/style.css`, generated pages and `assets/products.js`, `README.md`.

### 2026-11-17: Update on request when the hosting does not allow exec()
- The real hosting (LiteSpeed) switches PHP's `exec()` off, so the webhook answered 501 and could not start the update. `api/deploy.php` now writes a request file (`~/.babyglee-update-requested`) after a signed push to `main` and answers `{"ok":true,"queued":true}`; where `exec()` works it also starts the update at once (`started`).
- `tools/auto-update.sh --on-request` (cron job, every minute): stops immediately unless the request file exists (no GitHub contact otherwise), claims the file atomically, deploys, removes it; a failed attempt is kept and retried for up to 60 minutes (then dropped and logged); paused updates keep the file; a webhook arriving mid-update is not lost. Without the argument the script behaves as before.
- `docs/deploy.md` section 4 rewritten around this flow.
- Tests: 44 sandbox checks (the earlier 29 + 15 new: no flag = nothing, no GitHub contact, flag = update and removal, nothing new, paused, retry after failure, give-up after an hour, webhook with `exec` disabled leaves the file and deploys nothing itself, other branch and wrong signature leave no file) + deploy and IP suites. Not tested: a real cPanel cron job.
- Backup before this change: `backups/site-2026-11-17-before-flag-update.zip`.
- Files: `api/deploy.php`, `tools/auto-update.sh`, `docs/deploy.md`.

### 2026-11-17: Test of the automatic update (GitHub webhook)
- New harmless file `assets/version.txt`. After this is merged, it should appear at `/assets/version.txt` on the live site within seconds without any click in cPanel; that proves the webhook, `api/deploy.php`, `tools/auto-update.sh` and `tools/deploy.sh` work together on the real hosting. Nothing else changed.
- Backup before this change: `backups/site-2026-11-17-before-update-test.zip`.
- Files: `assets/version.txt`.

### 2026-11-16: Webhook is the recommended way to update (no per-minute cron)
- `docs/deploy.md` section 4 reordered: **A** the GitHub webhook (the server updates only when `main` changes, i.e. when you say "merge"; includes how to check Recent Deliveries and what 403 / 501 mean), **B** two clicks in cPanel Git Version Control, with an optional cron every 30–60 minutes as a safety net instead of every minute, and how to hold updates with `~/.babyglee-paused`. No code changed (`api/deploy.php` and `tools/auto-update.sh` were added earlier).
- Backup before this change: `backups/site-2026-11-16-before-webhook-docs.zip`.
- Files: `docs/deploy.md`.

### 2026-11-16: US$30, delivery time line, floating cart above WhatsApp
- International price is now **US$30** (hero, product cards, product data). Schema v8 updates existing products whose US price is still the old default 15 to 30; a price you changed yourself in Admin is kept.
- New full-width line under the four trust items on the home page: "Order today, delivered in **3–5 working days** across Bangladesh". FAQ ("How does delivery work?", "Where do you deliver?") and the Shipping & returns page now say 3–5 working days too.
- Cart on phones: the bottom bar is now only the wide **Checkout · ৳…** button; the cart button is the floating round icon above the WhatsApp button (and the bag in the header). Both floating buttons hide while the hero buttons are on screen, and are smaller on short phones. The checkout page still sends `view_cart` + `begin_checkout` for every visitor who reaches it; opening the cart sheet sends one more `view_cart`.
- Tests: 55 new (delivery line at 6 widths, US$30, button order and overlap, view_cart) + all earlier browser suites (35 + 12 + 43 + 65 + 31) + 34 and 52 backend + v7 to v8 migration check.
- Backup before this change: `backups/site-2026-11-16-before-price-delivery-cart.zip` (made without the `backups/` folder).
- Files: `tools/build.py`, `assets/main.js`, `assets/style.css`, `api/lib.php`, generated pages.

### 2026-11-16: Auto-update from GitHub, instant webhook, backups, rollback
- `tools/auto-update.sh` (cron, every minute): pulls `main` and deploys only when there is a newer commit; skips while paused or while another update runs; logs to `~/deploy.log`; a failed deploy is logged and retried on the next run.
- `api/deploy.php` (optional GitHub webhook, a few seconds): needs `deploy_secret` in `api/config.php`, verifies GitHub's HMAC-SHA256 signature, reacts only to a push to `main`, runs only the fixed update script after answering; 404 without a secret, 401 for a wrong or missing signature, 501 when `exec()` is off.
- `tools/deploy.sh`: one deploy at a time (lock), a backup of the live files before every deploy over an existing site (`~/deploy-backups`, newest 10, private), records the deployed commit; no duplicate cPanel PHP block when the new `.htaccess` already has it.
- `tools/rollback.sh`: restores the previous (or a named) backup, backs up the current files first, pauses automatic updates (`~/.babyglee-paused`).
- `docs/deploy.md` section 4 rewritten: chat → PR → "merge" → live; cron, webhook, backups and rollback.
- Tests: 29 checks in a sandbox with a fake GitHub (deploy, no-op run, backup contents and permissions, retention, rollback, pause and resume, two updates at once, failed deploy retried, signed webhook accepted, wrong, missing and mismatched signatures refused, other branch ignored, ping, GET, no secret) + 36 deploy + 11 IP checks. Not tested: a real cPanel account, GitHub webhook delivery, Cloudflare.
- Backup before this change: `backups/site-2026-11-16-before-auto-deploy.zip`. This and all later backups are made without the `backups/` folder (`git archive --format=zip -o backups/<name>.zip origin/main -- . ':(exclude)backups'`): before, each backup contained every earlier one and doubled in size, and the last one (142 MB) hit GitHub's 100 MB file limit. The older zips in the repository add up to about 140 MB and make the first clone slow; they can be moved out of the repository when you decide.
- Files: `tools/auto-update.sh` (new), `tools/rollback.sh` (new), `tools/deploy.sh`, `api/deploy.php` (new), `api/config.sample.php`, `docs/deploy.md`.

### 2026-11-16: Deploy keeps the cPanel PHP version block
- `tools/deploy.sh` no longer overwrites the cPanel-generated PHP handler block (`# php -- BEGIN/END cPanel-generated handler`, which holds "PHP 8.2 / ea-php82") when it replaces the web folder's `.htaccess`: the block is read first and appended to the new file (once, also after repeated deploys). Before, a deploy could drop the domain's PHP version setting.
- The first deploy also keeps a copy of the existing `.htaccess` (for example cPanel's Force HTTPS rule) as `.htaccess.before-deploy`; it is created once and never overwritten.
- `docs/deploy.md`: when the site is the account's main domain the Document Root is usually `public_html`; check the folder exists and save the path file; Cloudflare must be on Full / Full (strict) when cPanel's Force HTTPS Redirect is on.
- Tests: deploy simulation now has an existing cPanel handler block (36 checks: original .htaccess saved once, block kept once, site rules present, nothing duplicated on a second deploy, rsync and copy fallback).
- Backup before this change: `backups/site-2026-11-16-before-htaccess-preserve.zip`.
- Files: `tools/deploy.sh`, `docs/deploy.md`.

### 2026-11-16: Hosting deploy from GitHub, real visitor IP behind Cloudflare
- New `docs/deploy.md`: Cloudflare DNS/SSL, cPanel PHP and database, cPanel Git Version Control, auto-update by cron (merged changes go live within about 5 minutes), first-run checks.
- New `tools/deploy.sh` and `.cpanel.yml`: copy only the website files (pages, `assets/`, `img/`, `admin/`, `api/`, `.htaccess`) into the web folder named in `~/.babyglee-deploy-path`; `api/config.php` and everything in `uploads/` are never touched; tools, docs, README and backups are not published; it refuses the home folder, `/` and missing folders; rsync removes files deleted from the repository, with a plain-copy fallback when rsync is missing.
- Fix for sites behind Cloudflare: `client_ip()` now uses `CF-Connecting-IP`, but only when the request comes from a Cloudflare address. Before, every visitor looked like one of a few Cloudflare addresses, which would trip the per-address order and incomplete-order limits and send wrong IPs to Meta and server GTM.
- Tests: 26 deploy checks in a simulated cPanel account (rsync and fallback, protected files, refusals, repeat run) and 11 client-IP checks (IPv4/IPv6, range edges, spoofed header); live-backend suites still pass. Not tested: a real cPanel account, cPanel Git Version Control, Cloudflare.
- Backup before this change: `backups/site-2026-11-16-before-deploy-setup.zip`.
- Files: `tools/deploy.sh`, `.cpanel.yml`, `api/lib.php`, `docs/deploy.md`, `docs/backend-setup.md`.

### 2026-11-16: Delivery retries, Meta fields, user agent (second tracking review)
- Fixed my own regression: an inline comment had cut `order_id` and `content_type` (and the rest of that line) out of the Meta Conversions API `custom_data`. A test now checks them.
- Server GTM request: Meta-ready matching fields sent separately from the Google ones (`meta_ph` is the phone as digits `880...` without `+`, plus `meta_em`, `meta_fn`, `meta_ln`, `meta_ct`, `meta_country`, `meta_external_id`); `ip_override` is also at the top level of the request; the request's User-Agent header is the customer's.
- Incomplete orders now keep the customer's user agent (`leads.user_agent`), carried into the order created from Admin → Incomplete.
- Durable delivery: `api/dispatch.php` (moved out of `capi.php`) keeps a status per destination, retries failures after 1, 5, 15, 60 and 240 minutes (six tries), never resends what already succeeded, and runs after the order answer is sent (customers never wait for it). Retries run when an admin page opens, when an order arrives, and from the optional cron endpoint `api/retry.php?key=...` (`cron_key` in `api/config.php`). Order page: status and "Try again now"; dashboard warns about failed deliveries. Schema v7 (`orders.dispatch*`, `leads.user_agent`); a v6 database upgrades in place.
- Page leave: if `sendBeacon()` refuses the save (returns false) a keepalive request is sent instead.
- Checkout waits at most 1.2 s for tracking (both steps run together), not two 2 s waits in a row.
- Tests: 31 browser checks, 34 backend checks (mock Meta and server GTM that can fail or stall), v6 to v7 upgrade, plus 35 demo + 52 backend + 12 dataLayer + 43 size + 65 small-screen pass. Not tested: a real server GTM container, Meta delivery, real EMQ.
- Backup before this change: `backups/site-2026-11-16-before-delivery-retries.zip`.
- Files: `api/dispatch.php` (new), `api/retry.php` (new), `api/capi.php`, `api/order.php`, `api/lead.php`, `api/lib.php`, `api/config.sample.php`, `.htaccess`, `admin/index.php`, `assets/main.js`, `docs/`.

### 2026-11-16: Tracking reliability (from the tracking review)
- Incomplete orders: a save counts as done only after the backend answers ok; network errors and 5xx/408/429 are retried (2, 5, 15, 40 s); the page-leave save uses `sendBeacon`; the `generate_lead` event is sent after the first confirmed save.
- `view_item_list` now fires when the first product card shows (it could never fire on a 320x568 phone before).
- `_fbc` is replaced when a new ad click (different `fbclid`) arrives; case and format are kept. `page_data` now carries a shared `event_id` for PageView de-duplication; `whatsapp_click` has an `event_id` and identifiers.
- Purchase: built from the accepted order (items, prices, shipping, total returned by `api/order.php`); marked as reported only after it is pushed; demo orders send no Purchase (`localStorage.bg_track_demo = '1'` to test); checkout never waits more than 2 s for tracking.
- Server-side Purchase delivery: `dispatch_purchase()` for web orders and for orders confirmed from Admin → Incomplete (previously none). Optional server GTM Measurement Protocol URL and mode (recovered / every order / never) in Admin → Settings; Meta value is now the product value, as in the browser event; the order stores the visitor ID (`uid`) and GA client cookie.
- Cart: "+" inside the cart sends `add_to_cart`; adding beyond 10 pairs of a size reports only the pairs added (none at the limit, with a message); the shipping step also fires when the name is the last field completed.
- Admin: the username can be an email address.
- Docs: `docs/meta-tracking.md` (trigger/tag mapping, external ID, Lead meaning, Purchase reliability) and `docs/backend-setup.md`.
- Tests: 28 new browser checks, 18 new backend checks (mock Meta and server GTM receivers) + 35 demo + 52 backend + 12 dataLayer + 43 size + 65 small-screen pass. Not tested: a real GTM container, Meta delivery, real EMQ.
- Backup before this change: `backups/site-2026-11-16-before-tracking-reliability.zip`.
- Files: `assets/main.js`, `assets/tracking.js`, `api/capi.php`, `api/order.php`, `api/lead.php`, `api/lib.php`, `admin/index.php`, `docs/`.

### 2026-11-15: Small screens, short screens and landscape
- Hero: the background circle no longer covers the heading, price or note (it is sized to the picture area); on short and landscape screens the layout is tighter (landscape phones use two columns). The WhatsApp button hides while the hero buttons are on screen and returns when you scroll.
- Checkout at 320px (and down to 300px): the form and the expanded "Order summary" no longer widen the page (grid columns and inputs can shrink; summary lines stack on very small phones).
- Header at 320px and below: logo, country button, bag and menu all fit; the bag and menu buttons keep their full size (below 315px only the flag and arrow show for the country).
- Size popup: reopening it keeps the typed measurement and shows "Select EU xx" again.
- Size guide: nothing is suggested outside the chart. A foot over 21 cm (insole over 22 cm), a wide-foot choice at EU 36, or a foot under 12 cm shows "No matching size" with a message to contact us, and no Select button.
- Tests: 65 new small-screen checks (10 screen sizes, checkout at 8 widths, popup and limits) + 43 size + 35 demo + 52 backend + 12 dataLayer pass.
- Backup before this change: `backups/site-2026-11-15-before-small-screen-fixes.zip`.
- Files: `assets/main.js`, `assets/style.css`.

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
