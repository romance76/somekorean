<?php

namespace Database\Seeders;

use App\Models\MusicCategory;
use App\Models\MusicTrack;
use Illuminate\Database\Seeder;

class MusicSeeder extends Seeder
{
    public function run(): void
    {
        $categories = [
            '발라드' => [
                'slug'   => 'ballad',
                'tracks' => [
                    ['title' => '사랑했지만',            'artist' => '김광석',     'youtube_id' => 'sUDcxYyQBDo', 'duration' => 280],
                    ['title' => '거리에서',              'artist' => '성시경',     'youtube_id' => 'HREFz4ygXhg', 'duration' => 260],
                    ['title' => '사랑 그 한마디',        'artist' => '김종국',     'youtube_id' => 'z3h0VKKwqZk', 'duration' => 250],
                    ['title' => '첫눈처럼 너에게 가겠다','artist' => '에일리',     'youtube_id' => 'BYhqWFOxRDQ', 'duration' => 240],
                    ['title' => '여행',                  'artist' => '볼빨간사춘기','youtube_id' => 'xRbPAVnqtcs', 'duration' => 230],
                    ['title' => '봄날',                  'artist' => 'BTS',        'youtube_id' => 'xEeFrLSkMm8', 'duration' => 275],
                    ['title' => '너의 모든 순간',        'artist' => '성시경',     'youtube_id' => 'jyqjm9WJKPU', 'duration' => 285],
                    ['title' => '비가 오는 날엔',        'artist' => '비스트',     'youtube_id' => 'xBGnIhPGr2E', 'duration' => 255],
                ],
            ],
            '트로트' => [
                'slug'   => 'trot',
                'tracks' => [
                    ['title' => '사랑의 배터리',       'artist' => '홍진영',      'youtube_id' => 'wNxT3FKaNpI', 'duration' => 220],
                    ['title' => '트로트 메들리',       'artist' => '송가인',      'youtube_id' => 'wfmB4TMmfHU', 'duration' => 300],
                    ['title' => '잠이 오질 않네요',    'artist' => '장윤정',      'youtube_id' => 'Wv2O8V_O0wk', 'duration' => 240],
                    ['title' => '꽃길',                'artist' => '임영웅',      'youtube_id' => 'FnR28kUb06M', 'duration' => 250],
                    ['title' => '보라빛 엽서',         'artist' => '임영웅',      'youtube_id' => 'KGnw59CXHm0', 'duration' => 270],
                    ['title' => '어메이징 그레이스',    'artist' => '송가인',      'youtube_id' => 'HI_SHGM-Cj4', 'duration' => 230],
                    ['title' => '내 나이가 어때서',     'artist' => '오승근',      'youtube_id' => 'nNF1CvDzTZk', 'duration' => 210],
                ],
            ],
            'K-POP' => [
                'slug'   => 'kpop',
                'tracks' => [
                    ['title' => 'Dynamite',           'artist' => 'BTS',          'youtube_id' => 'gdZLi9oWNZg', 'duration' => 220],
                    ['title' => 'How You Like That',  'artist' => 'BLACKPINK',    'youtube_id' => 'ioNng23DkIM', 'duration' => 195],
                    ['title' => 'Next Level',         'artist' => 'aespa',        'youtube_id' => '4TWR90KJl84', 'duration' => 230],
                    ['title' => 'ANTIFRAGILE',        'artist' => 'LE SSERAFIM',  'youtube_id' => 'pyf8cbqyfPs', 'duration' => 195],
                    ['title' => 'Super Shy',          'artist' => 'NewJeans',     'youtube_id' => 'ArmDp-zijuc', 'duration' => 182],
                    ['title' => 'GODS',               'artist' => 'NewJeans',     'youtube_id' => 'C3GouGa0noM', 'duration' => 198],
                    ['title' => 'Kitsch',             'artist' => 'IVE',          'youtube_id' => 'PbBNNlmPNBM', 'duration' => 190],
                    ['title' => 'UNFORGIVEN',         'artist' => 'LE SSERAFIM',  'youtube_id' => 'CSWQ1pOID00', 'duration' => 196],
                    ['title' => 'Butter',             'artist' => 'BTS',          'youtube_id' => 'WMweEpGlu_U', 'duration' => 165],
                    ['title' => 'Shut Down',          'artist' => 'BLACKPINK',    'youtube_id' => 'POe9SOEKotk', 'duration' => 178],
                ],
            ],
            '힙합' => [
                'slug'   => 'hiphop',
                'tracks' => [
                    ['title' => 'STILL LIFE',         'artist' => 'BIGBANG',      'youtube_id' => 'BWCWsRtGLMc', 'duration' => 255],
                    ['title' => '어떻게 이별까지 사랑하겠어', 'artist' => 'AKMU',  'youtube_id' => 'OPWMfKtxfhU', 'duration' => 265],
                    ['title' => '무릎',               'artist' => 'IU',           'youtube_id' => 'PUB4vUMqHDk', 'duration' => 245],
                    ['title' => 'GANADARA',           'artist' => 'Jay Park',     'youtube_id' => 'TS4vBCxBKWI', 'duration' => 220],
                    ['title' => 'Daechwita',          'artist' => 'Agust D',      'youtube_id' => 'qGjAWJ2zWWI', 'duration' => 240],
                    ['title' => '아무노래',            'artist' => '지코',         'youtube_id' => 'UuV2BmJ1p_I', 'duration' => 210],
                ],
            ],
            'R&B' => [
                'slug'   => 'rnb',
                'tracks' => [
                    ['title' => 'Celebrity',          'artist' => 'IU',           'youtube_id' => '0-q1KafFCLU', 'duration' => 195],
                    ['title' => 'Palette',            'artist' => 'IU',           'youtube_id' => 'd9IxdwEFk1c', 'duration' => 210],
                    ['title' => 'eight',              'artist' => 'IU (feat. SUGA)', 'youtube_id' => 'TgOu00Mf3kI', 'duration' => 185],
                    ['title' => 'WAYO',               'artist' => 'LeeHi',        'youtube_id' => '6Xqb1jHjxqQ', 'duration' => 230],
                    ['title' => 'Love poem',          'artist' => 'IU',           'youtube_id' => 'OcVmaIlHZ1o', 'duration' => 260],
                    ['title' => 'HOLO',               'artist' => 'LeeHi',        'youtube_id' => 'VdeK_VsG9U0', 'duration' => 220],
                ],
            ],
            '재즈' => [
                'slug'   => 'jazz',
                'tracks' => [
                    ['title' => 'Autumn Leaves (Jazz)', 'artist' => '나윤선',      'youtube_id' => 'ZJ6n2qNGTbg', 'duration' => 300],
                    ['title' => 'My Funny Valentine',    'artist' => '나윤선',      'youtube_id' => 'RuQ-Dlpp5YE', 'duration' => 320],
                    ['title' => 'Fly Me to the Moon',    'artist' => '조윤성',      'youtube_id' => 'ZEcqHA7dbwM', 'duration' => 280],
                    ['title' => 'Night and Day',         'artist' => '김현철',      'youtube_id' => '9GCYbP_yX80', 'duration' => 290],
                    ['title' => 'Summertime',            'artist' => '나윤선',      'youtube_id' => 'zTKWtAqiLhM', 'duration' => 310],
                ],
            ],
            '클래식' => [
                'slug'   => 'classic',
                'tracks' => [
                    ['title' => 'Canon in D',            'artist' => '임동혁',      'youtube_id' => 'Ptk_1Dc2iPY', 'duration' => 360],
                    ['title' => 'Moonlight Sonata',      'artist' => '손열음',      'youtube_id' => '4Tr0otuiQuU', 'duration' => 420],
                    ['title' => 'Spring Waltz',          'artist' => '조성진',      'youtube_id' => 'SRiJd1jxAso', 'duration' => 380],
                    ['title' => 'Clair de Lune',         'artist' => '조성진',      'youtube_id' => 'WNcsUNKlAKw', 'duration' => 320],
                    ['title' => 'Ballade No.1',          'artist' => '조성진',      'youtube_id' => 'VEBuSS4e7RI', 'duration' => 540],
                ],
            ],
            'OST' => [
                'slug'   => 'ost',
                'tracks' => [
                    ['title' => 'Stay With Me',         'artist' => '찬열, 펀치',   'youtube_id' => 'pcKR0LPwoYs', 'duration' => 240],
                    ['title' => 'Beautiful',            'artist' => '크러쉬',       'youtube_id' => 'x2XX3cNW4K0', 'duration' => 230],
                    ['title' => 'My Love',              'artist' => '이하이',       'youtube_id' => 'C-F7AkZ4FNE', 'duration' => 260],
                    ['title' => 'All Of My Life',       'artist' => '박원',         'youtube_id' => '4mB7UH4k5GI', 'duration' => 250],
                    ['title' => 'I Love You Boy',       'artist' => '수지',         'youtube_id' => '8ATu_U_gfpA', 'duration' => 220],
                    ['title' => 'It\'s You',            'artist' => '헨리',         'youtube_id' => 'yH2zcel3PFE', 'duration' => 235],
                    ['title' => 'Your Name',            'artist' => 'RADWIMPS',     'youtube_id' => 'LBc1jFjKDvM', 'duration' => 270],
                    ['title' => 'Start Over',           'artist' => '갈렌',         'youtube_id' => '8FNNTFYtGBI', 'duration' => 245],
                ],
            ],
        ];

        $catOrder = 0;
        foreach ($categories as $name => $data) {
            $catOrder += 10;
            $category = MusicCategory::create([
                'name'       => $name,
                'slug'       => $data['slug'],
                'image'      => null,
                'sort_order' => $catOrder,
            ]);

            $trackOrder = 0;
            foreach ($data['tracks'] as $track) {
                $trackOrder += 10;
                MusicTrack::create([
                    'category_id' => $category->id,
                    'title'       => $track['title'],
                    'artist'      => $track['artist'],
                    'youtube_url' => 'https://www.youtube.com/watch?v=' . $track['youtube_id'],
                    'youtube_id'  => $track['youtube_id'],
                    'duration'    => $track['duration'],
                    'sort_order'  => $trackOrder,
                ]);
            }
        }

        $totalTracks = MusicTrack::count();
        $this->command->info("MusicSeeder: " . count($categories) . " categories, {$totalTracks} tracks created");
    }
}
