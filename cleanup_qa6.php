<?php
require __DIR__."/vendor/autoload.php";
$app = require __DIR__."/bootstrap/app.php";
$kernel = $app->make(Illuminate\Contracts\Console\Kernel::class);
$kernel->bootstrap();

use Illuminate\Support\Facades\DB;

// Delete QA post 343
$r = DB::table("qa_posts")->where("id", 343)->delete();
echo "QA 343 deleted: $r\n";

// Show like/comment tables
$tables = DB::select("SHOW TABLES");
foreach ($tables as $t) {
    $name = array_values((array)$t)[0];
    if (str_contains($name, "like")) echo "Like table: $name\n";
    if (str_contains($name, "comment")) echo "Comment table: $name\n";
}

// Try content_likes (polymorphic)
$r = DB::table("content_likes")->where("user_id", 1)->where("likeable_id", 349)->delete();
echo "Content likes for 349 deleted: $r\n";

// Try recipe_comments
try {
    $r = DB::table("recipe_comments")->where("user_id", 1)->where("recipe_id", 349)->orderByDesc("id")->first();
    if ($r) {
        DB::table("recipe_comments")->where("id", $r->id)->delete();
        echo "Recipe comment {$r->id} deleted\n";
    } else {
        echo "No recipe comment found for cleanup\n";
    }
} catch (\Exception $e) {
    echo "recipe_comments error: " . $e->getMessage() . "\n";
}

// Check if first run QA answer for qa_id=1 still exists
$ans = DB::table("qa_answers")->where("user_id", 1)->where("qa_post_id", 1)->orderByDesc("id")->first();
if ($ans) {
    DB::table("qa_answers")->where("id", $ans->id)->delete();
    echo "QA answer {$ans->id} deleted\n";
} else {
    echo "No stale QA answer found\n";
}

echo "Cleanup done\n";
