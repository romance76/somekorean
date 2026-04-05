import paramiko, sys, base64
sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1)
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('68.183.60.70', username='root', password='EhdRh0817wodl', timeout=15)

def ssh(cmd, timeout=120):
    _, out, err = c.exec_command(cmd, timeout=timeout)
    o = out.read().decode('utf-8', errors='replace').strip()
    e = err.read().decode('utf-8', errors='replace').strip()
    return o + (('\nERR:'+e) if e else '')

def write_file(path, content):
    encoded = base64.b64encode(content.encode('utf-8')).decode('ascii')
    chunks = [encoded[i:i+3000] for i in range(0, len(encoded), 3000)]
    ssh('> /tmp/_wf.b64')
    for chunk in chunks:
        ssh("echo -n '{}' >> /tmp/_wf.b64".format(chunk))
    return ssh('base64 -d /tmp/_wf.b64 > {} && rm /tmp/_wf.b64 && echo OK'.format(path))

# ── 1. RecipeController - add uploadImage + update store ──────────────────────
print("=== 1. Updating RecipeController ===")
controller = r'''<?php
namespace App\Http\Controllers\API;
use App\Http\Controllers\Controller;
use App\Models\RecipeCategory;
use App\Models\RecipePost;
use App\Models\RecipeComment;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Auth;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Facades\Storage;

class RecipeController extends Controller {
    public function categories() {
        return response()->json(RecipeCategory::where('is_active', true)->orderBy('sort_order')->get());
    }

    public function index(Request $request) {
        $query = RecipePost::with('user:id,nickname,username,avatar', 'category:id,name,key,icon')
            ->where('is_hidden', false)
            ->where('source', 'user');

        if ($request->sort === 'popular') {
            $query->orderByDesc('like_count');
        } elseif ($request->sort === 'views') {
            $query->orderByDesc('view_count');
        } else {
            $query->orderByDesc('created_at');
        }

        if ($request->category) $query->whereHas('category', fn($q) => $q->where('key', $request->category));
        if ($request->difficulty) $query->where('difficulty', $request->difficulty);
        if ($request->search) {
            $s = $request->search;
            $query->where(function($q) use ($s) {
                $q->where('title', 'like', "%$s%")
                  ->orWhere('intro', 'like', "%$s%")
                  ->orWhereJsonContains('tags', $s);
            });
        }

        $perPage = $request->per_page ? (int)$request->per_page : 20;
        return response()->json($query->paginate($perPage));
    }

    public function show($id) {
        $recipe = RecipePost::with(['user:id,nickname,username,avatar', 'category:id,name,key,icon',
            'comments' => fn($q) => $q->with('user:id,nickname,username,avatar')->latest()->limit(20),
        ])->findOrFail($id);
        $recipe->increment('view_count');
        $isLiked = Auth::check() ? DB::table('content_likes')->where('user_id', Auth::id())->where('likeable_type', 'recipe')->where('likeable_id', $id)->exists() : false;
        $isBookmarked = Auth::check() ? DB::table('content_likes')->where('user_id', Auth::id())->where('likeable_type', 'recipe_bookmark')->where('likeable_id', $id)->exists() : false;
        $related = RecipePost::where('category_id', $recipe->category_id)
            ->where('id', '!=', $id)
            ->where('is_hidden', false)
            ->where('source', 'user')
            ->inRandomOrder()->limit(6)
            ->get(['id','title','image_url','difficulty','cook_time','like_count','view_count','category_id']);
        $avgRating = DB::table('recipe_comments')
            ->where('recipe_id', $id)->where('is_hidden', false)->whereNotNull('rating')->avg('rating');
        return response()->json(array_merge($recipe->toArray(), [
            'is_liked' => $isLiked, 'is_bookmarked' => $isBookmarked,
            'related' => $related,
            'avg_rating' => $avgRating ? round($avgRating, 1) : null,
            'comment_count' => $recipe->comments->count(),
        ]));
    }

    public function uploadImage(Request $request) {
        $request->validate(['image' => 'required|image|mimes:jpeg,png,jpg,gif,webp|max:5120']);
        $path = $request->file('image')->store('recipes', 'public');
        return response()->json(['url' => asset('storage/' . $path)]);
    }

    public function store(Request $request) {
        $request->validate([
            'title'       => 'required|string|max:200',
            'category_id' => 'required|exists:recipe_categories,id',
            'ingredients' => 'nullable|array',
            'steps'       => 'nullable|array',
            'tips'        => 'nullable|array',
            'tags'        => 'nullable|array',
        ]);

        $recipe = RecipePost::create([
            'user_id'     => Auth::id(),
            'title'       => $request->title,
            'intro'       => $request->intro,
            'category_id' => $request->category_id,
            'difficulty'  => $request->difficulty,
            'cook_time'   => $request->cook_time,
            'calories'    => $request->calories,
            'servings'    => $request->servings ?? 2,
            'ingredients' => $request->ingredients ?? [],
            'steps'       => $request->steps ?? [],
            'tips'        => $request->tips ?? [],
            'tags'        => $request->tags ?? [],
            'image_url'   => $request->image_url,
            'source'      => 'user',
        ]);
        return response()->json($recipe->load('user:id,nickname,avatar', 'category:id,name,key,icon'), 201);
    }

    public function update(Request $request, $id) {
        $recipe = RecipePost::where('id', $id)->where('user_id', Auth::id())->firstOrFail();
        $recipe->update($request->only(['title','intro','category_id','difficulty','cook_time','calories','servings','ingredients','steps','tips','tags','image_url']));
        return response()->json($recipe);
    }

    public function destroy($id) {
        $recipe = RecipePost::where('id', $id)->where('user_id', Auth::id())->firstOrFail();
        $recipe->delete();
        return response()->json(['message' => '삭제되었습니다.']);
    }

    public function like($id) {
        RecipePost::findOrFail($id);
        $userId = Auth::id();
        $existing = DB::table('content_likes')->where('user_id', $userId)->where('likeable_type', 'recipe')->where('likeable_id', $id)->first();
        if ($existing) {
            DB::table('content_likes')->where('id', $existing->id)->delete();
            RecipePost::where('id', $id)->decrement('like_count');
        } else {
            DB::table('content_likes')->insert(['user_id' => $userId, 'likeable_type' => 'recipe', 'likeable_id' => $id, 'created_at' => now()]);
            RecipePost::where('id', $id)->increment('like_count');
        }
        $count = DB::table('content_likes')->where('likeable_type', 'recipe')->where('likeable_id', $id)->count();
        return response()->json(['liked' => !$existing, 'like_count' => $count]);
    }

    public function bookmark($id) {
        RecipePost::findOrFail($id);
        $userId = Auth::id();
        $existing = DB::table('content_likes')->where('user_id', $userId)->where('likeable_type', 'recipe_bookmark')->where('likeable_id', $id)->first();
        if ($existing) {
            DB::table('content_likes')->where('id', $existing->id)->delete();
            RecipePost::where('id', $id)->decrement('bookmark_count');
        } else {
            DB::table('content_likes')->insert(['user_id' => $userId, 'likeable_type' => 'recipe_bookmark', 'likeable_id' => $id, 'created_at' => now()]);
            RecipePost::where('id', $id)->increment('bookmark_count');
        }
        return response()->json(['bookmarked' => !$existing]);
    }

    public function comment(Request $request, $id) {
        RecipePost::findOrFail($id);
        $request->validate(['content' => 'required|string|max:1000', 'rating' => 'nullable|integer|min:1|max:5']);
        $comment = RecipeComment::create(['recipe_id' => $id, 'user_id' => Auth::id(), 'content' => $request->content, 'rating' => $request->rating]);
        return response()->json(['message' => '댓글 등록', 'comment' => $comment->load('user:id,nickname,username,avatar')], 201);
    }

    public function popular() {
        return response()->json(RecipePost::where('is_hidden', false)->where('source','user')->orderByDesc('like_count')->limit(10)->get(['id','title','image_url','difficulty','cook_time','like_count']));
    }

    public function myRecipes(Request $request) {
        $recipes = RecipePost::where('user_id', Auth::id())
            ->orderByDesc('created_at')
            ->paginate(20);
        return response()->json($recipes);
    }
}
'''
print(write_file('/var/www/somekorean/app/Http/Controllers/API/RecipeController.php', controller))

