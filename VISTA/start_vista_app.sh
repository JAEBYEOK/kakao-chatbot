#!/bin/bash

# VISTA 앱 실행 스크립트

echo "🏝️ VISTA - 제주도 AI 내비게이션 앱 시작"
echo "======================================="

# 백엔드 서버 시작
echo "📡 백엔드 API 서버 시작 중..."
cd backend
python api_server.py &
BACKEND_PID=$!
cd ..

# 잠시 대기
sleep 3

# React Native 앱 시작
echo "📱 React Native 앱 시작 중..."
cd VistaNavApp
npm start &
APP_PID=$!
cd ..

echo ""
echo "✅ VISTA 앱이 실행되었습니다!"
echo ""
echo "📡 백엔드 서버: http://localhost:5000"
echo "📱 앱 개발 서버: http://localhost:8081"
echo ""
echo "앱을 중지하려면 Ctrl+C를 누르세요."
echo ""

# 사용자가 Ctrl+C를 누를 때까지 대기
trap "echo ''; echo '🛑 VISTA 앱을 종료합니다...'; kill $BACKEND_PID $APP_PID; exit" INT

# 백그라운드 프로세스가 실행 중인 동안 대기
wait 