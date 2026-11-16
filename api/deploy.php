<?php
/* Update on request: GitHub calls this address after every push to "main" (Settings > Webhooks) and the server updates itself from "main".

   How it works: the request is checked, then a small flag file ~/.babyglee-update-requested is written (PHP can always do that).
   - If PHP may run commands (exec), the update script starts at once (a few seconds).
   - If the hosting forbids exec (shared hosting often does), the answer is {"ok":true,"queued":true} and a cron job that runs
     "tools/auto-update.sh --on-request" picks the flag up within a minute. That cron job only looks for the flag file; it does not contact GitHub
     and does nothing when there is no flag, so the site is only updated after a merge.

   Safe by design:
   - it does nothing unless 'deploy_secret' is set in api/config.php, and every request must carry GitHub's signature made with that secret
     (X-Hub-Signature-256, HMAC-SHA256 of the body); without a valid signature it answers 401 and runs nothing;
   - it only reacts to a push to refs/heads/main, and what it runs is fixed (tools/auto-update.sh); nothing from the request is ever executed;
   - the answer is sent first, the update runs afterwards, so GitHub never waits. */
declare(strict_types=1);
require __DIR__ . '/lib.php';

$secret = (string) (cfg()['deploy_secret'] ?? '');
if ($secret === '' || strpos($secret, 'CHANGE-THIS') === 0) { http_response_code(404); exit; }
if (($_SERVER['REQUEST_METHOD'] ?? '') !== 'POST') json_out(['ok' => false, 'error' => 'POST only'], 405);

$raw = (string) file_get_contents('php://input', false, null, 0, 2000000);
$sig = (string) ($_SERVER['HTTP_X_HUB_SIGNATURE_256'] ?? '');
if (!hash_equals('sha256=' . hash_hmac('sha256', $raw, $secret), $sig)) json_out(['ok' => false, 'error' => 'bad signature'], 401);

$event = (string) ($_SERVER['HTTP_X_GITHUB_EVENT'] ?? '');
if ($event === 'ping') json_out(['ok' => true, 'pong' => true]);
$payload = json_decode($raw, true);
if ($event !== 'push' || !is_array($payload) || ($payload['ref'] ?? '') !== 'refs/heads/main') json_out(['ok' => true, 'ignored' => true]);

$home = (string) (cfg()['deploy_home'] ?? '');   // optional override; normally the account's home folder is found automatically
if ($home === '' && function_exists('posix_getpwuid') && function_exists('posix_geteuid')) { $pw = @posix_getpwuid(posix_geteuid()); $home = is_array($pw) ? (string) ($pw['dir'] ?? '') : ''; }
if ($home === '') $home = (string) (getenv('HOME') ?: '');
if ($home === '' || !is_dir($home)) json_out(['ok' => false, 'error' => 'home folder not found; set deploy_home in api/config.php'], 500);

/* 1. Leave the request for the update script (works everywhere). */
$flag = rtrim($home, '/') . '/.babyglee-update-requested';
if (@file_put_contents($flag, date('c') . ' ' . substr((string) ($payload['after'] ?? ''), 0, 7) . "\n") === false) json_out(['ok' => false, 'error' => 'cannot write the request file in ' . $home], 500);

/* 2. Where the hosting allows commands, start the update right now. */
$off = array_map('trim', explode(',', (string) ini_get('disable_functions')));
$repo = (string) (cfg()['deploy_repo'] ?? (rtrim($home, '/') . '/repositories/babyglee-landing-page'));
$script = $repo . '/tools/auto-update.sh';
if (!function_exists('exec') || in_array('exec', $off, true) || !is_file($script)) json_out(['ok' => true, 'queued' => true]);

json_out_then(['ok' => true, 'started' => true], function () use ($home, $repo, $script) {
    exec('env HOME=' . escapeshellarg($home) . ' BG_REPO=' . escapeshellarg($repo) . ' /bin/bash ' . escapeshellarg($script) . ' --on-request > /dev/null 2>&1');
});
