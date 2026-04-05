<?php

namespace App\Http\Controllers\API;

use App\Http\Controllers\Controller;
use App\Models\ElderCheckinLog;
use App\Models\ElderSetting;
use App\Models\ElderSosLog;
use App\Models\Notification;
use App\Models\User;
use Illuminate\Http\Request;
use Illuminate\Support\Carbon;
use Illuminate\Support\Facades\Auth;
use Illuminate\Support\Facades\DB;

class ElderController extends Controller
{
    // ─── 1. settings ─────────────────────────────────────────────
    public function settings()
    {
        try {
            $settings = ElderSetting::firstOrCreate(
                ['user_id' => Auth::id()],
                ['elder_mode' => false, 'checkin_interval' => 24]
            );

            $logs = ElderCheckinLog::where('user_id', Auth::id())
                ->where('checkin_date', '>=', now()->subDays(7))
                ->orderBy('checkin_date', 'desc')
                ->get();

            return response()->json([
                'settings' => $settings,
                'recent_logs' => $logs,
            ]);
        } catch (\Exception $e) {
            return response()->json(['message' => '설정을 불러오는 중 오류가 발생했습니다.', 'error' => $e->getMessage()], 500);
        }
    }

    // ─── 2. updateSettings ───────────────────────────────────────
    public function updateSettings(Request $request)
    {
        try {
            $data = $request->validate([
                'elder_mode'        => 'sometimes|boolean',
                'guardian_name'     => 'nullable|string|max:50',
                'guardian_phone'    => 'nullable|string|max:20',
                'guardian2_name'    => 'nullable|string|max:50',
                'guardian2_phone'   => 'nullable|string|max:20',
                'checkin_interval'  => 'sometimes|integer|in:12,24,48',
                'checkin_time'      => 'nullable|string|max:5',
                'checkin_enabled'   => 'sometimes|boolean',
                'sos_enabled'       => 'sometimes|boolean',
                'auto_call_enabled' => 'sometimes|boolean',
                'timezone'          => 'nullable|string|max:50',
            ]);

            $settings = ElderSetting::updateOrCreate(
                ['user_id' => Auth::id()],
                $data
            );

            return response()->json($settings);
        } catch (\Exception $e) {
            return response()->json(['message' => '설정 업데이트 중 오류가 발생했습니다.', 'error' => $e->getMessage()], 500);
        }
    }

    // ─── 3. checkin ──────────────────────────────────────────────
    public function checkin()
    {
        try {
            $user = Auth::user();
            $settings = ElderSetting::firstOrCreate(
                ['user_id' => $user->id],
                ['elder_mode' => true, 'checkin_interval' => 24]
            );

            $now = now();
            $today = $now->toDateString();

            // Update or create today's checkin log
            $log = ElderCheckinLog::updateOrCreate(
                ['user_id' => $user->id, 'checkin_date' => $today],
                ['checked_at' => $now, 'status' => 'checked']
            );

            // Reset missed count & update settings
            $settings->update([
                'last_checkin_at' => $now,
                'alert_sent'     => false,
                'missed_count'   => 0,
            ]);

            // Award points if first check-in today
            $pointsEarned = 0;
            if ($log->wasRecentlyCreated || $log->wasChanged()) {
                $pointsEarned = 5;
                $user->addPoints($pointsEarned, 'elder_checkin', 'earn', null, '노인안심 체크인');
            }

            return response()->json([
                'message'       => '체크인 완료!',
                'points_earned' => $pointsEarned,
                'checked_at'    => $now,
                'log'           => $log,
            ]);
        } catch (\Exception $e) {
            return response()->json(['message' => '체크인 중 오류가 발생했습니다.', 'error' => $e->getMessage()], 500);
        }
    }

