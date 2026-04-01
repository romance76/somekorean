import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('68.183.60.70', username='root', password='EhdRh0817wodl')

def run(label, cmd):
    print(f"\n=== {label} ===")
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=120)
    out = stdout.read().decode()
    err = stderr.read().decode()
    if out:
        print(out)
    if err:
        print("STDERR:", err)

# Step 1: Deduplicate businesses
run("STEP 1: Deduplicate businesses", r"""cd /var/www/somekorean && php artisan tinker --execute="
\$dupes = DB::select('SELECT name, COUNT(*) as cnt FROM businesses GROUP BY name HAVING cnt > 1');
echo 'Found ' . count(\$dupes) . \" duplicate business names\\n\";
\$totalDeleted = 0;
foreach(\$dupes as \$d) {
    \$ids = DB::table('businesses')->where('name', \$d->name)->orderByDesc('id')->pluck('id')->toArray();
    \$keepId = array_shift(\$ids);
    if(count(\$ids) > 0) {
        DB::table('businesses')->whereIn('id', \$ids)->delete();
        \$totalDeleted += count(\$ids);
    }
}
echo \"Deleted \$totalDeleted duplicate businesses\\n\";
echo 'Remaining businesses: ' . DB::table('businesses')->count() . \"\\n\";
" """)

# Step 2: Fix NULL site_settings
run("STEP 2: Fix NULL site_settings", r"""cd /var/www/somekorean && php artisan tinker --execute="
\$fixed = DB::table('site_settings')->whereNull('value')->update(['value' => '']);
echo \"Fixed \$fixed NULL site_settings values\\n\";
" """)

# Step 3: Clean up empty/orphan data
run("STEP 3: Clean up empty/orphan data", r"""cd /var/www/somekorean && php artisan tinker --execute="
\$emptyShorts = DB::table('shorts')->whereNull('title')->orWhere('title', '')->delete();
echo \"Deleted \$emptyShorts empty shorts\\n\";
\$tables = ['users','businesses','job_posts','market_items','posts','events','news','recipe_posts','shorts','comments','chat_messages'];
foreach(\$tables as \$t) {
    echo \"\$t: \" . DB::table(\$t)->count() . \" rows\\n\";
}
" """)

# Step 4: Optimize tables
run("STEP 4: Optimize tables", r"""cd /var/www/somekorean && php artisan tinker --execute="
DB::statement('OPTIMIZE TABLE businesses, news, recipe_posts, qa_answers, shorts, comments');
echo 'Tables optimized';
" """)

ssh.close()
print("\n=== ALL DONE ===")
