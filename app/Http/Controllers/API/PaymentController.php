<?php
namespace App\Http\Controllers\API;

use App\Http\Controllers\Controller;
use App\Models\Payment;
use App\Models\User;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Facades\Http;
use Illuminate\Support\Str;

class PaymentController extends Controller
{
    // 포인트 구매 패키지
    private $packages = [
        ['id' => 'pkg_5',  'amount' => 500,  'points' => 1000,  'bonus' => 0,  'label' => '$5 - 1,000P'],
        ['id' => 'pkg_10', 'amount' => 1000, 'points' => 2500,  'bonus' => 25, 'label' => '$10 - 2,500P (+25%)'],
        ['id' => 'pkg_25', 'amount' => 2500, 'points' => 7000,  'bonus' => 40, 'label' => '$25 - 7,000P (+40%)'],
        ['id' => 'pkg_50', 'amount' => 5000, 'points' => 16000, 'bonus' => 60, 'label' => '$50 - 16,000P (+60%)'],
    ];

    /**
     * GET /api/payments/packages
     * 구매 가능 패키지 목록
     */
    public function packages()
    {
        return response()->json($this->packages);
    }

    /**
     * POST /api/payments/create-intent
     * Stripe PaymentIntent 생성
     */
    public function createIntent(Request $request)
    {
        $packageId = $request->input('package_id');
        $package = collect($this->packages)->firstWhere('id', $packageId);

        if (!$package) {
            return response()->json(['error' => 'Invalid package'], 400);
        }

        $stripeSecret = config('services.stripe.secret');
        if (!$stripeSecret) {
            return response()->json(['error' => 'Stripe is not configured'], 500);
        }

        $response = Http::asForm()->withBasicAuth($stripeSecret, '')
            ->post('https://api.stripe.com/v1/payment_intents', [
                'amount'               => $package['amount'],
                'currency'             => 'usd',
                'metadata[user_id]'    => auth()->id(),
                'metadata[package_id]' => $packageId,
                'metadata[points]'     => $package['points'],
            ]);

        if (!$response->successful()) {
            return response()->json(['error' => 'Failed to create payment intent', 'detail' => $response->json()], 500);
        }

        return response()->json([
            'clientSecret' => $response->json('client_secret'),
            'amount'       => $package['amount'],
            'points'       => $package['points'],
        ]);
    }

    /**
     * POST /api/payments/confirm
     * 결제 확인 후 포인트 지급
     */
    public function confirm(Request $request)
    {
        $paymentIntentId = $request->input('payment_intent_id');

        if (!$paymentIntentId) {
            return response()->json(['error' => 'payment_intent_id is required'], 400);
        }

        $stripeSecret = config('services.stripe.secret');

        // Stripe에서 PaymentIntent 조회
        $response = Http::asForm()->withBasicAuth($stripeSecret, '')
            ->get("https://api.stripe.com/v1/payment_intents/{$paymentIntentId}");

        if (!$response->successful()) {
            return response()->json(['error' => 'Failed to retrieve payment intent'], 500);
        }

        $pi = $response->json();

        if (($pi['status'] ?? '') !== 'succeeded') {
            return response()->json(['error' => 'Payment not completed', 'status' => $pi['status'] ?? 'unknown'], 400);
        }

        $userId    = $pi['metadata']['user_id'] ?? auth()->id();
        $points    = (int)($pi['metadata']['points'] ?? 0);
        $packageId = $pi['metadata']['package_id'] ?? 'unknown';

        // 중복 처리 방지
        $existing = Payment::where('stripe_payment_id', $paymentIntentId)->first();
        if ($existing) {
            return response()->json(['error' => 'Already processed'], 400);
        }

        // 트랜잭션으로 처리
        DB::beginTransaction();
        try {
            // user_wallets 테이블 업데이트
            DB::table('user_wallets')->where('user_id', $userId)->increment('coin_balance', $points);

            $newBalance = DB::table('user_wallets')->where('user_id', $userId)->value('coin_balance');

            // Payment 기록
            Payment::create([
                'user_id'           => $userId,
                'transaction_id'    => Str::uuid(),
                'type'              => 'point_purchase',
                'item_name'         => $packageId,
                'amount'            => $pi['amount'] / 100,
                'currency'          => 'usd',
                'payment_method'    => 'stripe',
                'status'            => 'completed',
                'stripe_payment_id' => $paymentIntentId,
                'paid_at'           => now(),
            ]);

            // wallet_transactions 기록
            DB::table('wallet_transactions')->insert([
                'user_id'       => $userId,
                'type'          => 'purchase',
                'currency'      => 'coin',
                'amount'        => $points,
                'balance_after' => $newBalance,
                'description'   => "포인트 구매: {$points}P",
                'created_at'    => now(),
                'updated_at'    => now(),
            ]);

            DB::commit();

            return response()->json([
                'success' => true,
                'points'  => $points,
                'balance' => $newBalance,
            ]);
        } catch (\Exception $e) {
            DB::rollBack();
            return response()->json(['error' => 'Failed to process payment: ' . $e->getMessage()], 500);
        }
    }

    /**
     * GET /api/payments/history
     * 결제 내역
     */
    public function history()
    {
        return Payment::where('user_id', auth()->id())
            ->orderBy('created_at', 'desc')
            ->paginate(20);
    }
}
