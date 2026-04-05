<?php

namespace App\Http\Controllers\API;

use App\Http\Controllers\Controller;
use App\Models\ShoppingStore;
use App\Models\ShoppingDeal;
use App\Models\StoreLocation;
use App\Models\StoreFlyer;
use App\Models\ScrapeLog;
use Illuminate\Http\Request;

class ShoppingController extends Controller
{
    // ===================== PUBLIC =====================

    /**
     * GET /api/shopping/deals
     * List deals with store filter, category, active only, sorted by discount
     */
    public function index(Request $request)
    {
        $query = ShoppingDeal::with('store:id,name,logo,type,region,logo_url,category')
            ->where('is_active', true)
            ->where(fn($q) => $q->whereNull('valid_until')->orWhere('valid_until', '>=', now()->toDateString()));

        // Store filter
        if ($request->filled('store_id')) {
            $query->where('store_id', $request->store_id);
        }

        // Category filter
        if ($request->filled('category')) {
            $query->where('category', $request->category);
        }

        // Special deals only
        if ($request->filled('is_special')) {
            $query->where('is_special', true);
        }

        // Featured
        if ($request->filled('featured')) {
            $query->where('is_featured', true);
        }

        // Search
        if ($request->filled('search')) {
            $query->where('title', 'like', '%' . $request->search . '%');
        }

        // Location-based filtering
        if ($request->filled('lat') && $request->filled('lng')) {
            $radius = (float) ($request->input('radius_miles', 30));
            $storeIds = StoreLocation::where('is_active', true)
                ->nearby($request->lat, $request->lng, $radius)
                ->pluck('store_id')
                ->unique();
            $query->whereIn('store_id', $storeIds);
        }

        // Sort by discount
        $query->orderByDesc('is_featured')
              ->orderByDesc('is_special')
              ->orderByDesc('discount_percent')
              ->orderByDesc('created_at');

        return response()->json([
            'success' => true,
            'data'    => $query->paginate(20),
        ]);
    }

    /**
     * GET /api/shopping/stores
     * List active stores
     */
    public function stores(Request $request)
    {
        $query = ShoppingStore::where('is_active', true);

        if ($request->filled('category')) {
            $query->where('category', $request->category);
        }
        if ($request->filled('region') && $request->region !== 'all') {
            $query->where(function ($q) use ($request) {
                $q->where('region', $request->region)->orWhere('region', 'National');
            });
        }
        if ($request->filled('type')) {
            $query->where('type', $request->type);
        }

        $stores = $query
            ->withCount(['locations' => fn($q) => $q->where('is_active', true)])
            ->withCount(['deals as active_deals_count' => fn($q) => $q->where('is_active', true)
                ->where(fn($q) => $q->whereNull('valid_until')->orWhere('valid_until', '>=', now()))])
            ->get();

        return response()->json(['success' => true, 'data' => $stores]);
    }

    /**
     * GET /api/shopping/stores/{id}
     */
    public function showStore(Request $request, $id)
    {
        $store = ShoppingStore::with(['locations' => fn($q) => $q->where('is_active', true)])
            ->findOrFail($id);

        $activeDeals = $store->activeDeals()
            ->orderByDesc('is_special')
            ->orderByDesc('created_at')
            ->limit(50)
            ->get();

        $flyers = StoreFlyer::where('store_id', $id)
            ->where('is_active', true)
            ->where(fn($q) => $q->whereNull('valid_until')->orWhere('valid_until', '>=', now()))
            ->get();

        $result = [
            'store'  => $store,
            'deals'  => $activeDeals,
            'flyers' => $flyers,
        ];

        if ($request->filled('lat') && $request->filled('lng')) {
            $result['nearest_location'] = StoreLocation::where('store_id', $id)
                ->where('is_active', true)
                ->nearby($request->lat, $request->lng)
                ->first();
        }

        return response()->json(['success' => true, 'data' => $result]);
    }

    /**
     * GET /api/shopping/nearby-stores
     */
    public function nearbyStores(Request $request)
    {
        $lat = $request->input('lat');
        $lng = $request->input('lng');
        $radius = $request->input('radius_miles', 30);

        if (!$lat || !$lng) {
            return response()->json(['success' => false, 'message' => 'lat, lng required'], 422);
        }

        $locations = StoreLocation::with('store')
            ->where('is_active', true)
            ->nearby($lat, $lng, $radius)
            ->get();

        $grouped = $locations->groupBy('store_id')->map(function ($locs) {
            $store = $locs->first()->store;
            if (!$store || !$store->is_active) return null;

            $nearest = $locs->first();
            return [
                'store'               => $store,
                'nearest_location'    => $nearest,
                'distance'            => round($nearest->distance, 1),
                'is_open_now'         => $nearest->is_open_now,
                'locations_count'     => $locs->count(),
                'deals_count'         => $store->activeDeals()->count(),
                'special_deals_count' => $store->activeDeals()->where('is_special', true)->count(),
            ];
        })->filter()->values();

        return response()->json(['success' => true, 'data' => $grouped]);
    }

    /**
     * GET /api/shopping/categories
     */
    public function categories()
    {
        $cats = ShoppingDeal::where('is_active', true)
            ->whereNotNull('category')
            ->select('category')
            ->distinct()
            ->pluck('category');

        return response()->json(['success' => true, 'data' => $cats]);
    }

    // ===================== ADMIN =====================

    public function adminStores(Request $request)
    {
        $q = ShoppingStore::withTrashed()->withCount('locations')->withCount('deals');
        if ($request->filled('category')) {
            $q->where('category', $request->category);
        }
        return response()->json(['success' => true, 'data' => $q->orderBy('name')->get()]);
    }

