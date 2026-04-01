import React, { useState, useEffect, useCallback } from 'react'
import {
  View, Text, FlatList, TouchableOpacity, StyleSheet,
  RefreshControl, ActivityIndicator,
} from 'react-native'
import { useSafeAreaInsets } from 'react-native-safe-area-context'
import api from '../../services/api'
import { formatRelative, COLORS } from '../../utils/helpers'

const NOTIF_ICONS = {
  like:    '❤️',
  comment: '💬',
  follow:  '👤',
  chat:    '💌',
  system:  '📢',
  friend:  '🤝',
  match:   '💝',
}

export default function NotificationsScreen({ navigation }) {
  const insets = useSafeAreaInsets()
  const [notifs, setNotifs]       = useState([])
  const [loading, setLoading]     = useState(true)
  const [refreshing, setRefreshing] = useState(false)

  async function fetchNotifs() {
    try {
      const { data } = await api.get('/notifications')
      setNotifs(data.data ?? data)
    } catch {}
    finally { setLoading(false); setRefreshing(false) }
  }

  useEffect(() => { fetchNotifs() }, [])

  async function markRead(id) {
    try {
      await api.post(`/notifications/${id}/read`)
      setNotifs(prev => prev.map(n => n.id === id ? { ...n, read_at: new Date().toISOString() } : n))
    } catch {}
  }

  async function markAllRead() {
    try {
      await api.post('/notifications/read-all')
      setNotifs(prev => prev.map(n => ({ ...n, read_at: n.read_at ?? new Date().toISOString() })))
    } catch {}
  }

  const onRefresh = useCallback(() => { setRefreshing(true); fetchNotifs() }, [])

  function renderNotif({ item }) {
    const unread = !item.read_at
    return (
      <TouchableOpacity
        style={[styles.item, unread && styles.itemUnread]}
        onPress={() => { markRead(item.id) }}
        activeOpacity={0.85}
      >
        <View style={styles.iconWrap}>
          <Text style={styles.icon}>{NOTIF_ICONS[item.type] ?? '🔔'}</Text>
          {unread && <View style={styles.unreadDot} />}
        </View>
        <View style={styles.content}>
          <Text style={styles.message}>{item.data?.message ?? item.message ?? '새로운 알림이 있습니다'}</Text>
          <Text style={styles.time}>{formatRelative(item.created_at)}</Text>
        </View>
      </TouchableOpacity>
    )
  }

  const unreadCount = notifs.filter(n => !n.read_at).length

  return (
    <View style={[styles.container, { paddingTop: insets.top }]}>
      {/* 헤더 */}
      <View style={styles.header}>
        <Text style={styles.headerTitle}>🔔 알림</Text>
        {unreadCount > 0 && (
          <TouchableOpacity onPress={markAllRead} style={styles.readAllBtn}>
            <Text style={styles.readAllText}>모두 읽음</Text>
          </TouchableOpacity>
        )}
      </View>

      {loading
        ? <ActivityIndicator style={{ marginTop: 48 }} size="large" color={COLORS.primary} />
        : (
          <FlatList
            data={notifs}
            keyExtractor={item => String(item.id)}
            renderItem={renderNotif}
            onRefresh={onRefresh}
            refreshing={refreshing}
            contentContainerStyle={{ paddingBottom: insets.bottom + 80 }}
            ItemSeparatorComponent={() => <View style={{ height: 1, backgroundColor: COLORS.gray[100] }} />}
            ListEmptyComponent={
              <View style={styles.empty}>
                <Text style={{ fontSize: 48 }}>🔔</Text>
                <Text style={styles.emptyText}>알림이 없습니다</Text>
              </View>
            }
          />
        )
      }
    </View>
  )
}

const styles = StyleSheet.create({
  container:   { flex: 1, backgroundColor: '#fff' },
  header:      { flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between', paddingHorizontal: 16, paddingVertical: 14, borderBottomWidth: 1, borderBottomColor: COLORS.gray[100] },
  headerTitle: { fontSize: 18, fontWeight: '900', color: COLORS.gray[800] },
  readAllBtn:  { backgroundColor: COLORS.gray[100], paddingHorizontal: 12, paddingVertical: 6, borderRadius: 8 },
  readAllText: { fontSize: 12, color: COLORS.gray[500], fontWeight: '600' },
  item:        { flexDirection: 'row', alignItems: 'flex-start', paddingHorizontal: 16, paddingVertical: 14, gap: 12 },
  itemUnread:  { backgroundColor: '#EFF6FF' },
  iconWrap:    { position: 'relative' },
  icon:        { fontSize: 28 },
  unreadDot:   { position: 'absolute', top: -2, right: -2, width: 8, height: 8, borderRadius: 4, backgroundColor: COLORS.primary },
  content:     { flex: 1 },
  message:     { fontSize: 14, color: COLORS.gray[700], lineHeight: 20 },
  time:        { fontSize: 12, color: COLORS.gray[400], marginTop: 4 },
  empty:       { alignItems: 'center', paddingTop: 80 },
  emptyText:   { color: COLORS.gray[400], fontSize: 15, marginTop: 12 },
})
