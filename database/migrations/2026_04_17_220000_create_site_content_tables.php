<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Facades\Schema;

/**
 * Phase 2-C 묶음 5: 사이트 콘텐츠 관리 테이블
 * - footer_links: App.vue 하드코딩 → DB 이관
 * - static_pages: About/Terms/Privacy 본문
 * - static_page_versions: 약관 변경 이력 (법적 고지)
 * - faqs: FAQ 시스템 신규
 * - site_setting_history: site_settings 변경 감사
 */
return new class extends Migration {
    public function up(): void
    {
        Schema::create('footer_links', function (Blueprint $table) {
            $table->id();
            $table->string('section', 100);            // 'services'|'content'|'info'|'legal'
            $table->string('label', 255);
            $table->string('label_en', 255)->nullable();
            $table->string('route_path', 255);
            $table->string('icon', 50)->nullable();
            $table->integer('sort_order')->default(0);
            $table->boolean('enabled')->default(true);
            $table->timestamps();
            $table->index(['section', 'sort_order']);
        });

        Schema::create('static_pages', function (Blueprint $table) {
            $table->id();
            $table->string('slug', 100)->unique();     // 'about'|'terms'|'privacy'|'community-guidelines'
            $table->string('title', 255);
            $table->longText('content');                // HTML
            $table->text('meta_description')->nullable();
            $table->string('meta_keywords', 500)->nullable();
            $table->boolean('published')->default(true);
            $table->integer('version')->default(1);
            $table->foreignId('updated_by')->nullable()->constrained('users')->nullOnDelete();
            $table->timestamps();
        });

        Schema::create('static_page_versions', function (Blueprint $table) {
            $table->id();
            $table->foreignId('static_page_id')->constrained()->cascadeOnDelete();
            $table->integer('version');
            $table->longText('content');
            $table->foreignId('changed_by')->nullable()->constrained('users')->nullOnDelete();
            $table->text('change_note')->nullable();
            $table->timestamp('created_at')->useCurrent();
            $table->index(['static_page_id', 'version']);
        });

        Schema::create('faqs', function (Blueprint $table) {
            $table->id();
            $table->string('category', 100);            // 'account'|'payment'|'usage'|'safety'
            $table->string('question', 500);
            $table->text('answer');
            $table->integer('sort_order')->default(0);
            $table->boolean('published')->default(true);
            $table->integer('helpful_count')->default(0);
            $table->integer('view_count')->default(0);
            $table->timestamps();
            $table->index(['category', 'sort_order']);
        });

        Schema::create('site_setting_history', function (Blueprint $table) {
            $table->id();
            $table->string('setting_key', 100);
            $table->longText('old_value')->nullable();
            $table->longText('new_value')->nullable();
            $table->foreignId('changed_by')->nullable()->constrained('users')->nullOnDelete();
            $table->text('change_note')->nullable();
            $table->timestamp('created_at')->useCurrent();
            $table->index(['setting_key', 'created_at']);
        });

        // ─── 시드 ───
        // Footer links (App.vue 기존 하드코딩 반영)
        $now = now();
        DB::table('footer_links')->insert([
            ['section'=>'services','label'=>'커뮤니티','route_path'=>'/community','icon'=>'💬','sort_order'=>1,'enabled'=>true,'created_at'=>$now,'updated_at'=>$now],
            ['section'=>'services','label'=>'업소록','route_path'=>'/directory','icon'=>'🏪','sort_order'=>2,'enabled'=>true,'created_at'=>$now,'updated_at'=>$now],
            ['section'=>'services','label'=>'중고장터','route_path'=>'/market','icon'=>'🛒','sort_order'=>3,'enabled'=>true,'created_at'=>$now,'updated_at'=>$now],
            ['section'=>'services','label'=>'부동산','route_path'=>'/realestate','icon'=>'🏠','sort_order'=>4,'enabled'=>true,'created_at'=>$now,'updated_at'=>$now],
            ['section'=>'content','label'=>'뉴스','route_path'=>'/news','icon'=>'📰','sort_order'=>1,'enabled'=>true,'created_at'=>$now,'updated_at'=>$now],
            ['section'=>'content','label'=>'레시피','route_path'=>'/recipes','icon'=>'🍳','sort_order'=>2,'enabled'=>true,'created_at'=>$now,'updated_at'=>$now],
            ['section'=>'content','label'=>'이벤트','route_path'=>'/events','icon'=>'🎉','sort_order'=>3,'enabled'=>true,'created_at'=>$now,'updated_at'=>$now],
            ['section'=>'info','label'=>'회사소개','route_path'=>'/about','icon'=>'ℹ️','sort_order'=>1,'enabled'=>true,'created_at'=>$now,'updated_at'=>$now],
            ['section'=>'info','label'=>'이용약관','route_path'=>'/terms','icon'=>'📋','sort_order'=>2,'enabled'=>true,'created_at'=>$now,'updated_at'=>$now],
            ['section'=>'info','label'=>'개인정보','route_path'=>'/privacy','icon'=>'🔒','sort_order'=>3,'enabled'=>true,'created_at'=>$now,'updated_at'=>$now],
            ['section'=>'info','label'=>'FAQ','route_path'=>'/faq','icon'=>'❓','sort_order'=>4,'enabled'=>true,'created_at'=>$now,'updated_at'=>$now],
        ]);

        // Static pages — 기존 프론트 하드코딩 본문을 DB 로 이관
        $aboutHtml = '<h2>SomeKorean 소개</h2>'
            . '<p>SomeKorean은 미국에 거주하는 한인들을 위한 올인원 커뮤니티 플랫폼입니다.</p>'
            . '<p>커뮤니티·업소록·구인구직·중고장터·부동산·뉴스·레시피·이벤트 등 한인 생활에 필요한 모든 정보를 한 곳에서 만나보실 수 있습니다.</p>'
            . '<p>문의: <a href="mailto:admin@somekorean.com">admin@somekorean.com</a></p>';

        $termsHtml = '<h2>이용약관</h2>'
            . '<h3>제1조 (목적)</h3>'
            . '<p>본 약관은 SomeKorean(이하 "회사")이 제공하는 서비스의 이용과 관련하여 회사와 이용자 간의 권리, 의무 및 책임사항을 규정함을 목적으로 합니다.</p>'
            . '<h3>제2조 (정의)</h3>'
            . '<p>본 약관에서 사용하는 용어의 정의는 다음과 같습니다.</p>'
            . '<ul><li>"서비스"란 SomeKorean 웹사이트 및 애플리케이션을 통해 제공되는 모든 기능을 의미합니다.</li>'
            . '<li>"회원"이란 본 약관에 동의하고 회원가입을 완료한 자를 말합니다.</li></ul>'
            . '<h3>제3조 (약관의 효력)</h3>'
            . '<p>본 약관은 서비스를 이용하고자 하는 모든 이용자에 대하여 그 효력을 발생합니다.</p>'
            . '<p><em>최종 수정일: 2026-04-06</em></p>';

        $privacyHtml = '<h2>개인정보처리방침</h2>'
            . '<h3>1. 수집하는 개인정보</h3>'
            . '<p>회사는 다음의 개인정보를 수집합니다: 이름, 이메일, 전화번호, 주소(선택).</p>'
            . '<h3>2. 개인정보의 이용목적</h3>'
            . '<p>회원 식별, 서비스 제공, 부정 이용 방지, 통계 분석.</p>'
            . '<h3>3. 개인정보의 보유기간</h3>'
            . '<p>회원 탈퇴 시까지. 관계 법령에 따라 일정 기간 보관이 필요한 정보는 해당 기간 동안 보관 후 파기합니다.</p>'
            . '<p><em>최종 수정일: 2026-04-06</em></p>';

        DB::table('static_pages')->insert([
            ['slug'=>'about','title'=>'SomeKorean 소개','content'=>$aboutHtml,'meta_description'=>'미국 한인 올인원 커뮤니티 SomeKorean 소개','published'=>true,'version'=>1,'created_at'=>$now,'updated_at'=>$now],
            ['slug'=>'terms','title'=>'이용약관','content'=>$termsHtml,'meta_description'=>'SomeKorean 이용약관','published'=>true,'version'=>1,'created_at'=>$now,'updated_at'=>$now],
            ['slug'=>'privacy','title'=>'개인정보처리방침','content'=>$privacyHtml,'meta_description'=>'SomeKorean 개인정보처리방침','published'=>true,'version'=>1,'created_at'=>$now,'updated_at'=>$now],
        ]);

        // site_settings 의 about_page/terms_page/privacy_page 값도 동기화 (기존 경로 호환)
        if (Schema::hasTable('site_settings')) {
            DB::table('site_settings')->updateOrInsert(['key'=>'about_page'],   ['value'=>$aboutHtml,  'group'=>'pages','updated_at'=>$now,'created_at'=>$now]);
            DB::table('site_settings')->updateOrInsert(['key'=>'terms_page'],   ['value'=>$termsHtml,  'group'=>'pages','updated_at'=>$now,'created_at'=>$now]);
            DB::table('site_settings')->updateOrInsert(['key'=>'privacy_page'], ['value'=>$privacyHtml,'group'=>'pages','updated_at'=>$now,'created_at'=>$now]);
        }

        // FAQ 기본 4건
        DB::table('faqs')->insert([
            ['category'=>'account','question'=>'회원가입은 어떻게 하나요?','answer'=>'상단 우측 "회원가입" 버튼을 클릭하여 이메일·비밀번호 입력 후 가입할 수 있습니다.','sort_order'=>1,'published'=>true,'created_at'=>$now,'updated_at'=>$now],
            ['category'=>'account','question'=>'비밀번호를 잊어버렸습니다.','answer'=>'로그인 페이지의 "비밀번호 찾기" 링크를 통해 이메일로 재설정 코드를 받으실 수 있습니다.','sort_order'=>2,'published'=>true,'created_at'=>$now,'updated_at'=>$now],
            ['category'=>'usage','question'=>'포인트는 어떻게 얻나요?','answer'=>'회원가입 보너스, 일일 로그인, 게시글 작성, 댓글, 일일 룰렛 등을 통해 포인트를 획득할 수 있습니다.','sort_order'=>1,'published'=>true,'created_at'=>$now,'updated_at'=>$now],
            ['category'=>'payment','question'=>'결제 후 환불이 가능한가요?','answer'=>'결제 후 7일 이내 사용하지 않은 포인트는 환불이 가능합니다. 고객센터로 문의해주세요.','sort_order'=>1,'published'=>true,'created_at'=>$now,'updated_at'=>$now],
        ]);
    }

    public function down(): void
    {
        Schema::dropIfExists('site_setting_history');
        Schema::dropIfExists('faqs');
        Schema::dropIfExists('static_page_versions');
        Schema::dropIfExists('static_pages');
        Schema::dropIfExists('footer_links');
    }
};
