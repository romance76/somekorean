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
        DB::table('news_categories')->delete();

        $groups = [
            '사회' => ['사회', '사건사고', '사람/커뮤니티', '이민/비자', '교육', '정치', '국제', '오피니언'],
            '경제' => ['경제', '생활경제', '금융/증권', '재테크', '부동산', '비즈니스', '자동차'],
            '라이프' => ['라이프/레저', '건강', '종교', '여행/취미', '리빙·스타일', '문화·예술', '시니어'],
            '연예·스포츠' => ['방송/연예', '영화', '스포츠', '한국야구', 'MLB', '농구', '풋볼', '골프', '축구'],
        ];

        foreach ($groups as $parentName => $children) {
            $parentId = DB::table('news_categories')->insertGetId([
                'name' => $parentName,
                'slug' => \Illuminate\Support\Str::slug($parentName),
                'parent_id' => null,
                'created_at' => now(),
                'updated_at' => now(),
            ]);

            foreach ($children as $child) {
                DB::table('news_categories')->insert([
                    'name' => $child,
                    'slug' => \Illuminate\Support\Str::slug($child) ?: $child,
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
