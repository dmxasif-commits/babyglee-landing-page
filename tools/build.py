#!/usr/bin/env python3
"""Generates the Babyglee landing site (index, checkout, thank-you, policies) into the repo root: python3 tools/build.py"""
import json, pathlib, re

OUT = pathlib.Path(__file__).resolve().parent.parent
BASE = "https://dmxasif-commits.github.io/babyglee-landing-page/"  # change if you move to a custom domain
PRICE, LIST = 1290, 1800
PRICE_USD = 15  # international price, no discount (1,800 BDT list price at ~123 BDT/USD = $14.63)
WA = "8801974974973"
PHONE_DISPLAY = "+880 1974-974973"

PRODUCTS = [
    dict(key="sky-blue", slug="bounce-sky-blue", img="sky-blue-yellow", name="Sky Blue & Yellow", short="Sky Blue", color="#3fb4e8"),
    dict(key="blue-beige", slug="bounce-blue-beige", img="blue-beige", name="Blue & Beige", short="Blue & Beige", color="#3d7fa5"),
    dict(key="grey", slug="bounce-grey", img="grey", name="Grey", short="Grey", color="#8a9096"),
    dict(key="navy-brown", slug="bounce-navy-brown", img="navy-brown", name="Navy & Brown", short="Navy & Brown", color="#26335a"),
    dict(key="black", slug="bounce-black", img="black", name="Black", short="Black", color="#262626"),
]

ICONS = {
 "bag": '<path d="M5 8h14l-1 12H6z"/><path d="M9 8a3 3 0 016 0"/>',
 "truck": '<path d="M3 7h11v9H3z"/><path d="M14 10h4l3 3v3h-7z"/><circle cx="7" cy="18" r="1.8"/><circle cx="17" cy="18" r="1.8"/>',
 "cash": '<rect x="3" y="6" width="18" height="12" rx="2"/><circle cx="12" cy="12" r="2.6"/>',
 "exchange": '<path d="M4 8h13l-3-3"/><path d="M20 16H7l3 3"/>',
 "shield": '<path d="M12 3l7 3v5c0 5-3 8-7 10-4-2-7-5-7-10V6z"/><path d="M9 12l2 2 4-4"/>',
 "ruler": '<rect x="3" y="8" width="18" height="8" rx="1.5"/><path d="M7 8v3M11 8v4M15 8v3M19 8v4"/>',
 "phone": '<path d="M5 4h4l2 5-2.5 1.5a11 11 0 005 5L15 13l5 2v4a2 2 0 01-2 2A16 16 0 013 6a2 2 0 012-2z"/>',
 "whatsapp": '<path d="M4 20l1.3-4A8 8 0 1112 20a8 8 0 01-3.7-.9z"/><path d="M9 9.5c.4 2.2 2.6 4.4 5 5l1.2-1.2-2-1-.8.8a4 4 0 01-2-2l.8-.8-1-2z"/>',
 "mail": '<rect x="3" y="5" width="18" height="14" rx="2"/><path d="M3 7l9 6 9-6"/>',
 "pin": '<path d="M12 21s-7-6-7-11a7 7 0 0114 0c0 5-7 11-7 11z"/><circle cx="12" cy="10" r="2.5"/>',
 "layers": '<path d="M12 3l9 5-9 5-9-5z"/><path d="M3 13l9 5 9-5"/>',
 "cushion": '<path d="M4 15c0-4 3-7 8-7s8 3 8 7v2H4z"/><path d="M8 12.5c1-.8 2.2-1.2 4-1.2"/>',
 "expand": '<path d="M4 9V4h5M20 9V4h-5M4 15v5h5M20 15v5h-5"/>',
 "bolt": '<path d="M13 2L5 14h6l-1 8 8-12h-6z"/>',
 "grid": '<path d="M4 8h16M4 12h16M4 16h16"/><path d="M8 5v14M12 5v14M16 5v14"/>',
 "menu": '<path d="M4 7h16M4 12h16M4 17h16"/>',
 "close": '<path d="M6 6l12 12M18 6L6 18"/>',
 "check": '<path d="M5 12l5 5 9-10"/>',
 "facebook": '<path d="M14 8h3V4h-3a4 4 0 00-4 4v3H7v4h3v6h4v-6h3l1-4h-4V8.5z"/>',
 "chev": '<path d="M6 9l6 6 6-6"/>',
 "clock": '<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/>',
 "star": '<path d="M12 3l2.7 5.6 6.1.9-4.4 4.3 1 6.1L12 17l-5.4 2.9 1-6.1L3.2 9.5l6.1-.9z"/>',
}
SPRITE = '<svg width="0" height="0" style="position:absolute" aria-hidden="true">' + "".join(
    f'<symbol id="i-{k}" viewBox="0 0 24 24">{v}</symbol>' for k, v in ICONS.items()) + "</svg>"

def ic(n, cls=""):
    return f'<svg class="ic {cls}" aria-hidden="true"><use href="#i-{n}"/></svg>'

def fmt(n):
    return f"৳{n:,}"

