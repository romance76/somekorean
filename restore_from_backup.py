#!/usr/bin/env python3
"""
Restore from backup: take the /tmp/mobile_backup_0401 files (which have previous session features)
and undo ONLY the mobile-responsive CSS class changes that agents added.
"""
import os, re

APP = '/var/www/somekorean'
BACKUP = '/tmp/mobile_backup_0401'

def undo_mobile(content):
    # Ordered replacements - longer/more specific patterns first
    reps = [
        # Flex layout patterns (search bars, headers)
        ('flex flex-col sm:flex-row items-stretch sm:items-center gap-2', 'flex items-center gap-2'),
        ('flex flex-col sm:flex-row items-stretch sm:items-center', 'flex items-center'),
        ('flex flex-col sm:flex-row sm:items-center justify-between', 'flex items-center justify-between'),
        ('flex flex-col sm:flex-row justify-center gap-2 sm:gap-3', 'flex justify-center gap-3'),
        ('flex flex-col sm:flex-row justify-center', 'flex justify-center'),
        ('flex flex-col sm:flex-row gap-3', 'flex gap-3'),
        ('flex flex-col sm:flex-row gap-2', 'flex gap-2'),
        ('flex flex-col-reverse sm:flex-row justify-end gap-2 sm:space-x-3', 'flex justify-end space-x-3'),
        ('flex flex-col-reverse sm:flex-row justify-end gap-2', 'flex justify-end gap-3'),
        ('flex flex-wrap gap-2 sm:gap-3', 'flex flex-wrap gap-3'),
        ('flex flex-wrap items-center gap-1 sm:gap-3', 'flex items-center gap-3'),

        # Grid patterns
        ('grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4', 'grid-cols-2 md:grid-cols-3 lg:grid-cols-4'),
        ('grid-cols-3 sm:grid-cols-4 md:grid-cols-5 lg:grid-cols-6', 'grid-cols-4 sm:grid-cols-5 lg:grid-cols-6'),
        ('grid-cols-1 sm:grid-cols-2 md:grid-cols-3', 'grid-cols-2 md:grid-cols-3'),
        ('grid-cols-1 sm:grid-cols-2 gap-4', 'grid-cols-2 gap-4'),
        ('grid-cols-1 sm:grid-cols-2 gap-3', 'grid-cols-2 gap-3'),
        ('grid-cols-1 sm:grid-cols-3 gap-4', 'grid-cols-3 gap-4'),
        ('grid-cols-2 sm:grid-cols-4', 'grid-cols-4'),
        ('col-span-2 sm:col-span-3 lg:col-span-4', 'col-span-4'),

        # Combined padding patterns (must be before individual)
        ('px-4 sm:px-6 py-4 sm:py-5 gap-3', 'px-6 py-5'),
        ('px-4 sm:px-6 py-4 sm:py-6 gap-2', 'px-6 py-6'),
        ('px-4 sm:px-6 py-4 sm:py-5', 'px-6 py-5'),
        ('px-4 sm:px-6 py-4 sm:py-6', 'px-6 py-6'),
        ('px-3 sm:px-4 py-1.5 sm:py-2', 'px-4 py-2'),
        ('px-3 sm:px-6 py-2 sm:py-2.5', 'px-6 py-2.5'),

        # Individual padding/gap patterns
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

        # Text size patterns
        ('text-lg sm:text-xl', 'text-xl'),
        ('text-xs sm:text-sm', 'text-sm'),

        # Button padding
        ('p-2 sm:px-3 sm:py-1.5', 'px-3 py-1.5'),

        # Image/map
        ('max-height: clamp(200px, 50vw, 420px)', 'max-height:420px'),
        ('aspect-video sm:aspect-[16/7]', 'aspect-[16/7]'),
        ('min-w-[44px]', 'min-w-12'),

        # Flex sizing
        ('flex-1 sm:flex-auto ', ''),
        ('flex-1 sm:flex-none ', ''),
    ]

    for old, new in reps:
        content = content.replace(old, new)

    # Remove responsive width/self classes (word boundary aware)
    content = re.sub(r'\s+w-full sm:w-auto', '', content)
    content = re.sub(r'\s+self-start sm:self-auto', '', content)
    content = re.sub(r'\s+self-end sm:self-auto', '', content)
    content = re.sub(r'self-start\s+', '', content)

    # Revert hidden sm:inline spans back to plain text
    content = re.sub(r'<span class="hidden sm:inline">(.*?)</span>', r'\1', content)

    # Clean up any double spaces in class attributes
    content = re.sub(r'(class="[^"]*?)  +([^"]*?")', lambda m: m.group(1) + ' ' + m.group(2), content)

    return content

