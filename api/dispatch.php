<?php
/* Purchase delivery from the server, with durable retries.

   The browser sends Purchase from the thank-you page. This file sends it again from the SAVED order (items, prices, delivery as accepted), so it does not
   depend on the page being loaded, and also covers orders confirmed from Admin > Incomplete (their customers never see the thank-you page).
   Destinations: Meta Conversions API (when Pixel ID + token are saved) and a server-side GTM container (when a Measurement Protocol URL is saved).
   Every destination has its own status. A failed one is retried later (see BG_RETRY_MINUTES) until it works or the tries run out; one that already
   worked is never sent again. The state lives in the database (orders.dispatch*), so a restart or a slow server does not lose a conversion.
   Retries run from api/retry.php (optional cron job) and, without cron, whenever an admin page is opened or an order arrives. */
declare(strict_types=1);

const BG_RETRY_MINUTES = [1, 5, 15, 60, 240];   // pause after the 1st, 2nd, 3rd, 4th, 5th failed try; after the 6th the delivery is marked failed

/* Sends the Purchase to a server-side GTM container through its GA4 Measurement Protocol URL (Admin > Settings). Same event_id / transaction_id as the
   browser event, so a Purchase seen twice is counted once. Returns 'sent HH:MM', 'error NNN', 'failed: ...', or '' when not set up. */
function sgtm_purchase(array $order, array $tr, string $ip, string $ua): string {
    $url = setting('sgtm_mp_url');
    if ($url === '' || !function_exists('curl_init')) return '';
    $parts = preg_split('/\s+/', trim(mb_strtolower($order['name']))) ?: [];
    $first = capi_clean($parts[0] ?? ''); $last = capi_clean(implode(' ', array_slice($parts, 1)));
    $uid = (string) ($tr['uid'] ?? '');
    /* Google format (enhanced conversions): phone as E.164 with +880. */
    $ud = ['sha256_phone_number' => [capi_hash('+' . $order['phone'])], 'address' => [array_filter(['sha256_first_name' => capi_hash($first), 'sha256_last_name' => capi_hash($last), 'city' => $order['district'], 'region' => $order['district'], 'country' => 'BD'])]];
    if ($order['email'] !== '') $ud['sha256_email_address'] = [capi_hash(mb_strtolower(trim($order['email'])))];
    /* Meta format, separate from the Google one: phone is the digits with country code and NO plus (8801...), names without punctuation. The two hashes are
       different values and cannot replace each other. Map these meta_* event parameters to the Meta Conversions API tag's user data in your server container. */
    $metaUser = array_filter(['meta_ph' => capi_hash($order['phone']), 'meta_em' => $order['email'] !== '' ? capi_hash(mb_strtolower(trim($order['email']))) : '', 'meta_fn' => capi_hash($first), 'meta_ln' => capi_hash($last),
        'meta_ct' => capi_hash(capi_clean($order['district'])), 'meta_country' => capi_hash('bd'), 'meta_external_id' => $uid !== '' ? capi_hash($uid) : ''], fn($v) => $v !== '');
    $ga = (string) ($tr['ga'] ?? ''); $cid = preg_match('/^GA\d\.\d\.(\d+\.\d+)$/', $ga, $m) ? $m[1] : ($uid ?: $order['id']);
    $items = array_map(fn($i) => ['item_id' => $i['sku'], 'item_name' => $i['product'], 'item_brand' => 'Babyglee', 'item_variant' => 'EU ' . $i['size'], 'price' => (int) $i['price'], 'quantity' => (int) $i['qty']], $order['items']);
    $params = array_filter(array_merge(['transaction_id' => $order['id'], 'value' => (int) $order['subtotal'], 'currency' => 'BDT', 'shipping' => (int) $order['delivery'], 'tax' => 0, 'items' => $items,
        'event_id' => $tr['event_id'] ?? ('purchase_' . $order['id']), 'event_source_url' => $tr['page_url'] ?? '', 'order_source' => $order['source'], 'payment_type' => 'Cash on Delivery', 'shipping_tier' => $order['area'],
        'fbp' => $tr['fbp'] ?? '', 'fbc' => $tr['fbc'] ?? '', 'external_id' => $uid, 'ip_override' => $ip, 'user_agent' => $ua, 'engagement_time_msec' => 1, 'backend_event' => 1], $metaUser), fn($v) => $v !== '' && $v !== null);
    /* ip_override is also sent at the top level of the request, where the GA4 Measurement Protocol documents it; keep both until you have checked in
       server GTM Preview which one your container reads. The request's own User-Agent header is the customer's, so a server container that reads the header gets the right value. */
    $body = ['client_id' => $cid, 'timestamp_micros' => (int) (microtime(true) * 1000000), 'ip_override' => $ip, 'user_data' => $ud, 'events' => [['name' => 'purchase', 'params' => $params]]];
    if ($ip === '') unset($body['ip_override']);
    $ch = curl_init($url);
    $opt = [CURLOPT_POST => true, CURLOPT_POSTFIELDS => json_encode($body, JSON_UNESCAPED_UNICODE), CURLOPT_HTTPHEADER => ['Content-Type: application/json'],
        CURLOPT_RETURNTRANSFER => true, CURLOPT_TIMEOUT => 4, CURLOPT_CONNECTTIMEOUT => 2];
    if ($ua !== '') $opt[CURLOPT_USERAGENT] = $ua;
    curl_setopt_array($ch, $opt);
    $resp = curl_exec($ch); $code = (int) curl_getinfo($ch, CURLINFO_HTTP_CODE); $err = curl_error($ch); curl_close($ch);
    if ($resp === false) return 'failed: ' . $err;
    return $code >= 200 && $code < 300 ? 'sent ' . date('H:i') : 'error ' . $code;
}