# ---------- size data ----------
def age_band(eu):
    if eu <= 23: return "≈ 1–2 yrs"
    if eu <= 26: return "≈ 2–4 yrs"
    if eu <= 29: return "≈ 4–6 yrs"
    if eu <= 32: return "≈ 6–8 yrs"
    return "≈ 8–10 yrs"

SIZE_CHART = [(21, 13.5, "12–18M"), (22, 14.0, "18–24M"), (23, 14.5, "2Y"), (24, 15.0, "2.5Y"), (25, 15.5, "3Y"), (26, 16.0, "3.5Y"), (27, 16.5, "4Y"), (28, 17.0, "4.5Y"),
              (29, 17.5, "5Y"), (30, 18.0, "5.5Y"), (31, 18.6, "6Y"), (32, 19.2, "6.5Y"), (33, 19.7, "7Y"), (34, 20.4, "8Y"), (35, 21.2, "9Y"), (36, 22.0, "10–12Y")]  # insole cm; foot = insole - 1

def finder(p, use=False):
    """Size finder block: measuring steps, centimetre entry, result. Ids start with the prefix p (sz = size sheet, fs = page section)."""
    return f"""<ol class="mstep"><li>Stand your child on a sheet of paper, heel against a wall.</li><li>Mark the tip of the longest toe, then measure from the wall to the mark.</li><li>Type the length below. We add 1 cm for growing room.</li></ol>
      <label class="sl" for="{p}Cm">Foot length in cm</label>
      <div class="cm-row"><input type="number" id="{p}Cm" inputmode="decimal" min="8" max="25" step="0.1" placeholder="e.g. 15" autocomplete="off"><span>cm</span></div>
      <label class="wide"><input type="checkbox" id="{p}Wide"> Wide feet or thick socks (one size up)</label>
      <div class="size-res" id="{p}Res"><span>Suggested size</span><b id="{p}Out">EU —</b><em id="{p}Age">Enter a length</em></div>
      <p class="fine" id="{p}Note">Insole length = foot length + 1 cm. Example: a 15 cm foot needs a 16 cm insole, which is EU 26.</p>
      {'<button class="btn block" type="button" id="szUse" hidden>Select this size</button>' if use else ''}"""

def size_table():
    rows = "".join(f"<tr data-eu=\"{eu}\"><td><b>EU {eu}</b></td><td>{ins-1:.1f} cm</td><td>{ins:.1f} cm</td><td>{age}</td></tr>" for eu, ins, age in SIZE_CHART)
    return (f'<div class="tbl-wrap"><table class="tbl"><thead><tr><th>Shoe size</th><th>Foot length</th><th>Insole</th><th>Age</th></tr></thead>'
            f'<tbody>{rows}</tbody></table></div>'
            '<p class="fine">Pick the size whose insole is your child\'s foot length + 1 cm. For wide feet or thick socks, go one size up. Our team also confirms the size with you by call or message before shipping.</p>')

# ---------- shared chrome ----------
FAVICON = ("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 64 64'%3E%3Crect width='64' height='64' rx='16' fill='%2324babc'/%3E"
           "%3Ctext x='32' y='46' font-size='40' font-family='Arial' font-weight='700' text-anchor='middle' fill='white'%3Eb%3C/text%3E%3C/svg%3E")

def head(title, desc, page, img="img/sky-blue-yellow.webp", extra=""):
    return f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{desc}">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:type" content="website">
