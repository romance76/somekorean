import paramiko, base64, sys
sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1)
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('68.183.60.70', username='root', password='EhdRh0817wodl', timeout=15)
def ssh(cmd, timeout=180):
    _, out, _ = c.exec_command(cmd, timeout=timeout)
    return out.read().decode('utf-8', errors='replace').strip()
def write_file(path, content):
    enc = base64.b64encode(content.encode('utf-8')).decode('ascii')
    chunks = [enc[i:i+2000] for i in range(0, len(enc), 2000)]
    ssh('rm -f /tmp/wf_chunk')
    for p in chunks:
        ssh(f"printf '%s' '{p}' >> /tmp/wf_chunk")
    ssh(f'cat /tmp/wf_chunk | base64 -d > {path} && rm -f /tmp/wf_chunk')
    print(f'Written {path}: {ssh(f"wc -c < {path}")} bytes')

# Task 1: BusinessClaimController.php
business_claim_controller = r'''<?php
namespace App\Http\Controllers\API;
use App\Http\Controllers\Controller;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Facades\Auth;
use Illuminate\Support\Facades\Storage;
use Illuminate\Support\Facades\Mail;
use Illuminate\Support\Str;

class BusinessClaimController extends Controller
{
    // POST /api/businesses/{id}/claim — 클레임 시작
    public function initiate(Request $req, $businessId)
    {
        $user = Auth::user();
        $business = DB::table('businesses')->where('id', $businessId)->first();
        if (!$business) return response()->json(['error' => '업소를 찾을 수 없습니다'], 404);
        if ($business->is_claimed) return response()->json(['error' => '이미 등록된 업소입니다'], 409);

        // Check if user already has a pending claim
        $existing = DB::table('business_claims')
            ->where('business_id', $businessId)
            ->where('user_id', $user->id)
            ->whereIn('status', ['pending'])
            ->first();
        if ($existing) return response()->json(['error' => '이미 신청 중인 클레임이 있습니다', 'claim_id' => $existing->id], 409);

        $req->validate(['method' => 'required|in:document,email,kakao']);

        $claimId = DB::table('business_claims')->insertGetId([
            'business_id' => $businessId,
            'user_id' => $user->id,
            'method' => $req->method_type ?? $req->input('method'),
            'status' => 'pending',
            'submitted_at' => now(),
            'created_at' => now(),
            'updated_at' => now(),
        ]);

        return response()->json(['success' => true, 'claim_id' => $claimId, 'message' => '소유권 신청이 시작되었습니다']);
    }

    // POST /api/claims/{id}/email — 이메일 인증 발송
    public function sendEmailVerification(Request $req, $claimId)
    {
        $user = Auth::user();
        $claim = DB::table('business_claims')->where('id', $claimId)->where('user_id', $user->id)->first();
        if (!$claim) return response()->json(['error' => '클레임을 찾을 수 없습니다'], 404);

        $req->validate(['email' => 'required|email']);
        $token = Str::random(64);

        DB::table('business_claims')->where('id', $claimId)->update([
            'email_token' => $token,
            'email_verified' => false,
            'updated_at' => now(),
        ]);

        // Send verification email
        $business = DB::table('businesses')->where('id', $claim->business_id)->first();
        $verifyUrl = config('app.url') . '/api/claims/email/verify/' . $token;

        try {
            \Mail::to($req->email)->send(new \App\Mail\ClaimVerificationMail($business->name ?? '업소', $verifyUrl, $user->nickname ?? $user->username));
        } catch (\Exception $e) {
            \Log::error('Claim email error: ' . $e->getMessage());
        }

        return response()->json(['success' => true, 'message' => '인증 이메일이 발송되었습니다']);
    }

    // GET /api/claims/email/verify/{token} — 이메일 인증 확인 (공개)
    public function verifyEmail($token)
    {
        $claim = DB::table('business_claims')->where('email_token', $token)->first();
        if (!$claim) return response()->json(['error' => '유효하지 않은 토큰입니다'], 404);

        DB::table('business_claims')->where('id', $claim->id)->update([
            'email_verified' => true,
            'updated_at' => now(),
        ]);

        return redirect(config('app.url') . '/directory/' . $claim->business_id . '/claim?email_verified=1');
    }

    // POST /api/claims/{id}/documents — 서류 업로드
    public function uploadDocuments(Request $req, $claimId)
    {
        $user = Auth::user();
        $claim = DB::table('business_claims')->where('id', $claimId)->where('user_id', $user->id)->first();
        if (!$claim) return response()->json(['error' => '클레임을 찾을 수 없습니다'], 404);

        $req->validate([
            'documents' => 'required|array|min:1',
            'documents.*' => 'file|mimes:jpg,jpeg,png,pdf|max:10240',
        ]);

        $uploaded = [];
        $dir = 'claims/' . $claimId;
        foreach ($req->file('documents') as $file) {
            $path = $file->store($dir, 'local');
            $uploaded[] = [
                'path' => $path,
                'type' => $file->getClientOriginalName(),
                'size' => $file->getSize(),
                'uploaded_at' => now()->toISOString(),
            ];
        }

        $existing = json_decode($claim->documents ?? '[]', true);
        $all = array_merge($existing, $uploaded);

        DB::table('business_claims')->where('id', $claimId)->update([
            'documents' => json_encode($all),
            'updated_at' => now(),
        ]);

        return response()->json(['success' => true, 'count' => count($uploaded), 'total' => count($all)]);
    }

    // GET /api/claims/{id}/status
    public function status($claimId)
    {
        $user = Auth::user();
        $claim = DB::table('business_claims as bc')
            ->join('businesses as b', 'bc.business_id', '=', 'b.id')
            ->select('bc.*', 'b.name as business_name', 'b.address as business_address')
            ->where('bc.id', $claimId)
            ->where('bc.user_id', $user->id)
            ->first();
        if (!$claim) return response()->json(['error' => '클레임을 찾을 수 없습니다'], 404);
        return response()->json($claim);
    }

    // GET /api/my-claims
    public function myClaims()
    {
        $user = Auth::user();
        $claims = DB::table('business_claims as bc')
            ->join('businesses as b', 'bc.business_id', '=', 'b.id')
            ->select('bc.*', 'b.name as business_name', 'b.address as business_address')
            ->where('bc.user_id', $user->id)
            ->orderByDesc('bc.created_at')
            ->get();
        return response()->json($claims);
    }

    // Admin: GET /api/admin/business-claims
    public function adminList(Request $req)
    {
        $status = $req->query('status', 'pending');
        $claims = DB::table('business_claims as bc')
            ->join('businesses as b', 'bc.business_id', '=', 'b.id')
            ->join('users as u', 'bc.user_id', '=', 'u.id')
            ->select('bc.*', 'b.name as business_name', 'b.address', 'u.nickname', 'u.email as user_email')
            ->when($status !== 'all', fn($q) => $q->where('bc.status', $status))
            ->orderByDesc('bc.submitted_at')
            ->paginate(20);
        return response()->json($claims);
    }

    // Admin: POST /api/admin/business-claims/{id}/approve
    public function approve(Request $req, $claimId)
    {
        $claim = DB::table('business_claims')->where('id', $claimId)->first();
        if (!$claim) return response()->json(['error' => '없음'], 404);

        DB::table('business_claims')->where('id', $claimId)->update([
            'status' => 'approved',
            'admin_note' => $req->input('note', ''),
            'reviewed_at' => now(),
            'reviewed_by' => Auth::id(),
            'updated_at' => now(),
        ]);

        // Update business
        DB::table('businesses')->where('id', $claim->business_id)->update([
            'owner_user_id' => $claim->user_id,
            'is_claimed' => true,
            'updated_at' => now(),
        ]);

        // Send approval email
        $user = DB::table('users')->where('id', $claim->user_id)->first();
        $business = DB::table('businesses')->where('id', $claim->business_id)->first();
        if ($user) {
            try {
                \Mail::to($user->email)->send(new \App\Mail\ClaimApprovedMail($business->name ?? '업소', $user->nickname ?? $user->username));
            } catch (\Exception $e) { \Log::error('Claim approve email: ' . $e->getMessage()); }
        }

        return response()->json(['success' => true]);
    }

    // Admin: POST /api/admin/business-claims/{id}/reject
    public function reject(Request $req, $claimId)
    {
        DB::table('business_claims')->where('id', $claimId)->update([
            'status' => 'rejected',
            'admin_note' => $req->input('note', ''),
            'reviewed_at' => now(),
            'reviewed_by' => Auth::id(),
            'updated_at' => now(),
        ]);
        return response()->json(['success' => true]);
    }
}
'''

