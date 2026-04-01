<?php
namespace App\Http\Controllers\API;
use App\Http\Controllers\Controller;
use App\Models\RecipeCategory;
use App\Models\RecipePost;
use App\Models\RecipeComment;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Auth;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Facades\Storage;

class RecipeController extends Controller {
    public function categories() {
        return response()->json(RecipeCategory::where('is_active', true)->orderBy('sort_order')->get());
    }

    public function index(Request $request) {
        $query = RecipePost::with('user:id,nickname,username,avatar', 'category:id,name,key,icon')
            ->where('is_hidden', false);

        if ($request->sort === 'popular') {
            $query->orderByDesc('like_count');
        } elseif ($request->sort === 'views') {
            $query->orderByDesc('view_count');
        } else {
            $query->orderByDesc('created_at');
        }

        if ($request->category) $query->whereHas('category', fn($q) => $q->where('key', $request->category));
        if ($request->difficulty) $query->where('difficulty', $request->difficulty);
        if ($request->search) {
            $s = $request->search;
            $query->where(function($q) use ($s) {
                $q->where('title', 'like', "%$s%")
                  ->orWhere('intro', 'like', "%$s%")
                  ->orWhereJsonContains('tags', $s);
            });
        }

        $perPage = $request->per_page ? (int)$request->per_page : 20;
        return response()->json($query->paginate($perPage));
    }

    public function show($id) {
        $recipe = RecipePost::with(['user:id,nickname,username,avatar', 'category:id,name,key,icon',
            'comments' => fn($q) => $q->with('user:id,nickname,username,avatar')->latest()->limit(20),
        ])->findOrFail($id);
        $recipe->increment('view_count');
        $isLiked = Auth::check() ? DB::table('content_likes')->where('user_id', Auth::id())->where('likeable_type', 'recipe')->where('likeable_id', $id)->exists() : false;
        $isBookmarked = Auth::check() ? DB::table('content_likes')->where('user_id', Auth::id())->where('likeable_type', 'recipe_bookmark')->where('likeable_id', $id)->exists() : false;
        $related = RecipePost::where('category_id', $recipe->category_id)
            ->where('id', '!=', $id)
            ->where('is_hidden', false)
            ->where('source', 'user')
            ->inRandomOrder()->limit(6)
            ->get(['id','title','image_url','difficulty','cook_time','like_count','view_count','category_id']);
        $avgRating = DB::table('recipe_comments')
            ->where('recipe_id', $id)->where('is_hidden', false)->whereNotNull('rating')->avg('rating');
        return response()->json(array_merge($recipe->toArray(), [
            'is_liked' => $isLiked, 'is_bookmarked' => $isBookmarked,
            'related' => $related,
            'avg_rating' => $avgRating ? round($avgRating, 1) : null,
            'comment_count' => $recipe->comments->count(),
        ]));
    }

    public function uploadImage(Request $request) {
        $request->validate(['image' => 'required|image|mimes:jpeg,png,jpg,gif,webp|max:5120']);
        $path = $request->file('image')->store('recipes', 'public');
        return response()->json(['url' => asset('storage/' . $path)]);
    }

    public function store(Request $request) {
        $request->validate([
            'title'       => 'required|string|max:200',
            'category_id' => 'required|exists:recipe_categories,id',
            'ingredients' => 'nullable|array',
            'steps'       => 'nullable|array',
            'tips'        => 'nullable|array',
            'tags'        => 'nullable|array',
        ]);

        $recipe = RecipePost::create([
            'user_id'     => Auth::id(),
            'title'       => $request->title,
            'intro'       => $request->intro,
            'category_id' => $request->category_id,
            'difficulty'  => $request->difficulty,
            'cook_time'   => $request->cook_time,
            'calories'    => $request->calories,
            'servings'    => $request->servings ?? 2,
            'ingredients' => $request->ingredients ?? [],
            'steps'       => $request->steps ?? [],
            'tips'        => $request->tips ?? [],
            'tags'        => $request->tags ?? [],
            'image_url'   => $request->image_url,
            'source'      => 'user',
        ]);
        // 포인트 적립: 레시피 작성
        Auth::user()->addPoints(5, 'recipe_write', 'earn', $recipe->id, '레시피 작성');

        return response()->json($recipe->load('user:id,nickname,avatar', 'category:id,name,key,icon'), 201);
    }

    public function update(Request $request, $id) {
        $recipe = RecipePost::findOrFail($id);
        if ($recipe->user_id !== Auth::id() && !Auth::user()->is_admin) {
            return response()->json(['message' => '수정 권한이 없습니다.'], 403);
        }
        $recipe->update($request->only(['title','intro','category_id','difficulty','cook_time','calories','servings','ingredients','steps','tips','tags','image_url']));
        return response()->json($recipe);
    }

    public function destroy($id) {
        $recipe = RecipePost::findOrFail($id);
        if ($recipe->user_id !== Auth::id() && !Auth::user()->is_admin) {
            return response()->json(['message' => '삭제 권한이 없습니다.'], 403);
        }
        $recipe->delete();
        return response()->json(['message' => '삭제되었습니다.']);
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
        return response()->json(RecipePost::where('is_hidden', false)->where('source','user')->orderByDesc('like_count')->limit(10)->get(['id','title','image_url','difficulty','cook_time','like_count']));
    }

    public function myRecipes(Request $request) {
        $recipes = RecipePost::where('user_id', Auth::id())
            ->orderByDesc('created_at')
            ->paginate(20);
        return response()->json($recipes);
    }
}
