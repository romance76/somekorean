import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import ko from '../i18n/ko'
import en from '../i18n/en'

const MESSAGES = { ko, en }

export const useLangStore = defineStore('lang', () => {
  const locale = ref(localStorage.getItem('sk_lang') || 'ko')

  // Full translation object for current locale
  const t = computed(() => MESSAGES[locale.value] || MESSAGES.ko)

  // Set locale and persist
  function setLang(lang) {
    if (!MESSAGES[lang]) return
    locale.value = lang
    localStorage.setItem('sk_lang', lang)
    document.documentElement.lang = lang
  }

  // Toggle between ko and en
  function toggle() {
    setLang(locale.value === 'ko' ? 'en' : 'ko')
  }

  // Dot-notation key lookup: $t('nav.home') -> '홈'
  function $t(key) {
    const keys = key.split('.')
    let val = t.value
    for (const k of keys) {
      val = val?.[k]
    }
    return val ?? key
  }

  return { locale, t, setLang, toggle, $t }
})