# ── 2. Add new API routes ──────────────────────────────────────────────────────
print("\n=== 2. Updating API routes ===")
raw = ssh('base64 /var/www/somekorean/routes/api.php')
api = base64.b64decode(raw).decode('utf-8')

old_recipe_routes = "    Route::post('recipes',                  [RecipeController::class, 'store']);\n    Route::post('recipes/{id}/like',        [RecipeController::class, 'like']);\n    Route::post('recipes/{id}/bookmark',    [RecipeController::class, 'bookmark']);\n    Route::post('recipes/{id}/comments',    [RecipeController::class, 'comment']);"

new_recipe_routes = "    Route::post('recipes/image',            [RecipeController::class, 'uploadImage']);\n    Route::post('recipes',                  [RecipeController::class, 'store']);\n    Route::put('recipes/{id}',              [RecipeController::class, 'update']);\n    Route::delete('recipes/{id}',           [RecipeController::class, 'destroy']);\n    Route::post('recipes/{id}/like',        [RecipeController::class, 'like']);\n    Route::post('recipes/{id}/bookmark',    [RecipeController::class, 'bookmark']);\n    Route::post('recipes/{id}/comments',    [RecipeController::class, 'comment']);\n    Route::get('recipes/my',                [RecipeController::class, 'myRecipes']);"

