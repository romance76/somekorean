<?php

namespace Database\Seeders;

use App\Models\SiteSetting;
use Illuminate\Database\Seeder;

class SiteSettingSeeder extends Seeder
{
    public function run(): void
    {
        $settings = [
            // General
            ['key' => 'site_name',            'value' => 'SomeKorean',                'group' => 'general'],
            ['key' => 'site_description',     'value' => '미국 한인 커뮤니티',          'group' => 'general'],
            ['key' => 'site_url',             'value' => 'https://somekorean.com',     'group' => 'general'],
            ['key' => 'logo',                 'value' => 'logo_00.jpg',               'group' => 'general'],
            ['key' => 'favicon',              'value' => 'favicon.ico',               'group' => 'general'],
            ['key' => 'default_language',     'value' => 'ko',                        'group' => 'general'],
            ['key' => 'timezone',             'value' => 'America/Los_Angeles',       'group' => 'general'],
            ['key' => 'maintenance_mode',     'value' => 'false',                     'group' => 'general'],

            // Appearance
            ['key' => 'primary_color',        'value' => '#3B82F6',                   'group' => 'appearance'],
            ['key' => 'secondary_color',      'value' => '#10B981',                   'group' => 'appearance'],
            ['key' => 'accent_color',         'value' => '#F59E0B',                   'group' => 'appearance'],
            ['key' => 'dark_mode_enabled',    'value' => 'true',                      'group' => 'appearance'],
            ['key' => 'header_style',         'value' => 'default',                   'group' => 'appearance'],
            ['key' => 'footer_text',          'value' => '2026 SomeKorean. All rights reserved.', 'group' => 'appearance'],

            // Features
            ['key' => 'registration_enabled', 'value' => 'true',                      'group' => 'features'],
            ['key' => 'social_login_enabled', 'value' => 'true',                      'group' => 'features'],
            ['key' => 'chat_enabled',         'value' => 'true',                      'group' => 'features'],
            ['key' => 'games_enabled',        'value' => 'true',                      'group' => 'features'],
            ['key' => 'music_enabled',        'value' => 'true',                      'group' => 'features'],
            ['key' => 'shorts_enabled',       'value' => 'true',                      'group' => 'features'],
            ['key' => 'elder_care_enabled',   'value' => 'true',                      'group' => 'features'],
            ['key' => 'group_buy_enabled',    'value' => 'true',                      'group' => 'features'],
            ['key' => 'point_system_enabled', 'value' => 'true',                      'group' => 'features'],

            // Points
            ['key' => 'points_per_post',      'value' => '10',                        'group' => 'points'],
            ['key' => 'points_per_comment',   'value' => '5',                         'group' => 'points'],
            ['key' => 'points_per_login',     'value' => '5',                         'group' => 'points'],
            ['key' => 'points_per_referral',  'value' => '100',                       'group' => 'points'],
            ['key' => 'daily_point_limit',    'value' => '200',                       'group' => 'points'],

            // SEO
            ['key' => 'meta_title',           'value' => 'SomeKorean - 미국 한인 커뮤니티', 'group' => 'seo'],
            ['key' => 'meta_description',     'value' => '미국 한인들을 위한 최고의 커뮤니티 플랫폼. 뉴스, 구인구직, 마켓, 부동산, 맛집, Q&A 등 다양한 정보를 공유하세요.', 'group' => 'seo'],
            ['key' => 'meta_keywords',        'value' => '한인,커뮤니티,미국,한인타운,구인,구직,마켓,부동산,뉴스', 'group' => 'seo'],
            ['key' => 'google_analytics_id',  'value' => '',                          'group' => 'seo'],

            // Notification
            ['key' => 'email_notifications',  'value' => 'true',                      'group' => 'notification'],
            ['key' => 'push_notifications',   'value' => 'true',                      'group' => 'notification'],
            ['key' => 'admin_email',          'value' => 'admin@somekorean.com',      'group' => 'notification'],

            // Content Moderation
            ['key' => 'auto_moderate',        'value' => 'false',                     'group' => 'moderation'],
            ['key' => 'report_threshold',     'value' => '5',                         'group' => 'moderation'],
            ['key' => 'banned_words',         'value' => '',                          'group' => 'moderation'],
            ['key' => 'max_image_size_mb',    'value' => '5',                         'group' => 'moderation'],
            ['key' => 'max_images_per_post',  'value' => '10',                        'group' => 'moderation'],
        ];

        foreach ($settings as $setting) {
            SiteSetting::updateOrCreate(
                ['key' => $setting['key']],
                ['value' => $setting['value'], 'group' => $setting['group']]
            );
        }

        $this->command->info('SiteSettingSeeder: ' . count($settings) . ' site settings created');
    }
}
