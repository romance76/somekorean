<?php

namespace App\Console\Commands;

use App\Models\Business;
use App\Models\BusinessReview;
use Illuminate\Console\Command;
use Illuminate\Support\Facades\Http;
use Illuminate\Support\Facades\DB;

class ImportGooglePlaces extends Command
{
    protected $signature = 'places:import {--fresh : 기존 데이터 삭제 후 시작} {--limit=0 : 최대 임포트 수 (0=무제한)}';
    protected $description = 'Google Places API에서 미국 한인 업소 데이터 임포트';

    private $apiKey;
    private $imported = 0;
    private $updated = 0;
    private $errors = 0;

    // 한인 밀집 도시
    private $cities = [
        ['name' => 'Los Angeles', 'state' => 'CA', 'lat' => 34.0522, 'lng' => -118.2437],
        ['name' => 'New York', 'state' => 'NY', 'lat' => 40.7128, 'lng' => -74.0060],
        ['name' => 'Bergen County', 'state' => 'NJ', 'lat' => 40.9176, 'lng' => -74.0712],
        ['name' => 'Atlanta', 'state' => 'GA', 'lat' => 33.7490, 'lng' => -84.3880],
        ['name' => 'Chicago', 'state' => 'IL', 'lat' => 41.8781, 'lng' => -87.6298],
        ['name' => 'Dallas', 'state' => 'TX', 'lat' => 32.7767, 'lng' => -96.7970],
        ['name' => 'Houston', 'state' => 'TX', 'lat' => 29.7604, 'lng' => -95.3698],
        ['name' => 'Seattle', 'state' => 'WA', 'lat' => 47.6062, 'lng' => -122.3321],
        ['name' => 'San Francisco', 'state' => 'CA', 'lat' => 37.7749, 'lng' => -122.4194],
        ['name' => 'Washington', 'state' => 'DC', 'lat' => 38.9072, 'lng' => -77.0369],
        ['name' => 'Philadelphia', 'state' => 'PA', 'lat' => 39.9526, 'lng' => -75.1652],
        ['name' => 'Irvine', 'state' => 'CA', 'lat' => 33.6846, 'lng' => -117.8265],
        ['name' => 'Fullerton', 'state' => 'CA', 'lat' => 33.8703, 'lng' => -117.9242],
        ['name' => 'Flushing', 'state' => 'NY', 'lat' => 40.7654, 'lng' => -73.8328],
        ['name' => 'Honolulu', 'state' => 'HI', 'lat' => 21.3069, 'lng' => -157.8583],
        ['name' => 'Las Vegas', 'state' => 'NV', 'lat' => 36.1699, 'lng' => -115.1398],
        ['name' => 'Denver', 'state' => 'CO', 'lat' => 39.7392, 'lng' => -104.9903],
    ];

    // 검색 키워드 → 카테고리 매핑
    private $searches = [
        'Korean restaurant' => 'restaurant',
        'Korean grocery' => 'mart',
        'Korean market' => 'mart',
        'Korean beauty salon' => 'beauty',
        'Korean nail salon' => 'beauty',
        'Korean hair salon' => 'beauty',
        'Korean church' => 'etc',
        'Korean auto repair' => 'auto',
        'Korean dentist' => 'medical',
        'Korean doctor' => 'medical',
        'Korean lawyer' => 'professional',
        'Korean accountant' => 'professional',
        'Korean real estate' => 'realestate',
        'Korean school' => 'education',
        'Korean spa' => 'beauty',
        'Korean bakery' => 'restaurant',
        'Korean BBQ' => 'restaurant',
    ];

    public function handle()
    {
        $this->apiKey = config('services.google_places.key') ?: env('GOOGLE_PLACES_API_KEY');
        if (!$this->apiKey) {
            $this->error('GOOGLE_PLACES_API_KEY가 설정되지 않았습니다.');
            return 1;
        }

        $limit = (int) $this->option('limit');

        if ($this->option('fresh')) {
            $this->warn('기존 데이터 삭제 중...');
            DB::table('business_reviews')->truncate();
            DB::table('businesses')->truncate();
            $this->info('삭제 완료.');
        }

        $this->info("Google Places API 임포트 시작...");

        foreach ($this->cities as $city) {
            foreach ($this->searches as $query => $category) {
                if ($limit > 0 && $this->imported >= $limit) {
                    $this->info("리밋 {$limit}개 도달. 중단합니다.");
                    $this->printSummary();
                    return 0;
                }

                $this->info("🔍 {$city['name']}: {$query}");

                try {
                    $this->searchAndImport($query, $city, $category);
                } catch (\Exception $e) {
                    if (str_contains($e->getMessage(), 'OVER_QUERY_LIMIT') || str_contains($e->getMessage(), 'quota')) {
                        $this->error("⚠️ API 할당량 초과! 내일 다시 실행하세요.");
                        $this->printSummary();
                        return 0;
                    }
                    $this->error("에러: {$e->getMessage()}");
                    $this->errors++;
                }

                usleep(200000); // 0.2초 대기 (rate limit 방지)
            }
        }

        $this->printSummary();
        return 0;
    }

