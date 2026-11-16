<?php
/* Optional cron job: retries server-side Purchase deliveries that failed (see api/dispatch.php). Without cron they are also retried whenever an admin page
   is opened or an order arrives. In cPanel > Cron Jobs run this every 5 minutes, for example:
   curl -s "https://yourdomain.com/api/retry.php?key=YOUR_CRON_KEY" > /dev/null
   The key is "cron_key" in api/config.php (a long random text). Without it this address answers 404. */
declare(strict_types=1);
require __DIR__ . '/lib.php';
require __DIR__ . '/capi.php';

$key = (string) (cfg()['cron_key'] ?? '');
if ($key === '' || strpos($key, 'CHANGE-THIS') === 0 || !hash_equals($key, (string) ($_GET['key'] ?? ''))) { http_response_code(404); exit; }
json_out(['ok' => true, 'tried' => retry_dispatches(db(), 20)]);
