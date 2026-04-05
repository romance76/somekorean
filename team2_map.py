import paramiko, base64, sys
sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1)
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('68.183.60.70', username='root', password='EhdRh0817wodl', timeout=15)

def ssh(cmd, timeout=180):
    _, out, _ = c.exec_command(cmd, timeout=timeout)
    return out.read().decode('utf-8', errors='replace').strip()

def write_file(path, content):
    enc = base64.b64encode(content.encode('utf-8')).decode('ascii')
    chunks = [enc[i:i+2000] for i in range(0, len(enc), 2000)]
    ssh('rm -f /tmp/wf_chunk')
    for p in chunks:
        ssh(f"printf '%s' '{p}' >> /tmp/wf_chunk")
    ssh(f'cat /tmp/wf_chunk | base64 -d > {path} && rm -f /tmp/wf_chunk')
    print(f'Written {path}: {ssh(f"wc -c < {path}")} bytes')

# ============================================================
# Task 1: Install Leaflet
# ============================================================
print("=== Task 1: Installing Leaflet ===")
result = ssh('cd /var/www/somekorean && npm install leaflet --save 2>&1 | tail -5', timeout=120)
print(result)
verify = ssh('grep \'"leaflet"\' /var/www/somekorean/package.json')
print(f"Verify leaflet in package.json: {verify}")

# ============================================================
# Task 2: Create LeafletMap.vue component
# ============================================================
print("\n=== Task 2: Creating LeafletMap.vue ===")

leaflet_map_vue = '''<template>
  <div class="leaflet-map-wrapper">
    <div v-if="loading" class="map-loading">
      <div class="map-spinner"></div>
      <p>지도 불러오는 중...</p>
    </div>
    <div v-else-if="error" class="map-error">
      <p>📍 {{ address }}</p>
      <a :href="\'https://www.openstreetmap.org/search?query=\'+encodeURIComponent(address)"
         target="_blank" class="map-link">OpenStreetMap에서 보기 →</a>
    </div>
    <div v-else ref="mapEl" class="map-container"></div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch } from \'vue\'

const props = defineProps({
  lat: { type: Number, default: null },
  lng: { type: Number, default: null },
  name: { type: String, default: \'\' },
  address: { type: String, default: \'\' }
})

const mapEl = ref(null)
const loading = ref(true)
const error = ref(false)
let map = null
let L = null

async function geocodeAddress(addr) {
  const url = \'https://nominatim.openstreetmap.org/search?format=json&limit=1&countrycodes=us&q=\' + encodeURIComponent(addr)
  const res = await fetch(url, { headers: { \'Accept-Language\': \'ko,en\' } })
  const data = await res.json()
  if (data.length > 0) return { lat: parseFloat(data[0].lat), lng: parseFloat(data[0].lon) }
  return null
}

async function initMap(lat, lng) {
  if (!mapEl.value) return
  const leaflet = await import(\'leaflet\')
  await import(\'leaflet/dist/leaflet.css\')
  L = leaflet.default || leaflet
  // Fix default icon paths broken by bundlers
  delete L.Icon.Default.prototype._getIconUrl
  L.Icon.Default.mergeOptions({
    iconRetinaUrl: new URL(\'leaflet/dist/images/marker-icon-2x.png\', import.meta.url).href,
    iconUrl: new URL(\'leaflet/dist/images/marker-icon.png\', import.meta.url).href,
    shadowUrl: new URL(\'leaflet/dist/images/marker-shadow.png\', import.meta.url).href,
  })
  map = L.map(mapEl.value).setView([lat, lng], 15)
  L.tileLayer(\'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png\', {
    attribution: \'© <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors\',
    maxZoom: 19
  }).addTo(map)
  L.marker([lat, lng]).addTo(map).bindPopup(props.name || props.address).openPopup()
}

onMounted(async () => {
  try {
    let lat = props.lat, lng = props.lng
    if (!lat || !lng) {
      if (!props.address) { error.value = true; loading.value = false; return }
      const coords = await geocodeAddress(props.address)
      if (!coords) { error.value = true; loading.value = false; return }
      lat = coords.lat; lng = coords.lng
    }
    loading.value = false
    await new Promise(r => setTimeout(r, 50)) // wait for DOM
    await initMap(lat, lng)
  } catch (e) {
    console.error(\'Map error:\', e)
    error.value = true
    loading.value = false
  }
})

onUnmounted(() => {
  if (map) { map.remove(); map = null }
})
</script>

<style scoped>
.leaflet-map-wrapper { width: 100%; }
.map-container { width: 100%; height: 300px; border-radius: 12px; z-index: 0; }
.map-loading { display: flex; flex-direction: column; align-items: center; justify-content: center; height: 200px; color: #64748b; gap: 12px; }
.map-spinner { width: 32px; height: 32px; border: 3px solid #e2e8f0; border-top-color: #3b82f6; border-radius: 50%; animation: spin .8s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }
.map-error { padding: 24px; background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 12px; text-align: center; color: #64748b; }
.map-link { color: #3b82f6; text-decoration: underline; font-size: 14px; }
</style>
'''

