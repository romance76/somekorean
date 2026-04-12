<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Support\Facades\DB;

/**
 * news_categories 를 koreadaily 실제 카테고리 구조로 재구성.
 *
 * 대분류 4개: 사회 / 경제 / 라이프 / 연예·스포츠
 * 각 대분류 아래에 실제 사이트의 세부 카테고리.
 */
return new class extends Migration {
    public function up(): void
    {
        // 기존 카테고리 레코드 전부 제거 (외래키 cascade 는 news.category_id nullable 이어야 함)
        DB::statement('UPDATE news SET category_id = NULL');
        DB::statement('DELETE FROM news_categories');
        DB::statement('ALTER TABLE news_categories AUTO_INCREMENT = 1');

        $groups = [
            '사회' => ['사회', '사건사고', '사람/커뮤니티', '이민/비자', '교육', '정치', '국제', '오피니언'],
            '경제' => ['경제', '생활경제', '금융/증권', '재테크', '부동산', '비즈니스', '자동차'],
            '라이프' => ['라이프/레저', '건강', '종교', '여행/취미', '리빙·스타일', '문화·예술', '시니어'],
            '연예·스포츠' => ['방송/연예', '영화', '스포츠', '한국야구', 'MLB', '농구', '풋볼', '골프', '축구'],
        ];

        $parentSlugs = [
            '사회' => 'society',
            '경제' => 'economy',
            '라이프' => 'life',
            '연예·스포츠' => 'sports',
        ];

        foreach ($groups as $parentName => $children) {
            $parentSlug = $parentSlugs[$parentName];
            $parentId = DB::table('news_categories')->insertGetId([
                'name' => $parentName,
                'slug' => $parentSlug,
                'parent_id' => null,
                'created_at' => now(),
                'updated_at' => now(),
            ]);

            foreach ($children as $i => $child) {
                DB::table('news_categories')->insert([
                    'name' => $child,
                    // 한글이라 Str::slug 가 빈 값이 되므로 parent-index 로 유니크 slug 생성
                    'slug' => $parentSlug . '-' . ($i + 1),
                    'parent_id' => $parentId,
                    'created_at' => now(),
                    'updated_at' => now(),
                ]);
            }
        }
    }

    public function down(): void
    {
        // 되돌리지 않음 (데이터 구조 변경이라 down 생략)
    }
};
