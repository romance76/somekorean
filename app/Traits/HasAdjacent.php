<?php

namespace App\Traits;

use Illuminate\Support\Facades\Schema;

/**
 * Detail 응답에 prev/next id·title 주입 공통 트레이트.
 * 모든 상세 페이지 하단 "이전글 / 목록 / 다음글" 공통 노출.
 *
 * 리스트 정렬과 동일하게 동작하도록 orderCol/orderDir 지원
 * (예: list 가 created_at desc 면 prev = 더 최근 글, next = 더 오래된 글)
 */
trait HasAdjacent
{
    /**
     * @param  string $modelClass  Eloquent 모델
     * @param  int    $currentId
     * @param  string $titleCol    표시할 타이틀 컬럼
     * @param  array  $scope       [컬럼 => 값] 같은 카테고리 한정 (선택)
     * @param  string $orderCol    리스트 정렬 컬럼 (기본 'created_at')
     * @param  string $orderDir    'desc' (기본) | 'asc'  — 리스트 정렬 방향
     * @return array               ['prev' => [...], 'next' => [...]]
     */
    protected function adjacentPair(
        string $modelClass,
        int $currentId,
        string $titleCol = 'title',
        array $scope = [],
        string $orderCol = 'created_at',
        string $orderDir = 'desc'
    ): array {
        $base = $modelClass::query();
        foreach ($scope as $col => $val) {
            if ($val !== null && $val !== '') $base->where($col, $val);
        }

        // 활성 상태 자동 반영 (is_active 컬럼 있을 때)
        $model = new $modelClass;
        $table = $model->getTable();
        if (Schema::hasColumn($table, 'is_active')) {
            $base->where('is_active', true);
        }

        // 정렬 컬럼이 실제 존재하는지 안전 체크
        if (!Schema::hasColumn($table, $orderCol)) {
            $orderCol = 'id';
        }

        // 현재 글의 정렬 컬럼 값 가져오기
        $current = $modelClass::find($currentId);
        if (!$current) {
            return ['prev' => null, 'next' => null];
        }
        $curVal = $current->$orderCol;

        // 정렬 방향에 따라 prev/next 의미가 다름
        // - desc 정렬: prev = 더 큰 값 (위쪽 = 더 최근)
        //              next = 더 작은 값 (아래쪽 = 더 오래된)
        // - asc 정렬:  prev = 더 작은 값
        //              next = 더 큰 값
        if ($orderDir === 'desc') {
            $prev = (clone $base)
                ->where(function ($q) use ($orderCol, $curVal, $currentId) {
                    $q->where($orderCol, '>', $curVal)
                      ->orWhere(function ($qq) use ($orderCol, $curVal, $currentId) {
                          $qq->where($orderCol, $curVal)->where('id', '>', $currentId);
                      });
                })
                ->orderBy($orderCol, 'asc')->orderBy('id', 'asc')
                ->first(['id', $titleCol]);

            $next = (clone $base)
                ->where(function ($q) use ($orderCol, $curVal, $currentId) {
                    $q->where($orderCol, '<', $curVal)
                      ->orWhere(function ($qq) use ($orderCol, $curVal, $currentId) {
                          $qq->where($orderCol, $curVal)->where('id', '<', $currentId);
                      });
                })
                ->orderBy($orderCol, 'desc')->orderBy('id', 'desc')
                ->first(['id', $titleCol]);
        } else {
            $prev = (clone $base)
                ->where(function ($q) use ($orderCol, $curVal, $currentId) {
                    $q->where($orderCol, '<', $curVal)
                      ->orWhere(function ($qq) use ($orderCol, $curVal, $currentId) {
                          $qq->where($orderCol, $curVal)->where('id', '<', $currentId);
                      });
                })
                ->orderBy($orderCol, 'desc')->orderBy('id', 'desc')
                ->first(['id', $titleCol]);

            $next = (clone $base)
                ->where(function ($q) use ($orderCol, $curVal, $currentId) {
                    $q->where($orderCol, '>', $curVal)
                      ->orWhere(function ($qq) use ($orderCol, $curVal, $currentId) {
                          $qq->where($orderCol, $curVal)->where('id', '>', $currentId);
                      });
                })
                ->orderBy($orderCol, 'asc')->orderBy('id', 'asc')
                ->first(['id', $titleCol]);
        }

        return [
            'prev' => $prev ? ['id' => $prev->id, 'title' => $prev->$titleCol ?? ''] : null,
            'next' => $next ? ['id' => $next->id, 'title' => $next->$titleCol ?? ''] : null,
        ];
    }
}
