#!/bin/bash
# Cron job (every minute is fine): brings the live site up to date with the "main" branch on GitHub.
#   * does nothing when the site already runs the newest commit
#   * does nothing while updates are paused (the file ~/.babyglee-paused exists, created by tools/rollback.sh)
#   * does nothing when another update is already running
# Every update is written to ~/deploy.log. The deploy itself (tools/deploy.sh) backs up the live site first.
#
# cPanel > Cron Jobs, every minute:   /bin/bash $HOME/repositories/babyglee-landing-page/tools/auto-update.sh > /dev/null 2>&1
set -uo pipefail

HOME_DIR="${HOME:-}"
REPO="${BG_REPO:-$HOME_DIR/repositories/babyglee-landing-page}"
LOG="${BG_LOG:-$HOME_DIR/deploy.log}"
log() { echo "$(date '+%F %T') $*" >> "$LOG"; }

[ -f "$HOME_DIR/.babyglee-paused" ] && exit 0
cd "$REPO" 2>/dev/null || { log "repository not found: $REPO"; exit 1; }
if command -v flock >/dev/null 2>&1; then exec 8>"$HOME_DIR/.babyglee-update.lock"; flock -n 8 || exit 0; fi

git fetch -q origin main 2>>"$LOG" || { log "git fetch failed"; exit 1; }
NEW="$(git rev-parse origin/main)"
DONE="$(cat "$HOME_DIR/.babyglee-deployed-commit" 2>/dev/null || true)"
[ "$NEW" = "$DONE" ] && exit 0

# This clone is only used for deploying, so it always mirrors main exactly.
git reset -q --hard origin/main || { log "git reset failed"; exit 1; }
if out="$(bash tools/deploy.sh 2>&1)"; then
  log "deployed ${NEW:0:7}: $(echo "$out" | tail -n 1)"
else
  log "DEPLOY FAILED for ${NEW:0:7}: $out"
  exit 1
fi
tail -n 300 "$LOG" > "$LOG.tmp" 2>/dev/null && mv "$LOG.tmp" "$LOG"
exit 0