    // ─── 4. sos ──────────────────────────────────────────────────
    public function sos(Request $request)
    {
        try {
            $user = Auth::user();
            $settings = ElderSetting::firstOrCreate(
                ['user_id' => $user->id],
                ['elder_mode' => true]
            );

            $settings->update(['last_sos_at' => now()]);

            // Create SOS alert record
            $sosId = DB::table('elder_sos_alerts')->insertGetId([
                'user_id'    => $user->id,
                'latitude'   => $request->input('latitude') ?? $request->input('lat'),
                'longitude'  => $request->input('longitude') ?? $request->input('lng'),
                'address'    => $request->input('address'),
                'status'     => 'active',
                'created_at' => now(),
                'updated_at' => now(),
            ]);

            // Also create legacy SOS log for backward compatibility
            $sosLog = ElderSosLog::create([
                'user_id' => $user->id,
                'lat'     => $request->input('latitude') ?? $request->input('lat'),
                'lng'     => $request->input('longitude') ?? $request->input('lng'),
                'status'  => 'triggered',
            ]);

            // Update today's checkin log status
            ElderCheckinLog::updateOrCreate(
                ['user_id' => $user->id, 'checkin_date' => now()->toDateString()],
                ['status' => 'sos']
            );

            // Notify all guardians
            $guardianIds = collect();

            // Primary guardian
            if ($settings->guardian_user_id) {
                $guardianIds->push($settings->guardian_user_id);
            }

            // Also check elder_settings for any guardians watching this senior
            $additionalGuardians = DB::table('elder_settings')
                ->where('guardian_user_id', '!=', null)
                ->where('user_id', '!=', $user->id)
                ->pluck('guardian_user_id');

            // Primary guardian notification
            if ($settings->guardian_user_id) {
                Notification::create([
                    'user_id' => $settings->guardian_user_id,
                    'type'    => 'elder_sos',
                    'title'   => 'SOS 긴급 알림',
                    'body'    => ($user->nickname ?? $user->name) . '님이 SOS 긴급 신호를 보냈습니다.',
                    'data'    => json_encode([
                        'sos_id'  => $sosId,
                        'user_id' => $user->id,
                        'lat'     => $request->input('latitude') ?? $request->input('lat'),
                        'lng'     => $request->input('longitude') ?? $request->input('lng'),
                    ]),
                    'url'     => '/elder/guardian?sos=' . $sosId,
                ]);
            }

            // 보호자에게 소켓/푸시 알림
            if ($settings->guardian_user_id) {
                try {
                    \Illuminate\Support\Facades\Http::post('http://127.0.0.1:3001/send-notification', [
                        'userId' => (string) $settings->guardian_user_id,
                        'event' => 'elder:sos-alert',
                        'data' => [
                            'title' => '긴급 SOS',
                            'message' => ($user->nickname ?? $user->name) . '님이 SOS를 발동했습니다!',
                            'body' => ($user->nickname ?? $user->name) . '님이 SOS를 발동했습니다!',
                            'url' => '/elder/guardian',
                            'elderId' => $user->id,
                            'elderName' => $user->nickname ?? $user->name,
                            'lat' => $request->input('latitude') ?? $request->input('lat'),
                            'lng' => $request->input('longitude') ?? $request->input('lng'),
                            'address' => $request->input('address'),
                        ]
                    ]);
                } catch (\Exception $e) {
                    \Log::error('SOS push notification failed: ' . $e->getMessage());
                }
            }

            $guardianPhone = $settings->guardian_phone;
            $guardianName  = $settings->guardian_name ?? '보호자';

            return response()->json([
                'success'       => true,
                'message'       => 'SOS 신호가 발송되었습니다.',
                'sos_id'        => $sosId,
                'guardian_name' => $guardianName,
                'sent_to'       => $guardianPhone
                    ? substr($guardianPhone, 0, 3) . '****' . substr($guardianPhone, -4)
                    : null,
            ]);
        } catch (\Exception $e) {
            return response()->json(['message' => 'SOS 발송 중 오류가 발생했습니다.', 'error' => $e->getMessage()], 500);
        }
    }

