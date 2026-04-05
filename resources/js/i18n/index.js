import { ref, computed } from 'vue'
import ko from './ko'
import en from './en'

const messages = { ko, en }
const currentLocale = ref(localStorage.getItem('sk_lang') || 'ko')

export function useI18n() {
  const locale = currentLocale

  // Get translation by dot-notation key
  function t(key) {
    const keys = key.split('.')
    let result = messages[locale.value] || messages.ko
    for (const k of keys) {
      result = result?.[k]
    }
    return result || key
  }

  // Set locale and persist
  function setLocale(lang) {
    if (!messages[lang]) return
    currentLocale.value = lang
    localStorage.setItem('sk_lang', lang)
    document.documentElement.lang = lang
  }

  return { locale, t, setLocale }
}
