import requests
import json
import socket
import ssl

print("="*60)
print("=== WEBSOCKET CONNECTION TEST ===")
print("="*60)

# Test WebSocket handshake via HTTPS
print("\n[1] WebSocket HTTP Upgrade Test")
try:
    import websocket
    ws_available = True
    print("  websocket-client available")
except ImportError:
    ws_available = False
    print("  websocket-client NOT available, using raw socket")

# Raw WebSocket connection test
print("\n[2] Raw WebSocket connection to wss://somekorean.com/app/somekorean_key_2026")
try:
    import urllib3
    urllib3.disable_warnings()

    # Try upgrading connection
    headers = {
        'Host': 'somekorean.com',
        'Upgrade': 'websocket',
        'Connection': 'Upgrade',
        'Sec-WebSocket-Key': 'dGhlIHNhbXBsZSBub25jZQ==',
        'Sec-WebSocket-Version': '13',
        'Origin': 'https://somekorean.com',
    }

    r = requests.get(
        'https://somekorean.com/app/somekorean_key_2026?protocol=7&client=js&version=8.0.0',
        headers=headers,
        timeout=10,
        verify=False
    )
    print(f"  Status: {r.status_code}")
    print(f"  Response headers: {dict(list(r.headers.items())[:5])}")
    print(f"  Body: {r.text[:200]}")

    if r.status_code == 101:
        print("  PASS: WebSocket upgrade successful!")
    elif r.status_code == 400:
        print("  INFO: 400 - likely bad request format but server is alive")
    else:
        print(f"  Status {r.status_code}")

except Exception as e:
    print(f"  Error: {type(e).__name__}: {e}")

# Test if port 443 WS works via SSL socket
print("\n[3] SSL Socket WebSocket Handshake Test")
try:
    context = ssl.create_default_context()
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE

    with socket.create_connection(('somekorean.com', 443), timeout=10) as sock:
        with context.wrap_socket(sock, server_hostname='somekorean.com') as ssock:
            handshake = (
                "GET /app/somekorean_key_2026?protocol=7&client=js&version=8.0.0 HTTP/1.1\r\n"
                "Host: somekorean.com\r\n"
                "Upgrade: websocket\r\n"
                "Connection: Upgrade\r\n"
                "Sec-WebSocket-Key: dGhlIHNhbXBsZSBub25jZQ==\r\n"
                "Sec-WebSocket-Version: 13\r\n"
                "Origin: https://somekorean.com\r\n"
                "\r\n"
            )
            ssock.send(handshake.encode())
            response = ssock.recv(1024).decode('utf-8', errors='replace')
            print(f"  Response: {response[:300]}")

            if '101 Switching Protocols' in response:
                print("  PASS: WebSocket upgrade successful!")
            elif '200' in response or '400' in response:
                print(f"  Server responded but not upgraded")
            else:
                print(f"  Unexpected response")

except Exception as e:
    print(f"  Error: {type(e).__name__}: {e}")

# Test DM functionality check
print("\n[4] DM (Direct Message) Feature Check")
print("  Checking if DM routes exist...")
r = requests.get('https://somekorean.com/api/dm',
                 headers={"Authorization": "Bearer dummy", "Accept": "application/json"},
                 timeout=10)
print(f"  /api/dm status: {r.status_code}")
try:
    data = r.json()
    print(f"  Response: {json.dumps(data)[:100]}")
except:
    print(f"  Response: {r.text[:100]}")

r = requests.get('https://somekorean.com/api/messages',
                 headers={"Authorization": "Bearer dummy", "Accept": "application/json"},
                 timeout=10)
print(f"  /api/messages status: {r.status_code}")
try:
    data = r.json()
    print(f"  Response: {json.dumps(data)[:100]}")
except:
    print(f"  Response: {r.text[:100]}")

print("\n  NOTE: No dedicated DM endpoints found in current routes.")
print("  DM functionality would need to be implemented separately.")
