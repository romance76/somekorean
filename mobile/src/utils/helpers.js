import { format, isToday, isYesterday } from 'date-fns'
import { ko } from 'date-fns/locale'

export function formatDate(dt) {
  if (!dt) return ''
  const d = new Date(dt)
  if (isToday(d)) return '오늘'
  if (isYesterday(d)) return '어제'
  return format(d, 'yyyy년 M월 d일 (eee)', { locale: ko })
}

export function formatTime(dt) {
  if (!dt) return ''
  return format(new Date(dt), 'a h:mm', { locale: ko })
}

export function formatRelative(dt) {
  if (!dt) return ''
  const diff = (Date.now() - new Date(dt).getTime()) / 1000
  if (diff < 60) return '방금 전'
  if (diff < 3600) return `${Math.floor(diff / 60)}분 전`
  if (diff < 86400) return `${Math.floor(diff / 3600)}시간 전`
  if (diff < 604800) return `${Math.floor(diff / 86400)}일 전`
  return format(new Date(dt), 'M월 d일', { locale: ko })
}

export function formatNumber(n) {
  if (!n) return '0'
  if (n >= 1000) return `${(n / 1000).toFixed(1)}k`
  return String(n)
}

export const COLORS = {
  primary: '#2563EB',
  primaryLight: '#3B82F6',
  primaryDark: '#1D4ED8',
  secondary: '#7C3AED',
  success: '#10B981',
  warning: '#F59E0B',
  danger: '#EF4444',
  gray: {
    50: '#F9FAFB', 100: '#F3F4F6', 200: '#E5E7EB',
    300: '#D1D5DB', 400: '#9CA3AF', 500: '#6B7280',
    600: '#4B5563', 700: '#374151', 800: '#1F2937', 900: '#111827',
  },
}
