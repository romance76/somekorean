<?php

namespace App\Http\Controllers\API;

use App\Http\Controllers\Controller;
use App\Models\Event;
use App\Models\Bookmark;
use App\Models\Comment;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Auth;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Facades\Storage;

class EventController extends Controller
{
    /**
     * GET /api/events
     * List events with category, date range, distance filter, upcoming by default
     */
    public function index(Request $request)
    {
        $query = Event::whereNotIn('status', ['cancelled', 'draft'])
            ->with('user:id,name,username,avatar');

        // Category filter
        if ($request->filled('category')) {
            $query->where('category', $request->category);
        }

        // Region filter
        if ($request->filled('region')) {
            $query->where('region', $request->region);
        }

        // Date range filter
        if ($request->filled('start_date')) {
            $query->where('event_date', '>=', $request->start_date);
        }
        if ($request->filled('end_date')) {
            $query->where('event_date', '<=', $request->end_date);
        }

        // By default show upcoming events
        if (!$request->filled('start_date') && !$request->filled('show_past')) {
            $query->where('event_date', '>=', now());
        }

        // Search
        if ($request->filled('search')) {
            $s = $request->search;
            $query->where(function ($q) use ($s) {
                $q->where('title', 'like', "%{$s}%")
                  ->orWhere('description', 'like', "%{$s}%")
                  ->orWhere('location', 'like', "%{$s}%");
            });
        }

        // Distance filter (Haversine)
        $lat = $request->input('lat');
        $lng = $request->input('lng');
        $radius = $request->input('radius');

        if ($lat && $lng && $radius && (float) $radius > 0) {
            $query->selectRaw(
                "*, (3959 * acos(cos(radians(?)) * cos(radians(latitude)) * cos(radians(longitude) - radians(?)) + sin(radians(?)) * sin(radians(latitude)))) AS distance",
                [(float) $lat, (float) $lng, (float) $lat]
            )->having('distance', '<', (float) $radius)
              ->orderBy('distance');
        } else {
            $query->orderBy('event_date');
        }

        return response()->json([
            'success' => true,
            'data'    => $query->paginate(20),
        ]);
    }

    /**
     * GET /api/events/{id}
     * Single event with view_count, attendee_count, user attending status
     */
    public function show($id)
    {
        $event = Event::with('user:id,name,username,avatar')->findOrFail($id);
        $event->increment('view_count');

        $isAttending = false;
        $isLiked = false;
        $isBookmarked = false;

        if (Auth::check()) {
            $isAttending = DB::table('event_attendees')
                ->where('event_id', $id)
                ->where('user_id', Auth::id())
                ->exists();
            $isLiked = DB::table('content_likes')
                ->where('user_id', Auth::id())
                ->where('likeable_type', 'event')
                ->where('likeable_id', $id)
                ->exists();
            $isBookmarked = Bookmark::where('user_id', Auth::id())
                ->where('bookmarkable_type', Event::class)
                ->where('bookmarkable_id', $id)
                ->exists();
        }

        $likeCount = DB::table('content_likes')
            ->where('likeable_type', 'event')
            ->where('likeable_id', $id)
            ->count();

        $comments = Comment::where('commentable_type', 'event')
            ->where('commentable_id', $id)
            ->with('user:id,name,username,avatar')
            ->latest()
            ->get();

        return response()->json([
            'success' => true,
            'data'    => array_merge($event->toArray(), [
                'is_attending'  => $isAttending,
                'is_liked'      => $isLiked,
                'is_bookmarked' => $isBookmarked,
                'like_count'    => $likeCount,
                'comments'      => $comments,
            ]),
        ]);
    }

    /**
     * POST /api/events
     * Create event with location data
     */
    public function store(Request $request)
    {
        $data = $request->validate([
            'title'         => 'required|string|max:100',
            'description'   => 'nullable|string',
            'location'      => 'nullable|string',
            'region'        => 'nullable|string',
            'category'      => 'nullable|in:general,meetup,food,culture,sports,education,business,social',
            'max_attendees' => 'nullable|integer|min:1',
            'price'         => 'nullable|numeric|min:0',
            'event_date'    => 'required|date|after:now',
            'is_online'     => 'nullable|boolean',
            'latitude'      => 'nullable|numeric',
            'longitude'     => 'nullable|numeric',
            'image'         => 'nullable|image|max:5120',
        ]);

        if ($request->hasFile('image')) {
            $path = $request->file('image')->store('events', 'public');
            $data['image_url'] = Storage::url($path);
        }

        $event = Event::create(array_merge($data, ['user_id' => Auth::id()]));

        return response()->json([
            'success' => true,
            'message' => '이벤트가 등록되었습니다.',
            'data'    => $event->load('user:id,name,username'),
        ], 201);
    }

