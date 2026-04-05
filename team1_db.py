import paramiko, base64, sys
sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1)
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('68.183.60.70', username='root', password='EhdRh0817wodl', timeout=15)

def ssh(cmd, timeout=180):
    _, out, err = c.exec_command(cmd, timeout=timeout)
    result = out.read().decode('utf-8', errors='replace').strip()
    error = err.read().decode('utf-8', errors='replace').strip()
    if error:
        return result + '\nSTDERR: ' + error
    return result

def write_file(path, content):
    enc = base64.b64encode(content.encode('utf-8')).decode('ascii')
    chunks = [enc[i:i+2000] for i in range(0, len(enc), 2000)]
    ssh('rm -f /tmp/wf_chunk')
    for p in chunks:
        ssh(f"printf '%s' '{p}' >> /tmp/wf_chunk")
    ssh(f'cat /tmp/wf_chunk | base64 -d > {path} && rm -f /tmp/wf_chunk')
    print(f'Written {path}: {ssh(f"wc -c < {path}")} bytes')

# ============================================================
# Step 1: Check existing table structures
# ============================================================
print("=" * 60)
print("STEP 1: Checking existing table structures")
print("=" * 60)

print("\n--- DESCRIBE businesses ---")
print(ssh("mysql --defaults-file=/tmp/sk_main.cnf somekorean -e 'DESCRIBE businesses;'"))

print("\n--- DESCRIBE business_reviews ---")
print(ssh("mysql --defaults-file=/tmp/sk_main.cnf somekorean -e 'DESCRIBE business_reviews;'"))

print("\n--- SHOW TABLES LIKE business% ---")
print(ssh("mysql --defaults-file=/tmp/sk_main.cnf somekorean -e \"SHOW TABLES LIKE 'business%';\""))

# ============================================================
# Step 2: ALTER businesses table
# ============================================================
print("\n" + "=" * 60)
print("STEP 2: ALTER TABLE businesses")
print("=" * 60)

alter_businesses = """
ALTER TABLE businesses
  ADD COLUMN IF NOT EXISTS owner_user_id BIGINT UNSIGNED NULL AFTER owner_id,
  ADD COLUMN IF NOT EXISTS is_claimed TINYINT(1) DEFAULT 0 AFTER is_verified,
  ADD COLUMN IF NOT EXISTS is_premium TINYINT(1) DEFAULT 0 AFTER is_claimed,
  ADD COLUMN IF NOT EXISTS premium_type VARCHAR(20) NULL AFTER is_premium,
  ADD COLUMN IF NOT EXISTS premium_expires_at TIMESTAMP NULL AFTER premium_type,
  ADD COLUMN IF NOT EXISTS google_place_id VARCHAR(255) NULL AFTER premium_expires_at,
  ADD COLUMN IF NOT EXISTS name_ko VARCHAR(100) NULL AFTER name,
  ADD COLUMN IF NOT EXISTS name_en VARCHAR(100) NULL AFTER name_ko,
  ADD COLUMN IF NOT EXISTS owner_description_ko TEXT NULL,
  ADD COLUMN IF NOT EXISTS owner_description_en TEXT NULL,
  ADD COLUMN IF NOT EXISTS owner_photos JSON NULL,
  ADD COLUMN IF NOT EXISTS menu_items JSON NULL,
  ADD COLUMN IF NOT EXISTS data_source VARCHAR(50) NULL DEFAULT 'manual',
  ADD COLUMN IF NOT EXISTS source_url VARCHAR(500) NULL,
  ADD COLUMN IF NOT EXISTS temp_closed TINYINT(1) DEFAULT 0,
  ADD COLUMN IF NOT EXISTS temp_closed_note VARCHAR(255) NULL;
"""

result = ssh(f"mysql --defaults-file=/tmp/sk_main.cnf somekorean -e \"{alter_businesses.strip()}\"")
print("ALTER businesses result:", result if result else "OK")

# ============================================================
# Step 3: ALTER business_reviews table
# ============================================================
print("\n" + "=" * 60)
print("STEP 3: ALTER TABLE business_reviews")
print("=" * 60)