write_file('/var/www/somekorean/resources/js/components/LeafletMap.vue', leaflet_map_vue)

# ============================================================
# Task 3: Read BusinessDetail.vue
# ============================================================
print("\n=== Task 3: Reading BusinessDetail.vue ===")
wc = ssh('wc -l /var/www/somekorean/resources/js/pages/directory/BusinessDetail.vue')
print(f"Line count: {wc}")
grep_result = ssh('grep -n "iframe\\|maps.google\\|maps/maps" /var/www/somekorean/resources/js/pages/directory/BusinessDetail.vue')
print(f"iframe/maps lines:\n{grep_result}")

# Read full file via base64
print("\nReading full file via base64...")
raw_b64 = ssh('base64 -w 0 /var/www/somekorean/resources/js/pages/directory/BusinessDetail.vue', timeout=60)
file_content = base64.b64decode(raw_b64).decode('utf-8')
print(f"File length: {len(file_content)} chars")

# ============================================================
# Task 4: Update BusinessDetail.vue
# ============================================================
print("\n=== Task 4: Updating BusinessDetail.vue ===")

# 1. Find and replace the iframe/map section
# Search for iframe block
import re

# Find the iframe section - look for a div containing an iframe with maps.google.com
# Common patterns: <div class="map..."> or <div v-if...> containing the iframe
print("Searching for iframe pattern...")

# Print lines around the iframe for debugging
lines = file_content.split('\n')
for i, line in enumerate(lines):
    if 'iframe' in line.lower() or 'maps.google' in line.lower():
        start = max(0, i-3)
        end = min(len(lines), i+4)
        print(f"Context around line {i+1}:")
        for j in range(start, end):
            print(f"  {j+1}: {lines[j]}")
        print()

# Strategy: find the iframe tag and its wrapping div
# Look for the full block to replace
iframe_pattern = re.compile(
    r'(\s*<div[^>]*class="[^"]*map[^"]*"[^>]*>\s*\n\s*<iframe[^\n]*maps\.google[^\n]*\n.*?</iframe>\s*\n\s*</div>)',
    re.DOTALL | re.IGNORECASE
)

# Also try simpler pattern - just the iframe line and its wrapper
iframe_pattern2 = re.compile(
    r'\s*<div[^>]*>\s*\n\s*<iframe[^>]*maps\.google\.com[^>]*/>\s*\n\s*</div>',
    re.DOTALL
)

# Most flexible: find from containing div to /iframe
iframe_pattern3 = re.compile(
    r'(\s*<div[^\n]*>\n\s*<iframe[^\n]*maps[^\n]*\n[^\n]*</iframe>\n[^\n]*</div>)',
    re.DOTALL
)

