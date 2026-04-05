<?php

namespace Database\Seeders;

use App\Models\QaCategory;
use Illuminate\Database\Seeder;
use Illuminate\Support\Str;

class QaCategorySeeder extends Seeder
{
    public function run(): void
    {
        $categories = [
            '이민/비자'   => 'immigration-visa',
            '법률'        => 'legal',
            '세금/회계'   => 'tax-accounting',
            '부동산'      => 'real-estate',
            '자동차'      => 'automobile',
            '의료/보험'   => 'medical-insurance',
            '교육'        => 'education',
            '취업'        => 'employment',
            '생활정보'    => 'life-info',
            'IT/기술'     => 'it-tech',
            '기타'        => 'etc',
        ];

        $i = 0;
        foreach ($categories as $name => $slug) {
            QaCategory::create([
                'name'       => $name,
                'slug'       => $slug,
                'sort_order' => ($i + 1) * 10,
            ]);
            $i++;
        }

        $this->command->info('QaCategorySeeder: ' . count($categories) . ' categories created');
    }
}
