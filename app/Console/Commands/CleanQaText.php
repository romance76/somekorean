<?php

namespace App\Console\Commands;

use Illuminate\Console\Command;
use App\Models\QaPost;
use App\Models\QaAnswer;

/**
 * Q&A 본문/제목에서 네이버 출처 흔적 정리:
 * - 네이버/naver/지식인 → 어썸코리안/awesomekorean/Q&A
 * - 변호사 프로필 보기/답변 더 보기 등 잔여 링크 텍스트 제거
 * - tistory.com 등 외부 도메인 링크 제거
 * - 원래 질문에 대한 링크 < 클릭 패턴 제거
 * - 빈 #/| 라인 정리
 *
 * 사용:
 *   php artisan qa:clean-text          # 실제 실행
 *   php artisan qa:clean-text --dry    # 변경 카운트만 확인 (저장 안 함)
 */
class CleanQaText extends Command
{
    protected $signature = 'qa:clean-text {--dry : 변경 사항만 카운트하고 저장 안 함}';
    protected $description = 'Q&A 본문/제목에서 네이버 출처/잔여 링크/노이즈 정리';

    /** [pattern, replacement] — 순서대로 적용. 긴 문구 먼저! */
    private array $replacements = [
        // ─── 네이버 지식인 → 어썸코리안 Q&A (가장 긴 문구 먼저)
        ['/네이버\s*지식\s*[인iI]?[nN]?/u',                    '어썸코리안 Q&A'],
        ['/지식\s*[i I][n N]/u',                                'Q&A'],
        ['/지식인/u',                                            'Q&A'],
        // ─── 네이버 도메인
        ['/(?<![a-zA-Z])naver\.com/i',                           'awesomekorean.com'],
        ['/네이버\.?닷컴/u',                                      'awesomekorean.com'],
        // ─── 네이버 단독
        ['/네이버/u',                                            '어썸코리안'],
        // ─── never 단어 (영문)
        ['/(?<![a-zA-Z])naver(?![a-zA-Z])/i',                    'awesomekorean'],
    ];

    /** 제거할 정규식 패턴들 */
    private array $removals = [
        // 변호사 / 답변 / 프로필 등 잔여 링크 텍스트 (대괄호 안)
        '/\[\s*변호사\s+프로필\s+보기\s*\]/u',
        '/\[\s*변호사님의?\s+답변\s+더?\s*보기\s*\]/u',
        '/\[\s*더\s+많은\s+문의\s*사례?\s+보기\s*\]/u',
        '/\[\s*[^\]]*?(?:프로필|답변)\s+(?:더\s*)?보기\s*\]/u',
        // 원래 질문에 대한 링크 < 클릭
        '/원래\s*질문에\s*대한\s*링크\s*[<＜]?\s*클릭\s*하?\s*[기여]?\s*/u',
        // tistory 풀 URL (See More 같은 뒤따라오는 가비지 포함)
        '/https?:\/\/[^\s\)\]]*\.tistory\.com[^\s\)\]]*/i',
        // 맨 도메인 tistory.com
        '/(?<![\/\.a-zA-Z])[a-zA-Z0-9_\-]+\.tistory\.com(?:\/[^\s\)\]]*)?/i',
        // See More + URL 인코딩 가비지 (- %EC... 같은 패턴)
        '/See\s+More\s*-?\s*(?:%[A-Fa-f0-9]{2}){2,}[^\s]*/i',
        // 결과적으로 남은 빈 대괄호 [ ] [ ]
        '/\[\s*\]/u',
    ];

    public function handle(): int
    {
        $dry = (bool) $this->option('dry');

        $stats = [
            'posts_title' => 0,
            'posts_content' => 0,
            'answers_content' => 0,
            'total_replacements' => 0,
        ];

        // ─── Posts: title + content ───
        $this->info('📝 qa_posts 처리...');
        $posts = QaPost::select('id', 'title', 'content')->get();
        $bar = $this->output->createProgressBar($posts->count());
        $bar->start();
        foreach ($posts as $p) {
            $newTitle = $this->cleanText($p->title, $stats);
            $newContent = $this->cleanText($p->content, $stats);
            $changed = false;
            $update = [];
            if ($newTitle !== $p->title) { $update['title'] = $newTitle; $stats['posts_title']++; $changed = true; }
            if ($newContent !== $p->content) { $update['content'] = $newContent; $stats['posts_content']++; $changed = true; }
            if ($changed && !$dry) {
                QaPost::where('id', $p->id)->update($update);
            }
            $bar->advance();
        }
        $bar->finish();
        $this->newLine();

        // ─── Answers: content ───
        $this->info('💬 qa_answers 처리...');
        $answers = QaAnswer::select('id', 'content')->get();
        $bar = $this->output->createProgressBar($answers->count());
        $bar->start();
        foreach ($answers as $a) {
            $newContent = $this->cleanText($a->content, $stats);
            if ($newContent !== $a->content) {
                $stats['answers_content']++;
                if (!$dry) {
                    QaAnswer::where('id', $a->id)->update(['content' => $newContent]);
                }
            }
            $bar->advance();
        }
        $bar->finish();
        $this->newLine(2);

        $this->info($dry ? '🔍 [DRY RUN] 결과' : '✅ 정리 완료');
        $this->table(
            ['항목', '변경된 수'],
            [
                ['질문 제목 (qa_posts.title)',     $stats['posts_title']],
                ['질문 본문 (qa_posts.content)',   $stats['posts_content']],
                ['답변 본문 (qa_answers.content)', $stats['answers_content']],
                ['총 치환/제거 횟수',              $stats['total_replacements']],
            ]
        );

        return 0;
    }

    private function cleanText(?string $text, array &$stats): string
    {
        if ($text === null || $text === '') return $text ?? '';

        $original = $text;

        // 1) 치환
        foreach ($this->replacements as [$pat, $repl]) {
            $text = preg_replace($pat, $repl, $text, -1, $count);
            if ($count > 0) $stats['total_replacements'] += $count;
        }

        // 2) 제거 (빈 문자열로 치환)
        foreach ($this->removals as $pat) {
            $text = preg_replace($pat, '', $text, -1, $count);
            if ($count > 0) $stats['total_replacements'] += $count;
        }

        // 3) 결과 정리
        // 라인이 # 또는 | 또는 공백/대시 만 있는 경우 제거
        $lines = preg_split('/\r?\n/', $text);
        $cleanLines = [];
        foreach ($lines as $line) {
            $stripped = trim($line);
            // 노이즈만 남은 라인 제거: # 만, | 만, < 만, < 클릭 만, 등
            if (preg_match('/^[#\|<>＜＞\-\s]*$/u', $stripped)) {
                continue;
            }
            // 줄 끝의 고립된 # | 정리
            $cleanLines[] = rtrim($line);
        }
        $text = implode("\n", $cleanLines);

        // 4) 연속 빈 줄 압축 (3개 이상 → 2개)
        $text = preg_replace('/\n{3,}/', "\n\n", $text);

        // 5) trim
        $text = trim($text);

        return $text;
    }
}