# Task 2: OwnerDashboardController.php
owner_dashboard_controller = r'''<?php
namespace App\Http\Controllers\API;
use App\Http\Controllers\Controller;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Facades\Auth;
use Illuminate\Support\Facades\Storage;
use Illuminate\Support\Facades\Validator;

class OwnerDashboardController extends Controller
{
    private function getOwnedBusiness()
    {
        return DB::table('businesses')
            ->where('owner_user_id', Auth::id())
            ->where('status', 'active')
            ->first();
    }

    // GET /api/owner/business
    public function myBusiness()
    {
        $biz = $this->getOwnedBusiness();
        if (!$biz) return response()->json(['error' => '등록된 업소가 없습니다'], 404);

        $biz->events = DB::table('business_events')
            ->where('business_id', $biz->id)
            ->where('is_active', true)
            ->orderByDesc('created_at')->limit(5)->get();

        $biz->recent_reviews = DB::table('business_reviews as r')
            ->join('users as u', 'r.user_id', '=', 'u.id')
            ->select('r.*', 'u.nickname', 'u.profile_image')
            ->where('r.business_id', $biz->id)
            ->where('r.is_visible', true)
            ->orderByDesc('r.created_at')->limit(5)->get();

        // Stats summary (last 30 days)
        $stats = DB::table('business_stats')
            ->where('business_id', $biz->id)
            ->where('stat_date', '>=', now()->subDays(30)->toDateString())
            ->selectRaw('SUM(views) as total_views, SUM(phone_clicks) as total_phone, SUM(direction_clicks) as total_directions, SUM(website_clicks) as total_website')
            ->first();
        $biz->stats_30d = $stats;

        return response()->json($biz);
    }

    // PUT /api/owner/business
    public function update(Request $req)
    {
        $biz = $this->getOwnedBusiness();
        if (!$biz) return response()->json(['error' => '등록된 업소가 없습니다'], 404);

        $allowed = ['name', 'name_ko', 'name_en', 'category', 'address', 'phone', 'website',
                    'owner_description_ko', 'owner_description_en', 'hours', 'temp_closed', 'temp_closed_note'];
        $data = $req->only($allowed);
        $data['updated_at'] = now();

        DB::table('businesses')->where('id', $biz->id)->update($data);
        return response()->json(['success' => true, 'message' => '업소 정보가 업데이트되었습니다']);
    }

    // POST /api/owner/business/photos
    public function uploadPhotos(Request $req)
    {
        $biz = $this->getOwnedBusiness();
        if (!$biz) return response()->json(['error' => '없음'], 404);

        $isPremium = $biz->is_premium;
        $maxPhotos = $isPremium ? 20 : 5;

        $req->validate(['photos' => 'required|array', 'photos.*' => 'image|max:5120']);

        $existing = json_decode($biz->owner_photos ?? '[]', true);
        $remaining = $maxPhotos - count($existing);
        if ($remaining <= 0) return response()->json(['error' => "최대 {$maxPhotos}장까지 업로드 가능합니다"], 422);

        $uploaded = [];
        foreach (array_slice($req->file('photos'), 0, $remaining) as $file) {
            $path = $file->store("businesses/{$biz->id}/photos", 'public');
            $uploaded[] = Storage::url($path);
        }

        $all = array_merge($existing, $uploaded);
        DB::table('businesses')->where('id', $biz->id)->update(['owner_photos' => json_encode($all), 'updated_at' => now()]);

        return response()->json(['success' => true, 'photos' => $all, 'count' => count($all), 'max' => $maxPhotos]);
    }

    // PUT /api/owner/business/photos/reorder
    public function reorderPhotos(Request $req)
    {
        $biz = $this->getOwnedBusiness();
        if (!$biz) return response()->json(['error' => '없음'], 404);
        $req->validate(['photos' => 'required|array']);
        DB::table('businesses')->where('id', $biz->id)->update(['owner_photos' => json_encode($req->input('photos')), 'updated_at' => now()]);
        return response()->json(['success' => true]);
    }

    // DELETE /api/owner/business/photos/{index}
    public function deletePhoto(Request $req, $index)
    {
        $biz = $this->getOwnedBusiness();
        if (!$biz) return response()->json(['error' => '없음'], 404);
        $photos = json_decode($biz->owner_photos ?? '[]', true);
        if (!isset($photos[$index])) return response()->json(['error' => '사진 없음'], 404);
        array_splice($photos, $index, 1);
        DB::table('businesses')->where('id', $biz->id)->update(['owner_photos' => json_encode($photos), 'updated_at' => now()]);
        return response()->json(['success' => true]);
    }

    // POST /api/owner/business/menu-item
    public function upsertMenuItem(Request $req)
    {
        $biz = $this->getOwnedBusiness();
        if (!$biz) return response()->json(['error' => '없음'], 404);
        $req->validate(['name' => 'required|string|max:100']);
        $items = json_decode($biz->menu_items ?? '[]', true);
        $newItem = [
            'id' => uniqid(),
            'name' => $req->input('name'),
            'name_ko' => $req->input('name_ko', ''),
            'price' => $req->input('price', ''),
            'description' => $req->input('description', ''),
            'image_url' => $req->input('image_url', ''),
        ];
        $items[] = $newItem;
        DB::table('businesses')->where('id', $biz->id)->update(['menu_items' => json_encode($items), 'updated_at' => now()]);
        return response()->json(['success' => true, 'item' => $newItem]);
    }

    // DELETE /api/owner/business/menu-item/{itemId}
    public function deleteMenuItem($itemId)
    {
        $biz = $this->getOwnedBusiness();
        if (!$biz) return response()->json(['error' => '없음'], 404);
        $items = json_decode($biz->menu_items ?? '[]', true);
        $items = array_values(array_filter($items, fn($i) => $i['id'] !== $itemId));
        DB::table('businesses')->where('id', $biz->id)->update(['menu_items' => json_encode($items), 'updated_at' => now()]);
        return response()->json(['success' => true]);
    }

    // GET /api/owner/reviews
    public function myReviews(Request $req)
    {
        $biz = $this->getOwnedBusiness();
        if (!$biz) return response()->json(['error' => '없음'], 404);
        $reviews = DB::table('business_reviews as r')
            ->join('users as u', 'r.user_id', '=', 'u.id')
            ->select('r.*', 'u.nickname', 'u.profile_image')
            ->where('r.business_id', $biz->id)
            ->when($req->query('no_reply'), fn($q) => $q->whereNull('r.owner_reply'))
            ->when($req->query('reported'), fn($q) => $q->where('r.report_count', '>', 0))
            ->orderByDesc('r.created_at')
            ->paginate(20);
        return response()->json($reviews);
    }

    // POST /api/owner/reviews/{id}/reply
    public function replyReview(Request $req, $reviewId)
    {
        $biz = $this->getOwnedBusiness();
        if (!$biz) return response()->json(['error' => '없음'], 404);
        $review = DB::table('business_reviews')->where('id', $reviewId)->where('business_id', $biz->id)->first();
        if (!$review) return response()->json(['error' => '리뷰를 찾을 수 없습니다'], 404);
        if ($review->owner_reply) return response()->json(['error' => '이미 답글을 작성했습니다'], 409);
        $req->validate(['reply' => 'required|string|max:1000']);
        DB::table('business_reviews')->where('id', $reviewId)->update([
            'owner_reply' => $req->input('reply'),
            'owner_replied_at' => now(),
            'updated_at' => now(),
        ]);
        return response()->json(['success' => true]);
    }

    // POST /api/owner/reviews/{id}/report
    public function reportReview(Request $req, $reviewId)
    {
        $biz = $this->getOwnedBusiness();
        if (!$biz) return response()->json(['error' => '없음'], 404);
        DB::table('business_reviews')->where('id', $reviewId)->where('business_id', $biz->id)
            ->increment('report_count');
        return response()->json(['success' => true]);
    }

    // GET /api/owner/events
    public function myEvents()
    {
        $biz = $this->getOwnedBusiness();
        if (!$biz) return response()->json(['error' => '없음'], 404);
        $events = DB::table('business_events')->where('business_id', $biz->id)->orderByDesc('created_at')->get();
        return response()->json($events);
    }

    // POST /api/owner/events
    public function createEvent(Request $req)
    {
        $biz = $this->getOwnedBusiness();
        if (!$biz) return response()->json(['error' => '없음'], 404);
        if (!$biz->is_premium) return response()->json(['error' => '프리미엄 업소만 이벤트를 등록할 수 있습니다', 'upgrade_required' => true], 403);
        $req->validate(['title' => 'required|string|max:200']);
        $id = DB::table('business_events')->insertGetId([
            'business_id' => $biz->id,
            'title' => $req->input('title'),
            'content' => $req->input('content'),
            'image_url' => $req->input('image_url'),
            'starts_at' => $req->input('starts_at'),
            'expires_at' => $req->input('expires_at'),
            'is_active' => true,
            'created_at' => now(),
            'updated_at' => now(),
        ]);
        return response()->json(['success' => true, 'id' => $id]);
    }

    // DELETE /api/owner/events/{id}
    public function deleteEvent($eventId)
    {
        $biz = $this->getOwnedBusiness();
        if (!$biz) return response()->json(['error' => '없음'], 404);
        DB::table('business_events')->where('id', $eventId)->where('business_id', $biz->id)->delete();
        return response()->json(['success' => true]);
    }

    // GET /api/owner/stats
    public function stats(Request $req)
    {
        $biz = $this->getOwnedBusiness();
        if (!$biz) return response()->json(['error' => '없음'], 404);
        $days = (int)($req->query('days', 30));
        if (!$biz->is_premium && $days > 7) $days = 7; // Free: 7 days only

        $stats = DB::table('business_stats')
            ->where('business_id', $biz->id)
            ->where('stat_date', '>=', now()->subDays($days)->toDateString())
            ->orderBy('stat_date')
            ->get();

        $totals = [
            'views' => $stats->sum('views'),
            'phone_clicks' => $stats->sum('phone_clicks'),
            'direction_clicks' => $stats->sum('direction_clicks'),
            'website_clicks' => $stats->sum('website_clicks'),
            'bookmark_adds' => $stats->sum('bookmark_adds'),
        ];

        $review_count = DB::table('business_reviews')->where('business_id', $biz->id)->where('is_visible', true)->count();
        $avg_rating = DB::table('business_reviews')->where('business_id', $biz->id)->where('is_visible', true)->avg('rating');

        return response()->json([
            'daily' => $stats,
            'totals' => $totals,
            'review_count' => $review_count,
            'avg_rating' => round($avg_rating, 1),
            'period_days' => $days,
            'is_premium' => (bool)$biz->is_premium,
        ]);
    }
}
'''

