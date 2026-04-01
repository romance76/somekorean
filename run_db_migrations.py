import paramiko, sys, time
sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1)
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('68.183.60.70', username='root', password='EhdRh0817wodl', timeout=15)

def ssh(cmd, timeout=60):
    _, out, err = c.exec_command(cmd, timeout=timeout)
    o = out.read().decode('utf-8', errors='replace').strip()
    e = err.read().decode('utf-8', errors='replace').strip()
    return o + (('\nERR: '+e) if e else '')

DB = "mysql -u somekorean_user -pSK_DB@2026\\!secure somekorean"

# SQL migrations
migrations = """
-- Alter businesses table
ALTER TABLE businesses
  ADD COLUMN IF NOT EXISTS owner_user_id BIGINT UNSIGNED NULL AFTER id,
  ADD COLUMN IF NOT EXISTS is_claimed TINYINT(1) DEFAULT 0 AFTER owner_user_id,
  ADD COLUMN IF NOT EXISTS is_premium TINYINT(1) DEFAULT 0 AFTER is_claimed,
  ADD COLUMN IF NOT EXISTS premium_type ENUM('basic','standard','premium') NULL AFTER is_premium,
  ADD COLUMN IF NOT EXISTS premium_expires_at TIMESTAMP NULL AFTER premium_type,
  ADD COLUMN IF NOT EXISTS name_ko VARCHAR(255) NULL AFTER name,
  ADD COLUMN IF NOT EXISTS name_en VARCHAR(255) NULL AFTER name_ko,
  ADD COLUMN IF NOT EXISTS owner_description_ko TEXT NULL,
  ADD COLUMN IF NOT EXISTS owner_description_en TEXT NULL,
  ADD COLUMN IF NOT EXISTS owner_photos JSON NULL,
  ADD COLUMN IF NOT EXISTS menu_items JSON NULL,
  ADD COLUMN IF NOT EXISTS data_source VARCHAR(50) DEFAULT 'manual',
  ADD COLUMN IF NOT EXISTS source_url VARCHAR(500) NULL,
  ADD COLUMN IF NOT EXISTS temp_closed TINYINT(1) DEFAULT 0;

-- Alter business_reviews table
ALTER TABLE business_reviews
  ADD COLUMN IF NOT EXISTS visit_date DATE NULL,
  ADD COLUMN IF NOT EXISTS sub_ratings JSON NULL,
  ADD COLUMN IF NOT EXISTS is_visible TINYINT(1) DEFAULT 1,
  ADD COLUMN IF NOT EXISTS report_count INT DEFAULT 0,
  ADD COLUMN IF NOT EXISTS owner_reply TEXT NULL,
  ADD COLUMN IF NOT EXISTS owner_replied_at TIMESTAMP NULL;

-- Create business_claims table
CREATE TABLE IF NOT EXISTS business_claims (
  id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  business_id BIGINT UNSIGNED NOT NULL,
  user_id BIGINT UNSIGNED NOT NULL,
  status ENUM('pending','email_sent','email_verified','docs_submitted','approved','rejected') DEFAULT 'pending',
  email_token VARCHAR(100) NULL,
  email_verified_at TIMESTAMP NULL,
  document_urls JSON NULL,
  admin_note TEXT NULL,
  reviewed_by BIGINT UNSIGNED NULL,
  reviewed_at TIMESTAMP NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  INDEX idx_business_id (business_id),
  INDEX idx_user_id (user_id),
  INDEX idx_status (status)
);

-- Create business_stats table
CREATE TABLE IF NOT EXISTS business_stats (
  id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  business_id BIGINT UNSIGNED NOT NULL,
  stat_date DATE NOT NULL,
  views INT DEFAULT 0,
  clicks INT DEFAULT 0,
  phone_clicks INT DEFAULT 0,
  direction_clicks INT DEFAULT 0,
  website_clicks INT DEFAULT 0,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  UNIQUE KEY uq_business_date (business_id, stat_date),
  INDEX idx_business_id (business_id)
);

-- Create business_events table
CREATE TABLE IF NOT EXISTS business_events (
  id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  business_id BIGINT UNSIGNED NOT NULL,
  title VARCHAR(255) NOT NULL,
  description TEXT NULL,
  image_url VARCHAR(500) NULL,
  event_date DATE NOT NULL,
  event_time TIME NULL,
  is_active TINYINT(1) DEFAULT 1,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  INDEX idx_business_id (business_id),
  INDEX idx_event_date (event_date)
);
"""

# Write SQL to file and run
import base64
enc = base64.b64encode(migrations.encode()).decode()
print(ssh(f"echo '{enc}' | base64 -d > /tmp/sk_migrations.sql"))
print(ssh(f"{DB} < /tmp/sk_migrations.sql 2>&1"))
print("Migration SQL done")

# Verify
print(ssh(f"{DB} -e \"SHOW COLUMNS FROM businesses\" | grep -E 'is_claimed|owner_user_id|is_premium'"))
print(ssh(f"{DB} -e \"SHOW TABLES LIKE 'business_%'\""))

# Create models
# BusinessClaim.php
claim_model = r"""<?php
namespace App\Models;
use Illuminate\Database\Eloquent\Model;
class BusinessClaim extends Model {
    protected $fillable = [
        'business_id','user_id','status','email_token','email_verified_at',
        'document_urls','admin_note','reviewed_by','reviewed_at'
    ];
    protected $casts = ['document_urls'=>'array','email_verified_at'=>'datetime','reviewed_at'=>'datetime'];
    public function business() { return $this->belongsTo(Business::class); }
    public function user() { return $this->belongsTo(User::class); }
}
"""
enc = base64.b64encode(claim_model.encode()).decode()
print(ssh(f"echo '{enc}' | base64 -d > /var/www/somekorean/app/Models/BusinessClaim.php"))

# BusinessStat.php
stat_model = r"""<?php
namespace App\Models;
use Illuminate\Database\Eloquent\Model;
class BusinessStat extends Model {
    protected $fillable = ['business_id','stat_date','views','clicks','phone_clicks','direction_clicks','website_clicks'];
    public function business() { return $this->belongsTo(Business::class); }
}
"""
enc = base64.b64encode(stat_model.encode()).decode()
print(ssh(f"echo '{enc}' | base64 -d > /var/www/somekorean/app/Models/BusinessStat.php"))

# BusinessEvent.php
event_model = r"""<?php
namespace App\Models;
use Illuminate\Database\Eloquent\Model;
class BusinessEvent extends Model {
    protected $fillable = ['business_id','title','description','image_url','event_date','event_time','is_active'];
    protected $casts = ['event_date'=>'date','is_active'=>'boolean'];
    public function business() { return $this->belongsTo(Business::class); }
}
"""
enc = base64.b64encode(event_model.encode()).decode()
print(ssh(f"echo '{enc}' | base64 -d > /var/www/somekorean/app/Models/BusinessEvent.php"))
print("Models created")

# Create storage/app/claims directory
print(ssh("mkdir -p /var/www/somekorean/storage/app/public/claims && chown -R www-data:www-data /var/www/somekorean/storage/app/public/claims"))

print("=== Team 1 DB Alpha COMPLETE ===")
c.close()
