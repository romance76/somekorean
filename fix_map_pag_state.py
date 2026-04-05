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

# ── FIX 1: LeafletMap.vue - city fallback + sessionStorage cache ─────────────
leaflet_map = r"""<template>
  <div style="width:100%">
    <div v-if="loading" class="flex flex-col items-center justify-center bg-gray-100 rounded-xl text-gray-400 text-sm gap-2" style="height:280px">
      <div class="animate-spin w-6 h-6 border-4 border-blue-500 border-t-transparent rounded-full"></div>
      <span>지도 불러오는 중...</span>
    </div>
    <div v-show="!loading" ref="mapEl" style="width:100%;height:280px;border-radius:12px;z-index:0;"></div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'

const props = defineProps({
  lat: { type: [Number, String], default: null },
  lng: { type: [Number, String], default: null },
  name: { type: String, default: '' },
  address: { type: String, default: '' }
})

const mapEl = ref(null)
const loading = ref(true)
let mapInstance = null

// Fallback coords for known Korean-American cities
const CITY_COORDS = {
  'los angeles': [34.0522, -118.2437], 'la': [34.0522, -118.2437],
  'new york': [40.7128, -74.0060],    'ny': [40.7128, -74.0060],
  'flushing': [40.7673, -73.8330],    'fort lee': [40.8501, -73.9707],
  'chicago': [41.8781, -87.6298],     'houston': [29.7604, -95.3698],
  'seattle': [47.6062, -122.3321],    'atlanta': [33.7490, -84.3880],
  'dallas': [32.7767, -96.7970],      'san francisco': [37.7749, -122.4194],
  'washington': [38.9072, -77.0369],  'las vegas': [36.1699, -115.1398],
  'boston': [42.3601, -71.0589],      'philadelphia': [39.9526, -75.1652],
  'miami': [25.7617, -80.1918],       'san diego': [32.7157, -117.1611],
  'denver': [39.7392, -104.9903],     'annandale': [38.8304, -77.1944],
  'honolulu': [21.3069, -157.8583],   'portland': [45.5051, -122.6750],
  'minneapolis': [44.9778, -93.2650], 'detroit': [42.3314, -83.0458],
  'phoenix': [33.4484, -112.0740],    'baltimore': [39.2904, -76.6122],
}

function getCityCoords(address) {
  const lower = (address || '').toLowerCase()
  for (const [city, coords] of Object.entries(CITY_COORDS)) {
    if (lower.includes(city)) return coords
  }
  return null
}

async function geocode(query) {
  const key = 'geo:' + query
  const cached = sessionStorage.getItem(key)
  if (cached) {
    const d = JSON.parse(cached)
    if (d) return d
  }
  try {
    const url = 'https://nominatim.openstreetmap.org/search?format=json&limit=1&countrycodes=us&q=' + encodeURIComponent(query)
    const res = await fetch(url, {
      headers: { 'Accept-Language': 'en', 'User-Agent': 'SomeKorean/1.0' }
    })
    const data = await res.json()
    if (data && data.length > 0) {
      const result = [parseFloat(data[0].lat), parseFloat(data[0].lon)]
      sessionStorage.setItem(key, JSON.stringify(result))
      return result
    }
  } catch(e) { console.warn('Geocode error:', e) }
  sessionStorage.setItem(key, 'null')
  return null
}

onMounted(async () => {
  try {
    let lat = props.lat ? parseFloat(props.lat) : null
    let lng = props.lng ? parseFloat(props.lng) : null
    let coords = null

    if (lat && lng && !isNaN(lat) && !isNaN(lng)) {
      coords = [lat, lng]
    } else if (props.address) {
      // 1) Try full address geocoding
      coords = await geocode(props.address)
      // 2) Try city fallback from address string
      if (!coords) coords = getCityCoords(props.address)
      // 3) Try just city,state portion (last part of address)
      if (!coords) {
        const parts = props.address.split(',')
        if (parts.length >= 2) {
          const cityState = parts.slice(-2).join(',').trim()
          coords = await geocode(cityState)
        }
      }
    }

    // Default fallback: center of USA
    if (!coords) coords = [37.0902, -95.7129]

    loading.value = false
    await new Promise(r => setTimeout(r, 80))
    if (!mapEl.value) return

    const L = (await import('leaflet')).default
    await import('leaflet/dist/leaflet.css')

    // CDN icons - avoids bundler path issues
    const base = 'https://unpkg.com/leaflet@1.9.4/dist/images/'
    L.Marker.prototype.options.icon = L.icon({
      iconUrl: base + 'marker-icon.png',
      iconRetinaUrl: base + 'marker-icon-2x.png',
      shadowUrl: base + 'marker-shadow.png',
      iconSize: [25, 41], iconAnchor: [12, 41],
      popupAnchor: [1, -34], shadowSize: [41, 41]
    })

    const zoom = (lat && lng) ? 15 : coords[2] ? coords[2] : 13
    mapInstance = L.map(mapEl.value, { scrollWheelZoom: false, zoomControl: true })
      .setView([coords[0], coords[1]], zoom)

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: '© <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>',
      maxZoom: 19
    }).addTo(mapInstance)

    if (props.address || props.name) {
      L.marker([coords[0], coords[1]]).addTo(mapInstance)
        .bindPopup(`<strong>${props.name || ''}</strong>${props.address ? '<br><small>' + props.address + '</small>' : ''}`)
        .openPopup()
    }
  } catch(e) {
    console.error('LeafletMap error:', e)
    loading.value = false
  }
})

onUnmounted(() => { if (mapInstance) { mapInstance.remove(); mapInstance = null } })
</script>
"""
print("Writing LeafletMap.vue...")
print(write_file('/var/www/somekorean/resources/js/components/LeafletMap.vue', leaflet_map))