if old_recipe_routes in api:
    api = api.replace(old_recipe_routes, new_recipe_routes)
    print("OK routes updated")
else:
    print("WARN: exact match not found")
print(write_file('/var/www/somekorean/routes/api.php', api))

# ── 3. RecipeCreate.vue ────────────────────────────────────────────────────────
print("\n=== 3. Writing RecipeCreate.vue ===")
recipe_create = '''<template>
  <div class="min-h-screen bg-gray-50 pb-20">
    <div class="max-w-2xl mx-auto px-4 pt-4">

      <!-- 헤더 -->
      <div class="flex items-center gap-3 mb-5">
        <button @click="$router.back()" class="p-2 rounded-xl bg-white border text-gray-500 hover:bg-gray-50">
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"/></svg>
        </button>
        <div>
          <h1 class="text-xl font-black text-gray-800">레시피 올리기</h1>
          <p class="text-xs text-gray-400">나만의 요리 레시피를 공유해보세요</p>
        </div>
      </div>

      <!-- Step bar -->
      <div class="flex gap-1.5 mb-2">
        <div v-for="s in 4" :key="s" @click="if(s < step) step=s"
          :class="['flex-1 h-1.5 rounded-full transition', s <= step ? 'bg-orange-500' : 'bg-gray-200']"></div>
      </div>
      <p class="text-xs text-center text-gray-400 mb-5">
        {{ ['기본 정보', '재료', '조리 순서', '마무리'][step-1] }} {{ step }}/4
      </p>

      <!-- ── STEP 1: 기본 정보 ── -->
      <div v-if="step === 1" class="space-y-4">

        <!-- 대표 사진 -->
        <div class="bg-white rounded-2xl shadow-sm p-4">
          <p class="text-sm font-semibold text-gray-700 mb-3">대표 사진</p>
          <div v-if="!form.image_url"
            class="w-full h-48 border-2 border-dashed border-gray-200 rounded-xl flex flex-col items-center justify-center gap-2 cursor-pointer hover:border-orange-400 transition relative"
            @click="$refs.imgInput.click()">
            <div v-if="uploadingImg" class="absolute inset-0 bg-white/80 rounded-xl flex items-center justify-center">
              <div class="animate-spin w-8 h-8 border-4 border-orange-500 border-t-transparent rounded-full"></div>
            </div>
            <div class="text-4xl">📸</div>
            <p class="text-sm text-gray-400">클릭하여 사진 업로드</p>
            <p class="text-xs text-gray-300">JPG, PNG, WEBP (최대 5MB)</p>
          </div>
          <div v-else class="relative">
            <img :src="form.image_url" class="w-full h-48 object-cover rounded-xl"/>
            <button @click="form.image_url=''" class="absolute top-2 right-2 bg-black/50 text-white rounded-full w-8 h-8 flex items-center justify-center text-sm hover:bg-black/70">✕</button>
          </div>
          <input ref="imgInput" type="file" accept="image/*" class="hidden" @change="uploadImage"/>
        </div>

        <div class="bg-white rounded-2xl shadow-sm p-4 space-y-4">
          <!-- 제목 -->
          <div>
            <label class="block text-sm font-semibold text-gray-700 mb-1.5">
              요리 이름 <span class="text-red-500">*</span>
            </label>
            <input v-model="form.title" type="text" placeholder="예: 김치찌개, 불고기 덮밥..." maxlength="100"
              class="w-full border border-gray-200 rounded-xl px-4 py-3 text-sm focus:outline-none focus:border-orange-400"/>
          </div>

          <!-- 카테고리 -->
          <div>
            <label class="block text-sm font-semibold text-gray-700 mb-2">
              카테고리 <span class="text-red-500">*</span>
            </label>
            <div class="flex flex-wrap gap-2">
              <button v-for="cat in categories" :key="cat.id"
                @click="form.category_id = cat.id"
                :class="['px-3 py-1.5 rounded-full text-sm border transition', form.category_id === cat.id
                  ? 'bg-orange-500 text-white border-orange-500'
                  : 'bg-white text-gray-600 border-gray-200 hover:border-orange-300']">
                {{ cat.icon }} {{ cat.name }}
              </button>
            </div>
          </div>

          <!-- 소개 -->
          <div>
            <label class="block text-sm font-semibold text-gray-700 mb-1.5">간단 소개</label>
            <textarea v-model="form.intro" rows="3" maxlength="300"
              placeholder="이 요리에 대해 간단히 소개해주세요..."
              class="w-full border border-gray-200 rounded-xl px-4 py-3 text-sm focus:outline-none focus:border-orange-400 resize-none"></textarea>
          </div>
        </div>

        <!-- 기본 정보 -->
        <div class="bg-white rounded-2xl shadow-sm p-4">
          <p class="text-sm font-semibold text-gray-700 mb-3">기본 정보</p>
          <div class="grid grid-cols-3 gap-3">
            <div>
              <label class="block text-xs text-gray-500 mb-1">난이도</label>
              <select v-model="form.difficulty" class="w-full border border-gray-200 rounded-xl px-2 py-2.5 text-sm focus:outline-none focus:border-orange-400">
                <option value="">선택</option>
                <option value="쉬움">😊 쉬움</option>
                <option value="보통">😐 보통</option>
                <option value="어려움">😤 어려움</option>
              </select>
            </div>
            <div>
              <label class="block text-xs text-gray-500 mb-1">조리 시간</label>
              <select v-model="form.cook_time" class="w-full border border-gray-200 rounded-xl px-2 py-2.5 text-sm focus:outline-none focus:border-orange-400">
                <option value="">선택</option>
                <option value="10분 이내">10분 이내</option>
                <option value="15분">15분</option>
                <option value="30분">30분</option>
                <option value="45분">45분</option>
                <option value="1시간">1시간</option>
                <option value="1시간 이상">1시간+</option>
              </select>
            </div>
            <div>
              <label class="block text-xs text-gray-500 mb-1">인분</label>
              <select v-model="form.servings" class="w-full border border-gray-200 rounded-xl px-2 py-2.5 text-sm focus:outline-none focus:border-orange-400">
                <option :value="1">1인분</option>
                <option :value="2">2인분</option>
                <option :value="3">3인분</option>
                <option :value="4">4인분</option>
                <option :value="6">6인분</option>
                <option :value="8">8인분+</option>
              </select>
            </div>
          </div>
        </div>
      </div>

      <!-- ── STEP 2: 재료 ── -->
      <div v-if="step === 2" class="space-y-4">
        <div class="bg-white rounded-2xl shadow-sm p-4">
          <div class="flex items-center justify-between mb-3">
            <p class="text-sm font-semibold text-gray-700">재료 목록</p>
            <span class="text-xs text-gray-400">{{ form.ingredients.length }}개</span>
          </div>
          <div class="space-y-2 mb-3">
            <div v-for="(ing, i) in form.ingredients" :key="i" class="flex gap-2 items-center">
              <input v-model="ing.name" type="text" placeholder="재료명" maxlength="50"
                class="flex-1 border border-gray-200 rounded-xl px-3 py-2.5 text-sm focus:outline-none focus:border-orange-400"/>
              <input v-model="ing.amount" type="text" placeholder="양 (예: 1컵)" maxlength="30"
                class="w-28 border border-gray-200 rounded-xl px-3 py-2.5 text-sm focus:outline-none focus:border-orange-400"/>
              <button @click="form.ingredients.splice(i,1)" class="text-gray-300 hover:text-red-400 text-xl leading-none flex-shrink-0 pb-0.5">×</button>
            </div>
          </div>
          <button @click="form.ingredients.push({name:'',amount:''})"
            class="w-full border-2 border-dashed border-gray-200 rounded-xl py-2.5 text-sm text-gray-400 hover:border-orange-400 hover:text-orange-500 transition">
            + 재료 추가
          </button>
        </div>

        <!-- 빠른 추가 -->
        <div class="bg-orange-50 rounded-2xl p-4 border border-orange-100">
          <p class="text-xs font-semibold text-orange-600 mb-2">자주 쓰는 재료 빠른 추가</p>
          <div class="flex flex-wrap gap-2">
            <button v-for="item in quickIngredients" :key="item"
              @click="form.ingredients.push({name:item, amount:''})"
              class="px-2.5 py-1 bg-white border border-orange-200 rounded-full text-xs text-orange-700 hover:bg-orange-100 transition">
              + {{ item }}
            </button>
          </div>
        </div>
      </div>

      <!-- ── STEP 3: 조리 순서 ── -->
      <div v-if="step === 3" class="space-y-4">
        <div class="bg-white rounded-2xl shadow-sm p-4">
          <div class="flex items-center justify-between mb-3">
            <p class="text-sm font-semibold text-gray-700">조리 순서</p>
            <span class="text-xs text-gray-400">{{ form.steps.length }}단계</span>
          </div>
          <div class="space-y-3 mb-3">
            <div v-for="(st, i) in form.steps" :key="i" class="flex gap-3">
              <div class="flex-shrink-0 w-7 h-7 bg-orange-500 text-white rounded-full flex items-center justify-center text-xs font-bold mt-2.5">{{ i+1 }}</div>
              <div class="flex-1">
                <textarea v-model="st.text" rows="2" :placeholder="(i+1) + '번째 순서를 입력하세요'" maxlength="400"
                  class="w-full border border-gray-200 rounded-xl px-3 py-2 text-sm focus:outline-none focus:border-orange-400 resize-none"></textarea>
              </div>
              <button @click="form.steps.splice(i,1)" class="text-gray-300 hover:text-red-400 text-xl leading-none flex-shrink-0 mt-2.5">×</button>
            </div>
          </div>
          <button @click="form.steps.push({text:''})"
            class="w-full border-2 border-dashed border-gray-200 rounded-xl py-2.5 text-sm text-gray-400 hover:border-orange-400 hover:text-orange-500 transition">
            + 단계 추가
          </button>
        </div>
      </div>

      <!-- ── STEP 4: 마무리 ── -->
      <div v-if="step === 4" class="space-y-4">
        <!-- 태그 -->
        <div class="bg-white rounded-2xl shadow-sm p-4">
          <p class="text-sm font-semibold text-gray-700 mb-2">태그</p>
          <div class="flex gap-2 mb-2 flex-wrap">
            <span v-for="(tag, i) in form.tags" :key="i"
              class="flex items-center gap-1 bg-orange-100 text-orange-700 rounded-full px-3 py-1 text-sm">
              #{{ tag }}
              <button @click="form.tags.splice(i,1)" class="hover:text-red-500 ml-0.5">×</button>
            </span>
          </div>
          <div class="flex gap-2">
            <input v-model="tagInput" type="text" placeholder="태그 입력 후 엔터 (예: 한식, 간단요리)"
              @keyup.enter="addTag" maxlength="20"
              class="flex-1 border border-gray-200 rounded-xl px-3 py-2 text-sm focus:outline-none focus:border-orange-400"/>
            <button @click="addTag" class="bg-orange-100 text-orange-600 px-4 py-2 rounded-xl text-sm font-medium hover:bg-orange-200 transition">추가</button>
          </div>
        </div>

        <!-- 팁 -->
        <div class="bg-white rounded-2xl shadow-sm p-4">
          <p class="text-sm font-semibold text-gray-700 mb-2">요리 팁 (선택)</p>
          <div class="space-y-2 mb-2">
            <div v-for="(tip, i) in form.tips" :key="i" class="flex gap-2">
              <input v-model="form.tips[i]" type="text" placeholder="예: 고추장은 청양고추장을 쓰면 더 맛있어요" maxlength="200"
                class="flex-1 border border-gray-200 rounded-xl px-3 py-2 text-sm focus:outline-none focus:border-orange-400"/>
              <button @click="form.tips.splice(i,1)" class="text-gray-300 hover:text-red-400 text-xl">×</button>
            </div>
          </div>
          <button @click="form.tips.push('')"
            class="w-full border-2 border-dashed border-gray-200 rounded-xl py-2.5 text-sm text-gray-400 hover:border-orange-400 hover:text-orange-500 transition">
            + 팁 추가
          </button>
        </div>

        <!-- 미리보기 -->
        <div class="bg-gradient-to-br from-orange-50 to-amber-50 rounded-2xl p-4 border border-orange-100">
          <p class="text-sm font-bold text-gray-700 mb-3">게시물 미리보기</p>
          <div class="flex gap-3 bg-white rounded-xl p-3">
            <div class="w-20 h-20 bg-gray-100 rounded-xl overflow-hidden flex-shrink-0">
              <img v-if="form.image_url" :src="form.image_url" class="w-full h-full object-cover"/>
              <div v-else class="w-full h-full flex items-center justify-center text-3xl">🍳</div>
            </div>
            <div class="flex-1 min-w-0">
              <p class="font-bold text-gray-800 truncate">{{ form.title || '제목 없음' }}</p>
              <p class="text-xs text-gray-400 mt-0.5">{{ categoryName }}</p>
              <div class="flex gap-1.5 mt-2 flex-wrap">
                <span v-if="form.difficulty" class="text-xs bg-gray-100 rounded-full px-2 py-0.5">{{ form.difficulty }}</span>
                <span v-if="form.cook_time" class="text-xs bg-gray-100 rounded-full px-2 py-0.5">{{ form.cook_time }}</span>
                <span v-if="form.servings" class="text-xs bg-gray-100 rounded-full px-2 py-0.5">{{ form.servings }}인분</span>
              </div>
              <p class="text-xs text-gray-400 mt-1">재료 {{ form.ingredients.filter(i=>i.name).length }}가지 · {{ form.steps.filter(s=>s.text).length }}단계</p>
            </div>
          </div>
        </div>
      </div>

      <!-- 에러 -->
      <div v-if="error" class="mt-4 bg-red-50 border border-red-200 rounded-xl px-4 py-3 text-sm text-red-600">
        {{ error }}
      </div>

      <!-- 버튼 -->
      <div class="mt-6 flex gap-3">
        <button v-if="step > 1" @click="step--"
          class="flex-1 border border-gray-200 bg-white text-gray-600 py-3.5 rounded-2xl font-semibold text-sm hover:bg-gray-50 transition">
          이전
        </button>
        <button v-if="step < 4" @click="nextStep"
          class="flex-1 bg-orange-500 text-white py-3.5 rounded-2xl font-semibold text-sm hover:bg-orange-600 transition shadow-sm">
          다음
        </button>
        <button v-if="step === 4" @click="submit" :disabled="submitting"
          :class="['flex-1 py-3.5 rounded-2xl font-bold text-sm transition shadow-sm flex items-center justify-center gap-2',
            submitting ? 'bg-orange-300 text-white cursor-not-allowed' : 'bg-orange-500 text-white hover:bg-orange-600']">
          <div v-if="submitting" class="animate-spin w-4 h-4 border-2 border-white border-t-transparent rounded-full"></div>
          {{ submitting ? '등록 중...' : '레시피 올리기' }}
        </button>
      </div>

    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'

const router = useRouter()
const step = ref(1)
const submitting = ref(false)
const uploadingImg = ref(false)
const error = ref('')
const tagInput = ref('')
const categories = ref([])

const form = ref({
  title: '',
  intro: '',
  category_id: null,
  difficulty: '',
  cook_time: '',
  servings: 2,
  image_url: '',
  ingredients: [{ name: '', amount: '' }],
  steps: [{ text: '' }],
  tips: [],
  tags: [],
})

const quickIngredients = [
  '소금','설탕','간장','고추장','된장','참기름','마늘','생강','대파','양파',
  '계란','두부','돼지고기','소고기','닭고기','김치','쌀','당면','깻잎','들기름',
  '식용유','후추','다진마늘','고춧가루','참깨','굴소스','미림','청주'
]

const categoryName = computed(() => {
  const cat = categories.value.find(c => c.id === form.value.category_id)
  return cat ? cat.icon + ' ' + cat.name : ''
})

async function loadCategories() {
  try {
    const { data } = await axios.get('/api/recipes/categories')
    categories.value = data
  } catch {}
}

async function uploadImage(e) {
  const file = e.target.files[0]
  if (!file) return
  if (file.size > 5 * 1024 * 1024) { error.value = '이미지는 5MB 이하만 가능합니다.'; return }
  uploadingImg.value = true
  error.value = ''
  try {
    const fd = new FormData()
    fd.append('image', file)
    const { data } = await axios.post('/api/recipes/image', fd, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    form.value.image_url = data.url
  } catch {
    error.value = '이미지 업로드에 실패했습니다. 다시 시도해주세요.'
  } finally {
    uploadingImg.value = false
  }
}

function addTag() {
  const t = tagInput.value.trim().replace(/^#/, '')
  if (t && !form.value.tags.includes(t) && form.value.tags.length < 10) {
    form.value.tags.push(t)
  }
  tagInput.value = ''
}

function nextStep() {
  error.value = ''
  if (step.value === 1) {
    if (!form.value.title.trim()) { error.value = '요리 이름을 입력해주세요.'; return }
    if (!form.value.category_id) { error.value = '카테고리를 선택해주세요.'; return }
  }
  step.value++
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

async function submit() {
  error.value = ''
  if (!form.value.title.trim()) { error.value = '요리 이름을 입력해주세요.'; step.value = 1; return }
  if (!form.value.category_id) { error.value = '카테고리를 선택해주세요.'; step.value = 1; return }

  submitting.value = true
  try {
    const payload = {
      ...form.value,
      ingredients: form.value.ingredients.filter(i => i.name.trim()),
      steps: form.value.steps.filter(s => s.text.trim()),
      tips: form.value.tips.filter(t => t.trim()),
    }
    const { data } = await axios.post('/api/recipes', payload)
    router.push({ name: 'recipe-detail', params: { id: data.id } })
  } catch (e) {
    error.value = e.response?.data?.message || '등록에 실패했습니다. 다시 시도해주세요.'
  } finally {
    submitting.value = false
  }
}

onMounted(loadCategories)
</script>
'''
print(write_file('/var/www/somekorean/resources/js/pages/recipes/RecipeCreate.vue', recipe_create))

