<?php

namespace App\Http\Controllers\API;

use App\Http\Controllers\Controller;
use App\Models\JobPost;
use App\Models\JobApplication;
use App\Models\JobPromotion;
use App\Traits\AdminAuthorizes;
use App\Traits\CompressesUploads;
use Illuminate\Http\Request;

class JobController extends Controller
{
    use AdminAuthorizes, CompressesUploads;

    public function index(Request $request)
    {
        // 만료된 프로모션 자동 해제
        JobPost::where('promotion_tier', '!=', 'none')
            ->where('promotion_expires_at', '<', now())
            ->update(['promotion_tier' => 'none', 'promotion_expires_at' => null]);

        $query = JobPost::with('user:id,name,nickname')
            ->active()
            ->when($request->post_type, fn($q, $v) => $q->where('post_type', $v))
            ->when($request->category, fn($q, $v) => $q->where('category', $v))
            ->when($request->type, fn($q, $v) => $q->where('type', $v))
            ->when($request->search, fn($q, $v) => $q->where('title', 'like', "%{$v}%"))
            ->when($request->state, fn($q, $v) => $q->where('state', $v));

        if ($request->lat && $request->lng) {
            $query->nearby($request->lat, $request->lng, $request->radius ?? 50);
        }

        // 프로모션 우선 정렬: national > state_plus > sponsored > 최신
        $query->orderByRaw("CASE promotion_tier WHEN 'national' THEN 1 WHEN 'state_plus' THEN 2 WHEN 'sponsored' THEN 3 ELSE 4 END")
              ->orderByDesc('created_at');

        return response()->json(['success' => true, 'data' => $query->paginate($request->per_page ?? 20)]);
    }

    // 프로모션 슬롯 현황 조회
    public function promotionSlots(Request $request)
    {
        $tier = $request->tier ?: 'national';
        $state = $request->state;

        $query = JobPost::where('promotion_tier', $tier)
            ->where('promotion_expires_at', '>', now());

        if ($tier === 'state_plus' && $state) {
            $query->whereJsonContains('promotion_states', $state);
        }

        $active = $query->orderBy('promotion_expires_at')->get(['id', 'title', 'promotion_expires_at']);
        $used = $active->count();
        $available = max(JobPromotion::MAX_SLOTS - $used, 0);

        $nextSlotTime = $used >= JobPromotion::MAX_SLOTS ? $active->first()?->promotion_expires_at : null;

        return response()->json([
            'success' => true,
            'data' => [
                'tier' => $tier,
                'max_slots' => JobPromotion::MAX_SLOTS,
                'used' => $used,
                'available' => $available,
                'daily_cost' => JobPromotion::pricePerDay($tier),
                'next_slot_time' => $nextSlotTime,
            ]
        ]);
    }

    // 프로모션 구매
    public function promote(Request $request, $id)
    {
        $job = $this->findOwnedOrAdmin(JobPost::class, $id);

        $request->validate([
            'tier' => 'required|in:national,state_plus,sponsored',
            'days' => 'required|integer|min:1|max:90',
            'states' => 'nullable|array',
        ]);

        $tier = $request->tier;
        $days = (int) $request->days;
        $dailyCost = JobPromotion::pricePerDay($tier);
        $totalCost = $dailyCost * $days;

        // 슬롯 체크
        if ($tier !== 'sponsored') {
            $slotQuery = JobPost::where('promotion_tier', $tier)->where('promotion_expires_at', '>', now());
            if ($tier === 'state_plus' && $request->states) {
                $slotQuery->where(function ($q) use ($request) {
                    foreach ($request->states as $st) $q->orWhereJsonContains('promotion_states', $st);
                });
            }
            if ($slotQuery->count() >= JobPromotion::MAX_SLOTS) {
                return response()->json(['success' => false, 'message' => '슬롯이 모두 사용 중입니다'], 422);
            }
        }

        // 포인트 차감
        $user = auth()->user();
        if ($user->points < $totalCost) {
            return response()->json(['success' => false, 'message' => '포인트가 부족합니다'], 422);
        }

        $user->addPoints(-$totalCost, 'job_promotion', "구인 상위노출 ({$tier}, {$days}일)");

        $startsAt = now();
        $expiresAt = now()->addDays($days);

        JobPromotion::create([
            'job_post_id' => $id,
            'user_id' => auth()->id(),
            'tier' => $tier,
            'states' => $request->states,
            'days' => $days,
            'daily_cost' => $dailyCost,
            'total_cost' => $totalCost,
            'starts_at' => $startsAt,
            'expires_at' => $expiresAt,
            'status' => 'active',
        ]);

        $job->update([
            'promotion_tier' => $tier,
            'promotion_expires_at' => $expiresAt,
            'promotion_states' => $request->states,
        ]);

        return response()->json(['success' => true, 'message' => '상위노출이 적용되었습니다']);
    }

