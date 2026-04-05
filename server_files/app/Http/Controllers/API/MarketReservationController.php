<?php

namespace App\Http\Controllers\API;

use App\Http\Controllers\Controller;
use App\Models\MarketItem;
use App\Models\MarketReservation;
use App\Models\Notification;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Auth;
use Illuminate\Support\Facades\DB;

class MarketReservationController extends Controller
{
    /**
     * POST /api/market/{id}/reserve - 찜하기
     */
    public function reserve($itemId)
    {
        $item = MarketItem::findOrFail($itemId);

        // 자기 물건 찜 불가
        if ($item->user_id === Auth::id()) {
            return response()->json(['message' => '자신의 물품은 찜할 수 없습니다.'], 403);
        }

        // 판매완료/삭제된 물품 찜 불가
        if ($item->status === 'sold') {
            return response()->json(['message' => '이미 판매완료된 물품입니다.'], 400);
        }

        // 이미 pending 찜이 있는지 확인 (1아이템 1찜)
        $existingReservation = MarketReservation::where('market_item_id', $item->id)
            ->where('status', 'pending')
            ->first();

        if ($existingReservation) {
            if ($existingReservation->buyer_id === Auth::id()) {
                return response()->json(['message' => '이미 찜한 물품입니다.'], 400);
            }
            return response()->json(['message' => '다른 사용자가 이미 찜한 물품입니다.'], 400);
        }

        $points = (int) ($item->reservation_points ?? 0);
        $hours = (int) ($item->reservation_hours ?? 24);

        // 보증금이 있으면 포인트 확인 및 차감
        if ($points > 0) {
            $wallet = DB::table('user_wallets')->where('user_id', Auth::id())->first();
            $coinBalance = $wallet ? (int) $wallet->coin_balance : 0;

            if ($coinBalance < $points) {
                return response()->json([
                    'message' => "보증금이 부족합니다. 필요: {$points}P, 보유: {$coinBalance}P",
                ], 400);
            }

            // 포인트 차감
            DB::table('user_wallets')->where('user_id', Auth::id())->update([
                'coin_balance' => DB::raw('coin_balance - ' . $points),
                'updated_at' => now(),
            ]);
            DB::table('wallet_transactions')->insert([
                'user_id' => Auth::id(),
                'type' => 'reservation_hold',
                'currency' => 'coin',
                'amount' => -$points,
                'balance_after' => $coinBalance - $points,
                'description' => "찜 보증금 ({$item->title})",
                'created_at' => now(),
                'updated_at' => now(),
            ]);
        }

        // 찜 레코드 생성
        $reservation = MarketReservation::create([
            'market_item_id' => $item->id,
            'buyer_id' => Auth::id(),
            'seller_id' => $item->user_id,
            'points_held' => $points,
            'status' => 'pending',
            'expires_at' => now()->addHours($hours),
        ]);

        // 아이템 상태를 예약중으로 변경
        $item->update(['status' => 'reserved']);

        // 판매자에게 알림
        Notification::create([
            'user_id' => $item->user_id,
            'type' => 'market_reservation',
            'title' => '찜 알림',
            'body' => Auth::user()->name . '님이 "' . mb_substr($item->title, 0, 20) . '" 물품을 찜했습니다.',
            'data' => json_encode(['item_id' => $item->id, 'reservation_id' => $reservation->id]),
            'url' => '/market/' . $item->id,
        ]);

        // 구매자에게 알림
        Notification::create([
            'user_id' => Auth::id(),
            'type' => 'market_reservation',
            'title' => '찜 완료',
            'body' => '"' . mb_substr($item->title, 0, 20) . '" 물품을 찜했습니다. ' . $hours . '시간 이내에 연락해주세요.',
            'data' => json_encode(['item_id' => $item->id, 'reservation_id' => $reservation->id]),
            'url' => '/market/' . $item->id,
        ]);

        return response()->json([
            'message' => '찜이 완료되었습니다.',
            'reservation' => $reservation->load(['buyer:id,name', 'seller:id,name']),
        ], 201);
    }

    /**
     * POST /api/market/reservations/{id}/complete - 거래 성사
     */
    public function complete($id)
    {
        $reservation = MarketReservation::findOrFail($id);

        // 찜 소유자(구매자) 또는 판매자만 가능
        if ($reservation->buyer_id !== Auth::id() && $reservation->seller_id !== Auth::id()) {
            return response()->json(['message' => '권한이 없습니다.'], 403);
        }

        if ($reservation->status !== 'pending') {
            return response()->json(['message' => '이미 처리된 찜입니다.'], 400);
        }

        // 포인트를 구매자에게 반환 (거래 성사 시)
        if ($reservation->points_held > 0) {
            $wallet = DB::table('user_wallets')->where('user_id', $reservation->buyer_id)->first();
            $newBalance = ($wallet ? (int) $wallet->coin_balance : 0) + $reservation->points_held;

            DB::table('user_wallets')->where('user_id', $reservation->buyer_id)->update([
                'coin_balance' => DB::raw('coin_balance + ' . $reservation->points_held),
                'updated_at' => now(),
            ]);
            DB::table('wallet_transactions')->insert([
                'user_id' => $reservation->buyer_id,
                'type' => 'reservation_refund',
                'currency' => 'coin',
                'amount' => $reservation->points_held,
                'balance_after' => $newBalance,
                'description' => '찜 보증금 반환 (거래 성사)',
                'created_at' => now(),
                'updated_at' => now(),
            ]);
        }

        // 상태 변경
        $reservation->update([
            'status' => 'completed',
            'completed_at' => now(),
        ]);

        // 아이템 상태를 sold로 변경
        $item = MarketItem::find($reservation->market_item_id);
        if ($item) {
            $item->update(['status' => 'sold']);
        }

        // 양쪽에 알림
        $otherUserId = Auth::id() === $reservation->buyer_id
            ? $reservation->seller_id
            : $reservation->buyer_id;

        Notification::create([
            'user_id' => $otherUserId,
            'type' => 'market_reservation_complete',
            'title' => '거래 완료',
            'body' => ($item ? '"' . mb_substr($item->title, 0, 20) . '"' : '물품') . ' 거래가 완료되었습니다.',
            'data' => json_encode(['item_id' => $reservation->market_item_id]),
            'url' => '/market/' . $reservation->market_item_id,
        ]);

        return response()->json([
            'message' => '거래가 완료되었습니다.',
            'reservation' => $reservation,
        ]);
    }

