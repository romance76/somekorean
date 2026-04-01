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

# Check MySQL version
print("MySQL version:", ssh("mysql --defaults-file=/tmp/sk_main.cnf -e 'SELECT VERSION();'"))

# Use a SQL script file approach - write SQL to a file then execute it
# This avoids quoting issues with complex SQL in shell commands

businesses_alter_sql = """
-- Add columns to businesses table (conditional via stored procedure)
DROP PROCEDURE IF EXISTS add_business_columns;
DELIMITER //
CREATE PROCEDURE add_business_columns()
BEGIN
    IF NOT EXISTS (SELECT 1 FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA='somekorean' AND TABLE_NAME='businesses' AND COLUMN_NAME='owner_user_id') THEN
        ALTER TABLE businesses ADD COLUMN owner_user_id BIGINT UNSIGNED NULL AFTER owner_id;
    END IF;
    IF NOT EXISTS (SELECT 1 FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA='somekorean' AND TABLE_NAME='businesses' AND COLUMN_NAME='is_claimed') THEN
        ALTER TABLE businesses ADD COLUMN is_claimed TINYINT(1) DEFAULT 0 AFTER is_verified;
    END IF;
    IF NOT EXISTS (SELECT 1 FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA='somekorean' AND TABLE_NAME='businesses' AND COLUMN_NAME='is_premium') THEN
        ALTER TABLE businesses ADD COLUMN is_premium TINYINT(1) DEFAULT 0 AFTER is_claimed;
    END IF;
    IF NOT EXISTS (SELECT 1 FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA='somekorean' AND TABLE_NAME='businesses' AND COLUMN_NAME='premium_type') THEN
        ALTER TABLE businesses ADD COLUMN premium_type VARCHAR(20) NULL AFTER is_premium;
    END IF;
    IF NOT EXISTS (SELECT 1 FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA='somekorean' AND TABLE_NAME='businesses' AND COLUMN_NAME='premium_expires_at') THEN
        ALTER TABLE businesses ADD COLUMN premium_expires_at TIMESTAMP NULL AFTER premium_type;
    END IF;
    IF NOT EXISTS (SELECT 1 FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA='somekorean' AND TABLE_NAME='businesses' AND COLUMN_NAME='google_place_id') THEN
        ALTER TABLE businesses ADD COLUMN google_place_id VARCHAR(255) NULL AFTER premium_expires_at;
    END IF;
    IF NOT EXISTS (SELECT 1 FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA='somekorean' AND TABLE_NAME='businesses' AND COLUMN_NAME='name_ko') THEN
        ALTER TABLE businesses ADD COLUMN name_ko VARCHAR(100) NULL AFTER name;
    END IF;
    IF NOT EXISTS (SELECT 1 FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA='somekorean' AND TABLE_NAME='businesses' AND COLUMN_NAME='name_en') THEN
        ALTER TABLE businesses ADD COLUMN name_en VARCHAR(100) NULL AFTER name_ko;
    END IF;
    IF NOT EXISTS (SELECT 1 FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA='somekorean' AND TABLE_NAME='businesses' AND COLUMN_NAME='owner_description_ko') THEN
        ALTER TABLE businesses ADD COLUMN owner_description_ko TEXT NULL;
    END IF;
    IF NOT EXISTS (SELECT 1 FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA='somekorean' AND TABLE_NAME='businesses' AND COLUMN_NAME='owner_description_en') THEN
        ALTER TABLE businesses ADD COLUMN owner_description_en TEXT NULL;
    END IF;
    IF NOT EXISTS (SELECT 1 FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA='somekorean' AND TABLE_NAME='businesses' AND COLUMN_NAME='owner_photos') THEN
        ALTER TABLE businesses ADD COLUMN owner_photos JSON NULL;
    END IF;
    IF NOT EXISTS (SELECT 1 FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA='somekorean' AND TABLE_NAME='businesses' AND COLUMN_NAME='menu_items') THEN
        ALTER TABLE businesses ADD COLUMN menu_items JSON NULL;
    END IF;
    IF NOT EXISTS (SELECT 1 FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA='somekorean' AND TABLE_NAME='businesses' AND COLUMN_NAME='data_source') THEN
        ALTER TABLE businesses ADD COLUMN data_source VARCHAR(50) NULL DEFAULT 'manual';
    END IF;
    IF NOT EXISTS (SELECT 1 FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA='somekorean' AND TABLE_NAME='businesses' AND COLUMN_NAME='source_url') THEN
        ALTER TABLE businesses ADD COLUMN source_url VARCHAR(500) NULL;
    END IF;
    IF NOT EXISTS (SELECT 1 FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA='somekorean' AND TABLE_NAME='businesses' AND COLUMN_NAME='temp_closed') THEN
        ALTER TABLE businesses ADD COLUMN temp_closed TINYINT(1) DEFAULT 0;
    END IF;
    IF NOT EXISTS (SELECT 1 FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA='somekorean' AND TABLE_NAME='businesses' AND COLUMN_NAME='temp_closed_note') THEN
        ALTER TABLE businesses ADD COLUMN temp_closed_note VARCHAR(255) NULL;
    END IF;
END //
DELIMITER ;
CALL add_business_columns();
DROP PROCEDURE IF EXISTS add_business_columns;

-- Add columns to business_reviews table
DROP PROCEDURE IF EXISTS add_review_columns;
DELIMITER //
CREATE PROCEDURE add_review_columns()
BEGIN
    IF NOT EXISTS (SELECT 1 FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA='somekorean' AND TABLE_NAME='business_reviews' AND COLUMN_NAME='visit_date') THEN
        ALTER TABLE business_reviews ADD COLUMN visit_date DATE NULL;
    END IF;
    IF NOT EXISTS (SELECT 1 FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA='somekorean' AND TABLE_NAME='business_reviews' AND COLUMN_NAME='sub_ratings') THEN
        ALTER TABLE business_reviews ADD COLUMN sub_ratings JSON NULL;
    END IF;
    IF NOT EXISTS (SELECT 1 FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA='somekorean' AND TABLE_NAME='business_reviews' AND COLUMN_NAME='is_visible') THEN
        ALTER TABLE business_reviews ADD COLUMN is_visible TINYINT(1) DEFAULT 1;
    END IF;
    IF NOT EXISTS (SELECT 1 FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA='somekorean' AND TABLE_NAME='business_reviews' AND COLUMN_NAME='report_count') THEN
        ALTER TABLE business_reviews ADD COLUMN report_count INT DEFAULT 0;
    END IF;
    IF NOT EXISTS (SELECT 1 FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA='somekorean' AND TABLE_NAME='business_reviews' AND COLUMN_NAME='owner_reply') THEN
        ALTER TABLE business_reviews ADD COLUMN owner_reply TEXT NULL;
    END IF;
    IF NOT EXISTS (SELECT 1 FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA='somekorean' AND TABLE_NAME='business_reviews' AND COLUMN_NAME='owner_replied_at') THEN
        ALTER TABLE business_reviews ADD COLUMN owner_replied_at TIMESTAMP NULL;
    END IF;
END //
DELIMITER ;
CALL add_review_columns();
DROP PROCEDURE IF EXISTS add_review_columns;
"""

