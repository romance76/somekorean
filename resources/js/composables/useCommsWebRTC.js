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
  // ── 상태 ──────────────────────────────────────────────────────
  // idle → calling/ringing → connecting → connected → ended → idle
  const callStatus         = ref('idle')
  const callDuration       = ref(0)
  const isMuted            = ref(false)
  const isSpeaker          = ref(true)
  const currentCallId      = ref(null)
  const currentRoomId      = ref(null)
  const remoteUser         = ref(null)
  const incomingCall       = ref(null)
  const remoteAudioBlocked = ref(false)  // 모바일 autoplay 차단 시 true

  let pc = null
  let localStream = null
  let durationTimer = null
  let missedTimer = null
  let disconnectTimer = null
  let pendingOffer = null
  let pendingIceCandidates = []

  // ── SDP 정리 ──────────────────────────────────────────────────
  function sanitizeSdp(sdpObj) {
    if (!sdpObj || !sdpObj.sdp) return sdpObj
    return {
      type: sdpObj.type,
      sdp: sdpObj.sdp.replace(/ +(\r?\n)/g, '$1').replace(/\r?\n/g, '\r\n')
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
        }).catch(() => {})
      }
    }

    // ★ 원격 오디오 트랙 수신
    pc.ontrack = (event) => {
      const stream = event.streams[0]
      console.log('[WebRTC] 🔊 Remote track received:', stream.getAudioTracks().length, 'audio tracks')

      const audio = document.getElementById('sk-remote-audio')
      if (!audio) {
        console.error('[WebRTC] ❌ <audio> element not found!')
        return
      }

      audio.srcObject = stream
      const playPromise = audio.play()
      if (playPromise) {
        playPromise.then(() => {
          remoteAudioBlocked.value = false
          console.log('[WebRTC] ✅ Remote audio playing')
        }).catch(e => {
          console.warn('[WebRTC] ⚠️ audio.play() blocked:', e.name)
          remoteAudioBlocked.value = true
        })
      }
    }

    // ★ 연결 상태 변화 — callStatus='connected'의 유일한 출처
    pc.onconnectionstatechange = () => {
      const state = pc?.connectionState
      console.log('[WebRTC] Connection state:', state)

      if (state === 'connected') {
        if (disconnectTimer) { clearTimeout(disconnectTimer); disconnectTimer = null }
        if (callStatus.value !== 'connected') {
          callStatus.value = 'connected'
          startDurationTimer()
          console.log('[WebRTC] ✅ P2P Connected — audio active!')
        }
      }
      if (state === 'failed') {
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

  // ── 마이크 획득 ────────────────────────────────────────────────
  async function getLocalStream() {
    if (localStream) return localStream
    try {
      localStream = await navigator.mediaDevices.getUserMedia({ audio: true, video: false })
      console.log('[WebRTC] ✅ Mic:', localStream.getAudioTracks()[0]?.label)
      return localStream
    } catch (err) {
      console.error('[WebRTC] ❌ Mic failed:', err.name, err.message)
      return null
    }
  }

  // ── 타이머 ────────────────────────────────────────────────────
  function startDurationTimer() {
    stopDurationTimer()
    callDuration.value = 0
    durationTimer = setInterval(() => callDuration.value++, 1000)
  }
  function stopDurationTimer() {
    if (durationTimer) { clearInterval(durationTimer); durationTimer = null }
  }

  // ── 통화 종료 처리 ────────────────────────────────────────────
  function handleCallEnded() {
    stopDurationTimer()
    stopRingtone()
    if (missedTimer) { clearTimeout(missedTimer); missedTimer = null }
    if (disconnectTimer) { clearTimeout(disconnectTimer); disconnectTimer = null }
    remoteAudioBlocked.value = false
    const audio = document.getElementById('sk-remote-audio')
    if (audio) { audio.pause(); audio.srcObject = null }
    localStream?.getTracks().forEach(t => t.stop())
    if (pc) { try { pc.close() } catch {} }
    pc = null
    localStream = null
    pendingOffer = null
    pendingIceCandidates = []
    callStatus.value = 'ended'
    const endedCallId = currentCallId.value
    setTimeout(() => {
      if (currentCallId.value === endedCallId || callStatus.value === 'ended') {
        callStatus.value = 'idle'
        currentCallId.value = null
        currentRoomId.value = null
        remoteUser.value = null
        incomingCall.value = null
      }
    }, 3000)
  }

  // ── 오디오 차단 해제 (사용자가 "소리 켜기" 버튼 탭) ──────────
  function unblockRemoteAudio() {
    const audio = document.getElementById('sk-remote-audio')
    if (audio && audio.srcObject) {
      audio.play().then(() => {
        remoteAudioBlocked.value = false
        console.log('[WebRTC] ✅ Audio unblocked by user tap')
      }).catch(e => {
        console.warn('[WebRTC] Manual unblock failed:', e)
      })
    }
  }

  // ── WebSocket 시그널 수신 ─────────────────────────────────────
  function listenForSignals(myUserId) {
    if (!window.Echo) { console.warn('[WebRTC] Echo not available'); return }

    window.Echo.private(`user.${myUserId}`)
      .listen('.webrtc.signal', async (event) => {
        const { type, payload, room_id } = event
        console.log('[WebRTC] Signal:', type)

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
            // ★ connected는 여기서 설정하지 않음! onconnectionstatechange가 처리
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
          // 서버가 수신자 수락 확인 — P2P는 아직 미연결
          // onconnectionstatechange가 실제 연결 시 'connected' 설정
          console.log('[WebRTC] Call answered by remote, awaiting P2P...')
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

    // ★ getUserMedia 최우선 — user gesture 소비 전에
    const stream = await getLocalStream()

    try {
      const { data } = await axios.post('/api/comms/calls/initiate', { callee_id: targetUser.id })
      currentCallId.value = data.call_id
      currentRoomId.value = data.room_id

      createPeerConnection(data.room_id, targetUser.id)
      if (stream && pc) {
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
      console.log('[WebRTC] ✅ Offer sent')
      startCallMonitor()
    } catch (err) {
      console.error('[WebRTC] startCall failed:', err)
      handleCallEnded()
    }
  }

  // ── 수신 수락 ──────────────────────────────────────────────────
  async function answerCall() {
    if (!incomingCall.value) return

    // ★ await 전에 데이터 복사 (async 중 null 방지)
    const { call_id, room_id, caller_id, caller_name, caller_avatar } = { ...incomingCall.value }

    // 즉시 상태 업데이트
    currentCallId.value = call_id
    currentRoomId.value = room_id
    remoteUser.value = { id: caller_id, name: caller_name, avatar: caller_avatar }
    callStatus.value = 'connecting'  // ★ 'connected' 아님! P2P 연결 전
    incomingCall.value = null
    stopRingtone()
    if (missedTimer) { clearTimeout(missedTimer); missedTimer = null }

    // ★ getUserMedia — 마이크 권한 (user gesture 체인)
    const stream = await getLocalStream()
    startCallMonitor()

    try {
      // 서버에 수락 알림
      await axios.post(`/api/comms/calls/${call_id}/answer`).catch(() => {})

      // PeerConnection 생성 + 트랙 추가
      createPeerConnection(room_id, caller_id)
      if (stream && pc) {
        stream.getTracks().forEach(t => pc.addTrack(t, stream))
      }

      // 버퍼된 offer 처리
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
        console.log('[WebRTC] ✅ Answer sent')
      }
      // ★ 여기서 connected 설정 안 함 — onconnectionstatechange가 처리
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

  // ── 폴링 모니터 ───────────────────────────────────────────────
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

  // ── 컨트롤 ────────────────────────────────────────────────────
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
      } catch {}
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
    remoteAudioBlocked, unblockRemoteAudio,
    listenForSignals, startCall, answerCall, declineCall, endCall,
    toggleMute, toggleSpeaker,
  }
}
