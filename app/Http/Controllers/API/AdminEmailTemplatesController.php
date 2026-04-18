<?php

namespace App\Http\Controllers\API;

use App\Http\Controllers\Controller;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Str;

/**
 * 이메일 템플릿 관리 + 변수 치환 (Phase 2-C Post).
 */
class AdminEmailTemplatesController extends Controller
{
    public function index()
    {
        return response()->json(['success' => true, 'data' => DB::table('email_templates')->orderBy('category')->orderBy('name')->get()]);
    }

    public function show($id)
    {
        $row = DB::table('email_templates')->where('id', $id)->first();
        if (!$row) return response()->json(['success' => false, 'message' => 'Not found'], 404);
        return response()->json(['success' => true, 'data' => $row]);
    }

    public function store(Request $request)
    {
        $data = $request->validate([
            'slug'      => 'required|string|max:100|unique:email_templates,slug',
            'name'      => 'required|string|max:255',
            'subject'   => 'required|string|max:255',
            'body_html' => 'required|string',
            'body_text' => 'nullable|string',
            'variables' => 'nullable|array',
            'category'  => 'nullable|string|max:100',
            'is_active' => 'boolean',
        ]);
        $data['created_by'] = auth()->id();
        $data['variables'] = isset($data['variables']) ? json_encode(array_values($data['variables'])) : null;
        $data['category'] = $data['category'] ?? 'general';
        $data['is_active'] = $data['is_active'] ?? true;
        $data['created_at'] = $data['updated_at'] = now();

        $id = DB::table('email_templates')->insertGetId($data);
        return response()->json(['success' => true, 'id' => $id]);
    }

    public function update(Request $request, $id)
    {
        $row = DB::table('email_templates')->where('id', $id)->first();
        if (!$row) return response()->json(['success' => false, 'message' => 'Not found'], 404);

        $data = $request->only(['name', 'subject', 'body_html', 'body_text', 'category', 'is_active']);
        if ($request->has('variables')) $data['variables'] = json_encode(array_values($request->input('variables', [])));
        $data['updated_at'] = now();

        DB::table('email_templates')->where('id', $id)->update($data);
        return response()->json(['success' => true]);
    }

    public function destroy($id)
    {
        DB::table('email_templates')->where('id', $id)->delete();
        return response()->json(['success' => true]);
    }

    /**
     * 템플릿 렌더: {{var}} 치환 후 반환 (미리보기·발송 준비).
     */
    public function render(Request $request, $id)
    {
        $tpl = DB::table('email_templates')->where('id', $id)->first();
        if (!$tpl) return response()->json(['success' => false], 404);

        $vars = $request->input('variables', []);
        if (!is_array($vars)) $vars = [];

        $subject = $this->substitute($tpl->subject, $vars);
        $html    = $this->substitute($tpl->body_html, $vars);
        $text    = $tpl->body_text ? $this->substitute($tpl->body_text, $vars) : null;

        return response()->json(['success' => true, 'data' => [
            'subject'   => $subject,
            'body_html' => $html,
            'body_text' => $text,
        ]]);
    }

    /** 간단한 {{key}} 치환. XSS 주의: body_html 은 관리자 입력이므로 신뢰. */
    protected function substitute(string $template, array $vars): string
    {
        return preg_replace_callback('/\{\{\s*([a-zA-Z0-9_]+)\s*\}\}/', function ($m) use ($vars) {
            return $vars[$m[1]] ?? '';
        }, $template);
    }
}
