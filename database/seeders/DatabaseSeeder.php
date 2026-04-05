<?php

namespace Database\Seeders;

use Illuminate\Database\Console\Seeds\WithoutModelEvents;
use Illuminate\Database\Seeder;

class DatabaseSeeder extends Seeder
{
    use WithoutModelEvents;

    public function run(): void
    {
        $this->call([
            UserSeeder::class,
            BoardSeeder::class,
            NewsCategorySeeder::class,
            QaCategorySeeder::class,
            RecipeCategorySeeder::class,
            PostSeeder::class,
            JobSeeder::class,
            MarketSeeder::class,
            RealEstateSeeder::class,
            ClubSeeder::class,
            RecipeSeeder::class,
            GroupBuySeeder::class,
            QaSeeder::class,
            GameSettingSeeder::class,
            SiteSettingSeeder::class,
            MusicSeeder::class,
            CommentSeeder::class,
        ]);
    }
}
