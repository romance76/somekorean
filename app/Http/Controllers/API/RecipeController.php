<?php
namespace App\Http\Controllers\API;

use App\Http\Controllers\Controller;
use App\Models\RecipePost;
use Illuminate\Http\Request;

class RecipeController extends Controller
{
    // GET /api/recipes — 공용 목록 (페이지네이션)
    public function index(Request $request)
    {
        $query = RecipePost::where('is_active', true);

        if ($request->search) {
            $query->where('title', 'like', "%{$request->search}%");
        }
        if ($request->category) {
            $query->where('category', $request->category);
        }

        $perPage = (int) ($request->per_page ?? 12);
        return response()->json(
            $query->orderByDesc('id')->paginate($perPage)
        );
    }

    // GET /api/recipes/{id}
    public function show($id)
    {
        $recipe = RecipePost::where('is_active', true)->findOrFail($id);
        $recipe->increment('view_count');
        return response()->json($recipe);
    }

    // GET /api/recipes/categories — 카테고리 목록 (count 포함)
    public function categories()
    {
        $cats = RecipePost::where('is_active', true)
            ->whereNotNull('category')
            ->where('category', '!=', '')
            ->groupBy('category')
            ->selectRaw('category, count(*) as count')
            ->orderByDesc('count')
            ->get();
        return response()->json($cats);
    }
}
