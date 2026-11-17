(() => {
'use strict';
const $ = (s, r = document) => r.querySelector(s), $$ = (s, r = document) => [...r.querySelectorAll(s)];
const BG = window.BG || {}, PR = window.BG_PRODUCTS || {}, RV = Array.isArray(window.BG_REVIEWS) ? window.BG_REVIEWS : [];
const noop = () => {};
const T = window.BGT || { ecom: noop, push: noop, item: () => null, sum: () => 0, pageData: noop, customerData: () => Promise.resolve({}), ids: () => ({}), eventId: () => String(Date.now()), attribution: () => ({}), uid: () => '' };
const fmt = n => '৳' + Number(n).toLocaleString('en-US');
const page = document.body.dataset.page;
const toast = (() => { let t; return m => { const e = $('#toast'); if (!e) return; e.textContent = m; e.classList.add('on'); clearTimeout(t); t = setTimeout(() => e.classList.remove('on'), 2200); }; })();
const PAGE_TYPES = { landing: 'landing', checkout: 'checkout', thanks: 'thank_you' };
T.pageData(PAGE_TYPES[page] || 'info', 'landing');

/* ---------- catalogue helpers (live data from the admin panel when the backend is on) ---------- */
const esc = s => String(s == null ? '' : s).replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
const priceOf = s => (PR[s] && PR[s].price) || BG.PRICE;
const listOf = s => (PR[s] && PR[s].listPrice) || BG.LIST_PRICE || priceOf(s);
const usdOf = s => (PR[s] && PR[s].priceUsd != null) ? PR[s].priceUsd : BG.PRICE_USD;
const sizesOf = s => (PR[s] && PR[s].sizes && PR[s].sizes.length) ? PR[s].sizes.map(Number) : null;
const outOf = s => (PR[s] && PR[s].out) ? PR[s].out.map(Number) : [];
const soldOut = s => { const a = sizesOf(s), o = outOf(s); return !!a && a.every(n => o.includes(n)); };
function setPrice(box, slug) {
  if (!box) return;
  const p = slug ? priceOf(slug) : BG.PRICE, l = slug ? listOf(slug) : BG.LIST_PRICE, s = $('s', box), b = $('b', box);
  if (b) b.textContent = fmt(p);
  if (s) { s.textContent = fmt(l); s.hidden = !(l > p); }
}
/* Rebuilds the size chips from the product's own variations (admin panel); sold-out sizes are shown crossed out and cannot be chosen. */

/* ---------- mobile menu ---------- */
const burger = $('#burger'), nav = $('#nav');
if (burger) {
  const set = o => { nav.classList.toggle('open', o); document.body.classList.toggle('nav-open', o); burger.setAttribute('aria-expanded', o); };
  burger.addEventListener('click', () => set(!nav.classList.contains('open')));
  document.addEventListener('click', e => { if (nav.classList.contains('open') && !e.target.closest('#nav') && !e.target.closest('#burger')) set(false); });
  $$('#nav a').forEach(a => a.addEventListener('click', () => set(false)));
  document.addEventListener('keydown', e => e.key === 'Escape' && set(false));
}

/* ---------- ship-to selector ---------- */
const shipBtn = $('#shipBtn'), shipMenu = $('#shipMenu');
if (shipBtn) {
  const setShip = o => { shipMenu.hidden = !o; shipBtn.setAttribute('aria-expanded', o); };
  shipBtn.addEventListener('click', e => { e.stopPropagation(); setShip(shipMenu.hidden); });
  document.addEventListener('click', e => { if (!shipMenu.hidden && !shipMenu.contains(e.target)) setShip(false); });
  document.addEventListener('keydown', e => e.key === 'Escape' && setShip(false));
}

/* ---------- copy-link buttons (lp/index.html) ---------- */
$$('[data-copy]').forEach(b => b.addEventListener('click', async () => {
  const url = b.dataset.copy;
  try { await navigator.clipboard.writeText(url); }
  catch (e) { const ta = document.createElement('textarea'); ta.value = url; document.body.appendChild(ta); ta.select(); try { document.execCommand('copy'); } catch (x) {} document.body.removeChild(ta); }
  const old = b.textContent; b.textContent = 'Copied!'; toast('Link copied'); setTimeout(() => b.textContent = old, 1500);
}));

/* ---------- 3D tilt (pointer devices only) ---------- */
if (matchMedia('(hover:hover) and (pointer:fine)').matches) {
  $$('.tilt').forEach(el => {
    el.addEventListener('pointermove', e => {
      const r = el.getBoundingClientRect(), x = (e.clientX - r.left) / r.width - .5, y = (e.clientY - r.top) / r.height - .5;
      el.style.transform = `rotateY(${x * 14}deg) rotateX(${-y * 14}deg) translateY(-4px)`;
    });
    el.addEventListener('pointerleave', () => el.style.transform = '');
  });
  const stage = $('#stage');
  if (stage) {
    const shoes = $$('.shoe', stage);
    stage.addEventListener('pointermove', e => {
      const r = stage.getBoundingClientRect(), x = (e.clientX - r.left) / r.width - .5, y = (e.clientY - r.top) / r.height - .5;
      shoes.forEach(s => { s.style.setProperty('--ry', x * 22 + 'deg'); s.style.setProperty('--rx', -y * 16 + 'deg'); s.style.setProperty('--z', (s.dataset.depth || 0) + 'px'); });
    });
    stage.addEventListener('pointerleave', () => shoes.forEach(s => { s.style.setProperty('--ry', '0deg'); s.style.setProperty('--rx', '0deg'); s.style.setProperty('--z', '0px'); }));
  }
}

/* ---------- scroll reveal ---------- */
if ('IntersectionObserver' in window) {
  const io = new IntersectionObserver(es => es.forEach(e => { if (e.isIntersecting) { e.target.classList.add('in'); io.unobserve(e.target); } }), { threshold: .12 });
  $$('.sec-head,.pcard,.feat,.checks li,.faq details,.cc').forEach(el => { el.classList.add('rv'); io.observe(el); });
}

/* ---------- size finder (home) ---------- */
const CHART = [[21, 13.5, '12–18M'], [22, 14.0, '18–24M'], [23, 14.5, '2Y'], [24, 15.0, '2.5Y'], [25, 15.5, '3Y'], [26, 16.0, '3.5Y'], [27, 16.5, '4Y'], [28, 17.0, '4.5Y'],
  [29, 17.5, '5Y'], [30, 18.0, '5.5Y'], [31, 18.6, '6Y'], [32, 19.2, '6.5Y'], [33, 19.7, '7Y'], [34, 20.4, '8Y'], [35, 21.2, '9Y'], [36, 22.0, '10–12Y']];  // insole cm; insole = foot + 1 cm
/* Size for a foot length: the smallest EU size whose insole is at least foot + 1 cm; one size up for wide feet or thick socks. */
/* Returns { eu, age } or { eu: null, over: 'high' | 'low' } when the foot is outside what the chart supports (never a made-up size). */
function sizeFor(foot, wide) {
  const need = foot + 1, last = CHART.length - 1;
  if (need > CHART[last][1] + 0.001) return { eu: null, over: 'high' };
  if (foot < CHART[0][1] - 1.5 - 0.001) return { eu: null, over: 'low' };
  let i = CHART.findIndex(r => r[1] >= need - 0.001);
  if (wide) { if (i >= last) return { eu: null, over: 'high', wide: true }; i++; }
  return { eu: CHART[i][0], age: CHART[i][2] };
}
/* Binds one finder block (ids start with prefix p); onChange(eu or null) lets the size sheet offer "Select EU xx". */
function bindFinder(p, onChange) {
  const inp = $('#' + p + 'Cm'); if (!inp) return;
  const wide = $('#' + p + 'Wide'), out = $('#' + p + 'Out'), age = $('#' + p + 'Age'), note = $('#' + p + 'Note');
  const scope = inp.closest('.sheet') || inp.closest('.size-box') || document, base = note.textContent;
  const calc = () => {
    const v = parseFloat(String(inp.value).replace(',', '.'));
    $$('tr[data-eu]', scope).forEach(r => r.classList.toggle('hl', false));
    if (!(v >= 8 && v <= 25)) { out.textContent = 'EU —'; age.textContent = inp.value ? 'Enter 8 to 25 cm' : 'Enter a length'; note.textContent = base; if (onChange) onChange(null); return; }
    const r = sizeFor(v, wide.checked);
    if (!r.eu) {
      out.textContent = 'EU —'; age.textContent = 'No matching size';
      note.textContent = r.over === 'low' ? 'This is smaller than our smallest size (EU 21). Please message us and we will help.'
        : r.wide ? 'A wider fit would need a size above EU 36, which we do not make. Please message us and we will help.' : 'This is longer than our biggest size (EU 36). Please message us and we will help.';
      if (onChange) onChange(null); return;
    }
    out.textContent = 'EU ' + r.eu; age.textContent = '≈ ' + r.age;
    note.textContent = `Foot ${v.toFixed(1)} cm + 1 cm = ${(v + 1).toFixed(1)} cm (${((v + 1) / 2.54).toFixed(1)} in) insole${wide.checked ? ', one size up for wide feet or thick socks' : ''}.`;
    $$('tr[data-eu="' + r.eu + '"]', scope).forEach(x => x.classList.add('hl'));
    if (onChange) onChange(r.eu);
  };
  inp.addEventListener('input', calc); wide.addEventListener('change', calc); calc();
  return calc;
}
bindFinder('fs');

/* =====================================================================
   Bottom sheets (size guide + quick add): accessible, body-scroll locked
   ===================================================================== */
const sheetStack = [];
let lastFocus = null;
const syncLock = () => document.body.classList.toggle('lock', sheetStack.length > 0);
function openSheet(el) {
  if (!el) return;
  lastFocus = lastFocus || document.activeElement;
  el.hidden = false; sheetStack.push(el); syncLock();
  requestAnimationFrame(() => { el.classList.add('on'); const f = $('[data-close].icon-btn', el); if (f) f.focus({ preventScroll: true }); });
}
function closeSheet(el) {
  if (!el || el.hidden) return;
  el.classList.remove('on'); const i = sheetStack.indexOf(el); if (i > -1) sheetStack.splice(i, 1); syncLock();
  setTimeout(() => { if (!el.classList.contains('on')) el.hidden = true; }, 260);
  if (!sheetStack.length && lastFocus && lastFocus.focus) { try { lastFocus.focus({ preventScroll: true }); } catch (e) {} lastFocus = null; }
}
document.addEventListener('click', e => { const c = e.target.closest('[data-close]'); if (c) closeSheet(c.closest('.sheet-wrap')); });
document.addEventListener('keydown', e => {
  const top = sheetStack[sheetStack.length - 1]; if (!top) return;
  if (e.key === 'Escape') closeSheet(top);
  if (e.key === 'Tab') { const f = $$('button,[href],input,select,textarea,[tabindex]:not([tabindex="-1"])', top).filter(x => !x.disabled && x.offsetParent !== null); if (!f.length) return; const a = f[0], z = f[f.length - 1]; if (e.shiftKey && document.activeElement === a) { e.preventDefault(); z.focus(); } else if (!e.shiftKey && document.activeElement === z) { e.preventDefault(); a.focus(); } }
});

/* size guide sheet: foot-length helper + full table; can hand the chosen size back to the caller */
const sizeModal = $('#sizeModal');
let sizeTarget = null;
if (sizeModal) {
  const use = $('#szUse');
  const recalc = bindFinder('sz', eu => { use.dataset.eu = eu || ''; use.hidden = !(sizeTarget && eu); if (eu) use.textContent = 'Select EU ' + eu; });
  use.addEventListener('click', () => { if (sizeTarget && use.dataset.eu) sizeTarget(+use.dataset.eu); closeSheet(sizeModal); });
  document.addEventListener('click', e => {
    const b = e.target.closest('[data-open-size]'); if (!b) return;
    sizeTarget = b.sizeTarget || null; recalc(); openSheet(sizeModal);   // recalc: the kept measurement shows its "Select EU xx" button again
    T.push({ event: 'size_guide_open', page_type: PAGE_TYPES[page] || 'other' });
  });
}


const LISTS = {};
/* resolves with the promise's value, or null after ms milliseconds (the promise itself keeps running) */
const within = (pr, ms) => Promise.race([pr, new Promise(res => setTimeout(() => res(null), ms))]);
const itemsHTML = items => items.map(i => `<li><span>${esc(i.product)}<small>EU ${esc(i.size)}</small></span><b>× ${+i.qty}</b></li>`).join('');
const itemsOf = list => list.map((i, n) => T.item(i.slug, { size: i.size, qty: i.qty, index: n })).filter(Boolean);
const valueOf = items => T.sum(items);


const el = (form, k) => form.elements.namedItem(k);
const phoneOk = v => /^01[3-9]\d{8}$/.test(v);
/* Bangladesh mobile number: "+88" is fixed in front; the box keeps digits only, starts with 0, and stops at 11 digits. */
function cleanPhone(v) {
  let d = String(v || '').replace(/\D/g, '');
  if (d.startsWith('8801')) d = d.slice(2);     // +8801712... pasted or typed with the country code
  if (d[0] === '1') d = '0' + d;                // 1712... typed without the leading 0
  return d.slice(0, 11);
}
document.addEventListener('input', e => { const t = e.target; if (t && t.name === 'phone' && t.closest('.phone')) { const c = cleanPhone(t.value); if (c !== t.value) t.value = c; } });
/* Incomplete orders: once the mobile number is valid, what the visitor typed is saved so the team can follow up if the order is not finished. */
function watchLead(form, source, getItems) {
  let token = ''; try { token = sessionStorage.getItem('bg_lead') || ''; } catch (e) {}
  if (!token) { token = (Date.now().toString(36) + Math.random().toString(36).slice(2, 12)).toLowerCase(); try { sessionStorage.setItem('bg_lead', token); } catch (e) {} }
  let timer, retryTimer, saved = '', inflight = '', tries = 0, leadPushed = false;
  const bodyNow = () => JSON.stringify({ token, source, phone: el(form, 'phone').value, name: el(form, 'name').value, email: el(form, 'email').value, district: el(form, 'district').value, address: el(form, 'address').value,
    area: el(form, 'district').value || el(form, 'address').value ? (el(form, 'area').value === 'dhaka' ? 'Inside Dhaka' : 'Outside Dhaka') : '',
    items: getItems().map(i => ({ slug: i.slug, size: +i.size || 0, qty: i.qty })), tracking: Object.assign({ page_url: location.href, referrer: document.referrer }, T.attribution().last || {}, T.ids()) });
  /* The Lead event means "a valid mobile number was captured". It is sent once the backend has confirmed the save (right away in demo mode, where nothing is saved). */
  const pushLead = () => { if (leadPushed) return; leadPushed = true; stageEvent('generate_lead', custOf(form), getItems(), el(form, 'area').value, { event_id: 'lead_' + token, lead_type: 'incomplete_checkout', page_type: 'checkout' }); };
  const RETRY = [2000, 5000, 15000, 40000];
  const retry = () => { if (tries >= RETRY.length || form.dataset.done) return; clearTimeout(retryTimer); retryTimer = setTimeout(() => send(false), RETRY[tries++]); };
  /* A body counts as saved only after the backend answered ok. Network errors and 5xx/408/429 are retried with a growing pause; other 4xx answers are final until the form changes. */
  const send = async final => {
    if (!phoneOk(el(form, 'phone').value) || form.dataset.done) return;
    const body = bodyNow(); if (body === saved || body === inflight) return;
    if (!BG.LEAD_ENDPOINT) { saved = body; pushLead(); return; }
    /* leaving the page: a beacon is the most reliable way out; if the browser refuses it (returns false, e.g. over its size limit), fall back to a keepalive request */
    if (final && navigator.sendBeacon) { try { if (navigator.sendBeacon(BG.LEAD_ENDPOINT, new Blob([body], { type: 'text/plain' }))) { saved = body; return; } } catch (e) {} }
    inflight = body;
    try {
      const r = await fetch(BG.LEAD_ENDPOINT, { method: 'POST', headers: { 'Content-Type': 'text/plain' }, body, keepalive: true });
      const j = await r.json().catch(() => null);
      if (r.ok && j && j.ok) { saved = body; tries = 0; pushLead(); }
      else if (r.status >= 500 || r.status === 408 || r.status === 429) retry();
    } catch (e) { retry(); }
    finally { inflight = ''; }
  };
  const later = () => { clearTimeout(timer); timer = setTimeout(() => send(false), 1200); };
  form.addEventListener('input', later); form.addEventListener('change', later);
  addEventListener('pagehide', () => send(true));
}
const rules = {
  name: v => v.trim().length < 2 ? 'Please enter your name' : '',
  phone: v => !phoneOk(v) ? 'Enter your 11-digit mobile number, e.g. 01712345678' : '',
  email: v => v.trim() && !/^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(v.trim()) ? 'Enter a valid email or leave it empty' : '',
  district: v => !v ? 'Please select your district' : '',
  address: v => v.trim().length < 10 ? 'Please enter your full address' : ''
};
const setErr = (f, msg) => { const s = f.closest('.fld').querySelector('.err'); if (s) s.textContent = msg || ''; f.setAttribute('aria-invalid', msg ? 'true' : 'false'); };
/* On blur only that field is checked (no page jumps while the parent is still filling the form). */
function bindFields(form) {
  const keys = Object.keys(rules);
  const check = k => { const f = el(form, k), m = rules[k](f.value); setErr(f, m); return !m; };
  keys.forEach(k => { const f = el(form, k); f.addEventListener(f.tagName === 'SELECT' ? 'change' : 'blur', () => (f.value || f.tagName === 'SELECT') && check(k)); });
  return {
    firstInvalid: () => { const bad = keys.filter(k => !check(k)); return bad.length ? el(form, bad[0]) : null; },
    silentValid: () => keys.every(k => !rules[k](el(form, k).value))
  };
}
/* District decides the default delivery area (Dhaka = inside Dhaka); the parent can still change it. */
function bindDistrict(form) {
  const d = el(form, 'district');
  d.addEventListener('change', () => {
    const r = form.querySelector(`input[name=area][value=${d.value === 'Dhaka' ? 'dhaka' : 'outside'}]`);
    if (d.value && r && !r.checked) { r.checked = true; r.dispatchEvent(new Event('change', { bubbles: true })); }
  });
}
const newId = () => 'BG' + Date.now().toString(36).toUpperCase().slice(-7);
const areaLabel = a => a === 'dhaka' ? 'Inside Dhaka' : 'Outside Dhaka';
const custOf = form => ({ name: el(form, 'name').value, phone: el(form, 'phone').value, email: el(form, 'email').value, address: el(form, 'address').value, district: el(form, 'district').value });
const buildOrder = (form, source, items, area) => {
  const sub = items.reduce((a, i) => a + i.qty * i.price, 0), del = BG.DELIVERY[area], c = custOf(form);
  return { id: newId(), source, items, name: c.name.trim(), phone: c.phone.trim(), email: c.email.trim(), country: 'Bangladesh', district: c.district,
    address: c.address.trim(), area: areaLabel(area), subtotal: sub, delivery: del, total: sub + del, payment: 'Cash on Delivery', page: location.href, time: new Date().toISOString() };
};
/* Sends the order to ORDER_ENDPOINT. With no endpoint the site is in demo mode: the order is only kept locally. */
async function sendOrder(order) {
  if (BG.ORDER_ENDPOINT) {
    try {
      const r = await fetch(BG.ORDER_ENDPOINT, { method: 'POST', headers: { 'Content-Type': 'text/plain' }, body: JSON.stringify(order) });
      const j = await r.json().catch(() => null);
      if (j && j.ok) {
        /* keep what the server accepted (prices, delivery, total): the Purchase event is built from these, not from today's catalogue */
        if (j.total) { order.total = j.total; order.delivery = j.delivery != null ? j.delivery : order.delivery; }
        if (j.subtotal != null) order.subtotal = j.subtotal;
        if (Array.isArray(j.items)) order.accepted = j.items;
        return { ok: true };
      }
      return { ok: false, msg: j && j.error };
    } catch (e) { return { ok: false }; }
  }
  try { const k = 'bg_demo_orders', all = JSON.parse(localStorage.getItem(k) || '[]'); all.push(order); localStorage.setItem(k, JSON.stringify(all)); } catch (e) {}
  return { ok: true, demo: true };
}
const SEND_ERR = "Sorry, we couldn't place your order. Please check your connection and try again, or call us.";
function sendFailed(res) { const e = $('#sendErr'); e.textContent = res.msg || SEND_ERR; e.hidden = false; $('#submitBtn').disabled = false; e.scrollIntoView({ behavior: 'smooth', block: 'center' }); }
function showDone(order) {
  $('#oid').textContent = '#' + order.id;
  $('#rItems').innerHTML = itemsHTML(order.items);
  $('#rA').textContent = order.address + ', ' + order.district + ' (' + order.area + ')';
  $('#rT').textContent = fmt(order.total); $('#rPh').textContent = order.phone;
  $('#demoNote').hidden = !!BG.ORDER_ENDPOINT;
  $('#done').hidden = false; $('#done').scrollIntoView({ behavior: 'smooth', block: 'center' });
}
const fillCharges = () => { const d = $('#chD'), o = $('#chO'); if (d) d.textContent = fmt(BG.DELIVERY.dhaka); if (o) o.textContent = fmt(BG.DELIVERY.outside); };



/* ---------- the funnel events that need customer data (hashed once, in tracking.js) ---------- */
const fired = new Set();
async function stageEvent(name, cust, items, area, extra) {
  const cd = await T.customerData(cust), its = itemsOf(items), value = valueOf(its), del = BG.DELIVERY[area];
  const payload = Object.assign({ user_data: cd.user_data, meta_user_data: cd.meta_user_data }, T.ids(), extra || {});
  const ecommerce = { value, items: its };
  if (name === 'add_shipping_info') ecommerce.shipping_tier = areaLabel(area);
  if (name === 'add_payment_info') { ecommerce.payment_type = 'Cash on Delivery'; ecommerce.shipping_tier = areaLabel(area); }
  if (name === 'purchase') { ecommerce.transaction_id = payload.transaction_id; ecommerce.shipping = del; ecommerce.tax = 0; }
  return T.ecom(name, ecommerce, payload);
}
/* Purchase event from what the server accepted for this order (items, prices, delivery), never from the current catalogue or settings. */
async function purchaseEvent(o, beforePush) {
  const src = o.accepted && o.accepted.length ? o.accepted : o.items;
  const items = src.map((i, n) => {
    const g = T.item(i.slug, { size: i.size, qty: i.qty, index: n });
    if (!g) return { item_id: i.sku || i.slug, item_name: i.product || i.slug, item_brand: 'Babyglee', item_variant: 'EU ' + i.size, price: i.price, quantity: i.qty, index: n };
    g.price = i.price; g.discount = Math.max(0, ((PR[i.slug] && PR[i.slug].listPrice) || i.price) - i.price); if (i.sku) g.item_id = i.sku; return g;
  });
  const value = o.subtotal != null ? o.subtotal : valueOf(items);
  /* if hashing the customer data stalls, the Purchase is still sent (without it) rather than lost */
  let cd = {}; try { cd = await within(T.customerData({ name: o.name, phone: o.phone, email: o.email, address: o.address, district: o.district }), 2500) || {}; } catch (e) {}
  if (beforePush && beforePush() === false) return;   // already reported for this order (checked again right before the push)
  const payload = Object.assign({ user_data: cd.user_data, meta_user_data: cd.meta_user_data }, T.ids(), { event_id: 'purchase_' + o.id, transaction_id: o.id, order_total: o.total, order_source: 'landing', payment_type: 'Cash on Delivery', shipping_tier: o.area });
  return T.ecom('purchase', { transaction_id: o.id, value, shipping: o.delivery, tax: 0, items }, payload);
}
/* The same details go into the order so the server (Conversions API) can send the matching Purchase with the same event_id. */
async function trackingBlock(cust, order) {
  const cd = await T.customerData(cust);
  return Object.assign({ event_id: 'purchase_' + order.id, user_agent: navigator.userAgent, page_url: location.href, referrer: document.referrer, user_data: cd.user_data, meta_user_data: cd.meta_user_data, attribution: T.attribution() }, T.ids());
}
function watchShipping(form, fields, getItems, area) {
  const go = () => { if (fired.has('ship') || !fields.silentValid()) return; fired.add('ship'); stageEvent('add_shipping_info', custOf(form), getItems(), area()); };
  form.addEventListener('focusout', go); form.addEventListener('change', go);   // whichever field is completed last (name, phone, district or address) triggers the check
}

/* =====================================================================
   LANDING PAGE: choose several colours and sizes, add to cart, one checkout
   ===================================================================== */
const imgsOf = s => (PR[s] && PR[s].images && PR[s].images.length) ? PR[s].images : [PR[s].img];
const BAG = '<svg class="ic" aria-hidden="true"><use href="#i-bag"/></svg>';
const RULER = '<svg class="ic" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="2" y="8" width="20" height="8" rx="2"/><path d="M6 8v4M10 8v3M14 8v4M18 8v3"/></svg>';
const cardHTML = (s, p) => {
  const pr = priceOf(s), l = listOf(s), usd = usdOf(s), ims = imgsOf(s), all = sizesOf(s) || [], out = outOf(s), sold = soldOut(s), low = p.low || {};
  const chips = all.map(n => { const o = out.includes(n), lw = low[n] ? ` title="Only ${low[n]} left"` : (o ? ' title="Sold out"' : ''); return `<label class="szc${o ? ' out' : ''}${low[n] ? ' low' : ''}"${lw}><input type="radio" name="sz-${esc(s)}" value="${n}"${o ? ' disabled' : ''}><span>${n}</span></label>`; }).join('');
  return `<article class="pc${sold ? ' is-sold' : ''}" id="p-${esc(s)}" data-slug="${esc(s)}">
  <div class="pc-img"><span class="sw" style="background:${esc(p.colorHex || '#24babc')}"></span><span class="pc-in"></span><img class="pc-main" src="${esc(ims[0])}" alt="${esc(p.title)}" loading="lazy">
    ${ims.length > 1 ? `<div class="thumbs">${ims.map((u, i) => `<button type="button" class="th${i ? '' : ' on'}" data-img="${esc(u)}" aria-label="Photo ${i + 1}"><img src="${esc(u)}" alt="" loading="lazy"></button>`).join('')}</div>` : ''}</div>
  <div class="pc-body"><h3>${esc(p.title.replace(/^Babyglee\s+/, ''))}</h3>
    <div class="pc-price">${l > pr ? `<s>${fmt(l)}</s> ` : ''}<b>${fmt(pr)}</b>${l > pr ? `<span class="off">Save ${Math.round((l - pr) / l * 100)}%</span>` : ''}</div>
    ${usd ? `<p class="usd-line">US$${usd} <span>international price</span></p>` : ''}
    <fieldset class="pc-sizes"><button type="button" class="btn block ghost find-size" data-open-size>${RULER} Find the right size<small>Enter your child's foot length in cm</small></button><legend>Choose size (EU)</legend><div class="szs">${chips}</div><small class="err"></small></fieldset>
    <div class="pc-buy"><div class="qty"><button type="button" data-q="-1" aria-label="Decrease quantity">−</button><output>1</output><button type="button" data-q="1" aria-label="Increase quantity">+</button></div>
      ${sold ? '<button class="btn" type="button" disabled>Sold out</button>' : `<button class="btn" type="button" data-add>${BAG} Add to cart</button>`}</div>
    <p class="pc-msg" role="status"></p></div></article>`;
};
const stars = n => '★★★★★'.slice(0, n) + '☆☆☆☆☆'.slice(0, 5 - n);

/* ---------- cart ---------- */
const KEY = 'bg_cart';
const loadCart = () => { try { const c = JSON.parse(localStorage.getItem(KEY) || '[]'); return (Array.isArray(c) ? c : []).filter(i => PR[i.slug] && i.size && i.qty > 0).map(i => ({ ...i, k: i.slug + '|' + i.size })); } catch (e) { return []; } };
let cart = loadCart();
const persist = () => { try { localStorage.setItem(KEY, JSON.stringify(cart.map(({ slug, size, qty }) => ({ slug, size, qty })))); } catch (e) {} };
const count = () => cart.reduce((a, i) => a + i.qty, 0);
const subtotal = () => cart.reduce((a, i) => a + i.qty * priceOf(i.slug), 0);
const toOrderItems = list => list.map(i => ({ product: PR[i.slug].title, slug: i.slug, size: i.size, qty: i.qty, price: priceOf(i.slug) }));

const lineHTML = (i, edit) => {
  const p = PR[i.slug];
  return `<div class="cl" data-k="${i.k}"><img src="${p.img}" alt="" loading="lazy">
    <div class="cl-i"><b>${p.title}</b><small>Size EU ${i.size}</small>
    ${edit ? `<div class="qty sm"><button type="button" data-act="dec" aria-label="Decrease quantity">−</button><output>${i.qty}</output><button type="button" data-act="inc" aria-label="Increase quantity">+</button></div>` : `<small>Qty ${i.qty}</small>`}</div>
    <div class="cl-p"><b>${fmt(i.qty * priceOf(i.slug))}</b>${edit ? '<button type="button" class="rm" data-act="rm">Remove</button>' : ''}</div></div>`;
};

let onCartChange = () => {};
const cartSheet = $('#cartSheet');
function drawCartSheet() {
  if (!cartSheet) return;
  const l = cart, n = count(), empty = !l.length;
  $('#csLines').innerHTML = l.map(i => lineHTML(i, true)).join('');
  $('#csEmpty').hidden = !empty; $('#csFoot').hidden = empty;
  $('#csCount').textContent = n + (n === 1 ? ' pair' : ' pairs'); $('#csTotal').textContent = fmt(subtotal()); $('#csGo').textContent = 'Checkout — ' + fmt(subtotal());
}
function refresh() {
  const n = count();
  $$('.js-cart-count').forEach(c => { c.textContent = n; c.classList.toggle('on', n > 0); });
  const bar = $('#cartBar');
  if (bar) { bar.hidden = n === 0; $('#cbGo').textContent = 'Checkout · ' + fmt(subtotal()); document.body.classList.toggle('has-cartbar', n > 0); }
  const cf = $('#cartFab'); if (cf) cf.hidden = n === 0;
  drawCartSheet();
  $$('.pc').forEach(c => { const q = cart.filter(i => i.slug === c.dataset.slug).reduce((a, i) => a + i.qty, 0), b = $('.pc-in', c); if (b) b.textContent = q ? q + ' in cart' : ''; });
  onCartChange();
}
function change(k, d) {
  const i = cart.find(x => x.k === k); if (!i) return;
  if (d < 0) T.ecom('remove_from_cart', { value: priceOf(i.slug), items: [T.item(i.slug, { size: i.size, qty: 1 })] });
  const before = i.qty; i.qty += d; if (i.qty < 1) cart = cart.filter(x => x !== i); else i.qty = Math.min(10, i.qty);
  persist(); refresh();
  if (d > 0 && i.qty > before) T.ecom('add_to_cart', { value: priceOf(i.slug), items: [T.item(i.slug, { size: i.size, qty: 1 })] });   // one more pair added from the cart
}
function removeLine(k) {
  const i = cart.find(x => x.k === k); if (!i) return;
  T.ecom('remove_from_cart', { value: priceOf(i.slug) * i.qty, items: [T.item(i.slug, { size: i.size, qty: i.qty })] });
  cart = cart.filter(x => x !== i); persist(); refresh();
}
/* Adds pairs (at most 10 of one size). Returns how many were really added; the event reports only those. */
function addToCart(slug, size, qty) {
  const k = slug + '|' + size, ex = cart.find(i => i.k === k), before = ex ? ex.qty : 0, added = Math.min(10, before + qty) - before;
  if (added <= 0) return 0;
  if (ex) ex.qty = before + added; else cart.push({ k, slug, size, qty: added });
  persist(); refresh();
  T.ecom('add_to_cart', { value: priceOf(slug) * added, items: [T.item(slug, { size, qty: added })] });
  return added;
}


/* "Added to your cart" pop-up: what was added, cart total, keep shopping or check out */
function showAdded(slug, size, added) {
  const pop = $('#addedPop'); if (!pop) return;
  const p = PR[slug]; if (!p) return;
  const img = $('#apImg'); img.src = imgsOf(slug)[0]; img.alt = p.title;
  $('#apName').textContent = String(p.title).replace(/^Babyglee\s+/, '');
  $('#apMeta').textContent = `EU ${size} × ${added} · ${fmt(priceOf(slug) * added)}`;
  const n = count(); $('#apCount').textContent = `Your cart: ${n} ${n === 1 ? 'pair' : 'pairs'}`; $('#apTotal').textContent = fmt(subtotal());
  $('#apGo').textContent = 'Checkout · ' + fmt(subtotal());
  openSheet(pop);
}

if (page === 'landing') {
  /* hero price follows the admin catalogue */
  const slugsAll = Object.keys(PR);
  if (slugsAll.length) { const pt = $('.hero .price-tag'); if (pt) { const lo = Math.min(...slugsAll.map(priceOf)), hi = Math.max(...slugsAll.map(listOf)); $('b', pt).textContent = fmt(lo); const s = $('s', pt); s.textContent = fmt(hi); s.hidden = !(hi > lo); } const un = $('.hero .usd-note b'); if (un) un.textContent = 'US$' + Math.max(...slugsAll.map(usdOf)); }
  const grid = $('#grid'), slugs = slugsAll, listId = 'landing', listName = 'Landing - Bounce series';
  grid.innerHTML = slugs.length ? slugs.map(s => cardHTML(s, PR[s])).join('') : '<p class="empty-note">No products are available right now. Please check back soon.</p>';
  $$('.pc', grid).forEach(c => { const b = $('[data-open-size]', c); b.sizeTarget = eu => { const r = $(`input[value="${eu}"]`, c); if (r && !r.disabled) { r.checked = true; $('.err', c).textContent = ''; } }; });
  const touched = new Set();
  const touch = c => { const s = c.dataset.slug; if (touched.has(s)) return; touched.add(s); T.ecom('select_item', { item_list_id: listId, item_list_name: listName, items: [T.item(s, { index: slugs.indexOf(s), listId, listName })] }); };
  grid.addEventListener('click', e => {
    const c = e.target.closest('.pc'); if (!c) return; const s = c.dataset.slug;
    const th = e.target.closest('.th'); if (th) { $('.pc-main', c).src = th.dataset.img; $$('.th', c).forEach(x => x.classList.toggle('on', x === th)); touch(c); return; }
    const q = e.target.closest('[data-q]'); if (q) { const o = $('.qty output', c); o.textContent = Math.max(1, Math.min(10, +o.textContent + +q.dataset.q)); touch(c); return; }
    if (!e.target.closest('[data-add]')) return;
    const r = $('input:checked', c);
    if (!r) { $('.err', c).textContent = 'Please select a size'; const b = $('.szs', c); b.classList.remove('shake'); void b.offsetWidth; b.classList.add('shake'); return; }
    const o = $('.qty output', c), n = +o.textContent, size = +r.value;
    const added = addToCart(s, size, n); touch(c);
    if (!added) { $('.pc-msg', c).innerHTML = `You already have the maximum of 10 pairs in EU ${size}. <a href="checkout.html">Checkout</a> or pick another size.`; return; }
    o.textContent = '1'; r.checked = false;
    const btn = $('[data-add]', c); btn.classList.add('added'); btn.innerHTML = 'Added ✓'; setTimeout(() => { btn.classList.remove('added'); btn.innerHTML = BAG + ' Add to cart'; }, 1400);
    $('.pc-msg', c).innerHTML = `EU ${size} × ${added} added${added < n ? ' (maximum 10 per size)' : ''}. <a href="checkout.html">Checkout</a> or pick another size or colour.`;
    showAdded(s, size, added);
  });
  grid.addEventListener('change', e => { if (!e.target.matches('input[type=radio]')) return; const c = e.target.closest('.pc'); $('.err', c).textContent = ''; touch(c); T.push({ event: 'select_size', item_id: PR[c.dataset.slug].sku, size: 'EU ' + e.target.value }); });
  const sendList = () => T.ecom('view_item_list', { item_list_id: listId, item_list_name: listName, items: slugs.map((s, n) => T.item(s, { index: n, listId, listName })) });
  /* the list counts as seen when its first product card shows (the whole grid is taller than a small phone screen, so it can never be 15% visible there) */
  const firstCard = grid.firstElementChild;
  if ('IntersectionObserver' in window && firstCard) { const o = new IntersectionObserver(es => { if (es.some(e => e.isIntersecting)) { sendList(); o.disconnect(); } }, { threshold: 0.1 }); o.observe(firstCard); } else sendList();
  T.ecom('view_item', { value: priceOf(slugs[0] || ''), items: slugs.length ? [T.item(slugs[0])] : [] }, { page_type: 'landing', note: 'landing_view' });

  /* inside-every-Bounce hotspots: tap a number or a row to highlight both */
  const hl = i => $$('.hs,.anat-list li').forEach(x => x.classList.toggle('on', x.dataset.i === String(i)));
  $$('.hs,.anat-list li').forEach(x => { x.addEventListener('click', () => hl(x.dataset.i)); x.addEventListener('mouseenter', () => hl(x.dataset.i)); });

  /* reviews: real customer reviews added in the admin panel (text or screenshot); the section stays hidden when there are none */
  if (RV.length) {
    const avg = RV.reduce((a, r) => a + (+r.rating || 5), 0) / RV.length;
    $('#reviews').hidden = false; const nv = $('#navReviews'); if (nv) nv.hidden = false;
    $('#rvSum').innerHTML = `<span class="stars">${stars(Math.round(avg))}</span> <b>${avg.toFixed(1)}</b> out of 5 from ${RV.length} review${RV.length > 1 ? 's' : ''}`;
    $('#rvTrack').innerHTML = RV.map(r => r.img
      ? `<figure class="rvc shot"><button type="button" data-shot="${esc(r.img)}" aria-label="Open review screenshot"><img src="${esc(r.img)}" alt="Review by ${esc(r.name)}" loading="lazy"></button><figcaption><b>${esc(r.name)}</b>${r.city ? ' · ' + esc(r.city) : ''}<span class="stars">${stars(+r.rating || 5)}</span>${r.text ? `<p>${esc(r.text)}</p>` : ''}</figcaption></figure>`
      : `<figure class="rvc"><span class="stars">${stars(+r.rating || 5)}</span><p>“${esc(r.text)}”</p><figcaption><b>${esc(r.name)}</b>${r.city ? ' · ' + esc(r.city) : ''}</figcaption></figure>`).join('');
    $('#rvTrack').addEventListener('click', e => { const b = e.target.closest('[data-shot]'); if (!b) return; $('#shotImg').src = b.dataset.shot; lastFocus = b; openSheet($('#shotBox')); });
  }
}

/* =====================================================================
   CHECKOUT (page 2): everything in the cart, one set of details, Cash on Delivery
   ===================================================================== */
if (page === 'checkout') {
  const form = $('#coForm'); fillCharges();
  const area = () => el(form, 'area').value, lines = () => cart;
  const draw = () => {
    const l = lines(), sub = subtotal(), del = l.length ? BG.DELIVERY[area()] : 0;
    $('#coLines').innerHTML = l.map(i => lineHTML(i, true)).join('');
    $('#sSub').textContent = fmt(sub); $('#sDel').textContent = fmt(del); $('#sTot').textContent = fmt(sub + del); $('#sumTop').textContent = fmt(sub + del);
    $('#submitBtn').textContent = 'Place order — ' + fmt(sub + del);
    $('#coGrid').hidden = !l.length; $('#coEmpty').hidden = !!l.length;
  };
  onCartChange = draw; form.addEventListener('change', draw); draw();
  $('#coLines').addEventListener('click', e => { const b = e.target.closest('[data-act]'); if (!b) return; const k = b.closest('.cl').dataset.k, a = b.dataset.act; a === 'inc' ? change(k, 1) : a === 'dec' ? change(k, -1) : removeLine(k); });
  if (matchMedia('(max-width:980px)').matches) $('#sumD').open = false;
  if (cart.length) { T.ecom('view_cart', { value: subtotal(), items: itemsOf(cart) }); T.ecom('begin_checkout', { value: subtotal(), items: itemsOf(cart) }, { page_type: 'checkout' }); }
  const fields = bindFields(form); bindDistrict(form);
  watchShipping(form, fields, lines, area); watchLead(form, 'landing', lines);
  let sending = false;
  form.addEventListener('submit', async e => {
    e.preventDefault();
    if (sending || !cart.length) return;
    const bad = fields.firstInvalid();
    if (bad) { bad.scrollIntoView({ behavior: 'smooth', block: 'center' }); return; }
    sending = true; $('#submitBtn').disabled = true; $('#sendErr').hidden = true;
    const cust = custOf(form), order = buildOrder(form, 'landing', toOrderItems(lines()), area());
    /* Tracking must never hold up an order: both tracking steps run together and share one short time limit (1.2 s), then the order goes on. */
    const tbP = trackingBlock(cust, order), apP = stageEvent('add_payment_info', cust, lines(), area());
    await within(Promise.all([tbP, apP]), 1200);
    order.tracking = await within(tbP, 0) || Object.assign({ event_id: 'purchase_' + order.id, user_agent: navigator.userAgent, page_url: location.href, referrer: document.referrer, attribution: T.attribution() }, T.ids());
    const res = await sendOrder(order);
    if (!res.ok) { sending = false; sendFailed(res); return; }
    form.dataset.done = '1'; try { sessionStorage.removeItem('bg_lead'); } catch (e) {}
    const keep = Object.assign({}, order, { demo: !BG.ORDER_ENDPOINT }); delete keep.tracking;
    try { sessionStorage.setItem('bg_last_order', JSON.stringify(keep)); } catch (e) {}
    cart = []; persist();
    location.href = 'thank-you.html';
  });
}

/* =====================================================================
   THANK YOU (page 3): order summary; the Purchase event fires here once per order
   ===================================================================== */
if (page === 'thanks') {
  let o = null; try { o = JSON.parse(sessionStorage.getItem('bg_last_order') || 'null'); } catch (e) {}
  if (!o || !o.id) $('#noOrder').hidden = false;
  else {
    $('#done').hidden = false; $('#oid').textContent = '#' + o.id;
    $('#rItems').innerHTML = itemsHTML(o.items);
    $('#rA').textContent = o.address + ', ' + o.district + ' (' + o.area + ')'; $('#rT').textContent = fmt(o.total); $('#rPh').textContent = o.phone;
    $('#demoNote').hidden = !o.demo;
    /* The order id is remembered in sessionStorage and localStorage; a reload, a back/forward visit or a later visit never sends the same order again. */
    const k = 'bg_purchased', readDone = () => { let all = []; [sessionStorage, localStorage].forEach(st => { try { all = all.concat(JSON.parse(st.getItem(k) || '[]')); } catch (e) {} }); return all; };
    /* A demo order (no backend) is not a sale: it sends no Purchase unless localStorage bg_track_demo = 1 (for testing the dataLayer). */
    let demoOff = false; try { demoOff = !!o.demo && localStorage.getItem('bg_track_demo') !== '1'; } catch (e) { demoOff = !!o.demo; }
    if (!readDone().includes(o.id) && !demoOff) {
      /* marked in the same moment the event goes into the dataLayer (after the customer data is hashed), so a quick reload cannot send it twice */
      purchaseEvent(o, () => {
        const all = readDone(); if (all.includes(o.id)) return false;
        const next = JSON.stringify(all.concat(o.id).slice(-50)); [sessionStorage, localStorage].forEach(st => { try { st.setItem(k, next); } catch (e) {} });
      }).catch(() => {});
    }
  }
}

/* floating WhatsApp stays out of the way while the hero buttons are on screen (it covered "Find my kid's size" on short phones) */
const heroCta = $('.hero .cta');
if (heroCta && 'IntersectionObserver' in window) new IntersectionObserver(es => document.body.classList.toggle('cta-vis', es[0].isIntersecting), { threshold: 0.01 }).observe(heroCta);

/* floating WhatsApp: pre-filled with what the visitor is looking at */
const wa = $('#waFab');
if (wa) wa.href = `https://wa.me/${BG.WHATSAPP}?text=` + encodeURIComponent('Hi Babyglee, I need help with: ' + document.title.replace(/\s*[—|-]\s*Babyglee.*$/, ''));
document.addEventListener('click', e => { const a = e.target.closest('a[href*="wa.me"]'); if (a) T.push({ event: 'whatsapp_click', event_id: T.eventId('whatsapp'), event_source_url: location.href, external_id: T.ids().external_id, fbp: T.ids().fbp, fbc: T.ids().fbc, page_type: PAGE_TYPES[page] || 'info', link_location: a.id === 'waFab' ? 'floating_button' : 'page_link' }); });
refresh();
/* ---------- cart sheet (floating cart button + header bag) ---------- */
if (cartSheet) {
  const openCart = () => { drawCartSheet(); openSheet(cartSheet); if (cart.length) T.ecom('view_cart', { value: subtotal(), items: itemsOf(cart) }); };
  document.addEventListener('click', e => { if (e.target.closest('#cartFab') || e.target.closest('a.cart-btn')) { e.preventDefault(); openCart(); } });
  $('#csLines').addEventListener('click', e => { const b = e.target.closest('[data-act]'); if (!b) return; const k = b.closest('.cl').dataset.k, a = b.dataset.act; a === 'inc' ? change(k, 1) : a === 'dec' ? change(k, -1) : removeLine(k); });
}
})();
