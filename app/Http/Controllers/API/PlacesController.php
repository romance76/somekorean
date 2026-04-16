<?php

namespace App\Http\Controllers\API;

use App\Http\Controllers\Controller;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Cache;
use Illuminate\Support\Facades\Http;

class PlacesController extends Controller
{
    public function nearbySchools(Request $request)
    {
        $request->validate([
            'lat' => 'required|numeric',
            'lng' => 'required|numeric',
        ]);

        $lat = $request->lat;
        $lng = $request->lng;
        $radius = $request->input('radius', 8045); // 5 miles in meters

        $cacheKey = "nearby_schools_{$lat}_{$lng}_{$radius}";

        $schools = Cache::remember($cacheKey, 86400, function () use ($lat, $lng, $radius) {
            $apiKey = env('GOOGLE_PLACES_API_KEY');
            if (!$apiKey) return [];

            $results = [];

            $response = Http::get('https://maps.googleapis.com/maps/api/place/nearbysearch/json', [
                'location' => "{$lat},{$lng}",
                'radius' => $radius,
                'type' => 'school',
                'key' => $apiKey,
                'language' => 'en',
            ]);

            $data = $response->json();
            if (!empty($data['results'])) {
                foreach ($data['results'] as $place) {
                    $results[] = [
                        'name' => $place['name'] ?? '',
                        'address' => $place['vicinity'] ?? '',
                        'rating' => $place['rating'] ?? null,
                        'user_ratings_total' => $place['user_ratings_total'] ?? 0,
                        'types' => $place['types'] ?? [],
                        'lat' => $place['geometry']['location']['lat'] ?? null,
                        'lng' => $place['geometry']['location']['lng'] ?? null,
                        'place_id' => $place['place_id'] ?? '',
                        'open_now' => $place['opening_hours']['open_now'] ?? null,
                    ];
                }

                // Fetch next page if available
                if (!empty($data['next_page_token']) && count($results) < 40) {
                    sleep(2); // Google requires delay for next_page_token
                    $next = Http::get('https://maps.googleapis.com/maps/api/place/nearbysearch/json', [
                        'pagetoken' => $data['next_page_token'],
                        'key' => $apiKey,
                    ])->json();

                    foreach (($next['results'] ?? []) as $place) {
                        $results[] = [
                            'name' => $place['name'] ?? '',
                            'address' => $place['vicinity'] ?? '',
                            'rating' => $place['rating'] ?? null,
                            'user_ratings_total' => $place['user_ratings_total'] ?? 0,
                            'types' => $place['types'] ?? [],
                            'lat' => $place['geometry']['location']['lat'] ?? null,
                            'lng' => $place['geometry']['location']['lng'] ?? null,
                            'place_id' => $place['place_id'] ?? '',
                            'open_now' => $place['opening_hours']['open_now'] ?? null,
                        ];
                    }
                }
            }

            // Sort by rating (highest first), nulls last
            usort($results, function ($a, $b) {
                if ($a['rating'] === null) return 1;
                if ($b['rating'] === null) return -1;
                return $b['rating'] <=> $a['rating'];
            });

            return $results;
        });

        return response()->json(['success' => true, 'data' => $schools]);
    }
}
