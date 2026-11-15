# Working rules for this repository (set by the owner)

1. **Always record changes in `README.md`.** Every change adds an entry at the top of the "Changelog" section: date, what changed, files or areas touched.
2. **Always make a backup before changing things.** Before a round of changes, save a zip of the current live site (`main`) to
   `backups/site-<YYYY-MM-DD>-<short-reason>.zip` (`git archive --format=zip -o backups/... origin/main`) and mention it in the changelog.
3. Pages are generated: edit `tools/build.py` and run `python3 tools/build.py`. Do not hand-edit the generated `.html` files or `assets/products.js`.
   `assets/main.js` and `assets/style.css` are edited directly.
4. The site is a landing page: page 1 `index.html` (choose products and sizes), page 2 `checkout.html`, page 3 `thank-you.html`. Keep it to these three steps.
5. Mobile first: most visitors come from Facebook on phones in Bangladesh. Check every change at 360px and 390px width.
6. All site copy is in English; prices use the taka sign (৳). Do not mention where the shoes are manufactured.
7. Never invent customer reviews or statistics. Reviews are added by the owner in Admin → Reviews (text or screenshot).
8. Never commit `api/config.php`, database files, or anything with passwords or tokens.
