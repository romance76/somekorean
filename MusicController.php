<?php
namespace App\Http\Controllers\API;

use App\Http\Controllers\Controller;
use App\Models\MusicCategory;
use App\Models\MusicTrack;
use App\Models\UserPlaylist;
use App\Models\UserPlaylistTrack;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Auth;

class MusicController extends Controller {

    public function categories() {
        $cats = MusicCategory::where('is_active', true)
            ->withCount(['tracks' => fn($q) => $q->where('is_active', true)])
            ->orderBy('sort_order')->orderBy('id')->get();
        return response()->json($cats);
    }

    public function tracks(Request $request, $categoryId) {
        $cat = MusicCategory::where('is_active', true)->findOrFail($categoryId);
        $tracks = MusicTrack::where('category_id', $categoryId)
            ->where('is_active', true)
            ->orderBy('sort_order')->orderBy('id')
            ->get();
        return response()->json(['category' => $cat, 'tracks' => $tracks]);
    }

    public function playTrack(Request $request, $trackId) {
        $track = MusicTrack::findOrFail($trackId);
        $track->increment('play_count');
        return response()->json(['ok' => true, 'play_count' => $track->play_count]);
    }

    public function myPlaylists() {
        $playlists = UserPlaylist::where('user_id', Auth::id())
            ->withCount('tracks')
            ->orderBy('created_at', 'desc')->get();
        return response()->json($playlists);
    }

    public function createPlaylist(Request $request) {
        $req = $request->validate(['name' => 'required|string|max:100', 'description' => 'nullable|string|max:500', 'is_public' => 'boolean']);
        $playlist = UserPlaylist::create([
            'user_id' => Auth::id(),
            'name' => $req['name'],
            'description' => $req['description'] ?? null,
            'is_public' => $req['is_public'] ?? false,
        ]);
        return response()->json($playlist, 201);
    }

    public function getPlaylist($id) {
        $playlist = UserPlaylist::where('user_id', Auth::id())->with('tracks')->findOrFail($id);
        return response()->json($playlist);
    }

    public function updatePlaylist(Request $request, $id) {
        $playlist = UserPlaylist::where('user_id', Auth::id())->findOrFail($id);
        $req = $request->validate(['name' => 'sometimes|string|max:100', 'description' => 'nullable|string|max:500', 'is_public' => 'boolean']);
        $playlist->update($req);
        return response()->json($playlist);
    }

    public function deletePlaylist($id) {
        $playlist = UserPlaylist::where('user_id', Auth::id())->findOrFail($id);
        $playlist->delete();
        return response()->json(['ok' => true]);
    }

    public function addTrackToPlaylist(Request $request, $playlistId) {
        $playlist = UserPlaylist::where('user_id', Auth::id())->findOrFail($playlistId);
        $req = $request->validate([
            'youtube_url' => 'required|string|max:500',
            'title' => 'nullable|string|max:200',
            'artist' => 'nullable|string|max:100',
        ]);
        $youtubeId = MusicTrack::extractYoutubeId($req['youtube_url']);
        if (!$youtubeId) return response()->json(['message' => '유효한 YouTube URL을 입력해주세요.'], 422);

        $title = $req['title'] ?? null;
        $artist = $req['artist'] ?? null;
        if (!$title) {
            try {
                $oembedUrl = "https://www.youtube.com/oembed?url=https://www.youtube.com/watch?v={$youtubeId}&format=json";
                $ctx = stream_context_create(['http' => ['timeout' => 5]]);
                $oembedData = @file_get_contents($oembedUrl, false, $ctx);
                if ($oembedData) {
                    $oembed = json_decode($oembedData, true);
                    $title = $oembed['title'] ?? "YouTube - {$youtubeId}";
                    if (!$artist) $artist = $oembed['author_name'] ?? null;
                }
            } catch (\Exception $e) {}
            if (!$title) $title = "YouTube - {$youtubeId}";
        }

        $maxOrder = $playlist->tracks()->max('sort_order') ?? 0;
        $track = UserPlaylistTrack::create([
            'playlist_id' => $playlistId,
            'user_id' => Auth::id(),
            'title' => $title,
            'artist' => $artist,
            'youtube_url' => $req['youtube_url'],
            'youtube_id' => $youtubeId,
            'thumbnail' => MusicTrack::getThumbnail($youtubeId),
            'sort_order' => $maxOrder + 1,
        ]);
        return response()->json($track, 201);
    }

