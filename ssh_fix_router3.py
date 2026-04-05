import paramiko
import re

HOST = "68.183.60.70"
USER = "root"
PASS = "EhdRh0817wodl"
APP = "/var/www/somekorean"

def ssh_cmd(client, cmd):
    stdin, stdout, stderr = client.exec_command(cmd, timeout=30)
    out = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    return out, err

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(HOST, username=USER, password=PASS, timeout=15)

out, _ = ssh_cmd(client, f"cat {APP}/resources/js/router/index.js")

# For /games/bingo path conflict:
# Line 139: { path: '/games/bingo', component: BingoGame.vue, name: 'bingo' }   <- keep, it's in BingoGame block
# Line 143: { path: '/games/bingo', component: GameBingo.vue, name: 'game-bingo' } <- remove duplicate (GameBingo and BingoGame are different)
#    Actually GameBingo = senior bingo which is already at /games/senior-bingo, this is a leftover duplicate

# For /games/memory path conflict:
# Line 130: { path: '/games/memory', component: MemoryGame.vue, name: 'memory' }  <- keep
# Line 144: { path: '/games/memory', component: GameMemory.vue, name: 'game-memory' } <- remove duplicate
#    GameMemory is same as picture-memory which is already at /games/picture-memory

# Remove the second /games/bingo (game-bingo) and second /games/memory (game-memory)
old1 = "  { path: '/games/bingo', component: () => import('../pages/games/GameBingo.vue'), name: 'game-bingo' },"
old2 = "  { path: '/games/memory', component: () => import('../pages/games/GameMemory.vue'), name: 'game-memory' },"

new_content = out
removed = []

if old1 in new_content:
    new_content = new_content.replace(old1, '', 1)
    removed.append(old1.strip())
else:
    print("WARNING: could not find game-bingo line exactly")
    # Try without leading spaces
    for line in out.split('\n'):
        if "game-bingo" in line:
            print(f"  Found: '{line}'")

if old2 in new_content:
    new_content = new_content.replace(old2, '', 1)
    removed.append(old2.strip())
else:
    print("WARNING: could not find game-memory line exactly")
    for line in out.split('\n'):
        if "game-memory" in line:
            print(f"  Found: '{line}'")

print(f"Removed {len(removed)} lines:")
for r in removed:
    print(f"  {r}")

if removed:
    sftp = client.open_sftp()
    with sftp.open(f"{APP}/resources/js/router/index.js", 'w') as f:
        f.write(new_content)
    print("router/index.js updated")

# Verify
out2, _ = ssh_cmd(client, f"grep -oP \"path: '.*?'\" {APP}/resources/js/router/index.js | sort | uniq -d")
print("Remaining duplicate paths:", out2.strip() if out2.strip() else "NONE")

out3, _ = ssh_cmd(client, f"grep -oP \"name: '.*?'\" {APP}/resources/js/router/index.js | sort | uniq -d")
# Filter out guard references
names = [n for n in out3.strip().split('\n') if n.strip() and 'login' not in n and 'home' not in n]
print("Remaining duplicate route names:", '\n'.join(names) if names else "NONE (guard refs filtered)")

client.close()
print("=== DONE ===")
