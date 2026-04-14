<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        // ═══════════ 동호회 확장 ═══════════
        Schema::table('clubs', function (Blueprint $table) {
            if (!Schema::hasColumn('clubs', 'rules')) {
                $table->text('rules')->nullable()->after('description');
            }
            if (!Schema::hasColumn('clubs', 'max_members')) {
                $table->unsignedInteger('max_members')->default(0)->after('member_count'); // 0=무제한
            }
            if (!Schema::hasColumn('clubs', 'is_public')) {
                $table->boolean('is_public')->default(true)->after('is_active');
            }
            if (!Schema::hasColumn('clubs', 'cover_image')) {
                $table->string('cover_image')->nullable()->after('image');
            }
        });

        // 동호회 회원 등급 추가
        Schema::table('club_members', function (Blueprint $table) {
            if (!Schema::hasColumn('club_members', 'grade')) {
                $table->enum('grade', ['owner', 'admin', 'member', 'restricted'])->default('member')->after('role');
            }
        });

        // 동호회 게시판
        if (!Schema::hasTable('club_boards')) {
            Schema::create('club_boards', function (Blueprint $table) {
                $table->id();
                $table->foreignId('club_id')->constrained()->cascadeOnDelete();
                $table->string('name', 100);
                $table->string('description')->nullable();
                $table->unsignedSmallInteger('sort_order')->default(0);
                $table->boolean('only_admin_post')->default(false);
                $table->boolean('is_active')->default(true);
                $table->timestamps();
            });
        }

        // 동호회 게시글 확장
        Schema::table('club_posts', function (Blueprint $table) {
            if (!Schema::hasColumn('club_posts', 'board_id')) {
                $table->foreignId('board_id')->nullable()->after('club_id');
            }
            if (!Schema::hasColumn('club_posts', 'is_pinned')) {
                $table->boolean('is_pinned')->default(false)->after('comment_count');
            }
        });

        // ═══════════ 공동구매 확장 ═══════════
        Schema::table('group_buys', function (Blueprint $table) {
            if (!Schema::hasColumn('group_buys', 'category')) {
                $table->string('category', 50)->nullable()->after('content');
            }
            if (!Schema::hasColumn('group_buys', 'end_type')) {
                $table->enum('end_type', ['target_met', 'time_limit', 'flexible'])->default('flexible')->after('status');
            }
            if (!Schema::hasColumn('group_buys', 'discount_tiers')) {
                $table->json('discount_tiers')->nullable()->after('group_price');
                // [{min_people:5, discount_pct:10}, {min_people:10, discount_pct:20}]
            }
            if (!Schema::hasColumn('group_buys', 'payment_method')) {
                $table->enum('payment_method', ['point', 'stripe', 'both', 'none'])->default('none')->after('end_type');
            }
            if (!Schema::hasColumn('group_buys', 'business_doc')) {
                $table->string('business_doc')->nullable()->after('product_url');
            }
            if (!Schema::hasColumn('group_buys', 'is_approved')) {
                $table->boolean('is_approved')->default(false)->after('status');
            }
            if (!Schema::hasColumn('group_buys', 'approved_by')) {
                $table->foreignId('approved_by')->nullable()->after('is_approved');
            }
            if (!Schema::hasColumn('group_buys', 'approved_at')) {
                $table->timestamp('approved_at')->nullable()->after('approved_by');
            }
            if (!Schema::hasColumn('group_buys', 'rejection_reason')) {
                $table->string('rejection_reason')->nullable()->after('approved_at');
            }
        });

        // 공동구매 참여자
        if (!Schema::hasTable('group_buy_participants')) {
            Schema::create('group_buy_participants', function (Blueprint $table) {
                $table->id();
                $table->foreignId('group_buy_id')->constrained()->cascadeOnDelete();
                $table->foreignId('user_id')->constrained()->cascadeOnDelete();
                $table->unsignedInteger('quantity')->default(1);
                $table->unsignedInteger('paid_amount')->default(0);
                $table->enum('payment_type', ['point', 'stripe', 'none'])->default('none');
                $table->string('payment_id')->nullable(); // Stripe payment intent
                $table->enum('status', ['pending', 'paid', 'refunded', 'cancelled'])->default('pending');
                $table->timestamps();
                $table->unique(['group_buy_id', 'user_id']);
            });
        }

        // ═══════════ 이벤트 확장 ═══════════
        Schema::table('events', function (Blueprint $table) {
            if (!Schema::hasColumn('events', 'user_id')) {
                $table->foreignId('user_id')->nullable()->after('id');
            }
            if (!Schema::hasColumn('events', 'is_active')) {
                $table->boolean('is_active')->default(true)->after('attendee_count');
            }
            if (!Schema::hasColumn('events', 'max_attendees')) {
                $table->unsignedInteger('max_attendees')->default(0)->after('attendee_count');
            }
            if (!Schema::hasColumn('events', 'is_free')) {
                $table->boolean('is_free')->default(true)->after('price');
            }
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('group_buy_participants');
        Schema::dropIfExists('club_boards');
    }
};
