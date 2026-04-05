import paramiko
import json

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('68.183.60.70', username='root', password='EhdRh0817wodl')

def run(cmd, timeout=60):
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=timeout)
    return stdout.read().decode('utf-8', errors='replace'), stderr.read().decode('utf-8', errors='replace')

# Read the test results JSON from server
out, err = run('cat /tmp/ct_test_results.json 2>/dev/null')
try:
    results = json.loads(out)
    print(f'Loaded {len(results)} test results from server')
except json.JSONDecodeError as e:
    print(f'JSON error: {e}')
    print(out[:1000])
    ssh.close()
    exit(1)

# Analyze
passed = [r for r in results if r.get('pass') == 'PASS']
failed = [r for r in results if r.get('pass') in ['FAIL','FAIL_SECURITY_BUG']]
server_errs = [r for r in results if r.get('pass') == 'SERVER_ERROR' or r.get('status',0) >= 500]
na_404 = [r for r in results if r.get('pass') == 'N/A_404']
info_items = [r for r in results if r.get('pass') == 'INFO']
security_bugs = [r for r in results if r.get('security_risk','none') != 'none']

print(f'PASS: {len(passed)}')
print(f'FAIL: {len(failed)}')
print(f'SERVER_ERRORS: {len(server_errs)}')
print(f'N/A_404: {len(na_404)}')
print(f'INFO: {len(info_items)}')
print(f'SECURITY_BUGS: {len(security_bugs)}')

print()
print('=== SECURITY BUGS ===')
for b in security_bugs:
    print(f'  !! {b["method"]} {b["endpoint"]} => HTTP {b["status"]} | {b["security_risk"]}')
if not security_bugs:
    print('  None')

print()
print('=== SERVER ERRORS ===')
for e in server_errs:
    print(f'  500: {e["method"]} {e["endpoint"]}')
    print(f'     {e.get("body_preview","")[:200]}')
if not server_errs:
    print('  None')

print()
print('=== FAILED TESTS ===')
for f in failed:
    print(f'  FAIL: {f["label"]} => HTTP {f["status"]} (expected {f["expected"]})')
if not failed:
    print('  None')

print()
print('=== POINTS ANALYSIS ===')
points_results = [r for r in results if r.get('category') in ['points_analyst','points_award_test']]
for r in points_results:
    if r.get('category') == 'points_award_test':
        pts_before = r.get('points_before')
        pts_after = r.get('points_after')
        changed = r.get('points_changed')
        print(f'  [{r["user"]}] Points change on post: before={pts_before} after={pts_after} changed={changed}')
    elif r.get('status') == 200 and r.get('pass') == 'PASS':
        body = r.get('body_preview','')
        print(f'  [{r["user"]}] {r["endpoint"]}: {body[:200]}')

print()
print('=== GAME ROUTES FOUND ===')
game_results = [r for r in results if r.get('category') in ['game_check','game_test']]
for r in game_results:
    body_short = r.get('body_preview','')[:100]
    print(f'  {r["method"]} {r["endpoint"]} => {r["status"]} ({r["pass"]}) | {body_short}')

print()
print('=== ADMIN ACCESS TESTS DETAIL ===')
admin_results = [r for r in results if r.get('category') == 'admin_tester']
for r in admin_results:
    print(f'  [{r["user"]}] {r["method"]} {r["endpoint"]} => {r["status"]} ({r["pass"]})')

print()
print('=== CROSS-USER AUTH TESTS DETAIL ===')
cross_results = [r for r in results if r.get('category') in ['cross_user_auth','admin_tester_cross']]
for r in cross_results:
    print(f'  [{r["user"]}] {r["method"]} {r["endpoint"]} => {r["status"]} ({r["pass"]})')

print()
print('=== OPERATOR TESTS DETAIL ===')
op_results = [r for r in results if r.get('category') == 'operator_test']
for r in op_results:
    body_short = r.get('body_preview','')[:100]
    print(f'  [{r["user"]}] {r["method"]} {r["endpoint"]} => {r["status"]} ({r["pass"]}) | {body_short}')

# Save comprehensive report
users_created = [
    {'username':'testadmin1','email':'testadmin1@test.com','id':299,'password':'Test1234!','category':'admin_tester','status':'created'},
    {'username':'testadmin2','email':'testadmin2@test.com','id':300,'password':'Test1234!','category':'admin_tester','status':'created'},
    {'username':'user01','email':'user01@test.com','id':301,'password':'Test1234!','category':'general','status':'created'},
    {'username':'user02','email':'user02@test.com','id':302,'password':'Test1234!','category':'general','status':'created'},
    {'username':'user03','email':'user03@test.com','id':303,'password':'Test1234!','category':'general','status':'created'},
    {'username':'user04','email':'user04@test.com','id':304,'password':'Test1234!','category':'general','status':'created'},
    {'username':'user05','email':'user05@test.com','id':305,'password':'Test1234!','category':'general','status':'created'},
    {'username':'user06','email':'user06@test.com','id':306,'password':'Test1234!','category':'general','status':'created'},
    {'username':'user07','email':'user07@test.com','id':307,'password':'Test1234!','category':'general','status':'created'},
    {'username':'user08','email':'user08@test.com','id':308,'password':'Test1234!','category':'general','status':'created'},
    {'username':'user09','email':'user09@test.com','id':309,'password':'Test1234!','category':'general','status':'created'},
    {'username':'user10','email':'user10@test.com','id':310,'password':'Test1234!','category':'general','status':'created'},
    {'username':'oper01','email':'oper01@test.com','id':311,'password':'Test1234!','category':'operator','status':'created'},
    {'username':'oper02','email':'oper02@test.com','id':312,'password':'Test1234!','category':'operator','status':'created'},
    {'username':'oper03','email':'oper03@test.com','id':313,'password':'Test1234!','category':'operator','status':'created'},
    {'username':'points01','email':'points01@test.com','id':314,'password':'Test1234!','category':'points_analyst','status':'created'},
    {'username':'points02','email':'points02@test.com','id':315,'password':'Test1234!','category':'points_analyst','status':'created'},
    {'username':'points03','email':'points03@test.com','id':316,'password':'Test1234!','category':'points_analyst','status':'created'},
    {'username':'points04','email':'points04@test.com','id':317,'password':'Test1234!','category':'points_analyst','status':'created'},
    {'username':'points05','email':'points05@test.com','id':318,'password':'Test1234!','category':'points_analyst','status':'created'},
]

final_report = {
    'summary': {
        'total_users_created': 20,
        'total_tests': len(results),
        'passed': len(passed),
        'failed': len(failed),
        'server_errors': len(server_errs),
        'security_bugs': len(security_bugs),
        'missing_features_404': len(na_404),
        'info': len(info_items),
    },
    'users': users_created,
    'security_bugs': security_bugs,
    'server_errors': server_errs,
    'failed_tests': failed,
    'all_test_results': results,
}

with open('C:/Users/Admin/Desktop/somekorean/comprehensive_test_report.json', 'w', encoding='utf-8') as f:
    json.dump(final_report, f, indent=2, ensure_ascii=False)

print(f'\nFull report saved to comprehensive_test_report.json')
ssh.close()
