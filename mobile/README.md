# SomeKorean Mobile App

## 설치 및 실행

```bash
cd mobile
npm install
npx expo start
```

## 실기기 테스트
1. 핸드폰에 **Expo Go** 앱 설치 (iOS: App Store / Android: Play Store)
2. `npx expo start` 실행 후 QR 코드 스캔

## 빌드 (앱스토어 배포용)
```bash
npm install -g eas-cli
eas login
eas build --platform android   # APK/AAB
eas build --platform ios       # IPA (Mac 필요)
```

## 구조
```
src/
  screens/
    auth/        LoginScreen, RegisterScreen
    home/        HomeScreen (피드)
    community/   CommunityScreen (게시글/구인/마켓/업소)
    chat/        ChatRoomsScreen, ChatRoomScreen
    shorts/      ShortsScreen (세로 숏츠)
    profile/     ProfileScreen
    notifications/ NotificationsScreen
  stores/        authStore (Zustand)
  services/      api.js (axios → somekorean.com/api)
  navigation/    AppNavigator
  utils/         helpers (날짜/색상)
```

## API
모든 API는 `https://somekorean.com/api` 에 연결됩니다.
