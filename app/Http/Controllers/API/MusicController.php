<?php

namespace App\Http\Controllers\API;

use App\Http\Controllers\Controller;
use App\Models\MusicCategory;
use App\Models\MusicTrack;
use App\Models\UserPlaylist;
use App\Models\UserPlaylistTrack;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Auth;

class MusicController extends Controller
{
    /**
     * GET /api/music/categories
     * List music categories
     */
    public function categories()
    {
        $cats = MusicCategory::where('is_active', true)
            ->withCount(['tracks' => fn($q) => $q->where('is_active', true)])
            ->orderBy('sort_order')
            ->orderBy('id')
            ->get();

        return response()->json(['success' => true, 'data' => $cats]);
    }

    /**
     * GET /api/music/categories/{categoryId}/tracks
     * List tracks in category
     */
    public function tracks(Request $request, $categoryId)
    {
        $cat = MusicCategory::where('is_active', true)->findOrFail($categoryId);

        $tracks = MusicTrack::where('category_id', $categoryId)
            ->where('is_active', true)
            ->orderBy('sort_order')
            ->orderBy('id')
            ->get();

        return response()->json([
            'success' => true,
            'data'    => ['category' => $cat, 'tracks' => $tracks],
        ]);
    }

    /**
     * POST /api/music/tracks/{trackId}/play
     * Increment play count
     */
    public function playTrack($trackId)
    {
        $track = MusicTrack::findOrFail($trackId);
        $track->increment('play_count');

        return response()->json([
            'success' => true,
            'data'    => ['play_count' => $track->fresh()->play_count],
        ]);
    }

    /**
     * GET /api/music/playlists
     * User's playlists
     */
    public function playlists()
    {
        $playlists = UserPlaylist::where('user_id', Auth::id())
            ->withCount('tracks')
            ->orderByDesc('created_at')
            ->get();

        return response()->json(['success' => true, 'data' => $playlists]);
    }

    /**
     * POST /api/music/playlists
     * Create new playlist
     */
    public function createPlaylist(Request $request)
    {
        $request->validate([
            'name'        => 'required|string|max:100',
            'description' => 'nullable|string|max:500',
            'is_public'   => 'nullable|boolean',
        ]);

        $playlist = UserPlaylist::create([
            'user_id'     => Auth::id(),
            'name'        => $request->name,
            'description' => $request->description,
            'is_public'   => $request->boolean('is_public', false),
        ]);

        return response()->json([
            'success' => true,
            'message' => '플레이리스트가 생성되었습니다.',
            'data'    => $playlist,
        ], 201);
    }

    /**
     * GET /api/music/playlists/{id}
     */
    public function getPlaylist($id)
    {
        $playlist = UserPlaylist::where('user_id', Auth::id())
            ->with('tracks')
            ->findOrFail($id);

        return response()->json(['success' => true, 'data' => $playlist]);
    }

    /**
     * PUT /api/music/playlists/{id}
     */
    public function updatePlaylist(Request $request, $id)
    {
        $playlist = UserPlaylist::where('user_id', Auth::id())->findOrFail($id);

        $request->validate([
            'name'        => 'sometimes|string|max:100',
            'description' => 'nullable|string|max:500',
            'is_public'   => 'nullable|boolean',
        ]);

        $playlist->update($request->only(['name', 'description', 'is_public']));

        return response()->json(['success' => true, 'data' => $playlist]);
    }

    /**
     * DELETE /api/music/playlists/{id}
     */
    public function deletePlaylist($id)
    {
        $playlist = UserPlaylist::where('user_id', Auth::id())->findOrFail($id);
        $playlist->delete();

        return response()->json(['success' => true, 'message' => '삭제되었습니다.']);
    }

    /**
     * POST /api/music/playlists/{playlistId}/tracks
     * Add track to playlist (youtube URL)
     */
    public function addTrack(Request $request, $playlistId)
    {
        $playlist = UserPlaylist::where('user_id', Auth::id())->findOrFail($playlistId);

        $request->validate([
            'youtube_url' => 'required|string|max:500',
            'title'       => 'nullable|string|max:200',
            'artist'      => 'nullable|string|max:100',
        ]);

        $youtubeId = MusicTrack::extractYoutubeId($request->youtube_url);
        if (!$youtubeId) {
            return response()->json(['success' => false, 'message' => '유효한 YouTube URL을 입력해주세요.'], 422);
        }

        $title = $request->title;
        $artist = $request->artist;

        // Auto-fetch title from YouTube oEmbed
        if (!$title) {
            try {
                $oembedUrl = "https://www.youtube.com/oembed?url=https://www.youtube.com/watch?v={$youtubeId}&format=json";
                $ctx = stream_context_create(['http' => ['timeout' => 5]]);
                $oembedData = @file_get_contents($oembedUrl, false, $ctx);
                if ($oembedData) {
                    $oembed = json_decode($oembedData, true);
                    $title = $oembed['title'] ?? "YouTube - {$youtubeId}";
                    if (!$artist) {
                        $artist = $oembed['author_name'] ?? null;
                    }
                }
            } catch (\Exception $e) {
                // Skip
            }
            if (!$title) {
                $title = "YouTube - {$youtubeId}";
            }
        }

        $maxOrder = $playlist->tracks()->max('sort_order') ?? 0;

        $track = UserPlaylistTrack::create([
            'playlist_id' => $playlistId,
            'user_id'     => Auth::id(),
            'title'       => $title,
            'artist'      => $artist,
            'youtube_url' => $request->youtube_url,
            'youtube_id'  => $youtubeId,
            'thumbnail'   => MusicTrack::getThumbnail($youtubeId),
            'sort_order'  => $maxOrder + 1,
        ]);

        return response()->json([
            'success' => true,
            'message' => '트랙이 추가되었습니다.',
            'data'    => $track,
        ], 201);
    }

