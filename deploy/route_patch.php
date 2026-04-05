<?php
// Patch api.php routes for elder service
// Run from: cd /var/www/somekorean && php route_patch.php

$filePath = '/var/www/somekorean/routes/api.php';
$file = file_get_contents($filePath);

if (!$file) {
    echo "ERROR: Cannot read {$filePath}\n";
    exit(1);
}

// ─── Replace auth elder routes ───
$oldAuth = "Route::get('elder/settings',          [ElderController::class, 'settings']);";
$lastOldAuth = "Route::get('elder/guardian/{userId}', [ElderController::class, 'guardianView']);";

$posStart = strpos($file, $oldAuth);
$posEnd = strpos($file, $lastOldAuth);

if ($posStart !== false && $posEnd !== false) {
    $endOfLastLine = $posEnd + strlen($lastOldAuth);
    $before = substr($file, 0, $posStart);
    $after = substr($file, $endOfLastLine);

    // Detect line ending style
    $eol = (strpos($file, "\r\n") !== false) ? "\r\n" : "\n";

    $newRoutes = "Route::get('elder/settings',          [ElderController::class, 'settings']);" . $eol
               . "    Route::put('elder/settings',          [ElderController::class, 'updateSettings']);" . $eol
               . "    Route::post('elder/checkin',          [ElderController::class, 'checkin']);" . $eol
               . "    Route::post('elder/sos',              [ElderController::class, 'sos']);" . $eol
               . "    Route::get('elder/checkin-history',   [ElderController::class, 'checkinHistory']);" . $eol
               . "    Route::get('elder/sos-history',       [ElderController::class, 'sosHistory']);" . $eol
               . "    Route::post('elder/sos/{id}/resolve', [ElderController::class, 'resolveSos']);" . $eol
               . "    Route::get('elder/guardian/{userId}', [ElderController::class, 'guardianView']);" . $eol
               . "    Route::get('elder/guardian-search',   [ElderController::class, 'guardianSearch']);" . $eol
               . "    Route::post('elder/link-guardian',    [ElderController::class, 'linkGuardian']);";

    $file = $before . $newRoutes . $after;
    echo "Auth routes: REPLACED\n";
} else {
    echo "Auth routes: NOT FOUND (posStart=" . var_export($posStart, true) . ", posEnd=" . var_export($posEnd, true) . ")\n";
}

// ─── Replace admin elder routes ───
$oldAdminFirst = "Route::get('elder',                          [AdminController::class, 'elderMonitor']);";
$oldAdminLast = "Route::post('elder/settings',                [AdminController::class, 'saveElderSettings']);";

$posAdminStart = strpos($file, $oldAdminFirst);
$posAdminEnd = strpos($file, $oldAdminLast);

if ($posAdminStart !== false && $posAdminEnd !== false) {
    $endOfAdminLast = $posAdminEnd + strlen($oldAdminLast);
    $before = substr($file, 0, $posAdminStart);
    $after = substr($file, $endOfAdminLast);

    $eol = (strpos($file, "\r\n") !== false) ? "\r\n" : "\n";

    $newAdmin = "Route::get('elder/service-settings',         [ElderController::class, 'adminSettings']);" . $eol
              . "        Route::post('elder/service-settings',        [ElderController::class, 'adminSaveSettings']);" . $eol
              . "        Route::get('elder',                          [ElderController::class, 'adminMonitor']);" . $eol
              . "        Route::get('elder/{id}',                     [ElderController::class, 'adminDetail']);" . $eol
              . "        Route::post('elder/{id}/reset-checkin',      [ElderController::class, 'adminResetCheckin']);" . $eol
              . "        Route::post('elder/{id}/send-alert',         [ElderController::class, 'adminSendAlert']);";

    $file = $before . $newAdmin . $after;
    echo "Admin routes: REPLACED\n";
} else {
    echo "Admin routes: NOT FOUND (posStart=" . var_export($posAdminStart, true) . ", posEnd=" . var_export($posAdminEnd, true) . ")\n";
}

file_put_contents($filePath, $file);
echo "Routes saved!\n";
