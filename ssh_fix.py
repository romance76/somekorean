import paramiko

HOST = "68.183.60.70"
USER = "root"
PASS = "EhdRh0817wodl"
APP = "/var/www/somekorean"

def ssh_cmd(client, cmd):
    stdin, stdout, stderr = client.exec_command(cmd, timeout=30)
    out = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    return out, err

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(HOST, username=USER, password=PASS, timeout=15)

# ─── FIX 1: getShorts() - add platform/status filter ─────────────────────────
print("=== FIX 1: Add platform/status filter to getShorts() ===")

old_getshorts = r"""    public function getShorts(Request $req)
    {
        try {
            $q = DB::table('shorts')
                ->leftJoin('users', 'shorts.user_id', '=', 'users.id')
                ->select('shorts.*', 'users.name as user_name')
                ->orderByDesc('shorts.created_at');
            if ($req->search) {
                $q->where('shorts.title', 'like', "%{$req->search}%");
            }
            return response()->json($q->paginate(15));
        } catch (\Exception $e) {
            return response()->json(['data' => [], 'total' => 0]);
        }
    }"""

new_getshorts = r"""    public function getShorts(Request $req)
    {
        try {
            $q = DB::table('shorts')
                ->leftJoin('users', 'shorts.user_id', '=', 'users.id')
                ->select('shorts.*', 'users.name as user_name')
                ->orderByDesc('shorts.created_at');
            if ($req->search) {
                $q->where('shorts.title', 'like', "%{$req->search}%");
            }
            if ($req->platform) {
                $q->where('shorts.platform', $req->platform);
            }
            if ($req->status === 'active') {
                $q->where('shorts.is_active', 1);
            } elseif ($req->status === 'hidden') {
                $q->where('shorts.is_active', 0);
            }
            return response()->json($q->paginate(15));
        } catch (\Exception $e) {
            return response()->json(['data' => [], 'total' => 0]);
        }
    }"""

# Read the file
out, _ = ssh_cmd(client, f"cat {APP}/app/Http/Controllers/API/AdminController.php")
if old_getshorts.strip() in out:
    new_content = out.replace(old_getshorts, new_getshorts)
    # Write via heredoc
    import tempfile, os
    tmp = "/tmp/AdminController_fixed.php"
    write_cmd = f"cat > {tmp} << 'PHPEOF'\n{new_content}\nPHPEOF"
    # Use python's paramiko SFTP to write
    sftp = client.open_sftp()
    with sftp.open(f"{APP}/app/Http/Controllers/API/AdminController.php", 'w') as f:
        f.write(new_content)
    print("  AdminController.php - getShorts() platform/status filter ADDED")
else:
    print("  WARNING: Could not find exact getShorts block to replace")
    print("  Looking for alternative...")
    # Try to find it
    if "getShorts" in out:
        print("  getShorts exists but pattern didn't match - checking content")
        idx = out.find("public function getShorts")
        print(out[idx:idx+400])


# ─── FIX 2: api.php - fix crawl-status indentation ───────────────────────────
print("\n=== FIX 2: Fix crawl-status route indentation in api.php ===")

out2, _ = ssh_cmd(client, f"cat {APP}/routes/api.php")

old_crawl = "    Route::get('businesses/crawl-status', [AdminBusinessController::class, 'bulkImport']);"
new_crawl = "        Route::get('businesses/crawl-status', [AdminBusinessController::class, 'crawlStatus']);"

if old_crawl in out2:
    new_content2 = out2.replace(old_crawl, new_crawl)
    sftp2 = client.open_sftp()
    with sftp2.open(f"{APP}/routes/api.php", 'w') as f:
        f.write(new_content2)
    print("  api.php - crawl-status indentation FIXED")
else:
    print("  Could not find old_crawl pattern, checking...")
    if "crawl-status" in out2:
        idx = out2.find("crawl-status")
        print(out2[max(0,idx-50):idx+100])

client.close()
print("\n=== FIXES APPLIED ===")
