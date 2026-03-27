<?php
use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration {
    public function up(): void {
        Schema::table('users', function (Blueprint $table) {
            $table->string('username')->unique()->nullable()->after('name');
            $table->string('phone')->nullable()->after('email');
            $table->string('avatar')->nullable();
            $table->string('region')->nullable();
            $table->string('address')->nullable();
            $table->decimal('lat', 10, 7)->nullable();
            $table->decimal('lng', 10, 7)->nullable();
            $table->enum('level', ['씨앗','새싹','나무','숲','참나무'])->default('씨앗');
            $table->bigInteger('points_total')->default(0);
            $table->decimal('cash_balance', 10, 2)->default(0);
            $table->string('phone_verified_at')->nullable();
            $table->boolean('is_elder')->default(false);
            $table->boolean('is_driver')->default(false);
            $table->string('lang')->default('ko');
            $table->enum('status', ['active','banned','suspended'])->default('active');
            $table->boolean('is_admin')->default(false);
            $table->timestamp('last_login_at')->nullable();
            $table->string('bio')->nullable();
        });
    }
    public function down(): void {
        Schema::table('users', function (Blueprint $table) {
            $table->dropColumn(['username','phone','avatar','region','address','lat','lng','level','points_total','cash_balance','phone_verified_at','is_elder','is_driver','lang','status','is_admin','last_login_at','bio']);
        });
    }
};