# ── 4. Update RecipeList.vue - remove Maangchi, add write button ───────────────
print("\n=== 4. Updating RecipeList.vue ===")
raw = ssh('base64 /var/www/somekorean/resources/js/pages/recipes/RecipeList.vue')
content = base64.b64decode(raw).decode('utf-8')

# Remove Maangchi section - find it and cut it out
maangchi_start = content.find('      <!-- Maangchi')
recipe_list_start = content.find('      <!-- \ub808\uc2dc\ud53c \ubaa9\ub85d -->')
if maangchi_start >= 0 and recipe_list_start > maangchi_start:
    content = content[:maangchi_start] + content[recipe_list_start:]
    print("Maangchi section removed")
else:
    print("Maangchi section not found or already removed")

# Add write button to header
old_hdr = '''      <div class="bg-gradient-to-r from-orange-500 to-amber-400 text-white px-6 py-6 rounded-2xl mb-4">
        <h1 class="text-xl font-black">\U0001f373 \ub808\uc2dc\ud53c</h1>
        <p class="text-orange-100 text-sm mt-0.5">\ubbf8\uad6d \ud55c\uc778\ub4e4\uc758 \uc694\ub9ac \ub808\uc2dc\ud53c \ubaa8\uc74c</p>
      </div>'''
new_hdr = '''      <div class="bg-gradient-to-r from-orange-500 to-amber-400 text-white px-6 py-6 rounded-2xl mb-4">
        <div class="flex items-start justify-between">
          <div>
            <h1 class="text-xl font-black">\U0001f373 \ub808\uc2dc\ud53c</h1>
            <p class="text-orange-100 text-sm mt-0.5">\ubbf8\uad6d \ud55c\uc778\ub4e4\uc758 \uc694\ub9ac \ub808\uc2dc\ud53c \ubaa8\uc74c</p>
          </div>
          <router-link to="/recipes/create"
            class="bg-white text-orange-500 px-4 py-2 rounded-xl text-sm font-bold shadow hover:bg-orange-50 transition flex items-center gap-1 flex-shrink-0">
            \u270f\ufe0f \uc62c\ub9ac\uae30
          </router-link>
        </div>
      </div>'''
