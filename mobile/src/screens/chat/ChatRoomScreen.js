import React, { useState, useEffect, useRef, useCallback } from 'react'
import {
  View, Text, FlatList, TextInput, TouchableOpacity, StyleSheet,
  KeyboardAvoidingView, Platform, ActivityIndicator, Image,
  ActionSheetIOS, Alert,
} from 'react-native'
import { useSafeAreaInsets } from 'react-native-safe-area-context'
import * as ImagePicker from 'expo-image-picker'
import AsyncStorage from '@react-native-async-storage/async-storage'
import api from '../../services/api'
import { useAuthStore } from '../../stores/authStore'
import { formatDate, formatTime, COLORS } from '../../utils/helpers'

export default function ChatRoomScreen({ route, navigation }) {
  const { room } = route.params
  const insets   = useSafeAreaInsets()
  const auth     = useAuthStore()
  const listRef  = useRef(null)

  const [messages, setMessages]   = useState([])
  const [blocked, setBlocked]     = useState([])
  const [input, setInput]         = useState('')
  const [sending, setSending]     = useState(false)
  const [loading, setLoading]     = useState(true)

  useEffect(() => {
    navigation.setOptions({ title: room.name })
    load()
    return () => saveLastRead()
  }, [])

  async function load() {
    try {
      const { data } = await api.get(`/chat/rooms/${room.slug}`)
      setMessages(data.messages ?? [])
      setBlocked(data.blocked_ids ?? [])
      setTimeout(() => listRef.current?.scrollToEnd({ animated: false }), 100)
    } catch {}
    finally { setLoading(false) }
  }

  async function saveLastRead() {
    const last = messages[messages.length - 1]
    if (!last) return
    try {
      const raw = await AsyncStorage.getItem('chatLastRead')
      const obj = raw ? JSON.parse(raw) : {}
      obj[room.slug] = last.id
      await AsyncStorage.setItem('chatLastRead', JSON.stringify(obj))
    } catch {}
  }

  async function send() {
    if (!input.trim() || sending) return
    const text = input.trim(); setInput(''); setSending(true)
    try {
      const { data } = await api.post(`/chat/rooms/${room.slug}/messages`, { message: text })
      setMessages(prev => [...prev, data])
      setTimeout(() => listRef.current?.scrollToEnd({ animated: true }), 50)
    } catch { setInput(text) }
    finally { setSending(false) }
  }

  async function pickFile() {
    const res = await ImagePicker.launchImageLibraryAsync({
      mediaTypes: ImagePicker.MediaTypeOptions.All, quality: 0.8,
    })
    if (res.canceled) return
    const asset = res.assets[0]
    const fd = new FormData()
    fd.append('file', { uri: asset.uri, name: asset.fileName ?? 'upload.jpg', type: asset.mimeType ?? 'image/jpeg' })
    setSending(true)
    try {
      const { data } = await api.post(`/chat/rooms/${room.slug}/messages`, fd, {
        headers: { 'Content-Type': 'multipart/form-data' },
      })
      setMessages(prev => [...prev, data])
      setTimeout(() => listRef.current?.scrollToEnd({ animated: true }), 50)
    } catch { Alert.alert('오류', '파일 전송 실패. 10MB 이하만 가능합니다.') }
    finally { setSending(false) }
  }

  function onLongPress(msg) {
    if (!auth.isLoggedIn) return
    if (Platform.OS === 'ios') {
      ActionSheetIOS.showActionSheetWithOptions(
        { options: ['취소', '차단하기', '신고하기'], destructiveButtonIndex: 2, cancelButtonIndex: 0 },
        i => { if (i === 1) blockUser(msg.user); if (i === 2) reportMsg(msg) }
      )
    } else {
      Alert.alert('메시지', '', [
        { text: '차단하기', onPress: () => blockUser(msg.user) },
        { text: '신고하기', style: 'destructive', onPress: () => reportMsg(msg) },
        { text: '취소', style: 'cancel' },
      ])
    }
  }

  async function blockUser(user) {
    if (!user?.id) return
    Alert.alert('차단', `${user.name ?? '이 사용자'}님을 차단하시겠습니까?`, [
      { text: '취소', style: 'cancel' },
      { text: '차단', style: 'destructive', onPress: async () => {
        try { await api.post(`/chat/block/${user.id}`); setBlocked(b => [...b, user.id]) } catch {}
      }},
    ])
  }

  async function reportMsg(msg) {
    try { await api.post(`/chat/report/${msg.id}`); Alert.alert('완료', '신고가 접수되었습니다.') } catch {}
  }

  // 날짜 구분선
  function groupMessages() {
    const groups = []
    let curDate = null
    messages.filter(m => !blocked.includes(m.user?.id ?? m.user_id)).forEach(m => {
      const d = formatDate(m.created_at)
      if (d !== curDate) { groups.push({ type: 'date', key: `date-${d}`, label: d }); curDate = d }
      groups.push({ type: 'msg', key: String(m.id), msg: m })
    })
    return groups
  }

  function isMe(msg) { return msg.user?.id === auth.user?.id || msg.user_id === auth.user?.id }

  function renderItem({ item }) {
    if (item.type === 'date') {
      return (
        <View style={styles.dateSep}>
          <View style={styles.dateLine} />
          <Text style={styles.dateLabel}>{item.label}</Text>
          <View style={styles.dateLine} />
        </View>
      )
    }
    const msg = item.msg
    const me  = isMe(msg)
    return (
      <TouchableOpacity
        activeOpacity={0.85}
        onLongPress={() => !me && onLongPress(msg)}
        style={[styles.msgRow, me ? styles.msgRowMe : styles.msgRowOther]}
      >
        {!me && (
          <View style={styles.avatar}>
            {msg.user?.avatar
              ? <Image source={{ uri: msg.user.avatar }} style={styles.avatarImg} />
              : <Text style={styles.avatarText}>{(msg.user?.name ?? '?')[0]}</Text>
            }
          </View>
        )}
        <View style={{ maxWidth: '72%' }}>
          {!me && <Text style={styles.msgUser}>{msg.user?.name ?? '?'}</Text>}
          <View style={[styles.bubble, me ? styles.bubbleMe : styles.bubbleOther]}>
            {msg.file_type === 'image' && msg.file_url
              ? <Image source={{ uri: msg.file_url }} style={styles.msgImage} resizeMode="contain" />
              : msg.file_url
                ? <Text style={[styles.msgText, me && styles.msgTextMe]}>📎 {msg.file_name || '파일'}</Text>
                : <Text style={[styles.msgText, me && styles.msgTextMe]}>{msg.message}</Text>
            }
          </View>
          <Text style={[styles.msgTime, me && { textAlign: 'right' }]}>{formatTime(msg.created_at)}</Text>
        </View>
      </TouchableOpacity>
    )
  }

  return (
    <KeyboardAvoidingView
      style={{ flex: 1, backgroundColor: COLORS.gray[50] }}
      behavior={Platform.OS === 'ios' ? 'padding' : undefined}
      keyboardVerticalOffset={Platform.OS === 'ios' ? 90 : 0}
    >
      {loading
        ? <ActivityIndicator style={{ flex: 1 }} size="large" color={COLORS.primary} />
        : (
          <FlatList
            ref={listRef}
            data={groupMessages()}
            keyExtractor={item => item.key}
            renderItem={renderItem}
            contentContainerStyle={{ padding: 12, paddingBottom: 8 }}
            onContentSizeChange={() => listRef.current?.scrollToEnd({ animated: false })}
          />
        )
      }

      {/* 입력창 */}
      <View style={[styles.inputBar, { paddingBottom: Math.max(insets.bottom, 8) }]}>
        <TouchableOpacity onPress={pickFile} style={styles.attachBtn} disabled={!auth.isLoggedIn}>
          <Text style={styles.attachIcon}>📎</Text>
        </TouchableOpacity>
        <TextInput
          style={styles.input}
          placeholder={auth.isLoggedIn ? '메시지를 입력하세요...' : '로그인 후 채팅 가능'}
          placeholderTextColor={COLORS.gray[400]}
          value={input}
          onChangeText={setInput}
          multiline
          maxLength={500}
          editable={auth.isLoggedIn}
          onSubmitEditing={send}
          returnKeyType="send"
        />
        <TouchableOpacity
          style={[styles.sendBtn, (!input.trim() || sending) && styles.sendBtnDisabled]}
          onPress={auth.isLoggedIn ? send : () => navigation.navigate('Login')}
          disabled={auth.isLoggedIn && (!input.trim() || sending)}
        >
          {sending
            ? <ActivityIndicator size="small" color="#fff" />
            : <Text style={styles.sendText}>{auth.isLoggedIn ? '전송' : '로그인'}</Text>
          }
        </TouchableOpacity>
      </View>
    </KeyboardAvoidingView>
  )
}

