# Taskmaster 명령어 사용법

제주도 내비게이션 프로젝트의 Taskmaster 태스크 관리 가이드입니다.

## 기본 설정 확인

```bash
# 현재 태스크 목록 조회
taskmaster list

# 특정 태스크 정보 확인
taskmaster info link_data_processing

# 태스크 상태 확인
taskmaster status
```

## 태스크 실행

### 개별 태스크 실행
```bash
# 링크데이터 수집
taskmaster run link_data_processing

# POI 매칭
taskmaster run poi_matching

# 관광정보 라벨링
taskmaster run tourism_labeling

# LLM 통합
taskmaster run llm_integration
```

### 태스크 그룹 실행
```bash
# 데이터 파이프라인 전체 실행
taskmaster run-group data_pipeline

# ML 파이프라인 실행
taskmaster run-group ml_pipeline

# 배포 파이프라인 실행
taskmaster run-group deployment_pipeline
```

### 전체 파이프라인 실행
```bash
# 의존성 순서에 따라 전체 실행
taskmaster run-all

# 병렬 실행 (가능한 태스크들)
taskmaster run-all --parallel
```

## 태스크 모니터링

```bash
# 실행 중인 태스크 확인
taskmaster ps

# 태스크 로그 확인
taskmaster logs link_data_processing

# 실시간 로그 모니터링
taskmaster logs -f llm_integration
```

## 태스크 제어

```bash
# 태스크 중지
taskmaster stop poi_matching

# 태스크 재시작
taskmaster restart tourism_labeling

# 실패한 태스크 재시도
taskmaster retry stt_tts_training
```

## 환경 및 설정

```bash
# 환경 변수 확인
taskmaster env

# 설정 파일 유효성 검사
taskmaster validate

# 워크스페이스 정리
taskmaster clean
```

## 유용한 옵션들

### 태그 기반 실행
```bash
# 데이터 관련 태스크만 실행
taskmaster run --tags data

# ML 관련 태스크만 실행
taskmaster run --tags ml

# GPU 필요 태스크만 실행
taskmaster run --requires-gpu
```

### 조건부 실행
```bash
# 실패한 태스크만 재실행
taskmaster run --failed-only

# 변경된 입력 파일이 있는 태스크만 실행
taskmaster run --changed-only

# 특정 시간 이후 실행된 적 없는 태스크만
taskmaster run --older-than 1d
```

## 문제 해결

### 일반적인 문제들

1. **태스크를 찾을 수 없음**
   ```bash
   taskmaster validate
   ```

2. **의존성 오류**
   ```bash
   taskmaster check-deps link_data_processing
   ```

3. **로그 확인**
   ```bash
   taskmaster logs --level ERROR
   ```

### 디버깅 모드
```bash
# 디버그 모드로 태스크 실행
taskmaster run link_data_processing --debug

# 단계별 실행 (각 단계에서 정지)
taskmaster run llm_integration --step-by-step
```

## 파이프라인 사용 예시

### 개발 단계별 실행
```bash
# 1. 데이터 수집 및 전처리
taskmaster run-group data_pipeline

# 2. 모델 학습 (GPU 필요)
taskmaster run-group ml_pipeline

# 3. 배포 준비
taskmaster run-group deployment_pipeline
```

### 빠른 테스트
```bash
# 라벨링까지만 실행
taskmaster run link_data_processing poi_matching tourism_labeling

# LLM 통합만 재실행 (이전 결과 활용)
taskmaster run llm_integration --skip-deps
```

### 프로덕션 배포
```bash
# 전체 파이프라인 실행 (자동 재시도 포함)
taskmaster run-all --production --auto-retry
```

## 사용자 정의 명령어

프로젝트별 편의 명령어들:

```bash
# 제주도 데이터 업데이트
./scripts/update_jeju_data.sh

# 모델 성능 체크
taskmaster run model_validation

# 앱 빌드 및 테스트
taskmaster run mobile_build_test
```

이 명령어들을 활용하여 제주도 내비게이션 시스템을 효율적으로 구축하세요! 