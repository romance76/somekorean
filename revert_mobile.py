#!/usr/bin/env python3
import os, re, subprocess

APP = '/var/www/somekorean'

def undo_mobile_classes(content):
    replacements = [
        ('flex flex-col sm:flex-row items-stretch sm:items-center gap-2', 'flex items-center gap-2'),
        ('flex flex-col sm:flex-row items-stretch sm:items-center', 'flex items-center'),
        ('flex flex-col sm:flex-row sm:items-center justify-between', 'flex items-center justify-between'),
        ('flex flex-col sm:flex-row justify-center', 'flex justify-center'),
        ('flex flex-col sm:flex-row gap-3', 'flex gap-3'),
        ('flex flex-col sm:flex-row gap-2', 'flex gap-2'),
        ('flex flex-col-reverse sm:flex-row justify-end gap-2 sm:space-x-3', 'flex justify-end space-x-3'),
        ('flex flex-col-reverse sm:flex-row justify-end gap-2', 'flex justify-end gap-3'),
        ('flex flex-wrap gap-2 sm:gap-3', 'flex flex-wrap gap-3'),
        ('flex flex-wrap items-center gap-1 sm:gap-3', 'flex items-center gap-3'),
        ('grid-cols-1 sm:grid-cols-2 md:grid-cols-3', 'grid-cols-2 md:grid-cols-3'),
        ('grid-cols-1 sm:grid-cols-2 gap-4', 'grid-cols-2 gap-4'),
        ('grid-cols-1 sm:grid-cols-2 gap-3', 'grid-cols-2 gap-3'),
        ('grid-cols-1 sm:grid-cols-3 gap-4', 'grid-cols-3 gap-4'),
        ('grid-cols-2 sm:grid-cols-4', 'grid-cols-4'),
        ('grid-cols-3 sm:grid-cols-4 md:grid-cols-5 lg:grid-cols-6', 'grid-cols-4 sm:grid-cols-5 lg:grid-cols-6'),
        ('grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4', 'grid-cols-2 md:grid-cols-3 lg:grid-cols-4'),
        ('col-span-2 sm:col-span-3 lg:col-span-4', 'col-span-4'),
        ('px-4 sm:px-6 py-4 sm:py-5 gap-3', 'px-6 py-5'),
        ('px-4 sm:px-6 py-4 sm:py-6 gap-2', 'px-6 py-6'),
        ('px-4 sm:px-6 py-4 sm:py-5', 'px-6 py-5'),
        ('px-4 sm:px-6 py-4 sm:py-6', 'px-6 py-6'),
        ('px-4 sm:px-6', 'px-6'),
        ('py-4 sm:py-5', 'py-5'),
        ('py-4 sm:py-6', 'py-6'),
        ('px-3 sm:px-4', 'px-4'),
        ('py-1.5 sm:py-2', 'py-2'),
        ('px-2.5 sm:px-4', 'px-4'),
        ('px-2.5 sm:px-3', 'px-3'),
        ('px-2 sm:px-3', 'px-3'),
        ('py-1 sm:py-1.5', 'py-1.5'),
        ('px-3 sm:px-6', 'px-6'),
        ('py-2 sm:py-2.5', 'py-2.5'),
        ('gap-2 sm:gap-3', 'gap-3'),
        ('gap-1 sm:gap-3', 'gap-3'),
        ('h-20 sm:h-24', 'h-24'),
        ('h-[200px] sm:h-[300px]', 'h-[300px]'),
        ('text-lg sm:text-xl', 'text-xl'),
        ('text-xs sm:text-sm', 'text-sm'),
        ('p-2 sm:px-3 sm:py-1.5', 'px-3 py-1.5'),
        ('max-height: clamp(200px, 50vw, 420px)', 'max-height:420px'),
        ('aspect-video sm:aspect-[16/7]', 'aspect-[16/7]'),
        ('min-w-[44px]', 'min-w-12'),
        ('flex-1 sm:flex-auto ', ''),
    ]
    for old, new in replacements:
        content = content.replace(old, new)
    # Remove w-full sm:w-auto
    content = re.sub(r'\s+w-full sm:w-auto', '', content)
    content = re.sub(r'\s+self-start sm:self-auto', '', content)
    content = re.sub(r'\s+self-end sm:self-auto', '', content)
    content = re.sub(r'\bself-start\s+', '', content)
    # Revert hidden sm:inline spans
    content = re.sub(r'<span class="hidden sm:inline">(.*?)</span>', r'\1', content)
    # Clean double spaces in class attrs
    content = re.sub(r'class="([^"]*?)  +', lambda m: 'class="' + re.sub(r'  +', ' ', m.group(1)), content)
    return content

# Files to revert from git (only mobile changes, no previous session changes)
git_restore = [
    'resources/js/pages/events/EventCreate.vue',
    'resources/js/pages/realestate/RealEstateDetail.vue',
]
for f in git_restore:
    subprocess.run(['git', 'checkout', 'HEAD', '--', f], cwd=APP)
    print(f'GIT: {f}')

