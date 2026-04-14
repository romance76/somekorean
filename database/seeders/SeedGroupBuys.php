<?php

namespace Database\Seeders;

use Illuminate\Database\Seeder;
use App\Models\GroupBuy;
use App\Models\GroupBuyParticipant;
use App\Models\User;

class SeedGroupBuys extends Seeder
{
    public function run(): void
    {
        GroupBuyParticipant::query()->delete();
        GroupBuy::query()->delete();

        $users = User::pluck('id')->toArray();
        $now = now();

        $items = [
            // ═══ 식품 ═══
            ['title'=>'김치 공동구매 (포기김치 10kg)','category'=>'식품','content'=>"한국에서 직수입한 종가집 포기김치 10kg\n\n국내산 배추+고추가루\n냉장 배송 (미국 전역)\n유통기한: 제조일로부터 3개월\n\n개인 구매 시 $65\n공동구매 최저 $45 (30% 할인!)\n\n20명 모이면 최대 할인가 적용됩니다.",'original_price'=>65,'group_price'=>45,'min_participants'=>10,'max_participants'=>30,'discount_tiers'=>[['min_people'=>10,'discount_pct'=>15],['min_people'=>20,'discount_pct'=>25],['min_people'=>30,'discount_pct'=>30]],'end_type'=>'flexible','deadline'=>$now->copy()->addDays(14),'city'=>'Atlanta','state'=>'GA','lat'=>33.749,'lng'=>-84.388,'status'=>'recruiting','current_participants'=>8],
            ['title'=>'한국 과자 종합세트 (20종)','category'=>'식품','content'=>"한국 인기 과자 20종 세트\n\n새우깡, 양파링, 칸쵸, 빈츠, 초코파이, 마가렛트 등\n한 박스에 20가지!\n\n혼자 사면 $35\n10명 모이면 $25로!",'original_price'=>35,'group_price'=>25,'min_participants'=>10,'max_participants'=>50,'discount_tiers'=>[['min_people'=>10,'discount_pct'=>15],['min_people'=>30,'discount_pct'=>25],['min_people'=>50,'discount_pct'=>30]],'end_type'=>'time_limit','deadline'=>$now->copy()->addDays(7),'city'=>'Duluth','state'=>'GA','lat'=>34.003,'lng'=>-84.145,'status'=>'recruiting','current_participants'=>15],
            ['title'=>'된장/고추장 세트 (CJ 해찬들)','category'=>'식품','content'=>"CJ 해찬들 된장 1kg + 고추장 1kg 세트\n\n한인마트보다 저렴하게!\n배송비 포함 가격\n\n원래 $28 → 15명 모이면 $20",'original_price'=>28,'group_price'=>20,'min_participants'=>15,'max_participants'=>40,'discount_tiers'=>[['min_people'=>15,'discount_pct'=>20],['min_people'=>30,'discount_pct'=>28]],'end_type'=>'flexible','deadline'=>$now->copy()->addDays(10),'city'=>'Los Angeles','state'=>'CA','lat'=>34.052,'lng'=>-118.244,'status'=>'recruiting','current_participants'=>3],

            // ═══ 뷰티 ═══
            ['title'=>'설화수 자음생 크림 공동구매','category'=>'뷰티','content'=>"설화수 자음생 크림 60ml\n\n백화점 정품, 한국 직배송\n개인 구매 $180 → 공구가 $130\n\n최소 5명부터 진행\nEMS 배송 약 7~10일",'original_price'=>180,'group_price'=>130,'min_participants'=>5,'max_participants'=>20,'discount_tiers'=>[['min_people'=>5,'discount_pct'=>15],['min_people'=>10,'discount_pct'=>22],['min_people'=>20,'discount_pct'=>28]],'end_type'=>'target_met','deadline'=>$now->copy()->addDays(21),'city'=>'New York','state'=>'NY','lat'=>40.748,'lng'=>-73.997,'status'=>'recruiting','current_participants'=>7],
            ['title'=>'한국 마스크팩 100매 세트','category'=>'뷰티','content'=>"메디힐 + 더마토리 혼합 100매 세트\n\n한국에서 대량 구매로 초저가!\n$0.50/매 이하 가능\n\n혼자 사면 $80 → 20명 모이면 $50",'original_price'=>80,'group_price'=>50,'min_participants'=>10,'max_participants'=>30,'discount_tiers'=>[['min_people'=>10,'discount_pct'=>20],['min_people'=>20,'discount_pct'=>30],['min_people'=>30,'discount_pct'=>38]],'end_type'=>'time_limit','deadline'=>$now->copy()->addDays(5),'city'=>'','state'=>'','lat'=>0,'lng'=>0,'status'=>'recruiting','current_participants'=>18],

            // ═══ 전자제품 ═══
            ['title'=>'삼성 갤럭시 S26 울트라 공동구매','category'=>'전자제품','content'=>"삼성 갤럭시 S26 울트라 256GB\n\n미국 정식 출시 모델\n언락 버전\n\n개인 $1199 → 공구 $1050\n10대 이상 모이면 추가 할인\n\nSamsung 공인 딜러 통한 정품",'original_price'=>1199,'group_price'=>1050,'min_participants'=>5,'max_participants'=>20,'discount_tiers'=>[['min_people'=>5,'discount_pct'=>5],['min_people'=>10,'discount_pct'=>10],['min_people'=>20,'discount_pct'=>12]],'end_type'=>'target_met','deadline'=>$now->copy()->addDays(30),'city'=>'Dallas','state'=>'TX','lat'=>32.777,'lng'=>-96.797,'status'=>'recruiting','current_participants'=>4],
            ['title'=>'LG 공기청정기 AS300 공동구매','category'=>'전자제품','content'=>"LG 퓨리케어 공기청정기 AS300\n\nWi-Fi 연동, HEPA 필터\n한국 모델이라 더 조용하고 효율적\n\n미국 내 직배송\n$450 → 공구가 $350",'original_price'=>450,'group_price'=>350,'min_participants'=>8,'max_participants'=>25,'discount_tiers'=>[['min_people'=>8,'discount_pct'=>15],['min_people'=>15,'discount_pct'=>22]],'end_type'=>'flexible','deadline'=>$now->copy()->addDays(20),'city'=>'Chicago','state'=>'IL','lat'=>41.878,'lng'=>-87.630,'status'=>'recruiting','current_participants'=>6],

            // ═══ 생활용품 ═══
            ['title'=>'한국 이불 세트 (퀸사이즈) 공동구매','category'=>'생활용품','content'=>"한국식 솜이불 + 패드 + 베개 세트\n\n퀸사이즈, 순면 100%\n사계절용\n\n한국 직배송, $120 → 10명 모이면 $85",'original_price'=>120,'group_price'=>85,'min_participants'=>10,'max_participants'=>30,'discount_tiers'=>[['min_people'=>10,'discount_pct'=>20],['min_people'=>20,'discount_pct'=>29]],'end_type'=>'time_limit','deadline'=>$now->copy()->addDays(12),'city'=>'Duluth','state'=>'GA','lat'=>34.003,'lng'=>-84.145,'status'=>'recruiting','current_participants'=>12],
            ['title'=>'스텐리스 반찬통 세트 (10개)','category'=>'생활용품','content'=>"한국식 스텐리스 반찬통 10개 세트\n\n다양한 사이즈, 뚜껑 포함\n식기세척기/냉동실 OK\n\n아마존 $45 → 공구 $30",'original_price'=>45,'group_price'=>30,'min_participants'=>15,'max_participants'=>50,'discount_tiers'=>[['min_people'=>15,'discount_pct'=>20],['min_people'=>30,'discount_pct'=>30],['min_people'=>50,'discount_pct'=>33]],'end_type'=>'flexible','deadline'=>$now->copy()->addDays(8),'city'=>'Houston','state'=>'TX','lat'=>29.760,'lng'=>-95.370,'status'=>'recruiting','current_participants'=>22],

            // ═══ 건강 ═══
            ['title'=>'정관장 홍삼 에브리타임 공동구매','category'=>'건강','content'=>"정관장 홍삼 에브리타임 밸런스 30포\n\n한국 직배송 정품\n$65 → 20명 모이면 $45\n\n면역력 챙기세요!",'original_price'=>65,'group_price'=>45,'min_participants'=>10,'max_participants'=>40,'discount_tiers'=>[['min_people'=>10,'discount_pct'=>15],['min_people'=>20,'discount_pct'=>25],['min_people'=>40,'discount_pct'=>31]],'end_type'=>'time_limit','deadline'=>$now->copy()->addDays(15),'city'=>'','state'=>'','lat'=>0,'lng'=>0,'status'=>'recruiting','current_participants'=>14],

            // ═══ 완료/취소된 것들 ═══
            ['title'=>'한국 라면 박스 (20개입) — 완료','category'=>'식품','content'=>"신라면, 진라면, 너구리 등 한국 라면 20개 믹스박스\n\n공동구매 성공! 35명 참여\n배송 완료되었습니다.",'original_price'=>40,'group_price'=>25,'min_participants'=>20,'max_participants'=>50,'discount_tiers'=>[['min_people'=>20,'discount_pct'=>25],['min_people'=>40,'discount_pct'=>38]],'end_type'=>'target_met','deadline'=>$now->copy()->subDays(10),'city'=>'Atlanta','state'=>'GA','lat'=>33.749,'lng'=>-84.388,'status'=>'completed','current_participants'=>35,'is_approved'=>true],
            ['title'=>'한국 전기밥솥 쿠쿠 — 취소','category'=>'전자제품','content'=>"쿠쿠 전기밥솥 IH 10인용\n\n최소 인원 미달로 취소되었습니다.\n참여하신 분들께 전액 환불 완료.",'original_price'=>380,'group_price'=>280,'min_participants'=>10,'max_participants'=>20,'discount_tiers'=>[['min_people'=>10,'discount_pct'=>18],['min_people'=>20,'discount_pct'=>26]],'end_type'=>'flexible','deadline'=>$now->copy()->subDays(5),'city'=>'Seattle','state'=>'WA','lat'=>47.606,'lng'=>-122.332,'status'=>'cancelled','current_participants'=>4,'is_approved'=>true],
            ['title'=>'한국 겨울 패딩 공동구매 — 확정','category'=>'패션','content'=>"노스페이스 한국 한정판 롱패딩\n\n목표 인원 달성! 현재 결제 진행 중\n배송 예정: 2주 후",'original_price'=>350,'group_price'=>260,'min_participants'=>10,'max_participants'=>25,'discount_tiers'=>[['min_people'=>10,'discount_pct'=>18],['min_people'=>25,'discount_pct'=>26]],'end_type'=>'target_met','deadline'=>$now->copy()->addDays(3),'city'=>'New York','state'=>'NY','lat'=>40.748,'lng'=>-73.997,'status'=>'confirmed','current_participants'=>25,'is_approved'=>true],
        ];

        foreach ($items as $item) {
            $ownerId = $users[array_rand($users)];
            $item['user_id'] = $ownerId;
            if (!isset($item['is_approved'])) $item['is_approved'] = true; // 시드 데이터는 승인된 상태
            $item['payment_method'] = 'point';
            $gb = GroupBuy::create($item);

            // 참여자 추가
            $pCount = min($item['current_participants'], 15);
            $pIds = collect($users)->reject(fn($id) => $id === $ownerId)->shuffle()->take($pCount);
            foreach ($pIds as $pid) {
                GroupBuyParticipant::create([
                    'group_buy_id' => $gb->id,
                    'user_id' => $pid,
                    'quantity' => 1,
                    'paid_amount' => $gb->group_price * 100, // cents
                    'payment_type' => 'point',
                    'status' => in_array($gb->status, ['completed','confirmed']) ? 'paid' : 'pending',
                ]);
            }
        }

        $this->command->info('Created ' . count($items) . ' group buys with participants');
    }
}