/* Which destinations apply to an order. $origin: 'web' (placed on the site) or 'recovered' (confirmed from Admin > Incomplete). */
function purchase_destinations(string $origin): array {
    $d = [];
    if (setting('meta_pixel_id') !== '' && setting('meta_capi_token') !== '') $d[] = 'meta';
    $mode = setting('sgtm_mode');
    if (setting('sgtm_mp_url') !== '' && ($mode === 'all' || ($mode === 'recovered' && $origin === 'recovered'))) $d[] = 'sgtm';
    return $d;
}

/* One delivery round for an order: tries every destination that has not worked yet, then saves the result and when to try again. */
function dispatch_purchase(PDO $pdo, string $oid, string $origin): void {
    $stq = $pdo->prepare('SELECT * FROM orders WHERE id = ?'); $stq->execute([$oid]); $o = $stq->fetch();
    if (!$o) return;
    $st = json_decode((string) ($o['dispatch'] ?? ''), true);
    if (!is_array($st)) $st = ['origin' => $origin, 'tries' => 0, 'dest' => []];
    $origin = (string) ($st['origin'] ?? $origin);
    $dest = purchase_destinations($origin);
    if (!$dest) return;
    $tr = json_decode((string) $o['tracking'], true) ?: [];
    if (empty($tr['event_id'])) $tr['event_id'] = 'purchase_' . $oid;
    $order = ['id' => $oid, 'name' => (string) $o['name'], 'phone' => ltrim((string) $o['phone'], '+'), 'email' => (string) $o['email'], 'district' => (string) $o['district'], 'subtotal' => (int) $o['subtotal'],
        'delivery' => (int) $o['delivery'], 'total' => (int) $o['total'], 'items' => json_decode((string) $o['items'], true) ?: [], 'area' => (string) $o['area'], 'source' => (string) $o['source']];
    foreach ($dest as $name) {
        if (!empty($st['dest'][$name]['ok'])) continue;   // already delivered: never send it twice
        $txt = $name === 'meta' ? capi_purchase($order, $tr, (string) $o['ip'], (string) $o['user_agent']) : sgtm_purchase($order, $tr, (string) $o['ip'], (string) $o['user_agent']);
        $st['dest'][$name] = ['ok' => strncmp($txt, 'sent', 4) === 0, 'txt' => $txt];
    }
    $st['tries'] = (int) ($st['tries'] ?? 0) + 1;
    $left = array_filter($dest, fn($n) => empty($st['dest'][$n]['ok']));
    $next = null;
    if (!$left) $state = 'sent';
    elseif ($st['tries'] > count(BG_RETRY_MINUTES)) $state = 'failed';
    else { $state = 'pending'; $next = date('Y-m-d H:i:s', time() + BG_RETRY_MINUTES[$st['tries'] - 1] * 60); }
    $text = implode('; ', array_map(fn($n) => $n . ' ' . $st['dest'][$n]['txt'], $dest)) . ($state === 'pending' ? '; retry ' . date('H:i', strtotime((string) $next)) : ($state === 'failed' ? '; gave up' : ''));
    $pdo->prepare('UPDATE orders SET capi_status = ?, dispatch = ?, dispatch_state = ?, dispatch_next = ? WHERE id = ?')
        ->execute([mb_substr($text, 0, 120), json_encode($st), $state, $next, $oid]);
}

/* Runs the deliveries that are due. Each one is claimed first (its next time moves 2 minutes ahead), so two runs at the same moment do not send twice. Returns how many were tried. */
function retry_dispatches(PDO $pdo, int $limit = 3): int {
    $now = date('Y-m-d H:i:s');
    $q = $pdo->prepare("SELECT id, dispatch FROM orders WHERE dispatch_state = 'pending' AND dispatch_next IS NOT NULL AND dispatch_next <= ? ORDER BY dispatch_next LIMIT " . max(1, $limit));
    $q->execute([$now]); $n = 0;
    foreach ($q->fetchAll() as $r) {
        $claim = $pdo->prepare("UPDATE orders SET dispatch_next = ? WHERE id = ? AND dispatch_state = 'pending' AND dispatch_next <= ?");
        $claim->execute([date('Y-m-d H:i:s', time() + 120), $r['id'], $now]);
        if ($claim->rowCount() !== 1) continue;
        $st = json_decode((string) $r['dispatch'], true);
        try { dispatch_purchase($pdo, (string) $r['id'], (string) ($st['origin'] ?? 'web')); $n++; } catch (Throwable $e) { error_log('Babyglee purchase retry: ' . $e->getMessage()); }
    }
    return $n;
}
