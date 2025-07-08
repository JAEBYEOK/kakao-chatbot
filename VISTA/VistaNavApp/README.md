# VISTA - 제주도 AI 내비게이션 앱

제주도 여행자를 위한 맞춤형 AI 내비게이션 React Native 앱입니다.

## 📱 주요 기능

- **음성 인식**: "제주공항에서 성산일출봉까지 경치 좋은 길로 안내해주세요"
- **AI 추천**: 사용자 취향에 맞는 경로와 관광지 추천
- **실시간 내비게이션**: OSRM 기반 최적 경로 계산
- **POI 검색**: 카페, 식당, 관광지 검색 및 추천
- **음성 안내**: TTS 기반 친근한 음성 내비게이션

## 🚀 설치 및 실행

### 1. 사전 요구사항

- Node.js (v16 이상)
- npm 또는 yarn
- Expo CLI
- iOS 시뮬레이터 또는 Android 에뮬레이터

### 2. 의존성 설치

```bash
cd VistaNavApp
npm install
```

### 3. 백엔드 API 서버 실행

터미널 새 창에서:

```bash
cd ../backend
python api_server.py
```

서버가 http://localhost:5000 에서 실행됩니다.

### 4. React Native 앱 실행

```bash
# iOS (macOS만 가능)
npm run ios

# Android
npm run android

# 웹 (개발용)
npm run web
```

## 📂 프로젝트 구조

```
VistaNavApp/
├── App.js                 # 메인 앱 컴포넌트
├── services/
│   ├── VistaAPI.js        # 백엔드 API 통신
│   └── VoiceService.js    # 음성 인식/TTS 서비스
├── package.json
└── README.md
```

## 🎯 사용 방법

### 1. 음성 명령 사용하기

1. 메인 화면의 "여행 플랜 말하기" 버튼 터치
2. 마이크 아이콘이 활성화되면 음성 명령
3. 예시 명령어:
   - "제주공항에서 성산일출봉까지 경치 좋은 길로 안내해주세요"
   - "카페 추천해주세요"
   - "바다 보이는 식당 찾아주세요"

### 2. 추천 경로 확인

- 홈 화면에서 "추천 코스/장소" 섹션 확인
- 각 카드를 터치하여 상세 정보 확인

### 3. 하단 네비게이션

- **홈**: 메인 화면
- **추천**: 맞춤 추천 목록
- **내 여정**: 저장된 여행 계획
- **프로필**: 사용자 설정

## 🔧 개발 정보

### API 엔드포인트

백엔드 서버는 다음 API를 제공합니다:

- `POST /api/route/calculate` - 경로 계산
- `POST /api/stt/recognize` - 음성 인식
- `POST /api/llm/travel-plan` - AI 여행 계획 생성
- `GET /api/poi/search` - POI 검색
- `GET /api/recommendations/routes` - 추천 경로

### 주요 패키지

- **React Native**: 크로스플랫폼 모바일 개발
- **Expo**: 개발 및 배포 플랫폼
- **@expo/vector-icons**: 아이콘
- **expo-av**: 오디오 녹음
- **expo-speech**: 텍스트 음성 변환
- **axios**: HTTP 클라이언트

## 🔮 향후 개발 계획

- [ ] 실제 GPS 위치 연동
- [ ] 지도 화면 추가
- [ ] 오프라인 모드 지원
- [ ] 사용자 로그인/회원가입
- [ ] 여행 히스토리 저장
- [ ] 실시간 교통 정보 연동
- [ ] 소셜 공유 기능

## 🐛 문제 해결

### 음성 인식이 작동하지 않는 경우

1. 마이크 권한이 허용되었는지 확인
2. 시뮬레이터에서는 음성 입력이 제한될 수 있음
3. 실제 디바이스에서 테스트 권장

### 백엔드 연결 오류

1. API 서버가 실행중인지 확인: `http://localhost:5000/api/health`
2. 방화벽 설정 확인
3. 네트워크 연결 상태 확인

### iOS 시뮬레이터 오류

```bash
# iOS 시뮬레이터 초기화
npx react-native run-ios --simulator="iPhone 15"
```

### Android 에뮬레이터 오류

```bash
# Android 에뮬레이터 시작
emulator -avd Pixel_6_API_34
npx react-native run-android
```

## 📞 지원

문제가 발생하거나 기능 제안이 있으시면 이슈를 등록해주세요.

---

**VISTA Team** 🏝️ *제주도 여행의 새로운 경험* 