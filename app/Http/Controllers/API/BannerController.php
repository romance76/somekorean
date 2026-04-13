<?php

namespace App\Http\Controllers\API;

use App\Http\Controllers\Controller;
use App\Models\BannerAd;
use Illuminate\Http\Request;

class BannerController extends Controller
{
    // 공개: 특정 페이지/위치의 활성 광고 가져오기 (지역 타겟팅 포함)
    public function show(Request $request)
    {
        $page = $request->page ?: 'home';
        $position = $request->position ?: 'left';
        $limit = $request->limit ?: 5;

        // 유저 지역 정보 (로그인 시)
        $user = auth('api')->user();
        $userState = $user->state ?? null;
        $userCounty = $user->city ?? null; // city 필드를 county 매칭에도 사용

        $query = BannerAd::active()
            ->where('position', $position)
            ->where(function ($q) use ($page) {
                $q->where('page', $page)
                  ->orWhere('page', 'all')
                  ->orWhereJsonContains('target_pages', $page);
            });

        // 지역 타겟팅: 로그인=로컬 우선(카운티>주>전국), 비로그인=전국만
        if ($user && $userState) {
            $banners = $query->where(function ($q) use ($userState, $userCounty) {
                    $q->where('geo_scope', 'all')
                      ->orWhere(function ($q2) use ($userState) {
                          $q2->where('geo_scope', 'state')->where('geo_value', $userState);
                      })
                      ->orWhere(function ($q2) use ($userCounty) {
                          $q2->where('geo_scope', 'county')->where('geo_value', $userCounty);
                      });
                })
                ->orderByRaw("
                    CASE
                        WHEN geo_scope = 'county' AND geo_value = ? THEN 1
                        WHEN geo_scope = 'state' AND geo_value = ? THEN 2
                        WHEN geo_scope = 'all' THEN 3
                        ELSE 4
                    END
                ", [$userCounty, $userState])
                ->orderByDesc('bid_amount')
                ->limit($limit)
                ->get();
        } else {
            $banners = $query->where('geo_scope', 'all')
                ->orderByDesc('bid_amount')
                ->limit($limit)
                ->get();
        }

        // 노출 수 증가
        if ($banners->count()) {
            BannerAd::whereIn('id', $banners->pluck('id'))->increment('impressions');
        }

        return response()->json(['success' => true, 'data' => $banners]);
    }

    // 배너 클릭 추적
    public function click($id)
    {
        BannerAd::where('id', $id)->increment('clicks');
        return response()->json(['success' => true]);
    }

    // 유저: 내 배너 신청 목록
    public function myBanners()
    {
        $banners = BannerAd::where('user_id', auth()->id())
            ->orderByDesc('created_at')
            ->get();
        return response()->json(['success' => true, 'data' => $banners]);
    }

    // 유저: 광고 입찰 신청 (월간 경매)
    public function store(Request $request)
    {
        $request->validate([
            'title' => 'required|max:100',
            'image' => 'required|image|max:5120',
            'link_url' => 'nullable|url',
            'page' => 'required|in:home,sub,all',
            'position' => 'required|in:left,right',
            'slot_number' => 'required|integer|min:1|max:5',
            'geo_scope' => 'required|in:all,state,county',
            // city 제외 — 전국/주/카운티만
            'geo_value' => 'nullable|string|max:100',
            'bid_amount' => 'required|integer|min:50',
        ]);

        $bidAmount = (int) $request->bid_amount;
        $targetPages = json_decode($request->target_pages, true) ?: [$request->page];

        // 포인트 확인
        $user = auth()->user();
        if ($user->points < $bidAmount) {
            return response()->json([
                'success' => false,
                'message' => "포인트 부족. 입찰: {$bidAmount}P, 보유: {$user->points}P"
            ], 422);
        }

        $imagePath = $request->file('image')->store('banners', 'public');

        // 다음 달 1일~말일로 설정
        $nextMonth = now()->addMonth();
        $startDate = $nextMonth->copy()->startOfMonth();
        $endDate = $nextMonth->copy()->endOfMonth();
        $auctionMonth = $nextMonth->format('Y-m');

        $banner = BannerAd::create([
            'user_id' => $user->id,
            'title' => $request->title,
            'image_url' => '/storage/' . $imagePath,
            'link_url' => $request->link_url,
            'page' => $request->page,
            'target_pages' => $targetPages,
            'position' => $request->position,
            'slot_number' => $request->slot_number,
            'geo_scope' => $request->geo_scope,
            'geo_value' => $request->geo_value,
            'start_date' => $startDate,
            'end_date' => $endDate,
            'auction_month' => $auctionMonth,
            'bid_amount' => $bidAmount,
            'daily_cost' => $bidAmount,
            'total_cost' => $bidAmount,
            'status' => 'pending',
        ]);

        // 포인트 차감
        $user->addPoints(-$bidAmount, "광고 입찰: {$request->title} ({$auctionMonth})", 'banner');

        return response()->json([
            'success' => true,
            'message' => "입찰 완료! {$bidAmount}P 차감. {$auctionMonth} 경매 결과에 따라 배정됩니다.",
            'data' => $banner,
        ], 201);
    }
}