new_map_block = '''        <div v-if="biz.address || (biz.lat && biz.lng)" class="map-section">
          <LeafletMap :lat="biz.lat ? parseFloat(biz.lat) : null" :lng="biz.lng ? parseFloat(biz.lng) : null" :name="biz.name" :address="biz.address || ''" />
        </div>'''

# Try to find exactly where iframe is and replace
# First let's print the actual iframe line content
for i, line in enumerate(lines):
    if 'maps.google' in line or ('<iframe' in line and i > 0):
        print(f"Line {i+1}: [{line}]")

# Find the iframe block more carefully
updated_content = file_content

# Try pattern: look for div containing iframe with google maps
found = False

# Pattern: find the block starting with a div tag before the iframe through to </div>
# We'll use a line-by-line approach
new_lines = []
i = 0
while i < len(lines):
    line = lines[i]
    # Detect iframe line with maps.google
    if 'maps.google' in line and '<iframe' in line:
        print(f"Found iframe at line {i+1}: {line[:80]}...")
        # Walk backwards to find the opening div
        div_start = i
        for j in range(i-1, max(0, i-5), -1):
            if '<div' in lines[j]:
                div_start = j
                break
        # Walk forward to find the closing </div>
        div_end = i
        for j in range(i+1, min(len(lines), i+5)):
            if '</div>' in lines[j]:
                div_end = j
                break
        print(f"Replacing lines {div_start+1} to {div_end+1}")
        # Replace this block
        # Remove the old block lines
        # Don't add old lines, add the new block instead
        indent = len(lines[div_start]) - len(lines[div_start].lstrip())
        indent_str = ' ' * indent
        new_block_lines = [
            f'{indent_str}<div v-if="biz.address || (biz.lat && biz.lng)" class="map-section">',
            f'{indent_str}  <LeafletMap :lat="biz.lat ? parseFloat(biz.lat) : null" :lng="biz.lng ? parseFloat(biz.lng) : null" :name="biz.name" :address="biz.address || \'\'" />',
            f'{indent_str}</div>'
        ]
        new_lines.extend(new_block_lines)
        i = div_end + 1
        found = True
        continue
    new_lines.append(line)
    i += 1

if found:
    updated_content = '\n'.join(new_lines)
    print("iframe block replaced successfully")
else:
    print("WARNING: iframe block not found with line-by-line approach, trying regex...")
    # Try a more aggressive search
    m = re.search(r'<iframe[^>]*maps\.google[^>]*/>', file_content, re.DOTALL)
    if m:
        print(f"Found iframe at pos {m.start()}: {m.group()[:100]}")
        # Find the surrounding div
        before = file_content[:m.start()]
        after = file_content[m.end():]
        # Find last <div in before
        div_match = list(re.finditer(r'<div[^>]*>', before))
        if div_match:
            last_div = div_match[-1]
            # Find closing </div> after iframe
            close_match = re.search(r'</div>', after)
            if close_match:
                replace_start = last_div.start()
                replace_end = m.end() + close_match.end()
                old_block = file_content[replace_start:replace_end]
                print(f"Replacing block: {old_block[:100]}...")
                updated_content = file_content[:replace_start] + new_map_block + file_content[replace_end:]
                found = True

# 2. Add import for LeafletMap
if "import LeafletMap from '../../components/LeafletMap.vue'" not in updated_content:
    # Find the last import statement in script section
    last_import_match = None
    for m in re.finditer(r'^import .+', updated_content, re.MULTILINE):
        last_import_match = m
    if last_import_match:
        insert_pos = last_import_match.end()
        updated_content = (updated_content[:insert_pos] +
                          "\nimport LeafletMap from '../../components/LeafletMap.vue'" +
                          updated_content[insert_pos:])
        print("Added LeafletMap import")
    else:
        print("WARNING: Could not find import location")