# Files to undo mobile classes
mobile_files = [
    'resources/js/pages/community/PostDetail.vue',
    'resources/js/pages/community/ClubDetail.vue',
    'resources/js/pages/community/ClubList.vue',
    'resources/js/pages/events/EventDetail.vue',
    'resources/js/pages/events/EventList.vue',
    'resources/js/pages/jobs/JobDetail.vue',
    'resources/js/pages/jobs/JobList.vue',
    'resources/js/pages/jobs/JobWrite.vue',
    'resources/js/pages/recipes/RecipeDetail.vue',
    'resources/js/pages/recipes/RecipeList.vue',
    'resources/js/pages/market/MarketDetail.vue',
    'resources/js/pages/market/MarketList.vue',
    'resources/js/pages/market/MarketWrite.vue',
    'resources/js/pages/realestate/RealEstateList.vue',
    'resources/js/pages/realestate/RealEstateWrite.vue',
]
for f in mobile_files:
    fp = os.path.join(APP, f)
    with open(fp, 'r', encoding='utf-8') as fh:
        content = fh.read()
    reverted = undo_mobile_classes(content)
    if content != reverted:
        with open(fp, 'w', encoding='utf-8') as fh:
            fh.write(reverted)
        print(f'REVERTED: {f}')
    else:
        print(f'NO CHANGE: {f}')

# Revert BoardList.vue (has more changes from previous sessions)
fp = os.path.join(APP, 'resources/js/pages/community/BoardList.vue')
with open(fp, 'r', encoding='utf-8') as fh:
    content = fh.read()
reverted = undo_mobile_classes(content)
if content != reverted:
    with open(fp, 'w', encoding='utf-8') as fh:
        fh.write(reverted)
    print('REVERTED: BoardList.vue')

# Revert QnAHome.vue - undo the flex-col lg:flex-row change
fp = os.path.join(APP, 'resources/js/pages/community/QnAHome.vue')
with open(fp, 'r', encoding='utf-8') as fh:
    content = fh.read()
content = content.replace('flex flex-col lg:flex-row', 'flex')
content = content.replace('overflow-x-hidden', '')
reverted = undo_mobile_classes(content)
with open(fp, 'w', encoding='utf-8') as fh:
    fh.write(reverted)
print('REVERTED: QnAHome.vue')

# Revert NavBar.vue
fp = os.path.join(APP, 'resources/js/components/NavBar.vue')
with open(fp, 'r', encoding='utf-8') as fh:
    content = fh.read()
# Undo Row 1 changes
content = content.replace(
    'px-3 sm:px-4 flex items-center h-12 gap-2 sm:gap-3 overflow-hidden',
    'px-4 flex items-center h-12 gap-3'
)
# Undo right side gap
content = content.replace('gap-1 sm:gap-1.5', 'gap-1.5')
# Undo language button
content = content.replace(
    'gap-0.5 text-xs font-bold px-1.5 sm:px-2.5 py-1 rounded-lg border transition ml-0.5 sm:ml-1 flex-shrink-0',
    'gap-1 text-xs font-bold px-2.5 py-1 rounded-lg border transition ml-1 flex-shrink-0'
)
# Undo language button split spans
content = re.sub(
    r"<span>\{\{ langStore\.locale === 'ko' \? '....' : '....' \}\}</span>\s*<span class=\"hidden sm:inline\">\{\{ langStore\.locale === 'ko' \? 'EN' : '...' \}\}</span>",
    "{{ langStore.locale === 'ko' ? '🇺🇸 EN' : '🇰🇷 한' }}",
    content
)
# Simple approach: replace the entire language button content
content = re.sub(
    r"<span>\{\{ langStore\.locale === 'ko' \? '🇺🇸' : '🇰🇷' \}\}</span>\s*<span class=\"hidden sm:inline\">\{\{ langStore\.locale === 'ko' \? 'EN' : '한' \}\}</span>",
    "{{ langStore.locale === 'ko' ? '🇺🇸 EN' : '🇰🇷 한' }}",
    content
)
# Undo hamburger
content = content.replace(
    'md:hidden p-1.5 text-gray-600 hover:text-blue-600 flex-shrink-0',
    'md:hidden p-1.5 text-gray-600 hover:text-blue-600 ml-0.5'
)
# Undo drawer width
content = content.replace('w-[280px] max-w-[90vw]', 'w-72')
with open(fp, 'w', encoding='utf-8') as fh:
    fh.write(content)
print('REVERTED: NavBar.vue')

# Revert app.css
fp = os.path.join(APP, 'resources/css/app.css')
with open(fp, 'r', encoding='utf-8') as fh:
    content = fh.read()
content = content.replace(
    '''    html, body {
        font-family: 'Noto Sans KR', sans-serif;
        overflow-x: hidden;
        max-width: 100vw;
    }
    #somekorean-app {
        overflow-x: hidden;
        max-width: 100vw;
    }''',
    '''    body {
        font-family: 'Noto Sans KR', sans-serif;
    }'''
)
with open(fp, 'w', encoding='utf-8') as fh:
    fh.write(content)
print('REVERTED: app.css')

print('\nAll reverts done!')
