import { ref, onUnmounted } from 'vue'
import axios from 'axios'

const ICE_SERVERS = {
  iceServers: [
    { urls: 'stun:stun.l.google.com:19302' },
    { urls: 'stun:stun1.l.google.com:19302' },
  ],
}

export function useWebRTC(currentUserId) {
  const localStream  = ref(null)
  const remoteStream = ref(null)
  const callState    = ref('idle')   // idle | calling | ringing | connected | ended
  const callId       = ref(null)
  const remoteUser   = ref(null)
  const isMuted      = ref(false)
  const isVideoOff   = ref(false)
  const callType     = ref('video')  // video | audio

  let pc        = null   // RTCPeerConnection
  let signalCh  = null   // Echo private channel

  // ── 채널 수신 리스너 등록 ─────────────────────────────────
  function listenForCalls() {
    if (!window.Echo) return
    signalCh = window.Echo.private(`call.${currentUserId}`)
    signalCh.listen('.webrtc.signal', handleSignal)
  }

  function stopListening() {
    if (signalCh) {
      window.Echo?.leave(`call.${currentUserId}`)
      signalCh = null
    }
  }

  // ── 시그널 처리 ───────────────────────────────────────────
  async function handleSignal(data) {
    switch (data.type) {
      case 'call-request':
        callState.value = 'ringing'
        callId.value    = data.call_id
        callType.value  = data.payload?.call_type ?? 'video'
        remoteUser.value = data.payload?.caller ?? { id: data.from_user_id, name: '알 수 없음' }
        break

      case 'answer':
        if (pc && data.payload?.sdp) {
          await pc.setRemoteDescription(new RTCSessionDescription(data.payload))
          callState.value = 'connected'
        }
        break

      case 'ice-candidate':
        if (pc && data.payload?.candidate) {
          try { await pc.addIceCandidate(new RTCIceCandidate(data.payload)) } catch {}
        }
        break

      case 'call-end':
        hangup(false)
        break

      case 'offer':
        if (pc && data.payload?.sdp) {
          await pc.setRemoteDescription(new RTCSessionDescription(data.payload))
          const answer = await pc.createAnswer()
          await pc.setLocalDescription(answer)
          await sendSignal('answer', data.from_user_id, { ...answer }, data.call_id)
          callState.value = 'connected'
        }
        break
    }
  }

  // ── RTCPeerConnection 생성 ────────────────────────────────
  async function createPC(toUserId) {
    pc = new RTCPeerConnection(ICE_SERVERS)

    pc.onicecandidate = (e) => {
      if (e.candidate) {
        sendSignal('ice-candidate', toUserId, e.candidate.toJSON(), callId.value)
      }
    }

    pc.ontrack = (e) => {
      remoteStream.value = e.streams[0]
    }

    pc.onconnectionstatechange = () => {
      if (pc.connectionState === 'disconnected' || pc.connectionState === 'failed') {
        hangup(false)
      }
    }

    // 로컬 트랙 추가
    if (localStream.value) {
      localStream.value.getTracks().forEach(t => pc.addTrack(t, localStream.value))
    }

    return pc
  }

  // ── 전화 걸기 ─────────────────────────────────────────────
  async function call(toUser, type = 'video') {
    if (callState.value !== 'idle') return
    callType.value  = type
    remoteUser.value = toUser
    callState.value = 'calling'
    callId.value    = crypto.randomUUID()

    try {
      localStream.value = await navigator.mediaDevices.getUserMedia({
        video: type === 'video',
        audio: true,
      })
    } catch (e) {
      callState.value = 'idle'
      alert(type === 'video' ? '카메라/마이크 접근 권한이 필요합니다.' : '마이크 접근 권한이 필요합니다.')
      return
    }

    await createPC(toUser.id)

    // 수신자에게 call-request 전송
    await sendSignal('call-request', toUser.id, {
      call_type: type,
      caller: { id: currentUserId, name: '나' },
    }, callId.value)

    // offer 생성
    const offer = await pc.createOffer()
    await pc.setLocalDescription(offer)
    await sendSignal('offer', toUser.id, { ...offer }, callId.value)
  }

  // ── 수신 수락 ─────────────────────────────────────────────
  async function accept() {
    if (callState.value !== 'ringing') return

    try {
      localStream.value = await navigator.mediaDevices.getUserMedia({
        video: callType.value === 'video',
        audio: true,
      })
    } catch {
      alert('카메라/마이크 접근 권한이 필요합니다.')
      reject()
      return
    }

    await createPC(remoteUser.value.id)
    callState.value = 'connected'
    // offer는 signal handler에서 처리됨
  }

  // ── 수신 거절 ─────────────────────────────────────────────
  async function reject() {
    if (remoteUser.value?.id) {
      await sendSignal('call-end', remoteUser.value.id, {}, callId.value)
    }
    cleanup()
  }

  // ── 통화 종료 ─────────────────────────────────────────────
  async function hangup(sendEnd = true) {
    if (sendEnd && remoteUser.value?.id && callId.value) {
      await sendSignal('call-end', remoteUser.value.id, {}, callId.value)
    }
    cleanup()
  }

  function cleanup() {
    if (pc) { pc.close(); pc = null }
    if (localStream.value) { localStream.value.getTracks().forEach(t => t.stop()); localStream.value = null }
    remoteStream.value = null
    callState.value    = 'idle'
    callId.value       = null
    remoteUser.value   = null
  }

  // ── 음소거 토글 ───────────────────────────────────────────
  function toggleMute() {
    if (!localStream.value) return
    const track = localStream.value.getAudioTracks()[0]
    if (track) { track.enabled = !track.enabled; isMuted.value = !track.enabled }
  }

  // ── 카메라 토글 ───────────────────────────────────────────
  function toggleVideo() {
    if (!localStream.value) return
    const track = localStream.value.getVideoTracks()[0]
    if (track) { track.enabled = !track.enabled; isVideoOff.value = !track.enabled }
  }

  // ── 시그널 전송 ───────────────────────────────────────────
  async function sendSignal(type, toUserId, payload = {}, cid = null) {
    try {
      const { data } = await axios.post('/api/call/signal', {
        type, to_user_id: toUserId, payload, call_id: cid ?? callId.value,
      })
      if (!callId.value && data.call_id) callId.value = data.call_id
    } catch {}
  }

  onUnmounted(() => { cleanup(); stopListening() })

  return {
    localStream, remoteStream, callState, callId, remoteUser,
    isMuted, isVideoOff, callType,
    listenForCalls, stopListening,
    call, accept, reject, hangup,
    toggleMute, toggleVideo,
  }
}
