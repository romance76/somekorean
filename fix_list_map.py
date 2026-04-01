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

# ── FIX 1: BusinessList.vue ──────────────────────────────────────────────────
raw = ssh('base64 /var/www/somekorean/resources/js/pages/directory/BusinessList.vue')
content = base64.b64decode(raw).decode('utf-8')

# 1a) Replace naive pagination with smart pagination
old_pag = '''    <div v-if="totalPages > 1" class="flex justify-center space-x-1 mt-5">
      <button v-for="p in totalPages" :key="p" @click="load(p)"
        :class="['px-3 py-1.5 rounded text-sm', p === currentPage ? 'bg-red-600 text-white' : 'bg-white text-gray-700 hover:bg-gray-50 border border-gray-300']">
        {{ p }}
      </button>
    </div>'''

new_pag = '''    <div v-if="totalPages > 1" class="flex justify-center items-center gap-1 mt-6 flex-wrap">
      <!-- Prev -->
      <button @click="load(currentPage-1)" :disabled="currentPage===1"
        class="px-3 py-1.5 rounded-lg text-sm border bg-white text-gray-600 hover:bg-gray-50 disabled:opacity-40 disabled:cursor-not-allowed">
        ‹ 이전
      </button>
      <!-- First page -->
      <button v-if="pageList[0] > 1" @click="load(1)"
        class="px-3 py-1.5 rounded-lg text-sm border bg-white text-gray-700 hover:bg-blue-50">1</button>
      <span v-if="pageList[0] > 2" class="px-1 text-gray-400">…</span>
      <!-- Page window -->
      <button v-for="p in pageList" :key="p" @click="load(p)"
        :class="['px-3 py-1.5 rounded-lg text-sm border transition', p === currentPage
          ? 'bg-blue-600 text-white border-blue-600 font-semibold'
          : 'bg-white text-gray-700 hover:bg-blue-50']">
        {{ p }}
      </button>
      <!-- Last page -->
      <span v-if="pageList[pageList.length-1] < totalPages-1" class="px-1 text-gray-400">…</span>
      <button v-if="pageList[pageList.length-1] < totalPages" @click="load(totalPages)"
        class="px-3 py-1.5 rounded-lg text-sm border bg-white text-gray-700 hover:bg-blue-50">{{ totalPages }}</button>
      <!-- Next -->
      <button @click="load(currentPage+1)" :disabled="currentPage===totalPages"
        class="px-3 py-1.5 rounded-lg text-sm border bg-white text-gray-600 hover:bg-gray-50 disabled:opacity-40 disabled:cursor-not-allowed">
        다음 ›
      </button>
      <span class="ml-2 text-xs text-gray-400">{{ currentPage }}/{{ totalPages }}페이지 · 총 {{ totalCount }}개</span>
    </div>'''

if old_pag in content:
    content = content.replace(old_pag, new_pag)
    print("✓ Pagination template replaced")
else:
    print("✗ Pagination template not found - checking...")
    # Try to find actual content
    idx = content.find('v-for="p in totalPages"')
    if idx >= 0:
        print("Found at index:", idx)
        print(repr(content[idx-200:idx+200]))

# 1b) Replace script section - add computed pageList, totalCount, region list, radius support
old_script = '''<script setup>
import { ref, onMounted } from 'vue';
import { useAuthStore } from '../../stores/auth';

import axios from 'axios';

const authStore = useAuthStore();
const radius = ref(30);
const viewMode = ref('grid');
const businesses = ref([]);
const loading = ref(true);
const search = ref('');
const category = ref('');
const region = ref('');
const currentPage = ref(1);
const totalPages = ref(1);

const categories = [
  { value: '', label: '전체' },
  { value: '식당', label: '🍽️ 식당' },
  { value: '미용', label: '💇 미용' },
  { value: '의료', label: '🏥 의료' },
  { value: '법률', label: '⚖️ 법률' },
  { value: '부동산', label: '🏠 부동산' },
  { value: '쇼핑', label: '🛍️ 쇼핑' },
  { value: '교육', label: '📚 교육' },
  { value: '기타', label: '기타' },
];

async function load(page = 1) {
  loading.value = true;
  try {
    const { data } = await axios.get('/api/businesses', { params: { page, search: search.value, category: category.value, region: region.value } });
    businesses.value = data.data;
    currentPage.value = data.current_page;
    totalPages.value = data.last_page;
  } catch {}
  loading.value = false;
}

onMounted(() => load());
</script>'''