if old_hdr in content:
    content = content.replace(old_hdr, new_hdr)
    print("Write button added")
else:
    # Try raw string match
    idx = content.find('bg-gradient-to-r from-orange-500 to-amber-400 text-white px-6 py-6 rounded-2xl mb-4')
    if idx >= 0:
        print("Header found at index:", idx, "- trying block replacement")
        blk_start = content.rfind('<div', 0, idx)
        # Find the closing tag of this div (next </div> after the p tag)
        p_idx = content.find('레시피 모음</p>', idx)
        end_idx = content.find('</div>', p_idx) + 6
        old_block = content[blk_start:end_idx]
        new_block = '''      <div class="bg-gradient-to-r from-orange-500 to-amber-400 text-white px-6 py-6 rounded-2xl mb-4">
        <div class="flex items-start justify-between">
          <div>
            <h1 class="text-xl font-black">🍳 레시피</h1>
            <p class="text-orange-100 text-sm mt-0.5">미국 한인들의 요리 레시피 모음</p>
          </div>
          <router-link to="/recipes/create"
            class="bg-white text-orange-500 px-4 py-2 rounded-xl text-sm font-bold shadow hover:bg-orange-50 transition flex items-center gap-1 flex-shrink-0">
            ✏️ 올리기
          </router-link>
        </div>
      </div>'''
        content = content.replace(old_block, new_block)
        print("Header replaced via block")

