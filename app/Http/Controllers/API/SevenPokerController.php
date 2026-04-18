<?php
namespace App\Http\Controllers\API;

use App\Http\Controllers\Controller;
use App\Models\{SevenPokerRoom, SevenPokerGame, SevenPokerSeat, SevenPokerAction, User};
use Illuminate\Http\Request;
use Illuminate\Support\Facades\DB;

class SevenPokerController extends Controller
{
    /**
     * 로비 — 방 목록
     */
    public function rooms(Request $request)
    {
        $rooms = SevenPokerRoom::with(['host:id,name,nickname', 'seats:id,room_id,user_id,seat_number'])
            ->where('status', '!=', 'ended')
            ->orderByDesc('created_at')
            ->limit(50)
            ->get()
            ->map(function ($r) {
                return [
                    'id' => $r->id,
                    'name' => $r->name,
                    'host' => $r->host?->nickname ?: $r->host?->name,
                    'min_bet' => $r->min_bet,
                    'buy_in' => $r->buy_in,
                    'max_seats' => $r->max_seats,
                    'seats_taken' => $r->seats->count(),
                    'status' => $r->status,
                    'created_at' => $r->created_at,
                ];
            });
        return response()->json(['success' => true, 'data' => $rooms]);
    }

    /**
     * 방 생성
     */
    public function createRoom(Request $request)
    {
        $user = $request->user();
        $data = $request->validate([
            'name' => 'required|string|max:60',
            'min_bet' => 'nullable|integer|min:1000',
            'buy_in' => 'nullable|integer|min:100000',
            'max_seats' => 'nullable|integer|min:2|max:6',
        ]);

        $buyIn = (int)($data['buy_in'] ?? 1000000);
        if ($user->game_points < $buyIn) {
            return response()->json(['success' => false, 'message' => '게임머니 부족. 환전 후 입장하세요'], 422);
        }

        $room = SevenPokerRoom::create([
            'name' => $data['name'],
            'host_id' => $user->id,
            'min_bet' => $data['min_bet'] ?? 10000,
            'buy_in' => $buyIn,
            'max_seats' => $data['max_seats'] ?? 6,
            'status' => 'waiting',
        ]);

        // 호스트 자동 착석 (seat 1)
        $this->sitDown($user, $room, 1);

        return response()->json(['success' => true, 'data' => $this->roomState($room->id, $user->id)]);
    }

    /**
     * 방 입장 (빈 좌석 자동 배정)
     */
    public function joinRoom(Request $request, $roomId)
    {
        $user = $request->user();
        $room = SevenPokerRoom::findOrFail($roomId);

        if ($room->status === 'ended') {
            return response()->json(['success' => false, 'message' => '종료된 방입니다'], 422);
        }

        // 이미 앉아있으면 그냥 상태 반환
        $existing = SevenPokerSeat::where('room_id', $roomId)->where('user_id', $user->id)->first();
        if ($existing) {
            return response()->json(['success' => true, 'data' => $this->roomState($roomId, $user->id)]);
        }

        if ($user->game_points < $room->buy_in) {
            return response()->json(['success' => false, 'message' => "게임머니 부족 (" . number_format($room->buy_in) . " 필요)"], 422);
        }

        // 빈 좌석 찾기
        $taken = SevenPokerSeat::where('room_id', $roomId)->pluck('seat_number')->all();
        $free = null;
        for ($i = 1; $i <= $room->max_seats; $i++) {
            if (!in_array($i, $taken)) { $free = $i; break; }
        }
        if ($free === null) {
            return response()->json(['success' => false, 'message' => '자리가 가득참'], 422);
        }

        $this->sitDown($user, $room, $free);

        return response()->json(['success' => true, 'data' => $this->roomState($roomId, $user->id)]);
    }

    protected function sitDown(User $user, SevenPokerRoom $room, int $seatNumber): SevenPokerSeat
    {
        DB::transaction(function () use ($user, $room, $seatNumber, &$seat) {
            $user->decrement('game_points', $room->buy_in);
            $user->pointLogs()->create([
                'amount' => -$room->buy_in,
                'type' => 'poker7_buyin',
                'reason' => "세븐포커 방 입장 (바이인 " . number_format($room->buy_in) . " GM)",
                'balance_after' => $user->fresh()->game_points,
                'related_type' => 'seven_poker_room',
                'related_id' => $room->id,
            ]);
            $seat = SevenPokerSeat::create([
                'room_id' => $room->id,
                'user_id' => $user->id,
                'seat_number' => $seatNumber,
                'stack' => $room->buy_in,
                'state' => 'active',
                'joined_at' => now(),
            ]);
        });
        return $seat;
    }

    /**
     * 방 나가기 (남은 스택 반환)
     */
    public function leaveRoom(Request $request, $roomId)
    {
        $user = $request->user();
        $seat = SevenPokerSeat::where('room_id', $roomId)->where('user_id', $user->id)->first();
        if (!$seat) {
            return response()->json(['success' => false, 'message' => '앉아있지 않습니다'], 422);
        }

        $returnAmount = (int)$seat->stack;
        DB::transaction(function () use ($user, $seat, $returnAmount, $roomId) {
            if ($returnAmount > 0) {
                $user->increment('game_points', $returnAmount);
                $user->pointLogs()->create([
                    'amount' => $returnAmount,
                    'type' => 'poker7_cashout',
                    'reason' => "세븐포커 방 퇴장 (반환 " . number_format($returnAmount) . " GM)",
                    'balance_after' => $user->fresh()->game_points,
                    'related_type' => 'seven_poker_room',
                    'related_id' => $roomId,
                ]);
            }
            $seat->delete();
        });

        return response()->json(['success' => true, 'message' => number_format($returnAmount) . " GM 반환됨"]);
    }

