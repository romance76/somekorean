<?php
namespace App\Http\Controllers\API;
use App\Http\Controllers\Controller;
use App\Models\QaCategory;
use App\Models\QaPost;
use App\Models\QaAnswer;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Auth;
use Illuminate\Support\Facades\DB;

class QaController extends Controller {
    public function categories() {
        return response()->json(QaCategory::where('is_active', true)->orderBy('sort_order')->get());
    }

    public function index(Request $request) {
        $query = QaPost::with('user:id,nickname,username,avatar', 'category:id,name,key,icon,color')
            ->where('is_hidden', false)
            ->orderByDesc('is_pinned')
            ->orderByDesc('created_at');
        if ($request->category) $query->whereHas('category', fn($q) => $q->where('key', $request->category));
        if ($request->search) $query->where('title', 'like', '%'.$request->search.'%');
        if ($request->status) $query->where('status', $request->status);
        return response()->json($query->paginate(20));
    }

    public function show($id) {
        $post = QaPost::with(['user:id,nickname,username,avatar', 'category:id,name,key,icon,color',
            'answers' => fn($q) => $q->where('is_hidden', false)->with('user:id,nickname,username,avatar')->orderByDesc('is_best')->orderByDesc('like_count'),
            'bestAnswer.user:id,nickname,username,avatar',
        ])->findOrFail($id);
        $post->increment('view_count');
        return response()->json($post);
    }

    public function store(Request $request) {
        $request->validate(['title' => 'required|string|max:200', 'content' => 'required|string', 'category_id' => 'required|exists:qa_categories,id']);
        $post = QaPost::create([...$request->only(['title','content','category_id','region']), 'user_id' => Auth::id()]);
        return response()->json($post->load('user:id,nickname,username,avatar', 'category'), 201);
    }

    public function answer(Request $request, $id) {
        $request->validate(['content' => 'required|string|max:5000']);
        $post = QaPost::findOrFail($id);
        $answer = QaAnswer::create(['qa_post_id' => $id, 'user_id' => Auth::id(), 'content' => $request->content]);
        $post->increment('answer_count');
        return response()->json(['message' => '답변이 등록되었습니다.', 'answer' => $answer->load('user:id,nickname,username,avatar')], 201);
    }

    public function setBestAnswer(Request $request, $id) {
        $post = QaPost::where('id', $id)->where('user_id', Auth::id())->firstOrFail();
        $request->validate(['answer_id' => 'required|exists:qa_answers,id']);
        QaAnswer::where('qa_post_id', $id)->update(['is_best' => false]);
        QaAnswer::where('id', $request->answer_id)->update(['is_best' => true]);
        $post->update(['best_answer_id' => $request->answer_id, 'status' => 'solved']);
        return response()->json(['message' => '베스트 답변이 선택되었습니다.']);
    }

    public function likeAnswer($answerId) {
        $answer = QaAnswer::findOrFail($answerId);
        $answer->increment('like_count');
        return response()->json(['like_count' => $answer->fresh()->like_count]);
    }
}