# File mapping: backup filename -> server path
file_map = {
    'resources_js_pages_community_PostDetail.vue': 'resources/js/pages/community/PostDetail.vue',
    'resources_js_pages_community_BoardList.vue': 'resources/js/pages/community/BoardList.vue',
    'resources_js_pages_community_ClubDetail.vue': 'resources/js/pages/community/ClubDetail.vue',
    'resources_js_pages_community_ClubList.vue': 'resources/js/pages/community/ClubList.vue',
    'resources_js_pages_community_QnAHome.vue': 'resources/js/pages/community/QnAHome.vue',
    'resources_js_pages_events_EventCreate.vue': 'resources/js/pages/events/EventCreate.vue',
    'resources_js_pages_events_EventDetail.vue': 'resources/js/pages/events/EventDetail.vue',
    'resources_js_pages_events_EventList.vue': 'resources/js/pages/events/EventList.vue',
    'resources_js_pages_jobs_JobDetail.vue': 'resources/js/pages/jobs/JobDetail.vue',
    'resources_js_pages_jobs_JobList.vue': 'resources/js/pages/jobs/JobList.vue',
    'resources_js_pages_jobs_JobWrite.vue': 'resources/js/pages/jobs/JobWrite.vue',
    'resources_js_pages_recipes_RecipeDetail.vue': 'resources/js/pages/recipes/RecipeDetail.vue',
    'resources_js_pages_recipes_RecipeList.vue': 'resources/js/pages/recipes/RecipeList.vue',
    'resources_js_pages_market_MarketDetail.vue': 'resources/js/pages/market/MarketDetail.vue',
    'resources_js_pages_market_MarketList.vue': 'resources/js/pages/market/MarketList.vue',
    'resources_js_pages_market_MarketWrite.vue': 'resources/js/pages/market/MarketWrite.vue',
    'resources_js_pages_realestate_RealEstateDetail.vue': 'resources/js/pages/realestate/RealEstateDetail.vue',
    'resources_js_pages_realestate_RealEstateList.vue': 'resources/js/pages/realestate/RealEstateList.vue',
    'resources_js_pages_realestate_RealEstateWrite.vue': 'resources/js/pages/realestate/RealEstateWrite.vue',
    'resources_css_app.css': 'resources/css/app.css',
    'resources_js_components_NavBar.vue': 'resources/js/components/NavBar.vue',
}

for bk_name, server_path in file_map.items():
    bk_file = os.path.join(BACKUP, bk_name)
    dest_file = os.path.join(APP, server_path)

    with open(bk_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # Special handling for app.css
    if 'app.css' in bk_name:
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
        with open(dest_file, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f'RESTORED: {server_path} (css special)')
        continue

    # Special handling for NavBar.vue
    if 'NavBar.vue' in bk_name:
        content = content.replace(
            'px-3 sm:px-4 flex items-center h-12 gap-2 sm:gap-3 overflow-hidden',
            'px-4 flex items-center h-12 gap-3'
        )
        content = content.replace('gap-1 sm:gap-1.5', 'gap-1.5')
        content = content.replace(
            'gap-0.5 text-xs font-bold px-1.5 sm:px-2.5 py-1 rounded-lg border transition ml-0.5 sm:ml-1 flex-shrink-0',
            'gap-1 text-xs font-bold px-2.5 py-1 rounded-lg border transition ml-1 flex-shrink-0'
        )
        # Undo split language spans
        content = re.sub(
            r"""<span>\{\{ langStore\.locale === 'ko' \? '🇺🇸' : '🇰🇷' \}\}</span>\s*<span class="hidden sm:inline">\{\{ langStore\.locale === 'ko' \? 'EN' : '한' \}\}</span>""",
            "{{ langStore.locale === 'ko' ? '🇺🇸 EN' : '🇰🇷 한' }}",
            content
        )
        content = content.replace(
            'md:hidden p-1.5 text-gray-600 hover:text-blue-600 flex-shrink-0',
            'md:hidden p-1.5 text-gray-600 hover:text-blue-600 ml-0.5'
        )
        content = content.replace('w-[280px] max-w-[90vw]', 'w-72')
        with open(dest_file, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f'RESTORED: {server_path} (navbar special)')
        continue

    # Special handling for QnAHome.vue
    if 'QnAHome.vue' in bk_name:
        content = content.replace('flex flex-col lg:flex-row', 'flex')
        content = content.replace(' overflow-x-hidden', '')

    # General mobile CSS undo
    reverted = undo_mobile(content)

    with open(dest_file, 'w', encoding='utf-8') as f:
        f.write(reverted)

    changed = content != reverted
    print(f'RESTORED: {server_path}' + (' (reverted mobile css)' if changed else ' (no mobile css found)'))

print('\nAll files restored from backup!')
