import paramiko
import os

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('68.183.60.70', username='root', password='EhdRh0817wodl')

sftp = ssh.open_sftp()

base = r'C:\Users\Admin\Desktop\somekorean'

# Upload QAController.php
qa_path = os.path.join(base, 'QAController_new.php')
if os.path.exists(qa_path):
    with open(qa_path, 'r', encoding='utf-8') as f:
        content = f.read()
    with sftp.open('/var/www/somekorean/app/Http/Controllers/API/QAController.php', 'w') as f:
        f.write(content)
    print(f"QAController.php uploaded! ({len(content)} chars)")
else:
    print(f"QAController_new.php not found at {qa_path}")

# Verify both files
for fn in ['CommunityController.php', 'QAController.php']:
    path = f'/var/www/somekorean/app/Http/Controllers/API/{fn}'
    try:
        stat = sftp.stat(path)
        print(f"{fn}: {stat.st_size} bytes on server")
    except Exception as e:
        print(f"{fn}: NOT FOUND - {e}")

sftp.close()
ssh.close()