    /**
     * DELETE /api/music/playlists/{playlistId}/tracks/{trackId}
     * Remove track from playlist
     */
    public function removeTrack($playlistId, $trackId)
    {
        UserPlaylist::where('user_id', Auth::id())->findOrFail($playlistId);
        UserPlaylistTrack::where('playlist_id', $playlistId)->where('id', $trackId)->delete();

        return response()->json(['success' => true, 'message' => '트랙이 삭제되었습니다.']);
    }

    // ===================== ADMIN =====================

    /**
     * GET /api/admin/music/categories
     */
    public function adminCategories()
    {
        $cats = MusicCategory::withCount('tracks')
            ->orderBy('sort_order')
            ->orderBy('id')
            ->get();

        return response()->json(['success' => true, 'data' => $cats]);
    }

    /**
     * POST /api/admin/music/categories
     * Admin create category
     */
    public function storeCategory(Request $request)
    {
        $request->validate([
            'name'        => 'required|string|max:100',
            'description' => 'nullable|string|max:500',
            'icon'        => 'nullable|string|max:10',
            'sort_order'  => 'nullable|integer',
        ]);

        $cat = MusicCategory::create(array_merge(
            $request->only(['name', 'description', 'icon', 'sort_order']),
            ['created_by' => Auth::id()]
        ));

        return response()->json(['success' => true, 'data' => $cat], 201);
    }

    /**
     * PUT /api/admin/music/categories/{id}
     */
    public function updateCategory(Request $request, $id)
    {
        $cat = MusicCategory::findOrFail($id);

        $request->validate([
            'name'        => 'sometimes|string|max:100',
            'description' => 'nullable|string|max:500',
            'icon'        => 'nullable|string|max:10',
            'sort_order'  => 'nullable|integer',
            'is_active'   => 'nullable|boolean',
        ]);

        $cat->update($request->only(['name', 'description', 'icon', 'sort_order', 'is_active']));

        return response()->json(['success' => true, 'data' => $cat]);
    }

    /**
     * DELETE /api/admin/music/categories/{id}
     */
    public function destroyCategory($id)
    {
        MusicCategory::findOrFail($id)->delete();
        return response()->json(['success' => true, 'message' => '삭제되었습니다.']);
    }

    /**
     * POST /api/admin/music/tracks
     * Admin add track (youtube URL)
     */
    public function storeTrack(Request $request)
    {
        $request->validate([
            'category_id' => 'required|exists:music_categories,id',
            'youtube_url'  => 'required|string|max:500',
            'title'        => 'nullable|string|max:200',
            'artist'       => 'nullable|string|max:100',
            'sort_order'   => 'nullable|integer',
        ]);

        $youtubeId = MusicTrack::extractYoutubeId($request->youtube_url);
        if (!$youtubeId) {
            return response()->json(['success' => false, 'message' => '유효한 YouTube URL을 입력해주세요.'], 422);
        }

        $title = $request->title;
        $artist = $request->artist;

        if (!$title) {
            try {
                $oembedUrl = "https://www.youtube.com/oembed?url=https://www.youtube.com/watch?v={$youtubeId}&format=json";
                $ctx = stream_context_create(['http' => ['timeout' => 5]]);
                $oembedData = @file_get_contents($oembedUrl, false, $ctx);
                if ($oembedData) {
                    $oembed = json_decode($oembedData, true);
                    $title = $oembed['title'] ?? "YouTube - {$youtubeId}";
                    if (!$artist) {
                        $artist = $oembed['author_name'] ?? null;
                    }
                }
            } catch (\Exception $e) {
                // Skip
            }
            if (!$title) {
                $title = "YouTube - {$youtubeId}";
            }
        }

        $cat = MusicCategory::findOrFail($request->category_id);
        $maxOrder = $cat->tracks()->max('sort_order') ?? 0;

        $track = MusicTrack::create([
            'category_id' => $request->category_id,
            'title'       => $title,
            'artist'      => $artist,
            'youtube_url' => $request->youtube_url,
            'youtube_id'  => $youtubeId,
            'thumbnail'   => MusicTrack::getThumbnail($youtubeId),
            'sort_order'  => $request->sort_order ?? $maxOrder + 1,
            'added_by'    => Auth::id(),
        ]);

        return response()->json(['success' => true, 'data' => $track], 201);
    }

    /**
     * PUT /api/admin/music/tracks/{id}
     */
    public function updateTrack(Request $request, $id)
    {
        $track = MusicTrack::findOrFail($id);

        $request->validate([
            'title'       => 'sometimes|string|max:200',
            'artist'      => 'nullable|string|max:100',
            'youtube_url' => 'sometimes|string|max:500',
            'sort_order'  => 'nullable|integer',
            'is_active'   => 'nullable|boolean',
        ]);

        $data = $request->only(['title', 'artist', 'youtube_url', 'sort_order', 'is_active']);

        if (isset($data['youtube_url'])) {
            $youtubeId = MusicTrack::extractYoutubeId($data['youtube_url']);
            if ($youtubeId) {
                $data['youtube_id'] = $youtubeId;
                $data['thumbnail'] = MusicTrack::getThumbnail($youtubeId);
            }
        }

        $track->update($data);

        return response()->json(['success' => true, 'data' => $track]);
    }

    /**
     * DELETE /api/admin/music/tracks/{id}
     * Admin delete track
     */
    public function destroyTrack($id)
    {
        MusicTrack::findOrFail($id)->delete();
        return response()->json(['success' => true, 'message' => '삭제되었습니다.']);
    }
}
