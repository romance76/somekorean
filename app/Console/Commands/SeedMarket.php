<?php

namespace App\Console\Commands;

use App\Models\MarketItem;
use App\Models\User;
use Illuminate\Console\Command;
use Carbon\Carbon;

class SeedMarket extends Command
{
    protected $signature = 'market:seed';
    protected $description = '중고장터 현실적 시드 데이터 생성 (카테고리당 20~30개)';

    public function handle(): int
    {
        $this->info('기존 중고장터 데이터 삭제...');
        \DB::statement('DELETE FROM market_reservations');
        MarketItem::query()->delete();

        $userIds = User::pluck('id')->toArray();
        if (count($userIds) < 5) { $this->error('유저 부족'); return 1; }

        $cities = [
            ['city'=>'Los Angeles','state'=>'CA','lat'=>34.0522,'lng'=>-118.2437],
            ['city'=>'New York','state'=>'NY','lat'=>40.7128,'lng'=>-74.0060],
            ['city'=>'Chicago','state'=>'IL','lat'=>41.8781,'lng'=>-87.6298],
            ['city'=>'Houston','state'=>'TX','lat'=>29.7604,'lng'=>-95.3698],
            ['city'=>'Atlanta','state'=>'GA','lat'=>33.7490,'lng'=>-84.3880],
            ['city'=>'Seattle','state'=>'WA','lat'=>47.6062,'lng'=>-122.3321],
            ['city'=>'Dallas','state'=>'TX','lat'=>32.7767,'lng'=>-96.7970],
            ['city'=>'San Francisco','state'=>'CA','lat'=>37.7749,'lng'=>-122.4194],
            ['city'=>'Irvine','state'=>'CA','lat'=>33.6846,'lng'=>-117.8265],
            ['city'=>'Bergen County','state'=>'NJ','lat'=>40.9176,'lng'=>-74.0713],
        ];

        $items = $this->getItems();
        $total = 0;

        foreach ($items as $category => $listings) {
            $this->info("  {$category}: " . count($listings) . '개');
            foreach ($listings as $item) {
                $loc = $cities[array_rand($cities)];
                $daysAgo = rand(1, 60);
                $status = $this->weightedRandom(['active' => 70, 'reserved' => 15, 'sold' => 15]);

                MarketItem::create([
                    'user_id' => $userIds[array_rand($userIds)],
                    'title' => $item['title'],
                    'content' => $item['content'],
                    'price' => $item['price'],
                    'category' => $category,
                    'condition' => $item['condition'] ?? ['new','like_new','good','fair'][array_rand(['new','like_new','good','fair'])],
                    'status' => $status,
                    'is_negotiable' => rand(0, 1),
                    'view_count' => rand(20, 800),
                    'city' => $loc['city'],
                    'state' => $loc['state'],
                    'lat' => $loc['lat'] + (rand(-500, 500) / 10000),
                    'lng' => $loc['lng'] + (rand(-500, 500) / 10000),
                    'created_at' => Carbon::now()->subDays($daysAgo)->subHours(rand(0, 23)),
                    'updated_at' => Carbon::now()->subDays(max(0, $daysAgo - rand(0, 5))),
                ]);
                $total++;
            }
        }

        $this->info("완료: {$total}개 생성");
        return 0;
    }

    private function weightedRandom(array $w): string
    {
        $sum = array_sum($w); $r = rand(1, $sum); $c = 0;
        foreach ($w as $v => $wt) { $c += $wt; if ($r <= $c) return $v; }
        return array_key_first($w);
    }

