from flask import Flask, jsonify, request
import requests, sys, json
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import os.path
import pickle
import openai
from datetime import datetime, timedelta
import os
from dateutil import parser
import re

application = Flask(__name__)
a = {}

# Google Calendar API 설정
SCOPES = ['https://www.googleapis.com/auth/calendar']
CREDENTIALS_FILE = os.getenv('GOOGLE_CREDENTIALS_FILE', 'credentials.json')
TOKEN_FILE = 'token.pickle'

def get_google_calendar_service():
    creds = None
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, 'rb') as token:
            creds = pickle.load(token)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(TOKEN_FILE, 'wb') as token:
            pickle.dump(creds, token)
    
    return build('calendar', 'v3', credentials=creds)

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
            
        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": question}]
        )
        a[user_id] = completion.choices[0].message.content
    except Exception as e:
        a[user_id] = f"죄송합니다. 오류가 발생했습니다: {str(e)}"
    
    return jsonify(response)

@application.route("/schedule", methods=["POST"])
def schedule_meeting():
    request_data = request.get_json()
    user_id = request_data['userRequest']['user']['id']
    date_str = request_data['action']['params']['date']
    time_str = request_data['action']['params']['time']

    def parse_time_range(time_str, date_str):
        # "3시부터 4시" 패턴
        match = re.match(r'(\d{1,2})시부터\s*(\d{1,2})시', time_str)
        if match:
            start_hour = int(match.group(1))
            end_hour = int(match.group(2))
            start_time = f"{start_hour:02d}:00"
            end_time = f"{end_hour:02d}:00"
            return start_time, end_time
        # "15:00~16:00" 패턴
        match = re.match(r'(\d{1,2}:\d{2})\s*~\s*(\d{1,2}:\d{2})', time_str)
        if match:
            return match.group(1), match.group(2)
        # 단일 시간만 들어온 경우
        try:
            parsed = parser.parse(time_str)
            return parsed.strftime("%H:%M"), (parsed + timedelta(hours=1)).strftime("%H:%M")
        except:
            return None, None

    try:
        # 날짜와 시간 파싱
        start_time, end_time = parse_time_range(time_str, date_str)
        if not start_time or not end_time:
            raise ValueError(f"시간 형식을 인식할 수 없습니다: {time_str}")
        # Google Calendar API 사용
        service = get_google_calendar_service()
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
        event = service.events().insert(calendarId='primary', body=event).execute()
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