    public function show($id)
    {
        $job = JobPost::with('user:id,name,nickname,avatar')->findOrFail($id);
        $job->increment('view_count');
        return response()->json(['success' => true, 'data' => $job]);
    }

    public function store(Request $request)
    {
        $postType = $request->post_type ?? 'hiring';
        $rules = [
            'title' => 'required|max:200',
            'content' => 'required',
            'category' => 'required|max:30',
            'type' => 'required|in:full,part,contract',
            'post_type' => 'sometimes|in:hiring,seeking',
            'logo' => 'nullable|image|max:5120',
            'company_pdf' => 'nullable|mimes:pdf|max:10240',
            'salary_min' => 'nullable|integer|min:0',
            'salary_max' => 'nullable|integer|min:0',
            'salary_type' => 'nullable|in:hourly,monthly,yearly',
            'city' => 'nullable|max:100',
            'state' => 'nullable|max:10',
            'zipcode' => 'nullable|max:10',
            'contact_email' => 'nullable|email|max:100',
            'contact_phone' => 'nullable|max:30',
            'expires_at' => 'nullable|date',
        ];
        if ($postType === 'hiring') $rules['company'] = 'required|max:100';
        else $rules['company'] = 'nullable|max:100';

        $request->validate($rules);

        try {
            $data = $request->only('post_type', 'title', 'company', 'content', 'category', 'type', 'salary_min', 'salary_max', 'salary_type', 'lat', 'lng', 'city', 'state', 'zipcode', 'contact_email', 'contact_phone', 'expires_at');
            $data['user_id'] = auth()->id();

            // 빈 문자열은 null 로 변환 (DB 에러 방지)
            foreach (['salary_min','salary_max','salary_type','city','state','zipcode','contact_email','contact_phone','expires_at'] as $k) {
                if (isset($data[$k]) && $data[$k] === '') $data[$k] = null;
            }

            // 리치에디터 content 안에 삽입된 base64 이미지를 파일로 저장하고 URL 로 치환 + 압축
            if (!empty($data['content'])) {
                $data['content'] = $this->extractAndCompressBase64Images($data['content'], 'job_content', 1200, 80);
            }

            // JSON 필드 처리
            if ($request->filled('job_tags')) {
                $tags = is_string($request->job_tags) ? json_decode($request->job_tags, true) : $request->job_tags;
                $data['job_tags'] = is_array($tags) ? $tags : null;
            }
            if ($request->filled('benefits')) {
                $ben = is_string($request->benefits) ? json_decode($request->benefits, true) : $request->benefits;
                $data['benefits'] = is_array($ben) ? $ben : null;
            }

            // 파일 업로드 (로고는 500px로 압축, PDF는 그대로)
            if ($request->hasFile('logo')) {
                $data['logo'] = $this->storeCompressedImage($request->file('logo'), 'job_logos', 500, 82);
            }
            if ($request->hasFile('company_pdf')) {
                $data['company_pdf'] = $this->storeDocument($request->file('company_pdf'), 'job_pdfs');
            }

            $job = JobPost::create($data);
            return response()->json(['success' => true, 'data' => $job], 201);
        } catch (\Throwable $e) {
            \Log::error('JobPost create failed', ['err' => $e->getMessage(), 'user' => auth()->id()]);
            return response()->json([
                'success' => false,
                'message' => '등록 실패: ' . $e->getMessage(),
            ], 500);
        }
    }


