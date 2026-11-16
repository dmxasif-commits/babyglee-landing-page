# Put the site on your hosting and keep it updated from GitHub

This guide is for cPanel hosting with a subdomain on Cloudflare. Everything you merge on GitHub goes live by itself within about 5 minutes. The database, `api/config.php` and uploaded photos stay on the server and are never overwritten.

```
GitHub (main)  --git pull every 5 min-->  ~/repositories/babyglee-landing-page  --tools/deploy.sh-->  the subdomain's web folder
```

## 1. Cloudflare DNS and SSL

1. Cloudflare → DNS: an **A** record for the subdomain (for example `shop`) pointing to the hosting server's IP (cPanel shows it on the right side of the main page, "Shared IP Address").
2. The orange cloud (proxy) can stay on. The site reads the visitor's real IP from Cloudflare's `CF-Connecting-IP` header, but only for requests that really come from Cloudflare addresses (`api/lib.php`, list from cloudflare.com/ips).
3. SSL: in cPanel → *SSL/TLS Status* run **AutoSSL** for the subdomain. Then Cloudflare → SSL/TLS → set the mode to **Full (strict)**. If AutoSSL cannot validate while the proxy is on, set the DNS record to *DNS only* (grey cloud), run AutoSSL, then turn the proxy back on.
4. Cloudflare → SSL/TLS → Edge Certificates → **Always Use HTTPS** on. Speed → Optimization: **Rocket Loader off** (it breaks tracking scripts). Do not turn on HTML minify.
5. Optional: Rules → Cache Rules → *Bypass cache* for paths starting with `/api/` and `/admin/`. (The live settings files send their own 60-second cache time, so this is only for tidiness.)

## 2. cPanel: PHP and database

1. *MultiPHP Manager*: set the subdomain to **PHP 8.1 or newer** (7.4 is the minimum). Make sure the extensions `pdo_mysql`, `curl`, `mbstring` and `openssl` are on (*MultiPHP INI Editor* or *Select PHP Version*).
2. *MySQL® Database Wizard*: create a database and a user with a strong password, give the user **All privileges**. Write down the three names and the password.

## 3. Connect GitHub (cPanel Git Version Control)

1. cPanel → **Git™ Version Control** → *Create*. Turn *Clone a Repository* on.
   - Clone URL: `https://github.com/dmxasif-commits/babyglee-landing-page.git` (the repository is public, so no key is needed)
   - Repository Path: `repositories/babyglee-landing-page` (outside `public_html`)
2. Tell the deploy script where the site's web folder is. cPanel → *Domains* → note the **Document Root** of the subdomain (for example `/home/cpaneluser/shop.example.com`). In *File Manager* → Home directory (settings: show hidden files) → *New File* named `.babyglee-deploy-path` containing that one line.
3. First deploy: Git Version Control → *Manage* → *Pull or Deploy* → **Deploy HEAD Commit** (it runs `.cpanel.yml`, which runs `tools/deploy.sh`). Or in cPanel *Terminal*:
   ```bash
   cd ~/repositories/babyglee-landing-page && bash tools/deploy.sh
   ```
4. Create the private config. In File Manager open the web folder → `api/` → copy `config.sample.php` to **`config.php`** and fill in the database name, user, password, a long random `setup_key` and, optionally, a long random `cron_key`. This file is never in GitHub and the deploy never touches it.

## 4. Automatic updates

cPanel → **Cron Jobs** → add (every 5 minutes):

```bash
cd $HOME/repositories/babyglee-landing-page && git pull --ff-only -q origin main && bash tools/deploy.sh > /dev/null 2>&1
```

If you set a `cron_key`, add a second job (also every 5 minutes) for retrying failed Purchase deliveries:

```bash
curl -s "https://shop.example.com/api/retry.php?key=YOUR_CRON_KEY" > /dev/null
```

From now on: merge on GitHub → live within 5 minutes. To update at once: Git Version Control → *Manage* → *Update from Remote*, then *Deploy HEAD Commit*.

## 5. First check

1. `https://shop.example.com/` opens the site, `…/checkout.html` and `…/thank-you.html` open.
2. `https://shop.example.com/assets/config.js` must start with `/* live from database */`. If you see the static file, `.htaccess` was not deployed or `mod_rewrite` is off (ask the host).
3. `https://shop.example.com/api/config.php` and `…/tools/` must answer "Forbidden".
4. Open `https://shop.example.com/admin/` the first time: type the `setup_key`, a username (your email address works) and a password of 10+ characters. Then follow `docs/backend-setup.md` (GTM ID, delivery charges, WhatsApp, products, reviews).
5. Place a test order on your phone. In Admin → Orders the **IP** on the order page must be a normal visitor address, not one that starts with 104., 172.64–71., 162.158/159., 141.101., 108.162., 188.114., 190.93., 197.234. or 198.41. (those are Cloudflare). If it is a Cloudflare address, tell me.

## Things to know

- **Do not edit files on the server.** The next deploy overwrites `index.html`, `assets/`, `img/`, `admin/` and `api/` (except `config.php`). Change the repository instead.
- Product photos and review screenshots (`uploads/`) exist only on the server. Include them in your cPanel backups; the admin JSON backup does not contain image files.
- Settings, products, orders and reviews live in the database, so a deploy never changes them. The database upgrades itself when a new version needs new columns.
- To go back to an older version: pause the cron job, run `cd ~/repositories/babyglee-landing-page && git reset --hard <old commit> && bash tools/deploy.sh`, and re-enable the cron job only after you have fixed `main` on GitHub (the cron job pulls the newest version again).
- GitHub Pages can stay as a separate demo; it has no backend. Use the hosting address for real customers and for your ads.
