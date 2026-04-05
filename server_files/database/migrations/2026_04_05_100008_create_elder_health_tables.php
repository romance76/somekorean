<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        Schema::create('elder_health_records', function (Blueprint $table) {
            $table->id();
            $table->foreignId('user_id')->constrained()->cascadeOnDelete();
            $table->integer('blood_pressure_systolic')->nullable();
            $table->integer('blood_pressure_diastolic')->nullable();
            $table->integer('blood_sugar')->nullable();
            $table->decimal('weight', 5, 1)->nullable();
            $table->timestamp('recorded_at')->nullable();
            $table->timestamp('created_at')->nullable();

            $table->index(['user_id', 'recorded_at']);
        });

        Schema::create('elder_sos_alerts', function (Blueprint $table) {
            $table->id();
            $table->foreignId('user_id')->constrained()->cascadeOnDelete();
            $table->decimal('latitude', 10, 7)->nullable();
            $table->decimal('longitude', 10, 7)->nullable();
            $table->string('address')->nullable();
            $table->enum('status', ['active', 'resolved', 'false_alarm'])->default('active');
            $table->unsignedBigInteger('resolved_by')->nullable();
            $table->timestamp('resolved_at')->nullable();
            $table->timestamps();

            $table->index(['user_id', 'status']);
        });

        Schema::create('elder_medication_logs', function (Blueprint $table) {
            $table->id();
            $table->foreignId('user_id')->constrained()->cascadeOnDelete();
            $table->string('medication_id', 50);
            $table->timestamp('taken_at')->nullable();
            $table->timestamp('created_at')->nullable();

            $table->index(['user_id', 'taken_at']);
        });

        // Add medication_times column to elder_settings if not exists
        if (!Schema::hasColumn('elder_settings', 'medication_times')) {
            Schema::table('elder_settings', function (Blueprint $table) {
                $table->json('medication_times')->nullable()->after('notes');
            });
        }
    }

    public function down(): void
    {
        Schema::dropIfExists('elder_medication_logs');
        Schema::dropIfExists('elder_sos_alerts');
        Schema::dropIfExists('elder_health_records');

        if (Schema::hasColumn('elder_settings', 'medication_times')) {
            Schema::table('elder_settings', function (Blueprint $table) {
                $table->dropColumn('medication_times');
            });
        }
    }
};
