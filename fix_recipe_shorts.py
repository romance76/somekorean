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

# ── 1. RecipeList.vue – Maangchi 완전 제거 ───────────────────────
print("=== 1. RecipeList.vue Maangchi 완전 제거 ===")
raw = ssh('base64 /var/www/somekorean/resources/js/pages/recipes/RecipeList.vue')
content = base64.b64decode(raw).decode('utf-8')

# Find and remove Maangchi block from template
# Look for the comment start
maangchi_comment = '<!-- Maangchi'
start = content.find(maangchi_comment)
if start >= 0:
    # Find the opening div before the comment
    div_start = content.rfind('\n      <div', 0, start)
    # Find the closing </div> of this block - count divs
    search_from = start
    depth = 0
    pos = search_from
    found_first = False
    while pos < len(content):
        if content[pos:pos+4] == '<div' or content[pos:pos+8] == '<template':
            depth += 1
            found_first = True
        elif content[pos:pos+6] == '</div>' or content[pos:pos+9] == '</template':
            if found_first:
                depth -= 1
                if depth == 0:
                    end_pos = pos + 6
                    break
        pos += 1
    removed = content[div_start:end_pos]
    print(f"Removing {len(removed)} chars: {repr(removed[:60])}")
    content = content[:div_start] + content[end_pos:]
    print("Maangchi block removed from template")
else:
    print("Maangchi comment not found")

# Remove from script: maangchiRecipes ref
for old, new in [
    ("const maangchiRecipes = ref([])\n", ""),
    ("const maangchiRecipes = ref([])\r\n", ""),
    ("  const maangchiRecipes = ref([])\n", ""),
]:
    if old in content:
        content = content.replace(old, new)
        print("maangchiRecipes ref removed")
        break

# Remove loadMaangchi function
import re
content = re.sub(
    r'\n?async function loadMaangchi\(\).*?catch\(e\) \{\}\n\}',
    '',
    content,
    flags=re.DOTALL
)
# Remove loadMaangchi() call
content = content.replace('  await loadMaangchi()\n', '')
content = content.replace('  await loadMaangchi()\r\n', '')

print("Script refs cleaned")
print("Final check - 'Maangchi' remaining:", 'Maangchi' in content)
print(write_file('/var/www/somekorean/resources/js/pages/recipes/RecipeList.vue', content))

# ── 2. ShortsHome.vue – 스크롤 한 칸씩 수정 ─────────────────────
print("\n=== 2. ShortsHome.vue 스크롤 수정 ===")
raw = ssh('base64 /var/www/somekorean/resources/js/pages/shorts/ShortsHome.vue')
shorts = base64.b64decode(raw).decode('utf-8')

# Replace the scroll/swipe/keyboard handlers with debounced versions
old_vh = "// ── 실제 모바일 뷰포트 높이 (주소창 제외) ──────────────────────"
new_vh = """// ── 슬라이드 전환 잠금 (연속 스크롤 방지) ──────────────────────
const isTransitioning = ref(false)

function lockThenGo(fn) {
  if (isTransitioning.value) return
  isTransitioning.value = true
  fn()
  // CSS transition이 0.38s이므로 400ms 후 잠금 해제
  setTimeout(() => { isTransitioning.value = false }, 420)
}

// ── 실제 모바일 뷰포트 높이 (주소창 제외) ──────────────────────"""

if old_vh in shorts:
    shorts = shorts.replace(old_vh, new_vh)
    print("isTransitioning lock added")
else:
    print("WARN: vh comment not found, trying alt")
    # Try adding before setVh function
    old2 = "function setVh() {"
    new2 = """// 슬라이드 전환 잠금
const isTransitioning = ref(false)
function lockThenGo(fn) {
  if (isTransitioning.value) return
  isTransitioning.value = true
  fn()
  setTimeout(() => { isTransitioning.value = false }, 420)
}

function setVh() {"""
    if old2 in shorts:
        shorts = shorts.replace(old2, new2)
        print("isTransitioning lock added (alt)")

# Fix onWheel - add lock
old_wheel = """function onWheel(e) {
  if (e.deltaY > 30) goNext()
  else if (e.deltaY < -30) goPrev()
}"""
new_wheel = """function onWheel(e) {
  if (e.deltaY > 30) lockThenGo(goNext)
  else if (e.deltaY < -30) lockThenGo(goPrev)
}"""
if old_wheel in shorts:
    shorts = shorts.replace(old_wheel, new_wheel)
    print("onWheel debounced")

# Fix onTouchEnd - add lock
old_touch = """function onTouchEnd() {
  const diff = touchStartY.value - touchLastY.value
  if (diff > 50) goNext()
  else if (diff < -50) goPrev()
  dragOffset.value = 0
}"""
new_touch = """function onTouchEnd() {
  const diff = touchStartY.value - touchLastY.value
  if (Math.abs(diff) > 50) {
    if (diff > 0) lockThenGo(goNext)
    else lockThenGo(goPrev)
  }
  dragOffset.value = 0
}"""
if old_touch in shorts:
    shorts = shorts.replace(old_touch, new_touch)
    print("onTouchEnd debounced")

# Fix onKeydown - add lock
old_key = """function onKeydown(e) {
  if (e.key === 'ArrowDown' || e.key === 'ArrowRight') goNext()
  if (e.key === 'ArrowUp'   || e.key === 'ArrowLeft')  goPrev()
}"""
new_key = """function onKeydown(e) {
  if (e.key === 'ArrowDown' || e.key === 'ArrowRight') lockThenGo(goNext)
  if (e.key === 'ArrowUp'   || e.key === 'ArrowLeft')  lockThenGo(goPrev)
}"""
if old_key in shorts:
    shorts = shorts.replace(old_key, new_key)
    print("onKeydown debounced")

# Also add isTransitioning to imports if ref not imported
if 'const isTransitioning = ref(' in shorts and "import { ref," not in shorts and "import { ref " not in shorts:
    print("ref already imported")

print(write_file('/var/www/somekorean/resources/js/pages/shorts/ShortsHome.vue', shorts))

# ── 3. Build ─────────────────────────────────────────────────────
print("\n=== 3. Building ===")
result = ssh('cd /var/www/somekorean && npm run build 2>&1', timeout=180)
lines = result.splitlines()
has_error = any('Error' in l for l in lines if 'WARN' not in l and 'ERR' not in l)
if has_error:
    for l in lines:
        if 'Error' in l and 'WARN' not in l:
            print(l)
print('\n'.join(lines[-6:]))
c.close()
