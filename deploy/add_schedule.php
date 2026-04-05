<?php
// Add elder:check to schedule in routes/console.php

$filePath = '/var/www/somekorean/routes/console.php';
$file = file_get_contents($filePath);

if (strpos($file, 'elder:check') !== false) {
    echo "elder:check already in schedule\n";
    exit(0);
}

// Add after the last Schedule line
$file .= "\n" . "Schedule::command('elder:check')->everyMinute();\n";

file_put_contents($filePath, $file);
echo "Added elder:check to schedule\n";