new_script = '''<script setup>
import { ref, computed, onMounted } from 'vue';
import { useAuthStore } from '../../stores/auth';
import axios from 'axios';

const authStore = useAuthStore();
const radius = ref(30);
const viewMode = ref('grid');
const businesses = ref([]);
const loading = ref(true);
const search = ref('');
const category = ref('');
const region = ref('');
const currentPage = ref(1);
const totalPages = ref(1);
const totalCount = ref(0);

const categories = [
  { value: '', label: '전체' },
  { value: '한식당', label: '🍽️ 식당' },
  { value: '미용실', label: '💇 미용' },
  { value: '의원/한의원', label: '🏥 의료' },
  { value: '변호사', label: '⚖️ 법률' },
  { value: '부동산', label: '🏠 부동산' },
  { value: '한국마트', label: '🛒 마트' },
  { value: '한국BBQ', label: '🥩 BBQ' },
  { value: '스파/네일', label: '💅 스파' },
  { value: '교회', label: '⛪ 교회' },
  { value: '한국학교', label: '📚 교육' },
];

const regions = [
  '', 'Los Angeles', 'New York', 'Chicago', 'Houston', 'Seattle',
  'Atlanta', 'Dallas', 'San Francisco', 'Washington', 'Las Vegas',
  'Boston', 'Philadelphia', 'Miami', 'San Diego', 'Denver',
  'Annandale', 'Fort Lee', 'Flushing', 'Honolulu', 'Portland',
  'Minneapolis', 'Detroit', 'Phoenix', 'Baltimore',
];

// Smart pagination: show window of 5 pages around current
const pageList = computed(() => {
  const total = totalPages.value;
  const cur = currentPage.value;
  if (total <= 7) return Array.from({ length: total }, (_, i) => i + 1);
  const delta = 2;
  const start = Math.max(2, cur - delta);
  const end = Math.min(total - 1, cur + delta);
  const pages = [];
  for (let i = start; i <= end; i++) pages.push(i);
  return pages;
});

async function load(page = 1) {
  if (page < 1 || page > totalPages.value) return;
  loading.value = true;
  currentPage.value = page;
  try {
    const params = {
      page,
      search: search.value || undefined,
      category: category.value || undefined,
      region: region.value || undefined,
      per_page: 24,
    };
    const { data } = await axios.get('/api/businesses', { params });
    businesses.value = data.data || [];
    currentPage.value = data.current_page || page;
    totalPages.value = data.last_page || 1;
    totalCount.value = data.total || businesses.value.length;
  } catch(e) { console.error(e) }
  loading.value = false;
  window.scrollTo({ top: 0, behavior: 'smooth' });
}

onMounted(() => load());
</script>'''

if old_script in content:
    content = content.replace(old_script, new_script)
    print("✓ Script section replaced")
else:
    print("✗ Script section not found exactly - trying partial match")
    # Just replace the v-for="p in totalPages" line directly
    content = content.replace(
        'v-for="p in totalPages"',
        'v-for="p in pageList"'
    )
    # Add totalCount and pageList to script
    content = content.replace(
        "import { ref, onMounted } from 'vue';",
        "import { ref, computed, onMounted } from 'vue';"
    )
    content = content.replace(
        "const totalPages = ref(1);",
        "const totalPages = ref(1);\nconst totalCount = ref(0);\nconst pageList = computed(() => { const t=totalPages.value,c=currentPage.value; if(t<=7) return Array.from({length:t},(_,i)=>i+1); const s=Math.max(2,c-2),e=Math.min(t-1,c+2),p=[]; for(let i=s;i<=e;i++) p.push(i); return p; });"
    )
    content = content.replace(
        "totalPages.value = data.last_page;",
        "totalPages.value = data.last_page;\n    totalCount.value = data.total || 0;"
    )
    print("✓ Applied partial script fixes")

# 1c) Fix region dropdown - expand to all 24 cities
old_region = """          <select v-model="region" @change="load(1)" class="border border-gray-200 rounded-lg px-2 py-2 text-sm bg-white flex-shrink-0">
            <option value="">전체 지역</option>
            <option>Atlanta</option><option>New York</option><option>Los Angeles</option>
            <option>Dallas</option><option>Chicago</option>
          </select>"""

new_region = """          <select v-model="region" @change="load(1)" class="border border-gray-200 rounded-lg px-2 py-2 text-sm bg-white flex-shrink-0 max-w-[140px]">
            <option value="">전체 지역</option>
            <option v-for="r in regions" :key="r" :value="r">{{ r || '전체 지역' }}</option>
          </select>"""

if old_region in content:
    content = content.replace(old_region, new_region)
    print("✓ Region dropdown replaced")