    // ─── 5. guardianView ─────────────────────────────────────────
    public function guardianView($userId)
    {
        try {
            $user     = User::findOrFail($userId);
            $settings = ElderSetting::where('user_id', $userId)->first();

            if (!$settings || !$settings->elder_mode) {
                return response()->json(['message' => '해당 회원의 노인 안심 모드가 활성화되지 않았습니다.'], 404);
            }

            // Verify caller is the guardian
            $caller = Auth::user();
            $isGuardian = ($settings->guardian_user_id === $caller->id) || $caller->is_admin;
            if (!$isGuardian) {
                return response()->json(['message' => '보호자 권한이 없습니다.'], 403);
            }

            $checkinLogs = ElderCheckinLog::where('user_id', $userId)
                ->where('checkin_date', '>=', now()->subDays(30))
                ->orderBy('checkin_date', 'desc')
                ->get();

            $sosLogs = ElderSosLog::where('user_id', $userId)
                ->orderBy('created_at', 'desc')
                ->limit(20)
                ->get();

            // Health records (last 30 days)
            $healthRecords = DB::table('elder_health_records')
                ->where('user_id', $userId)
                ->where('recorded_at', '>=', now()->subDays(30))
                ->orderBy('recorded_at', 'desc')
                ->get();

            // Medication info
            $medications = json_decode($settings->medication_times ?? '[]', true);
            if (!is_array($medications)) $medications = [];
            $medicationTotal = count($medications);
            $medicationTaken = DB::table('elder_medication_logs')
                ->where('user_id', $userId)
                ->whereDate('taken_at', now()->toDateString())
                ->count();

            // Today checked
            $todayChecked = ElderCheckinLog::where('user_id', $userId)
                ->where('checkin_date', now()->toDateString())
                ->where('status', 'checked')
                ->exists();

            // Calculate streak
            $checkedDates = $checkinLogs->where('status', 'checked')->pluck('checkin_date')->map(fn($d) => $d->format('Y-m-d'))->toArray();
            $streak = 0;
            $today = now()->startOfDay();
            for ($i = 0; $i < 365; $i++) {
                $dateStr = $today->copy()->subDays($i)->format('Y-m-d');
                if (in_array($dateStr, $checkedDates)) {
                    $streak++;
                } elseif ($i > 0) {
                    break;
                }
            }

            $overdue = false;
            if ($settings->last_checkin_at) {
                $hoursAgo = $settings->last_checkin_at->diffInHours(now());
                $overdue  = $hoursAgo > $settings->checkin_interval;
            } else {
                $overdue = true;
            }

            // Recent notifications for this elder
            $recentNotifications = Notification::where('user_id', $caller->id)
                ->where(function ($q) use ($userId) {
                    $q->where('url', 'like', "%/elder/guardian/{$userId}%")
                      ->orWhere('url', 'like', '%/elder/guardian%');
                })
                ->orderBy('created_at', 'desc')
                ->limit(10)
                ->get();

            return response()->json([
                'user'              => ['id' => $user->id, 'name' => $user->name, 'nickname' => $user->nickname],
                'settings'          => $settings->only(['checkin_interval', 'checkin_time', 'checkin_enabled', 'last_checkin_at', 'last_sos_at', 'missed_count']),
                'is_overdue'        => $overdue,
                'alert_sent'        => $settings->alert_sent,
                'checkin_logs'      => $checkinLogs,
                'checkin_history'   => $checkinLogs,
                'sos_logs'          => $sosLogs,
                'sos_history'       => $sosLogs,
                'health_records'    => $healthRecords,
                'today_checked'     => $todayChecked,
                'last_checkin_at'   => $settings->last_checkin_at,
                'streak'            => $streak,
                'medication_taken'  => $medicationTaken,
                'medication_total'  => $medicationTotal,
                'notifications'     => $recentNotifications,
            ]);
        } catch (\Exception $e) {
            return response()->json(['message' => '보호자 대시보드 조회 중 오류가 발생했습니다.', 'error' => $e->getMessage()], 500);
        }
    }

    // ─── 6. checkinHistory ───────────────────────────────────────
    public function checkinHistory(Request $request)
    {
        try {
            $month = $request->input('month', now()->format('Y-m'));
            $start = Carbon::parse($month . '-01')->startOfMonth();
            $end   = Carbon::parse($month . '-01')->endOfMonth();

            $logs = ElderCheckinLog::where('user_id', Auth::id())
                ->whereBetween('checkin_date', [$start, $end])
                ->orderBy('checkin_date')
                ->get();

            return response()->json([
                'month' => $month,
                'logs'  => $logs,
                'stats' => [
                    'total'   => $logs->count(),
                    'checked' => $logs->where('status', 'checked')->count(),
                    'missed'  => $logs->where('status', 'missed')->count(),
                    'sos'     => $logs->where('status', 'sos')->count(),
                ],
            ]);
        } catch (\Exception $e) {
            return response()->json(['message' => '체크인 기록 조회 중 오류가 발생했습니다.', 'error' => $e->getMessage()], 500);
        }
    }