    private function searchAndImport(string $query, array $city, string $category)
    {
        // Text Search API
        $response = Http::get('https://maps.googleapis.com/maps/api/place/textsearch/json', [
            'query' => "{$query} in {$city['name']}, {$city['state']}",
            'key' => $this->apiKey,
            'language' => 'en',
        ]);

        $data = $response->json();

        if (($data['status'] ?? '') === 'OVER_QUERY_LIMIT') {
            throw new \Exception('OVER_QUERY_LIMIT');
        }

        $results = $data['results'] ?? [];
        $this->line("  → {$query}: " . count($results) . "개 발견");

        foreach ($results as $place) {
            $placeId = $place['place_id'] ?? null;
            if (!$placeId) continue;

            // 이미 존재하면 스킵 (daily update에서는 업데이트)
            $existing = Business::where('google_place_id', $placeId)->first();

            // Place Details 가져오기
            $details = $this->getPlaceDetails($placeId);
            if (!$details) continue;

            $bizData = $this->mapPlaceData($details, $category, $city);

            if ($existing) {
                // 기존 데이터 업데이트 (rating, review_count, reviews)
                $existing->update([
                    'rating' => $bizData['rating'],
                    'review_count' => $bizData['review_count'],
                    'google_reviews' => $bizData['google_reviews'],
                    'phone' => $bizData['phone'] ?: $existing->phone,
                    'website' => $bizData['website'] ?: $existing->website,
                    'hours' => $bizData['hours'] ?: $existing->hours,
                ]);
                $this->updated++;
            } else {
                // 새로 생성
                $biz = Business::create($bizData);

                // 구글 리뷰를 BusinessReview로도 저장
                $this->importReviews($biz, $details['reviews'] ?? []);
                $this->imported++;
            }

            usleep(100000); // 0.1초 대기
        }

        // 다음 페이지가 있으면 가져오기 (최대 1회 추가)
        if (!empty($data['next_page_token'])) {
            sleep(2); // next_page_token은 2초 후 활성화
            $this->fetchNextPage($data['next_page_token'], $category, $city);
        }
    }

    private function fetchNextPage(string $token, string $category, array $city)
    {
        $response = Http::get('https://maps.googleapis.com/maps/api/place/textsearch/json', [
            'pagetoken' => $token,
            'key' => $this->apiKey,
        ]);

        $data = $response->json();
        $results = $data['results'] ?? [];

        foreach ($results as $place) {
            $placeId = $place['place_id'] ?? null;
            if (!$placeId || Business::where('google_place_id', $placeId)->exists()) continue;

            $details = $this->getPlaceDetails($placeId);
            if (!$details) continue;

            $bizData = $this->mapPlaceData($details, $category, $city);
            $biz = Business::create($bizData);
            $this->importReviews($biz, $details['reviews'] ?? []);
            $this->imported++;

            usleep(100000);
        }
    }

    private function getPlaceDetails(string $placeId): ?array
    {
        $response = Http::get('https://maps.googleapis.com/maps/api/place/details/json', [
            'place_id' => $placeId,
            'key' => $this->apiKey,
            'fields' => 'name,formatted_phone_number,formatted_address,geometry,website,opening_hours,rating,user_ratings_total,reviews,address_components',
            'language' => 'en',
        ]);

        $data = $response->json();

        if (($data['status'] ?? '') === 'OVER_QUERY_LIMIT') {
            throw new \Exception('OVER_QUERY_LIMIT');
        }

        return $data['result'] ?? null;
    }

    private function mapPlaceData(array $details, string $category, array $city): array
    {
        // 주소 파싱
        $components = $details['address_components'] ?? [];
        $cityName = $city['name'];
        $stateName = $city['state'];
        $zipcode = '';

        foreach ($components as $c) {
            if (in_array('locality', $c['types'])) $cityName = $c['long_name'];
            if (in_array('administrative_area_level_1', $c['types'])) $stateName = $c['short_name'];
            if (in_array('postal_code', $c['types'])) $zipcode = $c['long_name'];
        }

        // 영업시간 파싱
        $hours = null;
        if (!empty($details['opening_hours']['weekday_text'])) {
            $hours = [];
            foreach ($details['opening_hours']['weekday_text'] as $line) {
                $parts = explode(': ', $line, 2);
                if (count($parts) === 2) {
                    $hours[$parts[0]] = $parts[1];
                }
            }
        }

        // 구글 리뷰 저장
        $googleReviews = [];
        foreach (($details['reviews'] ?? []) as $r) {
            $googleReviews[] = [
                'author' => $r['author_name'] ?? 'Anonymous',
                'rating' => $r['rating'] ?? 5,
                'text' => $r['text'] ?? '',
                'time' => $r['relative_time_description'] ?? '',
            ];
        }

        return [
            'google_place_id' => $details['place_id'] ?? null,
            'name' => $details['name'] ?? 'Unknown',
            'description' => '',
            'category' => $category,
            'phone' => $details['formatted_phone_number'] ?? null,
            'website' => $details['website'] ?? null,
            'address' => $details['formatted_address'] ?? null,
            'city' => $cityName,
            'state' => $stateName,
            'zipcode' => $zipcode,
            'lat' => $details['geometry']['location']['lat'] ?? $city['lat'],
            'lng' => $details['geometry']['location']['lng'] ?? $city['lng'],
            'hours' => $hours,
            'rating' => $details['rating'] ?? 0,
            'review_count' => $details['user_ratings_total'] ?? 0,
            'google_reviews' => $googleReviews,
            'is_verified' => true,
        ];
    }

    private function importReviews(Business $biz, array $reviews)
    {
        foreach ($reviews as $r) {
            // 구글 리뷰는 user_id 없이 저장 (user_id=0 또는 nullable)
            BusinessReview::create([
                'business_id' => $biz->id,
                'user_id' => 1, // 시스템 유저
                'rating' => $r['rating'] ?? 5,
                'content' => ($r['author_name'] ?? 'Google User') . ': ' . ($r['text'] ?? ''),
            ]);
        }
    }

    private function printSummary()
    {
        $this->newLine();
        $this->info("═══ 임포트 완료 ═══");
        $this->info("✅ 새로 추가: {$this->imported}개");
        $this->info("🔄 업데이트: {$this->updated}개");
        $this->info("❌ 에러: {$this->errors}개");
        $this->info("📊 전체 업소: " . Business::count() . "개");
    }
}