alter_reviews = """
ALTER TABLE business_reviews
  ADD COLUMN IF NOT EXISTS visit_date DATE NULL,
  ADD COLUMN IF NOT EXISTS sub_ratings JSON NULL,
  ADD COLUMN IF NOT EXISTS is_visible TINYINT(1) DEFAULT 1,
  ADD COLUMN IF NOT EXISTS report_count INT DEFAULT 0,
  ADD COLUMN IF NOT EXISTS owner_reply TEXT NULL,
  ADD COLUMN IF NOT EXISTS owner_replied_at TIMESTAMP NULL;
"""

result = ssh(f"mysql --defaults-file=/tmp/sk_main.cnf somekorean -e \"{alter_reviews.strip()}\"")
print("ALTER business_reviews result:", result if result else "OK")

# ============================================================
# Step 4: Create business_claims table
# ============================================================
print("\n" + "=" * 60)
print("STEP 4: CREATE TABLE business_claims")
print("=" * 60)

create_claims = """CREATE TABLE IF NOT EXISTS business_claims (
  id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  business_id BIGINT UNSIGNED NOT NULL,
  user_id BIGINT UNSIGNED NOT NULL,
  method ENUM('document','email','kakao') NOT NULL,
  status ENUM('pending','approved','rejected') DEFAULT 'pending',
  documents JSON NULL,
  email_token VARCHAR(64) NULL,
  email_verified TINYINT(1) DEFAULT 0,
  admin_note TEXT NULL,
  submitted_at TIMESTAMP NULL,
  reviewed_at TIMESTAMP NULL,
  reviewed_by BIGINT UNSIGNED NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  INDEX idx_business_id (business_id),
  INDEX idx_user_id (user_id),
  INDEX idx_status (status),
  INDEX idx_email_token (email_token)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;"""

result = ssh(f"mysql --defaults-file=/tmp/sk_main.cnf somekorean -e \"{create_claims}\"")
print("CREATE business_claims result:", result if result else "OK")

# ============================================================
# Step 5: Create business_stats table
# ============================================================
print("\n" + "=" * 60)
print("STEP 5: CREATE TABLE business_stats")
print("=" * 60)

create_stats = """CREATE TABLE IF NOT EXISTS business_stats (
  id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  business_id BIGINT UNSIGNED NOT NULL,
  stat_date DATE NOT NULL,
  views INT DEFAULT 0,
  phone_clicks INT DEFAULT 0,
  direction_clicks INT DEFAULT 0,
  website_clicks INT DEFAULT 0,
  bookmark_adds INT DEFAULT 0,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  UNIQUE KEY uk_business_date (business_id, stat_date),
  INDEX idx_business_id (business_id),
  INDEX idx_stat_date (stat_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;"""

result = ssh(f"mysql --defaults-file=/tmp/sk_main.cnf somekorean -e \"{create_stats}\"")
print("CREATE business_stats result:", result if result else "OK")

# ============================================================
# Step 6: Create business_events table
# ============================================================
print("\n" + "=" * 60)
print("STEP 6: CREATE TABLE business_events")
print("=" * 60)

create_events = """CREATE TABLE IF NOT EXISTS business_events (
  id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  business_id BIGINT UNSIGNED NOT NULL,
  title VARCHAR(200) NOT NULL,
  content TEXT NULL,
  image_url VARCHAR(500) NULL,
  starts_at DATE NULL,
  expires_at DATE NULL,
  is_active TINYINT(1) DEFAULT 1,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  INDEX idx_business_id (business_id),
  INDEX idx_active_expires (is_active, expires_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;"""

result = ssh(f"mysql --defaults-file=/tmp/sk_main.cnf somekorean -e \"{create_events}\"")
print("CREATE business_events result:", result if result else "OK")

# ============================================================
# Step 7: Create Laravel Models
# ============================================================
print("\n" + "=" * 60)
print("STEP 7: Writing Laravel Models")
print("=" * 60)

# BusinessClaim.php
business_claim_php = '''<?php
namespace App\\Models;
use Illuminate\\Database\\Eloquent\\Model;

class BusinessClaim extends Model
{
    protected $fillable = [
        'business_id','user_id','method','status','documents',
        'email_token','email_verified','admin_note',
        'submitted_at','reviewed_at','reviewed_by'
    ];
    protected $casts = [
        'documents' => 'array',
        'email_verified' => 'boolean',
        'submitted_at' => 'datetime',
        'reviewed_at' => 'datetime',
    ];
    public function business() { return $this->belongsTo(Business::class); }
    public function user() { return $this->belongsTo(User::class); }
    public function reviewer() { return $this->belongsTo(User::class, 'reviewed_by'); }
}
'''
write_file('/var/www/somekorean/app/Models/BusinessClaim.php', business_claim_php)