# Remove maangchiRecipes ref and loadMaangchi function from script
for old, new in [
    ("const maangchiRecipes = ref([])\n", ""),
    ("async function loadMaangchi() {\n  try {\n    const r = await axios.get('/api/recipes', { params: { source: 'maangchi', per_page: 8, sort: 'latest' } })\n    maangchiRecipes.value = r.data.data || r.data || []\n  } catch(e) {}\n}\n\n", ""),
    ("  await loadMaangchi()\n", ""),
]:
    if old in content:
        content = content.replace(old, new)
        print("Removed:", repr(old[:40]))

# Add sort select to filter bar
old_srch_btn = '''          <button @click="loadRecipes" class="bg-orange-500 hover:bg-orange-600 text-white px-4 py-2 rounded-xl text-sm font-medium transition">\uac80\uc0c9</button>
        </div>
      </div>'''
new_srch_btn = '''          <select v-model="sort" @change="loadRecipes" class="border border-gray-200 rounded-xl px-3 py-2 text-sm focus:outline-none focus:border-orange-400">
            <option value="latest">\ucd5c\uc2e0\uc21c</option>
            <option value="popular">\uc778\uae30\uc21c</option>
            <option value="views">\uc870\ud68c\uc21c</option>
          </select>
          <button @click="loadRecipes" class="bg-orange-500 hover:bg-orange-600 text-white px-4 py-2 rounded-xl text-sm font-medium transition">\uac80\uc0c9</button>
        </div>
      </div>'''
