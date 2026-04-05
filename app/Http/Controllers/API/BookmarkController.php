<?php

namespace App\Http\Controllers\API;

use App\Http\Controllers\Controller;
use App\Models\Bookmark;
use Illuminate\Http\Request;

class BookmarkController extends Controller
{
    /**
     * Map short type names to model classes.
     */
    private function resolveType(string $type): ?string
    {
        $map = [
            'post'        => 'App\\Models\\Post',
            'job'         => 'App\\Models\\JobPost',
            'market'      => 'App\\Models\\MarketItem',
            'business'    => 'App\\Models\\Business',
            'realestate'  => 'App\\Models\\RealEstateListing',
            'event'       => 'App\\Models\\Event',
            'recipe'      => 'App\\Models\\RecipePost',
            'qa'          => 'App\\Models\\QaPost',
            'news'        => 'App\\Models\\News',
        ];

        return $map[$type] ?? null;
    }

    /**
     * POST /api/bookmarks
     * Toggle bookmark (add/remove) for any bookmarkable type.
     */
    public function toggle(Request $request)
    {
        $request->validate([
            'type' => 'required|string',
            'id'   => 'required|integer',
        ]);

        $modelClass = $this->resolveType($request->type);
        if (!$modelClass) {
            return response()->json([
                'success' => false,
                'message' => '잘못된 북마크 유형입니다.',
            ], 400);
        }

        $userId = auth()->id();

        $existing = Bookmark::where('user_id', $userId)
            ->where('bookmarkable_type', $modelClass)
            ->where('bookmarkable_id', $request->id)
            ->first();

        if ($existing) {
            $existing->delete();
            return response()->json([
                'success' => true,
                'data'    => ['bookmarked' => false],
            ]);
        }

        Bookmark::create([
            'user_id'           => $userId,
            'bookmarkable_type' => $modelClass,
            'bookmarkable_id'   => $request->id,
        ]);

        return response()->json([
            'success' => true,
            'data'    => ['bookmarked' => true],
        ]);
    }

    /**
     * GET /api/bookmarks
     * List user's bookmarks grouped by type.
     */
    public function index(Request $request)
    {
        $bookmarks = Bookmark::where('user_id', auth()->id())
            ->with('bookmarkable')
            ->orderByDesc('created_at')
            ->get();

        // Group by type
        $grouped = $bookmarks->groupBy(function ($bookmark) {
            $typeMap = [
                'App\\Models\\Post'              => 'posts',
                'App\\Models\\JobPost'            => 'jobs',
                'App\\Models\\MarketItem'         => 'market',
                'App\\Models\\Business'           => 'businesses',
                'App\\Models\\RealEstateListing'  => 'realestate',
                'App\\Models\\Event'              => 'events',
                'App\\Models\\RecipePost'         => 'recipes',
                'App\\Models\\QaPost'             => 'qa',
                'App\\Models\\News'               => 'news',
            ];
            return $typeMap[$bookmark->bookmarkable_type] ?? 'other';
        });

        return response()->json([
            'success' => true,
            'data'    => $grouped,
        ]);
    }
}
