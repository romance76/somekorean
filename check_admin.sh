#!/bin/bash
TOKEN=$(curl -s -X POST https://somekorean.com/api/auth/login \
  -H 'Content-Type: application/json' \
  -d '{ "email": "admin@somekorean.com", "password": "Admin1234!" }' \
  | python3 -c 'import sys,json; d=json.load(sys.stdin); print(d.get("token","NO_TOKEN"))')

echo "TOKEN: ${TOKEN:0:50}..."
echo ""
echo "=== /api/auth/me ==="
curl -s https://somekorean.com/api/auth/me \
  -H "Authorization: Bearer $TOKEN" | python3 -c 'import sys,json; d=json.load(sys.stdin); print(json.dumps({k:d[k] for k in ["id","name","email","is_admin","status"] if k in d}, ensure_ascii=False))'
