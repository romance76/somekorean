import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import ko from '../i18n/ko'
import en from '../i18n/en'

const MESSAGES = { ko, en }

export const useLangStore = defineStore('lang', () => {
  const locale = ref(localStorage.getItem('lang') || 'ko')

  const t = computed(() => MESSAGES[locale.value] ?? MESSAGES.ko)

  function setLocale(lang) {
    if (!MESSAGES[lang]) return
    locale.value = lang
    localStorage.setItem('lang', lang)
    document.documentElement.lang = lang
  }

  function $t(key) {
    const keys = key.split('.')
    let val = t.value
    for (const k of keys) { val = val?.[k] }
    return val ?? key
  }

  return { locale, t, setLocale, $t }
})