    /**
     * POST /api/market/reservations/{id}/cancel - 취소
     */
    public function cancel($id)
    {
        $reservation = MarketReservation::findOrFail($id);

        // 구매자만 취소 가능
        if ($reservation->buyer_id !== Auth::id()) {
            return response()->json(['message' => '구매자만 찜을 취소할 수 있습니다.'], 403);
        }

        if ($reservation->status !== 'pending') {
            return response()->json(['message' => '이미 처리된 찜입니다.'], 400);
        }

        // 보증금 50% 판매자, 50% 구매자 반환
        if ($reservation->points_held > 0) {
            $buyerRefund = (int) floor($reservation->points_held / 2);
            $sellerShare = $reservation->points_held - $buyerRefund;

            // 구매자에게 50% 반환
            if ($buyerRefund > 0) {
                $buyerWallet = DB::table('user_wallets')->where('user_id', $reservation->buyer_id)->first();
                $buyerNewBalance = ($buyerWallet ? (int) $buyerWallet->coin_balance : 0) + $buyerRefund;

                DB::table('user_wallets')->where('user_id', $reservation->buyer_id)->update([
                    'coin_balance' => DB::raw('coin_balance + ' . $buyerRefund),
                    'updated_at' => now(),
                ]);
                DB::table('wallet_transactions')->insert([
                    'user_id' => $reservation->buyer_id,
                    'type' => 'reservation_cancel_refund',
                    'currency' => 'coin',
                    'amount' => $buyerRefund,
                    'balance_after' => $buyerNewBalance,
                    'description' => '찜 취소 보증금 반환 (50%)',
                    'created_at' => now(),
                    'updated_at' => now(),
                ]);
            }

            // 판매자에게 50% 지급
            if ($sellerShare > 0) {
                $sellerWallet = DB::table('user_wallets')->where('user_id', $reservation->seller_id)->first();
                if (!$sellerWallet) {
                    // 판매자 지갑이 없으면 생성
                    DB::table('user_wallets')->insert([
                        'user_id' => $reservation->seller_id,
                        'star_balance' => 0, 'gem_balance' => 0,
                        'coin_balance' => 0, 'chip_balance' => 0,
                        'lifetime_earned' => 0,
                        'created_at' => now(), 'updated_at' => now(),
                    ]);
                    $sellerWallet = DB::table('user_wallets')->where('user_id', $reservation->seller_id)->first();
                }
                $sellerNewBalance = (int) $sellerWallet->coin_balance + $sellerShare;

                DB::table('user_wallets')->where('user_id', $reservation->seller_id)->update([
                    'coin_balance' => DB::raw('coin_balance + ' . $sellerShare),
                    'lifetime_earned' => DB::raw('lifetime_earned + ' . $sellerShare),
                    'updated_at' => now(),
                ]);
                DB::table('wallet_transactions')->insert([
                    'user_id' => $reservation->seller_id,
                    'type' => 'reservation_cancel_penalty',
                    'currency' => 'coin',
                    'amount' => $sellerShare,
                    'balance_after' => $sellerNewBalance,
                    'description' => '구매자 찜 취소 위약금 수령',
                    'created_at' => now(),
                    'updated_at' => now(),
                ]);
            }
        }

        // 상태 변경
        $reservation->update([
            'status' => 'cancelled',
            'cancelled_at' => now(),
        ]);

        // 아이템 상태를 다시 active로 복원
        $item = MarketItem::find($reservation->market_item_id);
        if ($item && $item->status === 'reserved') {
            $item->update(['status' => 'active']);
        }

        // 판매자에게 알림
        Notification::create([
            'user_id' => $reservation->seller_id,
            'type' => 'market_reservation_cancel',
            'title' => '찜 취소',
            'body' => ($item ? '"' . mb_substr($item->title, 0, 20) . '"' : '물품') . ' 찜이 취소되었습니다.',
            'data' => json_encode(['item_id' => $reservation->market_item_id]),
            'url' => '/market/' . $reservation->market_item_id,
        ]);

        return response()->json([
            'message' => '찜이 취소되었습니다.',
            'reservation' => $reservation,
        ]);
    }

    /**
     * GET /api/market/reservations/my - 내 찜 목록
     */
    public function myReservations()
    {
        $userId = Auth::id();

        $asBuyer = MarketReservation::with(['marketItem:id,title,price,images,status', 'seller:id,name'])
            ->where('buyer_id', $userId)
            ->orderByDesc('created_at')
            ->get();

        $asSeller = MarketReservation::with(['marketItem:id,title,price,images,status', 'buyer:id,name'])
            ->where('seller_id', $userId)
            ->orderByDesc('created_at')
            ->get();

        return response()->json([
            'as_buyer' => $asBuyer,
            'as_seller' => $asSeller,
        ]);
    }
}
