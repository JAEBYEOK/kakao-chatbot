import os
import time
import json
from flask import Flask, jsonify, request
import openai
from datetime import datetime
from google.oauth2 import service_account
from googleapiclient.discovery import build

application = Flask(__name__)

SCOPES = ['https://www.googleapis.com/auth/calendar']
CREDENTIALS_FILE = os.getenv('GOOGLE_CREDENTIALS_FILE', 'credentials.json')

# Google Calendar API 서비스 계정 인증

def get_google_calendar_service():
    credentials = service_account.Credentials.from_service_account_file(
        CREDENTIALS_FILE, 
        scopes=SCOPES
    )
    return build('calendar', 'v3', credentials=credentials)

def build_gpt_prompt(user_input, today_str):
    return f"""
아래 문장에서 날짜와 시작/종료 시간을 ISO 8601 포맷(YYYY-MM-DDTHH:MM:SS)으로 추출해서 JSON으로 반환해줘.
오늘 날짜는 {today_str}야.
만약 일정 제목(요약)이 있으면 summary 필드도 포함해줘.

예시 입력: "내일 오후 3시부터 4시 회의"
예시 출력: {{"start_datetime": "2025-05-11T15:00:00", "end_datetime": "2025-05-11T16:00:00", "summary": "회의"}}

입력: "{user_input}"
"""

@application.route("/schedule", methods=["POST"])
def schedule_meeting():
    request_data = request.get_json()
    user_input = request_data['action']['params'].get('question')
    if not user_input:
        return jsonify({"version": "2.0", "template": {"outputs": [{"simpleText": {"text": "일정 내용을 입력해 주세요."}}]}})

    today_str = datetime.now().strftime("%Y-%m-%d")
    prompt = build_gpt_prompt(user_input, today_str)

    # GPT 호출
    openai.api_key = os.getenv('OPENAI_API_KEY')
    try:
        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            timeout=25
        )
        gpt_response = completion.choices[0].message.content
    except Exception as e:
        return jsonify({"version": "2.0", "template": {"outputs": [{"simpleText": {"text": f"GPT 호출 오류: {str(e)}"}}]}})

    # GPT 응답에서 JSON 파싱
    try:
        parsed = json.loads(gpt_response)
        start_datetime = parsed["start_datetime"]
        end_datetime = parsed["end_datetime"]
        summary = parsed.get("summary", "상담 일정")
    except Exception as e:
        return jsonify({"version": "2.0", "template": {"outputs": [{"simpleText": {"text": f"GPT 응답 파싱 오류: {str(e)}\n{gpt_response}"}}]}})

    # Google Calendar API에 등록
    try:
        service = get_google_calendar_service()
        calendar_id = os.getenv('GOOGLE_CALENDAR_ID')
        event = {
            'summary': summary,
            'description': f'카카오톡 챗봇을 통한 상담 예약',
            'start': {
                'dateTime': start_datetime,
                'timeZone': 'Asia/Seoul',
            },
            'end': {
                'dateTime': end_datetime,
                'timeZone': 'Asia/Seoul',
            },
        }
        print("event 데이터:", json.dumps(event, ensure_ascii=False))
        service.events().insert(
            calendarId=calendar_id,
            body=event,
            sendUpdates='all'
        ).execute()
        response = {
            "version": "2.0",
            "template": {
                "outputs": [{
                    "simpleText": {
                        "text": f"상담 일정이 성공적으로 등록되었습니다!\n{summary}\n{start_datetime} ~ {end_datetime}"
                    }
                }]
            }
        }
    except Exception as e:
        response = {
            "version": "2.0",
            "template": {
                "outputs": [{
                    "simpleText": {
                        "text": f"일정 등록 중 오류가 발생했습니다: {str(e)}"
                    }
                }]
            }
        }
    return jsonify(response)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    application.run(host='0.0.0.0', port=port, debug=False) 