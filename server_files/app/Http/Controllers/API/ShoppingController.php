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

    // GET /api/shopping/nearby-stores
    public function nearbyStores(Request $request)
    {
        $lat = $request->input('lat');
        $lng = $request->input('lng');
        $radius = $request->input('radius_miles', 30);

        if (!$lat || !$lng) {
            return response()->json(['message' => 'lat, lng required'], 422);
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
                'store' => $store,
                'nearest_location' => $nearest,
                'distance' => round($nearest->distance, 1),
                'is_open_now' => $nearest->is_open_now,
                'locations_count' => $locs->count(),
                'deals_count' => $store->activeDeals()->count(),
                'special_deals_count' => $store->activeDeals()->where('is_special', true)->count(),
            ];
        })->filter()->values();

        return response()->json($grouped);
    }

    // GET /api/shopping/stores
    public function stores(Request $request)
    {
        $q = ShoppingStore::where('is_active', true);

        if ($request->category) {
            $q->where('category', $request->category);
        }
        if ($request->region && $request->region !== 'all') {
            $q->where(function ($q) use ($request) {
                $q->where('region', $request->region)->orWhere('region', 'National');
            });
        }
        if ($request->type) {
            $q->where('type', $request->type);
        }

        $stores = $q->withCount(['locations' => fn($q) => $q->where('is_active', true)])
            ->withCount(['deals as active_deals_count' => fn($q) => $q->where('is_active', true)
                ->where(fn($q) => $q->whereNull('valid_until')->orWhere('valid_until', '>=', now()))])
            ->get();

        return response()->json($stores);
    }

    // GET /api/shopping/stores/{id}
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
            'store' => $store,
            'deals' => $activeDeals,
            'flyers' => $flyers,
        ];

        // If lat/lng provided, find nearest location
        if ($request->lat && $request->lng) {
            $nearest = StoreLocation::where('store_id', $id)
                ->where('is_active', true)
                ->nearby($request->lat, $request->lng)
                ->first();
            $result['nearest_location'] = $nearest;
        }

        return response()->json($result);
    }

    // GET /api/shopping/deals
    public function deals(Request $request)
    {
        $q = ShoppingDeal::with('store:id,name,logo,type,region,logo_url,category')
            ->where('is_active', true)
            ->where(fn($q) => $q->whereNull('valid_until')->orWhere('valid_until', '>=', now()->toDateString()));

        if ($request->store_id) {
            $q->where('store_id', $request->store_id);
        }
        if ($request->category) {
            $q->where('category', $request->category);
        }
        if ($request->is_special) {
            $q->where('is_special', true);
        }
        if ($request->search) {
            $q->where('title', 'like', '%'.$request->search.'%');
        }
        if ($request->featured) {
            $q->where('is_featured', true);
        }

        // Location-based filtering
        if ($request->lat && $request->lng) {
            $radius = $request->input('radius_miles', 30);
            $storeIds = StoreLocation::where('is_active', true)
                ->nearby($request->lat, $request->lng, $radius)
                ->pluck('store_id')
                ->unique();
            $q->whereIn('store_id', $storeIds);
        }

        $deals = $q->orderByDesc('is_featured')
            ->orderByDesc('is_special')
            ->orderByDesc('created_at')
            ->paginate(20);

        return response()->json($deals);
    }

    // GET /api/shopping/categories
    public function categories()
    {
        $cats = ShoppingDeal::where('is_active', true)
            ->whereNotNull('category')
            ->select('category')
            ->distinct()
            ->pluck('category');
        return response()->json($cats);
    }

    // ===================== ADMIN =====================

    // GET /api/admin/shopping/stores
    public function adminStores(Request $request)
    {
        $q = ShoppingStore::withTrashed()
            ->withCount('locations')
            ->withCount('deals');

        if ($request->category) {
            $q->where('category', $request->category);
        }

        $stores = $q->orderBy('name')->get();
        return response()->json($stores);
    }

    // POST /api/admin/shopping/stores
    public function adminStoreStore(Request $request)
    {
        $request->validate([
            'name' => 'required|string|max:100',
        ]);

        $store = ShoppingStore::create($request->only([
            'name','name_en','chain_name','category','logo_url','type','region',
            'website','weekly_ad_url','rss_url','scrape_method','scrape_schedule',
            'logo','description','is_active','memo'
        ]));

        return response()->json($store, 201);
    }

    // PUT /api/admin/shopping/stores/{id}
    public function adminUpdateStore(Request $request, $id)
    {
        $store = ShoppingStore::withTrashed()->findOrFail($id);
        $store->update($request->only([
            'name','name_en','chain_name','category','logo_url','type','region',
            'website','weekly_ad_url','rss_url','scrape_method','scrape_schedule',
            'logo','description','is_active','memo'
        ]));

        return response()->json($store);
    }

    // DELETE /api/admin/shopping/stores/{id}
    public function adminDeleteStore($id)
    {
        $store = ShoppingStore::findOrFail($id);
        $store->delete();
        return response()->json(['message' => 'deleted']);
    }

    // GET /api/admin/shopping/stores/{id}/locations
    public function adminLocations($id)
    {
        $locations = StoreLocation::where('store_id', $id)->orderBy('branch_name')->get();
        return response()->json($locations);
    }

    // POST /api/admin/shopping/stores/{id}/locations
    public function adminStoreLocation(Request $request, $id)
    {
        $request->validate([
            'address' => 'required|string',
        ]);

        $data = $request->only(['branch_name','address','city','state','zip_code','lat','lng','phone','open_time','close_time','open_days','is_24h','is_active']);
        $data['store_id'] = $id;

        $location = StoreLocation::create($data);
        return response()->json($location, 201);
    }

    // PUT /api/admin/shopping/locations/{id}
    public function adminUpdateLocation(Request $request, $id)
    {
        $location = StoreLocation::findOrFail($id);
        $location->update($request->only(['branch_name','address','city','state','zip_code','lat','lng','phone','open_time','close_time','open_days','is_24h','is_active']));
        return response()->json($location);
    }

    // DELETE /api/admin/shopping/locations/{id}
    public function adminDeleteLocation($id)
    {
        StoreLocation::findOrFail($id)->delete();
        return response()->json(['message' => 'deleted']);
    }

    // GET /api/admin/shopping/deals
    public function adminDeals(Request $request)
    {
        $q = ShoppingDeal::with('store:id,name');

        if ($request->store_id) {
            $q->where('store_id', $request->store_id);
        }
        if ($request->category) {
            $q->where('category', $request->category);
        }
        if ($request->has_error) {
            $q->where(function($q) {
                $q->where('sale_price', 0)->orWhere('sale_price', null)
                  ->orWhere('discount_percent', 0)->orWhere('discount_percent', null);
            })->where(function($q) {
                $q->where('price', 0)->orWhere('price', null);
            });
        }

        $deals = $q->orderByDesc('created_at')->paginate(30);
        return response()->json($deals);
    }

    // POST /api/admin/shopping/deals
    public function adminStoreDeal(Request $request)
    {
        $request->validate([
            'store_id' => 'required|exists:shopping_stores,id',
            'title' => 'required|string|max:200',
        ]);

        $deal = ShoppingDeal::create($request->only([
            'store_id','title','description','url','source_url','source',
            'price','original_price','sale_price','discount_percent',
            'image_url','category','is_active','is_featured','is_special',
            'valid_from','valid_until','unit'
        ]));

        return response()->json($deal, 201);
    }

    // PUT /api/admin/shopping/deals/{id}
    public function adminUpdateDeal(Request $request, $id)
    {
        $deal = ShoppingDeal::findOrFail($id);
        $deal->update($request->only([
            'store_id','title','description','url','source_url','source',
            'price','original_price','sale_price','discount_percent',
            'image_url','category','is_active','is_featured','is_special',
            'valid_from','valid_until','unit'
        ]));

        return response()->json($deal);
    }

    // DELETE /api/admin/shopping/deals/{id}
    public function adminDeleteDeal($id)
    {
        ShoppingDeal::findOrFail($id)->delete();
        return response()->json(['message' => 'deleted']);
    }

    // DELETE /api/admin/shopping/deals-bulk-errors
    public function adminBulkDeleteErrors()
    {
        $count = ShoppingDeal::where(function($q) {
            $q->where('sale_price', 0)->orWhereNull('sale_price');
        })->where(function($q) {
            $q->where('discount_percent', 0)->orWhereNull('discount_percent');
        })->where(function($q) {
            $q->where('price', 0)->orWhereNull('price');
        })->delete();

        return response()->json(['message' => "{$count} error deals deleted", 'count' => $count]);
    }

    // GET /api/admin/shopping/flyers
    public function adminFlyers(Request $request)
    {
        $q = StoreFlyer::with('store:id,name');
        if ($request->store_id) {
            $q->where('store_id', $request->store_id);
        }
        $flyers = $q->orderByDesc('created_at')->paginate(30);
        return response()->json($flyers);
    }

    // POST /api/admin/shopping/flyers
    public function adminStoreFlyer(Request $request)
    {
        $request->validate([
            'store_id' => 'required|exists:shopping_stores,id',
            'image_url' => 'required|string',
        ]);

        $flyer = StoreFlyer::create($request->only([
            'store_id','title','image_url','valid_from','valid_until','is_active'
        ]));

        return response()->json($flyer, 201);
    }

    // DELETE /api/admin/shopping/flyers/{id}
    public function adminDeleteFlyer($id)
    {
        StoreFlyer::findOrFail($id)->delete();
        return response()->json(['message' => 'deleted']);
    }

    // GET /api/admin/shopping/scrape-logs
    public function adminScrapeLogs()
    {
        $logs = ScrapeLog::with('store:id,name')
            ->orderByDesc('created_at')
            ->limit(50)
            ->get();
        return response()->json($logs);
    }
}
