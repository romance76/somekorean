<?php

namespace App\Traits;

/**
 * 소유권 체크 시 관리자에게는 bypass 허용.
 *
 * 예시:
 *   // 기존: 내 글만 삭제 가능
 *   JobPost::where('user_id', auth()->id())->findOrFail($id);
 *
 *   // 변경: 내 글 OR 관리자면 어떤 글이든 삭제 가능
 *   $this->findOwnedOrAdmin(JobPost::class, $id);
 */
trait AdminAuthorizes
{
    /**
     * 모델을 찾되, 관리자면 소유권 체크를 건너뛴다.
     *
     * @param  class-string  $modelClass  Eloquent 모델 클래스
     * @param  int|string    $id          primary key
     * @param  string        $ownerCol    소유자 컬럼 (기본: user_id)
     * @return \Illuminate\Database\Eloquent\Model
     */
    protected function findOwnedOrAdmin(string $modelClass, $id, string $ownerCol = 'user_id')
    {
        $user = auth()->user();
        $query = $modelClass::query();
        if (!$user || !$user->is_admin) {
            $query->where($ownerCol, $user?->id);
        }
        return $query->findOrFail($id);
    }

    /**
     * 현재 유저가 관리자인지.
     */
    protected function isAdmin(): bool
    {
        $u = auth()->user();
        return (bool) ($u && $u->is_admin);
    }
}
