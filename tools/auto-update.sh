#!/bin/bash
# Brings the live site up to date with the "main" branch on GitHub. Two ways to run it:
#
#   auto-update.sh --on-request   (the cron job; recommended)
#       Only does something when the file ~/.babyglee-update-requested exists. That file is written by api/deploy.php after GitHub's webhook
#       reports a push to main, i.e. after you said "merge". Without the file it stops at once: no network, no GitHub check, no work.
#   auto-update.sh                (no argument)
#       Always asks GitHub whether main has a newer commit and deploys it when it has (used by hand, or by a cron job every 15-60 minutes
#       if you do not use the webhook).
#
# In both ways:
#   * nothing happens while updates are paused (the file ~/.babyglee-paused exists, created by tools/rollback.sh)
#   * nothing happens while another update is running
#   * every update is written to ~/deploy.log; the deploy itself (tools/deploy.sh) backs up the live site first
#   * a request that fails (GitHub or the deploy had a problem) is kept and retried on the next run, for up to 60 minutes
#
# cPanel > Cron Jobs, every minute:
#   /bin/bash $HOME/repositories/babyglee-landing-page/tools/auto-update.sh --on-request > /dev/null 2>&1
set -uo pipefail

MODE="${1:-}"
HOME_DIR="${HOME:-}"
REPO="${BG_REPO:-$HOME_DIR/repositories/babyglee-landing-page}"
LOG="${BG_LOG:-$HOME_DIR/deploy.log}"
FLAG="$HOME_DIR/.babyglee-update-requested"
CLAIM="$FLAG.running"
log() { echo "$(date '+%F %T') $*" >> "$LOG"; }

[ -f "$HOME_DIR/.babyglee-paused" ] && exit 0
if [ "$MODE" = "--on-request" ] && [ ! -f "$FLAG" ] && [ ! -f "$CLAIM" ]; then exit 0; fi

cd "$REPO" 2>/dev/null || { log "repository not found: $REPO"; exit 1; }
if command -v flock >/dev/null 2>&1; then exec 8>"$HOME_DIR/.babyglee-update.lock"; flock -n 8 || exit 0; fi

# Claim the request (atomic rename). A webhook that arrives while we work writes a new flag, which is handled by the next run.
if [ -f "$FLAG" ]; then mv -f "$FLAG" "$CLAIM" 2>/dev/null || true; fi
# Give up on a request that kept failing for an hour, so a permanent problem does not repeat forever.
if [ -f "$CLAIM" ] && [ -n "$(find "$CLAIM" -mmin +60 2>/dev/null)" ]; then log "giving up on an update request that kept failing for 60 minutes"; rm -f "$CLAIM"; exit 1; fi
# Put the claim back if this run fails, so the next run tries again (unless a newer flag already exists).
restore() { if [ -f "$CLAIM" ] && [ ! -f "$FLAG" ]; then mv -f "$CLAIM" "$FLAG" 2>/dev/null || true; fi; }

git fetch -q origin main 2>>"$LOG" || { log "git fetch failed"; restore; exit 1; }
NEW="$(git rev-parse origin/main)"
DONE="$(cat "$HOME_DIR/.babyglee-deployed-commit" 2>/dev/null || true)"
if [ "$NEW" = "$DONE" ]; then rm -f "$CLAIM"; exit 0; fi

# This clone is only used for deploying, so it always mirrors main exactly.
git reset -q --hard origin/main || { log "git reset failed"; restore; exit 1; }
if out="$(bash tools/deploy.sh 2>&1)"; then
  log "deployed ${NEW:0:7}: $(echo "$out" | tail -n 1)"
  rm -f "$CLAIM"
else
  log "DEPLOY FAILED for ${NEW:0:7}: $out"
  restore
  exit 1
fi
tail -n 300 "$LOG" > "$LOG.tmp" 2>/dev/null && mv "$LOG.tmp" "$LOG"
exit 0
