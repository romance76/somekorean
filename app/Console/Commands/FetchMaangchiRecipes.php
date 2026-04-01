<?php
namespace App\Console\Commands;
use Illuminate\Console\Command;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Facades\Http;

class FetchMaangchiRecipes extends Command {
    protected $signature = 'maangchi:fetch';
    protected $description = 'Fetch latest recipes from Maangchi RSS';

    public function handle() {
        $inserted = 0;
        for ($page = 1; $page <= 5; $page++) {
            $url = $page === 1 ? 'https://www.maangchi.com/feed' : "https://www.maangchi.com/feed?paged={$page}";
            try {
                $response = Http::timeout(15)->get($url);
                if (!$response->ok()) break;
                $xml = simplexml_load_string($response->body());
                $ns = $xml->getNamespaces(true);
                foreach ($xml->channel->item as $item) {
                    $title = (string) $item->title;
                    $link = (string) $item->link;
                    if (!$title || !$link) continue;
                    if (DB::table('recipe_posts')->where('title', $title)->exists()) continue;
                    $desc = strip_tags((string) $item->description);
                    $imageUrl = null;
                    if (isset($ns['content'])) {
                        $content = $item->children($ns['content']);
                        if (isset($content->encoded)) {
                            preg_match('/<img[^>]+src=["\']([^"\']+)["\']/', (string)$content->encoded, $m);
                            if ($m) $imageUrl = $m[1];
                        }
                    }
                    $catId = DB::table('recipe_categories')->value('id') ?? 1;
                    DB::table('recipe_posts')->insert([
                        'category_id' => $catId, 'user_id' => 1,
                        'title' => $title, 'intro' => substr($desc, 0, 500),
                        'source' => 'maangchi', 'source_url' => $link,
                        'image_url' => $imageUrl, 'difficulty' => '보통',
                        'cook_time' => '30분', 'view_count' => rand(200,3000),
                        'like_count' => rand(20,300), 'created_at' => now(), 'updated_at' => now(),
                    ]);
                    $inserted++;
                }
            } catch (\Exception $e) { break; }
        }
        $this->info("Fetched {$inserted} new Maangchi recipes");
        return 0;
    }
}