# Task 3: AdminBusinessController.php
admin_business_controller = r'''<?php
namespace App\Http\Controllers\API;
use App\Http\Controllers\Controller;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Facades\Auth;

class AdminBusinessController extends Controller
{
    // GET /api/admin/businesses-list
    public function index(Request $req)
    {
        $query = DB::table('businesses as b')
            ->leftJoin('users as u', 'b.owner_user_id', '=', 'u.id')
            ->select('b.*', 'u.nickname as owner_name',
                DB::raw('(SELECT COUNT(*) FROM business_reviews WHERE business_id=b.id) as review_count_actual'),
                DB::raw('(SELECT COUNT(*) FROM business_claims WHERE business_id=b.id AND status="pending") as pending_claims')
            );

        if ($req->search) {
            $s = '%' . $req->search . '%';
            $query->where(fn($q) => $q->where('b.name', 'like', $s)->orWhere('b.address', 'like', $s)->orWhere('b.phone', 'like', $s));
        }
        if ($req->category) $query->where('b.category', $req->category);
        if ($req->is_claimed !== null) $query->where('b.is_claimed', $req->is_claimed);
        if ($req->is_premium !== null) $query->where('b.is_premium', $req->is_premium);
        if ($req->data_source) $query->where('b.data_source', $req->data_source);
        if ($req->region) $query->where('b.region', $req->region);

        $query->orderByDesc('b.is_premium')->orderByDesc('b.created_at');
        return response()->json($query->paginate(30));
    }

    // GET /api/admin/businesses-list/{id}
    public function show($id)
    {
        $biz = DB::table('businesses as b')
            ->leftJoin('users as u', 'b.owner_user_id', '=', 'u.id')
            ->select('b.*', 'u.nickname as owner_name', 'u.email as owner_email')
            ->where('b.id', $id)->first();
        if (!$biz) return response()->json(['error' => '없음'], 404);

        $biz->claims = DB::table('business_claims as c')
            ->join('users as u', 'c.user_id', '=', 'u.id')
            ->select('c.*', 'u.nickname', 'u.email')
            ->where('c.business_id', $id)->orderByDesc('c.created_at')->get();

        $biz->stats = DB::table('business_stats')
            ->where('business_id', $id)
            ->where('stat_date', '>=', now()->subDays(30)->toDateString())
            ->orderBy('stat_date')->get();

        return response()->json($biz);
    }

    // PUT /api/admin/businesses-list/{id}
    public function update(Request $req, $id)
    {
        $data = $req->only(['name','name_ko','name_en','category','address','phone','website',
                            'region','status','is_active','is_premium','premium_type','is_claimed']);
        $data['updated_at'] = now();
        DB::table('businesses')->where('id', $id)->update($data);
        return response()->json(['success' => true]);
    }

    // DELETE /api/admin/businesses-list/{id}
    public function destroy($id)
    {
        DB::table('businesses')->where('id', $id)->update(['status' => 'inactive', 'updated_at' => now()]);
        return response()->json(['success' => true]);
    }

    // GET /api/admin/business-claims-list
    public function claims(Request $req)
    {
        $status = $req->query('status', 'pending');
        return response()->json(
            DB::table('business_claims as c')
                ->join('businesses as b', 'c.business_id', '=', 'b.id')
                ->join('users as u', 'c.user_id', '=', 'u.id')
                ->select('c.*', 'b.name as business_name', 'b.address', 'b.phone',
                         'u.nickname', 'u.email as user_email', 'u.profile_image')
                ->when($status !== 'all', fn($q) => $q->where('c.status', $status))
                ->orderByDesc('c.submitted_at')
                ->paginate(20)
        );
    }

    // POST /api/admin/business-claims-list/{id}/approve
    public function approveClaim(Request $req, $claimId)
    {
        $claim = DB::table('business_claims')->where('id', $claimId)->first();
        if (!$claim) return response()->json(['error' => '없음'], 404);

        DB::table('business_claims')->where('id', $claimId)->update([
            'status' => 'approved', 'admin_note' => $req->input('note', ''),
            'reviewed_at' => now(), 'reviewed_by' => Auth::id(), 'updated_at' => now(),
        ]);
        DB::table('businesses')->where('id', $claim->business_id)->update([
            'owner_user_id' => $claim->user_id, 'is_claimed' => true, 'updated_at' => now(),
        ]);
        // Reject other pending claims for same business
        DB::table('business_claims')->where('business_id', $claim->business_id)
            ->where('id', '!=', $claimId)->where('status', 'pending')
            ->update(['status' => 'rejected', 'updated_at' => now()]);

        return response()->json(['success' => true]);
    }

    // POST /api/admin/business-claims-list/{id}/reject
    public function rejectClaim(Request $req, $claimId)
    {
        DB::table('business_claims')->where('id', $claimId)->update([
            'status' => 'rejected', 'admin_note' => $req->input('note', ''),
            'reviewed_at' => now(), 'reviewed_by' => Auth::id(), 'updated_at' => now(),
        ]);
        return response()->json(['success' => true]);
    }

    // GET /api/admin/business-reviews-list
    public function reviews(Request $req)
    {
        $query = DB::table('business_reviews as r')
            ->join('businesses as b', 'r.business_id', '=', 'b.id')
            ->join('users as u', 'r.user_id', '=', 'u.id')
            ->select('r.*', 'b.name as business_name', 'u.nickname', 'u.email');
        if ($req->query('reported')) $query->where('r.report_count', '>', 0);
        if ($req->query('hidden')) $query->where('r.is_visible', false);
        return response()->json($query->orderByDesc('r.created_at')->paginate(30));
    }

    // POST /api/admin/business-reviews-list/{id}/hide
    public function hideReview($id) {
        DB::table('business_reviews')->where('id', $id)->update(['is_visible' => false, 'updated_at' => now()]);
        return response()->json(['success' => true]);
    }

    // POST /api/admin/business-reviews-list/{id}/restore
    public function restoreReview($id) {
        DB::table('business_reviews')->where('id', $id)->update(['is_visible' => true, 'updated_at' => now()]);
        return response()->json(['success' => true]);
    }

    // DELETE /api/admin/business-reviews-list/{id}
    public function deleteReview($id) {
        DB::table('business_reviews')->where('id', $id)->delete();
        return response()->json(['success' => true]);
    }

    // POST /api/admin/businesses/import (bulk import from crawler)
    public function bulkImport(Request $req)
    {
        $businesses = $req->input('businesses', []);
        if (empty($businesses)) return response()->json(['error' => 'No data'], 422);
        $inserted = 0; $skipped = 0;
        foreach ($businesses as $biz) {
            $name = $biz['name_en'] ?? $biz['name_ko'] ?? $biz['name'] ?? '';
            if (!$name) { $skipped++; continue; }
            $exists = DB::table('businesses')->where('name', $name)->where('address', $biz['address'] ?? '')->exists();
            if ($exists) { $skipped++; continue; }
            DB::table('businesses')->insert([
                'name' => $name, 'name_ko' => $biz['name_ko'] ?? null, 'name_en' => $biz['name_en'] ?? null,
                'category' => $biz['category'] ?? '기타', 'address' => $biz['address'] ?? '',
                'phone' => $biz['phone'] ?? null, 'website' => $biz['website'] ?? null,
                'lat' => $biz['lat'] ?? null, 'lng' => $biz['lng'] ?? null,
                'region' => $biz['region'] ?? null, 'data_source' => 'crawler',
                'source_url' => $biz['source_url'] ?? null, 'status' => 'active',
                'is_active' => 1, 'created_at' => now(), 'updated_at' => now(),
            ]);
            $inserted++;
        }
        return response()->json(['inserted' => $inserted, 'skipped' => $skipped, 'total' => count($businesses)]);
    }
}
'''

