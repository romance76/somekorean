/**
 * RingtoneService — 모바일 호환 벨소리 서비스
 *
 * 전략:
 * 1. DOM <audio id="sk-ringtone"> 엘리먼트 사용 (CommHub.vue에 선언)
 * 2. 사용자 첫 터치 시 preloadRingtone()으로 WAV 로드 + play/pause unlock
 * 3. 수신 통화 시 startRingtone() → 이미 unlock된 엘리먼트의 play()
 * 4. navigator.vibrate() 진동 병행 (Android)
 *
 * iOS Safari: push notification 없이는 백그라운드 오디오 불가 — 진동도 미지원
 * Android Chrome: 한 번 play/pause하면 이후 비제스처 play() 가능
 */

let audioCtx = null
let ringtoneNodes = []
let isPlaying = false
let audioUnlocked = false
let ringtoneLoaded = false
let vibrationLoop = null
let ringtoneUrl = null

// ── WAV 생성 (440Hz + 480Hz 한국 전화 벨소리) ────────────────────
function generateRingtoneWav() {
  const sampleRate = 22050
  const ringDur = 0.8
  const gapDur = 0.5
  const cycles = 8  // ~10초
  const totalSamples = Math.floor(sampleRate * (ringDur + gapDur) * cycles)
  const samples = new Float32Array(totalSamples)

  for (let c = 0; c < cycles; c++) {
    const offset = Math.floor(c * (ringDur + gapDur) * sampleRate)
    const ringLen = Math.floor(ringDur * sampleRate)
    for (let i = 0; i < ringLen; i++) {
      const t = i / sampleRate
      const env = Math.min(1, i / (sampleRate * 0.02)) * Math.min(1, (ringLen - i) / (sampleRate * 0.02))
      samples[offset + i] = 0.35 * env * (Math.sin(2 * Math.PI * 440 * t) + Math.sin(2 * Math.PI * 480 * t))
    }
  }

  // WAV 헤더
  const numCh = 1, bps = 16
  const dataLen = totalSamples * numCh * (bps / 8)
  const buf = new ArrayBuffer(44 + dataLen)
  const v = new DataView(buf)
  const w = (o, s) => { for (let i = 0; i < s.length; i++) v.setUint8(o + i, s.charCodeAt(i)) }
  w(0, 'RIFF'); v.setUint32(4, 36 + dataLen, true); w(8, 'WAVE')
  w(12, 'fmt '); v.setUint32(16, 16, true); v.setUint16(20, 1, true)
  v.setUint16(22, numCh, true); v.setUint32(24, sampleRate, true)
  v.setUint32(28, sampleRate * numCh * (bps / 8), true)
  v.setUint16(32, numCh * (bps / 8), true); v.setUint16(34, bps, true)
  w(36, 'data'); v.setUint32(40, dataLen, true)
  for (let i = 0; i < totalSamples; i++) {
    v.setInt16(44 + i * 2, Math.max(-1, Math.min(1, samples[i])) * 0x7FFF, true)
  }
  return URL.createObjectURL(new Blob([buf], { type: 'audio/wav' }))
}

function getRingtoneUrl() {
  if (!ringtoneUrl) ringtoneUrl = generateRingtoneWav()
  return ringtoneUrl
}

// ── AudioContext unlock (Web Audio API 용) ────────────────────────
export function unlockAudio() {
  if (audioUnlocked) return
  try {
    audioCtx = new (window.AudioContext || window.webkitAudioContext)()
    const buf = audioCtx.createBuffer(1, 1, 22050)
    const src = audioCtx.createBufferSource()
    src.buffer = buf
    src.connect(audioCtx.destination)
    src.start(0)
    audioUnlocked = true
    console.log('[Ringtone] AudioContext unlocked')
  } catch (e) {
    console.warn('[Ringtone] AudioContext unlock failed:', e)
  }
}

// ── DOM <audio> 벨소리 pre-load (소스만 로드, 재생하지 않음) ──────
export function preloadRingtone() {
  const el = document.getElementById('sk-ringtone')
  if (!el || ringtoneLoaded) return

  // WAV 소스만 로드 — 재생은 하지 않음 (페이지 진입 시 벨소리 방지)
  // 실제 재생은 startRingtone()에서 수신 통화 시에만
  el.src = getRingtoneUrl()
  el.load()
  ringtoneLoaded = true
  console.log('[Ringtone] <audio> source pre-loaded (no play)')
}

// ── Web Audio 벨소리 (AudioContext 이미 unlock된 경우) ────────────
function playWebAudio() {
  if (!audioCtx || audioCtx.state === 'closed') return false
  if (audioCtx.state === 'suspended') {
    audioCtx.resume().catch(() => {})
    if (audioCtx.state === 'suspended') return false
  }
  const ctx = audioCtx
  let t = ctx.currentTime
  for (let r = 0; r < 10; r++) {
    for (const { freq, dur } of [{ freq: 440, dur: 0.4 }, { freq: 480, dur: 0.4 }]) {
      const o = ctx.createOscillator(), g = ctx.createGain()
      o.connect(g); g.connect(ctx.destination)
      o.type = 'sine'; o.frequency.setValueAtTime(freq, t)
      g.gain.setValueAtTime(0, t)
      g.gain.linearRampToValueAtTime(0.4, t + 0.02)
      g.gain.linearRampToValueAtTime(0.4, t + dur - 0.02)
      g.gain.linearRampToValueAtTime(0, t + dur)
      o.start(t); o.stop(t + dur)
      ringtoneNodes.push(o, g)
      t += dur
    }
    t += 1.0
  }
  return true
}

// ── 공개 API ────────────────────────────────────────────────────

export function startRingtone() {
  if (isPlaying) return
  isPlaying = true
  console.log('[Ringtone] Starting, loaded:', ringtoneLoaded, 'audioUnlocked:', audioUnlocked)

  let soundOk = false

  // 1차: DOM <audio> 엘리먼트 (pre-load된 경우 가장 안정적)
  const el = document.getElementById('sk-ringtone')
  if (el) {
    if (!el.src || !el.src.startsWith('blob:')) {
      el.src = getRingtoneUrl()
      el.load()
    }
    el.currentTime = 0
    el.volume = 1.0
    el.loop = true
    const p = el.play()
    if (p) {
      p.then(() => {
        soundOk = true
        console.log('[Ringtone] <audio> playing OK')
      }).catch(e => {
        console.warn('[Ringtone] <audio> play blocked:', e.name)
      })
    }
  }

  // 2차: Web Audio API (AudioContext unlock된 경우)
  if (audioUnlocked) {
    try {
      if (playWebAudio()) soundOk = true
    } catch (e) {}
  }

  // 3차: 진동 (Android — 항상 시도)
  try { navigator.vibrate?.([700, 300, 700, 300, 700, 300, 700, 300, 700]) } catch {}
  vibrationLoop = setInterval(() => {
    if (!isPlaying) return
    try { navigator.vibrate?.([700, 300, 700, 300, 700, 300, 700, 300, 700]) } catch {}
  }, 5000)
}

export function stopRingtone() {
  isPlaying = false

  // 진동 중지
  try { navigator.vibrate?.(0) } catch {}
  if (vibrationLoop) { clearInterval(vibrationLoop); vibrationLoop = null }

  // DOM <audio> 정지
  const el = document.getElementById('sk-ringtone')
  if (el) {
    try { el.pause(); el.currentTime = 0 } catch {}
  }

  // Web Audio 노드 정리
  ringtoneNodes.forEach(n => {
    try { n.disconnect() } catch {}
    try { n.stop?.() } catch {}
  })
  ringtoneNodes = []
}
