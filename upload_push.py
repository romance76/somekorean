import paramiko
import sys
import os

def get_ssh():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect('68.183.60.70', username='root', password='EhdRh0817wodl', timeout=10)
    return ssh

def upload_file(local_path, remote_path):
    ssh = get_ssh()
    sftp = ssh.open_sftp()
    sftp.put(local_path, remote_path)
    sftp.close()
    ssh.close()
    print(f"Uploaded: {local_path} -> {remote_path}")

def run_cmd(cmd, timeout=120):
    ssh = get_ssh()
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=timeout)
    out = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    code = stdout.channel.recv_exit_status()
    ssh.close()
    if out:
        print(out, end='')
    if err:
        print(err, end='', file=sys.stderr)
    return code

def write_remote(remote_path, content):
    ssh = get_ssh()
    sftp = ssh.open_sftp()
    with sftp.file(remote_path, 'w') as f:
        f.write(content)
    sftp.close()
    ssh.close()
    print(f"Written: {remote_path}")

if __name__ == '__main__':
    base = os.path.dirname(os.path.abspath(__file__))

    # 1. Upload server.js
    upload_file(os.path.join(base, 'server_js_new.js'), '/var/www/somekorean/socket-server/server.js')

    # 2. Create usePushNotification.js composable
    composable = r'''const VAPID_PUBLIC_KEY = 'BLVT7DZrnaD96Ygh4FlIaUjcexV0xFOkKs91apzUUxZQxzO5zS06oIW18AVj8vnKuzH_Kev3zYGGL1g7pdsC438';

export function usePushNotification() {
    async function subscribe(userId) {
        if (!('serviceWorker' in navigator) || !('PushManager' in window)) {
            console.log('Push notifications not supported');
            return false;
        }

        try {
            const registration = await navigator.serviceWorker.ready;
            let subscription = await registration.pushManager.getSubscription();

            if (!subscription) {
                subscription = await registration.pushManager.subscribe({
                    userVisibleOnly: true,
                    applicationServerKey: urlBase64ToUint8Array(VAPID_PUBLIC_KEY)
                });
            }

            // 서버에 구독 정보 저장
            await fetch('/api/socket/push-subscribe', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    userId,
                    subscription: subscription.toJSON()
                })
            });

            console.log('Push subscription saved for user', userId);
            return true;
        } catch (err) {
            console.error('Push subscription failed:', err);
            return false;
        }
    }

    function urlBase64ToUint8Array(base64String) {
        const padding = '='.repeat((4 - base64String.length % 4) % 4);
        const base64 = (base64String + padding).replace(/-/g, '+').replace(/_/g, '/');
        const rawData = window.atob(base64);
        const outputArray = new Uint8Array(rawData.length);
        for (let i = 0; i < rawData.length; ++i) {
            outputArray[i] = rawData.charCodeAt(i);
        }
        return outputArray;
    }

    async function requestPermission() {
        if (!('Notification' in window)) return 'denied';
        return await Notification.requestPermission();
    }

    return { subscribe, requestPermission };
}
'''
    write_remote('/var/www/somekorean/resources/js/composables/usePushNotification.js', composable)

    print("\nAll files uploaded successfully!")
