<?php
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