<meta property="og:image" content="{BASE}{img}">
<meta name="theme-color" content="#24babc">
<link rel="icon" href="{FAVICON}">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Fredoka:wght@500;600;700&family=Hind+Siliguri:wght@400;500;600;700&family=Nunito:wght@400;600;700;800&display=swap" rel="stylesheet">
<link rel="stylesheet" href="assets/style.css">
<script src="assets/config.js"></script>
<script src="assets/products.js"></script>
<script src="assets/reviews.js"></script>
<script src="assets/tracking.js"></script>
{extra}
</head>
<body data-page="{page}">
{SPRITE}
'''

def write(name, html):
    (OUT / name).write_text(html, encoding="utf-8")

# ---------- reusable blocks ----------
TRUST = [("cash", "Cash on Delivery", "Pay when it arrives"), ("truck", "Fast home delivery", "Across Bangladesh"),
         ("exchange", "72-hour exchange", "Easy size swaps"), ("shield", "Kid-safe materials", "REACH-compliant")]

def trust_strip():
    return '<section class="trust"><div class="wrap trust-grid">' + "".join(
        f'<div class="tr">{ic(i)}<div><b>{t}</b><span>{s}</span></div></div>' for i, t, s in TRUST) + "</div></section>"

FEATURES = [
 ("layers", "Multi-density sole", "Cushions every step and helps protect growing joints."),
 ("cushion", "Memory-foam insole", "Soft Ortholite-style insole for all-day comfort."),
 ("expand", "Wide toe box", "Shaped around natural foot development."),
 ("bolt", "Fast-lock strap", "Velcro strap with stretch bands, so kids can put them on alone."),
 ("grid", "Anti-slip rubber tread", "Shock-absorbing grip for playgrounds, courts and parks."),
 ("shield", "Safe materials", "Microfiber leather and breathable mesh; REACH, phthalate and azo-dye limits."),
]

def feature_cards():
    return '<div class="feat-grid">' + "".join(
        f'<article class="feat tilt"><span class="ficon">{ic(i)}</span><h3>{t}</h3><p>{d}</p></article>' for i, t, d in FEATURES) + "</div>"

FAQ = [
 ("How does delivery work?", "We deliver to your home across the areas we serve. Our team calls or messages you to confirm your size and address before shipping."),
 ("Can I pay on delivery?", "Yes. Cash on Delivery is available on every order."),
 ("What if the size doesn't fit?", "You can exchange within 72 hours of delivery. Delivery and return charges apply. See our Shipping &amp; Returns page."),
 ("Which sizes do you have?", "The Bounce series is available in EU sizes 21 to 36, suitable for roughly ages 1 to 10."),
 ("Are the shoes safe for kids?", "They are made from microfiber synthetic leather and breathable mesh, with chemical limits for REACH, phthalates and azo dyes."),
]

def faq_block():
    return '<div class="faq">' + "".join(f"<details><summary>{q}</summary><p>{a}</p></details>" for q, a in FAQ) + "</div>"

def faq_ld():
    return ('<script type="application/ld+json">' + json.dumps({"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a.replace("&amp;", "&")}} for q, a in FAQ]}) + "</script>")

# ---------- pages ----------
DISTRICTS = ['Bagerhat', 'Bandarban', 'Barguna', 'Barishal', 'Bhola', 'Bogura', 'Brahmanbaria', 'Chandpur', 'Chapainawabganj', 'Chattogram', 'Chuadanga', 'Cumilla', "Cox's-Bazar", 'Dhaka', 'Dinajpur', 'Faridpur', 'Feni', 'Gaibandha', 'Gazipur', 'Gopalganj', 'Habiganj', 'Jamalpur', 'Jashore', 'Jhalokathi', 'Jhenaidah', 'Joypurhat', 'Khagrachhari', 'Khulna', 'Kishoreganj', 'Kurigram', 'Kushtia', 'Lakshmipur', 'Lalmonirhat', 'Madaripur', 'Magura', 'Manikganj', 'Meherpur', 'Moulvibazar', 'Munshiganj', 'Mymensingh', 'Naogaon', 'Narail', 'Narayanganj', 'Narsingdi', 'Natore', 'Netrokona', 'Nilphamari', 'Noakhali', 'Pabna', 'Panchagarh', 'Patuakhali', 'Pirojpur', 'Rajbari', 'Rajshahi', 'Rangamati', 'Rangpur', 'Satkhira', 'Shariatpur', 'Sherpur', 'Sirajganj', 'Sunamganj', 'Sylhet', 'Tangail', 'Thakurgaon']

def contact_fields():
    """Customer fields shared by the store checkout and the landing pages (same names, same validation)."""
    opts = "".join(f'<option value="{d.replace("-", " ")}">{d.replace("-", " ")}</option>' for d in DISTRICTS)
    return f"""<div class="fld"><label for="f-name">Your name</label><input id="f-name" name="name" autocomplete="name" required><small class="err"></small></div>
      <div class="fld"><label for="f-phone">Mobile number</label><div class="phone"><span class="pfx"><span class="flag-bd" role="img" aria-label="Bangladesh flag"></span>+88</span><input id="f-phone" name="phone" type="tel" inputmode="numeric" autocomplete="tel-national" placeholder="01XXXXXXXXX" aria-describedby="phoneHint" required></div><small class="fine" id="phoneHint">11 digits, starting with 01</small><small class="err"></small></div>
      <div class="fld"><label for="f-email">Email <span class="opt-t">(optional)</span></label><input id="f-email" name="email" type="email" inputmode="email" autocomplete="email" placeholder="name@example.com"><small class="err"></small></div>
      <div class="fld"><label for="f-country">Country</label><div class="country"><span class="flag-bd" role="img" aria-label="Bangladesh flag"></span><input id="f-country" name="country" value="Bangladesh" readonly aria-readonly="true"></div><small class="fine">We currently deliver to Bangladesh.</small></div>
      <div class="fld"><label for="f-district">District</label><select id="f-district" name="district" autocomplete="address-level1" required><option value="">Select your district</option>{opts}</select><small class="err"></small></div>
      <div class="fld"><label for="f-addr">Full address</label><textarea id="f-addr" name="address" rows="3" autocomplete="street-address" placeholder="House, road, area, thana" required></textarea><small class="err"></small></div>
      <fieldset class="fld"><legend>Delivery area</legend>
        <div class="opts"><label class="opt"><input type="radio" name="area" value="dhaka" checked><span><b>Inside Dhaka</b><em id="chD"></em></span></label>
        <label class="opt"><input type="radio" name="area" value="outside"><span><b>Outside Dhaka</b><em id="chO"></em></span></label></div></fieldset>"""

def simple_page(fname, title, desc, key, eyebrow, h1, body):
    h = head(f"{title} — Babyglee", desc, key) + header(key)
    h += f'<section class="page-hero"><div class="wrap"><span class="eyebrow">{eyebrow}</span><h1>{h1}</h1></div></section><section class="sec"><div class="wrap narrow prose">{body}</div></section>'
    write(fname, h + footer())

def page_shipping():
    body = '''<p class="fine">Last updated: 2025</p>