    // ─── 7. sosHistory ───────────────────────────────────────────
    public function sosHistory()
    {
        try {
            $logs = ElderSosLog::where('user_id', Auth::id())
                ->orderBy('created_at', 'desc')
                ->paginate(20);

            return response()->json($logs);
        } catch (\Exception $e) {
            return response()->json(['message' => 'SOS 기록 조회 중 오류가 발생했습니다.', 'error' => $e->getMessage()], 500);
        }
    }

    // ─── 8. resolveSos ───────────────────────────────────────────
    public function resolveSos(Request $request, $id)
    {
        try {
            $sosLog = ElderSosLog::findOrFail($id);

            // Verify caller is guardian or admin
            $caller   = Auth::user();
            $settings = ElderSetting::where('user_id', $sosLog->user_id)->first();
            $isGuardian = $settings && $settings->guardian_user_id === $caller->id;
            if (!$isGuardian && !$caller->is_admin && $sosLog->user_id !== $caller->id) {
                return response()->json(['message' => '권한이 없습니다.'], 403);
            }

            $status = $request->input('status', 'resolved');
            if (!in_array($status, ['resolved', 'false_alarm'])) {
                $status = 'resolved';
            }

            $sosLog->update([
                'status'      => $status,
                'resolved_at' => now(),
                'resolved_by' => $caller->id,
                'note'        => $request->input('note'),
            ]);

            // Notify the elder user
            if ($sosLog->user_id !== $caller->id) {
                Notification::create([
                    'user_id' => $sosLog->user_id,
                    'type'    => 'elder_sos',
                    'title'   => 'SOS 해제',
                    'body'    => 'SOS 신호가 ' . ($status === 'resolved' ? '확인 처리' : '오인 처리') . '되었습니다.',
                    'data'    => json_encode(['sos_id' => $sosLog->id]),
                    'url'     => '/elder/sos-history',
                ]);
            }

            return response()->json([
                'message' => 'SOS가 해제되었습니다.',
                'sos_log' => $sosLog->fresh(),
            ]);
        } catch (\Exception $e) {
            return response()->json(['message' => 'SOS 해제 중 오류가 발생했습니다.', 'error' => $e->getMessage()], 500);
        }
    }

    // ─── 9. guardianSearch ───────────────────────────────────────
    public function guardianSearch(Request $request)
    {
        try {
            $query = $request->input('q', '');
            if (strlen($query) < 2) {
                return response()->json(['message' => '2글자 이상 입력해주세요.'], 422);
            }

            $users = User::where(function ($q) use ($query) {
                $q->where('email', 'like', "%{$query}%")
                  ->orWhere('nickname', 'like', "%{$query}%")
                  ->orWhere('name', 'like', "%{$query}%");
            })
            ->where('id', '!=', Auth::id())
            ->select('id', 'name', 'nickname', 'email')
            ->limit(10)
            ->get();

            // Mask email for privacy
            $users->transform(function ($user) {
                $email = $user->email;
                $parts = explode('@', $email);
                if (strlen($parts[0]) > 2) {
                    $parts[0] = substr($parts[0], 0, 2) . str_repeat('*', strlen($parts[0]) - 2);
                }
                $user->email = implode('@', $parts);
                return $user;
            });

            return response()->json($users);
        } catch (\Exception $e) {
            return response()->json(['message' => '보호자 검색 중 오류가 발생했습니다.', 'error' => $e->getMessage()], 500);
        }
    }

    // ─── 10. linkGuardian ────────────────────────────────────────
    public function linkGuardian(Request $request)
    {
        try {
            $data = $request->validate([
                'guardian_user_id' => 'required|integer|exists:users,id',
            ]);

            if ($data['guardian_user_id'] == Auth::id()) {
                return response()->json(['message' => '본인을 보호자로 지정할 수 없습니다.'], 422);
            }

            $settings = ElderSetting::firstOrCreate(
                ['user_id' => Auth::id()],
                ['elder_mode' => true]
            );

            $guardian = User::findOrFail($data['guardian_user_id']);
            $settings->update([
                'guardian_user_id' => $guardian->id,
                'guardian_name'    => $settings->guardian_name ?: ($guardian->nickname ?? $guardian->name),
            ]);

            // Notify the guardian
            Notification::create([
                'user_id' => $guardian->id,
                'type'    => 'elder_sos',
                'title'   => '노인안심 보호자 지정',
                'body'    => (Auth::user()->nickname ?? Auth::user()->name) . '님이 귀하를 보호자로 지정했습니다.',
                'data'    => json_encode(['elder_user_id' => Auth::id()]),
                'url'     => '/elder/guardian/' . Auth::id(),
            ]);

            return response()->json([
                'message'  => '보호자가 연결되었습니다.',
                'guardian' => [
                    'id'       => $guardian->id,
                    'name'     => $guardian->name,
                    'nickname' => $guardian->nickname,
                ],
            ]);
        } catch (\Exception $e) {
            return response()->json(['message' => '보호자 연결 중 오류가 발생했습니다.', 'error' => $e->getMessage()], 500);
        }
    }

