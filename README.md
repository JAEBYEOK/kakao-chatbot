
---

## 환경 변수 설정

| 변수명                | 설명                                      |
|----------------------|-------------------------------------------|
| `OPENAI_API_KEY`     | OpenAI GPT API 키                         |
| `GOOGLE_CREDENTIALS` | Google 서비스 계정 키(JSON 전체 내용)      |
| `GOOGLE_CALENDAR_ID` | 일정을 등록할 Google 캘린더의 ID           |
| `PORT`               | (선택) 서버 포트, 기본값 10000             |

> Render에서는 `render.yaml`의 `envVars`로 관리

---

## 서비스 계정 키 준비

1. Google Cloud Console에서 서비스 계정 생성
2. Calendar API 활성화
3. 서비스 계정 키(JSON) 다운로드
4. Google Calendar에서 해당 서비스 계정 이메일을 “편집 권한”으로 공유
5. JSON 전체 내용을 `GOOGLE_CREDENTIALS` 환경 변수에 입력

---

## 주요 엔드포인트

- `/question`  
  - AI와의 자유 대화 (질문/답변)
- `/schedule`  
  - 자연어 일정 등록 (GPT가 날짜/시간/제목 추출 → 캘린더 등록)

---

## 오픈빌더 연동 예시

### 1. 질문 블록/스킬
- 파라미터명: `question`
- 엔티티: `sys.text`
- 액션 URL: `/question`

### 2. 일정 등록 블록/스킬
- 파라미터명: `question`
- 엔티티: `sys.text`
- 액션 URL: `/schedule`

---

## 실행 방법 (로컬)

```bash
pip install -r requirements.txt
python app.py
```

---

## 배포 (Render 등)

- GitHub 저장소와 Render 연동
- 환경 변수 등록 (`OPENAI_API_KEY`, `GOOGLE_CREDENTIALS`, `GOOGLE_CALENDAR_ID`, `PORT`)
- 자동 배포 (Render는 `gunicorn app:application --config gunicorn_config.py`로 실행)

---

## 예시 대화