<h2>Shipping destination</h2><p>Babyglee is an international brand, and we currently ship to <b>Bangladesh</b>. Prices are in Bangladeshi taka (৳ BDT).</p>
<h2>Delivery</h2><p>We deliver to your home across the areas we serve in Bangladesh. After you place an order, our team contacts you by call or message to confirm your child's size and your delivery address, and then ships the parcel.</p>
<ul><li>Inside Dhaka and outside Dhaka delivery charges are shown at checkout before you confirm.</li><li>Delivery usually takes a few working days depending on your location.</li><li>Please keep your phone available so the courier can reach you.</li></ul>
<h2>Payment</h2><p>Cash on Delivery is available on all orders: you pay the courier when you receive your parcel. Please check the parcel before paying.</p>
<h2>Exchange</h2><p>If the size doesn't fit, you can request an exchange within <b>72 hours</b> of delivery.</p>
<ul><li>Shoes must be unused, clean and in their original packaging.</li><li>Delivery and return charges apply to exchanges.</li><li>Contact us by WhatsApp or phone with your order details to start an exchange.</li></ul>
<h2>Damaged or wrong item</h2><p>If your parcel arrives damaged or with the wrong item, contact us within 72 hours with photos and your order details, and we will make it right.</p>
<h2>Contact</h2><p>WhatsApp / phone: +880 1974-974973 · Email: info@babygleebd.com</p>'''
    simple_page("shipping-returns.html", "Shipping & Returns", "Babyglee delivery, Cash on Delivery and 72-hour exchange policy.", "shipping", "Policy", "Shipping to Bangladesh", body)

def page_privacy():
    body = '''<p class="fine">Last updated: 2025</p>
<p>This policy explains how Babyglee ("we", "us") collects and uses your information when you visit babygleebd.com or place an order.</p>
<h2>Information we collect</h2><ul><li><b>Order details:</b> your name, mobile number, delivery address, chosen product, size and quantity.</li><li><b>Unfinished orders:</b> if you start filling in the checkout form but do not finish, we may save the details you entered (such as your mobile number and chosen product) and contact you to help complete your order.</li><li><b>Messages:</b> anything you send us by WhatsApp, phone or email.</li><li><b>Usage data:</b> basic, anonymous information about how the site is used (pages visited, device type), which may be collected through cookies and analytics or advertising tools such as Meta Pixel.</li></ul>
<h2>How we use it</h2><ul><li>To confirm, deliver and support your order, including calling or messaging you about size and delivery.</li><li>To handle exchanges and customer service requests.</li><li>To understand how our site and ads perform and to improve them.</li></ul>
<h2>Sharing</h2><p>We share your name, phone number and address only with courier and delivery partners so your parcel can reach you. We do not sell your personal information.</p>
<h2>Cookies &amp; advertising</h2><p>We may use cookies and similar technologies, including the Meta Pixel, to measure ad performance and show relevant ads. You can control cookies in your browser settings.</p>
<h2>Data retention &amp; security</h2><p>We keep order information for as long as needed to fulfil your order and meet legal and accounting requirements. We take reasonable steps to protect your information.</p>
<h2>Your choices</h2><p>You may ask us to access, correct or delete your personal information by contacting us. We will respond as soon as we reasonably can.</p>
<h2>Children</h2><p>Our products are for children, but our website is intended for parents and guardians. We do not knowingly collect information from children.</p>
<h2>Contact</h2><p>Babyglee, Pallabi, Mirpur 12, Dhaka · info@babygleebd.com · +880 1974-974973</p>'''
    simple_page("privacy.html", "Privacy Policy", "How Babyglee collects, uses and protects your information.", "privacy", "Policy", "Privacy policy", body)

def page_terms():
    body = '''<p class="fine">Last updated: 2025</p>
