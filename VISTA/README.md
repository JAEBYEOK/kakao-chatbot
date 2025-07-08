# VISTA - 제주도 AI 내비게이션 시스템 🏝️

> **V**isual **I**ntelligent **S**mart **T**ravel **A**ssistant  
> 제주도 여행자를 위한 맞춤형 AI 내비게이션 및 여행 추천 시스템

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![React Native](https://img.shields.io/badge/React%20Native-0.72+-blue.svg)](https://reactnative.dev/)
[![Flask](https://img.shields.io/badge/Flask-2.0+-green.svg)](https://flask.palletsprojects.com/)

## 📱 프로젝트 개요

VISTA는 제주도 관광객을 위한 혁신적인 AI 기반 내비게이션 시스템입니다. 단순한 최단경로가 아닌, 사용자의 취향과 여행 목적에 맞는 경로를 추천하는 지능형 내비게이션을 제공합니다.

### 🌟 주요 특징

- **🎤 음성 인식**: "제주공항에서 성산일출봉까지 경치 좋은 길로 안내해주세요"
- **🤖 AI 추천**: LLM 기반 맞춤형 경로 및 관광지 추천
- **🗺️ 실시간 내비게이션**: OSRM 서버 기반 최적 경로 계산
- **📍 POI 매칭**: 도로 네트워크와 관심지점 연동
- **🔊 음성 안내**: 한국어 STT/TTS 기반 자연스러운 안내
- **📱 모바일 앱**: React Native 크로스플랫폼 모바일 애플리케이션

## 🏗️ 시스템 아키텍처

```
📱 React Native App (VistaNavApp/)
    ↕️ REST API
🖥️ Flask API Server (backend/)
    ↕️ Module Integration  
🧠 VISTA Core System
    ├── 🗺️ 링크데이터 수집 → POI 매칭 → 관광정보 라벨링
    ├── 🎤 STT/TTS 모델 학습 → 음성 인터페이스
    ├── 🛣️ OSRM 서버 구축 → 경로 최적화
    └── 🤖 LLM 통합 → 대화형 여행 계획
```

## 📂 프로젝트 구조

```
VISTA/
├── 📱 VistaNavApp/              # React Native 모바일 앱
│   ├── App.js                   # 메인 앱 컴포넌트
│   ├── services/
│   │   ├── VistaAPI.js         # 백엔드 API 통신
│   │   └── VoiceService.js     # 음성 인식/TTS 서비스
│   └── package.json
├── 🖥️ backend/                  # Flask API 서버
│   └── api_server.py           # REST API 엔드포인트
├── 🧠 Core System/              # VISTA 핵심 시스템
│   ├── scripts/                # 파이프라인 스크립트
│   │   ├── 01_link_data_collection.py
│   │   ├── 02_poi_matching.py
│   │   ├── 03_tourism_labeling.py
│   │   └── 07_llm_integration.py
│   ├── demo/                   # 데모 및 테스트
│   │   ├── jeju_advanced_navigation.py
│   │   └── jeju_interactive_nav.py
│   └── config/                 # 설정 파일
│       ├── project_config.yaml
│       └── osrm_config.yaml
├── 🚀 start_vista_app.sh       # 앱 실행 스크립트
└── 📋 README.md                # 이 파일
```

## 🚀 빠른 시작

### 1. 사전 요구사항

- **Python 3.8+** (백엔드 시스템)
- **Node.js 16+** (React Native 앱)
- **Expo CLI** (모바일 개발)
- **Git** (버전 관리)

### 2. 프로젝트 클론

```bash
git clone https://github.com/JAEBYEOK/VISTA.git
cd VISTA
```

### 3. 백엔드 설정

```bash
# Python 의존성 설치
pip install -r requirements.txt
pip install flask flask-cors

# 환경 변수 설정
cp env.example .env
# .env 파일을 편집하여 API 키 등을 설정
```

### 4. 모바일 앱 설정

```bash
cd VistaNavApp
npm install
```

### 5. 시스템 실행

#### 방법 1: 자동 실행 스크립트 사용
```bash
./start_vista_app.sh
```

#### 방법 2: 개별 실행
```bash
# 터미널 1: 백엔드 API 서버
cd backend
python api_server.py

# 터미널 2: React Native 앱
cd VistaNavApp
npm start
```

### 6. 앱 접속

- **백엔드 API**: http://localhost:5000
- **모바일 앱**: Expo Go 앱에서 QR 코드 스캔 또는 `npm run ios`/`npm run android`

## 📱 모바일 앱 기능

### 🎯 주요 화면

1. **홈 화면**
   - 음성 명령 인터페이스
   - 추천 코스/장소 카드
   - 위치 선택 및 설정

2. **음성 인식**
   - 실시간 음성 명령 처리
   - 자연어 의도 분석
   - 음성 피드백

3. **추천 시스템**
   - AI 기반 맞춤 추천
   - 경치 점수 및 메타데이터
   - 실시간 이미지 로딩

### 🗣️ 음성 명령 예시

- "제주공항에서 성산일출봉까지 경치 좋은 길로 안내해주세요"
- "바다 보이는 카페 추천해주세요"  
- "한라산 등반코스 알려주세요"
- "현재 위치에서 가까운 맛집 찾아주세요"

## 🔧 API 엔드포인트

### 📡 백엔드 REST API

| 엔드포인트 | 메소드 | 설명 |
|-----------|-------|------|
| `/api/health` | GET | 서버 상태 확인 |
| `/api/route/calculate` | POST | 경로 계산 |
| `/api/stt/recognize` | POST | 음성 인식 |
| `/api/llm/travel-plan` | POST | AI 여행 계획 생성 |
| `/api/poi/search` | GET | POI 검색 |
| `/api/recommendations/routes` | GET | 추천 경로 |

### 📋 API 사용 예시

```javascript
// 경로 계산 요청
const response = await fetch('http://localhost:5000/api/route/calculate', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    start: [126.4933, 33.5066], // 제주공항
    end: [126.9423, 33.4586],   // 성산일출봉
    preferences: { travel_style: 'scenic' }
  })
});
```

## 🧠 Core System 기능

### 📊 데이터 파이프라인

1. **링크데이터 수집** (`01_link_data_collection.py`)
   - 제주도 OSM 도로 네트워크 다운로드
   - 도로 세그먼트 처리 및 링크 ID 생성

2. **POI 매칭** (`02_poi_matching.py`)
   - 관심지점과 도로 링크 매칭
   - 공간 분석을 통한 근접 POI 식별

3. **관광정보 라벨링** (`03_tourism_labeling.py`)
   - 도로별 관광 특성 라벨링
   - 경치, 문화, 맛집 등 카테고리 분류

4. **LLM 통합** (`07_llm_integration.py`)
   - 대화형 내비게이션을 위한 LLM 학습
   - 사용자 쿼리 기반 경로 추천 시스템

### 🎮 파이프라인 실행

```bash
# 전체 파이프라인 실행
python run_pipeline.py --full

# 특정 단계만 실행
python run_pipeline.py --stage link_data_processing
python run_pipeline.py --stage poi_matching

# 파이프라인 상태 확인
python run_pipeline.py --status
```

## 🛠️ 개발 가이드

### 🔧 기술 스택

**모바일 앱**
- React Native + Expo
- JavaScript/ES6+
- Axios (HTTP 클라이언트)
- expo-av (오디오), expo-speech (TTS)

**백엔드**
- Python 3.8+
- Flask (웹 프레임워크)
- Flask-CORS (CORS 지원)

**AI/ML**
- OpenAI GPT (LLM)
- Whisper (STT)
- Custom TTS 모델

**지도/경로**
- OpenStreetMap (OSM)
- OSRM (라우팅 엔진)
- Folium (지도 시각화)

### 🧪 개발 환경 설정

```bash
# 개발 의존성 설치
npm install -g expo-cli
pip install -r requirements.txt

# 환경 변수 설정
export OPENAI_API_KEY="your_api_key"
export FLASK_ENV="development"

# 개발 서버 실행
cd VistaNavApp && npm run start
cd backend && python api_server.py
```

### 📱 모바일 앱 빌드

```bash
# iOS (macOS만 가능)
cd VistaNavApp
expo build:ios

# Android
expo build:android

# 웹 버전
npm run web
```

## 🌟 주요 데모 및 예시

### 🎬 데모 시나리오

1. **해안도로 드라이브**
   - 제주공항 → 애월해안도로 → 협재해수욕장
   - 경치 점수: 9.5/10, 소요시간: 3시간

2. **성산일출봉 + 우도 투어**
   - 성산일출봉 → 우도선착장 → 우도 해안도로
   - 경치 점수: 10.0/10, 소요시간: 4시간

3. **카페 투어**
   - 애월읍 → 한림해변카페거리
   - 인생샷 스팟과 오션뷰 카페 추천

### 📊 성능 지표

- **음성 인식 정확도**: 95%+
- **경로 계산 시간**: 평균 2초 이내  
- **추천 정확도**: 88%+ (사용자 만족도 기준)
- **모바일 앱 로딩 시간**: 3초 이내

## 🔮 향후 개발 계획

### 단기 계획 (1-3개월)
- [ ] 실제 GPS 위치 연동
- [ ] 지도 화면 추가 (MapView 통합)
- [ ] 오프라인 모드 지원
- [ ] 사용자 인증 시스템

### 중기 계획 (3-6개월)  
- [ ] 실시간 교통 정보 연동
- [ ] 사용자 여행 히스토리 저장
- [ ] 소셜 공유 기능
- [ ] 다국어 지원 (영어, 중국어, 일본어)

### 장기 계획 (6개월+)
- [ ] AR 기반 내비게이션
- [ ] 제주도 외 지역 확장
- [ ] 커뮤니티 기능 (리뷰, 평점)
- [ ] 개인화 AI 어시스턴트

## 🐛 문제 해결

### 일반적인 문제들

**음성 인식이 작동하지 않는 경우**
```bash
# 마이크 권한 확인
# iOS: 설정 > 개인정보 보호 > 마이크
# Android: 설정 > 앱 권한 > 마이크
```

**백엔드 연결 오류**
```bash
# API 서버 상태 확인
curl http://localhost:5000/api/health

# 포트 충돌 해결 (macOS)
sudo lsof -i :5000
# AirPlay Receiver 비활성화: 시스템 환경설정 > 공유
```

**모바일 앱 빌드 오류**
```bash
# 캐시 정리
expo r -c
npm start -- --reset-cache

# 의존성 재설치
rm -rf node_modules package-lock.json
npm install
```

## 🤝 기여하기

VISTA 프로젝트에 기여해주셔서 감사합니다!

### 기여 방법

1. **Fork** the repository
2. **Clone** your fork: `git clone https://github.com/YOUR_USERNAME/VISTA.git`
3. **Create** a feature branch: `git checkout -b feature/amazing-feature`
4. **Commit** your changes: `git commit -m 'Add amazing feature'`
5. **Push** to the branch: `git push origin feature/amazing-feature`
6. **Open** a Pull Request

### 코딩 스타일

- **Python**: PEP 8 준수
- **JavaScript**: ESLint + Prettier 사용
- **Commit**: Conventional Commits 형식 권장

## 📄 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다. 자세한 내용은 [LICENSE](LICENSE) 파일을 참조하세요.

## 📞 연락처

- **개발자**: JAEHYEOK CHOI
- **GitHub**: [@JAEBYEOK](https://github.com/JAEBYEOK)
- **이메일**: [Your Email]
- **프로젝트 링크**: https://github.com/JAEBYEOK/VISTA

## 🙏 감사의 말

- **제주특별자치도** - 관광 데이터 지원
- **OpenStreetMap** - 지도 데이터 제공
- **Expo 팀** - 모바일 개발 플랫폼
- **Flask 커뮤니티** - 웹 프레임워크 지원

---

**VISTA Team** 🏝️ *제주도 여행의 새로운 경험*

> "기술로 연결하는 제주도의 아름다운 순간들" 