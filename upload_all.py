import paramiko
import os

def get_ssh():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect('68.183.60.70', username='root', password='EhdRh0817wodl')
    return ssh

def upload_file(local_path, remote_path):
    ssh = get_ssh()
    sftp = ssh.open_sftp()
    sftp.put(local_path, remote_path)
    sftp.close()
    ssh.close()
    print(f"Uploaded: {local_path} -> {remote_path}")

deploy_dir = os.path.join(os.path.dirname(__file__), '_deploy')

files = {
    'ShoppingStore.php': '/var/www/somekorean/app/Models/ShoppingStore.php',
    'StoreLocation.php': '/var/www/somekorean/app/Models/StoreLocation.php',
    'StoreFlyer.php': '/var/www/somekorean/app/Models/StoreFlyer.php',
    'ScrapeLog.php': '/var/www/somekorean/app/Models/ScrapeLog.php',
    'ShoppingController.php': '/var/www/somekorean/app/Http/Controllers/API/ShoppingController.php',
    'AdminShopping.vue': '/var/www/somekorean/resources/js/pages/admin/AdminShopping.vue',
}

for local_name, remote_path in files.items():
    local_path = os.path.join(deploy_dir, local_name)
    if os.path.exists(local_path):
        upload_file(local_path, remote_path)
    else:
        print(f"MISSING: {local_path}")

print("\nAll files uploaded!")
