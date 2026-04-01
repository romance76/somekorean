import React, { useState, useEffect, useCallback } from 'react'
import {
  View, Text, FlatList, TouchableOpacity, StyleSheet,
  RefreshControl, ActivityIndicator, Image,
} from 'react-native'
import { useSafeAreaInsets } from 'react-native-safe-area-context'
import api from '../../services/api'
import { formatRelative, COLORS } from '../../utils/helpers'

const TABS = [
  { key: 'community', label: '커뮤니티', icon: '📋' },
  { key: 'jobs',      label: '구인구직', icon: '💼' },
  { key: 'market',    label: '중고장터', icon: '🛍️' },
  { key: 'business',  label: '업소록',   icon: '🏢' },
]

const ENDPOINTS = {
  community: '/posts',
  jobs:      '/jobs',
  market:    '/market',
  business:  '/businesses',
}

export default function CommunityScreen({ navigation }) {
  const insets = useSafeAreaInsets()
  const [tab, setTab]           = useState('community')
  const [items, setItems]       = useState([])
  const [loading, setLoading]   = useState(true)
  const [refreshing, setRefreshing] = useState(false)
  const [page, setPage]         = useState(1)
  const [hasMore, setHasMore]   = useState(true)

  async function fetchItems(p = 1, replace = false) {
    setLoading(true)
    try {
      const { data } = await api.get(ENDPOINTS[tab], { params: { page: p, per_page: 20 } })
      const list = data.data ?? data
      if (replace) setItems(list)
      else setItems(prev => [...prev, ...list])
      setHasMore((data.current_page ?? p) < (data.last_page ?? 1))
      setPage(p)
    } catch {}
    finally { setLoading(false); setRefreshing(false) }
  }

  useEffect(() => { fetchItems(1, true) }, [tab])

  const onRefresh = useCallback(() => { setRefreshing(true); fetchItems(1, true) }, [tab])
  const onEndReached = useCallback(() => { if (hasMore && !loading) fetchItems(page + 1) }, [hasMore, loading, page])

  function navToDetail(item) {
    const screens = { community: 'PostDetail', jobs: 'JobDetail', market: 'MarketDetail', business: 'BusinessDetail' }
    navigation.navigate(screens[tab], { id: item.id })
  }

  function renderItem({ item }) {
    return (
      <TouchableOpacity style={styles.card} onPress={() => navToDetail(item)} activeOpacity={0.85}>
        <View style={styles.cardBody}>
          <Text style={styles.cardTitle} numberOfLines={2}>{item.title ?? item.name ?? item.position ?? '(제목 없음)'}</Text>
          {(item.content ?? item.description) && (
            <Text style={styles.cardPreview} numberOfLines={2}>{item.content ?? item.description}</Text>
          )}
          <View style={styles.cardMeta}>
            <Text style={styles.cardMetaText}>{formatRelative(item.created_at)}</Text>
            {item.price && <Text style={styles.price}>${item.price}</Text>}
            {item.salary && <Text style={styles.price}>{item.salary}</Text>}
          </View>
        </View>
        {item.images?.[0] && (
          <Image source={{ uri: item.images[0] }} style={styles.thumb} />
        )}
      </TouchableOpacity>
    )
  }

  return (
    <View style={[styles.container, { paddingTop: insets.top }]}>
      {/* 탭 */}
      <View style={styles.tabs}>
        {TABS.map(t => (
          <TouchableOpacity key={t.key} onPress={() => setTab(t.key)} style={[styles.tab, tab === t.key && styles.tabActive]}>
            <Text style={styles.tabIcon}>{t.icon}</Text>
            <Text style={[styles.tabLabel, tab === t.key && styles.tabLabelActive]}>{t.label}</Text>
          </TouchableOpacity>
        ))}
      </View>

      {loading && !refreshing
        ? <ActivityIndicator style={{ marginTop: 48 }} size="large" color={COLORS.primary} />
        : (
          <FlatList
            data={items}
            keyExtractor={item => String(item.id)}
            renderItem={renderItem}
            onRefresh={onRefresh}
            refreshing={refreshing}
            onEndReached={onEndReached}
            onEndReachedThreshold={0.3}
            contentContainerStyle={{ padding: 12, gap: 8, paddingBottom: insets.bottom + 80 }}
            ListEmptyComponent={
              <View style={styles.empty}>
                <Text style={{ fontSize: 36 }}>📋</Text>
                <Text style={styles.emptyText}>게시글이 없습니다</Text>
              </View>
            }
          />
        )
      }

      <TouchableOpacity
        style={[styles.fab, { bottom: insets.bottom + 76 }]}
        onPress={() => navigation.navigate('PostWrite', { type: tab })}
      >
        <Text style={styles.fabText}>✏️</Text>
      </TouchableOpacity>
    </View>
  )
}

const styles = StyleSheet.create({
  container:      { flex: 1, backgroundColor: COLORS.gray[100] },
  tabs:           { backgroundColor: '#fff', flexDirection: 'row', borderBottomWidth: 1, borderBottomColor: COLORS.gray[100] },
  tab:            { flex: 1, alignItems: 'center', paddingVertical: 10, gap: 2 },
  tabActive:      { borderBottomWidth: 2, borderBottomColor: COLORS.primary },
  tabIcon:        { fontSize: 18 },
  tabLabel:       { fontSize: 11, color: COLORS.gray[400], fontWeight: '600' },
  tabLabelActive: { color: COLORS.primary },
  card:           { backgroundColor: '#fff', borderRadius: 14, padding: 14, flexDirection: 'row', gap: 12, shadowColor: '#000', shadowOpacity: 0.05, shadowRadius: 6, elevation: 1 },
  cardBody:       { flex: 1 },
  cardTitle:      { fontSize: 15, fontWeight: '700', color: COLORS.gray[800], marginBottom: 4 },
  cardPreview:    { fontSize: 13, color: COLORS.gray[500], lineHeight: 18, marginBottom: 6 },
  cardMeta:       { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center' },
  cardMetaText:   { fontSize: 11, color: COLORS.gray[400] },
  price:          { fontSize: 13, fontWeight: '700', color: COLORS.primary },
  thumb:          { width: 72, height: 72, borderRadius: 10, backgroundColor: COLORS.gray[200] },
  empty:          { alignItems: 'center', paddingTop: 64, gap: 8 },
  emptyText:      { color: COLORS.gray[400], fontSize: 15 },
  fab:            { position: 'absolute', right: 20, width: 52, height: 52, borderRadius: 26, backgroundColor: COLORS.primary, justifyContent: 'center', alignItems: 'center', shadowColor: COLORS.primary, shadowOpacity: 0.4, shadowRadius: 12, elevation: 6 },
  fabText:        { fontSize: 22 },
})
