import React, { useState, useEffect, useCallback } from 'react'
import {
  View, Text, FlatList, TouchableOpacity, StyleSheet,
  RefreshControl, ActivityIndicator, Image, TextInput,
} from 'react-native'
import { useSafeAreaInsets } from 'react-native-safe-area-context'
import api from '../../services/api'
import { formatRelative, COLORS } from '../../utils/helpers'

const CATEGORIES = [
  { key: 'all', label: '전체' },
  { key: 'community', label: '커뮤니티' },
  { key: 'jobs', label: '구인구직' },
  { key: 'market', label: '중고장터' },
  { key: 'businesses', label: '업소록' },
]

export default function HomeScreen({ navigation }) {
  const insets = useSafeAreaInsets()
  const [posts, setPosts]       = useState([])
  const [loading, setLoading]   = useState(true)
  const [refreshing, setRefreshing] = useState(false)
  const [cat, setCat]           = useState('all')
  const [page, setPage]         = useState(1)
  const [hasMore, setHasMore]   = useState(true)

  async function fetchPosts(p = 1, replace = false) {
    try {
      const { data } = await api.get('/posts', { params: { page: p, per_page: 20 } })
      const list = data.data ?? data
      if (replace) setPosts(list)
      else setPosts(prev => [...prev, ...list])
      setHasMore((data.current_page ?? p) < (data.last_page ?? 1))
      setPage(p)
    } catch {}
    finally { setLoading(false); setRefreshing(false) }
  }

  useEffect(() => { fetchPosts(1, true) }, [])

  const onRefresh = useCallback(() => {
    setRefreshing(true); fetchPosts(1, true)
  }, [])

  const onEndReached = useCallback(() => {
    if (hasMore && !loading) fetchPosts(page + 1)
  }, [hasMore, loading, page])

  function renderPost({ item }) {
    return (
      <TouchableOpacity
        style={styles.card}
        onPress={() => navigation.navigate('PostDetail', { id: item.id })}
        activeOpacity={0.85}
      >
        {item.images?.[0] && (
          <Image source={{ uri: item.images[0] }} style={styles.cardImage} />
        )}
        <View style={styles.cardBody}>
          <View style={styles.cardMeta}>
            <Text style={styles.cardBoard}>{item.board?.name ?? '커뮤니티'}</Text>
            <Text style={styles.cardTime}>{formatRelative(item.created_at)}</Text>
          </View>
          <Text style={styles.cardTitle} numberOfLines={2}>{item.title}</Text>
          <Text style={styles.cardPreview} numberOfLines={2}>{item.content}</Text>
          <View style={styles.cardFooter}>
            <View style={styles.cardUser}>
              <View style={styles.avatar}>
                {item.user?.avatar
                  ? <Image source={{ uri: item.user.avatar }} style={styles.avatarImg} />
                  : <Text style={styles.avatarText}>{(item.user?.name ?? '?')[0]}</Text>
                }
              </View>
              <Text style={styles.userName}>{item.user?.name ?? '익명'}</Text>
            </View>
            <View style={styles.stats}>
              <Text style={styles.stat}>👁 {item.views_count ?? 0}</Text>
              <Text style={styles.stat}>❤️ {item.likes_count ?? 0}</Text>
              <Text style={styles.stat}>💬 {item.comments_count ?? 0}</Text>
            </View>
          </View>
        </View>
      </TouchableOpacity>
    )
  }

  return (
    <View style={[styles.container, { paddingTop: insets.top }]}>
      {/* 상단 헤더 */}
      <View style={styles.header}>
        <Text style={styles.headerLogo}>🇰🇷 SomeKorean</Text>
        <TouchableOpacity onPress={() => navigation.navigate('Search')} style={styles.searchBtn}>
          <Text style={styles.searchIcon}>🔍</Text>
        </TouchableOpacity>
      </View>

      {/* 카테고리 탭 */}
      <View style={styles.tabs}>
        {CATEGORIES.map(c => (
          <TouchableOpacity
            key={c.key}
            onPress={() => setCat(c.key)}
            style={[styles.tab, cat === c.key && styles.tabActive]}
          >
            <Text style={[styles.tabText, cat === c.key && styles.tabTextActive]}>{c.label}</Text>
          </TouchableOpacity>
        ))}
      </View>

      {loading && !refreshing
        ? <ActivityIndicator style={{ marginTop: 48 }} size="large" color={COLORS.primary} />
        : (
          <FlatList
            data={posts}
            keyExtractor={item => String(item.id)}
            renderItem={renderPost}
            onRefresh={onRefresh}
            refreshing={refreshing}
            onEndReached={onEndReached}
            onEndReachedThreshold={0.3}
            contentContainerStyle={{ paddingBottom: insets.bottom + 80 }}
            ListEmptyComponent={
              <View style={styles.empty}>
                <Text style={styles.emptyText}>게시글이 없습니다</Text>
              </View>
            }
            ListFooterComponent={hasMore ? <ActivityIndicator style={{ padding: 16 }} color={COLORS.primary} /> : null}
          />
        )
      }

      {/* 글쓰기 FAB */}
      <TouchableOpacity
        style={[styles.fab, { bottom: insets.bottom + 76 }]}
        onPress={() => navigation.navigate('PostWrite')}
      >
        <Text style={styles.fabText}>✏️</Text>
      </TouchableOpacity>
    </View>
  )
}

