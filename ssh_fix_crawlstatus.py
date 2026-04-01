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

out, _ = ssh_cmd(client, f"cat {APP}/app/Http/Controllers/API/AdminBusinessController.php")

# Add crawlStatus method before the closing brace of the class
old_end = "\n}\n"
new_end = """
    public function crawlStatus()
    {
        $total = \\App\\Models\\Business::count();
        $claimed = \\App\\Models\\Business::where('is_claimed', true)->count();
        $premium = \\App\\Models\\Business::where('is_premium', true)->count();
        return response()->json([
            'total'   => $total,
            'claimed' => $claimed,
            'premium' => $premium,
        ]);
    }
}
"""

if out.strip().endswith('}'):
    # Find last closing brace
    new_content = out.rstrip().rstrip('}').rstrip() + new_end
    sftp = client.open_sftp()
    with sftp.open(f"{APP}/app/Http/Controllers/API/AdminBusinessController.php", 'w') as f:
        f.write(new_content)
    print("AdminBusinessController.php - crawlStatus() method ADDED")
else:
    print("Could not find end of class, content ends with:")
    print(repr(out[-100:]))

# Verify
out2, _ = ssh_cmd(client, f"grep 'public function' {APP}/app/Http/Controllers/API/AdminBusinessController.php")
print("\nMethods now in AdminBusinessController:")
print(out2)

# Also run php artisan route:clear to clear route cache
print("=== Clearing Laravel route cache ===")
out3, err3 = ssh_cmd(client, f"cd {APP} && php artisan route:clear 2>&1 && php artisan config:clear 2>&1")
print(out3.strip())
if err3.strip():
    print("STDERR:", err3.strip()[:200])

client.close()
print("=== DONE ===")
