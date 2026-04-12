<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Support\Facades\DB;

/**
 * news_categories 를 오마이뉴스 실제 카테고리로 교체.
 */
return new class extends Migration {
    public function up(): void
    {
        DB::statement('UPDATE news SET category_id = NULL');
        DB::statement('DELETE FROM news_categories');
        DB::statement('ALTER TABLE news_categories AUTO_INCREMENT = 1');

        $categories = [
            ['name' => '정치',       'slug' => 'politics'],
            ['name' => '경제',       'slug' => 'economy'],
            ['name' => '사회',       'slug' => 'society'],
            ['name' => '문화',       'slug' => 'culture'],
            ['name' => '교육',       'slug' => 'education'],
            ['name' => '미디어',     'slug' => 'media'],
            ['name' => '민족·국제',  'slug' => 'international'],
            ['name' => '스포츠',     'slug' => 'sports'],
            ['name' => '여성',       'slug' => 'woman'],
            ['name' => '스타',       'slug' => 'star'],
            ['name' => '만평·만화',  'slug' => 'cartoon'],
        ];

        foreach ($categories as $cat) {
            DB::table('news_categories')->insert([
                'name' => $cat['name'],
                'slug' => $cat['slug'],
                'parent_id' => null,
                'created_at' => now(),
                'updated_at' => now(),
            ]);
        }
    }

    public function down(): void {}
};
