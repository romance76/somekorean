<?php
namespace App\Console\Commands;

use Illuminate\Console\Command;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Facades\Http;

class FetchYoutubeShorts extends Command
{
    protected $signature = 'shorts:fetch {--limit=75 : Number of new shorts to add} {--keep=500 : Max YouTube shorts to keep}';
    protected $description = 'Fetch new Korean YouTube shorts and clean up old ones';

    // 40개 한국 관련 YouTube 채널 - 매일 랜덤으로 선택
    protected $channels = [
        // 요리/음식
        ['id' => 'UC8gFadPgK2r1ndqLI04Xvvw', 'name' => '마망쉬(Maangchi)', 'tag' => '한식'],
        ['id' => 'UCIvA9ZGeoR6CH2e0DZtvxzw', 'name' => 'Seonkyoung Longest', 'tag' => '한식'],
        ['id' => 'UC5qRAYQmCLx8hFGIiTWSQvA', 'name' => 'Aaron and Claire', 'tag' => '한식'],
        ['id' => 'UCKcaQK2v3WsiW-TCgwbs_Mw', 'name' => '쿠킹트리', 'tag' => '케이크'],
        ['id' => 'UCLsooMJoIpl_7uxIBtCICHQ', 'name' => '꿀키', 'tag' => '베이킹'],
        ['id' => 'UCvBtKQaoDhsHkrvtLjSAhyw', 'name' => 'Just One Cookbook', 'tag' => '일식'],
        ['id' => 'UCXkMvXdKVPMdF50MgHqyJtg', 'name' => '백종원', 'tag' => '한식'],
        ['id' => 'UCg-p3lQIqmhh7gHpyaOmOiQ', 'name' => 'Korean Englishman', 'tag' => '문화'],
        ['id' => 'UC4r4GeAILg2KiM51REJ7F7g', 'name' => '도티TV', 'tag' => '게임'],
        ['id' => 'UCzWQYUVCpZqtN93H8RR44Qw', 'name' => 'SMTOWN', 'tag' => 'K-POP'],
        // 먹방
        ['id' => 'UCu4PzMM0TwsxJkMbgOg4Cmw', 'name' => '햄지', 'tag' => '먹방'],
        ['id' => 'UCBsEP4M5aTxKIHfOMGCXYug', 'name' => '쯔양', 'tag' => '먹방'],
        ['id' => 'UCi0TAWEtJmGDFZxbvBQ6Hbg', 'name' => 'Boki', 'tag' => '먹방'],
        ['id' => 'UC8-CZWi9YX3bMi7gEOHcHEg', 'name' => '떵개떵', 'tag' => '먹방'],
        ['id' => 'UCTFjwhP5rIEtGcTo2E41B1g', 'name' => 'Dorothy', 'tag' => '일상'],
        // 문화/생활
        ['id' => 'UC-KHcBFRkKZGtZahIca4tYQ', 'name' => '워크맨', 'tag' => '예능'],
        ['id' => 'UCWqS9YkZGYJp3zXJfT2w9XQ', 'name' => '피식대학', 'tag' => '코미디'],
        ['id' => 'UCNAf1k0yIjyGu3k9BwAg3lg', 'name' => '침착맨', 'tag' => '예능'],
        ['id' => 'UCQGqX5Ndpm4snE0NTjyOJnA', 'name' => 'BIGBANG', 'tag' => 'K-POP'],
        ['id' => 'UCrY87RDPNIpXYnmNkjKoCSw', 'name' => 'BTS Official', 'tag' => 'K-POP'],
        ['id' => 'UCaO6TYtlC8U5ttz62hTrZgg', 'name' => 'TWICE', 'tag' => 'K-POP'],
        ['id' => 'UCNiJNzSkfumLB7bYtXcIEmg', 'name' => 'BLACKPINK', 'tag' => 'K-POP'],
        ['id' => 'UC3IZKseVpdzPSBaWxBxundA', 'name' => 'aespa', 'tag' => 'K-POP'],
        ['id' => 'UCjwmbv6NE4mOh8Z8AaEFDOA', 'name' => 'NewJeans', 'tag' => 'K-POP'],
        ['id' => 'UCNkSPaA96YWX_w5Y47dPaRg', 'name' => 'IVE', 'tag' => 'K-POP'],
        ['id' => 'UCo6AYi7LQNJiHnRfHpKUmHw', 'name' => 'STAYC', 'tag' => 'K-POP'],
        ['id' => 'UC4HRMiQL2Ct7hAzQxcIImrw', 'name' => 'ITZY', 'tag' => 'K-POP'],
        ['id' => 'UCE2CpHmOv1BpKRGLGCUMUhw', 'name' => 'EXO', 'tag' => 'K-POP'],
        // 뷰티/패션
        ['id' => 'UCy4_P5_9zqxIJI1NMJ5MzFA', 'name' => '입짧은햇님', 'tag' => '일상'],
        ['id' => 'UCLkAepWjdylmXSltofFvsYA', 'name' => 'BLACKPINK Beauty', 'tag' => '뷰티'],
        // 스포츠/기타
        ['id' => 'UC8P0wTHCEr0IEdlbGOBiENg', 'name' => 'Son Heungmin', 'tag' => '스포츠'],
        ['id' => 'UCo0GXN9BfkPTSiAFycZfaXw', 'name' => '안정환', 'tag' => '스포츠'],
        ['id' => 'UCRqNBpsBIZqGVSFA8NXGkfw', 'name' => '미국 한인 일상', 'tag' => '미국생활'],
        ['id' => 'UCiT9RITQ9PW6BhXK0y2jaeg', 'name' => 'KoreanInAmerica', 'tag' => '미국생활'],
        ['id' => 'UCBkJo9NTyqGBVRe9kcOQdcg', 'name' => '한인타운VLOG', 'tag' => '미국생활'],
        ['id' => 'UCB6AOmhzZw_jQEEGhexwVSg', 'name' => 'HYBE LABELS', 'tag' => 'K-POP'],
        ['id' => 'UCp7uh7q9lZlJGsGVxvGTb5A', 'name' => 'Studio Choom', 'tag' => 'K-POP'],
        ['id' => 'UC3fn3EVEGbA8WUPYhVzfVSg', 'name' => '런닝맨', 'tag' => '예능'],
        ['id' => 'UCYKbHUdRvnI-1e8U8dIe5ZA', 'name' => '무한도전', 'tag' => '예능'],
    ];