    public function update(Request $request, $id)
    {
        $job = $this->findOwnedOrAdmin(JobPost::class, $id);
        try {
            $data = $request->only('post_type', 'title', 'company', 'content', 'category', 'type', 'salary_min', 'salary_max', 'salary_type', 'city', 'state', 'zipcode', 'contact_email', 'contact_phone', 'expires_at', 'is_active');
            foreach (['salary_min','salary_max','salary_type','city','state','zipcode','contact_email','contact_phone','expires_at'] as $k) {
                if (isset($data[$k]) && $data[$k] === '') $data[$k] = null;
            }
            if (!empty($data['content'])) $data['content'] = $this->extractAndCompressBase64Images($data['content'], 'job_content', 1200, 80);
            if ($request->filled('job_tags')) {
                $tags = is_string($request->job_tags) ? json_decode($request->job_tags, true) : $request->job_tags;
                $data['job_tags'] = is_array($tags) ? $tags : null;
            }
            if ($request->filled('benefits')) {
                $ben = is_string($request->benefits) ? json_decode($request->benefits, true) : $request->benefits;
                $data['benefits'] = is_array($ben) ? $ben : null;
            }
            if ($request->hasFile('logo')) {
                $data['logo'] = $this->storeCompressedImage($request->file('logo'), 'job_logos', 500, 82);
            }
            if ($request->hasFile('company_pdf')) {
                $data['company_pdf'] = $this->storeDocument($request->file('company_pdf'), 'job_pdfs');
            }

            $job->update($data);
            return response()->json(['success' => true, 'data' => $job]);
        } catch (\Throwable $e) {
            \Log::error('JobPost update failed', ['err' => $e->getMessage(), 'id' => $id]);
            return response()->json(['success' => false, 'message' => '수정 실패: ' . $e->getMessage()], 500);
        }
    }

    public function destroy($id)
    {
        $this->findOwnedOrAdmin(JobPost::class, $id)->update(['is_active' => false]);
        return response()->json(['success' => true, 'message' => '삭제되었습니다']);
    }

    // 이력서로 지원하기
    public function apply(Request $request, $id)
    {
        $job = JobPost::findOrFail($id);

        // 자기 공고에 지원 불가
        if ($job->user_id === auth()->id()) {
            return response()->json(['success' => false, 'message' => '본인 공고에는 지원할 수 없습니다'], 422);
        }

        // 중복 지원 체크
        $exists = JobApplication::where('job_post_id', $id)
            ->where('user_id', auth()->id())
            ->exists();

        if ($exists) {
            return response()->json(['success' => false, 'message' => '이미 지원한 공고입니다'], 422);
        }

        $application = JobApplication::create([
            'job_post_id' => $id,
            'user_id' => auth()->id(),
            'resume_id' => $request->resume_id,
            'message' => $request->message,
        ]);

        return response()->json(['success' => true, 'data' => $application, 'message' => '지원이 완료되었습니다']);
    }

    // 내가 올린 구인/구직 공고 목록 (대시보드용)
    public function myPosts()
    {
        $posts = JobPost::where('user_id', auth()->id())
            ->orderByDesc('created_at')
            ->get(['id', 'post_type', 'title', 'company', 'category', 'type', 'logo', 'city', 'state', 'is_active', 'view_count', 'promotion_tier', 'promotion_expires_at', 'expires_at', 'created_at']);

        return response()->json(['success' => true, 'data' => $posts]);
    }

    // 내 지원 내역
    public function myApplications()
    {
        $apps = JobApplication::with(['jobPost:id,title,company,city,state,category', 'resume:id,title'])
            ->where('user_id', auth()->id())
            ->orderByDesc('created_at')
            ->paginate(20);

        return response()->json(['success' => true, 'data' => $apps]);
    }

    // 내 공고에 들어온 지원자 목록
    public function applicants($id)
    {
        $job = JobPost::where('user_id', auth()->id())->findOrFail($id);

        $apps = JobApplication::with(['user:id,name,nickname,avatar', 'resume'])
            ->where('job_post_id', $id)
            ->orderByDesc('created_at')
            ->get();

        return response()->json(['success' => true, 'data' => $apps]);
    }
}
