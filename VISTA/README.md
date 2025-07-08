# 제주도 여행 전용 내비게이션 시스템

사용자 맞춤형 제주도 여행 내비게이션 시스템 개발 프로젝트입니다.

## 프로젝트 개요

이 프로젝트는 제주도 관광객을 위한 맞춤형 내비게이션 시스템을 구축합니다. 단순한 최단경로가 아닌, 사용자의 취향과 여행 목적에 맞는 경로를 추천하는 AI 기반 내비게이션입니다.

## 시스템 아키텍처

```
제주도 링크데이터 → POI 매칭 → 관광정보 라벨링 → 음성데이터 수집 
    ↓
STT/TTS 모델 학습 → OSRM 서버 구축 → LLM 통합 → 모바일 앱
```

## 주요 기능

- 🗺️ **맞춤형 경로 추천**: 경치, 문화, 맛집 등 사용자 취향에 따른 경로 제공
- 🎤 **음성 안내**: 한국어 STT/TTS 기반 음성 내비게이션
- 🤖 **AI 대화형 안내**: LLM 기반 자연스러운 경로 설명
- 📱 **모바일 앱**: 실시간 내비게이션 및 관광 정보 제공

## 설치 및 설정

### 1. 환경 설정

```bash
# Python 의존성 설치
pip install -r requirements.txt

# 환경 변수 설정
cp env.example .env
# .env 파일을 편집하여 API 키 등을 설정하세요
```

### 2. 디렉토리 구조

```
VISTA/
├── workflow.yaml              # 워크플로우 정의
├── requirements.txt           # Python 의존성
├── run_pipeline.py           # 파이프라인 실행기
├── config/
│   ├── project_config.yaml   # 프로젝트 설정
│   └── osrm_config.yaml     # OSRM 서버 설정
├── scripts/
│   ├── 01_link_data_collection.py
│   ├── 02_poi_matching.py
│   ├── ...
│   └── 08_mobile_deployment.py
├── data/
│   ├── raw/                  # 원본 데이터
│   ├── processed/            # 전처리된 데이터
│   ├── labeled/              # 라벨링된 데이터
│   └── voice/                # 음성 데이터
├── models/                   # 학습된 모델
├── osrm_data/               # OSRM 서버 데이터
└── logs/                    # 로그 파일
```

## 사용법

### 파이프라인 상태 확인
```bash
python run_pipeline.py --status
```

### 전체 파이프라인 실행
```bash
python run_pipeline.py --full
```

### 특정 단계만 실행
```bash
python run_pipeline.py --stage link_data_processing
python run_pipeline.py --stage llm_integration
```

### 개별 스크립트 실행
```bash
python scripts/01_link_data_collection.py
python scripts/07_llm_integration.py
```

## 파이프라인 단계

### 1. 링크데이터 수집 (`link_data_processing`)
- 제주도 OSM 도로 네트워크 데이터 다운로드
- 도로 세그먼트 처리 및 링크 ID 생성
- POI 데이터 로드

### 2. POI 매칭 (`poi_matching`)
- 관심지점과 도로 링크 매칭
- 공간 분석을 통한 근접 POI 식별

### 3. 관광정보 라벨링 (`tourism_labeling`)
- 도로별 관광 특성 라벨링
- 경치, 문화, 맛집 등 카테고리 분류

### 4. 음성데이터 수집 (`voice_data_collection`)
- 내비게이션용 음성 데이터 수집
- 음성 전사 데이터 준비

### 5. STT/TTS 모델 학습 (`stt_tts_training`)
- 한국어 음성 인식 모델 학습
- 음성 합성 모델 학습

### 6. OSRM 서버 구축 (`osrm_server_setup`)
- 제주도 특화 라우팅 서버 구축
- 관광 가중치 적용된 경로 계산

### 7. LLM 통합 (`llm_integration`)
- 대화형 내비게이션을 위한 LLM 학습
- 사용자 쿼리 기반 경로 추천 시스템

### 8. 모바일 앱 배포 (`mobile_app_deployment`)
- 내비게이션 앱 빌드 및 배포
- API 엔드포인트 설정

## 설정 파일

### project_config.yaml
프로젝트 전체 설정을 관리합니다.
- 데이터 경로
- API 설정
- 모델 파라미터
- 제주도 지역 설정

### osrm_config.yaml
OSRM 서버 설정을 관리합니다.
- 라우팅 프로파일
- 관광 가중치
- 서버 설정

## 개발 가이드

### 새로운 스크립트 추가
1. `scripts/` 디렉토리에 스크립트 생성
2. `workflow.yaml`에 새 스테이지 정의
3. 의존성 및 입출력 파일 명시

### 설정 수정
- 프로젝트 설정: `config/project_config.yaml`
- 환경 변수: `.env` 파일

## 문제 해결

### 일반적인 문제들

1. **OSM 데이터 다운로드 실패**
   - 네트워크 연결 확인
   - 제주도 영역 좌표 확인

2. **API 키 오류**
   - `.env` 파일의 API 키 확인
   - API 할당량 및 권한 확인

3. **메모리 부족**
   - `config/project_config.yaml`에서 배치 크기 조정
   - GPU 메모리 설정 확인

### 로그 확인
```bash
tail -f logs/navigation_system.log
tail -f logs/pipeline_runner.log
```

## 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다.

## 기여

프로젝트 개선을 위한 기여를 환영합니다. 
이슈 리포트나 풀 리퀘스트를 통해 참여해주세요. 