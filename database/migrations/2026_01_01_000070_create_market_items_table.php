<?php
use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration {
    public function up(): void {
        Schema::create('market_items', function (Blueprint $table) {
            $table->id();
            $table->foreignId('user_id')->constrained()->onDelete('cascade');
            $table->string('title');
            $table->text('description');
            $table->decimal('price', 10, 2)->default(0);
            $table->boolean('price_negotiable')->default(false);
            $table->json('images')->nullable();
            $table->string('category')->default('etc');
            $table->enum('item_type', ['used','real_estate','car'])->default('used');
            $table->string('region')->nullable();
            $table->enum('condition', ['new','like_new','good','fair','poor'])->nullable();
            $table->unsignedBigInteger('view_count')->default(0);
            $table->enum('status', ['active','sold','deleted'])->default('active');
            $table->timestamps();
            $table->softDeletes();
            $table->index(['item_type', 'status', 'created_at']);
        });
    }
    public function down(): void { Schema::dropIfExists('market_items'); }
};
