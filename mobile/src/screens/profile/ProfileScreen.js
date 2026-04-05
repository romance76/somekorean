import React, { useState } from 'react'
import {
  View, Text, ScrollView, TouchableOpacity, StyleSheet,
  Image, Alert, Switch,
} from 'react-native'
import { useSafeAreaInsets } from 'react-native-safe-area-context'
import * as ImagePicker from 'expo-image-picker'
import * as LocalAuthentication from 'expo-local-authentication'
import { useAuthStore } from '../../stores/authStore'
import api from '../../services/api'
import { COLORS } from '../../utils/helpers'

const MENU_SECTIONS = [
  {
    title: '내 활동',
    items: [
      { icon: '📝', label: '내 게시글', nav: 'MyPosts' },
      { icon: '💬', label: '내 댓글', nav: 'MyComments' },
      { icon: '🔖', label: '북마크', nav: 'Bookmarks' },
      { icon: '💌', label: '쪽지함', nav: 'Messages' },
    ],
  },
  {
    title: '서비스',
    items: [
      { icon: '⭐', label: '포인트', nav: 'Points' },
      { icon: '🤝', label: '매칭', nav: 'Match' },
      { icon: '🚗', label: '알바라이드', nav: 'Ride' },
      { icon: '👴', label: '안심서비스', nav: 'Elder' },
    ],
  },
  {
    title: '설정',
    items: [
      { icon: '🔔', label: '알림 설정', nav: 'NotifSettings' },
      { icon: '🔒', label: '비밀번호 변경', nav: 'ChangePassword' },
      { icon: '🛡️', label: '차단 목록', nav: 'BlockedUsers' },
    ],
  },
]

export default function ProfileScreen({ navigation }) {
  const insets = useSafeAreaInsets()
  const auth   = useAuthStore()
  const [biometric, setBiometric] = useState(false)

  async function pickAvatar() {
    const res = await ImagePicker.launchImageLibraryAsync({
      mediaTypes: ImagePicker.MediaTypeOptions.Images, quality: 0.8, allowsEditing: true, aspect: [1, 1],
    })
    if (res.canceled) return
    const asset = res.assets[0]
    const fd = new FormData()
    fd.append('avatar', { uri: asset.uri, name: 'avatar.jpg', type: 'image/jpeg' })
    try {
      const { data } = await api.post('/profile/avatar', fd, { headers: { 'Content-Type': 'multipart/form-data' } })
      auth.updateUser({ ...auth.user, avatar: data.avatar })
    } catch { Alert.alert('오류', '프로필 사진 변경 실패') }
  }

  async function logout() {
    Alert.alert('로그아웃', '로그아웃하시겠습니까?', [
      { text: '취소', style: 'cancel' },
      { text: '로그아웃', style: 'destructive', onPress: () => auth.logout() },
    ])
  }

  if (!auth.isLoggedIn) {
    return (
      <View style={[styles.container, { justifyContent: 'center', alignItems: 'center', paddingTop: insets.top }]}>
        <Text style={{ fontSize: 48, marginBottom: 16 }}>👤</Text>
        <Text style={styles.loginTitle}>로그인이 필요합니다</Text>
        <TouchableOpacity style={styles.loginBtn} onPress={() => navigation.navigate('Login')}>
          <Text style={styles.loginBtnText}>로그인 / 회원가입</Text>
        </TouchableOpacity>
      </View>
    )
  }

  return (
    <ScrollView style={[styles.container, { paddingTop: insets.top }]}>
      {/* 프로필 헤더 */}
      <View style={styles.profileHeader}>
        <TouchableOpacity onPress={pickAvatar} style={styles.avatarWrap}>
          {auth.user?.avatar
            ? <Image source={{ uri: auth.user.avatar }} style={styles.avatar} />
            : <View style={styles.avatarPlaceholder}><Text style={styles.avatarInitial}>{(auth.user?.name ?? '?')[0]}</Text></View>
          }
          <View style={styles.avatarEdit}><Text style={{ fontSize: 12 }}>📷</Text></View>
        </TouchableOpacity>
        <View style={styles.profileInfo}>
          <Text style={styles.profileName}>{auth.user?.name}</Text>
          <Text style={styles.profileUsername}>@{auth.user?.username}</Text>
          <Text style={styles.profileEmail}>{auth.user?.email}</Text>
        </View>
        <TouchableOpacity style={styles.editBtn} onPress={() => navigation.navigate('EditProfile')}>
          <Text style={styles.editBtnText}>프로필 편집</Text>
        </TouchableOpacity>
      </View>

      {/* 포인트 카드 */}
      <View style={styles.pointCard}>
        <View style={styles.pointItem}>
          <Text style={styles.pointNum}>{auth.user?.point ?? 0}</Text>
          <Text style={styles.pointLabel}>포인트</Text>
        </View>
        <View style={styles.pointDivider} />
        <View style={styles.pointItem}>
          <Text style={styles.pointNum}>{auth.user?.posts_count ?? 0}</Text>
          <Text style={styles.pointLabel}>게시글</Text>
        </View>
        <View style={styles.pointDivider} />
        <View style={styles.pointItem}>
          <Text style={styles.pointNum}>{auth.user?.friends_count ?? 0}</Text>
          <Text style={styles.pointLabel}>친구</Text>
        </View>
      </View>

      {/* 메뉴 섹션 */}
      {MENU_SECTIONS.map(sec => (
        <View key={sec.title} style={styles.section}>
          <Text style={styles.sectionTitle}>{sec.title}</Text>
          <View style={styles.sectionCard}>
            {sec.items.map((item, i) => (
              <TouchableOpacity
                key={item.label}
                style={[styles.menuItem, i < sec.items.length - 1 && styles.menuItemBorder]}
                onPress={() => navigation.navigate(item.nav)}
              >
                <Text style={styles.menuIcon}>{item.icon}</Text>
                <Text style={styles.menuLabel}>{item.label}</Text>
                <Text style={styles.menuArrow}>›</Text>
              </TouchableOpacity>
            ))}
          </View>
        </View>
      ))}

      {/* 로그아웃 */}
      <TouchableOpacity style={styles.logoutBtn} onPress={logout}>
        <Text style={styles.logoutText}>로그아웃</Text>
      </TouchableOpacity>

      <View style={{ height: insets.bottom + 80 }} />
    </ScrollView>
  )
}

