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
        if ($request->search)   $query->where('name', 'like', '%'.$request->search.'%');

        return response()->json($query->paginate(20));
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
