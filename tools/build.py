#!/usr/bin/env python3
"""Generates the Babyglee landing site (index, checkout, thank-you, policies) into the repo root: python3 tools/build.py"""
import hashlib, json, pathlib, re

OUT = pathlib.Path(__file__).resolve().parent.parent
BASE = "https://dmxasif-commits.github.io/babyglee-landing-page/"  # change if you move to a custom domain
PRICE, LIST = 1290, 1800
PRICE_INTL = 35  # international price in euro, no discount (the field and JSON key keep the old name "priceUsd")
WA = "8801974974973"
PHONE_DISPLAY = "+880 1974-974973"
PHONE_TEL = "+8801974974973"
BKASH = "01974974973"   # bKash merchant account (Payment)
DELIVERY = "1–3 days"   # one delivery promise used everywhere (never "working days")
# Partner logos: put the files in img/partners/<file>; a partner without a file is not shown (no invented logos)
PARTNERS = [("ToguMogu", "togumogu"), ("Shishu Poribohon", "shishu-poribohon"), ("Prelegant Mall", "prelegant-mall"), ("Rokomari", "rokomari")]

PRODUCTS = [
    dict(key="sky-blue", slug="bounce-sky-blue", img="sky-blue-yellow", name="Multi Color", short="Multi Color", color="#3fb4e8"),
    dict(key="blue-beige", slug="bounce-blue-beige", img="blue-beige", name="Blue & Beige", short="Blue & Beige", color="#3d7fa5"),
    dict(key="grey", slug="bounce-grey", img="grey", name="Charcoal Grey", short="Charcoal Grey", color="#8a9096"),
    dict(key="navy-brown", slug="bounce-navy-brown", img="navy-brown", name="Dark Navy", short="Dark Navy", color="#26335a"),
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
      <p class="fine" id="{p}Note">Insole length = foot length + 1 cm. Example: a 15 cm foot needs a 16 cm (6.3 in) insole, which is EU 26.</p>
      {'<button class="btn block" type="button" id="szUse" hidden>Select this size</button>' if use else ''}"""

def size_table():
    rows = "".join(f"<tr data-eu=\"{eu}\"><td><b>EU {eu}</b></td><td>{ins-1:.1f} cm</td><td>{ins:.1f} cm<small>{ins/2.54:.1f} in</small></td><td>{age}</td></tr>" for eu, ins, age in SIZE_CHART)
    return (f'<div class="tbl-wrap"><table class="tbl"><thead><tr><th>Shoe size</th><th>Foot length</th><th>Insole (cm / in)</th><th>Age</th></tr></thead>'
            f'<tbody>{rows}</tbody></table></div>'
            '<p class="fine">Pick the size whose insole (shown in cm and inches) is your child\'s foot length + 1 cm. For wide feet or thick socks, go one size up. Our team also confirms the size with you by call or message before shipping.</p>')

# ---------- shared chrome ----------
# Browser-tab and home-screen icons come from the Babyglee logo (img/favicon*.png, img/favicon.ico, img/apple-touch-icon.png, img/icon-192.png): the "B" of the logo on a white rounded plate for
# the tab, the whole lettering with the baby for the home screen. They are linked with a content hash (asset()) because browsers keep favicons for a long time.
def icon_links():
    return (f'<link rel="icon" href="{asset("img/favicon.ico")}" sizes="any">\n'
            f'<link rel="icon" type="image/png" sizes="32x32" href="{asset("img/favicon-32.png")}">\n'
            f'<link rel="icon" type="image/png" sizes="16x16" href="{asset("img/favicon-16.png")}">\n'
            f'<link rel="apple-touch-icon" sizes="180x180" href="{asset("img/apple-touch-icon.png")}">')

def asset(path):
    """URL of a site file with a short content hash (?v=...). The server tells browsers and the CDN to keep CSS and images for 7 days; with the hash in the link a changed
    file is fetched at once by everybody. The hash is computed when the pages are built, so run `python3 tools/build.py` after every change to the CSS or JS."""
    f = OUT / path
    return f"{path}?v={hashlib.md5(f.read_bytes()).hexdigest()[:8]}" if f.exists() else path

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
{icon_links()}
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Fredoka:wght@500;600;700&family=Hind+Siliguri:wght@400;500;600;700&family=Nunito:wght@400;600;700;800&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{asset('assets/style.css')}">
<script src="assets/config.js"></script>
<script src="assets/products.js"></script>
<script src="assets/reviews.js"></script>
<script src="{asset('assets/tracking.js')}"></script>
{extra}
</head>
<body data-page="{page}">
{SPRITE}
'''

def write(name, html):
    (OUT / name).write_text(html, encoding="utf-8")

# ---------- reusable blocks ----------
def trust_strip():
    return f'<section class="trust"><div class="trust-dlv"><div class="wrap">{ic("truck")}<p>Order today, delivered in <b>{DELIVERY}</b> across Bangladesh</p></div></div></section>'

WHY = [   # (icon-free) label, text, hotspot position on the photo (None = no hotspot)
 ("Breathable Microfiber", "Keeps little feet comfortable and healthy all day long.", (20, 58)),
 ("Soft &amp; Comfortable Cushioning", "Protects growing joints during every jump and run.", (74, 24)),
 ("Easy Front-Lock Strap", "Simple for kids to fasten securely on their own.", (58, 30)),
 ("Anti-Slip Rubber Sole", "Maximum traction to prevent slips on school floors and playgrounds.", (50, 82)),
 ("Zero Toxic Chemicals", "100% safe materials tested for sensitive skin.", None),
 ("European Design", "Crafted with ergonomic standards to protect and support natural foot growth.", None),
]

def why_section():
    spots = "".join(f'<button class="hs" style="left:{x}%;top:{y}%" data-i="{n}" aria-label="{t.replace("&amp;", "and")}">{n + 1}</button>' for n, (t, d, pos) in enumerate(WHY) if pos for x, y in [pos])
    items = "".join(f'<li data-i="{n}"><span class="n">{n + 1}</span><div><b>{t}</b><p>{d}</p></div></li>' for n, (t, d, pos) in enumerate(WHY))
    return f'''<section class="sec alt" id="why"><div class="wrap">
  <div class="sec-head why-head"><span class="eyebrow">Why Babyglee®</span><h2>They’ll grow out of it anyway, why buy branded?</h2>
    <p class="why-sub"><b>This small thought quietly harms your baby's growing feet.</b></p>
    <p>Cheap, unbranded shoes use harmful glues, no engineering, and unsafe materials that can hurt their soft bones and destroy natural foot growth. At Babyglee®, we bring safe, Italian-designed support to protect your child's natural foot growth:</p></div>
  <div class="anat">
    <div class="anat-img"><img src="img/blue-beige.webp" alt="Babyglee Bounce sneaker in blue and beige" loading="lazy">{spots}</div>
    <ol class="anat-list">{items}</ol>
  </div>
</div></section>'''

FAQ = [
 ("What is Babyglee?", "Babyglee is your destination for high-quality, comfortable and stylish shoes for children aged 1 to 10 years. We focus on durable, safe and supportive footwear for all occasions."),
 ("How do I find the right shoe size?", "Use our size guide: measure your child's foot, type the length in cm and we suggest the size. The insole should be your child's foot length + 1 cm (shown in cm and inches in the size table). For wide feet or thick socks, go one size up. We also confirm the size with you by call or message before shipping."),
 ("Which sizes do you have?", "The Bounce series comes in EU sizes 21 to 36, suitable for roughly ages 1 to 10."),
 ("How do I place an order?", "Choose a size for each colour you like, add them to your cart, then check out once with your delivery details. We call you to confirm your sizes and delivery before shipping."),
 ("Where do you deliver from, and how long does it take?", f"Our head office is in Dhaka, Bangladesh, and we deliver to homes across Bangladesh, inside and outside Dhaka. Delivery takes {DELIVERY} everywhere."),
 ("What are the shipping costs?", "The delivery charge for inside Dhaka and outside Dhaka is shown at checkout before you confirm your order. Full details are on our Shipping &amp; Returns page."),
 ("Can I track my order?", "Yes. Once your order is dispatched, the courier gives you a tracking number, and you can use it on the courier's website for live updates on your delivery."),
 ("Can I pay on delivery? Which payment methods do you accept?", f"Cash on Delivery is available on every order: you pay in taka when your parcel arrives. You can also pay by bKash (merchant account {BKASH}, Payment option). Tell our team when we call to confirm your order."),
 ("What is your return and exchange policy?", "You can exchange within 72 hours of receiving your shoes, for items in original condition. Delivery and return charges apply. See our Shipping &amp; Returns page for details."),
 ("How can I contact Babyglee customer service?", f"Reach us on WhatsApp {PHONE_DISPLAY} (11 AM – 9 PM BST), on Facebook Messenger (Babyglee.Official) or by email at info@babygleebd.com. Our head office in Dhaka, Bangladesh, manages all customer enquiries."),
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
    body = f'''<h2>Shipping Policy</h2><p>At Babyglee, we ensure quick, reliable and hassle-free delivery for your child's new shoes. Prices are in Bangladeshi taka (৳ BDT).</p>
<h3>How we deliver</h3>
<ul><li><b>Fast processing:</b> orders are processed from our Dhaka, Bangladesh office within 1 business day. Our team calls or messages you to confirm your child's size and your delivery address before shipping.</li>
<li><b>Delivery time:</b> {DELIVERY} everywhere in Bangladesh, to your home.</li>
<li><b>Clear costs:</b> the delivery charge for inside Dhaka and outside Dhaka is shown at checkout before you confirm your order.</li>
<li><b>Easy tracking:</b> once your order is dispatched, the courier gives you a tracking number for live updates.</li>
<li>Please keep your phone available so the courier can reach you.</li></ul>
<h2>Payment</h2><p>Cash on Delivery is available on every order: you pay the courier when you receive your parcel. Please check the parcel before paying. You can also pay by bKash (merchant account {BKASH}, Payment option).</p>
<h2>Return &amp; Exchange Policy</h2><p>Your satisfaction is key! We make exchanges simple at Babyglee.</p>
<ul><li><b>Eligibility:</b> exchange items within 72 hours of receipt. Items must be unworn, unwashed, with all tags and in the original packaging.</li>
<li><b>How to start:</b> message us on WhatsApp or Facebook Messenger, or email info@babygleebd.com with your order number.</li>
<li><b>Charges:</b> delivery and return charges apply to exchanges, unless the error is ours.</li>
<li><b>Refunds:</b> where a refund applies, it is issued to your original payment method within 7–10 business days after inspection.</li>
<li><b>Damaged or defective:</b> contact us immediately with photos and your order details for a quick resolution.</li></ul>
<h2>Contact</h2><p>WhatsApp / phone: {PHONE_DISPLAY} (11 AM – 9 PM BST) · Email: info@babygleebd.com</p>'''
    simple_page("shipping-returns.html", "Shipping & Returns", "Babyglee delivery, payment and 72-hour exchange policy.", "shipping", "Policy", "Shipping &amp; returns policy", body)

def page_privacy():
    body = '''<p><b>Your privacy, our priority. Shop with confidence!</b></p>
<p>At Babyglee, your trust means everything. This guide explains how we handle your information so your shopping experience is secure and delightful.</p>
<h2>What we collect</h2><ul><li><b>From you:</b> your name, mobile number, delivery address and email (if you give it) for orders, the products and sizes you choose, and anything you send us by WhatsApp, phone or email.</li><li><b>Unfinished orders:</b> if you start filling in the checkout form but do not finish, we may save the details you entered (such as your mobile number and chosen product) and contact you to help complete your order.</li><li><b>Automatically:</b> how you use our site (like pages viewed and device type), through cookies and analytics or advertising tools such as Meta Pixel, to improve your experience.</li></ul>
<h2>How we use it</h2><ul><li>To process, confirm and deliver your orders, including calling or messaging you about size and delivery.</li><li>To handle exchanges and customer service requests.</li><li>To understand how our site and ads perform, and to show you shoes you will love.</li><li>To keep you updated on offers (you can opt out any time).</li><li>To ensure security and prevent fraud.</li></ul>
<h2>How we share it</h2><ul><li>With trusted partners (such as couriers and payment providers) who help us serve you. They must protect your data.</li><li>When required by law.</li></ul><p>We do not sell your personal information.</p>
<h2>Cookies &amp; advertising</h2><p>We may use cookies and similar technologies, including the Meta Pixel, to measure ad performance and show relevant ads. You can control cookies in your browser settings.</p>
<h2>You are in control</h2><ul><li>You can access, correct, delete or limit your data. Just ask us.</li><li>We use strong security measures to protect your information.</li><li>We keep your data only as long as needed to fulfil your order and meet legal and accounting requirements.</li><li>We do not knowingly collect data from children under 13. Our website is intended for parents and guardians.</li></ul>
<h2>Questions? We are happy to help</h2><p>Email: info@babygleebd.com · WhatsApp: +880 1974-974973 · Babyglee, Pallabi, Mirpur 12, Dhaka</p>'''
    simple_page("privacy.html", "Privacy Policy", "How Babyglee collects, uses and protects your information.", "privacy", "Policy", "Privacy policy", body)

def page_terms():
    body = '''<p>Welcome to Babyglee. By using our services (website, products), you agree to these Terms and our <a href="privacy.html">Privacy Policy</a>. If you do not agree, please do not use our services.</p>
<h2>Key points</h2>
<ul><li><b>Acceptance:</b> using Babyglee means you are 16+ or supervised by a guardian who agrees to these Terms. This is a binding agreement.</li>
<li><b>Services:</b> we offer children's shoes and related information. We may change or discontinue services at any time.</li>
<li><b>Conduct:</b> use our services lawfully. No harmful, fraudulent, offensive or infringing activities. Do not interfere with the site or collect data without permission.</li>
<li><b>Privacy:</b> your privacy is vital. See our Privacy Policy for details.</li>
<li><b>Intellectual property:</b> all Babyglee content is ours; do not reproduce it without permission. Babyglee® is a registered trademark in Bangladesh (Reg. No. 210926, Class 25). Content you submit grants us a licence to use it.</li></ul>
<h2>Products &amp; sales</h2>
<ul><li><b>Information:</b> we strive for accuracy (including colours, which can differ slightly on screens) but do not guarantee error-free content.</li>
<li><b>Pricing:</b> prices are in Bangladeshi Taka (BDT) and are subject to change; the price shown when you order applies. We can correct errors or cancel orders. The international price in euro is shown for reference only; orders are charged in BDT.</li>
<li><b>Orders:</b> an order is confirmed after our team contacts you to verify your details and size. Order confirmation does not guarantee acceptance; we can decline orders we cannot verify or fulfil. Please give a correct phone number and address.</li>
<li><b>Payment:</b> Cash on Delivery or bKash, as described on our <a href="shipping-returns.html">Shipping &amp; Returns</a> page.</li>
<li><b>Returns and shipping:</b> see our <a href="shipping-returns.html">Shipping &amp; Returns</a> policy (72 hours from delivery; delivery and return charges apply).</li></ul>
<h2>Disclaimers &amp; liability</h2><p>Services are provided "as is", without warranties. To the extent permitted by law, Babyglee is not liable for damages from using our services. Nothing limits your rights under applicable consumer law.</p>
<h2>Indemnification</h2><p>You agree to protect Babyglee from claims arising from your violation of these Terms or misuse of our services.</p>
<h2>Governing law</h2><p>The laws of Bangladesh govern these Terms. Disputes are resolved through negotiation or in the courts of Dhaka.</p>
<h2>Changes to these Terms</h2><p>We may update these Terms; continued use means you accept the new Terms.</p>
<h2>Contact</h2><p>Email: info@babygleebd.com · WhatsApp: +880 1974-974973 · Babyglee, Pallabi, Mirpur 12, Dhaka</p>'''
    simple_page("terms.html", "Terms & Conditions", "Terms and conditions for using the Babyglee website and placing orders.", "terms", "Policy", "Terms &amp; conditions", body)


# ======================================================================= landing site
def header(active="landing"):
    landing = active == "landing"
    links = ('<a href="#shop">Shop</a><a href="#why">Why Babyglee®</a><a href="#size">Size Guide</a><a href="#reviews" id="navReviews" hidden>Reviews</a><a href="#faq">FAQ</a>'
             if landing else '<a href="index.html#shop">Shop</a><a href="index.html#why">Why Babyglee®</a><a href="index.html#faq">FAQ</a>')
    return f"""<div class="topbar"><div class="wrap"><span>{ic("truck")} Available in Bangladesh</span><span>Designed for European markets</span><span>{ic("cash")} Cash on Delivery</span><span>{ic("exchange")} 72-Hour Easy Exchanges</span><a class="tb-tel" href="tel:{PHONE_TEL}">{ic("phone")} (+880) 1974974973</a></div></div>
<header class="hdr"><div class="wrap hdr-in">
  <a class="brand" href="index.html" aria-label="Babyglee home"><img src="img/logo.webp" alt="Babyglee — Because we love them!" width="117" height="87"></a>
  <nav class="nav" id="nav" aria-label="Main">{links}<a class="btn sm nav-cta" href="{'#shop' if landing else 'index.html#shop'}">Shop Now</a></nav>
  <div class="ship" id="ship">
    <button class="ship-btn" id="shipBtn" aria-expanded="false" aria-controls="shipMenu"><span class="flag-bd" role="img" aria-label="Bangladesh flag"></span><span class="ship-t"><small>Shipping to</small>Bangladesh<span class="cur"> · ৳ BDT</span></span><svg class="ic chev" aria-hidden="true"><use href="#i-chev"/></svg></button>
    <div class="ship-menu" id="shipMenu" hidden>
      <p class="sm-h">Shipping destination</p>
      <div class="sm-opt on"><span class="flag-bd" role="img" aria-label="Bangladesh flag"></span><b>Bangladesh</b>{ic("check")}</div>
      <p class="sm-n">Prices are in Bangladeshi taka (৳ BDT). The international price in euro is shown for reference.</p>
      <ul class="sm-l"><li>{ic("truck")} Home delivery</li><li>{ic("cash")} Cash on Delivery</li><li>{ic("exchange")} 72-hour easy exchange</li></ul>
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
<div class="sheet-wrap" id="addedPop" hidden>
  <div class="sheet-scrim" data-close></div>
  <section class="sheet added-pop" role="dialog" aria-modal="true" aria-labelledby="apTitle">
    <header><h3 id="apTitle">{ic("check")} Added to your cart</h3><button class="icon-btn" type="button" data-close aria-label="Close">{ic("close")}</button></header>
    <div class="sheet-body">
      <div class="ap-item"><img id="apImg" src="img/logo.webp" alt="" width="84" height="72"><div><b id="apName"></b><span id="apMeta"></span></div></div>
      <div class="ap-sum"><span id="apCount"></span><b id="apTotal"></b></div>
      <div class="ap-btns"><button class="btn ghost" type="button" data-close>Continue shopping</button><a class="btn" id="apGo" href="checkout.html">Checkout</a></div>
      <small class="ap-note">Delivery charge is added at checkout. {DELIVERY} delivery. Pay on delivery.</small>
    </div>
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
    cartfab = f"""<div class="cartbar" id="cartBar" hidden><a class="btn" id="cbGo" href="checkout.html">Checkout</a></div>
<button class="fab fab-cart" id="cartFab" type="button" aria-label="View cart" hidden>{ic("bag")}<i class="js-cart-count">0</i></button>
""" if landing else ""
    return f"""</main>
<footer class="ftr">
  <div class="wrap ftr-grid">
    <div class="ftr-brand">
      <img src="img/logo.webp" alt="Babyglee" width="117" height="87">
      <p>An international kids' sneaker brand, designed for European markets and available in Bangladesh.</p>
      <div class="soc"><a href="https://facebook.com/Babyglee.Official" target="_blank" rel="noopener" aria-label="Babyglee on Facebook">{ic("facebook")}</a>
      <a href="https://wa.me/{WA}" target="_blank" rel="noopener" aria-label="WhatsApp">{ic("whatsapp")}</a></div>
    </div>
    <div><h4>Customer Care</h4><a href="shipping-returns.html">Shipping &amp; returns</a><a href="index.html#faq">FAQ</a><a href="index.html#size">Size guide</a></div>
    <div><h4>Shop</h4><a href="index.html#shop">The Bounce series</a><a href="index.html#why">Why Babyglee®</a></div>
    <div><h4>Company</h4><a href="privacy.html">Privacy policy</a><a href="terms.html">Terms &amp; conditions</a></div>
    <div class="ftr-contact"><h4>Reach Us</h4>
      <a href="https://wa.me/{WA}">{ic("whatsapp")} {PHONE_DISPLAY}</a>
      <a href="mailto:info@babygleebd.com">{ic("mail")} info@babygleebd.com</a>
      <span class="ln">{ic("pin")} Dhaka office: Pallabi, Mirpur 12</span>
      <span class="ln">{ic("pin")} EU office: Pontedera, Italy</span>
      <span class="ln">{ic("clock")} 11 AM – 9 PM (BST)</span></div>
  </div>
  <div class="wrap ftr-bottom"><span>© 2025 Babyglee® — A concern of AMC Knit Composite Ltd.</span><span>Trademark Reg. No. 210926 (Class 25) · Trade licence TRAD/DNCC/090476/2022</span></div>
</footer>
<a class="fab fab-wa" id="waFab" href="https://wa.me/{WA}" target="_blank" rel="noopener" aria-label="Chat with us on WhatsApp">{ic("whatsapp")}</a>
{cartfab}{sheets}<div class="toast" id="toast" role="status"></div>
<script src="{asset('assets/main.js')}"></script>
</body>
</html>
"""

def partners_block():
    """Partner logos shown only for files that exist in img/partners/ (nothing is invented)."""
    items, copy = [], []
    for name, f in PARTNERS:
        for ext in ("svg", "webp", "png", "jpg"):
            if (OUT / "img" / "partners" / f"{f}.{ext}").exists():
                items.append(f'<li class="lg-{f}"><img src="img/partners/{f}.{ext}" alt="{name}" draggable="false"></li>')
                copy.append(f'<li class="lg-{f}"><img src="img/partners/{f}.{ext}" alt="" draggable="false"></li>'); break
    if not items: return ""
    # small strip under the reviews: one row of logos that slides from left to right, endlessly (the row is there twice so the loop has no gap;
    # the second copy is hidden from screen readers). Logos only, not links, each kept in its own proportions.
    return (f'<section class="partners" id="partners" aria-labelledby="ptTitle"><div class="wrap"><h2 id="ptTitle">Our Official Partners</h2></div>'
            f'<div class="pmarq"><div class="ptrack"><ul class="plogos">{"".join(items)}</ul><ul class="plogos" aria-hidden="true">{"".join(copy)}</ul></div></div></section>\n')

def page_index():
    h = head("Babyglee® — International Kids' Sneakers, Available in Bangladesh", "International kids' sneaker brand designed for European markets and available in Bangladesh. Five colours, EU sizes 21–36, Cash on Delivery and 72-hour easy exchange.", "landing", extra=faq_ld())
    h += header("landing")
    steps = [("1", "Choose", "Pick your favorite style and size."), ("2", "Checkout", "Enter your address with Cash on Delivery."), ("3", "Get Delivered", f"Receive your package right at your doorstep in {DELIVERY}.")]
    h += f"""<section class="hero" id="top">
  <div class="blob b1"></div><div class="blob b2"></div>
  <div class="wrap hero-in">
    <div class="hero-copy">
      <h1>Designed for active,<br><span class="grad">healthy feet development.</span></h1>
      <p class="lead">Many kids wear generic sneakers that harm their developing feet. Babyglee® offers premium sneakers at an accessible price so your child can play comfortably and grow healthy.</p>
      <div class="cta"><a class="btn lg" href="#shop">Choose your pair</a><button class="btn lg ghost" type="button" data-open-size>Find my kid's size</button></div>
      <div class="price-tag"><s>{fmt(LIST)}</s><b>{fmt(PRICE)}</b><span>(Cash on Delivery)</span></div>
      <p class="usd-note">International price: <b>€{PRICE_INTL}</b></p>
    </div>
    <div class="stage" id="stage">
      <div class="disc"></div>
      <img class="shoe s-main" data-depth="46" src="img/sky-blue-yellow.webp" alt="Babyglee Bounce sneakers in sky blue and yellow" fetchpriority="high">
      <img class="shoe s-side" data-depth="80" src="img/grey.webp" alt="Babyglee Bounce sneakers in grey" loading="lazy">
      <div class="chip c1">{ic("bolt")} Fast-lock strap</div>
      <div class="chip c2">{ic("cushion")} Soft cushioning</div>
    </div>
  </div>
</section>
{trust_strip()}
<section class="sec" id="shop"><div class="wrap">
  <div class="sec-head"><span class="eyebrow">The Bounce series</span><h2>Pick your pairs</h2><p>Choose your size, fill your cart, and check out all at once.</p></div>
  <div class="pgrid" id="grid" data-list="landing"><p class="empty-note">Loading the collection…</p></div>
  <noscript><p class="empty-note">Please turn on JavaScript to choose your pairs, or order on WhatsApp.</p></noscript>
</div></section>
{why_section()}
<section class="sec alt" id="size"><div class="wrap size-box">
  <div>
    <span class="eyebrow">Size Guide</span><h2>Find the right size in seconds</h2>
    {finder("fs")}
  </div>
  <div class="size-tbl">{size_table()}</div>
</div></section>
<section class="sec" id="reviews" hidden><div class="wrap">
  <div class="sec-head"><span class="eyebrow">Reviews</span><h2>What parents say</h2><p id="rvSum"></p></div>
  <div class="rv-track" id="rvTrack"></div>
</div></section>
{partners_block()}<section class="sec alt" id="how"><div class="wrap">
  <div class="sec-head"><span class="eyebrow">How it works</span><h2>Three-Step Order Process</h2></div>
  <div class="steps3">{"".join(f'<div class="st3 tilt"><span class="n">{n}</span><h3>{t}</h3><p>{d}</p></div>' for n, t, d in steps)}</div>
  <p class="center fine pay-line">{ic("cash")} Pay your way: Cash on Delivery · bKash (merchant {BKASH})</p>
  <p class="center fine">{ic("exchange")} Wrong size? Easy exchange within 72 hours of delivery (delivery and return charges apply).</p>
</div></section>
<section class="sec" id="faq"><div class="wrap narrow"><div class="sec-head"><span class="eyebrow">FAQ</span><h2>Got Questions? We've Got Answers.</h2></div>{faq_block()}</div></section>
<section class="cta-band"><div class="wrap"><h2>Ready for Healthy Growing Feet?</h2><p>Shop our European-standard ergonomic sneakers today.</p>
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
      <fieldset class="fld"><legend>Payment</legend><div class="opt on-static"><span><b>Cash on Delivery</b><em>Pay in BDT when your parcel arrives</em></span></div>
        <p class="fine pay-more">Prefer to pay online? bKash: merchant account <b>{BKASH}</b> (Payment option). Tell our team when we call to confirm your order.</p></fieldset>
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
    <ol class="next"><li><b>We call you</b><span>Our team calls <b id="rPh"></b> to confirm your sizes and address.</span></li><li><b>We deliver</b><span>Your parcel reaches your door in {DELIVERY}.</span></li><li><b>You pay</b><span>Cash on Delivery, in taka, when it arrives.</span></li></ol>
    <p class="demo" id="demoNote" hidden>Demo mode: ordering is not connected yet, so this order was not sent to the Babyglee team.</p>
    <p class="fine">Need help? <a href="https://wa.me/{WA}" target="_blank" rel="noopener">Chat on WhatsApp</a> or call {PHONE_DISPLAY}. Wrong size? Easy exchange within 72 hours.</p>
    <a class="btn ghost" href="index.html#shop">Order another pair</a>
  </div>
  <div class="empty-state" id="noOrder" hidden><span class="okc">{ic("bag")}</span><h3>No recent order found</h3><p>If you just placed an order, our team will call you. Otherwise you can choose your pairs here.</p><a class="btn" href="index.html#shop">Choose your pair</a></div>
</div></section>
"""
    h += footer()
    write("thank-you.html", h)

def write_data_files():
    data = {p["slug"]: {"title": f"Sneaker – {p['name']}", "name": p["name"], "img": f"img/{p['img']}.webp", "images": [f"img/{p['img']}.webp"], "url": "#shop", "sku": "BSTD-01-" + p["key"].upper(),
            "color": p["name"], "colorHex": p["color"], "price": PRICE, "listPrice": LIST, "priceUsd": PRICE_INTL, "sizes": list(range(21, 37)), "out": [], "low": {}} for p in PRODUCTS}
    (OUT / "assets" / "products.js").write_text("/* generated by tools/build.py (static fallback; with the backend this file is served from the database) */\nwindow.BG_PRODUCTS = " + json.dumps(data, ensure_ascii=False, indent=1) + ";\n", encoding="utf-8")
    (OUT / "assets" / "reviews.js").write_text("/* static fallback; with the backend this file is served from the database (Admin > Reviews) */\nwindow.BG_REVIEWS = [];\n", encoding="utf-8")

if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    page_index(); page_checkout(); page_thanks(); page_shipping(); page_privacy(); page_terms()
    write_data_files()
    print("built", len(list(OUT.glob("*.html"))), "pages")