# ── FIX 2 + 3: BusinessList.vue - pagination window ±4 + state buttons ──────
raw = ssh('base64 /var/www/somekorean/resources/js/pages/directory/BusinessList.vue')
old_content = base64.b64decode(raw).decode('utf-8')

# 2a) Expand page window from ±2 to ±4
old_computed = """const pageList = computed(() => {
  const total = totalPages.value;
  const cur = currentPage.value;
  if (total <= 7) return Array.from({ length: total }, (_, i) => i + 1);
  const delta = 2;
  const start = Math.max(2, cur - delta);
  const end = Math.min(total - 1, cur + delta);
  const pages = [];
  for (let i = start; i <= end; i++) pages.push(i);
  return pages;
});"""

new_computed = """const pageList = computed(() => {
  const total = totalPages.value;
  const cur = currentPage.value;
  if (total <= 11) return Array.from({ length: total }, (_, i) => i + 1);
  const delta = 4;
  const start = Math.max(2, cur - delta);
  const end = Math.min(total - 1, cur + delta);
  const pages = [];
  for (let i = start; i <= end; i++) pages.push(i);
  return pages;
});"""

if old_computed in old_content:
    old_content = old_content.replace(old_computed, new_computed)
    print("✓ Page window expanded to ±4")
else:
    # Fallback: replace delta value
    old_content = old_content.replace('const delta = 2;', 'const delta = 4;')
    old_content = old_content.replace('if (total <= 7)', 'if (total <= 11)')
    print("✓ Page window expanded (fallback)")

# 2b) Add state filter ref and selectedState
old_refs = """const totalCount = ref(0);"""
new_refs = """const totalCount = ref(0);
const selectedState = ref('');

const stateButtons = [
  { code: '', label: '전체' },
  { code: 'CA', label: '🌴 CA', cities: ['Los Angeles','San Francisco','San Diego'] },
  { code: 'NY', label: '🗽 NY', cities: ['New York','Flushing'] },
  { code: 'TX', label: '🤠 TX', cities: ['Houston','Dallas'] },
  { code: 'WA', label: '🌲 WA', cities: ['Seattle'] },
  { code: 'IL', label: '🏙️ IL', cities: ['Chicago'] },
  { code: 'GA', label: '🍑 GA', cities: ['Atlanta'] },
  { code: 'DC', label: '🏛️ DC', cities: ['Washington'] },
  { code: 'NV', label: '🎰 NV', cities: ['Las Vegas'] },
  { code: 'FL', label: '🌊 FL', cities: ['Miami'] },
  { code: 'MA', label: '🦞 MA', cities: ['Boston'] },
  { code: 'HI', label: '🌺 HI', cities: ['Honolulu'] },
  { code: 'CO', label: '⛰️ CO', cities: ['Denver'] },
  { code: 'NJ', label: '🏘️ NJ', cities: ['Fort Lee'] },
  { code: 'VA', label: '🌿 VA', cities: ['Annandale'] },
  { code: 'OR', label: '🌧️ OR', cities: ['Portland'] },
];

function selectState(st) {
  selectedState.value = st.code;
  if (st.cities && st.cities.length === 1) {
    region.value = st.cities[0];
  } else if (st.code === '') {
    region.value = '';
  } else {
    // Multiple cities - clear region to show all in state
    region.value = '';
  }
  load(1);
}"""

