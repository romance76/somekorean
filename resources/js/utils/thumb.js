// 리스트 페이지 이미지를 /api/thumb 프록시로 변환해 빠르게 로딩.
// 서버가 첫 요청 시 다운로드/리사이즈 → 로컬 캐시 → 이후 정적 파일로 서빙.
// 브라우저는 1년 immutable 캐시.
//
// 사용법:
//   <img :src="thumb(recipe.thumbnail, 240)" loading="lazy" />

export function thumb(url, width = 240) {
  if (!url || typeof url !== 'string') return ''
  // data URL 이나 blob 은 그대로
  if (url.startsWith('data:') || url.startsWith('blob:')) return url
  // 이미 /api/thumb 경로면 그대로
  if (url.includes('/api/thumb')) return url
  return `/api/thumb?url=${encodeURIComponent(url)}&w=${width}`
}

// Retina 용 2배 이미지 (선택)
export function thumb2x(url, width = 240) {
  return thumb(url, width * 2)
}
