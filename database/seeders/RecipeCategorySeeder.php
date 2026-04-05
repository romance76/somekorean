<?php

namespace Database\Seeders;

use App\Models\RecipeCategory;
use Illuminate\Database\Seeder;

class RecipeCategorySeeder extends Seeder
{
    public function run(): void
    {
        $categories = [
            '한식'          => 'korean',
            '중식'          => 'chinese',
            '일식'          => 'japanese',
            '양식'          => 'western',
            '분식'          => 'snack',
            '디저트/베이킹' => 'dessert',
            '반찬'          => 'side-dish',
            '국/찌개'       => 'soup-stew',
            '면/파스타'     => 'noodle-pasta',
            '음료'          => 'drink',
            '건강식'        => 'healthy',
            '간편식'        => 'quick-meal',
        ];

        $i = 0;
        foreach ($categories as $name => $slug) {
            RecipeCategory::create([
                'name'       => $name,
                'slug'       => $slug,
                'sort_order' => ($i + 1) * 10,
            ]);
            $i++;
        }

        $this->command->info('RecipeCategorySeeder: ' . count($categories) . ' categories created');
    }
}