# Task 4: Mail classes
claim_verification_mail = r'''<?php
namespace App\Mail;
use Illuminate\Bus\Queueable;
use Illuminate\Mail\Mailable;
use Illuminate\Mail\Mailables\Content;
use Illuminate\Mail\Mailables\Envelope;
use Illuminate\Queue\SerializesModels;

class ClaimVerificationMail extends Mailable
{
    use Queueable, SerializesModels;
    public function __construct(public string $businessName, public string $verifyUrl, public string $userName) {}
    public function envelope(): Envelope { return new Envelope(subject: '[SomeKorean] 업소 이메일 인증'); }
    public function content(): Content {
        return new Content(view: 'emails.claim-verification', with: [
            'businessName' => $this->businessName, 'verifyUrl' => $this->verifyUrl, 'userName' => $this->userName
        ]);
    }
}
'''

claim_approved_mail = r'''<?php
namespace App\Mail;
use Illuminate\Bus\Queueable;
use Illuminate\Mail\Mailable;
use Illuminate\Mail\Mailables\Content;
use Illuminate\Mail\Mailables\Envelope;
use Illuminate\Queue\SerializesModels;

class ClaimApprovedMail extends Mailable
{
    use Queueable, SerializesModels;
    public function __construct(public string $businessName, public string $userName) {}
    public function envelope(): Envelope { return new Envelope(subject: '[SomeKorean] 업소 소유권 신청이 승인되었습니다'); }
    public function content(): Content {
        return new Content(view: 'emails.claim-approved', with: [
            'businessName' => $this->businessName, 'userName' => $this->userName,
            'dashboardUrl' => config('app.url') . '/my-business'
        ]);
    }
}
'''

