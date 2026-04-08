import { ref, computed, onUnmounted } from 'vue'
import axios from 'axios'
import { startRingtone, stopRingtone } from '@/services/RingtoneService'

const ICE_SERVERS = {
  iceServers: [
    { urls: 'stun:stun.l.google.com:19302' },
    { urls: 'stun:stun1.l.google.com:19302' },
    { urls: 'stun:stun2.l.google.com:19302' },
    { urls: 'stun:stun3.l.google.com:19302' },
    {
      urls: 'turn:openrelay.metered.ca:80',
      username: 'openrelayproject',
      credential: 'openrelayproject',
    },
    {
      urls: 'turn:openrelay.metered.ca:443',
      username: 'openrelayproject',
      credential: 'openrelayproject',
    },
    {
      urls: 'turn:openrelay.metered.ca:443?transport=tcp',
      username: 'openrelayproject',
      credential: 'openrelayproject',
    },
  ],
  iceCandidatePoolSize: 10,
}

export function useCommsWebRTC() {
  const callStatus    = ref('idle')
  const callDuration  = ref(0)
  const isMuted       = ref(false)
  const isSpeaker     = ref(true)
  const currentCallId = ref(null)
  const currentRoomId = ref(null)
  const remoteUser    = ref(null)
  const incomingCall  = ref(null)

  let pc = null
  let localStream = null
  let durationTimer = null
  let missedTimer = null
  let disconnectTimer = null
  let pendingOffer = null
  let pendingIceCandidates = []
  let remoteAudioCtx = null      // 원격 오디오 재생용 AudioContext
  let remoteAudioSource = null   // MediaStreamSource 참조

  // ── SDP 정리 ──────────────────────────────────────────────────
  function sanitizeSdp(sdpObj) {
    if (!sdpObj || !sdpObj.sdp) return sdpObj
    return {
      type: sdpObj.type,
      sdp: sdpObj.sdp
        .replace(/ +(\r?\n)/g, '$1')
        .replace(/\r?\n/g, '\r\n')
    }
  }

  // ── 오디오 준비 (user gesture 중 호출!) ─────────────────────────
  // 버튼 클릭 직후 동기적으로 호출 → AudioContext 생성 + resume
  function prepareAudio() {
    try {
      if (!remoteAudioCtx || remoteAudioCtx.state === 'closed') {
        remoteAudioCtx = new (window.AudioContext || window.webkitAudioContext)()
      }
      if (remoteAudioCtx.state === 'suspended') {
        remoteAudioCtx.resume()
      }
      console.log('[WebRTC] AudioContext prepared:', remoteAudioCtx.state)
    } catch (e) {
      console.warn('[WebRTC] AudioContext creation failed:', e)
    }
  }

  // ── PeerConnection ──────────────────────────────────────────────
  function createPeerConnection(roomId, targetUserId) {
    if (pc) { try { pc.close() } catch {} }
    pc = new RTCPeerConnection(ICE_SERVERS)

    pc.onicecandidate = ({ candidate }) => {
      if (candidate) {
        axios.post('/api/comms/calls/signal', {
          target_user_id: targetUserId,
          room_id: roomId,
          type: 'ice-candidate',
          payload: { candidate: candidate.toJSON() },
        }).catch(e => console.warn('[WebRTC] ICE signal failed:', e))
      }
    }

    pc.ontrack = (event) => {
      const stream = event.streams[0]
      const tracks = stream.getAudioTracks()
      console.log('[WebRTC] 🔊 Remote track received, audio tracks:', tracks.length,
        tracks.map(t => `${t.label} enabled=${t.enabled}`).join(', '))

      // ★ AudioContext로 직접 스피커 출력 (가장 확실한 방법)
      // prepareAudio()에서 user gesture 중 생성+resume 되었으므로 running 상태
      if (remoteAudioCtx) {
        try {
          if (remoteAudioCtx.state === 'suspended') remoteAudioCtx.resume()
          if (remoteAudioSource) { try { remoteAudioSource.disconnect() } catch {} }
          remoteAudioSource = remoteAudioCtx.createMediaStreamSource(stream)
          remoteAudioSource.connect(remoteAudioCtx.destination)
          console.log('[WebRTC] ✅ Remote audio → AudioContext →', remoteAudioCtx.state)
        } catch (e) {
          console.error('[WebRTC] AudioContext route failed:', e)
        }
      }

      // <audio> 엘리먼트도 백업으로 설정 (데스크톱에서 더 안정적)
      const audio = document.getElementById('sk-remote-audio')
      if (audio) {
        audio.srcObject = stream
        audio.play().catch(() => {})
      }
    }

    pc.onconnectionstatechange = () => {
      const state = pc?.connectionState
      console.log('[WebRTC] Connection state:', state)

      if (state === 'connected') {
        console.log('[WebRTC] ✅ P2P Connected!')
        if (disconnectTimer) { clearTimeout(disconnectTimer); disconnectTimer = null }
        if (callStatus.value !== 'connected') {
          callStatus.value = 'connected'
          startDurationTimer()
        }
      }
      if (state === 'failed') {
        console.error('[WebRTC] ❌ Connection failed')
        setTimeout(() => { if (pc?.connectionState === 'failed') handleCallEnded() }, 5000)
      }
      if (state === 'disconnected') {
        if (disconnectTimer) clearTimeout(disconnectTimer)
        disconnectTimer = setTimeout(() => {
          if (pc?.connectionState === 'disconnected' || pc?.connectionState === 'closed') handleCallEnded()
        }, 2000)
      }
      if (state === 'closed') handleCallEnded()
    }

    return pc
  }

  async function getLocalStream() {
    if (localStream) return localStream
    try {
      localStream = await navigator.mediaDevices.getUserMedia({ audio: true, video: false })
      console.log('[WebRTC] ✅ Microphone acquired:', localStream.getAudioTracks()[0]?.label)
      return localStream
    } catch (err) {
      console.error('[WebRTC] ❌ 마이크 실패:', err.name, err.message)
      return null
    }
  }

  function startDurationTimer() {
    stopDurationTimer()
    callDuration.value = 0
    durationTimer = setInterval(() => callDuration.value++, 1000)
  }
  function stopDurationTimer() {
    if (durationTimer) { clearInterval(durationTimer); durationTimer = null }
  }

  function handleCallEnded() {
    stopDurationTimer()
    stopRingtone()
    if (missedTimer) { clearTimeout(missedTimer); missedTimer = null }
    if (disconnectTimer) { clearTimeout(disconnectTimer); disconnectTimer = null }
    if (remoteAudioSource) { try { remoteAudioSource.disconnect() } catch {} ; remoteAudioSource = null }
    if (remoteAudioCtx) { try { remoteAudioCtx.close() } catch {} ; remoteAudioCtx = null }
    localStream?.getTracks().forEach(t => t.stop())
    if (pc) { try { pc.close() } catch {} }
    pc = null
    localStream = null
    pendingOffer = null
    pendingIceCandidates = []
    callStatus.value = 'ended'
    setTimeout(() => {
      callStatus.value = 'idle'
      currentCallId.value = null
      currentRoomId.value = null
      remoteUser.value = null
      incomingCall.value = null
    }, 3000)
  }

  // ── WebSocket 시그널 수신 ─────────────────────────────────────
  function listenForSignals(myUserId) {
    if (!window.Echo) { console.warn('[WebRTC] window.Echo not available'); return }

    window.Echo.private(`user.${myUserId}`)
      .listen('.webrtc.signal', async (event) => {
        const { type, payload, room_id } = event
        console.log('[WebRTC] Signal:', type, 'room:', room_id)

        if (type === 'offer') {
          if (callStatus.value === 'ringing' || currentRoomId.value === room_id) {
            pendingOffer = { sdp: payload.sdp, room_id }
          }
          return
        }

        if (type === 'answer') {
          if (pc && currentRoomId.value === room_id) {
            await pc.setRemoteDescription(sanitizeSdp(payload.sdp))
            if (pendingIceCandidates.length > 0) {
              for (const c of pendingIceCandidates) await pc.addIceCandidate(c).catch(() => {})
              pendingIceCandidates = []
            }
            callStatus.value = 'connected'
            startDurationTimer()
          }
          return
        }

        if (type === 'ice-candidate') {
          if (pc && pc.remoteDescription) {
            await pc.addIceCandidate(payload.candidate).catch(() => {})
          } else {
            pendingIceCandidates.push(payload.candidate)
          }
          return
        }

        if (type === 'call-answered') {
          if (callStatus.value === 'calling') { callStatus.value = 'connected'; startDurationTimer() }
          return
        }

        if (type === 'call-answered-elsewhere') {
          if (!currentCallId.value && callStatus.value === 'ringing') {
            stopRingtone()
            if (missedTimer) { clearTimeout(missedTimer); missedTimer = null }
            incomingCall.value = null; currentRoomId.value = null
            pendingOffer = null; pendingIceCandidates = []
            callStatus.value = 'idle'
          }
          return
        }

        if (type === 'call-ended') {
          if (room_id === currentRoomId.value) endCall(false)
        }
      })
      .listen('.call.initiated', (event) => {
        console.log('[WebRTC] Incoming call:', event)
        incomingCall.value = event
        currentRoomId.value = event.room_id
        callStatus.value = 'ringing'
        startRingtone()
        missedTimer = setTimeout(() => {
          if (callStatus.value === 'ringing') {
            stopRingtone()
            if (incomingCall.value?.call_id) axios.post(`/api/comms/calls/${incomingCall.value.call_id}/end`).catch(() => {})
            incomingCall.value = null; currentRoomId.value = null; callStatus.value = 'idle'
          }
        }, 30000)
      })
  }

  // ── 발신 ───────────────────────────────────────────────────────
  async function startCall(targetUser) {
    if (callStatus.value !== 'idle') return
    remoteUser.value = targetUser
    callStatus.value = 'calling'

    // ★ 1단계: user gesture 중 AudioContext 생성 (동기)
    prepareAudio()

    // ★ 2단계: user gesture 중 마이크 획득 (첫 번째 await)
    // getUserMedia 성공 → 브라우저가 오디오 권한 전체 부여
    const stream = await getLocalStream()

    try {
      const { data } = await axios.post('/api/comms/calls/initiate', { callee_id: targetUser.id })
      currentCallId.value = data.call_id
      currentRoomId.value = data.room_id

      createPeerConnection(data.room_id, targetUser.id)
      if (stream) {
        stream.getTracks().forEach(t => pc.addTrack(t, stream))
      }

      const offer = await pc.createOffer({ offerToReceiveAudio: true })
      await pc.setLocalDescription(offer)

      await axios.post('/api/comms/calls/signal', {
        target_user_id: targetUser.id,
        room_id: data.room_id,
        type: 'offer',
        payload: { sdp: { type: offer.type, sdp: offer.sdp } },
      })
      console.log('[WebRTC] ✅ Offer sent to', targetUser.name)
      startCallMonitor()
    } catch (err) {
      console.error('[WebRTC] startCall failed:', err)
      handleCallEnded()
    }
  }

  // ── 수신 수락 ──────────────────────────────────────────────────
  async function answerCall() {
    if (!incomingCall.value) return

    // ★ 1단계: user gesture 중 AudioContext 생성 (동기)
    prepareAudio()

    // ★ 2단계: user gesture 중 마이크 획득 (첫 번째 await)
    const stream = await getLocalStream()

    stopRingtone()
    if (missedTimer) { clearTimeout(missedTimer); missedTimer = null }

    const { call_id, room_id, caller_id, caller_name, caller_avatar } = incomingCall.value
    currentCallId.value = call_id
    currentRoomId.value = room_id
    remoteUser.value = { id: caller_id, name: caller_name, avatar: caller_avatar }
    callStatus.value = 'connected'
    incomingCall.value = null
    startDurationTimer()
    startCallMonitor()

    try {
      await axios.post(`/api/comms/calls/${call_id}/answer`).catch(() => {})

      createPeerConnection(room_id, caller_id)
      if (stream) {
        stream.getTracks().forEach(t => pc.addTrack(t, stream))
      }

      if (pendingOffer && pendingOffer.room_id === room_id) {
        await pc.setRemoteDescription(sanitizeSdp(pendingOffer.sdp))

        if (pendingIceCandidates.length > 0) {
          for (const c of pendingIceCandidates) await pc.addIceCandidate(c).catch(() => {})
          pendingIceCandidates = []
        }

        const answer = await pc.createAnswer()
        await pc.setLocalDescription(answer)

        await axios.post('/api/comms/calls/signal', {
          target_user_id: caller_id,
          room_id,
          type: 'answer',
          payload: { sdp: { type: answer.type, sdp: answer.sdp } },
        })
        pendingOffer = null
        console.log('[WebRTC] ✅ Answer sent to caller')
      }
    } catch (err) {
      console.error('[WebRTC] answerCall error:', err.message || err)
    }
  }

  // ── 수신 거부 ──────────────────────────────────────────────────
  async function declineCall() {
    if (!incomingCall.value) return
    stopRingtone()
    if (missedTimer) { clearTimeout(missedTimer); missedTimer = null }
    await axios.post(`/api/comms/calls/${incomingCall.value.call_id}/end`).catch(() => {})
    incomingCall.value = null; currentRoomId.value = null
    pendingOffer = null; pendingIceCandidates = []
    callStatus.value = 'idle'
  }

  // ── 통화 종료 ──────────────────────────────────────────────────
  async function endCall(notifyServer = true) {
    if (notifyServer && currentCallId.value) {
      if (remoteUser.value?.id && currentRoomId.value) {
        axios.post('/api/comms/calls/signal', {
          target_user_id: remoteUser.value.id,
          room_id: currentRoomId.value,
          type: 'call-ended',
          payload: {},
        }).catch(() => {})
      }
      await axios.post(`/api/comms/calls/${currentCallId.value}/end`).catch(() => {})
    }
    handleCallEnded()
  }

  function startCallMonitor() {
    const monitor = setInterval(async () => {
      if (!currentCallId.value || callStatus.value === 'idle' || callStatus.value === 'ended') {
        clearInterval(monitor); return
      }
      try {
        const { data } = await axios.get(`/api/comms/calls/${currentCallId.value}/status`)
        if (data.status === 'ended') { clearInterval(monitor); handleCallEnded() }
      } catch {}
    }, 3000)
  }

  function toggleMute() {
    localStream?.getAudioTracks().forEach(t => (t.enabled = !t.enabled))
    isMuted.value = !isMuted.value
  }

  async function toggleSpeaker() {
    isSpeaker.value = !isSpeaker.value
    const audio = document.getElementById('sk-remote-audio')
    if (audio && typeof audio.setSinkId === 'function') {
      try {
        const devices = await navigator.mediaDevices.enumerateDevices()
        const speakers = devices.filter(d => d.kind === 'audiooutput')
        if (speakers.length > 1) {
          await audio.setSinkId(isSpeaker.value ? 'default' : speakers[0].deviceId)
        }
      } catch (e) {}
    }
  }

  const durationFormatted = computed(() => {
    const m = Math.floor(callDuration.value / 60).toString().padStart(2, '0')
    const s = (callDuration.value % 60).toString().padStart(2, '0')
    return `${m}:${s}`
  })

  onUnmounted(() => { try { endCall(false) } catch {} })

  return {
    callStatus, callDuration, durationFormatted, isMuted, isSpeaker,
    currentCallId, currentRoomId, remoteUser, incomingCall,
    listenForSignals, startCall, answerCall, declineCall, endCall,
    toggleMute, toggleSpeaker,
  }
}