# 3. Add claim banner - find review section or after map section
claim_banner = """
        <!-- 업소 소유권 클레임 배너 -->
        <div v-if="!biz.is_claimed" class="claim-banner">
          <div class="claim-text">
            <p class="claim-title">🏪 이 업소의 사장님이신가요?</p>
            <p class="claim-sub">업소 정보를 직접 관리하고 고객과 소통하세요.</p>
          </div>
          <router-link :to="'/directory/'+biz.id+'/claim'" class="claim-btn">
            내 업소 등록하기 →
          </router-link>
        </div>
        <div v-else-if="isOwner" class="owner-manage-banner">
          <router-link to="/my-business" class="manage-btn">📊 내 업소 관리하기</router-link>
        </div>"""

# Insert after map-section div or before review section
if 'claim-banner' not in updated_content:
    # Try to insert after the map-section div we just added
    map_section_end = updated_content.find('</div>', updated_content.find('class="map-section"'))
    if map_section_end != -1:
        insert_after = map_section_end + len('</div>')
        updated_content = updated_content[:insert_after] + claim_banner + updated_content[insert_after:]
        print("Added claim banner after map section")
    else:
        # Try inserting before </div></div> near end of template or before review section
        # Find a good anchor - look for review or comment section
        review_match = re.search(r'(<!-- 리뷰|<!-- review|class="review)', updated_content, re.IGNORECASE)
        if review_match:
            updated_content = updated_content[:review_match.start()] + claim_banner + '\n' + updated_content[review_match.start():]
            print("Added claim banner before review section")
        else:
            print("WARNING: Could not find good insertion point for claim banner")

# 4. Add stat tracking function
track_func = """
async function trackClick(type) {
  try { await axios.post('/api/businesses/' + biz.value.id + '/stat/' + type) } catch(e) {}
}"""

if 'trackClick' not in updated_content:
    # Insert before the last function or before </script>
    # Find a good spot - look for function declarations
    func_match = re.search(r'\nasync function ', updated_content)
    if func_match:
        updated_content = updated_content[:func_match.start()] + track_func + updated_content[func_match.start():]
        print("Added trackClick function")
    else:
        # Before closing </script>
        script_end = updated_content.rfind('</script>')
        if script_end != -1:
            updated_content = updated_content[:script_end] + track_func + '\n' + updated_content[script_end:]
            print("Added trackClick function before </script>")

# 5. Add @click="trackClick" to direction/phone/website buttons
# Direction button
if 'trackClick' in updated_content:
    # Find direction button - look for "길찾기" or "direction" button
    dir_patterns = [
        (r'(href="https://www\.google\.com/maps[^"]*")', r'\1 @click="trackClick(\'direction\')"'),
        (r'(<a[^>]*(?:direction|길찾기)[^>]*)(>)', r'\1 @click="trackClick(\'direction\')">\2'),
    ]
    # More targeted: find button/link with direction-related content
    # Look for google maps link in template
    maps_link = re.search(r'(href="https://(?:www\.)?google\.com/maps[^"]*")', updated_content)
    if maps_link:
        old = maps_link.group(0)
        new = old.replace('href=', '@click="trackClick(\'direction\')" href=')
        updated_content = updated_content.replace(old, new, 1)
        print("Added trackClick to direction link")

    # Phone link - tel: link
    phone_link = re.search(r'(href="tel:[^"]*")', updated_content)
    if phone_link:
        old = phone_link.group(0)
        new = old.replace('href=', '@click="trackClick(\'phone\')" href=')
        updated_content = updated_content.replace(old, new, 1)
        print("Added trackClick to phone link")

    # Website link
    website_link = re.search(r'(href="(?:https?://)[^"]*"[^>]*>(?:[^<]*(?:홈페이지|website|웹사이트|사이트)[^<]*)<)', updated_content, re.IGNORECASE)
    if website_link:
        old = website_link.group(0)
        if 'trackClick' not in old:
            new = old.replace('href=', '@click="trackClick(\'website\')" href=')
            updated_content = updated_content.replace(old, new, 1)
            print("Added trackClick to website link")
    else:
        # Try finding biz.website link
        website_match = re.search(r'(:href="biz\.website"[^>]*>)', updated_content)
        if website_match:
            old = website_match.group(0)
            # Find the full a tag
            a_start = updated_content.rfind('<a', 0, website_match.start())
            a_tag_end = website_match.end()
            old_a = updated_content[a_start:a_tag_end]
            if 'trackClick' not in old_a:
                new_a = old_a.replace('<a ', '<a @click="trackClick(\'website\')" ', 1)
                updated_content = updated_content[:a_start] + new_a + updated_content[a_start+len(old_a):]
                print("Added trackClick to website link (biz.website)")

