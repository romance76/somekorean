import React, { useEffect } from 'react'
import { View, Text, ActivityIndicator } from 'react-native'
import { NavigationContainer } from '@react-navigation/native'
import { createNativeStackNavigator } from '@react-navigation/native-stack'
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs'
import { useAuthStore } from '../stores/authStore'
import { COLORS } from '../utils/helpers'

// Auth
import LoginScreen    from '../screens/auth/LoginScreen'
import RegisterScreen from '../screens/auth/RegisterScreen'

// Main tabs
import HomeScreen          from '../screens/home/HomeScreen'
import CommunityScreen     from '../screens/community/CommunityScreen'
import ChatRoomsScreen     from '../screens/chat/ChatRoomsScreen'
import ChatRoomScreen      from '../screens/chat/ChatRoomScreen'
import ShortsScreen        from '../screens/shorts/ShortsScreen'
import ProfileScreen       from '../screens/profile/ProfileScreen'
import NotificationsScreen from '../screens/notifications/NotificationsScreen'

const Stack = createNativeStackNavigator()
const Tab   = createBottomTabNavigator()

const TAB_ICONS = {
  Home:          { active: '🏠', inactive: '🏠' },
  Community:     { active: '📋', inactive: '📋' },
  ChatRooms:     { active: '💬', inactive: '💬' },
  Shorts:        { active: '▶️', inactive: '▶️' },
  Profile:       { active: '👤', inactive: '👤' },
}

function TabNavigator() {
  return (
    <Tab.Navigator
      screenOptions={({ route }) => ({
        headerShown: false,
        tabBarStyle: { backgroundColor: '#fff', borderTopColor: '#E5E7EB', height: 60, paddingBottom: 6 },
        tabBarActiveTintColor: COLORS.primary,
        tabBarInactiveTintColor: '#9CA3AF',
        tabBarLabelStyle: { fontSize: 11, fontWeight: '600' },
        tabBarIcon: ({ focused, size }) => (
          <Text style={{ fontSize: 22 }}>{focused ? TAB_ICONS[route.name]?.active : TAB_ICONS[route.name]?.inactive}</Text>
        ),
      })}
    >
      <Tab.Screen name="Home"      component={HomeStack}      options={{ title: '홈' }} />
      <Tab.Screen name="Community" component={CommunityStack} options={{ title: '커뮤니티' }} />
      <Tab.Screen name="ChatRooms" component={ChatStack}      options={{ title: '채팅' }} />
      <Tab.Screen name="Shorts"    component={ShortsScreen}   options={{ title: '숏츠', headerShown: false }} />
      <Tab.Screen name="Profile"   component={ProfileStack}   options={{ title: '내정보' }} />
    </Tab.Navigator>
  )
}

function CommunityStack() {
  return (
    <Stack.Navigator screenOptions={{ headerTintColor: COLORS.primary, headerBackTitle: '' }}>
      <Stack.Screen name="CommunityMain" component={CommunityScreen} options={{ headerShown: false }} />
    </Stack.Navigator>
  )
}

function HomeStack() {
  return (
    <Stack.Navigator screenOptions={{ headerTintColor: COLORS.primary, headerBackTitle: '' }}>
      <Stack.Screen name="HomeMain" component={HomeScreen} options={{ headerShown: false }} />
    </Stack.Navigator>
  )
}

function ChatStack() {
  return (
    <Stack.Navigator screenOptions={{ headerTintColor: COLORS.primary, headerBackTitle: '' }}>
      <Stack.Screen name="ChatRoomsList" component={ChatRoomsScreen} options={{ headerShown: false }} />
      <Stack.Screen name="ChatRoom"      component={ChatRoomScreen}
        options={({ route }) => ({ title: route.params?.room?.name ?? '채팅', headerStyle: { backgroundColor: '#fff' } })}
      />
    </Stack.Navigator>
  )
}

function ProfileStack() {
  return (
    <Stack.Navigator screenOptions={{ headerTintColor: COLORS.primary, headerBackTitle: '' }}>
      <Stack.Screen name="ProfileMain" component={ProfileScreen} options={{ headerShown: false }} />
    </Stack.Navigator>
  )
}

function AuthStack() {
  return (
    <Stack.Navigator screenOptions={{ headerShown: false }}>
      <Stack.Screen name="Login"    component={LoginScreen} />
      <Stack.Screen name="Register" component={RegisterScreen} />
    </Stack.Navigator>
  )
}

export default function AppNavigator() {
  const { init, loading } = useAuthStore()

  useEffect(() => { init() }, [])

  if (loading) {
    return (
      <View style={{ flex: 1, justifyContent: 'center', alignItems: 'center', backgroundColor: '#2563EB' }}>
        <Text style={{ fontSize: 48, marginBottom: 16 }}>🇰🇷</Text>
        <ActivityIndicator color="#fff" size="large" />
      </View>
    )
  }

  return (
    <NavigationContainer>
      {/* 앱은 항상 탭 네비게이션으로 시작, 로그인 필요 시 각 화면에서 처리 */}
      <TabNavigator />
    </NavigationContainer>
  )
}