    // ─── Health Records ─────────────────────────────────────────

    // POST /api/elder/health-record - 건강 기록 저장
    public function storeHealthRecord(Request $request)
    {
        try {
            $request->validate([
                'blood_pressure_systolic'  => 'nullable|integer|min:60|max:250',
                'blood_pressure_diastolic' => 'nullable|integer|min:40|max:150',
                'blood_sugar'              => 'nullable|integer|min:30|max:600',
                'weight'                   => 'nullable|numeric|min:20|max:300',
            ]);

            DB::table('elder_health_records')->insert([
                'user_id'                  => Auth::id(),
                'blood_pressure_systolic'  => $request->blood_pressure_systolic,
                'blood_pressure_diastolic' => $request->blood_pressure_diastolic,
                'blood_sugar'              => $request->blood_sugar,
                'weight'                   => $request->weight,
                'recorded_at'              => now(),
                'created_at'               => now(),
            ]);

            return response()->json(['success' => true, 'message' => '건강 기록이 저장되었습니다.']);
        } catch (\Exception $e) {
            return response()->json(['message' => '건강 기록 저장 중 오류가 발생했습니다.', 'error' => $e->getMessage()], 500);
        }
    }

    // GET /api/elder/health-records - 건강 기록 목록
    public function healthRecords(Request $request)
    {
        try {
            $userId = $request->input('user_id', Auth::id());

            // If requesting another user's records, verify guardian access
            if ($userId != Auth::id()) {
                $settings = ElderSetting::where('user_id', $userId)->first();
                $caller = Auth::user();
                if (!$settings || ($settings->guardian_user_id !== $caller->id && !$caller->is_admin)) {
                    return response()->json(['message' => '권한이 없습니다.'], 403);
                }
            }

            $records = DB::table('elder_health_records')
                ->where('user_id', $userId)
                ->orderBy('recorded_at', 'desc')
                ->paginate(30);

            return response()->json($records);
        } catch (\Exception $e) {
            return response()->json(['message' => '건강 기록 조회 중 오류가 발생했습니다.', 'error' => $e->getMessage()], 500);
        }
    }

    // ─── Medications ─────────────────────────────────────────────

    // POST /api/elder/medications - 복약 알림 설정
    public function setMedication(Request $request)
    {
        try {
            $request->validate([
                'name' => 'required|string|max:100',
                'time' => 'required|string',
                'days' => 'required|array',
            ]);

            $settings = ElderSetting::firstOrCreate(
                ['user_id' => Auth::id()],
                ['elder_mode' => true]
            );

            $medications = json_decode($settings->medication_times ?? '[]', true);
            if (!is_array($medications)) $medications = [];

            $medications[] = [
                'id'   => uniqid(),
                'name' => $request->name,
                'time' => $request->time,
                'days' => $request->days,
            ];

            $settings->update(['medication_times' => json_encode($medications)]);

            return response()->json(['success' => true, 'medications' => $medications]);
        } catch (\Exception $e) {
            return response()->json(['message' => '복약 알림 설정 중 오류가 발생했습니다.', 'error' => $e->getMessage()], 500);
        }
    }

