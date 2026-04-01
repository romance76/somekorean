import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('68.183.60.70', username='root', password='EhdRh0817wodl')

# Read current router
stdin, stdout, stderr = client.exec_command('cat /var/www/somekorean/resources/js/router/index.js')
content = stdout.read().decode('utf-8')

# Replace old community routes with new ones
old_routes = """    // 지식인 (커뮤니티)
    { path: '/community',           component: () => import('../pages/community/QnAHome.vue'),    name: 'boards' },
    { path: '/community/boards',    component: () => import('../pages/community/BoardList.vue'),  name: 'board-list' },
    { path: '/community/write',     component: () => import('../pages/community/PostWrite.vue'),  name: 'post-write',  meta: { auth: true } },
    { path: '/community/post/:id',  component: () => import('../pages/community/PostDetail.vue'), name: 'post-detail' },
    { path: '/community/:slug',     component: () => import('../pages/community/PostList.vue'),   name: 'post-list' },"""

new_routes = """    // 커뮤니티 v2
    { path: '/community',            component: () => import('../pages/community/CommunityHome.vue'),     name: 'community-home' },
    { path: '/community/write',      component: () => import('../pages/community/CommunityWrite.vue'),    name: 'community-write', meta: { auth: true } },
    { path: '/community/:slug',      component: () => import('../pages/community/CommunityCategory.vue'), name: 'community-category' },
    { path: '/community/:slug/:id',  component: () => import('../pages/community/CommunityPost.vue'),     name: 'community-post' },
    { path: '/community/:slug/:id/edit', component: () => import('../pages/community/CommunityWrite.vue'), name: 'community-edit', meta: { auth: true } },"""

if old_routes in content:
    content = content.replace(old_routes, new_routes)
    print('Router routes replaced successfully')
else:
    print('WARNING: Could not find exact old routes block. Trying line-by-line...')
    # Try a more flexible approach
    lines = content.split('\n')
    new_lines = []
    skip = False
    replaced = False
    for line in lines:
        if '// 지식인 (커뮤니티)' in line or "// 지식인" in line:
            # Insert new routes
            new_lines.append('    // 커뮤니티 v2')
            new_lines.append("    { path: '/community',            component: () => import('../pages/community/CommunityHome.vue'),     name: 'community-home' },")
            new_lines.append("    { path: '/community/write',      component: () => import('../pages/community/CommunityWrite.vue'),    name: 'community-write', meta: { auth: true } },")
            new_lines.append("    { path: '/community/:slug',      component: () => import('../pages/community/CommunityCategory.vue'), name: 'community-category' },")
            new_lines.append("    { path: '/community/:slug/:id',  component: () => import('../pages/community/CommunityPost.vue'),     name: 'community-post' },")
            new_lines.append("    { path: '/community/:slug/:id/edit', component: () => import('../pages/community/CommunityWrite.vue'), name: 'community-edit', meta: { auth: true } },")
            skip = True
            replaced = True
            continue
        if skip:
            # Skip old community route lines
            stripped = line.strip()
            if stripped.startswith("{ path: '/community") and ("QnAHome" in line or "BoardList" in line or "PostWrite" in line or "PostDetail" in line or "PostList" in line):
                continue
            else:
                skip = False
                new_lines.append(line)
        else:
            new_lines.append(line)

    if replaced:
        content = '\n'.join(new_lines)
        print('Router routes replaced via line-by-line method')
    else:
        print('ERROR: Could not find community routes to replace')

# Write back
sftp = client.open_sftp()
with sftp.open('/var/www/somekorean/resources/js/router/index.js', 'w') as f:
    f.write(content)
sftp.close()

print('Router file updated!')
client.close()