    public function adminStoreStore(Request $request)
    {
        $request->validate(['name' => 'required|string|max:100']);
        $store = ShoppingStore::create($request->only([
            'name', 'name_en', 'chain_name', 'category', 'logo_url', 'type', 'region',
            'website', 'weekly_ad_url', 'rss_url', 'scrape_method', 'scrape_schedule',
            'logo', 'description', 'is_active', 'memo',
        ]));
        return response()->json(['success' => true, 'data' => $store], 201);
    }

    public function adminUpdateStore(Request $request, $id)
    {
        $store = ShoppingStore::withTrashed()->findOrFail($id);
        $store->update($request->only([
            'name', 'name_en', 'chain_name', 'category', 'logo_url', 'type', 'region',
            'website', 'weekly_ad_url', 'rss_url', 'scrape_method', 'scrape_schedule',
            'logo', 'description', 'is_active', 'memo',
        ]));
        return response()->json(['success' => true, 'data' => $store]);
    }

    public function adminDeleteStore($id)
    {
        ShoppingStore::findOrFail($id)->delete();
        return response()->json(['success' => true, 'message' => 'deleted']);
    }

    public function adminDeals(Request $request)
    {
        $q = ShoppingDeal::with('store:id,name');
        if ($request->filled('store_id')) $q->where('store_id', $request->store_id);
        if ($request->filled('category')) $q->where('category', $request->category);
        return response()->json(['success' => true, 'data' => $q->orderByDesc('created_at')->paginate(30)]);
    }

    public function adminStoreDeal(Request $request)
    {
        $request->validate([
            'store_id' => 'required|exists:shopping_stores,id',
            'title'    => 'required|string|max:200',
        ]);
        $deal = ShoppingDeal::create($request->only([
            'store_id', 'title', 'description', 'url', 'source_url', 'source',
            'price', 'original_price', 'sale_price', 'discount_percent',
            'image_url', 'category', 'is_active', 'is_featured', 'is_special',
            'valid_from', 'valid_until', 'unit',
        ]));
        return response()->json(['success' => true, 'data' => $deal], 201);
    }

    public function adminUpdateDeal(Request $request, $id)
    {
        $deal = ShoppingDeal::findOrFail($id);
        $deal->update($request->only([
            'store_id', 'title', 'description', 'url', 'source_url', 'source',
            'price', 'original_price', 'sale_price', 'discount_percent',
            'image_url', 'category', 'is_active', 'is_featured', 'is_special',
            'valid_from', 'valid_until', 'unit',
        ]));
        return response()->json(['success' => true, 'data' => $deal]);
    }

    public function adminDeleteDeal($id)
    {
        ShoppingDeal::findOrFail($id)->delete();
        return response()->json(['success' => true, 'message' => 'deleted']);
    }

    public function adminLocations($id)
    {
        return response()->json(['success' => true, 'data' => StoreLocation::where('store_id', $id)->orderBy('branch_name')->get()]);
    }

    public function adminStoreLocation(Request $request, $id)
    {
        $request->validate(['address' => 'required|string']);
        $data = $request->only(['branch_name', 'address', 'city', 'state', 'zip_code', 'lat', 'lng', 'phone', 'open_time', 'close_time', 'open_days', 'is_24h', 'is_active']);
        $data['store_id'] = $id;
        return response()->json(['success' => true, 'data' => StoreLocation::create($data)], 201);
    }

    public function adminUpdateLocation(Request $request, $id)
    {
        $location = StoreLocation::findOrFail($id);
        $location->update($request->only(['branch_name', 'address', 'city', 'state', 'zip_code', 'lat', 'lng', 'phone', 'open_time', 'close_time', 'open_days', 'is_24h', 'is_active']));
        return response()->json(['success' => true, 'data' => $location]);
    }

    public function adminDeleteLocation($id)
    {
        StoreLocation::findOrFail($id)->delete();
        return response()->json(['success' => true, 'message' => 'deleted']);
    }

    public function adminFlyers(Request $request)
    {
        $q = StoreFlyer::with('store:id,name');
        if ($request->filled('store_id')) $q->where('store_id', $request->store_id);
        return response()->json(['success' => true, 'data' => $q->orderByDesc('created_at')->paginate(30)]);
    }

    public function adminStoreFlyer(Request $request)
    {
        $request->validate(['store_id' => 'required|exists:shopping_stores,id', 'image_url' => 'required|string']);
        $flyer = StoreFlyer::create($request->only(['store_id', 'title', 'image_url', 'valid_from', 'valid_until', 'is_active']));
        return response()->json(['success' => true, 'data' => $flyer], 201);
    }

    public function adminDeleteFlyer($id)
    {
        StoreFlyer::findOrFail($id)->delete();
        return response()->json(['success' => true, 'message' => 'deleted']);
    }

    public function adminScrapeLogs()
    {
        $logs = ScrapeLog::with('store:id,name')->orderByDesc('created_at')->limit(50)->get();
        return response()->json(['success' => true, 'data' => $logs]);
    }

    public function adminBulkDeleteErrors()
    {
        $count = ShoppingDeal::where(function ($q) {
            $q->where('sale_price', 0)->orWhereNull('sale_price');
        })->where(function ($q) {
            $q->where('discount_percent', 0)->orWhereNull('discount_percent');
        })->where(function ($q) {
            $q->where('price', 0)->orWhereNull('price');
        })->delete();

        return response()->json(['success' => true, 'message' => "{$count} error deals deleted", 'data' => ['count' => $count]]);
    }
}
