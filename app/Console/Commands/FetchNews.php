<?php

namespace App\Console\Commands;

use App\Models\News;
use App\Models\NewsCategory;
use Illuminate\Console\Command;
use Carbon\Carbon;

/**
 * 미주중앙일보 (koreadaily.com) 4개 섹션 sitemap 에서 최신 기사를 가져온다.
 *
 * 구조:
 * - sitemap.xml → 섹션별 (society/economy/life/sports/hotdeal/allArticles) gz sitemap 목록
 * - 각 섹션 sitemap → news:news 태그 포함, 수만 건 URL
 * - 개별 기사 HTML → article:section2 메타에서 세부 카테고리 추출
 *
 * 옵션:
 *   --per-section=100  섹션당 최소 몇 건 가져올지
 *   --skip-content     본문 재스크래핑 없이 제목/이미지만 저장 (빠른 체크용)
 */
class FetchNews extends Command
{
    protected $signature   = 'news:fetch {--per-section=100} {--skip-content}';
    protected $description = '미주중앙일보 섹션별 최신 뉴스 가져오기';

    private array $sections = [
        // sitemap key => main category name (news_categories 테이블의 대분류와 매칭)
        'society' => '사회',
        'economy' => '경제',
        'life'    => '라이프',
        'sports'  => '연예·스포츠',
    ];

    public function handle(): int
    {
        $perSection = (int) $this->option('per-section');
        $skipContent = (bool) $this->option('skip-content');

        $created = 0;
        $updated = 0;
        $skipped = 0;
        $failed = 0;

        // 대분류 id 캐시
        $mainCategoryIds = [];
        foreach ($this->sections as $parentName) {
            $mainCategoryIds[$parentName] = NewsCategory::where('name', $parentName)->whereNull('parent_id')->value('id');
        }
        // 세부 카테고리 id 캐시 (name -> id)
        $subCategoryIds = NewsCategory::whereNotNull('parent_id')->pluck('id', 'name')->toArray();

        foreach ($this->sections as $sectionKey => $mainCategoryName) {
            $this->info("=== {$mainCategoryName} ({$sectionKey}) ===");
            $sitemapUrl = "https://www.koreadaily.com/sitemap/section/{$sectionKey}.xml.gz";
            $items = $this->loadSitemapItems($sitemapUrl, $perSection);
            $this->info("  sitemap 에서 {$items->count()}건 로드");

            $sectionCreated = 0;
            $sectionSkipped = 0;

            foreach ($items as $item) {
                $link = $item['loc'];
                $title = $item['title'];
                $pubDate = $item['pub_date'];

                if (!$link || !$title) { $failed++; continue; }

                // 중복 체크
                if (News::where('source_url', $link)->exists()) {
                    $sectionSkipped++;
                    $skipped++;
                    continue;
                }

                // 기사 HTML 가져와서 본문 + 이미지 + 서브카테고리 추출
                $html = $skipContent ? '' : $this->fetchHtml($link);
                $content = $html ? $this->extractBody($html, $link) : '';
                $imageUrl = $html ? $this->extractImage($html) : null;
                $subCategory = $html ? $this->extractSubCategory($html) : null;

                // category_id 결정: 서브 카테고리가 news_categories 에 있으면 그걸, 아니면 대분류
                $categoryId = null;
                if ($subCategory && isset($subCategoryIds[$subCategory])) {
                    $categoryId = $subCategoryIds[$subCategory];
                } else {
                    $categoryId = $mainCategoryIds[$mainCategoryName] ?? null;
                }

                try {
                    $publishedAt = $pubDate ? Carbon::parse($pubDate) : now();
                } catch (\Exception $e) {
                    $publishedAt = now();
                }

                News::create([
                    'title'        => $title,
                    'summary'      => mb_substr($content ?: $title, 0, 300),
                    'content'      => $content,
                    'source_url'   => $link,
                    'source'       => '미주중앙일보',
                    'category_id'  => $categoryId,
                    'image_url'    => $imageUrl,
                    'published_at' => $publishedAt,
                ]);
                $sectionCreated++;
                $created++;
            }

            $this->info("  신규 {$sectionCreated}건, 중복 {$sectionSkipped}건");
        }

        $this->info("완료: 신규={$created} 중복={$skipped} 실패={$failed}");
        return self::SUCCESS;
    }

