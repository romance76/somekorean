<?php
// Run from: cd /var/www/somekorean && php db_migrate.php

require __DIR__ . '/vendor/autoload.php';
$app = require_once __DIR__ . '/bootstrap/app.php';
$kernel = $app->make(Illuminate\Contracts\Console\Kernel::class);
$kernel->bootstrap();

use Illuminate\Support\Facades\DB;
use Illuminate\Support\Facades\Schema;

// Add columns to elder_settings
$columns = [
    'guardian_user_id'  => "BIGINT UNSIGNED NULL AFTER `alert_sent`",
    'guardian2_name'    => "VARCHAR(255) NULL AFTER `guardian_user_id`",
    'guardian2_phone'   => "VARCHAR(255) NULL AFTER `guardian2_name`",
    'checkin_time'      => "VARCHAR(5) DEFAULT '09:00' AFTER `guardian2_phone`",
    'checkin_enabled'   => "TINYINT(1) DEFAULT 1 AFTER `checkin_time`",
    'sos_enabled'       => "TINYINT(1) DEFAULT 1 AFTER `checkin_enabled`",
    'auto_call_enabled' => "TINYINT(1) DEFAULT 0 AFTER `sos_enabled`",
    'missed_count'      => "INT DEFAULT 0 AFTER `auto_call_enabled`",
    'timezone'          => "VARCHAR(50) DEFAULT 'America/New_York' AFTER `missed_count`",
    'notes'             => "TEXT NULL AFTER `timezone`",
];

foreach ($columns as $col => $def) {
    if (!Schema::hasColumn('elder_settings', $col)) {
        DB::statement("ALTER TABLE elder_settings ADD COLUMN `{$col}` {$def}");
        echo "Added: {$col}\n";
    } else {
        echo "Exists: {$col}\n";
    }
}

// Create elder_checkin_logs
if (!Schema::hasTable('elder_checkin_logs')) {
    DB::statement("
        CREATE TABLE elder_checkin_logs (
            id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
            user_id BIGINT UNSIGNED NOT NULL,
            checkin_date DATE NOT NULL,
            checked_at TIMESTAMP NULL,
            status ENUM('pending','checked','missed','sos') DEFAULT 'pending',
            alert_sent_at TIMESTAMP NULL,
            guardian_notified TINYINT(1) DEFAULT 0,
            created_at TIMESTAMP NULL,
            updated_at TIMESTAMP NULL,
            UNIQUE KEY elder_checkin_user_date (user_id, checkin_date),
            INDEX idx_elder_checkin_status (status),
            INDEX idx_elder_checkin_user (user_id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    ");
    echo "Created: elder_checkin_logs\n";
} else {
    echo "Exists: elder_checkin_logs\n";
}

// Create elder_sos_logs
if (!Schema::hasTable('elder_sos_logs')) {
    DB::statement("
        CREATE TABLE elder_sos_logs (
            id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
            user_id BIGINT UNSIGNED NOT NULL,
            lat DECIMAL(10,7) NULL,
            lng DECIMAL(10,7) NULL,
            status ENUM('triggered','responded','resolved','false_alarm') DEFAULT 'triggered',
            guardian_notified TINYINT(1) DEFAULT 0,
            resolved_at TIMESTAMP NULL,
            resolved_by BIGINT UNSIGNED NULL,
            note TEXT NULL,
            created_at TIMESTAMP NULL,
            updated_at TIMESTAMP NULL,
            INDEX idx_elder_sos_user (user_id),
            INDEX idx_elder_sos_status (status)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    ");
    echo "Created: elder_sos_logs\n";
} else {
    echo "Exists: elder_sos_logs\n";
}

echo "\nMigration complete!\n";