    public function handle()
    {
        $limit  = (int) $this->option('limit');
        $keep   = (int) $this->option('keep');

        // 1) 채널 20개 랜덤 선택
        $selected = collect($this->channels)->shuffle()->take(20)->values();

        $ns = [
            'atom'  => 'http://www.w3.org/2005/Atom',
            'yt'    => 'http://www.youtube.com/xml/schemas/2015',
            'media' => 'http://search.yahoo.com/mrss/',
        ];

        $candidates = [];

        foreach ($selected as $ch) {
            $url = 'https://www.youtube.com/feeds/videos.xml?channel_id=' . $ch['id'];
            try {
                $resp = Http::timeout(8)->withHeaders(['User-Agent' => 'SomeKorean/1.0'])->get($url);
                if (!$resp->ok()) continue;

                $xml = simplexml_load_string($resp->body());
                if (!$xml) continue;
                $xml->registerXPathNamespace('yt',    $ns['yt']);
                $xml->registerXPathNamespace('media', $ns['media']);

                foreach ($xml->entry ?? [] as $entry) {
                    $idNodes = $entry->xpath('yt:videoId');
                    if (empty($idNodes)) continue;
                    $vid = (string) $idNodes[0];

                    $thumbNodes = $entry->xpath('media:group/media:thumbnail');
                    $thumb = !empty($thumbNodes)
                        ? (string) $thumbNodes[0]->attributes()->url
                        : "https://img.youtube.com/vi/{$vid}/mqdefault.jpg";

                    $candidates[] = [
                        'video_id' => $vid,
                        'title'    => (string) ($entry->title ?? ''),
                        'channel'  => $ch['name'],
                        'tag'      => $ch['tag'],
                        'thumb'    => $thumb,
                    ];
                }
                sleep(0) ; // no extra delay needed
            } catch (\Exception $e) {
                $this->warn("Channel {$ch['name']}: " . $e->getMessage());
            }
        }

        // 2) 후보 셔플 후 최대 $limit 개 삽입
        shuffle($candidates);
        $inserted = 0;

        foreach (array_slice($candidates, 0, $limit * 2) as $v) {
            if ($inserted >= $limit) break;

            $shortUrl = 'https://www.youtube.com/shorts/' . $v['video_id'];
            if (DB::table('shorts')->where('url', $shortUrl)->exists()) continue;

            // Skip Chinese-language shorts
            if ($this->isChineseText($v['title'])) {
                continue;
            }

            DB::table('shorts')->insert([
                'user_id'     => 1,
                'url'         => $shortUrl,
                'embed_url'   => 'https://www.youtube.com/embed/' . $v['video_id']
                               . '?autoplay=0&mute=0&controls=1&loop=1&playlist=' . $v['video_id'] . '&rel=0',
                'platform'    => 'youtube',
                'title'       => $v['title'] ?: null,
                'thumbnail'   => $v['thumb'],
                'description' => $v['channel'] . ' · ' . $v['tag'],
                'tags'        => json_encode([$v['tag'], $v['channel'], '한국']),
                'view_count'  => rand(1000, 500000),
                'like_count'  => rand(100, 50000),
                'is_active'   => 1,
                'created_at'  => now(),
                'updated_at'  => now(),
            ]);
            $inserted++;
        }

        // 3) 오래된 YouTube 숏츠 정리: $keep 개 초과분 삭제 (회원 업로드 제외)
        $ytCount = DB::table('shorts')->where('platform', 'youtube')->where('user_id', 1)->count();
        if ($ytCount > $keep) {
            $deleteCount = $ytCount - $keep;
            $oldIds = DB::table('shorts')
                ->where('platform', 'youtube')
                ->where('user_id', 1)
                ->orderBy('created_at', 'asc')   // 가장 오래된 것부터
                ->limit($deleteCount)
                ->pluck('id');
            DB::table('shorts')->whereIn('id', $oldIds)->delete();
            $this->info("Cleaned up {$deleteCount} old YouTube shorts");
        }

        $total = DB::table('shorts')->where('is_active', 1)->count();
        $this->info("✅ Inserted: {$inserted} | Total active: {$total}");
        return 0;
    }

    /**
     * Check if text contains predominantly Chinese characters (not Korean)
     */
    private function isChineseText($text)
    {
        if (empty($text)) return false;

        // Count Chinese characters (CJK Unified Ideographs)
        preg_match_all('/[\x{4E00}-\x{9FFF}]/u', $text, $chineseMatches);
        $chineseCount = count($chineseMatches[0]);

        // Count Korean characters (Hangul)
        preg_match_all('/[\x{AC00}-\x{D7AF}\x{1100}-\x{11FF}\x{3130}-\x{318F}]/u', $text, $koreanMatches);
        $koreanCount = count($koreanMatches[0]);

        // Count total meaningful characters (excluding spaces, numbers, symbols)
        preg_match_all('/[\p{L}]/u', $text, $allLetters);
        $totalLetters = count($allLetters[0]);

        if ($totalLetters === 0) return false;

        // If has Chinese characters but NO Korean, and Chinese > 30% of text
        if ($chineseCount > 0 && $koreanCount === 0 && ($chineseCount / $totalLetters) > 0.3) {
            return true;
        }

        return false;
    }
}
