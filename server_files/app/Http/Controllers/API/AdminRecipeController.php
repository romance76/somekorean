<?php
namespace App\Http\Controllers\API;
use App\Http\Controllers\Controller;
use App\Models\RecipeCategory;
use App\Models\RecipePost;
use App\Models\RecipeComment;
use Illuminate\Http\Request;

class AdminRecipeController extends Controller {
    public function stats() {
        return response()->json([
            'total_recipes'     => RecipePost::count(),
            'ai_recipes'        => RecipePost::where('source','ai')->count(),
            'with_images'       => RecipePost::whereNotNull('image_url')->count(),
            'total_comments'    => RecipeComment::count(),
        ]);
    }
    public function categories() {
        return response()->json(RecipeCategory::orderBy('sort_order')->get());
    }
    public function storeCategory(Request $r) {
        $r->validate(['name' => 'required', 'key' => 'required|unique:recipe_categories,key']);
        return response()->json(RecipeCategory::create($r->only(['name','key','icon','sort_order'])), 201);
    }
    public function updateCategory(Request $r, $id) {
        $cat = RecipeCategory::findOrFail($id);
        $cat->update($r->only(['name','icon','sort_order','is_active']));
        return response()->json($cat);
    }
    public function destroyCategory($id) {
        RecipeCategory::findOrFail($id)->delete();
        return response()->json(['message' => '삭제됨']);
    }
    public function recipes(Request $r) {
        $q = RecipePost::with('user:id,name,username','category:id,name,key')
            ->orderByDesc('created_at');
        if ($r->search) $q->where('title','like','%'.$r->search.'%');
        if ($r->category) $q->where('category_id', $r->category);
        if ($r->difficulty) $q->where('difficulty', $r->difficulty);
        return response()->json($q->paginate(25));
    }
    public function show($id) {
        return response()->json(RecipePost::with('category','user:id,name,username')->findOrFail($id));
    }
    public function update(Request $r, $id) {
        $recipe = RecipePost::findOrFail($id);
        $recipe->update($r->only(['title','intro','difficulty','cook_time','calories','servings','ingredients','steps','tips','tags','image_url','image_credit','is_hidden']));
        return response()->json($recipe);
    }
    public function destroy($id) {
        RecipePost::findOrFail($id)->delete();
        return response()->json(['message' => '삭제됨']);
    }
    public function comments(Request $r) {
        $q = RecipeComment::with('user:id,name,username','recipe:id,title')->latest();
        if ($r->recipe_id) $q->where('recipe_id', $r->recipe_id);
        return response()->json($q->paginate(25));
    }
    public function destroyComment($id) {
        RecipeComment::findOrFail($id)->delete();
        return response()->json(['message' => '삭제됨']);
    }
}
