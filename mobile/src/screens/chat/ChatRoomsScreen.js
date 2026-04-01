import React, { useState, useEffect, useCallback } from 'react'
import {
  View, Text, FlatList, TouchableOpacity, StyleSheet,
  RefreshControl, ActivityIndicator,
} from 'react-native'
import { useSafeAreaInsets } from 'react-native-safe-area-context'
import api from '../../services/api'
import { formatRelative, COLORS } from '../../utils/helpers'
import AsyncStorage from '@react-native-async-storage/async-storage'

const ROOM_COLORS = {
  regional: ['#3B82F6', '#06B6D4'],
  theme:    ['#8B5CF6', '#EC4899'],
  friend:   ['#10B981', '#34D399'],
}

export default function ChatRoomsScreen({ navigation }) {
  const insets = useSafeAreaInsets()
  const [rooms, setRooms]         = useState([])
  const [loading, setLoading]     = useState(true)
  const [refreshing, setRefreshing] = useState(false)
  const [lastRead, setLastRead]   = useState({})

  async function loadLastRead() {
    try {
      const raw = await AsyncStorage.getItem('chatLastRead')
      if (raw) setLastRead(JSON.parse(raw))
    } catch {}
  }

  async function fetchRooms() {
    try {
      const { data } = await api.get('/chat/rooms')
      setRooms(data)
    } catch {}
    finally { setLoading(false); setRefreshing(false) }
  }

  useEffect(() => { loadLastRead(); fetchRooms() }, [])

  const onRefresh = useCallback(() => { setRefreshing(true); fetchRooms() }, [])

  function getUnread(room) {
    const last = lastRead[room.slug] ?? 0
    return (room.last_message_id ?? 0) > last ? 1 : 0
  }

  function renderRoom({ item }) {
    const colors = ROOM_COLORS[item.type] ?? ROOM_COLORS.friend
    const unread = getUnread(item)
    return (
      <TouchableOpacity
        style={styles.card}
        onPress={() => navigation.navigate('ChatRoom', { room: item })}
        activeOpacity={0.85}
      >
        {/* 컬러 배너 */}
        <View style={[styles.banner, { backgroundColor: colors[0] }]}>
          <Text style={styles.bannerIcon}>{item.icon || '💬'}</Text>
          <View style={{ flex: 1 }}>
            <Text style={styles.bannerName} numberOfLines={1}>{item.name}</Text>
            <Text style={styles.bannerDesc} numberOfLines={1}>{item.description}</Text>
          </View>
          {unread > 0 && (
            <View style={styles.badge}>
              <Text style={styles.badgeText}>{unread > 300 ? '300+' : unread}</Text>
            </View>
          )}
        </View>
        {/* 하단 */}
        <View style={styles.cardFooter}>
          {item.last_message_preview
            ? <Text style={styles.preview} numberOfLines={1}>{item.last_message_preview}</Text>
            : <Text style={styles.previewEmpty}>아직 메시지가 없습니다</Text>
          }
          <View style={styles.liveWrap}>
            <View style={styles.liveDot} />
            <Text style={styles.liveText}>실시간</Text>
          </View>
        </View>
      </TouchableOpacity>
    )
  }

  return (
    <View style={[styles.container, { paddingTop: insets.top }]}>
      {/* 헤더 */}
      <View style={styles.header}>
        <View>
          <Text style={styles.headerTitle}>💬 채팅방</Text>
          <Text style={styles.headerSub}>실시간 커뮤니티 채팅</Text>
        </View>
        <TouchableOpacity style={styles.createBtn} onPress={() => navigation.navigate('CreateRoom')}>
          <Text style={styles.createText}>+ 개설</Text>
        </TouchableOpacity>
      </View>

      {loading
        ? <ActivityIndicator style={{ marginTop: 48 }} size="large" color={COLORS.primary} />
        : (
          <FlatList
            data={rooms}
            keyExtractor={item => item.slug}
            renderItem={renderRoom}
            onRefresh={onRefresh}
            refreshing={refreshing}
            contentContainerStyle={{ padding: 12, gap: 8, paddingBottom: insets.bottom + 80 }}
            ListEmptyComponent={
              <View style={styles.empty}>
                <Text style={{ fontSize: 36, marginBottom: 8 }}>💬</Text>
                <Text style={styles.emptyText}>채팅방이 없습니다</Text>
              </View>
            }
          />
        )
      }
    </View>
  )
}

const styles = StyleSheet.create({
  container:    { flex: 1, backgroundColor: COLORS.gray[100] },
  header:       { backgroundColor: COLORS.primary, flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between', paddingHorizontal: 16, paddingVertical: 14 },
  headerTitle:  { fontSize: 18, fontWeight: '900', color: '#fff' },
  headerSub:    { fontSize: 12, color: 'rgba(255,255,255,0.75)', marginTop: 2 },
  createBtn:    { backgroundColor: '#fff', paddingHorizontal: 14, paddingVertical: 7, borderRadius: 10 },
  createText:   { color: COLORS.primary, fontWeight: '700', fontSize: 13 },
  card:         { backgroundColor: '#fff', borderRadius: 16, overflow: 'hidden', shadowColor: '#000', shadowOpacity: 0.06, shadowRadius: 8, elevation: 2 },
  banner:       { flexDirection: 'row', alignItems: 'center', paddingHorizontal: 14, paddingVertical: 12, gap: 10 },
  bannerIcon:   { fontSize: 22 },
  bannerName:   { fontSize: 14, fontWeight: '800', color: '#fff' },
  bannerDesc:   { fontSize: 11, color: 'rgba(255,255,255,0.75)', marginTop: 1 },
  badge:        { backgroundColor: '#EF4444', borderRadius: 10, paddingHorizontal: 7, paddingVertical: 3 },
  badgeText:    { color: '#fff', fontSize: 11, fontWeight: '800' },
  cardFooter:   { flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between', paddingHorizontal: 14, paddingVertical: 10 },
  preview:      { fontSize: 12, color: COLORS.gray[500], flex: 1, marginRight: 8 },
  previewEmpty: { fontSize: 12, color: COLORS.gray[300], fontStyle: 'italic' },
  liveWrap:     { flexDirection: 'row', alignItems: 'center', gap: 4 },
  liveDot:      { width: 6, height: 6, borderRadius: 3, backgroundColor: '#10B981' },
  liveText:     { fontSize: 11, color: COLORS.gray[400] },
  empty:        { alignItems: 'center', paddingTop: 80 },
  emptyText:    { color: COLORS.gray[400], fontSize: 15 },
})
