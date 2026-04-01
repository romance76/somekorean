<?php
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

    // POST /api/admin/businesses/import - trigger server-side crawler or bulk import
    public function bulkImport(Request $req)
    {
        // Manual trigger from admin UI - run actual crawler on server
        if ($req->input('trigger') === 'manual') {
            $city = escapeshellarg($req->input('city', 'all'));
            $category = escapeshellarg($req->input('category', 'all'));
            $crawlerPath = base_path('crawler_server/crawler.py');

            // Kill any existing crawl
            exec('pkill -f crawler_server/crawler.py 2>/dev/null');
            // Clear old log
            file_put_contents('/tmp/crawl.log', '');
            // Write initial status
            file_put_contents('/tmp/crawl_status.json', json_encode([
                'status' => 'running', 'inserted' => 0, 'skipped' => 0,
                'progress' => '0/0', 'message' => 'Starting crawler...', 'updated_at' => now()
            ]));
            // Run crawler in background
            // Build command - 'all' means no city/category filter (use defaults)
            $cityArg = ($req->input('city') && $req->input('city') !== 'all') ? "--city {$city}" : '';
            $catArg = ($req->input('category') && $req->input('category') !== 'all') ? "--category {$category}" : '';
            $cmd = "python3 {$crawlerPath} {$cityArg} {$catArg} --per-city 5 > /tmp/crawl.log 2>&1 &";
            exec($cmd);

            $total = DB::table('businesses')->count();
            return response()->json([
                'message' => "크롤링이 시작되었습니다!\n도시: " . $req->input('city','전체') . "\n카테고리: " . $req->input('category','전체') . "\n\n현재 업소 수: {$total}개\n페이지를 새로고침하면 결과가 업데이트됩니다.",
                'status' => 'started', 'current_total' => $total
            ]);
        }

        // Check crawl status
        if ($req->input('action') === 'status') {
            $statusFile = '/tmp/crawl_status.json';
            if (file_exists($statusFile)) {
                $status = json_decode(file_get_contents($statusFile), true);
                $status['total_businesses'] = DB::table('businesses')->count();
                return response()->json($status);
            }
            return response()->json(['status' => 'idle', 'total_businesses' => DB::table('businesses')->count()]);
        }

        // Actual bulk import from crawler API call (array of businesses)
        $businesses = $req->input('businesses', []);
        if (empty($businesses)) {
            return response()->json(['message' => '가져올 업소 데이터가 없습니다.', 'inserted' => 0, 'skipped' => 0], 200);
        }
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
        return response()->json([
            'message' => "{$inserted}개 업소가 추가되었습니다. ({$skipped}개 중복 건너뜀)",
            'inserted' => $inserted, 'skipped' => $skipped, 'total' => count($businesses)
        ]);
    }
    public function crawlStatus()
    {
        $total = \App\Models\Business::count();
        $claimed = \App\Models\Business::where('is_claimed', true)->count();
        $premium = \App\Models\Business::where('is_premium', true)->count();
        return response()->json([
            'total'   => $total,
            'claimed' => $claimed,
            'premium' => $premium,
        ]);
    }
}
