# Meta (Facebook) tracking with Google Tag Manager

The website only loads **one** thing: your GTM container (Admin → Settings → GTM container ID; add the server-side loader URL if you have a custom domain).
Pixel, Conversions API, GA4 and Google Ads are all set up inside GTM (web container + server-side container). The website's job is to push a **complete dataLayer**, so every tag has what it needs.
The "Meta Conversions API from this server" box in Admin → Settings stays **empty** when server-side GTM sends the events (do not do both).

## Events, in order of the visitor's journey

| Visitor does | dataLayer event | Meta event (map in GTM) | event_id |
|---|---|---|---|
| Opens the page | `page_data`, `view_item_list`, `view_item` | PageView (Pixel), ViewContent | auto |
| Taps a size / product | `select_item` | (not sent to Meta) | auto |
| Adds to cart | `add_to_cart` | AddToCart | auto |
| Opens checkout (page 2) | `view_cart`, `begin_checkout` | InitiateCheckout | auto |
| Types a valid mobile number, does not finish | `generate_lead` (`lead_type: incomplete_checkout`) | Lead | `lead_<token>` |
| Delivery area chosen | `add_shipping_info` | (not sent to Meta) | auto |
| Submits the order | `add_payment_info` (Cash on Delivery) | AddPaymentInfo | auto |
| Thank-you page | `purchase` | Purchase | `purchase_<orderId>` |

Rules that keep numbers clean: the same `event_id` goes to the browser Pixel tag and the server tag (Meta de-duplicates on `event_name` + `event_id`); Purchase fires once per order; a reload of the thank-you page sends nothing.

## What every event carries (top level of the dataLayer push)

| Field | Meaning | Meta field |
|---|---|---|
| `event_id` | unique ID shared by browser and server tag | `event_id` |
| `event_time` | Unix seconds | `event_time` |
| `event_source_url` | page URL | `event_source_url` |
| `external_id` | first-party visitor ID (random UUID, cookie `bg_uid`, 400 days) | `external_id` (let the tag hash it) |
| `fbp`, `fbc` | Meta cookies `_fbp`, `_fbc` (never changed or lower-cased; `_fbc` is built from `fbclid` when the Pixel has not) | `fbp`, `fbc` |
| `utm_*`, `fbclid`, `gclid`… | campaign data | custom / GA4 |
| `meta_custom_data` | `content_type: product`, `content_ids` (SKUs), `contents` (id, quantity, item_price), `num_items`, `value`, `currency: BDT` | `custom_data` |
| `ecommerce` | the same data in GA4 format (`items`, `value`, `currency`, `transaction_id`, `shipping`) | GA4 |

On events where the customer's details are known (`generate_lead`, `add_shipping_info`, `add_payment_info`, `purchase`) there are two more objects, already normalised and **SHA-256 hashed** in the browser (no raw phone, name or email ever enters the dataLayer):

- `meta_user_data`: `ph` (880… digits, no +), `em`, `fn`, `ln`, `ct` (district), `country` (`bd`), `external_id` → Meta `user_data`
- `user_data`: GA4 / Google Ads enhanced-conversions format (`sha256_phone_number` as +880…, `sha256_email_address`, address first/last name, city, region, country)

`purchase` also has `transaction_id`, `order_total`, `ecommerce.shipping`, `order_source`, `payment_type: Cash on Delivery`, `shipping_tier`.
Product SKU = `item_id` = Meta `content_id` (`BSTD-01-GREY` …): use the same IDs in your Meta catalogue.

## What the server container adds by itself

Things a browser cannot send reliably: `client_ip_address` and `client_user_agent` come from the request that reaches your server container (the Meta Conversions API tag fills them; never hash them). IPv6 is fine. For the best result:

1. Put the server container on **your own subdomain** (for example `sgtm.yourdomain.com`) and load GTM from it (Admin → Settings → loader URL). Then `_fbp`/`_fbc` can be refreshed by the server as first-party cookies, which last longer than JavaScript cookies on iPhone Safari.
2. In the server container, send `external_id`, `fbp`, `fbc`, `event_source_url`, `action_source: website`, `event_id` and the customer fields to the Meta tag.
3. Keep the web Pixel tag and the server tag on the **same event name and event_id** so Meta counts one event.

## What improves Event Match Quality (EMQ)

Send as many of these as are known: `em`, `ph`, `fn`, `ln`, `ct`, `country`, `external_id`, `fbp`, `fbc`, IP, user agent. The site already has all of them for `purchase` and `generate_lead`. For ViewContent / AddToCart the visitor is anonymous, so there `external_id`, `fbp`, `fbc`, IP and user agent do the matching. A repeat visitor keeps the same `external_id`, so earlier anonymous events can match the later purchase.

## How to check

1. Add `?bgdebug=1` to any page URL: every dataLayer push is shown on the page.
2. GTM → Preview mode: click each event, check the fields above.
3. Meta Events Manager → Test events (use your test code in the server tag): the event must show **Browser + Server**, "Deduplicated", and a match-quality score.
4. After a real test order: Events Manager → the Purchase shows value in BDT and the content IDs.
