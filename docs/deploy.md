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
2. Tell the deploy script where the site's web folder is. cPanel → *Domains* → note the **Document Root** of the domain (for example `/home/cpaneluser/shop.example.com`; if the site is the main domain of the account it is usually `/home/cpaneluser/public_html`). Check that this folder really exists in File Manager, and click **Save Changes** in the editor (the file must not show 0 bytes). In *File Manager* → Home directory (settings: show hidden files) → *New File* named `.babyglee-deploy-path` containing that one line.
3. First deploy: Git Version Control → *Manage* → *Pull or Deploy* → **Deploy HEAD Commit** (it runs `.cpanel.yml`, which runs `tools/deploy.sh`). Or in cPanel *Terminal*:
   ```bash
   cd ~/repositories/babyglee-landing-page && bash tools/deploy.sh
   ```
4. Create the private config. In File Manager open the web folder → `api/` → copy `config.sample.php` to **`config.php`** and fill in the database name, user, password, a long random `setup_key` and, optionally, a long random `cron_key`. This file is never in GitHub and the deploy never touches it.

## 4. Automatic updates (chat → GitHub → live site)

How a change reaches the site: you ask Claude in the chat → Claude changes the code, runs the tests, pushes a branch and opens a Pull Request → you say **"merge"** → the site updates itself. The word "merge" is the switch that sends a change live; nothing goes live without it.

**A. Recommended: GitHub tells the server (no polling, no cron).** The server does nothing until you merge; the moment `main` changes on GitHub, GitHub calls the server and the site updates within seconds.
1. In `api/config.php` on the server add a line `'deploy_secret' => 'a-long-random-text',` (see `api/config.sample.php`; use letters and digits, 40+ characters, and keep the same text for step 2).
2. GitHub → repository **Settings → Webhooks → Add webhook**: Payload URL `https://shop.example.com/api/deploy.php`, Content type `application/json`, Secret = the same long text, "Just the push event", Active. Save.
3. Check: Webhooks → your hook → **Recent Deliveries** → the first delivery (ping) must show a green tick and the response `{"ok":true,"pong":true}`. After the next merge a delivery shows `{"ok":true,"started":true}` and the site is updated a few seconds later.
4. If a delivery shows 403 or a Cloudflare page: Cloudflare → Security → WAF → add a *Skip* rule for the path `/api/deploy.php` (GitHub's webhook calls are signed, so they are safe). If it shows **501**, PHP's `exec()` is switched off on your hosting: use B instead.
5. A delivery that failed can be sent again from the same page (**Redeliver**).

The address only acts on a request signed with your secret, only for a push to `main`, and it only ever runs the fixed update script (`tools/auto-update.sh`).

**B. Without a webhook: two clicks when you want an update.** cPanel → **Git Version Control** → *Manage* → *Pull or Deploy* → **Update from Remote**, then **Deploy HEAD Commit**. If you also want a safety net, a cron job every 30 or 60 minutes (instead of every minute) is enough:

```bash
/bin/bash $HOME/repositories/babyglee-landing-page/tools/auto-update.sh > /dev/null 2>&1
```

It only fetches from GitHub and deploys when `main` has a newer commit, so most runs do nothing.

**Holding updates.** To stop every automatic update for a while (for example during an ad campaign), create an empty file called `.babyglee-paused` in the home folder (cPanel File Manager → Home directory → + File). Delete the file to resume; the next update then brings the site up to date. `tools/rollback.sh` creates this file too.

**C. Retries of failed Purchase deliveries (optional).** If you set a `cron_key`, add a job every 5 minutes:

```bash
curl -s "https://shop.example.com/api/retry.php?key=YOUR_CRON_KEY" > /dev/null
```

### Backups and going back

- Before every deploy over an existing site, the live files are saved as `~/deploy-backups/site-<date>-<commit>.tar.gz` (the newest 10 are kept; uploads and `config.php` are not in them). Every deploy is written to `~/deploy.log`.
- **Something broke after an update?** In cPanel → Terminal:
  ```bash
  bash ~/repositories/babyglee-landing-page/tools/rollback.sh
  ```
  It puts the previous version back and **pauses** automatic updates (so the bad version does not come back). Then tell Claude in the chat to fix or revert it; after that is merged, resume with `rm ~/.babyglee-paused` and the site updates to the newest `main`. You can also give a specific backup file: `bash …/tools/rollback.sh ~/deploy-backups/site-….tar.gz`.
- Database changes (new columns) are applied automatically and only add things, so a rollback of the files does not need a database rollback. For your data use cPanel → Backup and Admin → Settings → Download backup.

To update at once by hand (the same as B): Git Version Control → *Manage* → *Update from Remote*, then *Deploy HEAD Commit* (or run `bash ~/repositories/babyglee-landing-page/tools/auto-update.sh`).

## 5. First check

1. `https://shop.example.com/` opens the site, `…/checkout.html` and `…/thank-you.html` open.
2. `https://shop.example.com/assets/config.js` must start with `/* live from database */`. If you see the static file, `.htaccess` was not deployed or `mod_rewrite` is off (ask the host).
3. `https://shop.example.com/api/config.php` and `…/tools/` must answer "Forbidden".
4. Open `https://shop.example.com/admin/` the first time: type the `setup_key`, a username (your email address works) and a password of 10+ characters. Then follow `docs/backend-setup.md` (GTM ID, delivery charges, WhatsApp, products, reviews).
5. Place a test order on your phone. In Admin → Orders the **IP** on the order page must be a normal visitor address, not one that starts with 104., 172.64–71., 162.158/159., 141.101., 108.162., 188.114., 190.93., 197.234. or 198.41. (those are Cloudflare). If it is a Cloudflare address, tell me.

## Things to know

- cPanel keeps the domain's PHP version (for example "PHP 8.2 / ea-php82") in the web folder's `.htaccess`. The deploy keeps that block when it replaces `.htaccess`, so a deploy never changes the PHP version. If you change the PHP version in MultiPHP Manager later, cPanel rewrites the block itself.
- The first deploy keeps a copy of the `.htaccess` that was there before (for example with cPanel's *Force HTTPS Redirect* rule) as `.htaccess.before-deploy`, and never overwrites that copy later. With Cloudflare's **Always Use HTTPS** on, the redirect to https already happens at Cloudflare. Important: if cPanel's Force HTTPS Redirect is on, Cloudflare's SSL/TLS mode must be **Full** or **Full (strict)**; with *Flexible* the browser loops with "too many redirects".
- **Do not edit files on the server.** The next deploy overwrites `index.html`, `assets/`, `img/`, `admin/` and `api/` (except `config.php`). Change the repository instead.
- Product photos and review screenshots (`uploads/`) exist only on the server. Include them in your cPanel backups; the admin JSON backup does not contain image files.
- Settings, products, orders and reviews live in the database, so a deploy never changes them. The database upgrades itself when a new version needs new columns.
- To go back to an older version: pause the cron job, run `cd ~/repositories/babyglee-landing-page && git reset --hard <old commit> && bash tools/deploy.sh`, and re-enable the cron job only after you have fixed `main` on GitHub (the cron job pulls the newest version again).
- GitHub Pages can stay as a separate demo; it has no backend. Use the hosting address for real customers and for your ads.
