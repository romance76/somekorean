<?php

namespace App\Http\Controllers\API;

use App\Http\Controllers\Controller;
use App\Models\RecipePost;
use App\Models\RecipeComment;
use App\Models\RecipeCategory;
use Illuminate\Http\Request;

class AdminRecipeController extends Controller
{
    /**
     * GET /api/admin/recipes
     * 레시피 목록 (검색/카테고리/난이도 필터)
     */
    public function index(Request $request)
    {
        try {
            $query = RecipePost::with('user:id,name,nickname', 'category:id,name,key,icon');

            if ($search = $request->input('search')) {
                $query->where('title', 'like', "%{$search}%");
            }
            if ($categoryId = $request->input('category_id')) {
                $query->where('category_id', $categoryId);
            }
            if ($difficulty = $request->input('difficulty')) {
                $query->where('difficulty', $difficulty);
            }

            $recipes = $query->orderByDesc('created_at')->paginate($request->input('per_page', 25));

            $stats = [
                'total'      => RecipePost::count(),
                'this_week'  => RecipePost::where('created_at', '>=', now()->startOfWeek())->count(),
                'with_image' => RecipePost::whereNotNull('image_url')->where('image_url', '!=', '')->count(),
                'hidden'     => RecipePost::where('is_hidden', true)->count(),
            ];

            return response()->json(['success' => true, 'data' => $recipes, 'stats' => $stats]);
        } catch (\Exception $e) {
            return response()->json(['success' => false, 'message' => $e->getMessage()], 500);
        }
    }

    /**
     * DELETE /api/admin/recipes/{id}
     * 레시피 삭제
     */
    public function destroy($id)
    {
        try {
            $recipe = RecipePost::findOrFail($id);

            // 연관 댓글도 삭제
            RecipeComment::where('recipe_post_id', $id)->delete();
            $recipe->delete();

            return response()->json(['success' => true, 'message' => '레시피가 삭제되었습니다.']);
        } catch (\Exception $e) {
            return response()->json(['success' => false, 'message' => $e->getMessage()], 500);
        }
    }
}