<h2>Using this website</h2><p>By using babygleebd.com or placing an order, you agree to these terms. Please read them with our Privacy Policy and Shipping &amp; Returns policy.</p>
<h2>Products &amp; prices</h2><p>We try to show colours and details accurately, but screens differ slightly. Prices are in Bangladeshi Taka (BDT) and may change without notice. The price shown at the time you place your order applies. USD prices are shown for reference only; orders are charged in BDT.</p>
<h2>Orders</h2><ul><li>An order is confirmed after our team contacts you to verify your details and size.</li><li>We may cancel an order if details cannot be verified or an item is unavailable.</li><li>Please provide a correct phone number and address so delivery is not delayed.</li></ul>
<h2>Payment</h2><p>Payment is by Cash on Delivery unless we tell you otherwise.</p>
<h2>Exchanges</h2><p>Exchanges are handled under our <a href="shipping-returns.html">Shipping &amp; Returns</a> policy (72 hours from delivery; delivery and return charges apply).</p>
<h2>Intellectual property</h2><p>Babyglee® is a registered trademark in Bangladesh (Reg. No. 210926, Class 25). Website content, images and designs belong to Babyglee and may not be copied without permission.</p>
<h2>Liability</h2><p>To the extent permitted by law, we are not liable for indirect or consequential loss arising from use of this website or our products. Nothing limits your rights under applicable consumer law.</p>
<h2>Governing law</h2><p>These terms are governed by the laws of Bangladesh.</p>
<h2>Contact</h2><p>Babyglee, Pallabi, Mirpur 12, Dhaka · info@babygleebd.com · +880 1974-974973</p>'''
    simple_page("terms.html", "Terms & Conditions", "Terms and conditions for using the Babyglee website and placing orders.", "terms", "Policy", "Terms &amp; conditions", body)


# ======================================================================= landing site
TRUST_ITEMS = TRUST

def header(active="landing"):
    landing = active == "landing"
    links = ('<a href="#shop">Shop</a><a href="#why">Why Babyglee</a><a href="#size">Size guide</a><a href="#reviews" id="navReviews" hidden>Reviews</a><a href="#faq">FAQ</a>'
             if landing else '<a href="index.html#shop">Shop</a><a href="index.html#why">Why Babyglee</a><a href="index.html#faq">FAQ</a>')
    return f"""<div class="topbar"><div class="wrap"><span>{ic("pin")} Shipping to Bangladesh</span><span>Designed for European markets</span><span>{ic("cash")} Cash on Delivery</span><span>{ic("exchange")} 72-hour exchange</span></div></div>
<header class="hdr"><div class="wrap hdr-in">
  <a class="brand" href="index.html" aria-label="Babyglee home"><img src="img/logo.webp" alt="Babyglee — Because we love them!" width="117" height="87"></a>
  <nav class="nav" id="nav" aria-label="Main">{links}<a class="btn sm nav-cta" href="{'#shop' if landing else 'index.html#shop'}">Shop now</a></nav>
  <div class="ship" id="ship">
    <button class="ship-btn" id="shipBtn" aria-expanded="false" aria-controls="shipMenu"><span class="flag-bd" role="img" aria-label="Bangladesh flag"></span><span class="ship-t"><small>Shipping to</small>Bangladesh<span class="cur"> · ৳ BDT</span></span><svg class="ic chev" aria-hidden="true"><use href="#i-chev"/></svg></button>
    <div class="ship-menu" id="shipMenu" hidden>
      <p class="sm-h">Shipping destination</p>
      <div class="sm-opt on"><span class="flag-bd" role="img" aria-label="Bangladesh flag"></span><b>Bangladesh</b>{ic("check")}</div>
      <p class="sm-n">Prices are in Bangladeshi taka (৳ BDT). The international price in USD is shown for reference.</p>
      <ul class="sm-l"><li>{ic("truck")} Home delivery</li><li>{ic("cash")} Cash on Delivery</li><li>{ic("exchange")} 72-hour exchange</li></ul>
    </div>
  </div>
  <a class="cart-btn" href="checkout.html" aria-label="Cart and checkout">{ic("bag")}<i class="js-cart-count">0</i></a>
  <button class="burger" id="burger" aria-label="Open menu" aria-expanded="false">{ic("menu")}</button>
</div></header>
<main>
"""

def footer(landing=False):
    sheets = f"""<div class="sheet-wrap" id="sizeModal" hidden>
  <div class="sheet-scrim" data-close></div>
  <section class="sheet" role="dialog" aria-modal="true" aria-labelledby="szTitle">
    <header><h3 id="szTitle">Find the right size</h3><button class="icon-btn" type="button" data-close aria-label="Close size guide">{ic("close")}</button></header>
    <div class="sheet-body">
      <h4 class="sheet-h first">How to measure</h4>
      {finder("sz", True)}
      <h4 class="sheet-h">All sizes</h4>
      {size_table()}
    </div>
  </section>
</div>
<div class="sheet-wrap" id="cartSheet" hidden>
  <div class="sheet-scrim" data-close></div>
  <section class="sheet cart-sheet" role="dialog" aria-modal="true" aria-labelledby="csTitle">
    <header><h3 id="csTitle">Your cart</h3><button class="icon-btn" type="button" data-close aria-label="Close cart">{ic("close")}</button></header>
    <div class="sheet-body"><div id="csLines"></div>
      <div class="cs-empty" id="csEmpty" hidden><p>Your cart is empty.</p><button class="btn" type="button" data-close>Choose your pair</button></div></div>
    <div class="cs-foot" id="csFoot"><div class="cs-tot"><span id="csCount">0 pairs</span><b id="csTotal">৳0</b></div><a class="btn block" id="csGo" href="checkout.html">Checkout</a><small>Delivery charge is added at checkout. Pay on delivery.</small></div>
  </section>
</div>
<div class="sheet-wrap" id="shotBox" hidden>
  <div class="sheet-scrim" data-close></div>
  <section class="sheet shot" role="dialog" aria-modal="true" aria-label="Customer review">
    <header><h3>Customer review</h3><button class="icon-btn" type="button" data-close aria-label="Close">{ic("close")}</button></header>
    <div class="sheet-body"><img id="shotImg" src="img/logo.webp" alt="Customer review screenshot"></div>
  </section>
</div>
""" if landing else ""
    cartfab = f"""<div class="cartbar" id="cartBar" hidden><button class="cb-view" id="cbView" type="button" aria-label="View cart">{ic("bag")}<i class="js-cart-count">0</i></button><a class="btn" id="cbGo" href="checkout.html">Checkout</a></div>
""" if landing else ""
    return f"""</main>
<footer class="ftr">
  <div class="wrap ftr-grid">
    <div class="ftr-brand">
      <img src="img/logo.webp" alt="Babyglee" width="117" height="87">
      <p>An international kids' sneaker brand, designed for European markets and now shipping to Bangladesh.</p>
      <div class="soc"><a href="https://facebook.com/Babyglee.Official" target="_blank" rel="noopener" aria-label="Babyglee on Facebook">{ic("facebook")}</a>
      <a href="https://wa.me/{WA}" target="_blank" rel="noopener" aria-label="WhatsApp">{ic("whatsapp")}</a></div>
    </div>
    <div><h4>Shop</h4><a href="index.html#shop">The Bounce series</a><a href="index.html#size">Size guide</a><a href="index.html#faq">FAQ</a></div>
    <div><h4>Company</h4><a href="shipping-returns.html">Shipping &amp; returns</a><a href="privacy.html">Privacy policy</a><a href="terms.html">Terms &amp; conditions</a></div>
    <div class="ftr-contact"><h4>Get in touch</h4>
      <a href="https://wa.me/{WA}">{ic("whatsapp")} {PHONE_DISPLAY}</a>
      <a href="mailto:info@babygleebd.com">{ic("mail")} info@babygleebd.com</a>
      <span class="ln">{ic("pin")} Dhaka office: Pallabi, Mirpur 12</span>
      <span class="ln">{ic("pin")} EU office: Pontedera, Italy</span>
      <span class="ln">{ic("clock")} 9 AM – 7 PM (BST)</span></div>
  </div>
  <div class="wrap ftr-bottom"><span>© 2025 Babyglee® — A concern of AMC Knit Composite Ltd.</span><span>Trademark Reg. No. 210926 (Class 25) · Trade licence TRAD/DNCC/090476/2022</span></div>
</footer>
<a class="fab fab-wa" id="waFab" href="https://wa.me/{WA}" target="_blank" rel="noopener" aria-label="Chat with us on WhatsApp">{ic("whatsapp")}</a>
{cartfab}{sheets}<div class="toast" id="toast" role="status"></div>
<script src="assets/main.js"></script>
</body>
</html>
"""

FAQ = [
 ("How do I order?", "Choose a size for each colour you like, add them to your cart, then check out once with your delivery details. We call you to confirm your sizes and delivery before shipping."),
 ("Can I buy more than one pair or more than one colour?", "Yes. Add as many pairs, colours and sizes as you like to the cart and pay for them in a single checkout."),
 ("Can I pay on delivery?", "Yes. Cash on Delivery is available on every order. You pay in taka when your parcel arrives."),
 ("What if the size doesn't fit?", "You can exchange within 72 hours of delivery. Delivery and return charges apply. See our Shipping &amp; Returns page."),
 ("Which sizes do you have?", "The Bounce series comes in EU sizes 21 to 36, suitable for roughly ages 1 to 10. Use the size guide to match your child's foot length."),
 ("Are the shoes safe for kids?", "They are made from microfiber synthetic leather and breathable mesh, with chemical limits for REACH, phthalates and azo dyes."),
 ("Where do you deliver?", "We currently deliver to homes across Bangladesh, inside and outside Dhaka."),
]

def page_index():
    h = head("Babyglee — International Kids' Sneakers, Shipping to Bangladesh", "International kids' sneaker brand designed for European markets, now shipping to Bangladesh. Five colours, EU sizes 21–36, Cash on Delivery and 72-hour exchange.", "landing", extra=faq_ld())
    h += header("landing")
    steps = [("1", "Choose", "Pick your colours and sizes."), ("2", "Check out", "Enter your details once. Pay on delivery."), ("3", "We deliver", "We call to confirm, then deliver to your door.")]
    h += f"""<section class="hero" id="top">
  <div class="blob b1"></div><div class="blob b2"></div>
  <div class="wrap hero-in">
    <div class="hero-copy">
      <span class="pill">International brand · Shipping to Bangladesh</span>
      <h1>Happy feet.<br><span class="grad">Bouncy steps.</span></h1>
      <p class="lead">Kids' sneakers designed for European markets and now shipping to Bangladesh: memory-foam insole, wide toe box and an anti-slip sole that parents can trust.</p>
      <div class="cta"><a class="btn lg" href="#shop">Choose your pair</a><button class="btn lg ghost" type="button" data-open-size>Find my kid's size</button></div>
      <div class="price-tag"><s>{fmt(LIST)}</s><b>{fmt(PRICE)}</b><span>Cash on Delivery</span></div>
      <p class="usd-note">International price: <b>US${PRICE_USD}</b></p>
    </div>
    <div class="stage" id="stage">
      <div class="disc"></div>
      <img class="shoe s-main" data-depth="46" src="img/sky-blue-yellow.webp" alt="Babyglee Bounce sneakers in sky blue and yellow" fetchpriority="high">
      <img class="shoe s-side" data-depth="80" src="img/grey.webp" alt="Babyglee Bounce sneakers in grey" loading="lazy">
      <div class="chip c1">{ic("bolt")} Fast-lock strap</div>
      <div class="chip c2">{ic("cushion")} Memory-foam insole</div>
    </div>
  </div>
</section>
{trust_strip()}
<section class="sec" id="shop"><div class="wrap">
  <div class="sec-head"><span class="eyebrow">The Bounce series</span><h2>Pick your pairs</h2><p>Choose a size for each colour you like and add it to your cart. Add as many pairs as you want, then check out once.</p></div>
  <div class="pgrid" id="grid" data-list="landing"><p class="empty-note">Loading the collection…</p></div>
  <noscript><p class="empty-note">Please turn on JavaScript to choose your pairs, or order on WhatsApp.</p></noscript>
</div></section>
<section class="sec alt" id="why"><div class="wrap">
  <div class="sec-head"><span class="eyebrow">Why parents choose Babyglee</span><h2>Built around growing feet</h2><p>Little feet are busy feet. They run, climb, jump and grow fast, so the right sneaker needs room to move, grip on every surface and cushioning that keeps them comfortable all day.</p></div>
  {feature_cards()}
</div></section>
<section class="sec" id="anatomy"><div class="wrap">
  <div class="sec-head"><span class="eyebrow">Inside every Bounce</span><h2>The details that matter</h2><p>Tap a number to see what each part does.</p></div>
  <div class="anat">
    <div class="anat-img"><img src="img/blue-beige.webp" alt="Babyglee Bounce sneaker in blue and beige" loading="lazy">
      <button class="hs" style="left:58%;top:30%" data-i="0" aria-label="Fast-lock strap">1</button><button class="hs" style="left:20%;top:58%" data-i="1" aria-label="Breathable upper">2</button>
      <button class="hs" style="left:74%;top:24%" data-i="2" aria-label="Memory-foam insole">3</button><button class="hs" style="left:50%;top:82%" data-i="3" aria-label="Anti-slip sole">4</button></div>
    <ol class="anat-list">
      <li data-i="0"><span class="n">1</span><div><b>Fast-lock strap</b><p>A velcro strap with stretch bands, so kids can put their shoes on by themselves.</p></div></li>
      <li data-i="1"><span class="n">2</span><div><b>Breathable upper</b><p>Soft microfiber synthetic leather with breathable mesh keeps feet comfortable.</p></div></li>
      <li data-i="2"><span class="n">3</span><div><b>Memory-foam insole</b><p>A cushioned insole and a wide toe box leave room for natural foot movement.</p></div></li>
      <li data-i="3"><span class="n">4</span><div><b>Anti-slip, shock-absorbing sole</b><p>A multi-density rubber sole grips playgrounds and courts and softens every step.</p></div></li>
    </ol>
  </div>
</div></section>
<section class="sec alt" id="size"><div class="wrap size-box">
  <div>
    <span class="eyebrow">Size guide</span><h2>Find the right size in seconds</h2>
    {finder("fs")}
  </div>
  <div class="size-tbl">{size_table()}</div>
</div></section>
<section class="sec" id="reviews" hidden><div class="wrap">
  <div class="sec-head"><span class="eyebrow">Reviews</span><h2>What parents say</h2><p id="rvSum"></p></div>
  <div class="rv-track" id="rvTrack"></div>
</div></section>
<section class="sec alt" id="how"><div class="wrap">
  <div class="sec-head"><span class="eyebrow">How it works</span><h2>Order in three steps</h2></div>
  <div class="steps3">{"".join(f'<div class="st3 tilt"><span class="n">{n}</span><h3>{t}</h3><p>{d}</p></div>' for n, t, d in steps)}</div>
  <p class="center fine">{ic("exchange")} Wrong size? Exchange within 72 hours of delivery (delivery and return charges apply).</p>
</div></section>
<section class="sec" id="faq"><div class="wrap narrow"><div class="sec-head"><span class="eyebrow">FAQ</span><h2>Quick answers</h2></div>{faq_block()}</div></section>
<section class="cta-band"><div class="wrap"><h2>Ready to bounce?</h2><p>Free to look, easy to order, pay when it arrives.</p>
  <div class="cta center"><a class="btn lg" href="#shop">Choose your pair</a><a class="btn lg wa" href="https://wa.me/{WA}" target="_blank" rel="noopener">{ic("whatsapp")} Ask on WhatsApp</a></div></div></section>
"""
    h += footer(landing=True)
    write("index.html", h)

def page_checkout():
    h = head("Checkout — Babyglee", "Checkout: delivering to Bangladesh, Cash on Delivery.", "checkout", extra='<meta name="robots" content="noindex">')
    h += header("checkout")
    h += f"""<section class="page-hero slim"><div class="wrap"><ol class="progress" aria-label="Progress"><li class="done">{ic("check")} Choose</li><li class="on">2 Checkout</li><li>3 Done</li></ol><h1>Checkout</h1><p>Delivering to Bangladesh · Pay in BDT on delivery</p></div></section>
<section class="sec"><div class="wrap narrow-lg">
  <div class="empty-state" id="coEmpty" hidden><span class="okc">{ic("bag")}</span><h3>Your cart is empty</h3><p>Choose your pairs first, then come back to check out.</p><a class="btn" href="index.html#shop">Choose your pair</a></div>
  <div class="co-grid" id="coGrid">
    <form id="coForm" class="co-form" novalidate>
      <h3 class="sum-t">Delivery details</h3>
      {contact_fields()}
      <fieldset class="fld"><legend>Payment</legend><div class="opt on-static"><span><b>Cash on Delivery</b><em>Pay in BDT when your parcel arrives</em></span></div></fieldset>
      <p class="err-box" id="sendErr" role="alert" hidden>Sorry, we couldn't place your order. Please check your connection and try again, or call us on {PHONE_DISPLAY}.</p>
      <div class="co-submit"><button class="btn lg block" type="submit" id="submitBtn">Place order</button></div>
      <p class="fine center">{ic("shield")} Your details are used only to deliver your order.</p>
    </form>
    <aside class="summary" aria-label="Order summary"><details class="sum-d" id="sumD" open>
      <summary class="sum-t"><span>Order summary</span><b id="sumTop"></b></summary>
      <div id="coLines"></div>
      <dl><div><dt>Subtotal</dt><dd id="sSub"></dd></div><div><dt>Delivery</dt><dd id="sDel"></dd></div><div class="tot"><dt>Total (COD)</dt><dd id="sTot"></dd></div></dl>
      <p class="fine"><a class="lnk-b" href="index.html#shop">← Add more pairs</a> · <a class="lnk-b" href="https://wa.me/{WA}" target="_blank" rel="noopener">Chat on WhatsApp</a></p>
    </details></aside>
  </div>
</div></section>
"""
    h += footer()
    write("checkout.html", h)

def page_thanks():
    h = head("Thank you — Babyglee", "Your Babyglee order has been placed.", "thanks", extra='<meta name="robots" content="noindex">')
    h += header("thanks")
    h += f"""<section class="sec"><div class="wrap narrow">
  <div class="done" id="done" hidden>
    <span class="okc">{ic("check")}</span><h1>Thank you! Your order is placed.</h1>
    <p>Order ID <b id="oid"></b></p>
    <dl class="recap"><div><dt>Items</dt><dd><ul class="ritems" id="rItems"></ul></dd></div><div><dt>Deliver to</dt><dd id="rA"></dd></div><div class="tot"><dt>Pay on delivery</dt><dd id="rT"></dd></div></dl>
    <ol class="next"><li><b>We call you</b><span>Our team calls <b id="rPh"></b> to confirm your sizes and address.</span></li><li><b>We deliver</b><span>Your parcel is sent to your door.</span></li><li><b>You pay</b><span>Cash on Delivery, in taka, when it arrives.</span></li></ol>
    <p class="demo" id="demoNote" hidden>Demo mode: ordering is not connected yet, so this order was not sent to the Babyglee team.</p>
    <p class="fine">Need help? <a href="https://wa.me/{WA}" target="_blank" rel="noopener">Chat on WhatsApp</a> or call {PHONE_DISPLAY}. Wrong size? Exchange within 72 hours.</p>
    <a class="btn ghost" href="index.html#shop">Order another pair</a>
  </div>
  <div class="empty-state" id="noOrder" hidden><span class="okc">{ic("bag")}</span><h3>No recent order found</h3><p>If you just placed an order, our team will call you. Otherwise you can choose your pairs here.</p><a class="btn" href="index.html#shop">Choose your pair</a></div>
</div></section>
"""
    h += footer()
    write("thank-you.html", h)

def write_data_files():
    data = {p["slug"]: {"title": f"Babyglee Bounce — {p['name']}", "name": p["name"], "img": f"img/{p['img']}.webp", "images": [f"img/{p['img']}.webp"], "url": "#shop", "sku": "BSTD-01-" + p["key"].upper(),
            "color": p["name"], "colorHex": p["color"], "price": PRICE, "listPrice": LIST, "priceUsd": PRICE_USD, "sizes": list(range(21, 37)), "out": [], "low": {}} for p in PRODUCTS}
    (OUT / "assets" / "products.js").write_text("/* generated by tools/build.py (static fallback; with the backend this file is served from the database) */\nwindow.BG_PRODUCTS = " + json.dumps(data, ensure_ascii=False, indent=1) + ";\n", encoding="utf-8")
    (OUT / "assets" / "reviews.js").write_text("/* static fallback; with the backend this file is served from the database (Admin > Reviews) */\nwindow.BG_REVIEWS = [];\n", encoding="utf-8")

if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    page_index(); page_checkout(); page_thanks(); page_shipping(); page_privacy(); page_terms()
    write_data_files()
    print("built", len(list(OUT.glob("*.html"))), "pages")
