import React, { useState } from 'react'
import {
  View, Text, TextInput, TouchableOpacity, StyleSheet,
  KeyboardAvoidingView, Platform, ScrollView, ActivityIndicator, Alert,
} from 'react-native'
import { useAuthStore } from '../../stores/authStore'
import { COLORS } from '../../utils/helpers'

export default function RegisterScreen({ navigation }) {
  const [form, setForm] = useState({ name: '', username: '', email: '', password: '', password_confirmation: '' })
  const [loading, setLoading] = useState(false)
  const register = useAuthStore(s => s.register)

  function set(key, val) { setForm(f => ({ ...f, [key]: val })) }

  async function handleRegister() {
    if (!form.name || !form.username || !form.email || !form.password) {
      Alert.alert('입력 오류', '모든 항목을 입력해주세요.'); return
    }
    if (form.password !== form.password_confirmation) {
      Alert.alert('오류', '비밀번호가 일치하지 않습니다.'); return
    }
    setLoading(true)
    try {
      await register(form)
    } catch (e) {
      const msg = e?.response?.data?.message || e?.response?.data?.errors
        ? Object.values(e.response.data.errors).flat().join('\n')
        : '회원가입 실패. 다시 시도해주세요.'
      Alert.alert('회원가입 실패', msg)
    } finally { setLoading(false) }
  }

  return (
    <KeyboardAvoidingView behavior={Platform.OS === 'ios' ? 'padding' : undefined} style={{ flex: 1, backgroundColor: '#fff' }}>
      <ScrollView contentContainerStyle={styles.scroll} keyboardShouldPersistTaps="handled">
        <View style={styles.header}>
          <TouchableOpacity onPress={() => navigation.goBack()} style={styles.backBtn}>
            <Text style={styles.backText}>←</Text>
          </TouchableOpacity>
          <Text style={styles.title}>회원가입</Text>
        </View>

        {[
          { key: 'name',                  label: '이름',          placeholder: '홍길동',            type: 'default' },
          { key: 'username',              label: '아이디',         placeholder: 'hong123',          type: 'default' },
          { key: 'email',                 label: '이메일',         placeholder: 'email@example.com', type: 'email-address' },
          { key: 'password',              label: '비밀번호',       placeholder: '8자 이상',           secure: true },
          { key: 'password_confirmation', label: '비밀번호 확인',  placeholder: '비밀번호 재입력',     secure: true },
        ].map(f => (
          <View key={f.key}>
            <Text style={styles.label}>{f.label}</Text>
            <TextInput
              style={styles.input}
              placeholder={f.placeholder}
              placeholderTextColor={COLORS.gray[400]}
              value={form[f.key]}
              onChangeText={v => set(f.key, v)}
              keyboardType={f.type || 'default'}
              autoCapitalize="none"
              secureTextEntry={!!f.secure}
            />
          </View>
        ))}

        <TouchableOpacity
          style={[styles.btn, loading && { opacity: 0.6 }]}
          onPress={handleRegister}
          disabled={loading}
        >
          {loading ? <ActivityIndicator color="#fff" /> : <Text style={styles.btnText}>가입하기</Text>}
        </TouchableOpacity>

        <TouchableOpacity onPress={() => navigation.goBack()} style={styles.link}>
          <Text style={styles.linkText}>이미 계정이 있으신가요? <Text style={styles.linkBold}>로그인</Text></Text>
        </TouchableOpacity>
      </ScrollView>
    </KeyboardAvoidingView>
  )
}

const styles = StyleSheet.create({
  scroll:   { flexGrow: 1, padding: 24 },
  header:   { flexDirection: 'row', alignItems: 'center', marginBottom: 24, paddingTop: 8 },
  backBtn:  { marginRight: 12 },
  backText: { fontSize: 24, color: COLORS.primary },
  title:    { fontSize: 22, fontWeight: '900', color: COLORS.gray[800] },
  label:    { fontSize: 13, fontWeight: '600', color: COLORS.gray[600], marginBottom: 6, marginTop: 14 },
  input:    { backgroundColor: COLORS.gray[50], borderWidth: 1, borderColor: COLORS.gray[200], borderRadius: 12, paddingHorizontal: 16, paddingVertical: 12, fontSize: 15, color: COLORS.gray[800] },
  btn:      { backgroundColor: COLORS.primary, borderRadius: 12, paddingVertical: 14, alignItems: 'center', marginTop: 28 },
  btnText:  { color: '#fff', fontWeight: '800', fontSize: 16 },
  link:     { alignItems: 'center', marginTop: 16 },
  linkText: { color: COLORS.gray[500], fontSize: 14 },
  linkBold: { color: COLORS.primary, fontWeight: '700' },
})