    /**
     * section sitemap (gzip xml) 에서 최신 N건을 로드.
     */
    private function loadSitemapItems(string $url, int $limit): \Illuminate\Support\Collection
    {
        $ch = curl_init($url);
        curl_setopt_array($ch, [
            CURLOPT_RETURNTRANSFER => true,
            CURLOPT_FOLLOWLOCATION => true,
            CURLOPT_SSL_VERIFYPEER => false,
            CURLOPT_SSL_VERIFYHOST => false,
            CURLOPT_TIMEOUT => 30,
            CURLOPT_USERAGENT => 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            CURLOPT_ENCODING => '', // auto-decode gzip
        ]);
        $xmlContent = curl_exec($ch);
        curl_close($ch);

        if (!$xmlContent) return collect();

        $xml = @simplexml_load_string($xmlContent, 'SimpleXMLElement', LIBXML_NOCDATA);
        if (!$xml) return collect();

        $items = [];
        foreach ($xml->url as $url) {
            $namespaces = $url->getNameSpaces(true);
            $loc = (string) $url->loc;
            $lastmod = (string) ($url->lastmod ?? '');
            $title = '';
            $pubDate = '';
            if (isset($namespaces['news'])) {
                $newsNode = $url->children($namespaces['news']);
                if (isset($newsNode->news)) {
                    $title = (string) $newsNode->news->title;
                    $pubDate = (string) $newsNode->news->publication_date;
                }
            }
            if ($loc && $title) {
                $items[] = [
                    'loc' => $loc,
                    'title' => $title,
                    'pub_date' => $pubDate ?: $lastmod,
                ];
            }
        }

        // 최신순 정렬 후 상한
        usort($items, fn($a, $b) => strcmp($b['pub_date'], $a['pub_date']));
        return collect(array_slice($items, 0, $limit));
    }

    private function fetchHtml(string $url): ?string
    {
        $ch = curl_init($url);
        curl_setopt_array($ch, [
            CURLOPT_RETURNTRANSFER => true,
            CURLOPT_FOLLOWLOCATION => true,
            CURLOPT_SSL_VERIFYPEER => false,
            CURLOPT_SSL_VERIFYHOST => false,
            CURLOPT_CONNECTTIMEOUT => 10,
            CURLOPT_TIMEOUT => 15,
            CURLOPT_USERAGENT => 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        ]);
        $html = curl_exec($ch);
        curl_close($ch);
        return $html ?: null;
    }

    /**
     * koreadaily 기사 HTML 에서 본문을 추출. <!--#dev body--> 마커 사용.
     */
    private function extractBody(string $html, string $url): string
    {
        if (!preg_match('/<!--#dev body-->(.*?)<!--\s*태그 영역/s', $html, $m)) {
            return '';
        }
        $body = $m[1];

        // 광고/스크립트 제거
        $body = preg_replace('/<script[^>]*>.*?<\/script>/si', '', $body);
        $body = preg_replace('/<style[^>]*>.*?<\/style>/si', '', $body);
        $body = preg_replace('/<div[^>]*class=["\'][^"\']*(iniframe|addfp|google|ad_|real-inter)[^"\']*["\'][^>]*>.*?<\/div>/si', '', $body);

        // img 태그 보존 (마커 방식)
        $imgs = [];
        $body = preg_replace_callback('/<img[^>]+src=["\']([^"\']+)["\'][^>]*>/i', function ($mm) use (&$imgs) {
            $src = $mm[1];
            if (!str_starts_with($src, 'http')) return '';
            if (preg_match('/(logo|icon|pixel|banner|ad[_-]|ads?\/)/i', $src)) return '';
            $idx = count($imgs);
            $imgs[] = $src;
            return "\n[IMG:{$idx}]\n";
        }, $body);

        $text = strip_tags($body);
        $text = html_entity_decode($text, ENT_QUOTES, 'UTF-8');
        foreach ($imgs as $i => $src) {
            $text = str_replace("[IMG:{$i}]", "\n![뉴스 이미지]({$src})\n", $text);
        }

        $text = preg_replace('/[ \t]+/', ' ', $text);
        $text = preg_replace('/\n\s*\n/', "\n\n", $text);
        $text = trim($text);

        if (mb_strlen($text) > 8000) $text = mb_substr($text, 0, 8000);
        return $text;
    }

    /**
     * 기사 메인 이미지 추출 (og:image 우선, 없으면 본문 첫 이미지)
     */
    private function extractImage(string $html): ?string
    {
        if (preg_match('/<meta[^>]+property=["\']og:image["\'][^>]+content=["\']([^"\']+)["\']/i', $html, $m)) {
            return $m[1];
        }
        if (preg_match('/<meta[^>]+name=["\']twitter:image["\'][^>]+content=["\']([^"\']+)["\']/i', $html, $m)) {
            return $m[1];
        }
        return null;
    }

    /**
     * 기사 HTML 에서 세부 카테고리 추출 (article:section2 메타 우선).
     */
    private function extractSubCategory(string $html): ?string
    {
        if (preg_match('/<meta[^>]+property=[\'"]article:section2[\'"][^>]+content=[\'"]([^\'"]+)[\'"]/i', $html, $m)) {
            return $m[1];
        }
        if (preg_match('/<meta[^>]+property=[\'"]article:section[\'"][^>]+content=[\'"]([^\'"]+)[\'"]/i', $html, $m)) {
            return $m[1];
        }
        return null;
    }
}
