<?php
/* Copy this file to api/config.php and fill it in. api/config.php is private: never commit it or share it. */
return [
    'db' => [
        'driver' => 'mysql',
        'host'   => 'localhost',
        'name'   => 'cpaneluser_babyglee',   // database name from cPanel > MySQL Databases
        'user'   => 'cpaneluser_babyglee',   // database user
        'pass'   => 'PUT-THE-DATABASE-PASSWORD-HERE',
    ],
    // One-time key you type on the first visit to /admin/ to create the admin password. Use a long random text.
    'setup_key' => 'CHANGE-THIS-TO-A-LONG-RANDOM-TEXT',
    // Most orders accepted per hour from one internet address (protects against order spam). Mobile networks share addresses, so keep it generous.
    'order_limit_per_hour' => 30,
    // Optional: lets a cPanel cron job call api/retry.php?key=... to retry failed server-side Purchase deliveries. Use a long random text, or delete this line.
    'cron_key' => 'CHANGE-THIS-TO-ANOTHER-LONG-RANDOM-TEXT',
];
