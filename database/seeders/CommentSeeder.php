<?php

namespace Database\Seeders;

use App\Models\Comment;
use App\Models\Post;
use App\Models\RecipePost;
use App\Models\QaPost;
use App\Models\MarketItem;
use App\Models\GroupBuy;
use App\Models\User;
use Illuminate\Database\Seeder;

class CommentSeeder extends Seeder
{
    public function run(): void
    {
        $userIds = User::pluck('id')->toArray();
        if (empty($userIds)) { $this->command->warn('CommentSeeder: no users, skipping.'); return; }

        $commentTexts = [
            '좋은 정보 감사합니다!',
            '도움이 많이 되었어요.',
            '저도 같은 경험이 있어요. 공감합니다.',
            '이 정보 진짜 유용하네요. 공유 감사합니다!',
            '감사합니다. 덕분에 도움 받았습니다.',
            '오~ 이거 몰랐었는데 좋은 정보네요!',
            '잘 읽었습니다. 다음 글도 기대할게요.',
            '자세한 설명 감사합니다.',
            '저도 비슷한 상황인데 도움이 됐어요.',
            '항상 좋은 글 올려주셔서 감사합니다!',
            '아 이거 정말 궁금했는데! 감사합니다.',
            '추가로 하나 더 여쭤봐도 될까요?',
            '좋은 글이에요. 북마크 해뒀습니다.',
            '제 친구한테도 공유할게요!',
            '이 방법 한번 해봐야겠어요.',
            '오래전부터 궁금했는데 드디어 답을 찾았네요.',
            '맞아요, 저도 이렇게 했더니 잘 됐어요.',
            '좋은 경험 공유 감사합니다!',
            '이 지역에 이런 곳이 있었군요.',
            '가격이 정말 괜찮네요!',
            '상태가 좋아 보여요. 관심 있습니다.',
            '혹시 네고 가능할까요?',
            '이거 아직 있나요?',
            '위치가 어디예요?',
            '직거래 가능하신가요?',
            '만드는 법이 정말 자세하네요! 감사합니다.',
            '이 레시피 해봤는데 맛있었어요!',
            '저도 이렇게 만들어 봐야겠어요.',
            '재료가 쉽게 구할 수 있는 거라 좋네요.',
            '맛있어 보여요! 꼭 만들어 볼게요.',
            '아이들도 좋아하나요?',
            '매운 거 싫어하는데 고춧가루 안 넣어도 되나요?',
            '사진 보니까 침이 고이네요 ㅎㅎ',
            '저도 공구 참여하고 싶어요!',
            '가격이 진짜 좋네요. 몇 명 모였나요?',
            '언제까지 참여 가능한가요?',
            '이거 정말 좋은 딜이네요!',
            '좋은 답변 감사합니다. 많이 도움 되었어요.',
            '저도 이 방법으로 해결했습니다.',
            '추가 정보가 있으면 공유 부탁드려요.',
        ];

        $replyTexts = [
            '답변 감사합니다!',
            '네, 맞아요. 저도 그렇게 생각합니다.',
            '추가 정보 감사합니다.',
            '아 그렇군요! 다시 한번 알아볼게요.',
            '도움이 되셨다니 다행이에요.',
            '추가 질문 남겨주시면 답변 드릴게요.',
            '맞습니다. 제 경험도 비슷해요.',
            '네, 네고 가능합니다. 쪽지 주세요.',
            '아직 있습니다! 연락 주세요.',
            '저도 같은 생각이에요 ㅎㅎ',
        ];

        $now  = now();
        $rows = [];

        // Comments on Posts
        $postIds = Post::pluck('id')->toArray();
        foreach ($postIds as $postId) {
            $numComments = rand(0, 5);
            for ($c = 0; $c < $numComments; $c++) {
                $rows[] = [
                    'commentable_type' => 'App\\Models\\Post',
                    'commentable_id'   => $postId,
                    'user_id'          => $userIds[array_rand($userIds)],
                    'parent_id'        => null,
                    'content'          => $commentTexts[array_rand($commentTexts)],
                    'like_count'       => rand(0, 10),
                    'is_hidden'        => false,
                    'created_at'       => $now->copy()->subDays(rand(0, 60))->subHours(rand(0, 23)),
                    'updated_at'       => $now,
                ];
            }
        }

        // Comments on Recipes
        $recipeIds = RecipePost::pluck('id')->toArray();
        foreach ($recipeIds as $recipeId) {
            $numComments = rand(0, 4);
            for ($c = 0; $c < $numComments; $c++) {
                $rows[] = [
                    'commentable_type' => 'App\\Models\\RecipePost',
                    'commentable_id'   => $recipeId,
                    'user_id'          => $userIds[array_rand($userIds)],
                    'parent_id'        => null,
                    'content'          => $commentTexts[array_rand($commentTexts)],
                    'like_count'       => rand(0, 8),
                    'is_hidden'        => false,
                    'created_at'       => $now->copy()->subDays(rand(0, 60))->subHours(rand(0, 23)),
                    'updated_at'       => $now,
                ];
            }
        }

        // Comments on Market Items
        $marketIds = MarketItem::pluck('id')->toArray();
        foreach ($marketIds as $marketId) {
            $numComments = rand(0, 3);
            for ($c = 0; $c < $numComments; $c++) {
                $rows[] = [
                    'commentable_type' => 'App\\Models\\MarketItem',
                    'commentable_id'   => $marketId,
                    'user_id'          => $userIds[array_rand($userIds)],
                    'parent_id'        => null,
                    'content'          => $commentTexts[array_rand($commentTexts)],
                    'like_count'       => rand(0, 5),
                    'is_hidden'        => false,
                    'created_at'       => $now->copy()->subDays(rand(0, 45))->subHours(rand(0, 23)),
                    'updated_at'       => $now,
                ];
            }
        }

        // Comments on Group Buys
        $groupBuyIds = GroupBuy::pluck('id')->toArray();
        foreach ($groupBuyIds as $gbId) {
            $numComments = rand(0, 3);
            for ($c = 0; $c < $numComments; $c++) {
                $rows[] = [
                    'commentable_type' => 'App\\Models\\GroupBuy',
                    'commentable_id'   => $gbId,
                    'user_id'          => $userIds[array_rand($userIds)],
                    'parent_id'        => null,
                    'content'          => $commentTexts[array_rand($commentTexts)],
                    'like_count'       => rand(0, 5),
                    'is_hidden'        => false,
                    'created_at'       => $now->copy()->subDays(rand(0, 30))->subHours(rand(0, 23)),
                    'updated_at'       => $now,
                ];
            }
        }

        // Insert all comments
        foreach (array_chunk($rows, 100) as $chunk) {
            Comment::insert($chunk);
        }

        // Add some replies to existing comments
        $parentComments = Comment::inRandomOrder()->limit(200)->pluck('id')->toArray();
        $replyRows = [];
        foreach ($parentComments as $parentId) {
            $parent = Comment::find($parentId);
            if (!$parent) continue;

            if (rand(0, 100) > 50) {
                $replyRows[] = [
                    'commentable_type' => $parent->commentable_type,
                    'commentable_id'   => $parent->commentable_id,
                    'user_id'          => $userIds[array_rand($userIds)],
                    'parent_id'        => $parentId,
                    'content'          => $replyTexts[array_rand($replyTexts)],
                    'like_count'       => rand(0, 5),
                    'is_hidden'        => false,
                    'created_at'       => $parent->created_at->copy()->addHours(rand(1, 48)),
                    'updated_at'       => $now,
                ];
            }
        }

        foreach (array_chunk($replyRows, 100) as $chunk) {
            Comment::insert($chunk);
        }

        $totalComments = Comment::count();
        $this->command->info("CommentSeeder: {$totalComments} comments and replies created");
    }
}
