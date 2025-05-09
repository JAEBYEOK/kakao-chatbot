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

@application.route("/schedule", methods=["POST"])
def schedule_meeting():
    request_data = request.get_json()
    user_id = request_data['userRequest']['user']['id']
    date_str = request_data['action']['params']['date']
    time_param = request_data['action']['params']['time']

    print(f"date_str: {date_str}, time_param: {time_param}, type: {type(time_param)}")

    def parse_time_range(time_param, date_str):
        if isinstance(time_param, dict):
            start_time = time_param.get('from') or time_param.get('start')
            end_time = time_param.get('to') or time_param.get('end')
            try:
                start_time_fmt = parser.parse(start_time).strftime("%H:%M")
                end_time_fmt = parser.parse(end_time).strftime("%H:%M")
                return start_time_fmt, end_time_fmt
            except:
                return None, None
        match = re.match(r'(\d{1,2})시부터\s*(\d{1,2})시', time_param)
        if match:
            start_hour = int(match.group(1))
            end_hour = int(match.group(2))
            start_time = f"{start_hour:02d}:00"
            end_time = f"{end_hour:02d}:00"
            return start_time, end_time
        match = re.match(r'(\d{1,2}:\d{2})\s*~\s*(\d{1,2}:\d{2})', time_param)
        if match:
            return match.group(1), match.group(2)
        try:
            parsed = parser.parse(time_param)
            return parsed.strftime("%H:%M"), (parsed + timedelta(hours=1)).strftime("%H:%M")
        except:
            return None, None

    try:
        start_time, end_time = parse_time_range(time_param, date_str)
        if not start_time or not end_time:
            raise ValueError(f"시간 형식을 인식할 수 없습니다: {time_param}")
        service = get_google_calendar_service()
        calendar_id = os.getenv('GOOGLE_CALENDAR_ID')
        if not calendar_id:
            raise ValueError("환경변수 GOOGLE_CALENDAR_ID가 설정되어 있지 않습니다.")
        event = {
            'summary': '상담 일정',
            'description': f'카카오톡 챗봇을 통한 상담 예약',
            'start': {
                'dateTime': f"{date_str}T{start_time}:00",
                'timeZone': 'Asia/Seoul',
            },
            'end': {
                'dateTime': f"{date_str}T{end_time}:00",
                'timeZone': 'Asia/Seoul',
            },
        }
        event = service.events().insert(
            calendarId=calendar_id,
            body=event,
            sendUpdates='all'
        ).execute()
        response = {
            "version": "2.0",
            "template": {
                "outputs": [{
                    "simpleText": {
                        "text": f"상담 일정이 성공적으로 등록되었습니다!\n날짜: {date_str}\n시간: {start_time} ~ {end_time}"
                    }
                }]
            }
        }
    except Exception as e:
        error_message = f"일정 등록 중 오류가 발생했습니다: {str(e)}\n캘린더ID: {os.getenv('GOOGLE_CALENDAR_ID')}"
        print(error_message)  # 로깅을 위해 에러 메시지 출력
        response = {
            "version": "2.0",
            "template": {
                "outputs": [{
                    "simpleText": {
                        "text": error_message
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