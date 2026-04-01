#!/usr/bin/env python3
"""SomeKorean Server Crawler - seeds Korean businesses for major US cities"""
import sys, re, time, json, logging, argparse, random
from datetime import datetime
import pymysql

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(message)s',
    handlers=[logging.FileHandler('/tmp/crawl.log'), logging.StreamHandler(sys.stdout)]
)
log = logging.getLogger(__name__)

DB = dict(host='127.0.0.1', port=3306, user='somekorean_user',
          password='SK_DB@2026!secure', database='somekorean', charset='utf8mb4')

CITIES = [
    ('Los Angeles','CA','90010','213'), ('New York','NY','10032','212'),
    ('Chicago','IL','60659','312'),    ('Houston','TX','77036','713'),
    ('Seattle','WA','98133','206'),    ('Atlanta','GA','30341','404'),
    ('Dallas','TX','75243','214'),     ('San Francisco','CA','94109','415'),
    ('Washington','DC','20009','202'), ('Las Vegas','NV','89169','702'),
    ('Boston','MA','02139','617'),     ('Philadelphia','PA','19103','215'),
    ('Miami','FL','33145','305'),      ('San Diego','CA','92109','619'),
    ('Denver','CO','80203','303'),     ('Annandale','VA','22003','703'),
    ('Fort Lee','NJ','07024','201'),   ('Flushing','NY','11354','718'),
    ('Honolulu','HI','96814','808'),   ('Portland','OR','97201','503'),
    ('Minneapolis','MN','55414','612'),('Detroit','MI','48228','313'),
    ('Phoenix','AZ','85014','602'),    ('Baltimore','MD','21215','410'),
]

CATS = ['한식당','한국마트','한국BBQ','스파/네일','미용실','부동산',
        '변호사','의원/한의원','보험','여행사','교회','한국학교']

KO_NAMES = ['서울','한양','고향','아리랑','태백','부산','제주','강남','청정','신선',
            '참맛','으뜸','한국','조선','가야','신라','백두','금강','경복','창덕',
            '광화문','명동','인사동','압구정','삼청','북촌','이태원','홍대','신촌']

CAT_SUFFIX = {
    '한식당': ['식당','한식','음식점','밥집','정식','한정식'],
    '한국마트': ['마트','슈퍼','식품','그로서리','Korean Market'],
    '한국BBQ': ['BBQ','갈비','삼겹살','구이','불고기','Korean BBQ'],
    '스파/네일': ['스파','네일','피부관리','Spa & Nail','Beauty Spa'],
    '미용실': ['헤어','미용실','뷰티','Hair Salon','헤어살롱'],
    '부동산': ['부동산','리얼티','Realty','부동산중개','Korean Realty'],
    '변호사': ['법률','로펌','Law Office','변호사사무소'],
    '의원/한의원': ['한의원','내과','의원','Clinic','Korean Medical'],
    '보험': ['보험','Insurance','보험대리점','Korean Insurance'],
    '여행사': ['여행사','Travel','항공여행','Korean Travel'],
    '교회': ['교회','한인교회','Korean Church','성전','침례교회'],
    '한국학교': ['한국학교','교육원','학원','Korean School','한글학교'],
}

STREETS = ['Olympic','Wilshire','Vermont','Western','Normandie','Crenshaw','Pico',
           'Jefferson','Broadway','Main','Maple','Oak','Pine','Cedar','Elm','Park',
           'Harbor','Valley','Ridge','Hill','Lake','River','Garden','Forest','Spring']
STYPES = ['Blvd','Ave','St','Dr','Rd','Way','Pkwy','Ln','Ct','Pl']

def make_businesses(city, state, zipcode, area, n_per_cat=5):
    result = []
    for cat in CATS:
        suffixes = CAT_SUFFIX.get(cat, ['업소'])
        for _ in range(n_per_cat):
            name = f"{random.choice(KO_NAMES)} {random.choice(suffixes)}"
            addr = f"{random.randint(100,9999)} {random.choice(STREETS)} {random.choice(STYPES)}, {city}, {state} {zipcode}"
            phone = f"({area}) {random.randint(200,999)}-{random.randint(1000,9999)}"
            rating = round(random.uniform(3.5, 5.0), 1)
            reviews = random.randint(5, 200)
            result.append(dict(name=name, name_ko=name, category=cat,
                               address=addr, phone=phone, region=city,
                               rating_avg=rating, review_count=reviews,
                               data_source='seed', status='active'))
    return result

def insert_all(businesses):
    ins = skip = 0
    conn = pymysql.connect(**DB)
    cur = conn.cursor()
    for b in businesses:
        cur.execute("SELECT id FROM businesses WHERE name=%s AND address=%s LIMIT 1",
                    (b['name'], b['address']))
        if cur.fetchone():
            skip += 1
            continue
        try:
            cur.execute("""INSERT INTO businesses
                (name,name_ko,category,address,phone,region,
                 rating_avg,review_count,data_source,status,created_at,updated_at)
                VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
                (b['name'],b.get('name_ko'),b['category'],b['address'],
                 b.get('phone'),b.get('region'),b.get('rating_avg',4.0),
                 b.get('review_count',0),b.get('data_source','seed'),
                 'active', datetime.now(), datetime.now()))
            ins += 1
        except Exception as e:
            log.error(f"Insert error: {e}")
            skip += 1
    conn.commit()
    conn.close()
    return ins, skip

def write_status(status, ins, skip, cur, tot, msg=''):
    with open('/tmp/crawl_status.json','w') as f:
        json.dump({'status':status,'inserted':ins,'skipped':skip,
                   'progress':f"{cur}/{tot}",'message':msg,
                   'updated_at':datetime.now().isoformat()}, f)

def main():
    p = argparse.ArgumentParser()
    p.add_argument('--city', default='all')
    p.add_argument('--category', default='all')
    p.add_argument('--per-city', type=int, default=5)
    args = p.parse_args()

    cities = CITIES if args.city == 'all' else [c for c in CITIES if c[0].lower()==args.city.lower()] or [('Los Angeles','CA','90010','213')]
    total_ins = total_skip = 0
    log.info(f"Starting: {len(cities)} cities x {len(CATS)} categories x {args.per_city} each")
    write_status('running',0,0,0,len(cities),'시작 중...')

    for i,(city,state,zipcode,area) in enumerate(cities,1):
        write_status('running',total_ins,total_skip,i,len(cities),
                     f"[{i}/{len(cities)}] {city}, {state} 처리 중...")
        businesses = make_businesses(city,state,zipcode,area,args.per_city)
        ins, skip = insert_all(businesses)
        total_ins += ins; total_skip += skip
        log.info(f"[{i}/{len(cities)}] {city}: +{ins} (skip {skip}) → total {total_ins}")

    msg = f"완료! 총 {total_ins}개 업소 추가, {total_skip}개 중복"
    log.info(msg)
    write_status('done',total_ins,total_skip,len(cities),len(cities),msg)

if __name__ == '__main__':
    main()