claim_verification_view = r'''<!DOCTYPE html><html><head><meta charset="UTF-8"><style>body{font-family:sans-serif;max-width:600px;margin:0 auto;padding:20px}.btn{background:#2563eb;color:#fff;padding:12px 24px;border-radius:8px;text-decoration:none;display:inline-block;margin:16px 0}</style></head>
<body>
<h2>업소 이메일 인증</h2>
<p>안녕하세요, {{ $userName }}님!</p>
<p><strong>{{ $businessName }}</strong> 업소의 소유권 신청을 위한 이메일 인증입니다.</p>
<a href="{{ $verifyUrl }}" class="btn">이메일 인증하기</a>
<p style="color:#666;font-size:14px">이 링크는 24시간 후 만료됩니다.</p>
<p style="color:#666;font-size:12px">SomeKorean - 미국 한인 커뮤니티</p>
</body></html>
'''

claim_approved_view = r'''<!DOCTYPE html><html><head><meta charset="UTF-8"><style>body{font-family:sans-serif;max-width:600px;margin:0 auto;padding:20px}.btn{background:#16a34a;color:#fff;padding:12px 24px;border-radius:8px;text-decoration:none;display:inline-block;margin:16px 0}</style></head>
<body>
<h2>업소 소유권 승인!</h2>
<p>안녕하세요, {{ $userName }}님!</p>
<p><strong>{{ $businessName }}</strong> 업소의 소유권 신청이 승인되었습니다!</p>
<p>이제 업주 대시보드에서 업소 정보를 직접 관리하실 수 있습니다.</p>
<a href="{{ $dashboardUrl }}" class="btn">내 업소 관리하기</a>
<p style="color:#666;font-size:12px">SomeKorean - 미국 한인 커뮤니티</p>
</body></html>
'''

