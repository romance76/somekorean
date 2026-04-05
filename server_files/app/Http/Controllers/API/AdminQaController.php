<?php
namespace App\Http\Controllers\API;
use App\Http\Controllers\Controller;
use App\Models\QaCategory;
use App\Models\QaPost;
use App\Models\QaAnswer;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\DB;

class AdminQaController extends Controller {
    public function stats() {
        return response()->json([
            'total_posts'    => QaPost::count(),
            'solved_posts'   => QaPost::where('status', 'solved')->count(),
            'total_answers'  => QaAnswer::count(),
            'ai_posts'       => QaPost::where('source', 'ai')->count(),
        ]);
    }
    public function categories(Request $r) {
        return response()->json(QaCategory::orderBy('sort_order')->get());
    }
    public function storeCategory(Request $r) {
        $r->validate(['name' => 'required|string|max:50', 'key' => 'required|string|max:30|unique:qa_categories,key']);
        return response()->json(QaCategory::create($r->only(['name','key','icon','color','sort_order'])), 201);
    }
    public function updateCategory(Request $r, $id) {
        $cat = QaCategory::findOrFail($id);
        $cat->update($r->only(['name','icon','color','sort_order','is_active']));
        return response()->json($cat);
    }
    public function destroyCategory($id) {
        QaCategory::findOrFail($id)->delete();
        return response()->json(['message' => '삭제됨']);
    }
    public function posts(Request $r) {
        $q = QaPost::with('user:id,name,username','category:id,name,key')
            ->orderByDesc('created_at');
        if ($r->search) $q->where('title','like','%'.$r->search.'%');
        if ($r->category) $q->where('category_id', $r->category);
        if ($r->status) $q->where('status', $r->status);
        return response()->json($q->paginate(25));
    }
    public function updatePost(Request $r, $id) {
        $post = QaPost::findOrFail($id);
        $post->update($r->only(['title','content','status','is_pinned','is_hidden']));
        return response()->json($post);
    }
    public function destroyPost($id) {
        QaPost::findOrFail($id)->delete();
        return response()->json(['message' => '삭제됨']);
    }
    public function answers(Request $r, $postId) {
        return response()->json(QaAnswer::where('qa_post_id', $postId)->with('user:id,name,username')->get());
    }
    public function setBest(Request $r, $answerId) {
        $answer = QaAnswer::findOrFail($answerId);
        QaAnswer::where('qa_post_id', $answer->qa_post_id)->update(['is_best' => false]);
        $answer->update(['is_best' => true]);
        QaPost::where('id', $answer->qa_post_id)->update(['best_answer_id' => $answerId, 'status' => 'solved']);
        return response()->json(['message' => '베스트 답변 지정됨']);
    }
    public function destroyAnswer($id) {
        QaAnswer::findOrFail($id)->delete();
        return response()->json(['message' => '삭제됨']);
    }
}