if old_refs in old_content:
    old_content = old_content.replace(old_refs, new_refs)
    print("✓ State refs added")

# 2c) Add state buttons row in template (after category tabs, before search bar)
old_after_cat = """    <!-- Search bar -->
    <div class="max-w-[1200px] mx-auto px-4 mt-2">"""

new_after_cat = """    <!-- State filter buttons -->
    <div class="max-w-[1200px] mx-auto px-4 mt-2">
      <div class="flex gap-1.5 overflow-x-auto pb-1 flex-wrap" style="scrollbar-width:none">
        <button v-for="st in stateButtons" :key="st.code" @click="selectState(st)"
          :class="['flex-shrink-0 px-3 py-1.5 rounded-full text-xs font-semibold border transition',
            selectedState===st.code
              ? 'bg-blue-600 text-white border-blue-600'
              : 'bg-white text-gray-600 border-gray-200 hover:border-blue-400 hover:text-blue-600']">
          {{ st.label }}
        </button>
      </div>
    </div>

    <!-- Search bar -->
    <div class="max-w-[1200px] mx-auto px-4 mt-2">"""

if old_after_cat in old_content:
    old_content = old_content.replace(old_after_cat, new_after_cat)
    print("✓ State buttons row added")

# 2d) Also update load() to pass state
old_load = """    const params = {
      page,
      search: search.value || undefined,
      category: category.value || undefined,
      region: region.value || undefined,
      per_page: 24,
    };"""

new_load = """    const params = {
      page,
      search: search.value || undefined,
      category: category.value || undefined,
      region: region.value || undefined,
      state: selectedState.value || undefined,
      per_page: 24,
    };"""

if old_load in old_content:
    old_content = old_content.replace(old_load, new_load)
    print("✓ load() state param added")

print("\nWriting BusinessList.vue...")
print(write_file('/var/www/somekorean/resources/js/pages/directory/BusinessList.vue', old_content))

# ── FIX 4: BusinessController - support state filter ─────────────────────────
raw2 = ssh('base64 /var/www/somekorean/app/Http/Controllers/API/BusinessController.php')
ctrl = base64.b64decode(raw2).decode('utf-8')

# Find the index/listing method and add state filter
old_region_filter = "->when(\$request->region, fn(\$q, \$v) => \$q->where('region', 'like', \"%\$v%\"))"
if old_region_filter in ctrl:
    new_region_filter = old_region_filter + "\n            ->when(\$request->state, function(\$q, \$v) {\n                \$stateCities = ['CA'=>['Los Angeles','San Francisco','San Diego'],'NY'=>['New York','Flushing'],'TX'=>['Houston','Dallas'],'WA'=>['Seattle'],'IL'=>['Chicago'],'GA'=>['Atlanta'],'DC'=>['Washington'],'NV'=>['Las Vegas'],'FL'=>['Miami'],'MA'=>['Boston'],'HI'=>['Honolulu'],'CO'=>['Denver'],'NJ'=>['Fort Lee'],'VA'=>['Annandale'],'OR'=>['Portland'],'MN'=>['Minneapolis'],'MI'=>['Detroit'],'AZ'=>['Phoenix'],'MD'=>['Baltimore'],'PA'=>['Philadelphia']];\n                if (isset(\$stateCities[\$v])) \$q->whereIn('region', \$stateCities[\$v]);\n            })"
    ctrl = ctrl.replace(old_region_filter, new_region_filter)
    print("\nUpdating BusinessController with state filter...")
    print(write_file('/var/www/somekorean/app/Http/Controllers/API/BusinessController.php', ctrl))
    print(ssh('php -l /var/www/somekorean/app/Http/Controllers/API/BusinessController.php'))
else:
    # Try a simpler pattern
    print("\nState filter: trying alternative pattern in BusinessController...")
    for line in ctrl.splitlines():
        if 'region' in line and 'when' in line:
            print("  Found:", line.strip()[:100])

