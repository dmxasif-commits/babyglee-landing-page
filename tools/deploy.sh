#!/bin/bash
# Copies the website files from this repository into the web folder (the document root of your domain or subdomain).
# Used by cPanel's "Deploy HEAD Commit" (through .cpanel.yml) and by the cron job in docs/deploy.md.
#
# Where the web folder is, in this order:
#   1. the BG_DEPLOY_PATH environment variable
#   2. the first line of the file  ~/.babyglee-deploy-path   (create it once, for example: /home/cpaneluser/shop.example.com)
#   3. ~/public_html
#
# Never touched on the server: api/config.php (database login) and everything in uploads/ (product photos, review screenshots).
# Not copied at all: tools/, docs/, backups/, README.md, CLAUDE.md and other repository files.
set -euo pipefail

SRC="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
HOME_DIR="${HOME:-}"
if [ -n "${BG_DEPLOY_PATH:-}" ]; then DEST="$BG_DEPLOY_PATH"
elif [ -n "$HOME_DIR" ] && [ -f "$HOME_DIR/.babyglee-deploy-path" ]; then DEST="$(head -n 1 "$HOME_DIR/.babyglee-deploy-path" | tr -d '\r')"
else DEST="$HOME_DIR/public_html"; fi
DEST="${DEST%/}"

# Safety: only an existing folder that is not the home folder or the root of the server.
if [ -z "$DEST" ] || [ "$DEST" = "$HOME_DIR" ] || [ "$DEST" = "/" ]; then echo "Refusing to deploy to '$DEST'. Set the web folder (see the comments in this file)."; exit 1; fi
if [ ! -d "$DEST" ]; then echo "Web folder not found: $DEST"; exit 1; fi

use_rsync=0
if [ -z "${BG_NO_RSYNC:-}" ] && command -v rsync >/dev/null 2>&1; then use_rsync=1; fi

# Top-level pages and the Apache rules.
for f in "$SRC"/*.html "$SRC/.htaccess"; do [ -f "$f" ] && cp -f "$f" "$DEST/"; done

# Folders. With rsync, files that were removed from the repository are removed here too (config.php is always kept).
for d in assets img admin api; do
  mkdir -p "$DEST/$d"
  if [ "$use_rsync" = 1 ]; then rsync -a --delete --exclude 'config.php' "$SRC/$d/" "$DEST/$d/"
  else cp -R "$SRC/$d/." "$DEST/$d/"; fi
done

# Uploads: only make sure the folder and its protective .htaccess exist; the photos themselves are never touched.
mkdir -p "$DEST/uploads"
[ -f "$SRC/uploads/.htaccess" ] && cp -f "$SRC/uploads/.htaccess" "$DEST/uploads/.htaccess"

if [ ! -f "$DEST/api/config.php" ]; then echo "Note: $DEST/api/config.php does not exist yet. Create it from api/config.sample.php (see docs/deploy.md)."; fi
echo "Deployed $(cd "$SRC" && git rev-parse --short HEAD 2>/dev/null || echo files) to $DEST"
