<?php
/* Meta Conversions API: sends the Purchase from the server with the same event_id the browser used, so Meta de-duplicates the two.
   Customer data is normalised and hashed here from the stored order (never trusted from the browser). */
declare(strict_types=1);

function capi_hash(string $v): string { return $v === '' ? '' : hash('sha256', $v); }
function capi_clean(string $v): string { return preg_replace('/[^\p{L}\p{N}]/u', '', mb_strtolower(trim($v))) ?? ''; }

function capi_payload(array $order, array $tracking, string $ip, string $ua): array {
    $parts = preg_split('/\s+/', trim(mb_strtolower($order['name']))) ?: [];
    $user = array_filter([
        'ph' => capi_hash($order['phone']),                                  // digits with country code, no plus
        'em' => capi_hash(mb_strtolower(trim($order['email']))),
        'fn' => capi_hash(capi_clean($parts[0] ?? '')),
        'ln' => capi_hash(capi_clean(implode(' ', array_slice($parts, 1)))),
        'ct' => capi_hash(capi_clean($order['district'])),
        'country' => capi_hash('bd'),
        'external_id' => $tracking['external_id'] ?? (!empty($tracking['uid']) ? capi_hash((string) $tracking['uid']) : ''),   // same SHA-256 of the visitor ID the browser sends
        'fbp' => $tracking['fbp'] ?? '', 'fbc' => $tracking['fbc'] ?? '',
        'client_ip_address' => $ip, 'client_user_agent' => $ua,
    ], fn($v) => $v !== '');
    $event = [
        'event_name' => 'Purchase', 'event_time' => time(), 'event_id' => $tracking['event_id'], 'action_source' => 'website',
        'user_data' => $user,
        'custom_data' => ['currency' => 'BDT', 'value' => (float) ($order['subtotal'] ?? $order['total']),   // product value, same as the browser event 'order_id' => $order['id'], 'content_type' => 'product',
            'content_ids' => array_values(array_unique(array_column($order['items'], 'sku'))),
            'contents' => array_map(fn($i) => ['id' => $i['sku'], 'quantity' => $i['qty'], 'item_price' => $i['price']], $order['items']),
            'num_items' => array_sum(array_column($order['items'], 'qty'))],
    ];
    if (!empty($tracking['page_url'])) $event['event_source_url'] = $tracking['page_url'];
    return $event;
}

/* Returns '' when CAPI is not configured, otherwise a short status text that is saved on the order. */
function capi_purchase(array $order, array $tracking, string $ip, string $ua): string {
    $pixel = setting('meta_pixel_id'); $token = setting('meta_capi_token');
    if ($pixel === '' || $token === '' || !function_exists('curl_init')) return '';
    $body = ['data' => [capi_payload($order, $tracking, $ip, $ua)], 'access_token' => $token];
    if (setting('meta_test_code') !== '') $body['test_event_code'] = setting('meta_test_code');
    $url = (getenv('BG_CAPI_URL') ?: 'https://graph.facebook.com') . '/' . rawurlencode(setting('meta_api_version')) . '/' . rawurlencode($pixel) . '/events';
    $ch = curl_init($url);
    curl_setopt_array($ch, [CURLOPT_POST => true, CURLOPT_POSTFIELDS => json_encode($body), CURLOPT_HTTPHEADER => ['Content-Type: application/json'],
        CURLOPT_RETURNTRANSFER => true, CURLOPT_TIMEOUT => 5, CURLOPT_CONNECTTIMEOUT => 3]);
    $resp = curl_exec($ch); $code = (int) curl_getinfo($ch, CURLINFO_HTTP_CODE); $err = curl_error($ch); curl_close($ch);
    if ($resp === false) return 'failed: ' . $err;
    if ($code >= 200 && $code < 300) return 'sent ' . date('H:i');
    $j = json_decode((string) $resp, true);
    return 'error ' . $code . ': ' . ($j['error']['message'] ?? 'unknown');
}

/* ---------- Purchase delivery from the server (never depends on the thank-you page being loaded) ---------- */

/* Sends the Purchase to a server-side GTM container through its GA4 Measurement Protocol URL (Admin > Settings). The event carries the same
   event_id / transaction_id as the browser event, so a Purchase seen twice is counted once. Returns a short status text, or '' when not set up. */
