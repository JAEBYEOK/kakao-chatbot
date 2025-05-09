import os
import time
import json

GOOGLE_CREDENTIALS_ENV = os.getenv('GOOGLE_CREDENTIALS')
if GOOGLE_CREDENTIALS_ENV:
    with open('credentials.json', 'w') as f:
        f.write(GOOGLE_CREDENTIALS_ENV)

from flask import Flask, jsonify, request
import requests, sys, json
from google.oauth2 import service_account
from googleapiclient.discovery import build
import os.path
import pickle
import openai
from datetime import datetime, timedelta
from dateutil import parser
import re

application = Flask(__name__)
a = {}

# Google Calendar API 설정
SCOPES = ['https://www.googleapis.com/auth/calendar']
CREDENTIALS_FILE = os.getenv('GOOGLE_CREDENTIALS_FILE', 'credentials.json')

def get_google_calendar_service():
    try:
        credentials = service_account.Credentials.from_service_account_file(
            CREDENTIALS_FILE, 
            scopes=SCOPES
        )
        return build('calendar', 'v3', credentials=credentials)
    except Exception as e:
        print(f"Google Calendar 서비스 초기화 중 오류 발생: {str(e)}")
        raise e

@application.route("/")
def home():
    return jsonify({"status": "ok", "message": "서버가 정상적으로 실행 중입니다."})

@application.route("/webhook/", methods=["POST"])
def webhook():
    global a
    request_data = json.loads(request.get_data(), encoding='utf-8')
    a[request_data['user']] = request_data['result']['choices'][0]['message']['content']
    return jsonify({"status": "ok", "message": "웹훅이 성공적으로 처리되었습니다."})

@application.route("/question", methods=["POST"])
def get_question():
    global a
    request_data = request.get_json()
    user_id = request_data['userRequest']['user']['id']
    question = request_data['action']['params']['question']
    
    response = { "version": "2.0", "template": { "outputs": [{
        "simpleText": {"text": f"질문을 받았습니다. AI에게 물어보고 올께요!: {question}"}
    }]}}
    
    a[user_id] = '아직 AI가 처리중이에요'
    
    try:
        # OpenAI API 직접 호출
        openai.api_key = os.getenv('OPENAI_API_KEY')
        if not openai.api_key:
            raise ValueError("OpenAI API 키가 설정되지 않았습니다.")
        
        # 최대 3번까지 재시도
        max_retries = 3
        retry_count = 0
        last_error = None
        
        while retry_count < max_retries:
            try:
                completion = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": question}],
                    timeout=25  # 렌더의 30초 제한을 고려하여 25초로 설정
                )
                a[user_id] = completion.choices[0].message.content
                break
            except Exception as e:
                last_error = e
                retry_count += 1
                if retry_count == max_retries:
                    break
                time.sleep(2)  # 재시도 전 2초 대기
        
        if retry_count == max_retries:
            error_message = f"OpenAI API 호출 실패 (최대 재시도 횟수 초과): {str(last_error)}"
            a[user_id] = error_message
            print(error_message)  # 로깅을 위해 에러 메시지 출력
            
    except Exception as e:
        error_message = f"죄송합니다. 오류가 발생했습니다: {str(e)}"
        a[user_id] = error_message
        print(error_message)  # 로깅을 위해 에러 메시지 출력
    
    return jsonify(response)

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
    user_id = request_data['userRequest']['user']['id']
    # 자유 입력 파라미터(question)만 사용
    user_input = request_data['action']['params'].get('question')
    if not user_input:
        return jsonify({"version": "2.0", "template": {"outputs": [{"simpleText": {"text": "질문(일정 내용)을 입력해 주세요."}}]}})

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
    import json
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

@application.route("/ans", methods=["POST"])
def get_answer():
    request_data = request.get_json()
    response = { "version": "2.0", "template": { "outputs": [{
        "simpleText": {"text": f"답변: {a.get(request_data['userRequest']['user']['id'], '질문을 하신적이 없어보여요. 질문부터 해주세요')}"}
    }]}}
    return jsonify(response)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    application.run(host='0.0.0.0', port=port, debug=False) 