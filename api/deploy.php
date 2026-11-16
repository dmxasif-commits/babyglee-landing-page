<?php
/* Instant update: GitHub calls this address after every push (Settings > Webhooks) and the server updates itself from the "main" branch within seconds.

   Safe by design:
   - it does nothing unless 'deploy_secret' is set in api/config.php, and every request must carry GitHub's signature made with that secret
     (X-Hub-Signature-256, HMAC-SHA256 of the body); without a valid signature it answers 401 and runs nothing;
   - it only reacts to a push to refs/heads/main, and what it runs is fixed (tools/auto-update.sh); nothing from the request is ever executed;
   - the answer is sent first, the update runs afterwards, so GitHub never waits.
   If PHP's exec() is switched off on the server, answer 501: the cron job (every minute) still keeps the site up to date. */
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

$off = array_map('trim', explode(',', (string) ini_get('disable_functions')));
if (!function_exists('exec') || in_array('exec', $off, true)) json_out(['ok' => false, 'error' => 'exec() is disabled on this server; the cron job keeps the site updated'], 501);

$home = (string) (cfg()['deploy_home'] ?? '');   // optional override; normally the account's home folder is found automatically
if ($home === '' && function_exists('posix_getpwuid') && function_exists('posix_geteuid')) { $pw = @posix_getpwuid(posix_geteuid()); $home = is_array($pw) ? (string) ($pw['dir'] ?? '') : ''; }
if ($home === '') $home = (string) (getenv('HOME') ?: '');
$repo = (string) (cfg()['deploy_repo'] ?? ($home . '/repositories/babyglee-landing-page'));
$script = $repo . '/tools/auto-update.sh';
if ($home === '' || !is_file($script)) json_out(['ok' => false, 'error' => 'repository not found'], 500);

json_out_then(['ok' => true, 'started' => true], function () use ($home, $repo, $script) {
    exec('env HOME=' . escapeshellarg($home) . ' BG_REPO=' . escapeshellarg($repo) . ' /bin/bash ' . escapeshellarg($script) . ' > /dev/null 2>&1');
});
