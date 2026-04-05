<?php

namespace Database\Seeders;

use App\Models\RecipeCategory;
use App\Models\RecipePost;
use App\Models\User;
use Illuminate\Database\Seeder;

class RecipeSeeder extends Seeder
{
    public function run(): void
    {
        $userIds     = User::pluck('id')->toArray();
        $categoryIds = RecipeCategory::pluck('id', 'name')->toArray();
        if (empty($userIds) || empty($categoryIds)) {
            $this->command->warn('RecipeSeeder: users or categories missing, skipping.');
            return;
        }

        $recipes = [
            // 한식
            ['title' => 'Kimchi Jjigae', 'title_ko' => '김치찌개', 'cat' => '한식', 'diff' => 'easy', 'prep' => 10, 'cook' => 25, 'servings' => 4,
             'ingredients' => ['Aged kimchi 2 cups', 'Pork belly 200g', 'Tofu 1 block', 'Green onion 2 stalks', 'Gochugaru 1 tbsp', 'Garlic 3 cloves', 'Sesame oil 1 tbsp', 'Water 3 cups'],
             'ingredients_ko' => ['묵은지 2컵', '삼겹살 200g', '두부 1모', '대파 2대', '고춧가루 1큰술', '마늘 3쪽', '참기름 1큰술', '물 3컵'],
             'steps' => ['Slice pork belly into bite pieces', 'Sauté pork in sesame oil until browned', 'Add kimchi and stir-fry 3 min', 'Add water and bring to boil', 'Add tofu and simmer 15 min', 'Garnish with green onion'],
             'steps_ko' => ['삼겹살을 한입 크기로 썬다', '참기름에 삼겹살을 볶는다', '김치를 넣고 3분 볶는다', '물을 넣고 끓인다', '두부를 넣고 15분 끓인다', '대파를 올려 마무리한다']],

            ['title' => 'Bulgogi', 'title_ko' => '불고기', 'cat' => '한식', 'diff' => 'easy', 'prep' => 30, 'cook' => 15, 'servings' => 4,
             'ingredients' => ['Beef sirloin 500g', 'Soy sauce 4 tbsp', 'Sugar 2 tbsp', 'Sesame oil 2 tbsp', 'Garlic 4 cloves', 'Pear 1/2', 'Onion 1', 'Green onion 3'],
             'ingredients_ko' => ['소고기(등심) 500g', '간장 4큰술', '설탕 2큰술', '참기름 2큰술', '마늘 4쪽', '배 반개', '양파 1개', '대파 3대'],
             'steps' => ['Thinly slice beef', 'Mix marinade: soy sauce, sugar, sesame oil, minced garlic, grated pear', 'Marinate beef for 30 min', 'Cook on high heat until caramelized', 'Serve with rice and lettuce'],
             'steps_ko' => ['소고기를 얇게 썬다', '양념장을 만든다: 간장, 설탕, 참기름, 다진마늘, 배즙', '소고기를 30분 재운다', '강불에서 볶는다', '밥과 상추에 곁들여 낸다']],

            ['title' => 'Japchae', 'title_ko' => '잡채', 'cat' => '한식', 'diff' => 'medium', 'prep' => 20, 'cook' => 20, 'servings' => 6,
             'ingredients' => ['Sweet potato noodles 300g', 'Beef 150g', 'Spinach 200g', 'Carrot 1', 'Mushrooms 5', 'Soy sauce 3 tbsp', 'Sugar 1.5 tbsp', 'Sesame oil 2 tbsp'],
             'ingredients_ko' => ['당면 300g', '소고기 150g', '시금치 200g', '당근 1개', '표고버섯 5개', '간장 3큰술', '설탕 1.5큰술', '참기름 2큰술'],
             'steps' => ['Boil noodles and drain', 'Stir-fry beef', 'Stir-fry vegetables separately', 'Mix everything with sauce', 'Garnish with sesame seeds'],
             'steps_ko' => ['당면을 삶아 건진다', '소고기를 볶는다', '야채를 각각 볶는다', '모두 섞어 양념한다', '참깨를 뿌려 완성']],

            ['title' => 'Bibimbap', 'title_ko' => '비빔밥', 'cat' => '한식', 'diff' => 'medium', 'prep' => 30, 'cook' => 15, 'servings' => 4,
             'ingredients' => ['Rice 4 cups', 'Beef 200g', 'Spinach 150g', 'Bean sprouts 150g', 'Carrot 1', 'Zucchini 1', 'Egg 4', 'Gochujang 4 tbsp'],
             'ingredients_ko' => ['밥 4공기', '소고기 200g', '시금치 150g', '콩나물 150g', '당근 1개', '애호박 1개', '달걀 4개', '고추장 4큰술'],
             'steps' => ['Prepare all toppings separately', 'Blanch spinach and bean sprouts', 'Sauté carrot and zucchini', 'Season beef and cook', 'Fry eggs sunny-side up', 'Assemble on rice, top with gochujang'],
             'steps_ko' => ['모든 재료를 준비한다', '시금치와 콩나물을 데친다', '당근과 애호박을 볶는다', '소고기를 양념해서 볶는다', '계란 프라이를 한다', '밥 위에 올리고 고추장을 곁들인다']],

            ['title' => 'Tteokbokki', 'title_ko' => '떡볶이', 'cat' => '분식', 'diff' => 'easy', 'prep' => 5, 'cook' => 20, 'servings' => 3,
             'ingredients' => ['Rice cakes 500g', 'Fish cakes 3 sheets', 'Gochujang 3 tbsp', 'Gochugaru 1 tbsp', 'Sugar 1.5 tbsp', 'Soy sauce 1 tbsp', 'Green onion 2', 'Water 2 cups'],
             'ingredients_ko' => ['떡 500g', '어묵 3장', '고추장 3큰술', '고춧가루 1큰술', '설탕 1.5큰술', '간장 1큰술', '대파 2대', '물 2컵'],
             'steps' => ['Soak rice cakes if frozen', 'Boil water and add gochujang and gochugaru', 'Add rice cakes and fish cakes', 'Simmer until sauce thickens', 'Top with green onion'],
             'steps_ko' => ['떡이 얼었으면 불린다', '물에 고추장, 고춧가루를 풀어 끓인다', '떡과 어묵을 넣는다', '양념이 걸쭉해질 때까지 끓인다', '대파를 올려 완성']],

            ['title' => 'Doenjang Jjigae', 'title_ko' => '된장찌개', 'cat' => '국/찌개', 'diff' => 'easy', 'prep' => 10, 'cook' => 20, 'servings' => 4,
             'ingredients' => ['Doenjang 3 tbsp', 'Tofu 1 block', 'Zucchini 1/2', 'Potato 1', 'Mushrooms 3', 'Green chili 2', 'Garlic 2 cloves', 'Anchovy broth 3 cups'],
             'ingredients_ko' => ['된장 3큰술', '두부 1모', '애호박 반개', '감자 1개', '버섯 3개', '풋고추 2개', '마늘 2쪽', '멸치육수 3컵'],
             'steps' => ['Prepare anchovy broth', 'Dissolve doenjang in broth', 'Add potato first, cook 5 min', 'Add zucchini, mushrooms, tofu', 'Simmer 10 min, add green chili'],
             'steps_ko' => ['멸치육수를 낸다', '된장을 육수에 풀어준다', '감자를 먼저 넣고 5분 끓인다', '애호박, 버섯, 두부를 넣는다', '10분 끓이고 풋고추를 넣어 마무리']],

            ['title' => 'Sundubu Jjigae', 'title_ko' => '순두부찌개', 'cat' => '국/찌개', 'diff' => 'easy', 'prep' => 10, 'cook' => 15, 'servings' => 2,
             'ingredients' => ['Soft tofu 1 pack', 'Pork 100g', 'Kimchi 1/2 cup', 'Egg 1', 'Green onion 1', 'Gochugaru 1 tbsp', 'Garlic 2 cloves', 'Sesame oil 1 tbsp'],
             'ingredients_ko' => ['순두부 1팩', '돼지고기 100g', '김치 반컵', '달걀 1개', '대파 1대', '고춧가루 1큰술', '마늘 2쪽', '참기름 1큰술'],
             'steps' => ['Sauté pork in sesame oil', 'Add kimchi and gochugaru', 'Add water and bring to boil', 'Slide in soft tofu', 'Crack egg on top before serving'],
             'steps_ko' => ['참기름에 돼지고기를 볶는다', '김치와 고춧가루를 넣는다', '물을 넣고 끓인다', '순두부를 넣는다', '달걀을 올려 완성']],

            ['title' => 'Kimchi Fried Rice', 'title_ko' => '김치볶음밥', 'cat' => '한식', 'diff' => 'easy', 'prep' => 5, 'cook' => 10, 'servings' => 2,
             'ingredients' => ['Cooked rice 2 cups', 'Kimchi 1 cup', 'Spam or pork 100g', 'Egg 2', 'Sesame oil 1 tbsp', 'Gochujang 1 tbsp', 'Green onion 1'],
             'ingredients_ko' => ['밥 2공기', '김치 1컵', '스팸 또는 돼지고기 100g', '달걀 2개', '참기름 1큰술', '고추장 1큰술', '대파 1대'],
             'steps' => ['Dice kimchi and meat', 'Stir-fry meat first', 'Add kimchi and rice', 'Season with gochujang', 'Top with fried egg'],
             'steps_ko' => ['김치와 고기를 썬다', '고기를 먼저 볶는다', '김치와 밥을 넣고 볶는다', '고추장으로 간을 한다', '계란 프라이를 올린다']],

            ['title' => 'Korean Fried Chicken', 'title_ko' => '양념치킨', 'cat' => '한식', 'diff' => 'hard', 'prep' => 30, 'cook' => 30, 'servings' => 4,
             'ingredients' => ['Chicken wings 1kg', 'Cornstarch 1 cup', 'Gochujang 3 tbsp', 'Soy sauce 2 tbsp', 'Honey 3 tbsp', 'Garlic 4 cloves', 'Ginger 1 tbsp', 'Oil for frying'],
             'ingredients_ko' => ['닭 날개 1kg', '전분 1컵', '고추장 3큰술', '간장 2큰술', '꿀 3큰술', '마늘 4쪽', '생강 1큰술', '튀김기름'],
             'steps' => ['Season chicken and coat in cornstarch', 'Double-fry chicken until crispy', 'Make sauce: gochujang, soy, honey, garlic', 'Toss chicken in sauce', 'Garnish with sesame and peanuts'],
             'steps_ko' => ['닭에 전분을 입힌다', '두 번 튀겨 바삭하게 한다', '양념장을 만든다', '닭을 양념에 버무린다', '참깨와 땅콩을 뿌려 완성']],

            ['title' => 'Jajangmyeon', 'title_ko' => '짜장면', 'cat' => '중식', 'diff' => 'medium', 'prep' => 15, 'cook' => 20, 'servings' => 4,
             'ingredients' => ['Fresh noodles 400g', 'Black bean paste 4 tbsp', 'Pork belly 200g', 'Zucchini 1', 'Potato 1', 'Onion 2', 'Cabbage 2 leaves', 'Cornstarch slurry'],
             'ingredients_ko' => ['생면 400g', '춘장 4큰술', '삼겹살 200g', '애호박 1개', '감자 1개', '양파 2개', '양배추 2장', '전분물'],
             'steps' => ['Dice all vegetables', 'Fry black bean paste in oil', 'Add pork and cook', 'Add vegetables and water', 'Thicken with cornstarch', 'Serve over boiled noodles'],
             'steps_ko' => ['야채를 모두 깍둑 썬다', '춘장을 기름에 볶는다', '돼지고기를 넣고 볶는다', '야채와 물을 넣고 끓인다', '전분물로 농도를 맞춘다', '삶은 면 위에 올린다']],

            ['title' => 'Salmon Sashimi Bowl', 'title_ko' => '연어 덮밥', 'cat' => '일식', 'diff' => 'easy', 'prep' => 15, 'cook' => 0, 'servings' => 2,
             'ingredients' => ['Sushi-grade salmon 300g', 'Sushi rice 2 cups', 'Avocado 1', 'Soy sauce 2 tbsp', 'Wasabi', 'Pickled ginger', 'Sesame seeds', 'Seaweed flakes'],
             'ingredients_ko' => ['회용 연어 300g', '초밥용 밥 2공기', '아보카도 1개', '간장 2큰술', '와사비', '초생강', '참깨', '김가루'],
             'steps' => ['Prepare sushi rice', 'Slice salmon thinly', 'Slice avocado', 'Arrange on rice', 'Drizzle soy sauce, top with wasabi'],
             'steps_ko' => ['초밥용 밥을 짓는다', '연어를 얇게 썬다', '아보카도를 썬다', '밥 위에 예쁘게 올린다', '간장을 뿌리고 와사비를 곁들인다']],

            ['title' => 'Cream Pasta', 'title_ko' => '크림 파스타', 'cat' => '면/파스타', 'diff' => 'easy', 'prep' => 10, 'cook' => 15, 'servings' => 2,
             'ingredients' => ['Fettuccine 200g', 'Heavy cream 1 cup', 'Bacon 4 slices', 'Mushrooms 5', 'Garlic 3 cloves', 'Parmesan 1/2 cup', 'Salt and pepper', 'Olive oil 1 tbsp'],
             'ingredients_ko' => ['페투치네 200g', '생크림 1컵', '베이컨 4줄', '양송이 5개', '마늘 3쪽', '파마산치즈 반컵', '소금, 후추', '올리브오일 1큰술'],
             'steps' => ['Boil pasta al dente', 'Cook bacon until crispy', 'Sauté garlic and mushrooms', 'Add cream and simmer', 'Toss pasta and parmesan'],
             'steps_ko' => ['파스타를 알덴테로 삶는다', '베이컨을 바삭하게 굽는다', '마늘과 버섯을 볶는다', '생크림을 넣고 끓인다', '파스타와 치즈를 넣고 섞는다']],

            ['title' => 'Steak with Garlic Butter', 'title_ko' => '갈릭버터 스테이크', 'cat' => '양식', 'diff' => 'medium', 'prep' => 10, 'cook' => 15, 'servings' => 2,
             'ingredients' => ['Ribeye steak 2', 'Butter 3 tbsp', 'Garlic 4 cloves', 'Rosemary 2 sprigs', 'Salt and pepper', 'Olive oil 2 tbsp'],
             'ingredients_ko' => ['립아이 스테이크 2장', '버터 3큰술', '마늘 4쪽', '로즈마리 2줄기', '소금, 후추', '올리브오일 2큰술'],
             'steps' => ['Season steak with salt and pepper', 'Sear on high heat 3 min each side', 'Add butter, garlic, rosemary', 'Baste with melted butter', 'Rest 5 min before slicing'],
             'steps_ko' => ['스테이크에 소금, 후추를 뿌린다', '강불에서 양면 3분씩 굽는다', '버터, 마늘, 로즈마리를 넣는다', '녹은 버터를 끼얹어 준다', '5분 레스팅 후 썬다']],

            ['title' => 'Kongnamul Bap', 'title_ko' => '콩나물밥', 'cat' => '한식', 'diff' => 'easy', 'prep' => 10, 'cook' => 25, 'servings' => 4,
             'ingredients' => ['Rice 3 cups', 'Bean sprouts 300g', 'Ground beef 150g', 'Soy sauce 3 tbsp', 'Green onion 2', 'Sesame oil 1 tbsp', 'Gochugaru 1 tsp'],
             'ingredients_ko' => ['쌀 3컵', '콩나물 300g', '소고기 다진 것 150g', '간장 3큰술', '대파 2대', '참기름 1큰술', '고춧가루 1작은술'],
             'steps' => ['Wash rice and place in pot', 'Layer bean sprouts on top', 'Add seasoned beef', 'Cook rice normally', 'Make sauce and mix before eating'],
             'steps_ko' => ['쌀을 씻어 솥에 넣는다', '콩나물을 위에 올린다', '양념한 소고기를 넣는다', '밥을 평소대로 짓는다', '양념장을 만들어 비벼 먹는다']],

            ['title' => 'Gyeran Mari', 'title_ko' => '계란말이', 'cat' => '반찬', 'diff' => 'easy', 'prep' => 5, 'cook' => 10, 'servings' => 4,
             'ingredients' => ['Eggs 5', 'Green onion 2', 'Carrot 1/4', 'Salt pinch', 'Oil 1 tbsp'],
             'ingredients_ko' => ['달걀 5개', '대파 2대', '당근 1/4개', '소금 약간', '기름 1큰술'],
             'steps' => ['Beat eggs', 'Mince vegetables and mix in', 'Oil pan on medium heat', 'Pour egg mixture and roll', 'Slice and serve'],
             'steps_ko' => ['달걀을 풀어준다', '야채를 다져서 섞는다', '팬에 기름을 두른다', '계란물을 부어 말아준다', '한입 크기로 썬다']],

            ['title' => 'Hotteok', 'title_ko' => '호떡', 'cat' => '분식', 'diff' => 'medium', 'prep' => 60, 'cook' => 15, 'servings' => 8,
             'ingredients' => ['Flour 2 cups', 'Warm water 3/4 cup', 'Yeast 1 tsp', 'Sugar 1 tbsp', 'Brown sugar 1/2 cup', 'Cinnamon 1 tsp', 'Chopped nuts 1/4 cup', 'Oil'],
             'ingredients_ko' => ['밀가루 2컵', '따뜻한 물 3/4컵', '이스트 1작은술', '설탕 1큰술', '흑설탕 반컵', '계피 1작은술', '견과류 1/4컵', '기름'],
             'steps' => ['Make dough and let rise 1 hour', 'Make filling: brown sugar, cinnamon, nuts', 'Divide dough and fill', 'Flatten and pan-fry until golden', 'Serve warm'],
             'steps_ko' => ['반죽을 만들어 1시간 발효한다', '소를 만든다: 흑설탕, 계피, 견과류', '반죽을 나누어 소를 넣는다', '납작하게 눌러 노릇하게 굽는다', '따뜻할 때 먹는다']],

            ['title' => 'Banana Bread', 'title_ko' => '바나나 브레드', 'cat' => '디저트/베이킹', 'diff' => 'easy', 'prep' => 15, 'cook' => 60, 'servings' => 8,
             'ingredients' => ['Ripe bananas 3', 'Flour 1.5 cups', 'Sugar 3/4 cup', 'Butter 1/3 cup', 'Egg 1', 'Baking soda 1 tsp', 'Vanilla 1 tsp', 'Salt pinch'],
             'ingredients_ko' => ['잘 익은 바나나 3개', '밀가루 1.5컵', '설탕 3/4컵', '버터 1/3컵', '달걀 1개', '베이킹소다 1작은술', '바닐라 1작은술', '소금 약간'],
             'steps' => ['Mash bananas', 'Mix wet ingredients', 'Combine dry ingredients separately', 'Fold together gently', 'Bake at 350F for 60 min'],
             'steps_ko' => ['바나나를 으깬다', '습식 재료를 섞는다', '건식 재료를 따로 섞는다', '가볍게 합친다', '350도에서 60분 굽는다']],

            ['title' => 'Iced Americano', 'title_ko' => '아이스 아메리카노', 'cat' => '음료', 'diff' => 'easy', 'prep' => 5, 'cook' => 0, 'servings' => 1,
             'ingredients' => ['Espresso 2 shots', 'Cold water 1 cup', 'Ice'],
             'ingredients_ko' => ['에스프레소 2샷', '찬물 1컵', '얼음'],
             'steps' => ['Pull espresso shots', 'Fill glass with ice', 'Add cold water', 'Pour espresso over'],
             'steps_ko' => ['에스프레소를 추출한다', '컵에 얼음을 채운다', '찬물을 넣는다', '에스프레소를 붓는다']],

            ['title' => 'Soy Milk Noodles', 'title_ko' => '콩국수', 'cat' => '면/파스타', 'diff' => 'medium', 'prep' => 240, 'cook' => 15, 'servings' => 4,
             'ingredients' => ['Dried soybeans 2 cups', 'Noodles 400g', 'Salt', 'Sesame seeds', 'Cucumber', 'Tomato', 'Ice'],
             'ingredients_ko' => ['마른 콩 2컵', '소면 400g', '소금', '참깨', '오이', '토마토', '얼음'],
             'steps' => ['Soak soybeans overnight', 'Boil and blend with water', 'Strain through mesh', 'Boil noodles and rinse cold', 'Pour cold soy milk over noodles'],
             'steps_ko' => ['콩을 하룻밤 불린다', '삶아서 물과 함께 간다', '체에 거른다', '소면을 삶아 찬물에 헹군다', '차가운 콩국물을 부어 낸다']],

            ['title' => 'Hobak Jeon', 'title_ko' => '호박전', 'cat' => '반찬', 'diff' => 'easy', 'prep' => 10, 'cook' => 15, 'servings' => 4,
             'ingredients' => ['Zucchini 2', 'Eggs 2', 'Flour 1/2 cup', 'Salt', 'Oil'],
             'ingredients_ko' => ['애호박 2개', '달걀 2개', '밀가루 반컵', '소금', '기름'],
             'steps' => ['Slice zucchini into rounds', 'Season with salt', 'Coat in flour then egg', 'Pan-fry until golden', 'Serve with soy dipping sauce'],
             'steps_ko' => ['애호박을 동그랗게 썬다', '소금으로 간한다', '밀가루, 달걀 옷을 입힌다', '노릇하게 부친다', '간장 양념장에 곁들인다']],
        ];

        // Additional generic recipes to fill up to 300
        $genericRecipes = [
            ['title' => 'Chicken Breast Salad', 'title_ko' => '닭가슴살 샐러드', 'cat' => '건강식', 'diff' => 'easy', 'prep' => 15, 'cook' => 10, 'servings' => 2],
            ['title' => 'Ramyeon', 'title_ko' => '라면 끓이기', 'cat' => '간편식', 'diff' => 'easy', 'prep' => 2, 'cook' => 5, 'servings' => 1],
            ['title' => 'Egg Drop Soup', 'title_ko' => '계란국', 'cat' => '국/찌개', 'diff' => 'easy', 'prep' => 5, 'cook' => 10, 'servings' => 4],
            ['title' => 'Stir-fried Pork', 'title_ko' => '제육볶음', 'cat' => '한식', 'diff' => 'medium', 'prep' => 15, 'cook' => 15, 'servings' => 4],
            ['title' => 'Cucumber Salad', 'title_ko' => '오이무침', 'cat' => '반찬', 'diff' => 'easy', 'prep' => 10, 'cook' => 0, 'servings' => 4],
            ['title' => 'Miso Soup', 'title_ko' => '미소시루', 'cat' => '일식', 'diff' => 'easy', 'prep' => 5, 'cook' => 10, 'servings' => 4],
            ['title' => 'Garlic Bread', 'title_ko' => '마늘빵', 'cat' => '디저트/베이킹', 'diff' => 'easy', 'prep' => 10, 'cook' => 10, 'servings' => 6],
            ['title' => 'Tonkatsu', 'title_ko' => '돈까스', 'cat' => '일식', 'diff' => 'medium', 'prep' => 15, 'cook' => 15, 'servings' => 2],
            ['title' => 'Sweet Potato Latte', 'title_ko' => '고구마 라떼', 'cat' => '음료', 'diff' => 'easy', 'prep' => 10, 'cook' => 5, 'servings' => 2],
            ['title' => 'Kimbap', 'title_ko' => '김밥', 'cat' => '한식', 'diff' => 'medium', 'prep' => 30, 'cook' => 20, 'servings' => 4],
            ['title' => 'Tangsuyuk', 'title_ko' => '탕수육', 'cat' => '중식', 'diff' => 'hard', 'prep' => 20, 'cook' => 30, 'servings' => 4],
            ['title' => 'Chicken Curry', 'title_ko' => '치킨 카레', 'cat' => '양식', 'diff' => 'easy', 'prep' => 15, 'cook' => 30, 'servings' => 6],
            ['title' => 'Sikhye', 'title_ko' => '식혜', 'cat' => '음료', 'diff' => 'hard', 'prep' => 30, 'cook' => 240, 'servings' => 10],
            ['title' => 'Gamja Jorim', 'title_ko' => '감자조림', 'cat' => '반찬', 'diff' => 'easy', 'prep' => 10, 'cook' => 20, 'servings' => 4],
            ['title' => 'French Toast', 'title_ko' => '프렌치 토스트', 'cat' => '간편식', 'diff' => 'easy', 'prep' => 5, 'cook' => 10, 'servings' => 2],
            ['title' => 'Mapo Tofu', 'title_ko' => '마파두부', 'cat' => '중식', 'diff' => 'medium', 'prep' => 10, 'cook' => 15, 'servings' => 4],
            ['title' => 'Greek Salad', 'title_ko' => '그릭 샐러드', 'cat' => '건강식', 'diff' => 'easy', 'prep' => 10, 'cook' => 0, 'servings' => 2],
            ['title' => 'Cheese Tteokbokki', 'title_ko' => '치즈 떡볶이', 'cat' => '분식', 'diff' => 'easy', 'prep' => 5, 'cook' => 15, 'servings' => 2],
            ['title' => 'Pajeon', 'title_ko' => '파전', 'cat' => '한식', 'diff' => 'easy', 'prep' => 10, 'cook' => 15, 'servings' => 4],
            ['title' => 'Chicken Katsu Don', 'title_ko' => '치킨가츠동', 'cat' => '일식', 'diff' => 'medium', 'prep' => 10, 'cook' => 20, 'servings' => 2],
        ];

        // Default ingredients/steps for generics
        $defaultIngredients = ['Main ingredient', 'Seasoning', 'Oil', 'Salt', 'Pepper'];
        $defaultIngredientsKo = ['주재료', '양념', '기름', '소금', '후추'];
        $defaultSteps = ['Prepare ingredients', 'Cook main ingredient', 'Season to taste', 'Plate and serve'];
        $defaultStepsKo = ['재료를 준비한다', '주재료를 조리한다', '간을 맞춘다', '그릇에 담아 낸다'];

        $now  = now();
        $rows = [];

        // Insert detailed recipes
        foreach ($recipes as $r) {
            $catId = $categoryIds[$r['cat']] ?? null;
            $rows[] = [
                'user_id'        => $userIds[array_rand($userIds)],
                'title'          => $r['title'],
                'title_ko'       => $r['title_ko'],
                'content'        => $r['title_ko'] . ' 레시피입니다. 간단하고 맛있게 만들 수 있어요!',
                'content_ko'     => $r['title_ko'] . ' 레시피입니다. 간단하고 맛있게 만들 수 있어요!',
                'ingredients'    => json_encode($r['ingredients']),
                'ingredients_ko' => json_encode($r['ingredients_ko']),
                'steps'          => json_encode($r['steps']),
                'steps_ko'       => json_encode($r['steps_ko']),
                'category_id'    => $catId,
                'images'         => null,
                'servings'       => $r['servings'],
                'prep_time'      => $r['prep'],
                'cook_time'      => $r['cook'],
                'difficulty'     => $r['diff'],
                'view_count'     => rand(10, 500),
                'like_count'     => rand(0, 50),
                'comment_count'  => rand(0, 20),
                'created_at'     => $now->copy()->subDays(rand(0, 90))->subHours(rand(0, 23)),
                'updated_at'     => $now,
            ];
        }

        // Fill remaining to reach 300
        $remaining = 300 - count($rows);
        for ($i = 0; $i < $remaining; $i++) {
            $base = $i < count($genericRecipes) ? $genericRecipes[$i] : $genericRecipes[$i % count($genericRecipes)];
            $catId = $categoryIds[$base['cat']] ?? null;
            $suffix = $i >= count($genericRecipes) ? ' #' . ($i + 1) : '';

            $rows[] = [
                'user_id'        => $userIds[array_rand($userIds)],
                'title'          => $base['title'] . $suffix,
                'title_ko'       => $base['title_ko'] . $suffix,
                'content'        => $base['title_ko'] . ' 만드는 법을 소개합니다. 쉽고 빠르게 만들 수 있어요.',
                'content_ko'     => $base['title_ko'] . ' 만드는 법을 소개합니다. 쉽고 빠르게 만들 수 있어요.',
                'ingredients'    => json_encode($defaultIngredients),
                'ingredients_ko' => json_encode($defaultIngredientsKo),
                'steps'          => json_encode($defaultSteps),
                'steps_ko'       => json_encode($defaultStepsKo),
                'category_id'    => $catId,
                'images'         => null,
                'servings'       => $base['servings'],
                'prep_time'      => $base['prep'],
                'cook_time'      => $base['cook'],
                'difficulty'     => $base['diff'],
                'view_count'     => rand(10, 300),
                'like_count'     => rand(0, 30),
                'comment_count'  => rand(0, 15),
                'created_at'     => $now->copy()->subDays(rand(0, 90))->subHours(rand(0, 23)),
                'updated_at'     => $now,
            ];
        }

        foreach (array_chunk($rows, 50) as $chunk) {
            RecipePost::insert($chunk);
        }

        $this->command->info('RecipeSeeder: ' . count($rows) . ' recipes created');
    }
}