function sgtm_purchase(array $order, array $tr, string $ip, string $ua): string {
    $url = setting('sgtm_mp_url');
    if ($url === '' || !function_exists('curl_init')) return '';
    $parts = preg_split('/\s+/', trim(mb_strtolower($order['name']))) ?: [];
    $first = capi_clean($parts[0] ?? ''); $last = capi_clean(implode(' ', array_slice($parts, 1)));
    $ud = ['sha256_phone_number' => [capi_hash('+' . $order['phone'])], 'address' => [array_filter(['sha256_first_name' => capi_hash($first), 'sha256_last_name' => capi_hash($last), 'city' => $order['district'], 'region' => $order['district'], 'country' => 'BD'])]];
    if ($order['email'] !== '') $ud['sha256_email_address'] = [capi_hash(mb_strtolower(trim($order['email'])))];
    $ga = (string) ($tr['ga'] ?? ''); $cid = preg_match('/^GA\d\.\d\.(\d+\.\d+)$/', $ga, $m) ? $m[1] : ((string) ($tr['uid'] ?? '') ?: $order['id']);
    $items = array_map(fn($i) => ['item_id' => $i['sku'], 'item_name' => $i['product'], 'item_brand' => 'Babyglee', 'item_variant' => 'EU ' . $i['size'], 'price' => (int) $i['price'], 'quantity' => (int) $i['qty']], $order['items']);
    $params = array_filter(['transaction_id' => $order['id'], 'value' => (int) $order['subtotal'], 'currency' => 'BDT', 'shipping' => (int) $order['delivery'], 'tax' => 0, 'items' => $items,
        'event_id' => $tr['event_id'] ?? ('purchase_' . $order['id']), 'order_source' => $order['source'], 'payment_type' => 'Cash on Delivery', 'shipping_tier' => $order['area'],
        'page_location' => $tr['page_url'] ?? '', 'fbp' => $tr['fbp'] ?? '', 'fbc' => $tr['fbc'] ?? '', 'external_id' => $tr['uid'] ?? '', 'ip_override' => $ip, 'user_agent' => $ua,
        'engagement_time_msec' => 1, 'backend_event' => 1], fn($v) => $v !== '' && $v !== null);
    $body = ['client_id' => $cid, 'timestamp_micros' => (int) (microtime(true) * 1000000), 'user_data' => $ud, 'events' => [['name' => 'purchase', 'params' => $params]]];
    $ch = curl_init($url);
    curl_setopt_array($ch, [CURLOPT_POST => true, CURLOPT_POSTFIELDS => json_encode($body, JSON_UNESCAPED_UNICODE), CURLOPT_HTTPHEADER => ['Content-Type: application/json'],
        CURLOPT_RETURNTRANSFER => true, CURLOPT_TIMEOUT => 4, CURLOPT_CONNECTTIMEOUT => 2]);
    $resp = curl_exec($ch); $code = (int) curl_getinfo($ch, CURLINFO_HTTP_CODE); $err = curl_error($ch); curl_close($ch);
    if ($resp === false) return 'failed: ' . $err;
    return $code >= 200 && $code < 300 ? 'sent ' . date('H:i') : 'error ' . $code;
}

/* Delivers the Purchase of a saved order from the order's own saved values (items, prices, delivery), so it matches what the customer was charged.
   $origin: 'web' (placed on the site) or 'recovered' (created in Admin > Incomplete after a phone call: the browser never sent a Purchase for it).
   Meta Conversions API: as before, only when Pixel ID + token are saved. Server GTM: when a URL is saved and the mode is 'recovered' (default) or 'all'. */
function dispatch_purchase(PDO $pdo, string $oid, string $origin): void {
    $st = $pdo->prepare('SELECT * FROM orders WHERE id = ?'); $st->execute([$oid]); $o = $st->fetch();
    if (!$o) return;
    $tr = json_decode((string) $o['tracking'], true) ?: [];
    if (empty($tr['event_id'])) $tr['event_id'] = 'purchase_' . $oid;
    $order = ['id' => $oid, 'name' => (string) $o['name'], 'phone' => ltrim((string) $o['phone'], '+'), 'email' => (string) $o['email'], 'district' => (string) $o['district'], 'subtotal' => (int) $o['subtotal'],
        'delivery' => (int) $o['delivery'], 'total' => (int) $o['total'], 'items' => json_decode((string) $o['items'], true) ?: [], 'area' => (string) $o['area'], 'source' => (string) $o['source']];
    $status = [];
    $meta = capi_purchase($order, $tr, (string) $o['ip'], (string) $o['user_agent']);
    if ($meta !== '') $status[] = 'meta ' . $meta;
    $mode = setting('sgtm_mode');
    if (setting('sgtm_mp_url') !== '' && ($mode === 'all' || ($mode === 'recovered' && $origin === 'recovered'))) {
        $g = sgtm_purchase($order, $tr, (string) $o['ip'], (string) $o['user_agent']);
        if ($g !== '') $status[] = 'sgtm ' . $g;
    }
    if ($status) $pdo->prepare('UPDATE orders SET capi_status = ? WHERE id = ?')->execute([mb_substr(implode('; ', $status), 0, 120), $oid]);
}
