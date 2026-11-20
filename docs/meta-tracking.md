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
| `external_id` | first-party visitor ID (random UUID, cookie `bg_uid` renewed on every visit, with a localStorage copy that restores it; browsers cap script-set cookies, Chrome at 400 days) | `external_id` (let the tag hash it) |
| `fbp`, `fbc` | Meta cookies `_fbp`, `_fbc` (never changed or lower-cased; `_fbc` is built from `fbclid` when the Pixel has not) | `fbp`, `fbc` |
| `utm_*`, `fbclid`, `gclid`… | campaign data | custom / GA4 |
| `meta_custom_data` | `content_type: product`, `content_ids` (SKUs, the one product ID format of this site, same as `item_id` and the server copies; a Meta catalogue must use the SKU as its Content ID), `contents` (id, quantity, item_price), `num_items`, `value`, `currency: BDT` | `custom_data` |
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

## GTM must match the website (the dataLayer alone sends nothing)

An event in the dataLayer reaches Meta or GA4 only when your GTM containers have a trigger for it (Custom Event with exactly these names) and the tag maps the fields. Check each of these in GTM Preview:

| Website event | Trigger name | Meta tag event | Notes |
|---|---|---|---|
| `page_data` | Custom Event `page_data` | PageView | `event_id` of this push is the shared PageView ID: use it in the Pixel tag **and** the server tag |
| `view_item` | `view_item` | ViewContent | fires for the first product on load |
| `view_item_list` | `view_item_list` | (GA4 only) | sent when the first product card shows |
| `add_to_cart` | `add_to_cart` | AddToCart | also fired by "+" inside the cart; only the pairs really added (limit 10 per size) |
| `begin_checkout` | `begin_checkout` | InitiateCheckout | |
| `generate_lead` | `generate_lead` | Lead | means "valid mobile number saved", not "abandoned" (see below) |
| `add_payment_info` | `add_payment_info` | AddPaymentInfo | sent when the customer taps Place order |
| `purchase` | `purchase` | Purchase | thank-you page, or the server copy below |
| `whatsapp_click` | `whatsapp_click` | Contact (optional) | has an `event_id` |

Fields: map `meta_custom_data` to Meta `custom_data`, `meta_user_data` to `user_data`, `event_id`, `event_time`, `event_source_url`, `fbp`, `fbc`. Leave `fbp`, `fbc`, IP and user agent **unhashed**; do not hash the already hashed `meta_user_data` values again.
**External ID:** every event has the plain visitor ID in `external_id`; events with customer data also have its SHA-256 in `meta_user_data.external_id`. They are the same value, so use one style in all tags: either let the tag hash the plain `external_id`, or send `meta_user_data.external_id` as is. Both give Meta the same hash.

## What the Lead event means

`generate_lead` is sent once per checkout visit, after the backend confirmed it saved the incomplete order (the first valid mobile number). It does not mean the customer abandoned: people who go on to buy also send it. Build "abandoned" audiences by excluding purchasers (Purchase within N days), and use the Admin → Incomplete list for follow-up calls. Later changes to the form update the saved record in Admin but do not send a second Lead.
If the save fails (network, server error) the site retries a few times with a growing pause and sends the Lead only after a successful save; in demo mode (no backend) it is sent immediately.

## Purchase: how it is made reliable

- The thank-you page builds the Purchase from the **accepted order** returned by the server (items, prices, shipping, total), not from today's catalogue or settings. `value` is what the customer pays (products + delivery, e.g. 1,350 inside Dhaka for one pair; prices are already after any discount), `shipping` is the delivery charge on its own, `order_total` is the same total. The server copies (Meta Conversions API, server GTM) send the same `value`, so a duplicate is merged with the same amount. Tracking (GTM, Pixel, GA4) starts only on babygleebd.com and its subdomains; localhost, staging, preview links and other domains stay off (add `?bggtm=1` to test on purpose).
- The order is marked as reported only after the event is in the dataLayer. If the customer leaves too early, the next visit of the thank-you page sends it. If hashing the customer data stalls, the Purchase is sent without it after 2.5 seconds; checkout itself never waits for tracking more than 2 seconds.
- **Demo orders** (no backend, e.g. GitHub Pages) send no Purchase, so they cannot pollute your data. To test the dataLayer in demo mode set `localStorage.bg_track_demo = '1'` in the browser console.
- **Server copy (Admin → Settings → Server GTM backup):** paste your server container's GA4 Measurement Protocol URL. The backend then sends a `purchase` from the saved order with the same `event_id` (`purchase_<orderId>`) and `transaction_id`, plus hashed customer data, `fbp`, `fbc`, `external_id`, IP (`ip_override`) and user agent. Modes: *Only orders confirmed from Incomplete* (default: these customers never see the thank-you page, so the browser sends nothing), *Every order* (backup for lost browser events; the two copies carry the same IDs and are counted once) or *Never*. The Meta Conversions API box in Settings does the same job directly; use it **or** your server container, not both.
- Your server container needs a GA4 client that accepts these requests and a Purchase tag/trigger on it. This path is built to the Measurement Protocol format but has not been tested against a real container: check it once in server GTM Preview and in Events Manager.

### What the server request contains for Meta

Google and Meta hash the phone number differently, so the request carries **both**, separately:

| For | Field | Phone example |
|---|---|---|
| Google (enhanced conversions) | `user_data.sha256_phone_number` | hash of `+8801712345678` |
| Meta | event parameter `meta_ph` | hash of `8801712345678` (digits with country code, no `+`) |

The other Meta fields are `meta_em` (lower-case email), `meta_fn`, `meta_ln` (lower-case, no punctuation), `meta_ct` (district), `meta_country` (`bd`) and `meta_external_id` (SHA-256 of the visitor ID), plus the unhashed `fbp`, `fbc` and `external_id`. In your server container, map `meta_*` to the Meta tag's user data (do not hash them again) and leave the Google fields for the Google tags. Check in server GTM Preview that the event data shows these keys.
`ip_override` is sent at the top level of the request (as the Measurement Protocol documents) and also as an event parameter; use whichever your container reads and confirm it in Preview. The customer's user agent is sent as the `user_agent` parameter and as the request's `User-Agent` header. The IP address and user agent are the customer's own (saved with the order), never hashed.
The user agent of an incomplete order is saved when the order is captured and carried into the order created from Admin → Incomplete, so recovered Purchases have it too.

### Retries (no conversion is lost to a short outage)

- The customer gets the order answer first; the server then delivers the Purchase, so a slow Meta or server container never delays the thank-you page.
- Each destination (Meta, server GTM) has its own status. A failed one is tried again after 1, 5, 15, 60 and 240 minutes (six tries in all); one that already succeeded is never sent again. The state is stored in the order, so a restart loses nothing.
- Retries run when an admin page is opened, when another order arrives, and, if you add the optional cron job, every few minutes. In cPanel → Cron Jobs run `curl -s "https://yourdomain.com/api/retry.php?key=YOUR_CRON_KEY" > /dev/null` every 5 minutes and put the same `cron_key` in `api/config.php`.
- The order page shows the delivery status; if it is *pending* or *failed* there is a "Try again now" button, and the dashboard warns about failed deliveries.
- Default mode sends only orders confirmed from Incomplete. Ordinary web orders get the server copy only if you choose *Every order*: do so if you want protection against a lost thank-you page. Both copies carry the same `event_id` and `transaction_id`, so GA4 and Meta count one purchase; confirm this once in Events Manager.
