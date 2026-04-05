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

# ============================================================
# Task 5: Add trackStat to BusinessController.php
# ============================================================
print("=== Task 5: BusinessController.php ===")
raw_b64 = ssh('base64 -w 0 /var/www/somekorean/app/Http/Controllers/API/BusinessController.php', timeout=60)
controller = base64.b64decode(raw_b64).decode('utf-8')
print(f"File length: {len(controller)} chars")

# Check if trackStat already exists
if 'trackStat' in controller:
    print("trackStat already exists in controller")
else:
    # New method to add
    track_stat_method = '''
    public function trackStat(Request $request, $id)
    {
        $type = $request->route('type'); // phone, direction, website, view
        $col = match($type) {
            'phone' => 'phone_clicks',
            'direction' => 'direction_clicks',
            'website' => 'website_clicks',
            default => 'views'
        };
        $today = now()->toDateString();
        \\DB::table('business_stats')->updateOrInsert(
            ['business_id' => $id, 'stat_date' => $today],
            [$col => \\DB::raw($col . ' + 1'), 'updated_at' => now()]
        );
        return response()->json(['ok' => true]);
    }'''

    # Find a good insertion point - before the last closing brace of the class
    # Find the show() method to insert after it
    show_match = re.search(r'public function show\(', controller)
    if show_match:
        # Find the end of the show() method
        # Count braces after show(
        pos = show_match.start()
        # Find the next complete method or end of class
        # Look for the next 'public function' or end of class
        next_method = re.search(r'\n    public function ', controller[show_match.end():])
        if next_method:
            insert_pos = show_match.end() + next_method.start()
            controller = controller[:insert_pos] + track_stat_method + '\n' + controller[insert_pos:]
            print("Inserted trackStat after show() method")
        else:
            # Insert before last closing brace
            last_brace = controller.rfind('}')
            controller = controller[:last_brace] + track_stat_method + '\n' + controller[last_brace:]
            print("Inserted trackStat before last closing brace")
    else:
        # Insert before last closing brace
        last_brace = controller.rfind('}')
        controller = controller[:last_brace] + track_stat_method + '\n' + controller[last_brace:]
        print("Inserted trackStat before last closing brace (show not found)")

    write_file('/var/www/somekorean/app/Http/Controllers/API/BusinessController.php', controller)

    # Verify
    if 'trackStat' in controller:
        print("OK: trackStat method added")
    else:
        print("WARNING: trackStat not found in updated controller")

# ============================================================
# Task 6: Create ROUTES_TO_ADD.md
# ============================================================
print("\n=== Task 6: Creating ROUTES_TO_ADD.md ===")

routes_content = """# Routes to add to api.php (Team 6)
Route::post('businesses/{id}/stat/{type}', [BusinessController::class, 'trackStat']);

# Routes to add to router/index.js (Team 6)
{ path: '/directory/:id/claim', component: () => import('../pages/directory/ClaimBusiness.vue'), name: 'claim-business' }
{ path: '/my-business', component: () => import('../pages/owner/OwnerDashboard.vue'), name: 'my-business', meta: { auth: true } }
"""

write_file('/var/www/somekorean/ROUTES_TO_ADD.md', routes_content)

# ============================================================
# Task 7: Final Verification
# ============================================================
print("\n=== Task 7: Final Verification ===")

# Check LeafletMap.vue
lm_size = ssh('wc -c < /var/www/somekorean/resources/js/components/LeafletMap.vue')
print(f"LeafletMap.vue: {lm_size} bytes")

# Check leaflet in package.json
leaflet_pkg = ssh('grep \'"leaflet"\' /var/www/somekorean/package.json')
print(f"leaflet in package.json: {leaflet_pkg}")

# Check BusinessDetail.vue key patterns
bd_checks = ssh('''grep -c "LeafletMap\\|map-section\\|claim-banner\\|trackClick\\|isOwner" /var/www/somekorean/resources/js/pages/directory/BusinessDetail.vue''')
print(f"BusinessDetail.vue pattern matches: {bd_checks}")

# Confirm no google maps iframe
no_iframe = ssh('grep -c "maps.google" /var/www/somekorean/resources/js/pages/directory/BusinessDetail.vue || echo "0"')
print(f"maps.google occurrences in BusinessDetail.vue: {no_iframe} (should be 0)")

# Check BusinessController.php
controller_check = ssh('grep -n "trackStat" /var/www/somekorean/app/Http/Controllers/API/BusinessController.php')
print(f"trackStat in BusinessController: {controller_check}")

# Check ROUTES_TO_ADD.md
routes_check = ssh('cat /var/www/somekorean/ROUTES_TO_ADD.md')
print(f"ROUTES_TO_ADD.md:\n{routes_check}")

print("\n=== All Tasks Complete ===")
