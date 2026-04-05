<?php
namespace App\Http\Controllers\API;
use App\Http\Controllers\Controller;
use App\Models\RecipeCategory;
use App\Models\RecipePost;
use App\Models\RecipeComment;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Auth;
use Illuminate\Support\Facades\DB;

class RecipeController extends Controller {
    public function categories() {
        return response()->json(RecipeCategory::where('is_active', true)->orderBy('sort_order')->get());
    }

    public function index(Request $request) {
        $query = RecipePost::with('user:id,nickname,username,avatar', 'category:id,name,key,icon')
            ->where('is_hidden', false)
            ->orderByDesc('created_at');
        if ($request->category) $query->whereHas('category', fn($q) => $q->where('key', $request->category));
        if ($request->difficulty) $query->where('difficulty', $request->difficulty);
        if ($request->search) {
            $s = $request->search;
            $query->where(function($q) use ($s) {
                $q->where('title', 'like', "%$s%")
                  ->orWhere('intro', 'like', "%$s%")
                  ->orWhereJsonContains('ingredients', $s)
                  ->orWhereJsonContains('tags', $s);
            });
        }
        return response()->json($query->paginate(20));
    }

    public function show($id) {
        $recipe = RecipePost::with(['user:id,nickname,username,avatar', 'category:id,name,key,icon',
            'comments' => fn($q) => $q->with('user:id,nickname,username,avatar')->latest()->limit(20),
        ])->findOrFail($id);
        $recipe->increment('view_count');
        $isLiked = Auth::check() ? DB::table('content_likes')->where('user_id', Auth::id())->where('likeable_type', 'recipe')->where('likeable_id', $id)->exists() : false;
        $isBookmarked = Auth::check() ? DB::table('content_likes')->where('user_id', Auth::id())->where('likeable_type', 'recipe_bookmark')->where('likeable_id', $id)->exists() : false;
        // Related recipes (same category)
        $related = RecipePost::where('category_id', $recipe->category_id)
            ->where('id', '!=', $id)
            ->where('is_hidden', false)
            ->inRandomOrder()
            ->limit(6)
            ->get(['id', 'title', 'image_url', 'difficulty', 'cook_time', 'like_count', 'view_count', 'category_id']);
        // Average rating from comments
        $avgRating = DB::table('recipe_comments')
            ->where('recipe_id', $id)
            ->where('is_hidden', false)
            ->whereNotNull('rating')
            ->avg('rating');
        return response()->json(array_merge($recipe->toArray(), [
            'is_liked' => $isLiked,
            'is_bookmarked' => $isBookmarked,
            'related' => $related,
            'avg_rating' => $avgRating ? round($avgRating, 1) : null,
            'comment_count' => $recipe->comments->count(),
        ]));
    }

    public function store(Request $request) {
        $request->validate(['title' => 'required|string|max:200', 'category_id' => 'required|exists:recipe_categories,id']);
        $recipe = RecipePost::create([...$request->only(['title','intro','category_id','difficulty','cook_time','calories','servings','ingredients','steps','tips','tags','image_url']), 'user_id' => Auth::id()]);
        return response()->json($recipe, 201);
    }

    public function like($id) {
        RecipePost::findOrFail($id);
        $userId = Auth::id();
        $existing = DB::table('content_likes')->where('user_id', $userId)->where('likeable_type', 'recipe')->where('likeable_id', $id)->first();
        if ($existing) {
            DB::table('content_likes')->where('id', $existing->id)->delete();
            RecipePost::where('id', $id)->decrement('like_count');
        } else {
            DB::table('content_likes')->insert(['user_id' => $userId, 'likeable_type' => 'recipe', 'likeable_id' => $id, 'created_at' => now()]);
            RecipePost::where('id', $id)->increment('like_count');
        }
        $count = DB::table('content_likes')->where('likeable_type', 'recipe')->where('likeable_id', $id)->count();
        return response()->json(['liked' => !$existing, 'like_count' => $count]);
    }

    public function bookmark($id) {
        RecipePost::findOrFail($id);
        $userId = Auth::id();
        $existing = DB::table('content_likes')->where('user_id', $userId)->where('likeable_type', 'recipe_bookmark')->where('likeable_id', $id)->first();
        if ($existing) {
            DB::table('content_likes')->where('id', $existing->id)->delete();
            RecipePost::where('id', $id)->decrement('bookmark_count');
        } else {
            DB::table('content_likes')->insert(['user_id' => $userId, 'likeable_type' => 'recipe_bookmark', 'likeable_id' => $id, 'created_at' => now()]);
            RecipePost::where('id', $id)->increment('bookmark_count');
        }
        return response()->json(['bookmarked' => !$existing]);
    }

    public function comment(Request $request, $id) {
        RecipePost::findOrFail($id);
        $request->validate(['content' => 'required|string|max:1000', 'rating' => 'nullable|integer|min:1|max:5']);
        $comment = RecipeComment::create(['recipe_id' => $id, 'user_id' => Auth::id(), 'content' => $request->content, 'rating' => $request->rating]);
        return response()->json(['message' => '댓글 등록', 'comment' => $comment->load('user:id,nickname,username,avatar')], 201);
    }

    public function popular() {
        return response()->json(RecipePost::where('is_hidden', false)->orderByDesc('like_count')->limit(10)->get(['id','title','image_url','difficulty','cook_time','like_count']));
    }
}