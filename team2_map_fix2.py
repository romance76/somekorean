import paramiko, base64, sys, re
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

# Read current file
raw_b64 = ssh('base64 -w 0 /var/www/somekorean/resources/js/pages/directory/BusinessDetail.vue', timeout=60)
content = base64.b64decode(raw_b64).decode('utf-8')

lines = content.split('\n')

# ---- Fix 1: Replace iframe block (lines 120-127) ----
# The block is: lines 120-127 (0-indexed: 119-126 + possibly 127=empty)
# Line 120: <!-- 구글 맵 -->
# Line 121: <div v-if="biz.address" ...>
# Line 122-126: <iframe ... </iframe>
# Line 127: </div>
# We want to replace the entire block (comment + div + iframe + /div) with the new map-section

# Find the line with the comment "구글 맵"
comment_line = -1
div_start = -1
div_end = -1

for i, line in enumerate(lines):
    if '구글 맵' in line or 'Google Maps' in line.lower():
        comment_line = i
        print(f"Found map comment at line {i+1}")
    if comment_line >= 0 and '<div' in line and div_start < 0 and i > comment_line:
        div_start = i
        print(f"Found div start at line {i+1}")
    if div_start >= 0 and '</div>' in line and div_end < 0 and i > div_start:
        div_end = i
        print(f"Found div end at line {i+1}")
        break

print(f"Replacing lines {comment_line+1} to {div_end+1}")
print("Content being replaced:")
for j in range(comment_line, div_end+1):
    print(f"  {j+1}: {lines[j]}")

# Determine indentation from div_start line
indent = len(lines[div_start]) - len(lines[div_start].lstrip())
indent_str = ' ' * indent

new_map_lines = [
    f"{indent_str}<!-- Leaflet 지도 -->",
    f"{indent_str}<div v-if=\"biz.address || (biz.lat && biz.lng)\" class=\"map-section\">",
    f"{indent_str}  <LeafletMap :lat=\"biz.lat ? parseFloat(biz.lat) : null\" :lng=\"biz.lng ? parseFloat(biz.lng) : null\" :name=\"biz.name\" :address=\"biz.address || ''\" />",
    f"{indent_str}</div>"
]

# Replace the block
new_lines = lines[:comment_line] + new_map_lines + lines[div_end+1:]
content = '\n'.join(new_lines)
print(f"\nAfter replacement - file has {content.count(chr(10))} lines")

# Verify replacement
if 'maps.google' not in content and 'map-section' in content and '<LeafletMap' in content:
    print("OK: iframe replaced with LeafletMap")
else:
    print(f"WARNING: iframe still present: {'maps.google' in content}")
    print(f"  map-section present: {'map-section' in content}")
    print(f"  LeafletMap present: {'<LeafletMap' in content}")

# ---- Fix 2: Add CSS ----
# Find the end of the file - look for </style> or add it
new_css = """.claim-banner { display:flex; justify-content:space-between; align-items:center; background:#eff6ff; border:1px solid #bfdbfe; border-radius:14px; padding:16px 20px; margin:16px 0; gap:12px; flex-wrap:wrap; }
.claim-title { font-size:15px; font-weight:700; color:#1e40af; margin:0 0 4px; }
.claim-sub { font-size:13px; color:#3b82f6; margin:0; }
.claim-btn { background:#2563eb; color:#fff; padding:10px 20px; border-radius:10px; font-size:14px; font-weight:700; text-decoration:none; white-space:nowrap; }
.owner-manage-banner { background:#f0fdf4; border:1px solid #bbf7d0; border-radius:14px; padding:14px 20px; margin:16px 0; }
.manage-btn { color:#16a34a; font-weight:700; text-decoration:none; }
.map-section { margin:16px 0; }"""

# Check if there's a <style> tag
style_idx = content.find('<style')
style_end_idx = content.find('</style>')
print(f"\nStyle tag at pos: {style_idx}, </style> at pos: {style_end_idx}")

if style_end_idx != -1:
    content = content[:style_end_idx] + new_css + '\n' + content[style_end_idx:]
    print("Added CSS before </style>")
elif style_idx != -1:
    # style tag exists but no closing? strange
    print("WARNING: <style> found but </style> not found")
else:
    # No style section at all - add at end of file
    content = content.rstrip() + '\n\n<style scoped>\n' + new_css + '\n</style>\n'
    print("Added <style scoped> section at end of file")

# Verify CSS
if '.claim-banner {' in content:
    print("OK: CSS added")
else:
    print("WARNING: CSS not found in content")

# Print last 30 lines to verify
lines_check = content.split('\n')
print("\nLast 30 lines of file:")
for i in range(max(0, len(lines_check)-30), len(lines_check)):
    print(f"{i+1}: {lines_check[i]}")

# Write the fixed file
write_file('/var/www/somekorean/resources/js/pages/directory/BusinessDetail.vue', content)

# Final verification
print("\n=== Final Verification ===")
checks = {
    'LeafletMap import': "import LeafletMap from '../../components/LeafletMap.vue'",
    'map-section div': 'class="map-section"',
    'LeafletMap usage': '<LeafletMap',
    'claim-banner': 'claim-banner',
    'trackClick function': 'async function trackClick',
    'isOwner computed': 'isOwner',
    'claim-banner CSS': '.claim-banner {',
    'map-section CSS': '.map-section {',
    'NO iframe': 'maps.google' not in content,
}
for name, check in checks.items():
    if isinstance(check, bool):
        print(f"  {'OK' if check else 'FAIL'}: {name}")
    else:
        found = check in content
        print(f"  {'OK' if found else 'MISSING'}: {name}")
