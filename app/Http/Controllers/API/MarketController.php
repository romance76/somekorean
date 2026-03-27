<?php
namespace App\Http\Controllers\API;

use App\Http\Controllers\Controller;
use App\Models\MarketItem;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Auth;

class MarketController extends Controller
{
    public function index(Request $request)
    {
        $query = MarketItem::with('user:id,name,username,avatar')
            ->where('status', 'active')
            ->where('item_type', $request->type ?? 'used');

        if ($request->category) $query->where('category', $request->category);
        if ($request->region)   $query->where('region', 'like', '%'.$request->region.'%');
        if ($request->search) {
            $query->where(function($q) use ($request) {
                $q->where('title', 'like', '%'.$request->search.'%')
                  ->orWhere('description', 'like', '%'.$request->search.'%');
            });
        }

        return response()->json($query->orderByDesc('created_at')->paginate(20));
    }

    public function store(Request $request)
    {
        $request->validate([
            'title'       => 'required|string|max:200',
            'description' => 'required|string',
            'price'       => 'required|numeric|min:0',
            'item_type'   => 'in:used,real_estate,car',
        ]);
        $item = MarketItem::create(array_merge($request->only(['title','description','price','price_negotiable','category','item_type','region','condition']), ['user_id' => Auth::id()]));
        return response()->json(['message' => '등록되었습니다.', 'item' => $item], 201);
    }

    public function show(MarketItem $item)
    {
        $item->increment('view_count');
        return response()->json($item->load('user:id,name,username,avatar'));
    }

    public function update(Request $request, MarketItem $item)
    {
        if ($item->user_id !== Auth::id()) abort(403);
        $item->update($request->only(['title','description','price','price_negotiable','status','region','condition']));
        return response()->json(['message' => '수정되었습니다.', 'item' => $item]);
    }

    public function destroy(MarketItem $item)
    {
        if ($item->user_id !== Auth::id() && !Auth::user()->is_admin) abort(403);
        $item->delete();
        return response()->json(['message' => '삭제되었습니다.']);
    }
}