    // GET /api/elder/medications - 복약 알림 목록 + 오늘 복약 기록
    public function getMedications()
    {
        try {
            $settings = ElderSetting::where('user_id', Auth::id())->first();
            $medications = [];
            if ($settings) {
                $medications = json_decode($settings->medication_times ?? '[]', true);
                if (!is_array($medications)) $medications = [];
            }

            $todayLogs = DB::table('elder_medication_logs')
                ->where('user_id', Auth::id())
                ->whereDate('taken_at', now()->toDateString())
                ->get();

            return response()->json([
                'medications' => $medications,
                'today_logs'  => $todayLogs,
            ]);
        } catch (\Exception $e) {
            return response()->json(['message' => '복약 알림 조회 중 오류가 발생했습니다.', 'error' => $e->getMessage()], 500);
        }
    }

    // POST /api/elder/medications/{id}/taken - 복약 완료
    public function medicationTaken($id)
    {
        try {
            DB::table('elder_medication_logs')->insert([
                'user_id'       => Auth::id(),
                'medication_id' => $id,
                'taken_at'      => now(),
                'created_at'    => now(),
            ]);

            return response()->json(['success' => true, 'message' => '복약 완료가 기록되었습니다.']);
        } catch (\Exception $e) {
            return response()->json(['message' => '복약 완료 처리 중 오류가 발생했습니다.', 'error' => $e->getMessage()], 500);
        }
    }

    // DELETE /api/elder/medications/{id} - 복약 알림 삭제
    public function deleteMedication($id)
    {
        try {
            $settings = ElderSetting::where('user_id', Auth::id())->first();
            if (!$settings) {
                return response()->json(['message' => '설정을 찾을 수 없습니다.'], 404);
            }

            $medications = json_decode($settings->medication_times ?? '[]', true);
            if (!is_array($medications)) $medications = [];

            $medications = array_values(array_filter($medications, fn($m) => ($m['id'] ?? '') !== $id));

            $settings->update(['medication_times' => json_encode($medications)]);

            return response()->json(['success' => true]);
        } catch (\Exception $e) {
            return response()->json(['message' => '복약 알림 삭제 중 오류가 발생했습니다.', 'error' => $e->getMessage()], 500);
        }
    }

    // ═══════════════════════════════════════════════════════════════
    // ADMIN METHODS
    // ═══════════════════════════════════════════════════════════════

    // ─── 11. adminMonitor ────────────────────────────────────────
    public function adminMonitor(Request $request)
    {
        try {
            $today = now()->toDateString();

            $query = ElderSetting::where('elder_mode', true)
                ->with(['user:id,name,nickname,email']);

            // Search
            if ($search = $request->input('search')) {
                $query->whereHas('user', function ($q) use ($search) {
                    $q->where('name', 'like', "%{$search}%")
                      ->orWhere('nickname', 'like', "%{$search}%")
                      ->orWhere('email', 'like', "%{$search}%");
                });
            }

            $elders = $query->orderBy('missed_count', 'desc')->paginate(30);

            // Today's checkin stats
            $todayLogs = ElderCheckinLog::where('checkin_date', $today)->get();
            $stats = [
                'total_elders' => ElderSetting::where('elder_mode', true)->count(),
                'checked_today' => $todayLogs->where('status', 'checked')->count(),
                'pending_today' => $todayLogs->where('status', 'pending')->count(),
                'missed_today'  => $todayLogs->where('status', 'missed')->count(),
                'sos_today'     => $todayLogs->where('status', 'sos')->count(),
                'active_sos'    => ElderSosLog::where('status', 'triggered')->count(),
            ];

            return response()->json([
                'elders' => $elders,
                'stats'  => $stats,
            ]);
        } catch (\Exception $e) {
            return response()->json(['message' => '관리자 모니터링 조회 중 오류가 발생했습니다.', 'error' => $e->getMessage()], 500);
        }
    }

    // ─── 12. adminDetail ─────────────────────────────────────────
    public function adminDetail($id)
    {
        try {
            $settings = ElderSetting::where('user_id', $id)->firstOrFail();
            $user = User::findOrFail($id);

            $checkinLogs = ElderCheckinLog::where('user_id', $id)
                ->where('checkin_date', '>=', now()->subDays(30))
                ->orderBy('checkin_date', 'desc')
                ->get();

            $sosLogs = ElderSosLog::where('user_id', $id)
                ->orderBy('created_at', 'desc')
                ->limit(20)
                ->get();

            return response()->json([
                'user'         => $user->only(['id', 'name', 'nickname', 'email', 'phone']),
                'settings'     => $settings,
                'checkin_logs' => $checkinLogs,
                'sos_logs'     => $sosLogs,
                'guardian'     => $settings->guardian_user_id
                    ? User::find($settings->guardian_user_id)?->only(['id', 'name', 'nickname', 'email'])
                    : null,
            ]);
        } catch (\Exception $e) {
            return response()->json(['message' => '상세 정보 조회 중 오류가 발생했습니다.', 'error' => $e->getMessage()], 500);
        }
    }