const styles = StyleSheet.create({
  dateSep:       { flexDirection: 'row', alignItems: 'center', marginVertical: 16, gap: 8 },
  dateLine:      { flex: 1, height: 1, backgroundColor: COLORS.gray[200] },
  dateLabel:     { fontSize: 12, color: COLORS.gray[400], backgroundColor: '#fff', paddingHorizontal: 10, paddingVertical: 3, borderRadius: 10, borderWidth: 1, borderColor: COLORS.gray[200] },
  msgRow:        { flexDirection: 'row', marginBottom: 6, alignItems: 'flex-end', gap: 6 },
  msgRowMe:      { justifyContent: 'flex-end' },
  msgRowOther:   { justifyContent: 'flex-start' },
  avatar:        { width: 32, height: 32, borderRadius: 16, backgroundColor: '#DBEAFE', justifyContent: 'center', alignItems: 'center', overflow: 'hidden', flexShrink: 0 },
  avatarImg:     { width: 32, height: 32 },
  avatarText:    { fontSize: 13, fontWeight: '700', color: COLORS.primary },
  msgUser:       { fontSize: 11, color: COLORS.gray[400], marginBottom: 3, marginLeft: 2 },
  bubble:        { borderRadius: 18, paddingHorizontal: 12, paddingVertical: 8, maxWidth: '100%' },
  bubbleMe:      { backgroundColor: COLORS.primary, borderBottomRightRadius: 4 },
  bubbleOther:   { backgroundColor: '#fff', borderBottomLeftRadius: 4, shadowColor: '#000', shadowOpacity: 0.06, shadowRadius: 4, elevation: 1 },
  msgText:       { fontSize: 14, color: COLORS.gray[800], lineHeight: 20 },
  msgTextMe:     { color: '#fff' },
  msgImage:      { width: 200, height: 150, borderRadius: 10 },
  msgTime:       { fontSize: 10, color: COLORS.gray[400], marginTop: 2, marginHorizontal: 4 },
  inputBar:      { backgroundColor: '#fff', borderTopWidth: 1, borderTopColor: COLORS.gray[200], flexDirection: 'row', alignItems: 'flex-end', paddingHorizontal: 10, paddingTop: 8, gap: 6 },
  attachBtn:     { padding: 8 },
  attachIcon:    { fontSize: 20 },
  input:         { flex: 1, backgroundColor: COLORS.gray[50], borderWidth: 1, borderColor: COLORS.gray[200], borderRadius: 20, paddingHorizontal: 14, paddingVertical: 8, fontSize: 14, color: COLORS.gray[800], maxHeight: 100 },
  sendBtn:       { backgroundColor: COLORS.primary, borderRadius: 20, paddingHorizontal: 16, paddingVertical: 9, justifyContent: 'center', alignItems: 'center' },
  sendBtnDisabled:{ opacity: 0.5 },
  sendText:      { color: '#fff', fontWeight: '700', fontSize: 14 },
})
