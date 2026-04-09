<?php
use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;
use Illuminate\Support\Facades\DB;

return new class extends Migration {
    public function up(): void
    {
        // 포인트 설정 테이블 (관리자 수정 가능)
        if (!Schema::hasTable('point_settings')) {
            Schema::create('point_settings', function (Blueprint $table) {
                $table->id();
                $table->string('category', 50); // earn, spend, image, spam, auction, package
                $table->string('key', 100)->unique();
                $table->string('label');
                $table->string('value');
                $table->string('description')->nullable();
                $table->timestamps();
            });
        }

        // 게시글 상위 노출 테이블
        if (!Schema::hasTable('post_promotions')) {
            Schema::create('post_promotions', function (Blueprint $table) {
                $table->id();
                $table->foreignId('user_id')->constrained()->cascadeOnDelete();
                $table->string('promotable_type', 50); // post, job, market, realestate, qa
                $table->unsignedBigInteger('promotable_id');
                $table->integer('points_spent');
                $table->integer('days');
                $table->timestamp('starts_at');
                $table->timestamp('expires_at');
                $table->timestamps();
                $table->index(['promotable_type', 'promotable_id']);
                $table->index('expires_at');
            });
        }

        // 업소록 옥션 테이블
        if (!Schema::hasTable('business_auctions')) {
            Schema::create('business_auctions', function (Blueprint $table) {
                $table->id();
                $table->foreignId('business_id')->constrained('businesses')->cascadeOnDelete();
                $table->foreignId('user_id')->constrained()->cascadeOnDelete();
                $table->enum('scope', ['city', 'county', 'state', 'national']);
                $table->string('scope_value')->nullable(); // Atlanta, Gwinnett, GA, etc.
                $table->integer('daily_bid'); // 일일 입찰 포인트
                $table->boolean('is_active')->default(true);
                $table->timestamps();
                $table->unique(['business_id', 'scope']);
            });
        }

        // 기본 포인트 설정값 시드
        $settings = [
            // 적립
            ['category'=>'earn','key'=>'signup_bonus','label'=>'회원가입 보너스','value'=>'10','description'=>'최초 1회'],
            ['category'=>'earn','key'=>'profile_complete_bonus','label'=>'프로필 완성 보너스','value'=>'30','description'=>'사진+소개+전화+주소'],
            ['category'=>'earn','key'=>'checkin_min','label'=>'출석 최소','value'=>'5','description'=>'1P 단위 랜덤'],
            ['category'=>'earn','key'=>'checkin_max','label'=>'출석 최대','value'=>'50','description'=>'1P 단위 랜덤'],
            ['category'=>'earn','key'=>'post_write','label'=>'글 작성','value'=>'5','description'=>'1일 최대 10건'],
            ['category'=>'earn','key'=>'post_write_daily_max','label'=>'글 작성 일일 최대','value'=>'10','description'=>'건'],
            ['category'=>'earn','key'=>'comment_write','label'=>'댓글 작성','value'=>'3','description'=>'1일 최대 20건'],
            ['category'=>'earn','key'=>'comment_write_daily_max','label'=>'댓글 일일 최대','value'=>'20','description'=>'건'],
            ['category'=>'earn','key'=>'qa_answer_accepted','label'=>'Q&A 답변 채택','value'=>'20','description'=>''],

            // 상위 노출
            ['category'=>'spend','key'=>'promote_1day','label'=>'상위 노출 1일','value'=>'100','description'=>''],
            ['category'=>'spend','key'=>'promote_3day','label'=>'상위 노출 3일','value'=>'250','description'=>''],
            ['category'=>'spend','key'=>'promote_7day','label'=>'상위 노출 7일','value'=>'500','description'=>''],
            ['category'=>'spend','key'=>'promote_14day','label'=>'상위 노출 14일','value'=>'900','description'=>''],
            ['category'=>'spend','key'=>'promote_30day','label'=>'상위 노출 30일','value'=>'1500','description'=>''],

            // 이미지
            ['category'=>'image','key'=>'free_images','label'=>'무료 이미지 수','value'=>'2','description'=>'장'],
            ['category'=>'image','key'=>'extra_image_cost','label'=>'추가 이미지 1장','value'=>'10','description'=>'P'],
            ['category'=>'image','key'=>'max_images','label'=>'최대 이미지','value'=>'30','description'=>'장'],

            // 안심서비스
            ['category'=>'spend','key'=>'elder_scheduled_call','label'=>'안심 스케줄 전화 1회','value'=>'50','description'=>'15분 내 재전화 무료'],
            ['category'=>'spend','key'=>'elder_monthly_sub','label'=>'안심 30일 구독 가격','value'=>'14.99','description'=>'달러'],

            // 중고장터 스팸
            ['category'=>'spam','key'=>'market_free_posts_per_day','label'=>'중고 1일 무료 건수','value'=>'1','description'=>'동일 카테고리'],
            ['category'=>'spam','key'=>'market_2nd_post_cost','label'=>'2건째 비용','value'=>'100','description'=>'P'],
            ['category'=>'spam','key'=>'market_3rd_post_cost','label'=>'3건째 비용','value'=>'200','description'=>'P (3건 MAX)'],
            ['category'=>'spam','key'=>'market_max_posts_per_day','label'=>'1일 최대 게시','value'=>'3','description'=>'동일 카테고리'],

            // 업소록 옥션 최소 입찰가
            ['category'=>'auction','key'=>'auction_min_city','label'=>'옥션 최소 (시)','value'=>'50','description'=>'P/일'],
            ['category'=>'auction','key'=>'auction_min_county','label'=>'옥션 최소 (카운티)','value'=>'100','description'=>'P/일'],
            ['category'=>'auction','key'=>'auction_min_state','label'=>'옥션 최소 (주)','value'=>'200','description'=>'P/일'],
            ['category'=>'auction','key'=>'auction_min_national','label'=>'옥션 최소 (전국)','value'=>'500','description'=>'P/일'],
            ['category'=>'auction','key'=>'auction_top_slots','label'=>'옥션 상위 자리 수','value'=>'5','description'=>'개'],

            // 구매 패키지
            ['category'=>'package','key'=>'pkg_starter','label'=>'스타터','value'=>'4.99|500|0','description'=>'가격|포인트|보너스'],
            ['category'=>'package','key'=>'pkg_basic','label'=>'베이직','value'=>'9.99|1100|100','description'=>'가격|포인트|보너스'],
            ['category'=>'package','key'=>'pkg_standard','label'=>'스탠다드','value'=>'19.99|2500|500','description'=>'가격|포인트|보너스'],
            ['category'=>'package','key'=>'pkg_pro','label'=>'프로','value'=>'49.99|7500|2500','description'=>'가격|포인트|보너스'],
            ['category'=>'package','key'=>'pkg_business','label'=>'비즈니스','value'=>'99.99|17000|7000','description'=>'가격|포인트|보너스'],
        ];

        $now = now();
        foreach ($settings as $s) {
            DB::table('point_settings')->updateOrInsert(
                ['key' => $s['key']],
                array_merge($s, ['created_at' => $now, 'updated_at' => $now])
            );
        }
    }

    public function down(): void
    {
        Schema::dropIfExists('business_auctions');
        Schema::dropIfExists('post_promotions');
        Schema::dropIfExists('point_settings');
    }
};
