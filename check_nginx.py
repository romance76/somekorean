#!/usr/bin/env python3
import paramiko, sys

def log(msg):
    sys.stdout.buffer.write((str(msg) + '\n').encode('utf-8'))
    sys.stdout.buffer.flush()

c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('68.183.60.70', username='root', password='EhdRh0817wodl', timeout=15)

def ssh(cmd, timeout=30):
    stdin, stdout, stderr = c.exec_command(cmd, timeout=timeout)
    return stdout.read().decode('utf-8', errors='replace').strip(), stderr.read().decode('utf-8', errors='replace').strip()

# Test with host header
out, _ = ssh("curl -s -H 'Host: somekorean.com' http://localhost/api/qa/categories 2>&1")
log("With Host header:\n" + out[:500])

# Check nginx config
out, _ = ssh("cat /etc/nginx/sites-enabled/somekorean 2>/dev/null || cat /etc/nginx/sites-enabled/default 2>/dev/null | head -50")
log("\nNginx config:\n" + out[:1000])

# PHP-FPM status
out, _ = ssh("systemctl status php8.2-fpm 2>/dev/null || systemctl status php8.3-fpm 2>/dev/null || systemctl status php-fpm 2>/dev/null | head -5")
log("\nPHP-FPM: " + out[:200])

# Check Laravel log
out, _ = ssh("tail -20 /var/www/somekorean/storage/logs/laravel.log 2>/dev/null")
log("\nLaravel log:\n" + out[-500:])

c.close()