if old_srch_btn in content:
    content = content.replace(old_srch_btn, new_srch_btn)
    print("Sort select added")

# Add sort ref in script
old_diff = "const difficulty = ref('')"
new_diff = "const difficulty = ref('')\nconst sort = ref('latest')"
if old_diff in content:
    content = content.replace(old_diff, new_diff)
    print("sort ref added")

# Add sort to loadRecipes params
old_params = "    if (difficulty.value) params.difficulty = difficulty.value"
new_params = "    if (difficulty.value) params.difficulty = difficulty.value\n    if (sort.value) params.sort = sort.value"
if old_params in content:
    content = content.replace(old_params, new_params)
    print("sort param added")

print(write_file('/var/www/somekorean/resources/js/pages/recipes/RecipeList.vue', content))

# ── 5. Update router ──────────────────────────────────────────────────────────
print("\n=== 5. Updating router ===")
raw = ssh('base64 /var/www/somekorean/resources/js/router/index.js')
router_content = base64.b64decode(raw).decode('utf-8')

# Find the recipe-detail route line
det_line = "{ path: '/recipes/:id(\\\\d+)', component: () => import('../pages/recipes/RecipeDetail.vue'), name: 'recipe-detail' },"
if det_line in router_content:
    new_lines = "{ path: '/recipes/create', component: () => import('../pages/recipes/RecipeCreate.vue'), name: 'recipe-create', meta: { requiresAuth: true } },\n    " + det_line
    router_content = router_content.replace(det_line, new_lines)
    print("Recipe create route added")
    print(write_file('/var/www/somekorean/resources/js/router/index.js', router_content))
else:
    idx = router_content.find('recipe-detail')
    print("recipe-detail at index:", idx)
    print(repr(router_content[idx-80:idx+80]))

# ── 6. Delete Maangchi recipes from DB ───────────────────────────────────────
print("\n=== 6. Cleaning DB ===")
print(ssh("mysql -u somekorean_user -pSK_DB@2026!secure somekorean -e \"DELETE FROM recipe_posts WHERE source='maangchi'; SELECT ROW_COUNT() as deleted;\""))
print(ssh("mysql -u somekorean_user -pSK_DB@2026!secure somekorean -e \"SELECT COUNT(*) as user_recipes FROM recipe_posts WHERE source='user';\""))

# ── 7. Create recipes storage dir ────────────────────────────────────────────
print(ssh('mkdir -p /var/www/somekorean/storage/app/public/recipes && echo storage_ok'))

# ── 8. Build ──────────────────────────────────────────────────────────────────
print("\n=== 8. Building ===")
result = ssh('cd /var/www/somekorean && npm run build 2>&1', timeout=180)
lines = result.splitlines()
# Show errors if any
if 'error' in result.lower():
    for l in lines:
        if 'error' in l.lower() or 'Error' in l:
            print(l)
print('\n'.join(lines[-10:]))

c.close()