# 6. Add CSS
new_css = """
.claim-banner { display:flex; justify-content:space-between; align-items:center; background:#eff6ff; border:1px solid #bfdbfe; border-radius:14px; padding:16px 20px; margin:16px 0; gap:12px; flex-wrap:wrap; }
.claim-title { font-size:15px; font-weight:700; color:#1e40af; margin:0 0 4px; }
.claim-sub { font-size:13px; color:#3b82f6; margin:0; }
.claim-btn { background:#2563eb; color:#fff; padding:10px 20px; border-radius:10px; font-size:14px; font-weight:700; text-decoration:none; white-space:nowrap; }
.owner-manage-banner { background:#f0fdf4; border:1px solid #bbf7d0; border-radius:14px; padding:14px 20px; margin:16px 0; }
.manage-btn { color:#16a34a; font-weight:700; text-decoration:none; }
.map-section { margin:16px 0; }"""

if 'claim-banner' in updated_content and '.claim-banner {' not in updated_content:
    # Find </style> and insert before it
    style_end = updated_content.rfind('</style>')
    if style_end != -1:
        updated_content = updated_content[:style_end] + new_css + '\n' + updated_content[style_end:]
        print("Added CSS for claim banner and map section")
    else:
        print("WARNING: </style> not found")

# 7. Add isOwner computed
if 'isOwner' not in updated_content:
    # Find authStore or computed imports
    computed_match = re.search(r'const (\w+) = computed\(', updated_content)
    if computed_match:
        # Insert before first computed
        insert_pos = computed_match.start()
        updated_content = (updated_content[:insert_pos] +
                          "const isOwner = computed(() => authStore.user && biz.value && biz.value.owner_user_id === authStore.user.id)\n" +
                          updated_content[insert_pos:])
        print("Added isOwner computed")
    else:
        # Check if computed is imported
        if 'computed' in updated_content:
            # Find a good place after reactive declarations
            biz_val_match = re.search(r'const biz = ', updated_content)
            if biz_val_match:
                # Find end of that line
                line_end = updated_content.find('\n', biz_val_match.start())
                updated_content = (updated_content[:line_end+1] +
                                  "const isOwner = computed(() => authStore.user && biz.value && biz.value.owner_user_id === authStore.user.id)\n" +
                                  updated_content[line_end+1:])
                print("Added isOwner computed after biz declaration")
        else:
            print("WARNING: computed not found in imports, may need to add manually")

# Check if computed is in imports, add if needed
if 'isOwner' in updated_content and 'computed' not in updated_content:
    updated_content = updated_content.replace(
        "import { ref,",
        "import { ref, computed,"
    ).replace(
        "import { ref ",
        "import { ref, computed "
    )
    print("Added computed to Vue imports")

# Write updated file
write_file('/var/www/somekorean/resources/js/pages/directory/BusinessDetail.vue', updated_content)

print("\nVerification of BusinessDetail.vue changes:")
checks = {
    'LeafletMap import': "import LeafletMap from '../../components/LeafletMap.vue'",
    'map-section div': 'class="map-section"',
    'LeafletMap usage': '<LeafletMap',
    'claim-banner': 'claim-banner',
    'trackClick function': 'async function trackClick',
    'isOwner computed': 'isOwner',
    'claim-banner CSS': '.claim-banner {',
}
for name, pattern in checks.items():
    found_check = pattern in updated_content
    print(f"  {'OK' if found_check else 'MISSING'}: {name}")

print("\nDone with Task 4")
