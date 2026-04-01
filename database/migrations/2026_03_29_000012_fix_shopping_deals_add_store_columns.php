<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        Schema::table('shopping_deals', function (Blueprint $table) {
            // Add store relationship back (nullable so FetchShopping doesn't need it)
            if (!Schema::hasColumn('shopping_deals', 'store_id')) {
                $table->unsignedBigInteger('store_id')->nullable()->after('id');
            }
            // Add legacy columns that ShoppingController expects
            if (!Schema::hasColumn('shopping_deals', 'source_url')) {
                $table->string('source_url', 500)->nullable()->after('url');
            }
            if (!Schema::hasColumn('shopping_deals', 'valid_from')) {
                $table->date('valid_from')->nullable()->after('published_at');
            }
            if (!Schema::hasColumn('shopping_deals', 'valid_until')) {
                $table->date('valid_until')->nullable()->after('valid_from');
            }
            if (!Schema::hasColumn('shopping_deals', 'view_count')) {
                $table->integer('view_count')->default(0)->after('valid_until');
            }
            if (!Schema::hasColumn('shopping_deals', 'unit')) {
                $table->string('unit')->nullable()->after('view_count');
            }
        });

        // Create shopping_stores if missing
        if (!Schema::hasTable('shopping_stores')) {
            Schema::create('shopping_stores', function (Blueprint $table) {
                $table->id();
                $table->string('name');
                $table->enum('type', ['korean', 'american', 'asian', 'other'])->default('korean');
                $table->string('region')->nullable();
                $table->string('website')->nullable();
                $table->string('rss_url')->nullable();
                $table->string('logo')->nullable();
                $table->string('description')->nullable();
                $table->boolean('is_active')->default(true);
                $table->timestamps();
            });
        }
    }

    public function down(): void
    {
        Schema::table('shopping_deals', function (Blueprint $table) {
            $table->dropColumn(['store_id', 'source_url', 'valid_from', 'valid_until', 'view_count', 'unit']);
        });
    }
};
