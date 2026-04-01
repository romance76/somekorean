import React, { useState } from 'react'
import {
  View, Text, TextInput, TouchableOpacity, StyleSheet,
  KeyboardAvoidingView, Platform, ScrollView, ActivityIndicator, Alert,
} from 'react-native'
import { LinearGradient } from 'react-native-linear-gradient'
import { useAuthStore } from '../../stores/authStore'
import { COLORS } from '../../utils/helpers'

export default function LoginScreen({ navigation }) {
  const [email, setEmail]       = useState('')
  const [password, setPassword] = useState('')
  const [loading, setLoading]   = useState(false)
  const login = useAuthStore(s => s.login)

  async function handleLogin() {
    if (!email.trim() || !password.trim()) {
      Alert.alert('입력 오류', '이메일과 비밀번호를 입력해주세요.')
      return
    }
    setLoading(true)
    try {
      await login(email.trim(), password)
    } catch (e) {
      Alert.alert('로그인 실패', e?.response?.data?.message || '이메일 또는 비밀번호를 확인해주세요.')
    } finally { setLoading(false) }
  }

  return (
    <LinearGradient colors={['#2563EB', '#1D4ED8']} style={styles.bg}>
      <KeyboardAvoidingView behavior={Platform.OS === 'ios' ? 'padding' : undefined} style={{ flex: 1 }}>
        <ScrollView contentContainerStyle={styles.scroll} keyboardShouldPersistTaps="handled">
          {/* 로고 */}
          <View style={styles.logoWrap}>
            <Text style={styles.logoText}>🇰🇷</Text>
            <Text style={styles.logoTitle}>SomeKorean</Text>
            <Text style={styles.logoSub}>미국 한인 커뮤니티</Text>
          </View>

          {/* 폼 */}
          <View style={styles.card}>
            <Text style={styles.cardTitle}>로그인</Text>

            <Text style={styles.label}>이메일</Text>
            <TextInput
              style={styles.input}
              placeholder="email@example.com"
              placeholderTextColor={COLORS.gray[400]}
              value={email}
              onChangeText={setEmail}
              keyboardType="email-address"
              autoCapitalize="none"
              autoCorrect={false}
            />

            <Text style={styles.label}>비밀번호</Text>
            <TextInput
              style={styles.input}
              placeholder="비밀번호 입력"
              placeholderTextColor={COLORS.gray[400]}
              value={password}
              onChangeText={setPassword}
              secureTextEntry
            />

            <TouchableOpacity
              style={[styles.btn, loading && styles.btnDisabled]}
              onPress={handleLogin}
              disabled={loading}
            >
              {loading
                ? <ActivityIndicator color="#fff" />
                : <Text style={styles.btnText}>로그인</Text>
              }
            </TouchableOpacity>

            <TouchableOpacity onPress={() => navigation.navigate('Register')} style={styles.link}>
              <Text style={styles.linkText}>계정이 없으신가요? <Text style={styles.linkBold}>회원가입</Text></Text>
            </TouchableOpacity>
          </View>
        </ScrollView>
      </KeyboardAvoidingView>
    </LinearGradient>
  )
}

const styles = StyleSheet.create({
  bg:         { flex: 1 },
  scroll:     { flexGrow: 1, justifyContent: 'center', padding: 24 },
  logoWrap:   { alignItems: 'center', marginBottom: 32 },
  logoText:   { fontSize: 56 },
  logoTitle:  { fontSize: 28, fontWeight: '900', color: '#fff', marginTop: 8 },
  logoSub:    { fontSize: 14, color: 'rgba(255,255,255,0.75)', marginTop: 4 },
  card:       { backgroundColor: '#fff', borderRadius: 20, padding: 24, shadowColor: '#000', shadowOpacity: 0.15, shadowRadius: 20, elevation: 8 },
  cardTitle:  { fontSize: 20, fontWeight: '800', color: COLORS.gray[800], marginBottom: 20, textAlign: 'center' },
  label:      { fontSize: 13, fontWeight: '600', color: COLORS.gray[600], marginBottom: 6, marginTop: 12 },
  input:      { backgroundColor: COLORS.gray[50], borderWidth: 1, borderColor: COLORS.gray[200], borderRadius: 12, paddingHorizontal: 16, paddingVertical: 12, fontSize: 15, color: COLORS.gray[800] },
  btn:        { backgroundColor: COLORS.primary, borderRadius: 12, paddingVertical: 14, alignItems: 'center', marginTop: 24 },
  btnDisabled:{ opacity: 0.6 },
  btnText:    { color: '#fff', fontWeight: '800', fontSize: 16 },
  link:       { alignItems: 'center', marginTop: 16 },
  linkText:   { color: COLORS.gray[500], fontSize: 14 },
  linkBold:   { color: COLORS.primary, fontWeight: '700' },
})