write_file('/tmp/sk_alter.sql', businesses_alter_sql)

print("\nRunning ALTER TABLE migrations via SQL script...")
result = ssh("mysql --defaults-file=/tmp/sk_main.cnf somekorean < /tmp/sk_alter.sql 2>&1")
print("Result:", result if result else "OK")

print("\n--- DESCRIBE businesses (after alter) ---")
print(ssh("mysql --defaults-file=/tmp/sk_main.cnf somekorean -e 'DESCRIBE businesses;'"))

print("\n--- DESCRIBE business_reviews (after alter) ---")
print(ssh("mysql --defaults-file=/tmp/sk_main.cnf somekorean -e 'DESCRIBE business_reviews;'"))

# ============================================================
# Update Business.php model with new fields
# ============================================================
print("\n" + "=" * 60)
print("Updating Business.php model")
print("=" * 60)

business_php = '''<?php
namespace App\\Models;

use Illuminate\\Database\\Eloquent\\Model;
use Illuminate\\Database\\Eloquent\\SoftDeletes;

class Business extends Model
{
    use SoftDeletes;

    protected $fillable = [
        'owner_id', 'owner_user_id', 'name', 'name_ko', 'name_en',
        'category', 'description', 'address',
        'lat', 'lng', 'latitude', 'longitude',
        'phone', 'website', 'hours', 'photos',
        'region', 'is_verified', 'is_sponsored', 'status',
        'is_claimed', 'is_premium', 'premium_type', 'premium_expires_at',
        'google_place_id',
        'owner_description_ko', 'owner_description_en',
        'owner_photos', 'menu_items',
        'data_source', 'source_url',
        'temp_closed', 'temp_closed_note',
    ];

    protected $casts = [
        'hours' => 'array',
        'photos' => 'array',
        'owner_photos' => 'array',
        'menu_items' => 'array',
        'is_verified' => 'boolean',
        'is_sponsored' => 'boolean',
        'is_claimed' => 'boolean',
        'is_premium' => 'boolean',
        'temp_closed' => 'boolean',
        'premium_expires_at' => 'datetime',
    ];

    public function owner() { return $this->belongsTo(User::class, 'owner_id'); }
    public function ownerUser() { return $this->belongsTo(User::class, 'owner_user_id'); }
    public function reviews() { return $this->hasMany(BusinessReview::class); }
    public function claims() { return $this->hasMany(BusinessClaim::class); }
    public function stats() { return $this->hasMany(BusinessStat::class); }
    public function events() { return $this->hasMany(BusinessEvent::class); }
}
'''
write_file('/var/www/somekorean/app/Models/Business.php', business_php)

# ============================================================
# Update BusinessReview.php model with new fields
# ============================================================
print("\nUpdating BusinessReview.php model")

review_php = '''<?php
namespace App\\Models;

use Illuminate\\Database\\Eloquent\\Model;

class BusinessReview extends Model
{
    protected $fillable = [
        'business_id', 'user_id', 'rating', 'content', 'photos',
        'visit_date', 'sub_ratings', 'is_visible', 'report_count',
        'owner_reply', 'owner_replied_at',
    ];

    protected $casts = [
        'photos' => 'array',
        'sub_ratings' => 'array',
        'is_visible' => 'boolean',
        'visit_date' => 'date',
        'owner_replied_at' => 'datetime',
    ];

    public function business() { return $this->belongsTo(Business::class); }
    public function user() { return $this->belongsTo(User::class); }
}
'''
write_file('/var/www/somekorean/app/Models/BusinessReview.php', review_php)

# Final composer dump-autoload
print("\nRunning composer dump-autoload...")
print(ssh("cd /var/www/somekorean && composer dump-autoload 2>&1 | tail -3"))

print("\n" + "=" * 60)
print("ALL DONE - Final Summary")
print("=" * 60)
print("\nTables in DB:")
print(ssh("mysql --defaults-file=/tmp/sk_main.cnf somekorean -e \"SHOW TABLES LIKE 'business%';\""))

c.close()
