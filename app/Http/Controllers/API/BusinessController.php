<?php
namespace App\Http\Controllers\API;

use App\Http\Controllers\Controller;
use App\Models\Business;
use App\Models\BusinessReview;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Auth;

class BusinessController extends Controller
{
    public function index(Request $request)
    {
        $query = Business::where('status', 'active')
            ->orderByDesc('is_sponsored')
            ->orderByDesc('rating_avg');

        if ($request->category) $query->where('category', $request->category);
        if ($request->region)   $query->where('region', 'like', '%'.$request->region.'%');
        if ($request->state) {
            $stateCities = [
                'CA'=>['Los Angeles','LA','San Francisco','San Diego'],
                'NY'=>['New York','NY','Flushing'], 'TX'=>['Houston','Dallas'],
                'WA'=>['Seattle'], 'IL'=>['Chicago'], 'GA'=>['Atlanta'],
                'DC'=>['Washington'], 'NV'=>['Las Vegas'], 'FL'=>['Miami'],
                'MA'=>['Boston'], 'HI'=>['Honolulu'], 'CO'=>['Denver'],
                'NJ'=>['Fort Lee'], 'VA'=>['Annandale'], 'OR'=>['Portland'],
                'MN'=>['Minneapolis'], 'MI'=>['Detroit'], 'AZ'=>['Phoenix'],
                'MD'=>['Baltimore'], 'PA'=>['Philadelphia'],
            ];
            $s = strtoupper($request->state);
            if (isset($stateCities[$s])) $query->whereIn('region', $stateCities[$s]);
        }
        if ($request->search)   $query->where('name', 'like', '%'.$request->search.'%');

        $perPage = min((int)($request->per_page ?? 20), 50);
        return response()->json($query->paginate($perPage));
    }

    public function store(Request $request)
    {
        $request->validate([
            'name'     => 'required|string|max:100',
            'category' => 'required|string',
            'address'  => 'required|string',
        ]);
        $business = Business::create(array_merge($request->only(['name','category','description','address','lat','lng','phone','website','hours','region']), ['owner_id' => Auth::id()]));
        return response()->json(['message' => '업소가 등록되었습니다.', 'business' => $business], 201);
    }

    public function show(Business $business)
    {
        return response()->json($business->load(['owner:id,name,username', 'reviews.user:id,name,username,avatar']));
    }

    public function trackStat(Request $request, $id)
    {
        $type = $request->route('type'); // phone, direction, website, view
        $col = match($type) {
            'phone' => 'phone_clicks',
            'direction' => 'direction_clicks',
            'website' => 'website_clicks',
            default => 'views'
        };
        $today = now()->toDateString();
        \DB::table('business_stats')->updateOrInsert(
            ['business_id' => $id, 'stat_date' => $today],
            [$col => \DB::raw($col . ' + 1'), 'updated_at' => now()]
        );
        return response()->json(['ok' => true]);
    }

    public function toggleBookmark(Request $request, $id)
    {
        $userId = Auth::id();
        $key = 'biz_bm_'.$id.'_'.$userId;
        $exists = \DB::table('bookmarks')->where('user_id', $userId)->where('bookmarkable_type', 'App\Models\Business')->where('bookmarkable_id', $id)->exists();
        if ($exists) {
            \DB::table('bookmarks')->where('user_id', $userId)->where('bookmarkable_type', 'App\Models\Business')->where('bookmarkable_id', $id)->delete();
            return response()->json(['bookmarked' => false]);
        } else {
            \DB::table('bookmarks')->insert(['user_id' => $userId, 'bookmarkable_type' => 'App\Models\Business', 'bookmarkable_id' => $id, 'created_at' => now(), 'updated_at' => now()]);
            return response()->json(['bookmarked' => true]);
        }
    }

    public function review(Request $request, Business $business)
    {
        $request->validate(['rating' => 'required|integer|min:1|max:5', 'content' => 'nullable|string|max:500']);
        $review = BusinessReview::updateOrCreate(
            ['business_id' => $business->id, 'user_id' => Auth::id()],
            ['rating' => $request->rating, 'content' => $request->content]
        );
        // 평점 업데이트
        $avg = $business->reviews()->avg('rating');
        $business->update(['rating_avg' => $avg, 'review_count' => $business->reviews()->count()]);
        return response()->json(['message' => '리뷰가 등록되었습니다.', 'review' => $review], 201);
    }
}