const styles = StyleSheet.create({
  container:         { flex: 1, backgroundColor: COLORS.gray[100] },
  profileHeader:     { backgroundColor: '#fff', padding: 20, flexDirection: 'row', alignItems: 'center', gap: 14 },
  avatarWrap:        { position: 'relative' },
  avatar:            { width: 72, height: 72, borderRadius: 36 },
  avatarPlaceholder: { width: 72, height: 72, borderRadius: 36, backgroundColor: COLORS.primary, justifyContent: 'center', alignItems: 'center' },
  avatarInitial:     { color: '#fff', fontSize: 26, fontWeight: '800' },
  avatarEdit:        { position: 'absolute', bottom: 0, right: 0, backgroundColor: '#fff', borderRadius: 10, padding: 3, borderWidth: 1, borderColor: COLORS.gray[200] },
  profileInfo:       { flex: 1 },
  profileName:       { fontSize: 18, fontWeight: '800', color: COLORS.gray[800] },
  profileUsername:   { fontSize: 13, color: COLORS.gray[400], marginTop: 2 },
  profileEmail:      { fontSize: 12, color: COLORS.gray[400], marginTop: 1 },
  editBtn:           { backgroundColor: COLORS.gray[100], borderRadius: 10, paddingHorizontal: 12, paddingVertical: 6 },
  editBtnText:       { fontSize: 12, color: COLORS.gray[600], fontWeight: '600' },
  pointCard:         { backgroundColor: COLORS.primary, margin: 12, borderRadius: 16, flexDirection: 'row', paddingVertical: 16, shadowColor: COLORS.primary, shadowOpacity: 0.3, shadowRadius: 12, elevation: 4 },
  pointItem:         { flex: 1, alignItems: 'center' },
  pointNum:          { fontSize: 22, fontWeight: '900', color: '#fff' },
  pointLabel:        { fontSize: 12, color: 'rgba(255,255,255,0.75)', marginTop: 2 },
  pointDivider:      { width: 1, backgroundColor: 'rgba(255,255,255,0.3)' },
  section:           { marginHorizontal: 12, marginTop: 16 },
  sectionTitle:      { fontSize: 13, fontWeight: '700', color: COLORS.gray[500], marginBottom: 8, marginLeft: 4 },
  sectionCard:       { backgroundColor: '#fff', borderRadius: 14, overflow: 'hidden' },
  menuItem:          { flexDirection: 'row', alignItems: 'center', paddingHorizontal: 16, paddingVertical: 14, gap: 12 },
  menuItemBorder:    { borderBottomWidth: 1, borderBottomColor: COLORS.gray[100] },
  menuIcon:          { fontSize: 20, width: 28 },
  menuLabel:         { flex: 1, fontSize: 15, color: COLORS.gray[700], fontWeight: '500' },
  menuArrow:         { fontSize: 20, color: COLORS.gray[300] },
  logoutBtn:         { margin: 12, marginTop: 20, backgroundColor: '#fff', borderRadius: 14, paddingVertical: 14, alignItems: 'center', borderWidth: 1, borderColor: '#FEE2E2' },
  logoutText:        { color: COLORS.danger, fontWeight: '700', fontSize: 15 },
  loginTitle:        { fontSize: 18, fontWeight: '700', color: COLORS.gray[600], marginBottom: 24 },
  loginBtn:          { backgroundColor: COLORS.primary, paddingHorizontal: 32, paddingVertical: 14, borderRadius: 14 },
  loginBtnText:      { color: '#fff', fontWeight: '800', fontSize: 16 },
})
