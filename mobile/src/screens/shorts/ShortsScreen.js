import React, { useState, useEffect, useRef, useCallback } from 'react'
import {
  View, Text, FlatList, StyleSheet, Dimensions, TouchableOpacity,
  ActivityIndicator, StatusBar,
} from 'react-native'
import { WebView } from 'react-native-webview'
import { useSafeAreaInsets } from 'react-native-safe-area-context'
import { PanGestureHandler, State } from 'react-native-gesture-handler'
import Animated, {
  useAnimatedGestureHandler, useAnimatedStyle, useSharedValue,
  withSpring, runOnJS,
} from 'react-native-reanimated'
import api from '../../services/api'
import { useAuthStore } from '../../stores/authStore'
import { COLORS } from '../../utils/helpers'

const { height: SCREEN_H, width: SCREEN_W } = Dimensions.get('window')

function ShortSlide({ item, isActive, onLike }) {
  const auth = useAuthStore()
  const [liked, setLiked]   = useState(item.is_liked ?? false)
  const [likes, setLikes]   = useState(item.likes_count ?? 0)

  async function handleLike() {
    if (!auth.isLoggedIn) return
    setLiked(l => !l)
    setLikes(n => liked ? n - 1 : n + 1)
    try { await api.post(`/shorts/${item.id}/like`) } catch {}
  }

  // YouTube embed with autoplay
  const embedUrl = isActive && item.embed_url
    ? item.embed_url.replace('autoplay=0', 'autoplay=1').replace('mute=0', 'mute=1')
    : item.embed_url

  return (
    <View style={styles.slide}>
      <StatusBar hidden />
      {embedUrl
        ? (
          <WebView
            source={{ uri: embedUrl }}
            style={StyleSheet.absoluteFill}
            allowsFullscreenVideo
            mediaPlaybackRequiresUserAction={false}
            javaScriptEnabled
            allowsInlineMediaPlayback
          />
        )
        : (
          <View style={[StyleSheet.absoluteFill, { backgroundColor: '#000', justifyContent: 'center', alignItems: 'center' }]}>
            <Text style={{ color: '#fff', fontSize: 48 }}>🎬</Text>
          </View>
        )
      }

      {/* 오버레이: 오른쪽 액션 버튼 */}
      <View style={styles.actions} pointerEvents="box-none">
        <TouchableOpacity style={styles.actionBtn} onPress={handleLike}>
          <Text style={styles.actionIcon}>{liked ? '❤️' : '🤍'}</Text>
          <Text style={styles.actionLabel}>{likes}</Text>
        </TouchableOpacity>
        <TouchableOpacity style={styles.actionBtn}>
          <Text style={styles.actionIcon}>💬</Text>
          <Text style={styles.actionLabel}>{item.comments_count ?? 0}</Text>
        </TouchableOpacity>
        <TouchableOpacity style={styles.actionBtn}>
          <Text style={styles.actionIcon}>↗️</Text>
          <Text style={styles.actionLabel}>공유</Text>
        </TouchableOpacity>
      </View>

      {/* 하단 정보 */}
      <View style={styles.info} pointerEvents="none">
        <Text style={styles.infoUser}>@{item.user?.username ?? item.user?.name ?? '?'}</Text>
        <Text style={styles.infoTitle} numberOfLines={2}>{item.title}</Text>
      </View>
    </View>
  )
}

export default function ShortsScreen() {
  const insets   = useSafeAreaInsets()
  const [shorts, setShorts]   = useState([])
  const [loading, setLoading] = useState(true)
  const [active, setActive]   = useState(0)

  useEffect(() => {
    api.get('/shorts/feed').then(({ data }) => {
      setShorts(data.data ?? data)
    }).catch(() => {}).finally(() => setLoading(false))
  }, [])

  const onViewable = useCallback(({ viewableItems }) => {
    if (viewableItems[0]) setActive(viewableItems[0].index ?? 0)
  }, [])

  if (loading) return (
    <View style={[styles.container, { justifyContent: 'center', alignItems: 'center' }]}>
      <ActivityIndicator size="large" color={COLORS.primary} />
    </View>
  )

  return (
    <View style={styles.container}>
      <FlatList
        data={shorts}
        keyExtractor={item => String(item.id)}
        renderItem={({ item, index }) => (
          <ShortSlide item={item} isActive={index === active} />
        )}
        pagingEnabled
        showsVerticalScrollIndicator={false}
        snapToInterval={SCREEN_H}
        decelerationRate="fast"
        onViewableItemsChanged={onViewable}
        viewabilityConfig={{ itemVisiblePercentThreshold: 60 }}
        getItemLayout={(_, i) => ({ length: SCREEN_H, offset: SCREEN_H * i, index: i })}
        ListEmptyComponent={
          <View style={styles.empty}>
            <Text style={{ fontSize: 48 }}>🎬</Text>
            <Text style={{ color: '#fff', marginTop: 12, fontSize: 15 }}>숏츠가 없습니다</Text>
          </View>
        }
      />
    </View>
  )
}

const styles = StyleSheet.create({
  container:  { flex: 1, backgroundColor: '#000' },
  slide:      { width: SCREEN_W, height: SCREEN_H, backgroundColor: '#000' },
  actions:    { position: 'absolute', right: 12, bottom: 120, alignItems: 'center', gap: 20 },
  actionBtn:  { alignItems: 'center' },
  actionIcon: { fontSize: 30 },
  actionLabel:{ color: '#fff', fontSize: 12, marginTop: 2, fontWeight: '600', textShadowColor: 'rgba(0,0,0,0.8)', textShadowOffset: { width: 0, height: 1 }, textShadowRadius: 3 },
  info:       { position: 'absolute', left: 12, right: 80, bottom: 40 },
  infoUser:   { color: '#fff', fontWeight: '800', fontSize: 15, marginBottom: 4, textShadowColor: 'rgba(0,0,0,0.8)', textShadowOffset: { width: 0, height: 1 }, textShadowRadius: 4 },
  infoTitle:  { color: 'rgba(255,255,255,0.9)', fontSize: 13, lineHeight: 18, textShadowColor: 'rgba(0,0,0,0.8)', textShadowOffset: { width: 0, height: 1 }, textShadowRadius: 4 },
  empty:      { height: SCREEN_H, justifyContent: 'center', alignItems: 'center' },
})
