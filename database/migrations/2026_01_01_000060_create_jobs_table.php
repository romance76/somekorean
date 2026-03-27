<?php
use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration {
    public function up(): void {
        Schema::create('job_posts', function (Blueprint $table) {
            $table->id();
            $table->foreignId('user_id')->constrained()->onDelete('cascade');
            $table->string('title');
            $table->text('content');
            $table->string('company_name')->nullable();
            $table->string('contact_email')->nullable();
            $table->string('contact_phone')->nullable();
            $table->string('region')->nullable();
            $table->string('address')->nullable();
            $table->enum('job_type', ['full_time','part_time','contract','freelance'])->default('full_time');
            $table->string('salary_range')->nullable();
            $table->date('deadline')->nullable();
            $table->boolean('is_pinned')->default(false);
            $table->unsignedBigInteger('view_count')->default(0);
            $table->enum('status', ['active','closed','deleted'])->default('active');
            $table->timestamps();
            $table->softDeletes();
        });
    }
    public function down(): void { Schema::dropIfExists('job_posts'); }
};