    public function removeTrackFromPlaylist($playlistId, $trackId) {
        $playlist = UserPlaylist::where('user_id', Auth::id())->findOrFail($playlistId);
        UserPlaylistTrack::where('playlist_id', $playlistId)->where('id', $trackId)->delete();
        return response()->json(['ok' => true]);
    }

    public function adminCategories() {
        $cats = MusicCategory::withCount('tracks')->orderBy('sort_order')->orderBy('id')->get();
        return response()->json($cats);
    }

    public function adminCreateCategory(Request $request) {
        $req = $request->validate(['name' => 'required|string|max:100', 'description' => 'nullable|string|max:500', 'icon' => 'nullable|string|max:10', 'sort_order' => 'integer']);
        $cat = MusicCategory::create(array_merge($req, ['created_by' => Auth::id()]));
        return response()->json($cat, 201);
    }

    public function adminUpdateCategory(Request $request, $id) {
        $cat = MusicCategory::findOrFail($id);
        $req = $request->validate(['name' => 'sometimes|string|max:100', 'description' => 'nullable|string|max:500', 'icon' => 'nullable|string|max:10', 'sort_order' => 'integer', 'is_active' => 'boolean']);
        $cat->update($req);
        return response()->json($cat);
    }

    public function adminDeleteCategory($id) {
        MusicCategory::findOrFail($id)->delete();
        return response()->json(['ok' => true]);
    }

    public function adminCreateTrack(Request $request) {
        $req = $request->validate([
            'category_id' => 'required|exists:music_categories,id',
            'youtube_url' => 'required|string|max:500',
            'title' => 'nullable|string|max:200',
            'artist' => 'nullable|string|max:100',
            'sort_order' => 'integer',
        ]);
        $youtubeId = MusicTrack::extractYoutubeId($req['youtube_url']);
        if (!$youtubeId) return response()->json(['message' => '유효한 YouTube URL을 입력해주세요.'], 422);

        $title = $req['title'] ?? null;
        $artist = $req['artist'] ?? null;
        if (!$title) {
            try {
                $oembedUrl = "https://www.youtube.com/oembed?url=https://www.youtube.com/watch?v={$youtubeId}&format=json";
                $ctx = stream_context_create(['http' => ['timeout' => 5]]);
                $oembedData = @file_get_contents($oembedUrl, false, $ctx);
                if ($oembedData) {
                    $oembed = json_decode($oembedData, true);
                    $title = $oembed['title'] ?? "YouTube - {$youtubeId}";
                    if (!$artist) $artist = $oembed['author_name'] ?? null;
                }
            } catch (\Exception $e) {}
            if (!$title) $title = "YouTube - {$youtubeId}";
        }

        $cat = MusicCategory::findOrFail($req['category_id']);
        $maxOrder = $cat->tracks()->max('sort_order') ?? 0;
        $track = MusicTrack::create([
            'category_id' => $req['category_id'],
            'title' => $title,
            'artist' => $artist,
            'youtube_url' => $req['youtube_url'],
            'youtube_id' => $youtubeId,
            'thumbnail' => MusicTrack::getThumbnail($youtubeId),
            'sort_order' => $req['sort_order'] ?? $maxOrder + 1,
            'added_by' => Auth::id(),
        ]);
        return response()->json($track, 201);
    }

    public function adminUpdateTrack(Request $request, $id) {
        $track = MusicTrack::findOrFail($id);
        $req = $request->validate([
            'title' => 'sometimes|string|max:200',
            'artist' => 'nullable|string|max:100',
            'youtube_url' => 'sometimes|string|max:500',
            'sort_order' => 'integer',
            'is_active' => 'boolean',
        ]);
        if (isset($req['youtube_url'])) {
            $youtubeId = MusicTrack::extractYoutubeId($req['youtube_url']);
            if ($youtubeId) {
                $req['youtube_id'] = $youtubeId;
                $req['thumbnail'] = MusicTrack::getThumbnail($youtubeId);
            }
        }
        $track->update($req);
        return response()->json($track);
    }

    public function adminDeleteTrack($id) {
        MusicTrack::findOrFail($id)->delete();
        return response()->json(['ok' => true]);
    }
}
