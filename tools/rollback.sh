#!/bin/bash
# Puts a previous version of the live site back.
#   bash tools/rollback.sh                     -> the newest backup in ~/deploy-backups (the version before the last deploy)
#   bash tools/rollback.sh /path/to/backup.tar.gz
# Rolling back also PAUSES automatic updates (it creates ~/.babyglee-paused), otherwise the next update would put the bad version back.
# After main on GitHub is fixed, resume with:   rm ~/.babyglee-paused
# The current live files are backed up first, so a rollback can itself be undone. Uploads and api/config.php are never touched.
set -euo pipefail

HOME_DIR="${HOME:-}"
BK_DIR="${BG_BACKUP_DIR:-$HOME_DIR/deploy-backups}"
FILE="${1:-}"
if [ -z "$FILE" ]; then FILE="$(ls -1t "$BK_DIR"/site-*.tar.gz 2>/dev/null | head -n 1 || true)"; fi
if [ -z "$FILE" ] || [ ! -f "$FILE" ]; then echo "No backup found in $BK_DIR"; exit 1; fi

TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT
mkdir -p "$TMP/site"
tar -xzf "$FILE" -C "$TMP/site"

touch "$HOME_DIR/.babyglee-paused"
BG_SRC="$TMP/site" BG_NO_RECORD=1 bash "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/deploy.sh"
rm -f "$HOME_DIR/.babyglee-deployed-commit"   # so that, once updates are resumed, the live site is brought up to date with main again
echo "Rolled back to $(basename "$FILE")."
echo "Automatic updates are PAUSED. After the problem is fixed on GitHub, resume with:  rm ~/.babyglee-paused"
