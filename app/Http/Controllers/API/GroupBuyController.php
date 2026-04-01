<?php

namespace App\Http\Controllers\API;

use App\Http\Controllers\Controller;
use App\Models\GroupBuy;
use App\Models\GroupBuyParticipant;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Auth;
use Illuminate\Support\Facades\Storage;

class GroupBuyController extends Controller
{
    public function index(Request $request)
    {
        $q = GroupBuy::with('user:id,name,username,avatar')
            ->withCount('participants')
            ->where('status', '!=', 'cancelled');

        if ($request->category && $request->category !== 'all') {
            $q->where('category', $request->category);
        }
        if ($request->status) {
            $q->where('status', $request->status);
        }
        if ($request->search) {
            $q->where('title', 'like', "%{$request->search}%");
        }

        return response()->json($q->latest()->paginate(20));
    }

    public function show($id)
    {
        $gb = GroupBuy::with([
            'user:id,name,username,avatar',
            'participants.user:id,name,username,avatar',
        ])->withCount('participants')->findOrFail($id);

        return response()->json($gb);
    }

    public function store(Request $request)
    {
        $request->validate([
            'title'            => 'required|string|max:100',
            'description'      => 'required|string|max:3000',
            'target_price'     => 'required|numeric|min:0',
            'min_participants' => 'required|integer|min:2',
            'max_participants' => 'nullable|integer|min:2',
            'category'         => 'required|string',
            'deadline'         => 'required|date|after:now',
            'product_url'      => 'nullable|url',
        ]);

        $images = [];
        if ($request->hasFile('images')) {
            foreach ($request->file('images') as $file) {
                $path = $file->store('groupbuy', 'public');
                $images[] = Storage::url($path);
            }
        }

        $gb = GroupBuy::create([
            'user_id'          => Auth::id(),
            'title'            => $request->title,
            'description'      => $request->description,
            'target_price'     => $request->target_price,
            'min_participants' => $request->min_participants,
            'max_participants' => $request->max_participants,
            'category'         => $request->category,
            'deadline'         => $request->deadline,
            'product_url'      => $request->product_url,
            'images'           => $images,
            'status'           => 'open',
        ]);

        // 작성자 자동 참여
        GroupBuyParticipant::create(['group_buy_id' => $gb->id, 'user_id' => Auth::id(), 'quantity' => 1]);

        return response()->json($gb->load('user:id,name,username,avatar'), 201);
    }

    public function join(Request $request, $id)
    {
        $gb = GroupBuy::findOrFail($id);

        if ($gb->status !== 'open') {
            return response()->json(['message' => '모집이 종료된 공동구매입니다.'], 422);
        }
        if ($gb->max_participants && $gb->participants()->count() >= $gb->max_participants) {
            return response()->json(['message' => '최대 인원이 초과되었습니다.'], 422);
        }

        [$participant, $created] = [
            GroupBuyParticipant::firstOrCreate(
                ['group_buy_id' => $gb->id, 'user_id' => Auth::id()],
                ['quantity' => $request->quantity ?? 1]
            ),
            !GroupBuyParticipant::where(['group_buy_id' => $gb->id, 'user_id' => Auth::id()])->whereNull('created_at')->exists()
        ];

        // 포인트 적립: 신규 참여시만
        if ($participant->wasRecentlyCreated) {
            Auth::user()->addPoints(2, 'groupbuy_join', 'earn', $gb->id, '공동구매 참여');
        }

        // 최소 인원 달성 시 상태 변경
        $count = $gb->participants()->count();
        if ($count >= $gb->min_participants && $gb->status === 'open') {
            $gb->update(['status' => 'completed']);
        }

        return response()->json(['joined' => true, 'participants_count' => $count]);
    }

    public function leave($id)
    {
        $gb = GroupBuy::findOrFail($id);
        if ($gb->user_id === Auth::id()) {
            return response()->json(['message' => '작성자는 나갈 수 없습니다.'], 422);
        }
        GroupBuyParticipant::where('group_buy_id', $id)->where('user_id', Auth::id())->delete();

        return response()->json(['joined' => false]);
    }

    public function destroy($id)
    {
        $gb = GroupBuy::where('user_id', Auth::id())->findOrFail($id);
        $gb->update(['status' => 'cancelled']);
        return response()->json(['cancelled' => true]);
    }
}