    /**
     * PUT /api/events/{id}
     */
    public function update(Request $request, $id)
    {
        $event = Event::findOrFail($id);

        if ($event->user_id !== Auth::id() && !Auth::user()->is_admin) {
            return response()->json(['success' => false, 'message' => '수정 권한이 없습니다.'], 403);
        }

        $event->fill($request->only([
            'title', 'description', 'location', 'region', 'category',
            'event_date', 'is_online', 'max_attendees', 'price',
            'latitude', 'longitude',
        ]));
        $event->save();

        return response()->json([
            'success' => true,
            'message' => '수정되었습니다.',
            'data'    => $event,
        ]);
    }

    /**
     * DELETE /api/events/{id}
     */
    public function destroy($id)
    {
        $event = Event::findOrFail($id);

        if ($event->user_id !== Auth::id() && !Auth::user()->is_admin) {
            return response()->json(['success' => false, 'message' => '삭제 권한이 없습니다.'], 403);
        }

        $event->update(['status' => 'cancelled']);

        return response()->json(['success' => true, 'message' => '이벤트가 취소되었습니다.']);
    }

    /**
     * POST /api/events/{id}/attend
     * Toggle attendance (going/interested or remove)
     */
    public function toggleAttend($id)
    {
        $event = Event::findOrFail($id);

        if (in_array($event->status, ['cancelled', 'draft'])) {
            return response()->json(['success' => false, 'message' => '참가할 수 없는 이벤트입니다.'], 422);
        }

        $exists = DB::table('event_attendees')
            ->where('event_id', $id)
            ->where('user_id', Auth::id())
            ->exists();

        if ($exists) {
            DB::table('event_attendees')
                ->where('event_id', $id)
                ->where('user_id', Auth::id())
                ->delete();
            $event->decrement('attendee_count');

            return response()->json([
                'success' => true,
                'data'    => [
                    'attending'      => false,
                    'attendee_count' => $event->fresh()->attendee_count,
                ],
            ]);
        }

        if ($event->max_attendees && $event->attendee_count >= $event->max_attendees) {
            return response()->json(['success' => false, 'message' => '정원이 초과되었습니다.'], 422);
        }

        DB::table('event_attendees')->insert([
            'event_id'   => $id,
            'user_id'    => Auth::id(),
            'created_at' => now(),
            'updated_at' => now(),
        ]);
        $event->increment('attendee_count');

        // Points
        Auth::user()->addPoints(2, 'event_attend', 'earn', (int) $id, '이벤트 참가');

        return response()->json([
            'success' => true,
            'data'    => [
                'attending'      => true,
                'attendee_count' => $event->fresh()->attendee_count,
            ],
        ]);
    }

    /**
     * POST /api/events/{id}/like
     */
    public function like($id)
    {
        Event::findOrFail($id);
        $userId = Auth::id();

        $existing = DB::table('content_likes')
            ->where('user_id', $userId)
            ->where('likeable_type', 'event')
            ->where('likeable_id', $id)
            ->first();

        if ($existing) {
            DB::table('content_likes')->where('id', $existing->id)->delete();
        } else {
            DB::table('content_likes')->insert([
                'user_id'       => $userId,
                'likeable_type' => 'event',
                'likeable_id'   => $id,
                'created_at'    => now(),
            ]);
        }

        $likeCount = DB::table('content_likes')
            ->where('likeable_type', 'event')
            ->where('likeable_id', $id)
            ->count();

        return response()->json([
            'success' => true,
            'data'    => ['liked' => !$existing, 'like_count' => $likeCount],
        ]);
    }

    /**
     * POST /api/events/{id}/bookmark
     */
    public function bookmark($id)
    {
        Event::findOrFail($id);
        $userId = Auth::id();

        $existing = Bookmark::where('user_id', $userId)
            ->where('bookmarkable_type', Event::class)
            ->where('bookmarkable_id', $id)
            ->first();

        if ($existing) {
            $existing->delete();
            return response()->json(['success' => true, 'data' => ['bookmarked' => false]]);
        }

        Bookmark::create([
            'user_id'           => $userId,
            'bookmarkable_type' => Event::class,
            'bookmarkable_id'   => $id,
        ]);

        return response()->json(['success' => true, 'data' => ['bookmarked' => true]]);
    }

    /**
     * POST /api/events/{id}/comment
     */
    public function comment(Request $request, $id)
    {
        Event::findOrFail($id);
        $request->validate(['content' => 'required|string|max:2000']);

        $comment = Comment::create([
            'commentable_type' => 'event',
            'commentable_id'   => $id,
            'user_id'          => Auth::id(),
            'content'          => $request->content,
        ]);

        // Points (max 10 per day)
        $todayCount = Comment::where('user_id', Auth::id())->whereDate('created_at', today())->count();
        if ($todayCount <= 10) {
            Auth::user()->addPoints(5, 'comment_write', 'earn', $comment->id, '댓글 작성');
        }

        return response()->json([
            'success' => true,
            'message' => '댓글이 등록되었습니다.',
            'data'    => $comment->load('user:id,name,username,avatar'),
        ], 201);
    }
}
