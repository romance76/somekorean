import paramiko
import json
import requests

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('68.183.60.70', username='root', password='EhdRh0817wodl', timeout=30)

def run(cmd, timeout=60):
    stdin, stdout, stderr = client.exec_command(cmd, timeout=timeout)
    out = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    return out, err

print("=== BUG ANALYSIS AND FIXES ===\n")

# Bug 1: Check DM send returns correct structure
print("BUG CHECK 1: DM send response structure")
print("  - send() returns {'message': '...', 'data': {...message obj...}}")
print("  - Frontend should look for data.data.id not data.id")
print("  - This is a minor inconsistency but not a bug per se")
print("  STATUS: MINOR ISSUE (response wraps in 'data' key)")

# Bug 2: Check if chat/rooms POST exists (create room)
print("\nBUG CHECK 2: Chat room creation route")
out, err = run("grep -n 'chat/rooms' /var/www/somekorean/routes/api.php")
print(f"  Routes: {out.strip()}")
print("  STATUS: POST /api/chat/rooms only in admin routes, not user routes")

# Bug 3: Check match block
print("\nBUG CHECK 3: Match user block feature")
out, err = run("grep -rn 'match.*block\|block.*match' /var/www/somekorean/routes/api.php")
print(f"  Match block routes: {out.strip() or 'NONE'}")

# Bug 4: Check if there's a chat leave/exit route
print("\nBUG CHECK 4: Chat room leave feature")
out, err = run("grep -n 'leave\|exit\|quit' /var/www/somekorean/routes/api.php")
print(f"  Leave routes: {out.strip() or 'NONE'}")

# Bug 5: Check MessageController for delete/reply functionality
print("\nBUG CHECK 5: DM features (delete, reply, etc.)")
out, err = run("grep -n 'delete\|reply\|send\|read' /var/www/somekorean/routes/api.php | grep message")
print(f"  Message routes: {out.strip()}")

# Check full messages routes
out, err = run("grep -A1 -B1 'Message' /var/www/somekorean/routes/api.php | head -20")
print(f"\n  Full Message routes context: {out[:400]}")

# Bug 6: Check if chat rooms have DM type support
print("\nBUG CHECK 6: ChatRoom DM type check")
out, err = run("grep -n 'dm\|direct\|private\|type' /var/www/somekorean/app/Models/ChatRoom.php")
print(f"  ChatRoom type support: {out}")

out, err = run("cd /var/www/somekorean && php artisan tinker --execute=\"echo DB::select('SELECT DISTINCT type FROM chat_rooms')[0]->type ?? 'no types';\" 2>&1 | tail -3")
print(f"  ChatRoom types in DB: {out}")

# Bug 7: Check if match profiles has photos column
print("\nBUG CHECK 7: Match profile photos storage")
out, err = run("cd /var/www/somekorean && php artisan tinker --execute=\"\\$cols = DB::getSchemaBuilder()->getColumnListing('match_profiles'); echo implode(',', \\$cols);\" 2>&1 | tail -3")
print(f"  match_profiles columns: {out}")

# Bug 8: Check queue worker (for broadcast/notifications)
print("\nBUG CHECK 8: Queue worker status")
out, err = run("ps aux | grep 'queue:work' | grep -v grep")
print(f"  Queue workers: {out.strip() or 'NONE RUNNING'}")

client.close()