    /**
     * 방 상태 조회 (폴링용)
     */
    public function state(Request $request, $roomId)
    {
        $user = $request->user();
        return response()->json(['success' => true, 'data' => $this->roomState($roomId, $user->id)]);
    }

    protected function roomState($roomId, $viewerUserId)
    {
        $room = SevenPokerRoom::findOrFail($roomId);
        $game = SevenPokerGame::where('room_id', $roomId)->latest()->first();
        $seats = SevenPokerSeat::with('user:id,name,nickname,avatar')
            ->where('room_id', $roomId)
            ->orderBy('seat_number')->get();

        $mySeat = $seats->firstWhere('user_id', $viewerUserId);

        // 카드 공개 규칙: 본인은 전부 볼 수 있음, 남은 사람은 visibility true 인 카드만
        $seatData = $seats->map(function ($s) use ($viewerUserId) {
            $isSelf = $s->user_id === $viewerUserId;
            $visibility = $s->card_visibility ?? [];
            $cards = $s->cards ?? [];
            $visibleCards = [];
            foreach ($cards as $i => $c) {
                $visibleCards[] = ($isSelf || ($visibility[$i] ?? false)) ? $c : null;
            }
            return [
                'id' => $s->id,
                'seat_number' => $s->seat_number,
                'user' => [
                    'id' => $s->user_id,
                    'name' => $s->user?->nickname ?: $s->user?->name,
                    'avatar' => $s->user?->avatar,
                ],
                'stack' => (int)$s->stack,
                'current_bet' => (int)$s->current_bet,
                'round_bet' => (int)$s->round_bet,
                'state' => $s->state,
                'cards' => $visibleCards,
                'is_self' => $isSelf,
            ];
        });

        return [
            'room' => [
                'id' => $room->id,
                'name' => $room->name,
                'min_bet' => $room->min_bet,
                'buy_in' => $room->buy_in,
                'max_seats' => $room->max_seats,
                'status' => $room->status,
                'host_id' => $room->host_id,
            ],
            'game' => $game ? [
                'id' => $game->id,
                'status' => $game->status,
                'pot' => (int)$game->pot,
                'current_round' => (int)$game->current_round,
                'dealer_seat' => $game->dealer_seat,
                'current_turn_seat' => $game->current_turn_seat,
                'current_bet' => (int)$game->current_bet,
            ] : null,
            'seats' => $seatData,
            'my_seat' => $mySeat?->seat_number,
        ];
    }

    /**
     * 게임 시작 (호스트만, 2명 이상 필요)
     * 간단 버전: 랜덤 딜러, 각 플레이어 3장 분배 (2장 비공개 + 1장 공개)
     */
    public function startGame(Request $request, $roomId)
    {
        $user = $request->user();
        $room = SevenPokerRoom::findOrFail($roomId);
        if ($room->host_id !== $user->id) {
            return response()->json(['success' => false, 'message' => '호스트만 게임 시작 가능'], 403);
        }

        $seats = SevenPokerSeat::where('room_id', $roomId)->where('state', 'active')->orderBy('seat_number')->get();
        if ($seats->count() < 2) {
            return response()->json(['success' => false, 'message' => '2명 이상 필요'], 422);
        }

        // 이전 게임이 진행 중이면 거절
        $existingActive = SevenPokerGame::where('room_id', $roomId)
            ->whereNotIn('status', ['ended'])->first();
        if ($existingActive) {
            return response()->json(['success' => false, 'message' => '이미 진행 중인 게임이 있음'], 422);
        }

        // 덱 생성 + 셔플
        $deck = $this->buildDeck();
        shuffle($deck);

        $game = DB::transaction(function () use ($room, $seats, $deck) {
            $dealerSeat = $seats->random()->seat_number;

            // 각 좌석에 3장 분배 (카드 2장 비공개 + 1장 공개)
            foreach ($seats as $seat) {
                $hand = [];
                $visibility = [];
                for ($i = 0; $i < 3; $i++) {
                    $hand[] = array_shift($deck);
                    $visibility[] = ($i === 2); // 3번째 카드만 공개
                }
                $seat->update([
                    'cards' => $hand,
                    'card_visibility' => $visibility,
                    'current_bet' => 0,
                    'round_bet' => 0,
                    'state' => 'active',
                ]);
            }

            $g = SevenPokerGame::create([
                'room_id' => $room->id,
                'status' => 'round1',
                'pot' => 0,
                'current_round' => 1,
                'dealer_seat' => $dealerSeat,
                'current_turn_seat' => $seats->first()->seat_number,
                'current_bet' => 0,
                'deck' => $deck,
                'started_at' => now(),
            ]);
            $room->update(['status' => 'playing']);
            return $g;
        });

        return response()->json(['success' => true, 'data' => $this->roomState($roomId, $user->id)]);
    }

    protected function buildDeck(): array
    {
        $suits = ['S', 'H', 'D', 'C']; // Spade Heart Diamond Club
        $ranks = [2,3,4,5,6,7,8,9,10,'J','Q','K','A'];
        $deck = [];
        foreach ($suits as $s) {
            foreach ($ranks as $r) {
                $deck[] = ['r' => $r, 's' => $s];
            }
        }
        return $deck;
    }
}