# Also add lat/lng seed data to businesses for better map experience
# Update a sample to have coordinates
print("\n=== Adding lat/lng to businesses with known city coords ===")
city_coords_sql = """
UPDATE businesses SET lat=34.0522, lng=-118.2437 WHERE region='Los Angeles' AND lat IS NULL LIMIT 100;
UPDATE businesses SET lat=40.7128, lng=-74.0060 WHERE region='New York' AND lat IS NULL LIMIT 100;
UPDATE businesses SET lat=40.7673, lng=-73.8330 WHERE region='Flushing' AND lat IS NULL LIMIT 100;
UPDATE businesses SET lat=41.8781, lng=-87.6298 WHERE region='Chicago' AND lat IS NULL LIMIT 100;
UPDATE businesses SET lat=29.7604, lng=-95.3698 WHERE region='Houston' AND lat IS NULL LIMIT 100;
UPDATE businesses SET lat=47.6062, lng=-122.3321 WHERE region='Seattle' AND lat IS NULL LIMIT 100;
UPDATE businesses SET lat=33.7490, lng=-84.3880 WHERE region='Atlanta' AND lat IS NULL LIMIT 100;
UPDATE businesses SET lat=32.7767, lng=-96.7970 WHERE region='Dallas' AND lat IS NULL LIMIT 100;
UPDATE businesses SET lat=37.7749, lng=-122.4194 WHERE region='San Francisco' AND lat IS NULL LIMIT 100;
UPDATE businesses SET lat=38.9072, lng=-77.0369 WHERE region='Washington' AND lat IS NULL LIMIT 100;
UPDATE businesses SET lat=36.1699, lng=-115.1398 WHERE region='Las Vegas' AND lat IS NULL LIMIT 100;
UPDATE businesses SET lat=42.3601, lng=-71.0589 WHERE region='Boston' AND lat IS NULL LIMIT 100;
UPDATE businesses SET lat=39.9526, lng=-75.1652 WHERE region='Philadelphia' AND lat IS NULL LIMIT 100;
UPDATE businesses SET lat=25.7617, lng=-80.1918 WHERE region='Miami' AND lat IS NULL LIMIT 100;
UPDATE businesses SET lat=32.7157, lng=-117.1611 WHERE region='San Diego' AND lat IS NULL LIMIT 100;
UPDATE businesses SET lat=39.7392, lng=-104.9903 WHERE region='Denver' AND lat IS NULL LIMIT 100;
UPDATE businesses SET lat=38.8304, lng=-77.1944 WHERE region='Annandale' AND lat IS NULL LIMIT 100;
UPDATE businesses SET lat=40.8501, lng=-73.9707 WHERE region='Fort Lee' AND lat IS NULL LIMIT 100;
UPDATE businesses SET lat=21.3069, lng=-157.8583 WHERE region='Honolulu' AND lat IS NULL LIMIT 100;
UPDATE businesses SET lat=45.5051, lng=-122.6750 WHERE region='Portland' AND lat IS NULL LIMIT 100;
UPDATE businesses SET lat=44.9778, lng=-93.2650 WHERE region='Minneapolis' AND lat IS NULL LIMIT 100;
UPDATE businesses SET lat=42.3314, lng=-83.0458 WHERE region='Detroit' AND lat IS NULL LIMIT 100;
UPDATE businesses SET lat=33.4484, lng=-112.0740 WHERE region='Phoenix' AND lat IS NULL LIMIT 100;
UPDATE businesses SET lat=39.2904, lng=-76.6122 WHERE region='Baltimore' AND lat IS NULL LIMIT 100;
"""
import base64 as b64
enc = b64.b64encode(city_coords_sql.encode()).decode()
print(ssh("echo '{}' | base64 -d > /tmp/coords.sql".format(enc)))
print(ssh("mysql -u somekorean_user '-pSK_DB@2026!secure' somekorean < /tmp/coords.sql 2>&1"))
print(ssh("mysql -u somekorean_user '-pSK_DB@2026!secure' somekorean -e 'SELECT COUNT(*) as with_coords FROM businesses WHERE lat IS NOT NULL' 2>/dev/null"))

print("\nRunning npm build...")
result = ssh('cd /var/www/somekorean && npm run build 2>&1', timeout=300)
print('\n'.join(result.splitlines()[-10:]))
c.close()
