import { ref, computed } from 'vue'

const STORAGE_KEY = 'sk_location'
const userLocation = ref(null) // { name, state, lat, lng }
const radius = ref('30')       // miles
const initialized = ref(false)

export function useLocation() {
  // Initialize location from cache or API
  async function init() {
    if (initialized.value) return
    initialized.value = true

    // Try cached location first
    const cached = localStorage.getItem(STORAGE_KEY)
    if (cached) {
      try { userLocation.value = JSON.parse(cached); return } catch { /* ignore */ }
    }

    // Try API
    try {
      const token = localStorage.getItem('sk_token')
      if (!token) return

      const res = await fetch('/api/auth/me', {
        headers: { Authorization: `Bearer ${token}` }
      })
      const data = await res.json()
      const u = data.user || data
      if (u.city && u.state) {
        const loc = {
          name: u.city,
          state: u.state,
          lat: u.lat ? parseFloat(u.lat) : null,
          lng: u.lng ? parseFloat(u.lng) : null,
        }
        userLocation.value = loc
        localStorage.setItem(STORAGE_KEY, JSON.stringify(loc))
      }
    } catch { /* ignore */ }
  }

  // Get current position via browser geolocation
  function getCurrentPosition() {
    return new Promise((resolve, reject) => {
      if (!navigator.geolocation) {
        reject(new Error('Geolocation not supported'))
        return
      }
      navigator.geolocation.getCurrentPosition(
        (pos) => resolve({ lat: pos.coords.latitude, lng: pos.coords.longitude }),
        (err) => reject(err),
        { enableHighAccuracy: false, timeout: 10000 }
      )
    })
  }

  // Haversine distance between two points (returns miles)
  function getDistance(lat1, lng1, lat2, lng2) {
    const R = 3958.8 // Earth radius in miles
    const dLat = toRad(lat2 - lat1)
    const dLng = toRad(lng2 - lng1)
    const a = Math.sin(dLat / 2) ** 2 +
              Math.cos(toRad(lat1)) * Math.cos(toRad(lat2)) * Math.sin(dLng / 2) ** 2
    return R * 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a))
  }

  function toRad(deg) { return deg * (Math.PI / 180) }

  // Format distance for display
  function formatDistance(miles) {
    if (miles === null || miles === undefined) return ''
    if (miles < 0.1) return '0.1 mi'
    if (miles < 10) return `${miles.toFixed(1)} mi`
    return `${Math.round(miles)} mi`
  }

  // Set location manually
  function setLocation(loc) {
    userLocation.value = loc
    localStorage.setItem(STORAGE_KEY, JSON.stringify(loc))
  }

  function setRadius(r) { radius.value = r }

  // Build query params for API calls
  const locationQuery = computed(() => {
    if (radius.value === '\uC804\uAD6D' || radius.value === 'all') return {}
    if (!userLocation.value?.lat) return {}
    return {
      lat: userLocation.value.lat,
      lng: userLocation.value.lng,
      radius: parseInt(radius.value),
    }
  })

  // Display text for current location
  const displayText = computed(() => {
    if (radius.value === '\uC804\uAD6D' || radius.value === 'all') return '\uC804\uAD6D'
    if (!userLocation.value) return '\uC704\uCE58 \uC120\uD0DD'
    return `${userLocation.value.name}, ${userLocation.value.state}`
  })

  return {
    userLocation,
    radius,
    locationQuery,
    displayText,
    init,
    getCurrentPosition,
    getDistance,
    formatDistance,
    setLocation,
    setRadius,
  }
}
