<?php
use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration {
    public function up(): void {
        if (!Schema::hasTable('banners')) {
            Schema::create('banners', function (Blueprint $t) {
                $t->id();
                $t->string('name');
                $t->string('position'); // 메인상단,메인중간,사이드,게시판상단,팝업
                $t->string('image_url')->nullable();
                $t->string('link_url')->nullable();
                $t->boolean('new_tab')->default(true);
                $t->date('start_at')->nullable();
                $t->date('end_at')->nullable();
                $t->integer('order')->default(0);
                $t->boolean('active')->default(true);
                $t->string('advertiser')->nullable();
                $t->decimal('amount', 10, 2)->default(0);
                $t->integer('clicks')->default(0);
                $t->integer('impressions')->default(0);
                $t->text('memo')->nullable();
                $t->timestamps();
            });
        }
    }
    public function down(): void { Schema::dropIfExists('banners'); }
};