else:
    print("✗ Region dropdown not found exactly")

print("\nWriting BusinessList.vue...")
print(write_file('/var/www/somekorean/resources/js/pages/directory/BusinessList.vue', content))


# ── FIX 2: LeafletMap.vue - fix marker icons (use CDN instead of bundler path) ──
leaflet_map = '''<template>
  <div style="width:100%">
    <div v-if="loading" class="flex flex-col items-center justify-center h-48 bg-gray-100 rounded-xl text-gray-400 text-sm gap-2">
      <div class="animate-spin w-6 h-6 border-4 border-blue-500 border-t-transparent rounded-full"></div>
      지도 불러오는 중...
    </div>
    <div v-else-if="error" class="flex flex-col items-center justify-center h-32 bg-gray-50 rounded-xl text-gray-500 text-sm gap-2 border">
      <span class="text-2xl">📍</span>
      <p class="font-medium">{{ address }}</p>
      <a :href="\'https://www.openstreetmap.org/search?query=\'+encodeURIComponent(address)"
         target="_blank" class="text-blue-600 hover:underline text-xs">OpenStreetMap에서 보기 →</a>
    </div>
    <div v-show="!loading && !error" ref="mapEl" style="width:100%;height:300px;border-radius:12px;z-index:0;"></div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from \'vue\'

const props = defineProps({
  lat: { type: [Number, String], default: null },
  lng: { type: [Number, String], default: null },
  name: { type: String, default: \'\' },
  address: { type: String, default: \'\' }
})

const mapEl = ref(null)
const loading = ref(true)
const error = ref(false)
let mapInstance = null

async function geocodeAddress(addr) {
  try {
    const url = \'https://nominatim.openstreetmap.org/search?format=json&limit=1&countrycodes=us&q=\' + encodeURIComponent(addr)
    const res = await fetch(url, { headers: { \'User-Agent\': \'SomeKorean/1.0\', \'Accept-Language\': \'ko,en\' } })
    const data = await res.json()
    if (data && data.length > 0) return { lat: parseFloat(data[0].lat), lng: parseFloat(data[0].lon) }
  } catch(e) { console.warn(\'Geocode error:\', e) }
  return null
}

onMounted(async () => {
  try {
    let lat = props.lat ? parseFloat(props.lat) : null
    let lng = props.lng ? parseFloat(props.lng) : null

    if (!lat || !lng || isNaN(lat) || isNaN(lng)) {
      if (!props.address) { error.value = true; loading.value = false; return }
      const coords = await geocodeAddress(props.address)
      if (!coords) { error.value = true; loading.value = false; return }
      lat = coords.lat; lng = coords.lng
    }

    loading.value = false
    await new Promise(r => setTimeout(r, 100))
    if (!mapEl.value) { error.value = true; return }

    // Dynamically import Leaflet
    const L = (await import(\'leaflet\')).default
    await import(\'leaflet/dist/leaflet.css\')

    // Fix marker icons using CDN (avoids bundler path issues)
    const iconBase = \'https://unpkg.com/leaflet@1.9.4/dist/images/\'
    const DefaultIcon = L.icon({
      iconUrl: iconBase + \'marker-icon.png\',
      iconRetinaUrl: iconBase + \'marker-icon-2x.png\',
      shadowUrl: iconBase + \'marker-shadow.png\',
      iconSize: [25, 41], iconAnchor: [12, 41],
      popupAnchor: [1, -34], shadowSize: [41, 41]
    })
    L.Marker.prototype.options.icon = DefaultIcon

    mapInstance = L.map(mapEl.value, { zoomControl: true, scrollWheelZoom: false }).setView([lat, lng], 15)
    L.tileLayer(\'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png\', {
      attribution: \'© <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>\',
      maxZoom: 19
    }).addTo(mapInstance)
    L.marker([lat, lng]).addTo(mapInstance)
      .bindPopup(`<strong>${props.name || props.address}</strong>`).openPopup()
  } catch(e) {
    console.error(\'LeafletMap error:\', e)
    error.value = true
    loading.value = false
  }
})

onUnmounted(() => {
  if (mapInstance) { mapInstance.remove(); mapInstance = null }
})
</script>
'''

print("\nWriting LeafletMap.vue...")
print(write_file('/var/www/somekorean/resources/js/components/LeafletMap.vue', leaflet_map))

print("\nAll fixes written. Running npm build...")
result = ssh('cd /var/www/somekorean && npm run build 2>&1', timeout=300)
# Show last 800 chars
lines = result.splitlines()
print('\n'.join(lines[-15:]))
c.close()
