<?php
use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration {
    public function up(): void {
        if (!Schema::hasTable('payments')) {
            Schema::create('payments', function (Blueprint $t) {
                $t->id();
                $t->foreignId('user_id')->constrained()->onDelete('cascade');
                $t->string('transaction_id')->unique()->nullable();
                $t->string('type'); // 포인트충전,프리미엄,공동구매,업소등록
                $t->string('item_name');
                $t->decimal('amount', 10, 2);
                $t->string('currency', 3)->default('USD');
                $t->string('payment_method')->default('card'); // card,apple_pay,google_pay
                $t->string('card_brand')->nullable(); // visa,mastercard,amex
                $t->string('card_last4')->nullable();
                $t->string('status')->default('pending'); // pending,success,failed,refunded
                $t->string('stripe_payment_id')->nullable();
                $t->text('memo')->nullable();
                $t->timestamp('paid_at')->nullable();
                $t->timestamps();
            });
        }
    }
    public function down(): void { Schema::dropIfExists('payments'); }
};