# BusinessStat.php
business_stat_php = '''<?php
namespace App\\Models;
use Illuminate\\Database\\Eloquent\\Model;

class BusinessStat extends Model
{
    protected $fillable = [
        'business_id','stat_date','views','phone_clicks',
        'direction_clicks','website_clicks','bookmark_adds'
    ];
    protected $casts = ['stat_date' => 'date'];
    public function business() { return $this->belongsTo(Business::class); }
}
'''
write_file('/var/www/somekorean/app/Models/BusinessStat.php', business_stat_php)

# BusinessEvent.php
business_event_php = '''<?php
namespace App\\Models;
use Illuminate\\Database\\Eloquent\\Model;

class BusinessEvent extends Model
{
    protected $fillable = [
        'business_id','title','content','image_url',
        'starts_at','expires_at','is_active'
    ];
    protected $casts = [
        'starts_at' => 'date',
        'expires_at' => 'date',
        'is_active' => 'boolean',
    ];
    public function business() { return $this->belongsTo(Business::class); }
    public function scopeActive($q) {
        return $q->where('is_active', true)
                 ->where(function($q) { $q->whereNull('expires_at')->orWhere('expires_at', '>=', now()); });
    }
}
'''
write_file('/var/www/somekorean/app/Models/BusinessEvent.php', business_event_php)

# ============================================================
# Step 7b: Read and update Business.php
# ============================================================
print("\n--- Reading Business.php ---")
business_content = ssh("cat /var/www/somekorean/app/Models/Business.php")
print(business_content[:3000])

# ============================================================
# Step 7c: Read and update BusinessReview.php
# ============================================================
print("\n--- Reading BusinessReview.php ---")
review_content = ssh("cat /var/www/somekorean/app/Models/BusinessReview.php")
print(review_content[:3000])

# ============================================================
# Step 8: Create storage directory
# ============================================================
print("\n" + "=" * 60)
print("STEP 8: Create storage/app/claims directory")
print("=" * 60)

print(ssh("mkdir -p /var/www/somekorean/storage/app/claims"))
print(ssh("chmod 755 /var/www/somekorean/storage/app/claims"))
print(ssh("chown www-data:www-data /var/www/somekorean/storage/app/claims"))
print("Claims storage directory created.")

# ============================================================
# Step 9: Storage link
# ============================================================
print("\n" + "=" * 60)
print("STEP 9: php artisan storage:link")
print("=" * 60)
print(ssh("cd /var/www/somekorean && php artisan storage:link 2>&1"))

# ============================================================
# Step 10: composer dump-autoload
# ============================================================
print("\n" + "=" * 60)
print("STEP 10: composer dump-autoload")
print("=" * 60)
print(ssh("cd /var/www/somekorean && composer dump-autoload 2>&1 | tail -5"))

# ============================================================
# Step 11: Verify tables
# ============================================================
print("\n" + "=" * 60)
print("STEP 11: Verify all tables")
print("=" * 60)

print("\n--- SHOW TABLES LIKE business% ---")
print(ssh("mysql --defaults-file=/tmp/sk_main.cnf somekorean -e \"SHOW TABLES LIKE 'business%';\""))

print("\n--- DESCRIBE business_claims ---")
print(ssh("mysql --defaults-file=/tmp/sk_main.cnf somekorean -e 'DESCRIBE business_claims;'"))

print("\n--- DESCRIBE business_stats ---")
print(ssh("mysql --defaults-file=/tmp/sk_main.cnf somekorean -e 'DESCRIBE business_stats;'"))

print("\n--- DESCRIBE business_events ---")
print(ssh("mysql --defaults-file=/tmp/sk_main.cnf somekorean -e 'DESCRIBE business_events;'"))

print("\n--- DESCRIBE businesses (new columns) ---")
print(ssh("mysql --defaults-file=/tmp/sk_main.cnf somekorean -e 'DESCRIBE businesses;'"))

print("\n--- DESCRIBE business_reviews (new columns) ---")
print(ssh("mysql --defaults-file=/tmp/sk_main.cnf somekorean -e 'DESCRIBE business_reviews;'"))

print("\n" + "=" * 60)
print("DEPLOYMENT COMPLETE")
print("=" * 60)

c.close()