    private function getItems(): array
    {
        return [
            'electronics' => [
                ['title'=>'맥북 프로 14인치 M3 Pro 팝니다','content'=>"작년 11월에 구매했고 상태 A급입니다. 키스킨 붙여서 써서 자판 깨끗하고 배터리 사이클 47회입니다. 충전기, 박스 전부 있어요. 직거래 원합니다.",'price'=>1850,'condition'=>'like_new'],
                ['title'=>'아이패드 에어 5세대 64GB 와이파이','content'=>"아이들 학습용으로 샀는데 안 써서 팝니다. 케이스랑 필름 붙여둔 상태. 기스 없어요.",'price'=>380,'condition'=>'like_new'],
                ['title'=>'삼성 갤럭시 S24 울트라 256GB 언락','content'=>"3개월 사용. 케이스 끼고 써서 상태 좋습니다. 박스, 충전기 포함. 색상 블랙.",'price'=>850,'condition'=>'like_new'],
                ['title'=>'소니 WH-1000XM5 헤드폰','content'=>"노이즈 캔슬링 최고예요. 6개월 사용했고 이어패드 깨끗합니다. 케이스 포함.",'price'=>200,'condition'=>'good'],
                ['title'=>'닌텐도 스위치 OLED + 게임 3개','content'=>"젤다, 마리오카트, 동물의숲 포함. 프로컨도 같이 드려요. 독 + 조이콘 다 있습니다.",'price'=>280,'condition'=>'good'],
                ['title'=>'LG 27인치 4K 모니터 27UP850','content'=>"재택근무용으로 쓰다가 이사하면서 팝니다. USB-C 충전 되는 모델이에요. 박스는 없고 전원케이블만 있어요.",'price'=>250,'condition'=>'good'],
                ['title'=>'에어팟 프로 2세대 USB-C','content'=>"한 달 정도 사용. 귀에 안 맞아서 팝니다. 이어팁 새거 포함.",'price'=>170,'condition'=>'like_new'],
                ['title'=>'다이슨 V15 무선청소기 풀세트','content'=>"2년 사용했지만 관리 잘했어요. 배터리 아직 40분 이상 갑니다. 부속품 전부 포함.",'price'=>320,'condition'=>'good'],
                ['title'=>'캐논 EOS R6 Mark II 바디온리','content'=>"사진 취미로 샀다가 안 쓰게 돼서요. 셔터 카운트 5000 미만. 상태 최상.",'price'=>1600,'condition'=>'like_new'],
                ['title'=>'로지텍 MX Master 3S 마우스','content'=>"3개월 사용. 사무실에서 쓰다가 트랙패드로 바꿔서 팝니다.",'price'=>65,'condition'=>'like_new'],
                ['title'=>'PS5 디스크 에디션 + 듀얼센스 2개','content'=>"1년 반 사용. 게임은 디지털로만 사서 디스크 드라이브 거의 안 썼어요. 컨트롤러 2개 포함.",'price'=>350,'condition'=>'good'],
                ['title'=>'삼성 사운드바 HW-Q990C','content'=>"서라운드 사운드 오지게 좋습니다. 무선 서브우퍼 + 리어 스피커 풀세트. 이사 때문에 급매.",'price'=>550,'condition'=>'like_new'],
                ['title'=>'애플워치 울트라 2 49mm','content'=>"등산용으로 샀는데 결국 안 차고 다녀서요. 배터리 수명 100%. 추가 밴드 2개 포함.",'price'=>580,'condition'=>'like_new'],
                ['title'=>'아이폰 15 Pro Max 256GB 내츄럴 티타늄','content'=>"기변해서 팝니다. 케이스+필름 끼고 써서 기스 하나도 없어요. 배터리 95%. 언락폰.",'price'=>900,'condition'=>'like_new'],
                ['title'=>'JBL Charge 5 블루투스 스피커','content'=>"캠핑용으로 사놓고 2번 밖에 안 썼어요. 방수되고 소리 좋습니다.",'price'=>100,'condition'=>'like_new'],
                ['title'=>'로봇청소기 로보락 S8 Pro Ultra','content'=>"자동 물걸레 세척, 먼지통 비움 다 돼요. 1년 사용. 소모품 새걸로 교체해서 드립니다.",'price'=>650,'condition'=>'good'],
                ['title'=>'갤럭시 탭 S9 FE+ 128GB','content'=>"넷플릭스용으로 쓰다가 아이패드 사서 팝니다. S펜 포함. 기스 없음.",'price'=>350,'condition'=>'like_new'],
                ['title'=>'아마존 에코 쇼 10 3세대','content'=>"스마트홈 허브로 쓰기 좋아요. 화면 자동 회전됩니다. 거의 안 쓴 상태.",'price'=>120,'condition'=>'like_new'],
                ['title'=>'레노버 씽크패드 X1 카본 Gen 11','content'=>"회사에서 지급받았다가 퇴사하면서 구매한 거예요. i7, 16GB RAM, 512GB SSD. 보증 남아있음.",'price'=>1100,'condition'=>'like_new'],
                ['title'=>'Bose QC45 헤드폰 블랙','content'=>"비행기 탈 때만 쓴 거라 상태 좋아요. 노캔 성능 좋습니다. 케이스 포함.",'price'=>170,'condition'=>'good'],
                ['title'=>'DJI Mini 4 Pro 드론 플라이모어 콤보','content'=>"배터리 3개, 충전허브 포함. 영상 퀄리티 좋습니다. 10회 정도 비행.",'price'=>700,'condition'=>'like_new'],
                ['title'=>'전기밥솥 쿠쿠 10인용 IH','content'=>"한국에서 가져온 거예요. 변압기 필요 없는 110V 모델. 2년 사용.",'price'=>150,'condition'=>'good'],
                ['title'=>'LG 그램 17인치 2024년형','content'=>"가벼워서 출장용으로 좋아요. i7, 16GB, 1TB. 무게 1.35kg. 충전기 포함.",'price'=>1050,'condition'=>'like_new'],
            ],
            'furniture' => [
                ['title'=>'이케아 MALM 퀸 침대프레임 화이트','content'=>"2년 사용했고 상태 깨끗합니다. 매트리스는 별도. 분해해서 드려요. 셀프 픽업만 가능합니다.",'price'=>150,'condition'=>'good'],
                ['title'=>'가죽 소파 3인용 브라운','content'=>"Costco에서 $1200에 산 건데 이사 때문에 급매합니다. 약간의 사용감 있지만 전체적으로 깨끗해요.",'price'=>400,'condition'=>'good'],
                ['title'=>'스탠딩 데스크 전동 높낮이 조절','content'=>"FlexiSpot E7 모델. 1년 사용. 48x30인치. 모터 작동 완벽합니다.",'price'=>280,'condition'=>'good'],
                ['title'=>'이케아 KALLAX 4x4 책장 화이트','content'=>"상태 좋아요. 8칸짜리인데 수납 바구니 4개도 같이 드려요. 직접 와서 가져가셔야 합니다.",'price'=>80,'condition'=>'good'],
                ['title'=>'식탁 + 의자 4개 세트 우드','content'=>"원목 식탁이에요. 4인용이고 의자도 튼튼합니다. 3년 사용. 표면에 약간 스크래치.",'price'=>250,'condition'=>'fair'],
                ['title'=>'퀸 매트리스 Casper 오리지널','content'=>"1년 반 사용. 매트리스 커버 씌워서 써서 깨끗합니다. 허리 아픈 분한테 좋아요.",'price'=>300,'condition'=>'good'],
                ['title'=>'TV 스탠드 60인치까지 가능','content'=>"월마트에서 샀어요. 밑에 수납공간 넉넉합니다. 조립 상태로 가져가시면 됩니다.",'price'=>60,'condition'=>'good'],
                ['title'=>'사무용 의자 허먼밀러 에어론 리마스터드','content'=>"재택근무 끝나서 팝니다. 풀옵션이에요. 정가 $1400인데 2년 사용.",'price'=>650,'condition'=>'good'],
                ['title'=>'이케아 HEMNES 서랍장 6칸 화이트','content'=>"아기 방에 사용했어요. 깨끗하고 서랍 레일 부드럽습니다.",'price'=>120,'condition'=>'good'],
                ['title'=>'접이식 테이블 + 의자 2개 아웃도어용','content'=>"캠핑이나 피크닉에 좋아요. 접으면 차 트렁크에 들어갑니다.",'price'=>45,'condition'=>'good'],
                ['title'=>'드레서 화장대 + 거울 세트','content'=>"화이트 우드. 서랍 5칸. 거울은 탈부착 가능. 약간의 사용감.",'price'=>180,'condition'=>'good'],
                ['title'=>'책상 L자형 코너 데스크','content'=>"넓어서 모니터 2대 놓기 좋아요. 선 정리 구멍도 있어요. 1년 사용.",'price'=>130,'condition'=>'good'],
                ['title'=>'침대 사이드 테이블 2개 세트','content'=>"이케아 TARVA 모델. 내츄럴 우드. 깨끗한 상태.",'price'=>40,'condition'=>'good'],
                ['title'=>'소파베드 풀사이즈 그레이','content'=>"게스트룸에 놨던 건데 거의 안 펼쳐봤어요. 쿠션감 좋습니다.",'price'=>350,'condition'=>'like_new'],
                ['title'=>'와인 냉장고 12병 수납','content'=>"NewAir 브랜드. 소음 적고 온도 잘 유지돼요. 부엌 카운터 밑에 딱 들어가는 사이즈.",'price'=>100,'condition'=>'good'],
                ['title'=>'신발장 현관용 3단','content'=>"대나무 소재. 12켤레 정도 들어가요. 깔끔한 디자인.",'price'=>35,'condition'=>'good'],
                ['title'=>'유아 침대 크립 + 매트리스','content'=>"Graco 4-in-1 컨버터블. 토들러 베드까지 됩니다. 2년 사용. 깨끗.",'price'=>120,'condition'=>'good'],
                ['title'=>'바 스툴 2개 세트 26인치','content'=>"아일랜드 카운터용. 메탈 프레임 + 우드 시트. 실버 색상.",'price'=>70,'condition'=>'good'],
                ['title'=>'이케아 PAX 옷장 시스템','content'=>"문 2짝 + 내부 선반/서랍 구성. 해체해서 가져가셔야 해요. 조립 설명서 있음.",'price'=>200,'condition'=>'good'],
                ['title'=>'야외용 파티오 세트 4인용','content'=>"우산은 없고 테이블 + 의자 4개. 쿠션 포함. 비에 좀 탔지만 쓸만해요.",'price'=>150,'condition'=>'fair'],
            ],
            'clothing' => [
                ['title'=>'나이키 에어맥스 270 남성 10.5 새거','content'=>"선물 받았는데 사이즈가 안 맞아요. 박스째로 드립니다. 한 번도 안 신었어요.",'price'=>90,'condition'=>'new'],
                ['title'=>'캐나다구스 패딩 여성 M','content'=>"작년 겨울에 $900에 샀어요. 10번 정도 입었고 세탁 1회. 정품 인증서 있음.",'price'=>450,'condition'=>'like_new'],
                ['title'=>'노스페이스 눕시 700 남성 L','content'=>"검정색. 2시즌 입었는데 아직 따뜻해요. 지퍼 작동 완벽.",'price'=>150,'condition'=>'good'],
                ['title'=>'룰루레몬 레깅스 여성 6 3장 세트','content'=>"사이즈 아웃됐어요. Align 25인치 2장, Wunder Train 1장. 보풀 약간.",'price'=>80,'condition'=>'good'],
                ['title'=>'정장 세트 남성 40R 네이비','content'=>"Brooks Brothers. 면접 때 2번 입었어요. 드라이클리닝 완료.",'price'=>180,'condition'=>'like_new'],
                ['title'=>'아디다스 울트라부스트 여성 7.5','content'=>"일주일에 한 번씩 6개월 신었어요. 쿠션감 아직 좋아요.",'price'=>55,'condition'=>'good'],
                ['title'=>'한복 여성 M 분홍색','content'=>"설날에 한 번 입었어요. 치마 + 저고리 세트. 새것이나 다름없어요.",'price'=>120,'condition'=>'like_new'],
                ['title'=>'파타고니아 플리스 레트로 X 남성 M','content'=>"인기 모델이에요. 상태 좋고 따뜻합니다.",'price'=>100,'condition'=>'good'],
                ['title'=>'뉴발란스 993 그레이 남성 9','content'=>"미국에서만 살 수 있는 모델. 3개월 착용. 박스 있음.",'price'=>120,'condition'=>'good'],
                ['title'=>'유니클로 히트텍 울트라웜 5장 세트','content'=>"사이즈 L. 새 거 3장 + 1회 착용 2장. 겨울 필수템.",'price'=>40,'condition'=>'like_new'],
                ['title'=>'코치 핸드백 여성 브라운','content'=>"아울렛 정품. 6개월 사용. 안감 깨끗하고 가죽 상태 좋아요.",'price'=>95,'condition'=>'good'],
                ['title'=>'콜롬비아 겨울 자켓 남성 XL','content'=>"오므니히트 안감. 스키 탈 때 좋아요. 2시즌 입음.",'price'=>80,'condition'=>'good'],
                ['title'=>'아기 옷 0-12개월 50벌 일괄','content'=>"남아용. Carter, Gap, Old Navy 등. 상태 다양. 일괄 판매만.",'price'=>60,'condition'=>'fair'],
                ['title'=>'닥터마틴 1460 여성 6','content'=>"레드 체리 색상. 길들여진 상태라 편해요. 1년 반 착용.",'price'=>70,'condition'=>'good'],
                ['title'=>'나이키 테크 플리스 풀짚 남성 M','content'=>"블랙. 작년 모델. 상태 A급. 집앞 동네 산책용으로만 입음.",'price'=>65,'condition'=>'like_new'],
            ],
            'auto' => [
                ['title'=>'겨울 타이어 4개 세트 225/45R17','content'=>"Bridgestone Blizzak WS90. 한 시즌 사용. 트레드 80% 이상 남음. 휠은 없고 타이어만.",'price'=>350,'condition'=>'good'],
                ['title'=>'카시트 그라코 4ever DLX','content'=>"아이가 커서 바꿔야 해요. 사고 이력 없고 유통기한 2028년까지. 깨끗합니다.",'price'=>120,'condition'=>'good'],
                ['title'=>'루프탑 카고박스 Thule Motion XT L','content'=>"캠핑/스키 갈 때 필수. 2시즌 사용. 스크래치 약간. 잠금장치 정상.",'price'=>350,'condition'=>'good'],
                ['title'=>'대시캠 Viofo A129 Pro Duo 전후방','content'=>"4K 전방 + 1080p 후방. 설치 키트 포함. 1년 사용. 차 바꾸면서 탈거.",'price'=>120,'condition'=>'good'],
                ['title'=>'테슬라 Model 3 올웨더 플로어매트','content'=>"WeatherTech. 1년 사용. 세차해서 드립니다. 2021-2024 모델 호환.",'price'=>80,'condition'=>'good'],
                ['title'=>'점프스타터 NOCO GB40','content'=>"한 번 사용. 완충 상태. 겨울에 배터리 방전 될 때 필수.",'price'=>60,'condition'=>'like_new'],
                ['title'=>'자전거 트렁크 랙 2대용','content'=>"Saris Bones 2. SUV, 세단 모두 가능. 상태 좋아요.",'price'=>70,'condition'=>'good'],
                ['title'=>'블랙박스 아이나비 전후방','content'=>"한국에서 가져온 모델. 32GB SD카드 포함. 영상 화질 좋습니다.",'price'=>100,'condition'=>'good'],
                ['title'=>'타이어 체인 세트 사이즈 M','content'=>"눈 오는 지역 이사했다가 다시 캘리 와서 필요 없어졌어요. 1회 사용.",'price'=>45,'condition'=>'like_new'],
                ['title'=>'차량용 핸드폰 거치대 MagSafe','content'=>"벤트 클립형. 아이폰 15 시리즈용. 3개월 사용.",'price'=>20,'condition'=>'like_new'],
                ['title'=>'카플레이 무선 어댑터','content'=>"유선 CarPlay를 무선으로 바꿔주는 어댑터. 2023 토요타에서 사용했어요.",'price'=>50,'condition'=>'good'],
                ['title'=>'OBD2 블루투스 스캐너','content'=>"차 경고등 뜰 때 직접 진단할 수 있어요. 앱이랑 연동됩니다.",'price'=>15,'condition'=>'good'],
            ],
            'baby' => [
                ['title'=>'유모차 UPPAbaby Vista V2','content'=>"색상 그레고리. 배시넷 + 토들러 시트 + 범퍼바 포함. 2년 사용했지만 관리 잘 했어요.",'price'=>450,'condition'=>'good'],
                ['title'=>'하이체어 Stokke Tripp Trapp 화이트','content'=>"베이비세트 + 쿠션 포함. 성인까지 쓸 수 있는 의자. 상태 좋아요.",'price'=>180,'condition'=>'good'],
                ['title'=>'아기띠 에르고베이비 옴니 브리즈','content'=>"통기성 좋은 모델. 6개월 사용. 세탁 완료.",'price'=>80,'condition'=>'good'],
                ['title'=>'장난감 일괄 판매 (0-3세)','content'=>"피셔프라이스, VTech, 멜리사앤더그 등 20개 이상. 배터리 작동 확인. 일괄만.",'price'=>50,'condition'=>'fair'],
                ['title'=>'변기 트레이닝 세트 일괄','content'=>"보조 변기 + 스텝스툴 + 교육 책 3권. 거의 새것.",'price'=>25,'condition'=>'like_new'],
                ['title'=>'백팩 기저귀 가방 Skip Hop','content'=>"수납공간 넉넉하고 방수. 기저귀 매트 포함. 6개월 사용.",'price'=>30,'condition'=>'good'],
                ['title'=>'수유쿠션 Boppy 커버 2장 포함','content'=>"산후조리 끝나고 안 쓰게 됐어요. 커버 세탁 완료.",'price'=>20,'condition'=>'good'],
                ['title'=>'아기 바운서 4moms mamaRoo','content'=>"5가지 모션 + 블루투스 음악. 3개월 사용. 커버 세탁 가능.",'price'=>120,'condition'=>'like_new'],
                ['title'=>'아기 모니터 Nanit Pro 카메라','content'=>"호흡 감지 + 수면 분석. 벽 마운트 포함. 1년 사용.",'price'=>150,'condition'=>'good'],
                ['title'=>'유아 자전거 스트라이더 12인치','content'=>"밸런스 바이크. 2-4세용. 타이어 상태 좋아요. 색상 레드.",'price'=>50,'condition'=>'good'],
                ['title'=>'아기 욕조 Skip Hop Moby','content'=>"신생아~유아 3단계. 깨끗합니다. 6개월 사용.",'price'=>15,'condition'=>'good'],
                ['title'=>'젖병 세트 Dr. Brown 8개','content'=>"4oz 4개, 8oz 4개 + 브러시 + 건조대. 소독기도 같이 드려요.",'price'=>25,'condition'=>'good'],
            ],
            'sports' => [
                ['title'=>'골프 풀세트 캘러웨이 Rogue ST','content'=>"드라이버, 3W, 5W, 아이언 5-PW, 퍼터, 가방 포함. 1년 라운드 15회 정도.",'price'=>800,'condition'=>'good'],
                ['title'=>'펠로톤 바이크 Peloton Bike','content'=>"코로나 때 샀는데 결국 안 타게 됐어요ㅠ 구독은 별도. 매트 + 슈즈 포함.",'price'=>600,'condition'=>'good'],
                ['title'=>'덤벨 세트 5-50lbs + 랙','content'=>"고무 코팅 육각 덤벨. 총 15쌍. 랙 포함. 무겁지만 직접 와서 가져가셔야 해요.",'price'=>500,'condition'=>'good'],
                ['title'=>'테니스 라켓 윌슨 Blade 98 v8','content'=>"그립 사이즈 3. 스트링 교체한 지 한 달. 커버 포함.",'price'=>120,'condition'=>'good'],
                ['title'=>'캠핑 텐트 4인용 REI Co-op','content'=>"3시즌용. 5회 사용. 방수 완벽. 폴대, 스테이크 전부 있어요.",'price'=>180,'condition'=>'good'],
                ['title'=>'스키 부츠 남성 27.5cm Salomon','content'=>"중급자용. 한 시즌 탔어요. 커스텀 인솔 포함.",'price'=>120,'condition'=>'good'],
                ['title'=>'요가 매트 Manduka PRO 6mm','content'=>"블랙. 그립 좋고 두께 적당해요. 1년 사용. 가방 포함.",'price'=>60,'condition'=>'good'],
                ['title'=>'서핑보드 7ft 소프트탑','content'=>"초보용으로 좋아요. 핀 3개 + 리쉬코드 포함. 10회 사용.",'price'=>150,'condition'=>'good'],
                ['title'=>'농구공 Spalding NBA 공인구','content'=>"실내용. 거의 새것. 2번 사용.",'price'=>30,'condition'=>'like_new'],
                ['title'=>'등산 배낭 오스프리 Atmos 65L','content'=>"백패킹용. 2박 이상 트레일에 좋아요. 레인커버 포함. 5회 사용.",'price'=>150,'condition'=>'good'],
                ['title'=>'자전거 Specialized Allez Sport','content'=>"로드바이크. 사이즈 54cm. 2년 탔고 정비 완료. 라이트 + 락 포함.",'price'=>550,'condition'=>'good'],
                ['title'=>'낚시대 세트 초보자용','content'=>"릴 + 로드 + 태클박스. 아이와 낚시하려고 샀는데 한 번 가고 안 감.",'price'=>40,'condition'=>'like_new'],
                ['title'=>'풋살화 나이키 머큐리얼 270mm','content'=>"실내용. 5번 착용. 사이즈 안 맞아서 팝니다.",'price'=>50,'condition'=>'like_new'],
                ['title'=>'캠핑 의자 2개 + 테이블 세트','content'=>"Coleman. 접이식. 가방 포함. 3회 사용.",'price'=>45,'condition'=>'like_new'],
            ],
            'books' => [
                ['title'=>'토익 교재 세트 (RC+LC) 2024년판','content'=>"해커스 1000제 + ETS 기출. 깨끗하게 풀었어요. 연필 표기 지웠음.",'price'=>25,'condition'=>'good'],
                ['title'=>'해리포터 원서 전집 1-7','content'=>"페이퍼백. 상태 좋아요. 박스 세트 아니고 낱권.",'price'=>35,'condition'=>'good'],
                ['title'=>'미국 시민권 시험 교재 + 플래시카드','content'=>"USCIS 공식 100문제 + 한글 해설. 2주 공부하고 합격.",'price'=>10,'condition'=>'good'],
                ['title'=>'한국어 교재 세종한국어 1-4','content'=>"한글학교에서 사용. 워크북 포함. 약간의 필기 있음.",'price'=>20,'condition'=>'fair'],
                ['title'=>'요리책 백종원 집밥 시리즈 3권','content'=>"미국에서 구하기 힘든 한국 요리책. 상태 깨끗.",'price'=>25,'condition'=>'good'],
                ['title'=>'GRE 교재 Magoosh + Manhattan','content'=>"대학원 준비용. 2권 세트. 표시 없이 깨끗합니다.",'price'=>30,'condition'=>'good'],
                ['title'=>'SAT 프렙북 College Board 공식','content'=>"실전모의고사 8회분. 2024년 최신판. 한 번도 안 풀었어요.",'price'=>20,'condition'=>'new'],
                ['title'=>'부동산 자격증 교재 캘리포니아','content'=>"Kaplan Real Estate License Exam Prep. 최신판.",'price'=>25,'condition'=>'good'],
                ['title'=>'아이 그림책 한국어 30권 세트','content'=>"돼지학교, 곰돌이, 콩닥콩닥 등. 0-5세용. 상태 다양.",'price'=>40,'condition'=>'fair'],
                ['title'=>'IT 프로그래밍 책 5권 세트','content'=>"Clean Code, DDIA, Cracking the Coding Interview 등. 개발자 필독서.",'price'=>50,'condition'=>'good'],
            ],
            'etc' => [
                ['title'=>'김치냉장고 딤채 미니 소형','content'=>"한국에서 직구한 거예요. 110V 사용 가능. 김치 + 야채 보관용. 2년 사용.",'price'=>200,'condition'=>'good'],
                ['title'=>'한국 라면 박스 (20개입 5종)','content'=>"신라면, 진라면, 너구리, 안성탕면, 삼양라면. Costco보다 싸요.",'price'=>35,'condition'=>'new'],
                ['title'=>'이사 박스 + 테이프 일괄','content'=>"중형 20개 + 소형 10개 + 테이프 3개. 한 번 쓴 거라 아직 튼튼해요.",'price'=>15,'condition'=>'good'],
                ['title'=>'크리스마스 트리 7ft + 장식','content'=>"LED 불 내장형. 오너먼트 50개 + 스타 토퍼 포함. 3년 사용.",'price'=>50,'condition'=>'good'],
                ['title'=>'쿠팡 로켓배송 대행 받습니다','content'=>"한국 출장 갈 때 쿠팡에서 주문하신 거 가져다 드려요. 무게당 요금. 문의주세요.",'price'=>0,'condition'=>'new'],
                ['title'=>'피아노 디지털 야마하 P-125','content'=>"풀사이즈 88건반. 2년 사용. 스탠드 + 페달 + 헤드폰 포함.",'price'=>400,'condition'=>'good'],
                ['title'=>'강아지 용품 일괄 (중형견)','content'=>"크레이트 + 침대 + 밥그릇 + 리드 + 장난감. 강아지가 무지개다리 건너서요ㅠ",'price'=>80,'condition'=>'good'],
                ['title'=>'한국 식기 세트 4인용','content'=>"밥공기, 국그릇, 접시, 젓가락+숟가락 세트. 명절에만 꺼냈어요.",'price'=>40,'condition'=>'like_new'],
                ['title'=>'에어프라이어 닌자 5.5QT','content'=>"매일 쓰던 건데 큰 걸로 업그레이드해서 팝니다. 바스켓 깨끗.",'price'=>50,'condition'=>'good'],
                ['title'=>'변압기 3000W 승압 다운 겸용','content'=>"한국 가전제품 쓸 때 필요한 변압기. 무겁지만 성능 좋아요.",'price'=>60,'condition'=>'good'],
                ['title'=>'코스트코 선반 메탈 5단','content'=>"차고나 창고 정리용. 높이 조절 가능. 해체해서 드려요.",'price'=>35,'condition'=>'good'],
                ['title'=>'캠핑 쿨러 YETI Tundra 45','content'=>"보냉력 최고. 3박까지 얼음 안 녹아요. 무겁지만 튼튼합니다.",'price'=>180,'condition'=>'good'],
                ['title'=>'네스프레소 커피머신 Vertuo Plus','content'=>"캡슐 30개 같이 드려요. 1년 사용. 디스케일링 완료.",'price'=>80,'condition'=>'good'],
                ['title'=>'한국 보드게임 5개 세트','content'=>"할리갈리, 다빈치코드, 루미큐브, 블록커스, 스플렌더. 가족 모임용.",'price'=>40,'condition'=>'good'],
                ['title'=>'액자 세트 갤러리월 10개','content'=>"화이트 프레임. 다양한 사이즈. 벽걸이 키트 포함. 인테리어 예뻐요.",'price'=>30,'condition'=>'like_new'],
            ],
        ];
    }
}
