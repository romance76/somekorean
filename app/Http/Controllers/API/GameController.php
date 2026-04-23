<?php

namespace App\Http\Controllers\API;

use App\Http\Controllers\Controller;
use App\Models\Game;
use App\Models\GameSetting;
use Illuminate\Http\Request;

class GameController extends Controller
{
    /** 공개: 활성 게임 목록 (유저 GameLobby 용) */
    public function publicIndex()
    {
        $games = Game::active()->orderBy('sort_order')->get();
        return response()->json(['success' => true, 'data' => $games]);
    }

    /** 관리자: 전체 게임 목록 */
    public function index()
    {
        $games = Game::orderBy('sort_order')->get();
        return response()->json(['success' => true, 'data' => $games]);
    }

    /** 관리자: 게임 수정 (이름/설명/아이콘/카테고리/순서/활성) */
    public function update(Request $request, $id)
    {
        $game = Game::findOrFail($id);
        $data = $request->validate([
            'name'        => 'nullable|string|max:100',
            'description' => 'nullable|string|max:200',
            'icon'        => 'nullable|string|max:20',
            'category'    => 'nullable|in:card,brain,arcade,word,education',
            'is_active'   => 'nullable|boolean',
            'sort_order'  => 'nullable|integer',
        ]);
        $game->update($data);
        return response()->json(['success' => true, 'data' => $game->fresh()]);
    }

    /** 관리자: 활성 토글 */
    public function toggle($id)
    {
        $game = Game::findOrFail($id);
        $game->is_active = !$game->is_active;
        $game->save();
        return response()->json(['success' => true, 'data' => $game]);
    }

    /** 관리자: 순서 일괄 재조정 (id 배열 순서대로) */
    public function reorder(Request $request)
    {
        $ids = $request->input('ids', []);
        foreach ($ids as $i => $id) {
            Game::where('id', $id)->update(['sort_order' => $i]);
        }
        return response()->json(['success' => true]);
    }

    /** 관리자: 특정 게임 + 그 게임 설정 전체 */
    public function show($slug)
    {
        $game = Game::where('slug', $slug)->firstOrFail();
        $settings = GameSetting::where('game_type', $slug)->orderBy('key')->get();
        return response()->json(['success' => true, 'data' => [
            'game' => $game,
            'settings' => $settings,
        ]]);
    }

    /** 관리자: 게임별 key/value 설정 저장 */
    public function saveSettings(Request $request, $slug)
    {
        $game = Game::where('slug', $slug)->firstOrFail();
        $settings = $request->input('settings', []);
        foreach ($settings as $s) {
            if (empty($s['key'])) continue;
            GameSetting::updateOrCreate(
                ['game_type' => $game->slug, 'key' => $s['key']],
                ['value' => (string) ($s['value'] ?? '')],
            );
        }
        // 요청에 없는 기존 키는 유지 (삭제는 별도 엔드포인트)
        return response()->json(['success' => true]);
    }

    /** 관리자: 설정 key 삭제 */
    public function deleteSetting($slug, $key)
    {
        GameSetting::where('game_type', $slug)->where('key', $key)->delete();
        return response()->json(['success' => true]);
    }
}
