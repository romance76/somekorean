import { ref, computed } from 'vue'
import ko from './ko'
import en from './en'

const messages = { ko, en }
const currentLocale = ref(localStorage.getItem('locale') || 'ko')

export function useI18n() {
  const locale = currentLocale
  const t = (key) => {
    const keys = key.split('.')
    let result = messages[locale.value]
    for (const k of keys) {
      result = result?.[k]
    }
    return result || key
  }
  const setLocale = (l) => {
    currentLocale.value = l
    localStorage.setItem('locale', l)
  }
  return { locale, t, setLocale }
}