const styles = StyleSheet.create({
  container:    { flex: 1, backgroundColor: COLORS.gray[100] },
  header:       { backgroundColor: '#fff', flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between', paddingHorizontal: 16, paddingVertical: 12, borderBottomWidth: 1, borderBottomColor: COLORS.gray[100] },
  headerLogo:   { fontSize: 17, fontWeight: '900', color: COLORS.primary },
  searchBtn:    { padding: 4 },
  searchIcon:   { fontSize: 20 },
  tabs:         { backgroundColor: '#fff', flexDirection: 'row', paddingHorizontal: 12, paddingBottom: 8, gap: 6 },
  tab:          { paddingHorizontal: 14, paddingVertical: 6, borderRadius: 20, backgroundColor: COLORS.gray[100] },
  tabActive:    { backgroundColor: COLORS.primary },
  tabText:      { fontSize: 13, fontWeight: '600', color: COLORS.gray[500] },
  tabTextActive:{ color: '#fff' },
  card:         { backgroundColor: '#fff', marginHorizontal: 12, marginTop: 10, borderRadius: 16, overflow: 'hidden', shadowColor: '#000', shadowOpacity: 0.06, shadowRadius: 8, elevation: 2 },
  cardImage:    { width: '100%', height: 160, backgroundColor: COLORS.gray[200] },
  cardBody:     { padding: 14 },
  cardMeta:     { flexDirection: 'row', justifyContent: 'space-between', marginBottom: 6 },
  cardBoard:    { fontSize: 11, fontWeight: '700', color: COLORS.primary, backgroundColor: '#EFF6FF', paddingHorizontal: 8, paddingVertical: 2, borderRadius: 6 },
  cardTime:     { fontSize: 11, color: COLORS.gray[400] },
  cardTitle:    { fontSize: 15, fontWeight: '700', color: COLORS.gray[800], marginBottom: 4 },
  cardPreview:  { fontSize: 13, color: COLORS.gray[500], lineHeight: 18, marginBottom: 10 },
  cardFooter:   { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center' },
  cardUser:     { flexDirection: 'row', alignItems: 'center', gap: 6 },
  avatar:       { width: 24, height: 24, borderRadius: 12, backgroundColor: COLORS.gray[200], overflow: 'hidden', justifyContent: 'center', alignItems: 'center' },
  avatarImg:    { width: 24, height: 24 },
  avatarText:   { fontSize: 11, fontWeight: '700', color: COLORS.primary },
  userName:     { fontSize: 12, color: COLORS.gray[500] },
  stats:        { flexDirection: 'row', gap: 10 },
  stat:         { fontSize: 12, color: COLORS.gray[400] },
  empty:        { alignItems: 'center', paddingTop: 64 },
  emptyText:    { color: COLORS.gray[400], fontSize: 15 },
  fab:          { position: 'absolute', right: 20, width: 52, height: 52, borderRadius: 26, backgroundColor: COLORS.primary, justifyContent: 'center', alignItems: 'center', shadowColor: COLORS.primary, shadowOpacity: 0.4, shadowRadius: 12, elevation: 6 },
  fabText:      { fontSize: 22 },
})
