<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        // ─── Users Enhancement ───────────────────────────────────────
        Schema::table('users', function (Blueprint $table) {
            $table->string('nickname', 50)->nullable()->after('name');
            $table->string('phone', 20)->nullable()->after('nickname');
            $table->string('address')->nullable();
            $table->string('city', 100)->nullable();
            $table->string('state', 2)->nullable();
            $table->string('zipcode', 10)->nullable();
            $table->decimal('latitude', 10, 7)->nullable();
            $table->decimal('longitude', 10, 7)->nullable();
            $table->string('avatar')->nullable();
            $table->text('bio')->nullable();
            $table->string('language', 2)->default('ko');
            $table->integer('points')->default(0);
            $table->integer('game_points')->default(0);
            $table->string('role', 20)->default('user'); // user, admin, guardian
            $table->boolean('is_banned')->default(false);
            $table->string('ban_reason')->nullable();
            $table->timestamp('last_login_at')->nullable();
            $table->unsignedInteger('login_count')->default(0);
            $table->string('provider', 20)->nullable(); // social login
            $table->string('provider_id')->nullable();

            $table->index(['latitude', 'longitude']);
            $table->index('role');
            $table->index('city');
            $table->index('state');
        });

        // ─── 1. Boards ──────────────────────────────────────────────
        Schema::create('boards', function (Blueprint $table) {
            $table->id();
            $table->string('name', 100);
            $table->string('slug', 100)->unique();
            $table->string('description')->nullable();
            $table->unsignedInteger('sort_order')->default(0);
            $table->boolean('is_active')->default(true);
            $table->timestamps();

            $table->index('sort_order');
        });

        // ─── 2. Posts ────────────────────────────────────────────────
        Schema::create('posts', function (Blueprint $table) {
            $table->id();
            $table->foreignId('board_id')->constrained()->cascadeOnDelete();
            $table->foreignId('user_id')->constrained()->cascadeOnDelete();
            $table->string('title');
            $table->longText('content');
            $table->string('category', 50)->nullable();
            $table->json('images')->nullable();
            $table->unsignedInteger('view_count')->default(0);
            $table->unsignedInteger('like_count')->default(0);
            $table->unsignedInteger('comment_count')->default(0);
            $table->boolean('is_pinned')->default(false);
            $table->boolean('is_hidden')->default(false);
            $table->decimal('lat', 10, 7)->nullable();
            $table->decimal('lng', 10, 7)->nullable();
            $table->string('city', 100)->nullable();
            $table->string('state', 2)->nullable();
            $table->string('zipcode', 10)->nullable();
            $table->timestamps();

            $table->index(['board_id', 'created_at']);
            $table->index('category');
            $table->index(['lat', 'lng']);
            $table->index('is_pinned');
            $table->index('created_at');
        });

        // ─── 3. Comments (polymorphic) ───────────────────────────────
        Schema::create('comments', function (Blueprint $table) {
            $table->id();
            $table->string('commentable_type');
            $table->unsignedBigInteger('commentable_id');
            $table->foreignId('user_id')->constrained()->cascadeOnDelete();
            $table->unsignedBigInteger('parent_id')->nullable();
            $table->text('content');
            $table->unsignedInteger('like_count')->default(0);
            $table->boolean('is_hidden')->default(false);
            $table->timestamps();

            $table->index(['commentable_type', 'commentable_id']);
            $table->index('parent_id');
            $table->index('created_at');
        });

        // ─── 4. Post Likes ──────────────────────────────────────────
        Schema::create('post_likes', function (Blueprint $table) {
            $table->id();
            $table->foreignId('user_id')->constrained()->cascadeOnDelete();
            $table->foreignId('post_id')->constrained()->cascadeOnDelete();
            $table->timestamps();

            $table->unique(['user_id', 'post_id']);
        });

        // ─── 5. Bookmarks (polymorphic) ─────────────────────────────
        Schema::create('bookmarks', function (Blueprint $table) {
            $table->id();
            $table->foreignId('user_id')->constrained()->cascadeOnDelete();
            $table->string('bookmarkable_type');
            $table->unsignedBigInteger('bookmarkable_id');
            $table->timestamps();

            $table->index(['bookmarkable_type', 'bookmarkable_id']);
            $table->unique(['user_id', 'bookmarkable_type', 'bookmarkable_id'], 'bookmarks_unique');
        });

        // ─── 6. Job Posts ────────────────────────────────────────────
        Schema::create('job_posts', function (Blueprint $table) {
            $table->id();
            $table->foreignId('user_id')->constrained()->cascadeOnDelete();
            $table->string('title');
            $table->string('company')->nullable();
            $table->longText('content');
            $table->string('category', 50); // restaurant, office, retail, labor, beauty, driving, etc.
            $table->string('type', 20)->default('full'); // full, part, contract
            $table->unsignedInteger('salary_min')->nullable();
            $table->unsignedInteger('salary_max')->nullable();
            $table->string('salary_type', 10)->default('hourly'); // hourly, monthly, yearly
            $table->decimal('lat', 10, 7)->nullable();
            $table->decimal('lng', 10, 7)->nullable();
            $table->string('city', 100)->nullable();
            $table->string('state', 2)->nullable();
            $table->string('zipcode', 10)->nullable();
            $table->string('contact_email')->nullable();
            $table->string('contact_phone', 20)->nullable();
            $table->boolean('is_active')->default(true);
            $table->timestamp('expires_at')->nullable();
            $table->unsignedInteger('view_count')->default(0);
            $table->timestamps();

            $table->index(['lat', 'lng']);
            $table->index('category');
            $table->index('type');
            $table->index('is_active');
            $table->index('created_at');
        });

        // ─── 7. Market Items ─────────────────────────────────────────
        Schema::create('market_items', function (Blueprint $table) {
            $table->id();
            $table->foreignId('user_id')->constrained()->cascadeOnDelete();
            $table->string('title');
            $table->longText('content');
            $table->unsignedInteger('price')->default(0);
            $table->json('images')->nullable();
            $table->string('category', 50)->nullable();
            $table->string('condition', 20)->default('good'); // new, like_new, good, fair
            $table->decimal('lat', 10, 7)->nullable();
            $table->decimal('lng', 10, 7)->nullable();
            $table->string('city', 100)->nullable();
            $table->string('state', 2)->nullable();
            $table->string('status', 20)->default('active'); // active, reserved, sold
            $table->unsignedInteger('view_count')->default(0);
            $table->boolean('is_negotiable')->default(false);
            $table->timestamps();

            $table->index(['lat', 'lng']);
            $table->index('category');
            $table->index('status');
            $table->index('created_at');
        });

        // ─── 8. Market Reservations ──────────────────────────────────
        Schema::create('market_reservations', function (Blueprint $table) {
            $table->id();
            $table->foreignId('market_item_id')->constrained()->cascadeOnDelete();
            $table->foreignId('buyer_id')->constrained('users')->cascadeOnDelete();
            $table->foreignId('seller_id')->constrained('users')->cascadeOnDelete();
            $table->unsignedInteger('points_held')->default(0);
            $table->string('status', 20)->default('pending'); // pending, completed, cancelled, no_show
            $table->timestamp('completed_at')->nullable();
            $table->timestamp('cancelled_at')->nullable();
            $table->timestamps();

            $table->index('status');
        });

        // ─── 9. Businesses ───────────────────────────────────────────
        Schema::create('businesses', function (Blueprint $table) {
            $table->id();
            $table->foreignId('user_id')->nullable()->constrained()->nullOnDelete();
            $table->string('name');
            $table->longText('description')->nullable();
            $table->string('category', 50)->nullable();
            $table->string('subcategory', 50)->nullable();
            $table->string('phone', 20)->nullable();
            $table->string('email')->nullable();
            $table->string('website')->nullable();
            $table->string('address')->nullable();
            $table->string('city', 100)->nullable();
            $table->string('state', 2)->nullable();
            $table->string('zipcode', 10)->nullable();
            $table->decimal('lat', 10, 7)->nullable();
            $table->decimal('lng', 10, 7)->nullable();
            $table->json('images')->nullable();
            $table->string('logo')->nullable();
            $table->json('hours')->nullable();
            $table->decimal('rating', 3, 2)->default(0);
            $table->unsignedInteger('review_count')->default(0);
            $table->boolean('is_verified')->default(false);
            $table->boolean('is_claimed')->default(false);
            $table->foreignId('owner_id')->nullable()->constrained('users')->nullOnDelete();
            $table->unsignedInteger('view_count')->default(0);
            $table->timestamps();

            $table->index(['lat', 'lng']);
            $table->index('category');
            $table->index('subcategory');
            $table->index('city');
            $table->index('state');
            $table->index('is_verified');
            $table->index('created_at');
        });

        // ─── 10. Business Reviews ────────────────────────────────────
        Schema::create('business_reviews', function (Blueprint $table) {
            $table->id();
            $table->foreignId('business_id')->constrained()->cascadeOnDelete();
            $table->foreignId('user_id')->constrained()->cascadeOnDelete();
            $table->unsignedTinyInteger('rating'); // 1-5
            $table->text('content')->nullable();
            $table->json('images')->nullable();
            $table->timestamps();

            $table->index('business_id');
            $table->index('created_at');
        });

        // ─── 11. Business Claims ─────────────────────────────────────
        Schema::create('business_claims', function (Blueprint $table) {
            $table->id();
            $table->foreignId('business_id')->constrained()->cascadeOnDelete();
            $table->foreignId('user_id')->constrained()->cascadeOnDelete();
            $table->string('document_url')->nullable();
            $table->string('status', 20)->default('pending'); // pending, approved, rejected
            $table->text('notes')->nullable();
            $table->timestamps();

            $table->index('status');
        });

        // ─── 12. Real Estate Listings ────────────────────────────────
        Schema::create('real_estate_listings', function (Blueprint $table) {
            $table->id();
            $table->foreignId('user_id')->constrained()->cascadeOnDelete();
            $table->string('title');
            $table->longText('content');
            $table->string('type', 20); // rent, sale, roommate
            $table->string('property_type', 20); // apt, house, condo, studio, office
            $table->unsignedInteger('price')->default(0);
            $table->unsignedInteger('deposit')->nullable();
            $table->json('images')->nullable();
            $table->string('address')->nullable();
            $table->string('city', 100)->nullable();
            $table->string('state', 2)->nullable();
            $table->string('zipcode', 10)->nullable();
            $table->decimal('lat', 10, 7)->nullable();
            $table->decimal('lng', 10, 7)->nullable();
            $table->unsignedTinyInteger('bedrooms')->nullable();
            $table->decimal('bathrooms', 3, 1)->nullable();
            $table->unsignedInteger('sqft')->nullable();
            $table->boolean('is_active')->default(true);
            $table->unsignedInteger('view_count')->default(0);
            $table->string('contact_phone', 20)->nullable();
            $table->string('contact_email')->nullable();
            $table->timestamps();

            $table->index(['lat', 'lng']);
            $table->index('type');
            $table->index('property_type');
            $table->index('is_active');
            $table->index('created_at');
        });

        // ─── 13. Clubs ──────────────────────────────────────────────
        Schema::create('clubs', function (Blueprint $table) {
            $table->id();
            $table->foreignId('user_id')->constrained()->cascadeOnDelete();
            $table->string('name');
            $table->text('description')->nullable();
            $table->string('category', 50)->nullable();
            $table->string('image')->nullable();
            $table->string('type', 10)->default('local'); // online, local
            $table->string('zipcode', 10)->nullable();
            $table->unsignedInteger('member_count')->default(1);
            $table->boolean('is_active')->default(true);
            $table->timestamps();

            $table->index('category');
            $table->index('type');
            $table->index('is_active');
        });

        // ─── 14. Club Members ────────────────────────────────────────
        Schema::create('club_members', function (Blueprint $table) {
            $table->id();
            $table->foreignId('club_id')->constrained()->cascadeOnDelete();
            $table->foreignId('user_id')->constrained()->cascadeOnDelete();
            $table->string('role', 10)->default('member'); // admin, member
            $table->timestamp('joined_at')->nullable();
            $table->timestamps();

            $table->unique(['club_id', 'user_id']);
        });

        // ─── 15. Club Posts ──────────────────────────────────────────
        Schema::create('club_posts', function (Blueprint $table) {
            $table->id();
            $table->foreignId('club_id')->constrained()->cascadeOnDelete();
            $table->foreignId('user_id')->constrained()->cascadeOnDelete();
            $table->string('title');
            $table->longText('content');
            $table->json('images')->nullable();
            $table->unsignedInteger('like_count')->default(0);
            $table->unsignedInteger('comment_count')->default(0);
            $table->timestamps();

            $table->index(['club_id', 'created_at']);
        });

        // ─── 16. News Categories ─────────────────────────────────────
        Schema::create('news_categories', function (Blueprint $table) {
            $table->id();
            $table->string('name', 100);
            $table->string('slug', 100)->unique();
            $table->unsignedBigInteger('parent_id')->nullable();
            $table->timestamps();

            $table->index('parent_id');
        });

        // ─── 17. News ────────────────────────────────────────────────
        Schema::create('news', function (Blueprint $table) {
            $table->id();
            $table->string('title');
            $table->longText('content')->nullable();
            $table->text('summary')->nullable();
            $table->string('source')->nullable();
            $table->string('source_url')->nullable();
            $table->string('image_url')->nullable();
            $table->foreignId('category_id')->nullable()->constrained('news_categories')->nullOnDelete();
            $table->string('subcategory', 100)->nullable();
            $table->unsignedInteger('view_count')->default(0);
            $table->timestamp('published_at')->nullable();
            $table->timestamps();

            $table->index('category_id');
            $table->index('published_at');
            $table->index('created_at');
        });

        // ─── 18. Recipe Categories ───────────────────────────────────
        Schema::create('recipe_categories', function (Blueprint $table) {
            $table->id();
            $table->string('name', 100);
            $table->string('slug', 100)->unique();
            $table->unsignedInteger('sort_order')->default(0);
            $table->timestamps();
        });

        // ─── 19. Recipe Posts ────────────────────────────────────────
        Schema::create('recipe_posts', function (Blueprint $table) {
            $table->id();
            $table->foreignId('user_id')->constrained()->cascadeOnDelete();
            $table->string('title');
            $table->string('title_ko')->nullable();
            $table->longText('content');
            $table->longText('content_ko')->nullable();
            $table->json('ingredients')->nullable();
            $table->json('ingredients_ko')->nullable();
            $table->json('steps')->nullable();
            $table->json('steps_ko')->nullable();
            $table->foreignId('category_id')->nullable()->constrained('recipe_categories')->nullOnDelete();
            $table->json('images')->nullable();
            $table->unsignedTinyInteger('servings')->nullable();
            $table->unsignedSmallInteger('prep_time')->nullable(); // minutes
            $table->unsignedSmallInteger('cook_time')->nullable(); // minutes
            $table->string('difficulty', 10)->default('medium'); // easy, medium, hard
            $table->unsignedInteger('view_count')->default(0);
            $table->unsignedInteger('like_count')->default(0);
            $table->unsignedInteger('comment_count')->default(0);
            $table->timestamps();

            $table->index('category_id');
            $table->index('difficulty');
            $table->index('created_at');
        });

        // ─── 20. Group Buys ─────────────────────────────────────────
        Schema::create('group_buys', function (Blueprint $table) {
            $table->id();
            $table->foreignId('user_id')->constrained()->cascadeOnDelete();
            $table->string('title');
            $table->longText('content');
            $table->json('images')->nullable();
            $table->string('product_url')->nullable();
            $table->unsignedInteger('original_price')->default(0);
            $table->unsignedInteger('group_price')->default(0);
            $table->unsignedInteger('min_participants')->default(2);
            $table->unsignedInteger('max_participants')->nullable();
            $table->unsignedInteger('current_participants')->default(0);
            $table->decimal('lat', 10, 7)->nullable();
            $table->decimal('lng', 10, 7)->nullable();
            $table->string('city', 100)->nullable();
            $table->string('state', 2)->nullable();
            $table->string('status', 20)->default('recruiting'); // recruiting, confirmed, completed, cancelled
            $table->timestamp('deadline')->nullable();
            $table->timestamps();

            $table->index(['lat', 'lng']);
            $table->index('status');
            $table->index('deadline');
            $table->index('created_at');
        });

        // ─── 21. Events ─────────────────────────────────────────────
        Schema::create('events', function (Blueprint $table) {
            $table->id();
            $table->string('title');
            $table->text('description')->nullable();
            $table->longText('content')->nullable();
            $table->string('image_url')->nullable();
            $table->string('category', 50)->nullable();
            $table->string('organizer')->nullable();
            $table->string('venue')->nullable();
            $table->string('address')->nullable();
            $table->string('city', 100)->nullable();
            $table->string('state', 2)->nullable();
            $table->string('zipcode', 10)->nullable();
            $table->decimal('lat', 10, 7)->nullable();
            $table->decimal('lng', 10, 7)->nullable();
            $table->timestamp('start_date')->nullable();
            $table->timestamp('end_date')->nullable();
            $table->string('price', 50)->nullable();
            $table->string('url')->nullable();
            $table->string('source', 50)->nullable();
            $table->string('source_id')->nullable();
            $table->unsignedInteger('view_count')->default(0);
            $table->unsignedInteger('attendee_count')->default(0);
            $table->timestamps();

            $table->index(['lat', 'lng']);
            $table->index('category');
            $table->index('start_date');
            $table->index('city');
            $table->index('created_at');
        });

        // ─── 22. Event Attendees ─────────────────────────────────────
        Schema::create('event_attendees', function (Blueprint $table) {
            $table->id();
            $table->foreignId('event_id')->constrained()->cascadeOnDelete();
            $table->foreignId('user_id')->constrained()->cascadeOnDelete();
            $table->string('status', 20)->default('going'); // going, interested
            $table->timestamps();

            $table->unique(['event_id', 'user_id']);
        });

        // ─── 23. QA Categories ───────────────────────────────────────
        Schema::create('qa_categories', function (Blueprint $table) {
            $table->id();
            $table->string('name', 100);
            $table->string('slug', 100)->unique();
            $table->unsignedInteger('sort_order')->default(0);
            $table->timestamps();
        });

        // ─── 24. QA Posts ────────────────────────────────────────────
        Schema::create('qa_posts', function (Blueprint $table) {
            $table->id();
            $table->foreignId('user_id')->constrained()->cascadeOnDelete();
            $table->foreignId('category_id')->nullable()->constrained('qa_categories')->nullOnDelete();
            $table->string('title');
            $table->longText('content');
            $table->unsignedInteger('bounty_points')->default(0);
            $table->unsignedInteger('view_count')->default(0);
            $table->unsignedInteger('answer_count')->default(0);
            $table->boolean('is_resolved')->default(false);
            $table->unsignedBigInteger('best_answer_id')->nullable();
            $table->timestamps();

            $table->index('category_id');
            $table->index('is_resolved');
            $table->index('created_at');
        });

        // ─── 25. QA Answers ─────────────────────────────────────────
        Schema::create('qa_answers', function (Blueprint $table) {
            $table->id();
            $table->foreignId('qa_post_id')->constrained()->cascadeOnDelete();
            $table->foreignId('user_id')->constrained()->cascadeOnDelete();
            $table->longText('content');
            $table->unsignedInteger('like_count')->default(0);
            $table->boolean('is_best')->default(false);
            $table->timestamps();

            $table->index('qa_post_id');
            $table->index('created_at');
        });

        // ─── 26. Shorts ─────────────────────────────────────────────
        Schema::create('shorts', function (Blueprint $table) {
            $table->id();
            $table->foreignId('user_id')->nullable()->constrained()->nullOnDelete();
            $table->string('title')->nullable();
            $table->string('video_url')->nullable();
            $table->string('thumbnail_url')->nullable();
            $table->string('youtube_id', 20)->nullable();
            $table->unsignedSmallInteger('duration')->nullable();
            $table->unsignedInteger('view_count')->default(0);
            $table->unsignedInteger('like_count')->default(0);
            $table->unsignedInteger('comment_count')->default(0);
            $table->boolean('is_active')->default(true);
            $table->timestamps();

            $table->index('youtube_id');
            $table->index('is_active');
            $table->index('created_at');
        });

        // ─── 27. Short Likes ─────────────────────────────────────────
        Schema::create('short_likes', function (Blueprint $table) {
            $table->id();
            $table->foreignId('short_id')->constrained()->cascadeOnDelete();
            $table->foreignId('user_id')->constrained()->cascadeOnDelete();
            $table->timestamps();

            $table->unique(['short_id', 'user_id']);
        });

        // ─── 28. Shopping Stores ─────────────────────────────────────
        Schema::create('shopping_stores', function (Blueprint $table) {
            $table->id();
            $table->string('name');
            $table->string('logo')->nullable();
            $table->string('website')->nullable();
            $table->string('category', 50)->nullable();
            $table->timestamps();

            $table->index('category');
        });

        // ─── 29. Shopping Deals ──────────────────────────────────────
        Schema::create('shopping_deals', function (Blueprint $table) {
            $table->id();
            $table->foreignId('store_id')->nullable()->constrained('shopping_stores')->nullOnDelete();
            $table->string('title');
            $table->text('description')->nullable();
            $table->string('image_url')->nullable();
            $table->decimal('original_price', 10, 2)->nullable();
            $table->decimal('sale_price', 10, 2)->nullable();
            $table->unsignedTinyInteger('discount_percent')->nullable();
            $table->string('url')->nullable();
            $table->boolean('is_active')->default(true);
            $table->timestamp('expires_at')->nullable();
            $table->timestamps();

            $table->index('store_id');
            $table->index('is_active');
            $table->index('expires_at');
        });

        // ─── 30. Chat Rooms ─────────────────────────────────────────
        Schema::create('chat_rooms', function (Blueprint $table) {
            $table->id();
            $table->string('name')->nullable();
            $table->string('type', 10)->default('dm'); // dm, group
            $table->foreignId('created_by')->nullable()->constrained('users')->nullOnDelete();
            $table->timestamps();

            $table->index('type');
        });

        // ─── 31. Chat Room Users ─────────────────────────────────────
        Schema::create('chat_room_users', function (Blueprint $table) {
            $table->id();
            $table->foreignId('chat_room_id')->constrained()->cascadeOnDelete();
            $table->foreignId('user_id')->constrained()->cascadeOnDelete();
            $table->timestamp('last_read_at')->nullable();
            $table->timestamps();

            $table->unique(['chat_room_id', 'user_id']);
        });

        // ─── 32. Chat Messages ───────────────────────────────────────
        Schema::create('chat_messages', function (Blueprint $table) {
            $table->id();
            $table->foreignId('chat_room_id')->constrained()->cascadeOnDelete();
            $table->foreignId('user_id')->constrained()->cascadeOnDelete();
            $table->text('content')->nullable();
            $table->string('type', 10)->default('text'); // text, image, file
            $table->string('file_url')->nullable();
            $table->boolean('is_read')->default(false);
            $table->timestamps();

            $table->index(['chat_room_id', 'created_at']);
        });

        // ─── 33. Music Categories ────────────────────────────────────
        Schema::create('music_categories', function (Blueprint $table) {
            $table->id();
            $table->string('name', 100);
            $table->string('slug', 100)->unique();
            $table->string('image')->nullable();
            $table->unsignedInteger('sort_order')->default(0);
            $table->timestamps();
        });

        // ─── 34. Music Tracks ────────────────────────────────────────
        Schema::create('music_tracks', function (Blueprint $table) {
            $table->id();
            $table->foreignId('category_id')->nullable()->constrained('music_categories')->nullOnDelete();
            $table->string('title');
            $table->string('artist')->nullable();
            $table->string('youtube_url')->nullable();
            $table->string('youtube_id', 20)->nullable();
            $table->unsignedSmallInteger('duration')->nullable();
            $table->unsignedInteger('sort_order')->default(0);
            $table->timestamps();

            $table->index('category_id');
            $table->index('youtube_id');
        });

        // ─── 35. User Playlists ──────────────────────────────────────
        Schema::create('user_playlists', function (Blueprint $table) {
            $table->id();
            $table->foreignId('user_id')->constrained()->cascadeOnDelete();
            $table->string('name');
            $table->timestamps();

            $table->index('user_id');
        });

        // ─── 36. User Playlist Tracks ────────────────────────────────
        Schema::create('user_playlist_tracks', function (Blueprint $table) {
            $table->id();
            $table->foreignId('playlist_id')->constrained('user_playlists')->cascadeOnDelete();
            $table->foreignId('track_id')->constrained('music_tracks')->cascadeOnDelete();
            $table->unsignedInteger('sort_order')->default(0);
            $table->timestamps();

            $table->unique(['playlist_id', 'track_id']);
        });

        // ─── 37. Point Logs ─────────────────────────────────────────
        Schema::create('point_logs', function (Blueprint $table) {
            $table->id();
            $table->foreignId('user_id')->constrained()->cascadeOnDelete();
            $table->integer('amount');
            $table->string('type', 10); // earn, spend, purchase
            $table->string('reason');
            $table->string('related_type')->nullable();
            $table->unsignedBigInteger('related_id')->nullable();
            $table->integer('balance_after')->default(0);
            $table->timestamps();

            $table->index('user_id');
            $table->index('type');
            $table->index('created_at');
        });

        // ─── 38. User Daily Spins ────────────────────────────────────
        Schema::create('user_daily_spins', function (Blueprint $table) {
            $table->id();
            $table->foreignId('user_id')->constrained()->cascadeOnDelete();
            $table->timestamp('spun_at');
            $table->integer('points_won')->default(0);
            $table->timestamps();

            $table->index(['user_id', 'spun_at']);
        });

        // ─── 39. Game Rooms ─────────────────────────────────────────
        Schema::create('game_rooms', function (Blueprint $table) {
            $table->id();
            $table->string('game_type', 50);
            $table->foreignId('host_id')->constrained('users')->cascadeOnDelete();
            $table->string('status', 20)->default('waiting'); // waiting, playing, finished
            $table->unsignedTinyInteger('max_players')->default(4);
            $table->unsignedInteger('bet_amount')->default(0);
            $table->json('settings')->nullable();
            $table->timestamps();

            $table->index('game_type');
            $table->index('status');
            $table->index('created_at');
        });

        // ─── 40. Game Players ────────────────────────────────────────
        Schema::create('game_players', function (Blueprint $table) {
            $table->id();
            $table->foreignId('game_room_id')->constrained()->cascadeOnDelete();
            $table->foreignId('user_id')->constrained()->cascadeOnDelete();
            $table->integer('score')->default(0);
            $table->boolean('is_winner')->default(false);
            $table->unsignedInteger('bet_amount')->default(0);
            $table->timestamps();

            $table->index('game_room_id');
            $table->index('user_id');
        });

        // ─── 41. Game Settings ───────────────────────────────────────
        Schema::create('game_settings', function (Blueprint $table) {
            $table->id();
            $table->string('game_type', 50);
            $table->string('key');
            $table->text('value')->nullable();
            $table->timestamps();

            $table->unique(['game_type', 'key']);
        });

        // ─── 42. Elder Settings ──────────────────────────────────────
        Schema::create('elder_settings', function (Blueprint $table) {
            $table->id();
            $table->foreignId('user_id')->constrained()->cascadeOnDelete();
            $table->foreignId('guardian_id')->nullable()->constrained('users')->nullOnDelete();
            $table->unsignedSmallInteger('checkin_interval')->default(24); // hours
            $table->json('sos_contacts')->nullable();
            $table->json('medications')->nullable();
            $table->text('health_notes')->nullable();
            $table->timestamps();

            $table->index('user_id');
            $table->index('guardian_id');
        });

        // ─── 43. Elder Checkin Logs ──────────────────────────────────
        Schema::create('elder_checkin_logs', function (Blueprint $table) {
            $table->id();
            $table->foreignId('user_id')->constrained()->cascadeOnDelete();
            $table->timestamp('checked_in_at');
            $table->decimal('lat', 10, 7)->nullable();
            $table->decimal('lng', 10, 7)->nullable();
            $table->string('status', 10)->default('ok'); // ok, missed, sos
            $table->timestamps();

            $table->index(['user_id', 'checked_in_at']);
            $table->index('status');
        });

        // ─── 44. Elder SOS Logs ──────────────────────────────────────
        Schema::create('elder_sos_logs', function (Blueprint $table) {
            $table->id();
            $table->foreignId('user_id')->constrained()->cascadeOnDelete();
            $table->decimal('lat', 10, 7)->nullable();
            $table->decimal('lng', 10, 7)->nullable();
            $table->text('message')->nullable();
            $table->json('contacts_notified')->nullable();
            $table->timestamp('resolved_at')->nullable();
            $table->timestamps();

            $table->index('user_id');
        });

        // ─── 45. Friends ─────────────────────────────────────────────
        Schema::create('friends', function (Blueprint $table) {
            $table->id();
            $table->foreignId('user_id')->constrained()->cascadeOnDelete();
            $table->foreignId('friend_id')->constrained('users')->cascadeOnDelete();
            $table->string('status', 10)->default('pending'); // pending, accepted, blocked
            $table->timestamps();

            $table->unique(['user_id', 'friend_id']);
            $table->index('status');
        });

        // ─── 46. Notifications ───────────────────────────────────────
        Schema::create('notifications', function (Blueprint $table) {
            $table->id();
            $table->foreignId('user_id')->constrained()->cascadeOnDelete();
            $table->string('type', 50);
            $table->string('title')->nullable();
            $table->text('content')->nullable();
            $table->json('data')->nullable();
            $table->timestamp('read_at')->nullable();
            $table->timestamps();

            $table->index(['user_id', 'read_at']);
            $table->index('type');
            $table->index('created_at');
        });

        // ─── 47. Reports ─────────────────────────────────────────────
        Schema::create('reports', function (Blueprint $table) {
            $table->id();
            $table->foreignId('reporter_id')->constrained('users')->cascadeOnDelete();
            $table->string('reportable_type');
            $table->unsignedBigInteger('reportable_id');
            $table->string('reason', 50);
            $table->text('content')->nullable();
            $table->string('status', 20)->default('pending'); // pending, reviewed, resolved
            $table->text('admin_note')->nullable();
            $table->timestamps();

            $table->index(['reportable_type', 'reportable_id']);
            $table->index('status');
            $table->index('created_at');
        });

        // ─── 48. IP Bans ─────────────────────────────────────────────
        Schema::create('ip_bans', function (Blueprint $table) {
            $table->id();
            $table->string('ip_address', 45);
            $table->string('reason')->nullable();
            $table->foreignId('banned_by')->nullable()->constrained('users')->nullOnDelete();
            $table->timestamp('expires_at')->nullable();
            $table->timestamps();

            $table->index('ip_address');
            $table->index('expires_at');
        });

        // ─── 49. Site Settings ───────────────────────────────────────
        Schema::create('site_settings', function (Blueprint $table) {
            $table->id();
            $table->string('key')->unique();
            $table->text('value')->nullable();
            $table->string('group', 50)->default('general');
            $table->timestamps();

            $table->index('group');
        });

        // ─── 50. Banners ─────────────────────────────────────────────
        Schema::create('banners', function (Blueprint $table) {
            $table->id();
            $table->string('title');
            $table->string('image_url');
            $table->string('link_url')->nullable();
            $table->string('position', 30)->default('home'); // home, sidebar, etc.
            $table->unsignedInteger('sort_order')->default(0);
            $table->boolean('is_active')->default(true);
            $table->timestamp('starts_at')->nullable();
            $table->timestamp('ends_at')->nullable();
            $table->timestamps();

            $table->index('position');
            $table->index('is_active');
        });

        // ─── 51. Payments ────────────────────────────────────────────
        Schema::create('payments', function (Blueprint $table) {
            $table->id();
            $table->foreignId('user_id')->constrained()->cascadeOnDelete();
            $table->string('stripe_payment_id')->nullable();
            $table->decimal('amount', 10, 2);
            $table->string('currency', 3)->default('usd');
            $table->unsignedInteger('points_purchased')->default(0);
            $table->string('status', 20)->default('pending'); // pending, completed, failed
            $table->timestamps();

            $table->index('user_id');
            $table->index('status');
            $table->index('stripe_payment_id');
        });
    }

    public function down(): void
    {
        // Drop in reverse order of creation
        Schema::dropIfExists('payments');
        Schema::dropIfExists('banners');
        Schema::dropIfExists('site_settings');
        Schema::dropIfExists('ip_bans');
        Schema::dropIfExists('reports');
        Schema::dropIfExists('notifications');
        Schema::dropIfExists('friends');
        Schema::dropIfExists('elder_sos_logs');
        Schema::dropIfExists('elder_checkin_logs');
        Schema::dropIfExists('elder_settings');
        Schema::dropIfExists('game_settings');
        Schema::dropIfExists('game_players');
        Schema::dropIfExists('game_rooms');
        Schema::dropIfExists('user_daily_spins');
        Schema::dropIfExists('point_logs');
        Schema::dropIfExists('user_playlist_tracks');
        Schema::dropIfExists('user_playlists');
        Schema::dropIfExists('music_tracks');
        Schema::dropIfExists('music_categories');
        Schema::dropIfExists('chat_messages');
        Schema::dropIfExists('chat_room_users');
        Schema::dropIfExists('chat_rooms');
        Schema::dropIfExists('shopping_deals');
        Schema::dropIfExists('shopping_stores');
        Schema::dropIfExists('short_likes');
        Schema::dropIfExists('shorts');
        Schema::dropIfExists('qa_answers');
        Schema::dropIfExists('qa_posts');
        Schema::dropIfExists('qa_categories');
        Schema::dropIfExists('event_attendees');
        Schema::dropIfExists('events');
        Schema::dropIfExists('group_buys');
        Schema::dropIfExists('recipe_posts');
        Schema::dropIfExists('recipe_categories');
        Schema::dropIfExists('news');
        Schema::dropIfExists('news_categories');
        Schema::dropIfExists('club_posts');
        Schema::dropIfExists('club_members');
        Schema::dropIfExists('clubs');
        Schema::dropIfExists('real_estate_listings');
        Schema::dropIfExists('business_claims');
        Schema::dropIfExists('business_reviews');
        Schema::dropIfExists('businesses');
        Schema::dropIfExists('market_reservations');
        Schema::dropIfExists('market_items');
        Schema::dropIfExists('job_posts');
        Schema::dropIfExists('bookmarks');
        Schema::dropIfExists('post_likes');
        Schema::dropIfExists('comments');
        Schema::dropIfExists('posts');
        Schema::dropIfExists('boards');

        // Reverse users enhancement
        Schema::table('users', function (Blueprint $table) {
            $table->dropIndex(['latitude', 'longitude']);
            $table->dropIndex(['role']);
            $table->dropIndex(['city']);
            $table->dropIndex(['state']);
            $table->dropColumn([
                'nickname', 'phone', 'address', 'city', 'state', 'zipcode',
                'latitude', 'longitude', 'avatar', 'bio', 'language',
                'points', 'game_points', 'role', 'is_banned', 'ban_reason',
                'last_login_at', 'login_count', 'provider', 'provider_id',
            ]);
        });
    }
};