    // ─── 13. adminResetCheckin ────────────────────────────────────
    public function adminResetCheckin($id)
    {
        try {
            $settings = ElderSetting::where('user_id', $id)->firstOrFail();

            $settings->update([
                'missed_count' => 0,
                'alert_sent'   => false,
            ]);

            // Mark today's log as pending
            ElderCheckinLog::updateOrCreate(
                ['user_id' => $id, 'checkin_date' => now()->toDateString()],
                ['status' => 'pending', 'checked_at' => null, 'guardian_notified' => false]
            );

            return response()->json(['message' => '체크인이 리셋되었습니다.']);
        } catch (\Exception $e) {
            return response()->json(['message' => '체크인 리셋 중 오류가 발생했습니다.', 'error' => $e->getMessage()], 500);
        }
    }

    // ─── 14. adminSendAlert ──────────────────────────────────────
    public function adminSendAlert($id)
    {
        try {
            $settings = ElderSetting::where('user_id', $id)->firstOrFail();
            $user = User::findOrFail($id);

            // Notify guardian
            if ($settings->guardian_user_id) {
                Notification::create([
                    'user_id' => $settings->guardian_user_id,
                    'type'    => 'elder_checkin_missed',
                    'title'   => '노인안심 수동 알림',
                    'body'    => '관리자가 ' . ($user->nickname ?? $user->name) . '님의 안부 확인을 요청합니다.',
                    'data'    => json_encode(['elder_user_id' => $id]),
                    'url'     => '/elder/guardian/' . $id,
                ]);
            }

            // Notify the elder user too
            Notification::create([
                'user_id' => $id,
                'type'    => 'elder_checkin_missed',
                'title'   => '안부 확인 요청',
                'body'    => '관리자가 안부 확인을 요청합니다. 체크인을 해주세요.',
                'data'    => json_encode([]),
                'url'     => '/elder',
            ]);

            $settings->update(['alert_sent' => true]);

            return response()->json(['message' => '알림이 발송되었습니다.']);
        } catch (\Exception $e) {
            return response()->json(['message' => '알림 발송 중 오류가 발생했습니다.', 'error' => $e->getMessage()], 500);
        }
    }

    // ─── 15. adminSettings ───────────────────────────────────────
    public function adminSettings()
    {
        try {
            // Global elder service settings stored in a config or settings table
            // For now, return defaults; can be expanded with a settings table
            $settings = DB::table('site_settings')
                ->where('group', 'elder')
                ->pluck('value', 'key')
                ->toArray();

            $defaults = [
                'default_checkin_time'  => '09:00',
                'alert_delay_minutes'   => '30',
                'second_alert_minutes'  => '60',
                'auto_call_enabled'     => '0',
                'service_enabled'       => '1',
            ];

            return response()->json(array_merge($defaults, $settings));
        } catch (\Exception $e) {
            // If site_settings table doesn't exist, return defaults
            return response()->json([
                'default_checkin_time'  => '09:00',
                'alert_delay_minutes'   => '30',
                'second_alert_minutes'  => '60',
                'auto_call_enabled'     => '0',
                'service_enabled'       => '1',
            ]);
        }
    }

    // ─── 16. adminSaveSettings ───────────────────────────────────
    public function adminSaveSettings(Request $request)
    {
        try {
            $keys = ['default_checkin_time', 'alert_delay_minutes', 'second_alert_minutes', 'auto_call_enabled', 'service_enabled'];

            foreach ($keys as $key) {
                if ($request->has($key)) {
                    DB::table('site_settings')->updateOrInsert(
                        ['group' => 'elder', 'key' => $key],
                        ['value' => $request->input($key), 'updated_at' => now()]
                    );
                }
            }

            return response()->json(['message' => '설정이 저장되었습니다.']);
        } catch (\Exception $e) {
            return response()->json(['message' => '설정 저장 중 오류가 발생했습니다.', 'error' => $e->getMessage()], 500);
        }
    }
}