routes_to_add = r'''## Business Claim Routes (auth:api middleware)
Route::post('businesses/{id}/claim', [BusinessClaimController::class, 'initiate']);
Route::post('claims/{id}/email', [BusinessClaimController::class, 'sendEmailVerification']);
Route::get('claims/email/verify/{token}', [BusinessClaimController::class, 'verifyEmail']); // PUBLIC
Route::post('claims/{id}/documents', [BusinessClaimController::class, 'uploadDocuments']);
Route::get('claims/{id}/status', [BusinessClaimController::class, 'status']);
Route::get('my-claims', [BusinessClaimController::class, 'myClaims']);

## Owner Dashboard Routes (auth:api middleware)
Route::get('owner/business', [OwnerDashboardController::class, 'myBusiness']);
Route::put('owner/business', [OwnerDashboardController::class, 'update']);
Route::post('owner/business/photos', [OwnerDashboardController::class, 'uploadPhotos']);
Route::put('owner/business/photos/reorder', [OwnerDashboardController::class, 'reorderPhotos']);
Route::delete('owner/business/photos/{index}', [OwnerDashboardController::class, 'deletePhoto']);
Route::post('owner/business/menu-item', [OwnerDashboardController::class, 'upsertMenuItem']);
Route::delete('owner/business/menu-item/{itemId}', [OwnerDashboardController::class, 'deleteMenuItem']);
Route::get('owner/reviews', [OwnerDashboardController::class, 'myReviews']);
Route::post('owner/reviews/{id}/reply', [OwnerDashboardController::class, 'replyReview']);
Route::post('owner/reviews/{id}/report', [OwnerDashboardController::class, 'reportReview']);
Route::get('owner/events', [OwnerDashboardController::class, 'myEvents']);
Route::post('owner/events', [OwnerDashboardController::class, 'createEvent']);
Route::delete('owner/events/{id}', [OwnerDashboardController::class, 'deleteEvent']);
Route::get('owner/stats', [OwnerDashboardController::class, 'stats']);

## Admin Business Routes (admin middleware)
Route::get('businesses-list', [AdminBusinessController::class, 'index']);
Route::get('businesses-list/{id}', [AdminBusinessController::class, 'show']);
Route::put('businesses-list/{id}', [AdminBusinessController::class, 'update']);
Route::delete('businesses-list/{id}', [AdminBusinessController::class, 'destroy']);
Route::get('business-claims-list', [AdminBusinessController::class, 'claims']);
Route::post('business-claims-list/{id}/approve', [AdminBusinessController::class, 'approveClaim']);
Route::post('business-claims-list/{id}/reject', [AdminBusinessController::class, 'rejectClaim']);
Route::get('business-reviews-list', [AdminBusinessController::class, 'reviews']);
Route::post('business-reviews-list/{id}/hide', [AdminBusinessController::class, 'hideReview']);
Route::post('business-reviews-list/{id}/restore', [AdminBusinessController::class, 'restoreReview']);
Route::delete('business-reviews-list/{id}', [AdminBusinessController::class, 'deleteReview']);
Route::post('businesses/import', [AdminBusinessController::class, 'bulkImport']);
'''

