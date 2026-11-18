/* Babyglee tracking layer: GTM + GA4 e-commerce dataLayer + customer-matching data.
 *
 * Everything (GA4, Meta Pixel + Conversions API, Google Ads, Microsoft Clarity) is meant to live in Google Tag Manager.
 * This file only (1) loads GTM, (2) pushes clean e-commerce events to window.dataLayer, and
 * (3) prepares first-party data for event quality: hashed customer data, fbp/fbc, click IDs, UTMs, event_id.
 * Docs: docs/gtm-tracking.md
 */
(function () {
  'use strict';
  var BG = window.BG || {};
  window.dataLayer = window.dataLayer || [];
  var CUR = 'BDT';

  /* The GTM loader is further down (after the helpers), because on the thank-you page the customer data must be in the dataLayer before GTM starts. */

  /* ---------- small helpers ---------- */
  function getCookie(n) { var m = document.cookie.match(new RegExp('(?:^|; )' + n.replace(/[.$?*|{}()[\]\\/+^]/g, '\\$&') + '=([^;]*)')); return m ? decodeURIComponent(m[1]) : ''; }
  function setCookie(n, v, days) {
    try { document.cookie = n + '=' + encodeURIComponent(v) + ';max-age=' + Math.round(days * 86400) + ';path=/;SameSite=Lax' + (location.protocol === 'https:' ? ';Secure' : ''); } catch (e) {}
  }
  function lsGet(k) { try { return JSON.parse(localStorage.getItem(k)); } catch (e) { return null; } }
  function lsSet(k, v) { try { localStorage.setItem(k, JSON.stringify(v)); } catch (e) {} }
  function rand() { return Math.random().toString(36).slice(2, 10); }
  function uuid() { try { return crypto.randomUUID(); } catch (e) { return rand() + rand() + rand(); } }
  function eventId(prefix) { return prefix + '_' + Date.now().toString(36) + '_' + rand(); }

  /* ---------- visitor id (first-party, for Meta external_id) ---------- */
  /* One UUID per browser: first-party cookie (renewed on every visit; browsers cap script-set cookies, Chrome at 400 days, Safari shorter) with a copy in localStorage that restores the cookie when it expires or is cleared, so the value stays the same on every page and visit. */
  var uid = getCookie('bg_uid');
  if (!uid) { try { uid = localStorage.getItem('bg_uid') || ''; } catch (e) {} }
  if (!uid) { uid = uuid(); }
  setCookie('bg_uid', uid, 730);
  try { localStorage.setItem('bg_uid', uid); } catch (e) {}
  /* _fbp: Meta's browser ID (fb.1.<time ms>.<random>). Created here only if the Pixel has not made it yet, so server-side events always carry it. */
  if (!getCookie('_fbp')) setCookie('_fbp', 'fb.1.' + Date.now() + '.' + Math.floor(Math.random() * 1e10), 90);

  /* ---------- attribution: UTMs + click IDs (first touch kept, last touch updated) ---------- */
  /* What the ad link carries: names (campaign, ad set, ad), numbers (utm_id = campaign id, adset_id, ad_id), where the ad was shown (placement, site_source) and click ids. See Admin > Ads for the link to paste in Meta. */
  var KEYS = ['utm_source', 'utm_medium', 'utm_campaign', 'utm_content', 'utm_term', 'utm_id', 'adset_id', 'ad_id', 'placement', 'site_source', 'fbclid', 'gclid', 'gbraid', 'wbraid', 'ttclid'];
  var qs = new URLSearchParams(location.search), seen = {};
  KEYS.forEach(function (k) { var v = qs.get(k); if (v) seen[k] = v.slice(0, 300); });
  var attr = lsGet('bg_attr') || {};
  /* The ad details of a visitor count for 30 days: after that an order is no longer credited to an old ad click. */
  (function () { var ms = 30 * 864e5, now = Date.now(), cut = false; ['first', 'last'].forEach(function (k) { if (attr[k] && attr[k].ts && now - attr[k].ts > ms) { delete attr[k]; cut = true; } }); if (cut) lsSet('bg_attr', attr); })();
  if (Object.keys(seen).length) {
    seen.landing_page = location.pathname; seen.ts = Date.now();
    if (!attr.first) attr.first = seen;
    attr.last = seen; lsSet('bg_attr', attr);
  }
  /* _fbc from fbclid when the Pixel has not set it yet (format: fb.1.<timestamp ms>.<fbclid>) */
  /* A new ad click (a different fbclid) replaces the old _fbc, so the order is credited to the latest click. Case of the fbclid is kept exactly as Meta sent it. */
  if (seen.fbclid) {
    var curFbc = getCookie('_fbc');
    if (!curFbc || curFbc.split('.').slice(3).join('.') !== seen.fbclid) setCookie('_fbc', 'fb.1.' + Date.now() + '.' + seen.fbclid, 90);
  }

  /* ---------- SHA-256 (hex) with a pure-JS fallback for non-secure contexts ---------- */
  var SHA_K = null, SHA_H = null;
  function shaInit() {
    if (SHA_K) return;
    SHA_K = []; SHA_H = [];
    for (var n = 2, c = 0; c < 64; n++) {
      var prime = true;
      for (var d = 2; d * d <= n; d++) if (n % d === 0) { prime = false; break; }
      if (!prime) continue;
      if (c < 8) SHA_H[c] = (Math.pow(n, 0.5) * 4294967296) | 0;
      SHA_K[c++] = (Math.pow(n, 1 / 3) * 4294967296) | 0;
    }
  }
  /* Standard SHA-256 over a binary string; used only when crypto.subtle is unavailable (e.g. plain http). */
  function sha256Fallback(bin) {
    shaInit();
    var rr = function (v, n) { return (v >>> n) | (v << (32 - n)); };
    var h = SHA_H.slice(), k = SHA_K, words = [], i, j, bitLen = bin.length * 8;
    bin += '\x80'; while (bin.length % 64 !== 56) bin += '\x00';
    for (i = 0; i < bin.length; i++) { j = bin.charCodeAt(i); if (j > 255) return ''; words[i >> 2] |= j << ((3 - (i % 4)) * 8); }
    words.push((bitLen / 4294967296) | 0); words.push(bitLen | 0);
    for (j = 0; j < words.length; j += 16) {
      var w = words.slice(j, j + 16), a = h[0], b = h[1], c = h[2], d = h[3], e = h[4], f = h[5], g = h[6], hh = h[7];
      for (i = 0; i < 64; i++) {
        if (i >= 16) {
          var w15 = w[i - 15], w2 = w[i - 2];
          w[i] = (w[i - 16] + (rr(w15, 7) ^ rr(w15, 18) ^ (w15 >>> 3)) + w[i - 7] + (rr(w2, 17) ^ rr(w2, 19) ^ (w2 >>> 10))) | 0;
        }
        var t1 = (hh + (rr(e, 6) ^ rr(e, 11) ^ rr(e, 25)) + ((e & f) ^ (~e & g)) + k[i] + w[i]) | 0;
        var t2 = ((rr(a, 2) ^ rr(a, 13) ^ rr(a, 22)) + ((a & b) ^ (a & c) ^ (b & c))) | 0;
        hh = g; g = f; f = e; e = (d + t1) | 0; d = c; c = b; b = a; a = (t1 + t2) | 0;
      }
      h[0] = (h[0] + a) | 0; h[1] = (h[1] + b) | 0; h[2] = (h[2] + c) | 0; h[3] = (h[3] + d) | 0;
      h[4] = (h[4] + e) | 0; h[5] = (h[5] + f) | 0; h[6] = (h[6] + g) | 0; h[7] = (h[7] + hh) | 0;
    }
    return h.map(function (x) { return ('00000000' + (x >>> 0).toString(16)).slice(-8); }).join('');
  }
  function sha256(str) {
    str = String(str == null ? '' : str);
    if (!str) return Promise.resolve('');
    if (window.crypto && crypto.subtle && window.TextEncoder) {
      return crypto.subtle.digest('SHA-256', new TextEncoder().encode(str)).then(function (buf) {
        return Array.prototype.map.call(new Uint8Array(buf), function (b) { return ('0' + b.toString(16)).slice(-2); }).join('');
      }).catch(function () { return sha256Fallback(unescape(encodeURIComponent(str))); });
    }
    return Promise.resolve(sha256Fallback(unescape(encodeURIComponent(str))));
  }

  /* ---------- customer data normalisation (Bangladesh) ---------- */
  function phoneParts(raw) {
    var d = String(raw || '').replace(/\D/g, '');
    if (d.indexOf('880') === 0) d = d.slice(3);       // 880171... -> 171...
    if (d.indexOf('0') === 0) d = d.slice(1);         // 0171...  -> 171...
    if (!/^1[3-9]\d{8}$/.test(d)) return null;
    return { e164: '+880' + d, digits: '880' + d };   // Google: E.164 with +; Meta: digits with country code, no +
  }
  function splitName(full) { var p = String(full || '').trim().toLowerCase().split(/\s+/); return { first: p[0] || '', last: p.slice(1).join(' ') }; }
  var stripPunct = function (s) { return String(s || '').toLowerCase().replace(/[^\p{L}\p{N}]/gu, ''); };

  /* The exact strings that are hashed for Meta (meta_user_data): lowercase, trimmed; phone = digits with country code (8801XXXXXXXXX, no plus); name and city without punctuation or spaces; country "bd". Used by both the async and the synchronous hashing below, so the values are identical. */
  function metaNorm(c) {
    c = c || {};
    var ph = phoneParts(c.phone), nm = splitName(c.name), district = String(c.district || '').trim();
    return { ph: ph ? ph.digits : '', em: String(c.email || '').trim().toLowerCase(), fn: nm.first ? stripPunct(nm.first) : '', ln: nm.last ? stripPunct(nm.last) : '', ct: district ? stripPunct(district) : '' };
  }

  /* Builds hashed customer data for Google (user_data) and Meta (meta_user_data). Everything hashed once, here. */
  function customerData(c) {
    c = c || {};
    var ph = phoneParts(c.phone), nm = splitName(c.name), n = metaNorm(c), email = n.em;
    var street = String(c.address || '').trim().toLowerCase(), district = String(c.district || '').trim();
    return Promise.all([
      ph ? sha256(ph.e164) : '', email ? sha256(email) : '', nm.first ? sha256(nm.first) : '', nm.last ? sha256(nm.last) : '', street ? sha256(street) : '',
      n.ph ? sha256(n.ph) : '', n.fn ? sha256(n.fn) : '', n.ln ? sha256(n.ln) : '', n.ct ? sha256(n.ct) : '',
      sha256('bd'), sha256(uid)
    ]).then(function (r) {
      var g = { address: { country: 'BD' } };
      if (r[0]) g.sha256_phone_number = r[0];
      if (r[1]) g.sha256_email_address = r[1];
      if (r[2]) g.address.sha256_first_name = r[2];
      if (r[3]) g.address.sha256_last_name = r[3];
      if (r[4]) g.address.sha256_street = r[4];
      if (district) g.address.city = district; if (district) g.address.region = district;
      var m = { country: r[9], external_id: r[10] };
      if (r[5]) m.ph = r[5]; if (r[1]) m.em = r[1]; if (r[6]) m.fn = r[6]; if (r[7]) m.ln = r[7]; if (r[8]) m.ct = r[8];
      return { user_data: g, meta_user_data: m };
    });
  }

  /* Same meta_user_data as customerData(), but synchronous (pure-JS SHA-256), for the moment before GTM loads. */
  function sha256Sync(s) { s = String(s == null ? '' : s); return s ? sha256Fallback(unescape(encodeURIComponent(s))) : ''; }
  function metaUserDataSync(c) {
    var n = metaNorm(c), m = { country: sha256Sync('bd'), external_id: sha256Sync(uid) };
    if (n.ph) m.ph = sha256Sync(n.ph); if (n.em) m.em = sha256Sync(n.em); if (n.fn) m.fn = sha256Sync(n.fn); if (n.ln) m.ln = sha256Sync(n.ln); if (n.ct) m.ct = sha256Sync(n.ct);
    return m;
  }

  /* ---------- thank-you page: customer data goes into the dataLayer BEFORE GTM starts ---------- */
  /* The Meta Pixel is started by the GTM container; if the customer data only appears in the later purchase push, the Pixel has already begun without it.
     So on the thank-you page the hashed meta_user_data (and the visitor's external_id, the same key as on every event) is pushed first, from the order kept in sessionStorage.
     The purchase push itself still carries the same meta_user_data. No event_id here: the purchase event_id belongs to the purchase push only. */
  (function seedOrderData() {
    try {
      if (!/thank-you/.test(location.pathname)) return;
      var o = JSON.parse(sessionStorage.getItem('bg_last_order') || 'null');
      if (!o || !o.id) return;
      var demoOff = false; try { demoOff = !!o.demo && localStorage.getItem('bg_track_demo') !== '1'; } catch (e) { demoOff = !!o.demo; }
      if (demoOff) return;
      window.dataLayer.push({ external_id: uid, meta_user_data: metaUserDataSync(o) });
    } catch (e) { /* never block the page */ }
  })();

  /* ---------- GTM loader (set GTM_ID in assets/config.js; GTM_SRC optional first-party/server-side loader URL) ---------- */
  /* Not started on developer or preview hosts (localhost, 127.x, *.local, *.github.io), so testing there never sends events to the live Pixel/GA4.
     Add ?bggtm=1 to a URL to start it there on purpose (remembered for the browser tab). */
  var devHost = /^(localhost|127\.|0\.0\.0\.0|\[::1\]|.*\.local$|.*\.github\.io$)/i.test(location.hostname);
  if (devHost) { try { if (/[?&]bggtm=1/.test(location.search)) sessionStorage.setItem('bg_gtm_dev', '1'); devHost = sessionStorage.getItem('bg_gtm_dev') !== '1'; } catch (e) {} }
  if (BG.GTM_ID && !devHost) {
    (function (w, d, s, l, i) {
      w[l] = w[l] || []; w[l].push({ 'gtm.start': new Date().getTime(), event: 'gtm.js' });
      var f = d.getElementsByTagName(s)[0], j = d.createElement(s);
      j.async = true; j.src = (BG.GTM_SRC || 'https://www.googletagmanager.com/gtm.js') + '?id=' + i;
      f.parentNode.insertBefore(j, f);
    })(window, document, 'script', 'dataLayer', BG.GTM_ID);
  }

  /* ---------- identifiers sent with events ---------- */
  function ids() {
    var o = { fbp: getCookie('_fbp'), fbc: getCookie('_fbc'), external_id: uid };
    var a = attr.last || {}, f = attr.first || {};
    KEYS.forEach(function (k) { if (a[k]) o[k] = a[k]; });
    if (f.utm_source) o.first_utm_source = f.utm_source;
    if (f.utm_campaign) o.first_utm_campaign = f.utm_campaign;
    ['_ga', '_gcl_aw', '_clck'].forEach(function (n) { var v = getCookie(n); if (v) o[n.replace(/^_/, '')] = v; });
    return o;
  }

  /* ---------- products ---------- */
  function item(slug, opt) {
    var P = (window.BG_PRODUCTS || {})[slug]; if (!P) return null; opt = opt || {};
    var it = { item_id: P.sku, item_name: P.title, item_brand: 'Babyglee', item_category: 'Kids sneakers', item_category2: 'Bounce series',
      item_variant: opt.size ? P.color + ' / EU ' + opt.size : P.color, price: P.price || BG.PRICE, discount: Math.max(0, (P.listPrice || BG.LIST_PRICE || BG.PRICE) - (P.price || BG.PRICE)), quantity: opt.qty || 1 };
    if (opt.index != null) it.index = opt.index;
    if (opt.listId) { it.item_list_id = opt.listId; it.item_list_name = opt.listName || opt.listId; }
    return it;
  }
  var sum = function (items) { return items.reduce(function (a, i) { return a + i.price * i.quantity; }, 0); };

  /* ---------- pushing ---------- */
  function push(o) { window.dataLayer.push(o); }
  /* GA4 e-commerce push: clears the previous ecommerce object first, adds event_id (used to de-duplicate browser vs server events) */
  function ecom(name, ecommerce, extra) {
    ecommerce = ecommerce || {}; ecommerce.currency = CUR;
    var its = ecommerce.items || [], qty = its.reduce(function (a, i) { return a + (i.quantity || 1); }, 0);
    push({ ecommerce: null });
    var o = { event: name, event_id: (extra && extra.event_id) || eventId(name), event_time: Math.floor(Date.now() / 1000), event_source_url: location.href,
      external_id: uid, fbp: getCookie('_fbp'), fbc: getCookie('_fbc'), ecommerce: ecommerce,
      /* ready-made Meta custom_data (Pixel and Conversions API): same product IDs as the catalogue feed */
      meta_custom_data: { content_type: 'product', content_ids: its.map(function (i) { return i.item_id; }), num_items: qty, value: ecommerce.value, currency: CUR,
        contents: its.map(function (i) { return { id: i.item_id, quantity: i.quantity || 1, item_price: i.price }; }) } };
    var vid = ids(); for (var v in vid) if (vid[v] && o[v] == null) o[v] = vid[v];   // UTMs and click IDs on every event
    if (extra) for (var k in extra) if (k !== 'event_id') o[k] = extra[k];
    push(o); return o.event_id;
  }
  function pageData(type, section) {
    /* event_id here is the shared ID for PageView: use it in both the browser Pixel tag and the server tag so Meta counts one PageView */
    push({ event: 'page_data', event_id: eventId('page'), event_time: Math.floor(Date.now() / 1000), event_source_url: location.href, external_id: uid, fbp: getCookie('_fbp'), fbc: getCookie('_fbc'), page_type: type, site_section: section, currency: CUR, country: 'BD', language: 'en', store: 'babyglee', visitor: ids() });
  }

  /* ---------- debug overlay: add ?bgdebug=1 to any URL to see every dataLayer push on screen ---------- */
  if (/[?&]bgdebug=1/.test(location.search)) {
    var box = document.createElement('pre');
    box.style.cssText = 'position:fixed;left:0;right:0;bottom:0;max-height:38vh;overflow:auto;margin:0;padding:8px 10px;background:#111;color:#8ff0c8;font:11px/1.4 monospace;z-index:2147483647;white-space:pre-wrap';
    box.textContent = 'dataLayer debug (newest first)\n';
    document.addEventListener('DOMContentLoaded', function () { document.body.appendChild(box); });
    var orig = window.dataLayer.push.bind(window.dataLayer);
    window.dataLayer.push = function (o) { try { if (o && o.event && o.event.indexOf('gtm.') !== 0) box.textContent = 'dataLayer debug (newest first)\n' + o.event + ' ' + JSON.stringify(o).slice(0, 700) + '\n\n' + box.textContent.split('\n').slice(1).join('\n'); } catch (e) {} return orig(o); };
  }

  window.BGT = { push: push, ecom: ecom, item: item, sum: sum, pageData: pageData, customerData: customerData, ids: ids, eventId: eventId, sha256: sha256, phoneParts: phoneParts, getCookie: getCookie, uid: function () { return uid; }, attribution: function () { return attr; } };
})();
