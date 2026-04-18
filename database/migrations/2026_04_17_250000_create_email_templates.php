<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Facades\Schema;

/**
 * Phase 2-C Post: 이메일 템플릿 (관리자 재사용 가능).
 */
return new class extends Migration {
    public function up(): void
    {
        Schema::create('email_templates', function (Blueprint $table) {
            $table->id();
            $table->string('slug', 100)->unique();
            $table->string('name', 255);
            $table->string('subject', 255);
            $table->longText('body_html');
            $table->text('body_text')->nullable();
            $table->json('variables')->nullable();       // ["user_name", "verification_code"]
            $table->string('category', 100)->default('general');
            $table->boolean('is_active')->default(true);
            $table->foreignId('created_by')->nullable()->constrained('users')->nullOnDelete();
            $table->timestamps();
        });

        // 기본 템플릿 3개 시드
        $now = now();
        DB::table('email_templates')->insert([
            [
                'slug' => 'welcome', 'name' => '가입 환영',
                'subject' => '🎉 SomeKorean 가입을 환영합니다!',
                'body_html' => '<h2>{{user_name}}님 환영합니다!</h2><p>SomeKorean 커뮤니티에 오신 것을 환영합니다.</p><p><a href="https://somekorean.com">커뮤니티 둘러보기 →</a></p>',
                'body_text' => "{{user_name}}님 환영합니다!\n\nSomeKorean 커뮤니티에 오신 것을 환영합니다.\nhttps://somekorean.com",
                'variables' => json_encode(['user_name']),
                'category' => 'onboarding',
                'is_active' => true, 'created_at' => $now, 'updated_at' => $now,
            ],
            [
                'slug' => 'password-reset', 'name' => '비밀번호 재설정',
                'subject' => '🔐 SomeKorean 비밀번호 재설정 코드',
                'body_html' => '<h2>비밀번호 재설정</h2><p>{{user_name}}님, 재설정 코드: <strong>{{code}}</strong></p><p>이 코드는 10분간 유효합니다.</p>',
                'body_text' => "{{user_name}}님, 재설정 코드: {{code}}\n이 코드는 10분간 유효합니다.",
                'variables' => json_encode(['user_name', 'code']),
                'category' => 'security',
                'is_active' => true, 'created_at' => $now, 'updated_at' => $now,
            ],
            [
                'slug' => 'weekly-digest', 'name' => '주간 요약',
                'subject' => '📰 이번 주 SomeKorean 하이라이트',
                'body_html' => '<h2>{{user_name}}님의 이번 주</h2><p>새 글: {{new_posts_count}}개</p><p>받은 좋아요: {{likes_count}}개</p>',
                'body_text' => "{{user_name}}님\n이번 주 새 글 {{new_posts_count}}개 / 받은 좋아요 {{likes_count}}개",
                'variables' => json_encode(['user_name', 'new_posts_count', 'likes_count']),
                'category' => 'digest',
                'is_active' => true, 'created_at' => $now, 'updated_at' => $now,
            ],
        ]);
    }

    public function down(): void
    {
        Schema::dropIfExists('email_templates');
    }
};