# Ensure directories exist
print(ssh('mkdir -p /var/www/somekorean/app/Http/Controllers/API'))
print(ssh('mkdir -p /var/www/somekorean/app/Mail'))
print(ssh('mkdir -p /var/www/somekorean/resources/views/emails'))

# Task 1
write_file('/var/www/somekorean/app/Http/Controllers/API/BusinessClaimController.php', business_claim_controller)

# Task 2
write_file('/var/www/somekorean/app/Http/Controllers/API/OwnerDashboardController.php', owner_dashboard_controller)

# Task 3
write_file('/var/www/somekorean/app/Http/Controllers/API/AdminBusinessController.php', admin_business_controller)

# Task 4: Mail classes
write_file('/var/www/somekorean/app/Mail/ClaimVerificationMail.php', claim_verification_mail)
write_file('/var/www/somekorean/app/Mail/ClaimApprovedMail.php', claim_approved_mail)

# Task 4: Email blade views
write_file('/var/www/somekorean/resources/views/emails/claim-verification.blade.php', claim_verification_view)
write_file('/var/www/somekorean/resources/views/emails/claim-approved.blade.php', claim_approved_view)

# Task 5: composer dump-autoload
print('\n--- Task 5: composer dump-autoload ---')
result = ssh('cd /var/www/somekorean && composer dump-autoload 2>&1 | tail -5', timeout=120)
print(result)

# Task 6: ROUTES_TO_ADD.md
print('\n--- Task 6: ROUTES_TO_ADD.md ---')
write_file('/var/www/somekorean/ROUTES_TO_ADD.md', routes_to_add)

# Final summary
print('\n--- FINAL SUMMARY ---')
files = [
    '/var/www/somekorean/app/Http/Controllers/API/BusinessClaimController.php',
    '/var/www/somekorean/app/Http/Controllers/API/OwnerDashboardController.php',
    '/var/www/somekorean/app/Http/Controllers/API/AdminBusinessController.php',
    '/var/www/somekorean/app/Mail/ClaimVerificationMail.php',
    '/var/www/somekorean/app/Mail/ClaimApprovedMail.php',
    '/var/www/somekorean/resources/views/emails/claim-verification.blade.php',
    '/var/www/somekorean/resources/views/emails/claim-approved.blade.php',
    '/var/www/somekorean/ROUTES_TO_ADD.md',
]
for f in files:
    size = ssh(f'wc -c < {f}')
    exists = ssh(f'test -f {f} && echo OK || echo MISSING')
    print(f'{exists} {f} ({size} bytes)')

c.close()
print('\nDone.')
