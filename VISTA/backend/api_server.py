#!/usr/bin/env python3
"""
VISTA React Native 앱을 위한 API 서버
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import os
import sys
from datetime import datetime
import traceback

# VISTA 프로젝트 경로 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from demo.jeju_advanced_navigation import JejuNavigationSystem
    from demo.jeju_interactive_nav import InteractiveNavigator
except ImportError:
    print("VISTA 모듈을 찾을 수 없습니다. 모의 데이터를 사용합니다.")
    JejuNavigationSystem = None
    InteractiveNavigator = None

app = Flask(__name__)
CORS(app)  # React Native 앱에서 접근 허용

# VISTA 시스템 초기화
navigation_system = None
interactive_navigator = None

try:
    if JejuNavigationSystem:
        navigation_system = JejuNavigationSystem()
    if InteractiveNavigator:
        interactive_navigator = InteractiveNavigator()
except Exception as e:
    print(f"VISTA 시스템 초기화 실패: {e}")

@app.route('/api/health', methods=['GET'])
def health_check():
    """서버 상태 확인"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'vista_system_available': navigation_system is not None
    })

@app.route('/api/route/calculate', methods=['POST'])
def calculate_route():
    """경로 계산"""
    try:
        data = request.json
        start_point = data.get('start')
        end_point = data.get('end')
        preferences = data.get('preferences', {})
        
        print(f"경로 계산 요청: {start_point} -> {end_point}")
        
        if navigation_system:
            # 실제 VISTA 시스템 사용
            route = navigation_system.calculate_scenic_route(
                start=start_point,
                end=end_point,
                preferences=preferences
            )
        else:
            # 모의 응답
            route = {
                'distance': 25.4,
                'duration': 1800,  # 30분
                'geometry': {
                    'coordinates': [
                        [126.4933, 33.5066],  # 제주공항
                        [126.4500, 33.4800],
                        [126.4000, 33.4500],
                        [126.9423, 33.4586]   # 성산일출봉
                    ]
                },
                'jeju_features': {
                    'total_scenery_score': 8.5,
                    'route_pois': [
                        {
                            'name': '제주공항',
                            'category': '교통',
                            'distance_from_route': 0.0
                        },
                        {
                            'name': '성산일출봉',
                            'category': '관광명소',
                            'distance_from_route': 0.2
                        }
                    ],
                    'voice_navigation': [
                        '제주공항에서 출발합니다.',
                        '해안도로를 따라 동쪽으로 이동합니다.',
                        '성산일출봉에 도착했습니다.'
                    ],
                    'best_photo_spots': [
                        {
                            'coordinates': [126.7, 33.4],
                            'description': '해안 전망 포인트',
                            'scenery_score': 9.0
                        }
                    ]
                }
            }
        
        return jsonify({
            'success': True,
            'route': route,
            'calculation_time': datetime.now().isoformat()
        })
        
    except Exception as e:
        print(f"경로 계산 오류: {e}")
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/stt/recognize', methods=['POST'])
def recognize_speech():
    """음성 인식"""
    try:
        # 실제로는 오디오 파일을 받아서 STT 처리
        # 지금은 모의 응답
        
        mock_responses = [
            {
                'text': '제주공항에서 성산일출봉까지 경치 좋은 길로 안내해주세요',
                'intent': 'route_navigation',
                'entities': {
                    'start': '제주공항',
                    'destination': '성산일출봉',
                    'preference': 'scenic_route'
                },
                'confidence': 0.95
            },
            {
                'text': '카페 추천해주세요',
                'intent': 'poi_search',
                'entities': {
                    'category': 'cafe',
                    'location': 'current'
                },
                'confidence': 0.88
            }
        ]
        
        import random
        response = random.choice(mock_responses)
        
        return jsonify({
            'success': True,
            'result': response,
            'processing_time': datetime.now().isoformat()
        })
        
    except Exception as e:
        print(f"음성 인식 오류: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/llm/travel-plan', methods=['POST'])
def generate_travel_plan():
    """LLM 기반 여행 계획 생성"""
    try:
        data = request.json
        user_query = data.get('query')
        current_location = data.get('current_location')
        
        print(f"여행 계획 요청: {user_query}")
        
        if interactive_navigator:
            # 실제 VISTA LLM 사용
            plan = interactive_navigator.llm.analyze_and_plan({
                'text': user_query,
                'start': current_location,
                'end': None
            })
        else:
            # 모의 응답
            plan = {
                'travel_style': 'scenic_cultural',
                'recommended_duration': '4-6 시간',
                'waypoints': [
                    {
                        'name': '제주공항',
                        'type': 'start',
                        'estimated_time': 30
                    },
                    {
                        'name': '애월해안도로',
                        'type': 'scenic',
                        'estimated_time': 90
                    },
                    {
                        'name': '성산일출봉',
                        'type': 'destination',
                        'estimated_time': 120
                    }
                ],
                'description': 'AI가 분석한 맞춤형 제주도 여행 코스입니다.'
            }
        
        return jsonify({
            'success': True,
            'plan': plan,
            'generated_at': datetime.now().isoformat()
        })
        
    except Exception as e:
        print(f"여행 계획 생성 오류: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/poi/search', methods=['GET'])
def search_poi():
    """POI 검색"""
    try:
        query = request.args.get('q', '')
        category = request.args.get('category')
        lat = request.args.get('lat')
        lng = request.args.get('lng')
        
        print(f"POI 검색: {query}, 카테고리: {category}")
        
        # 모의 POI 데이터
        pois = [
            {
                'id': 1,
                'name': '오션뷰 에메 카페',
                'category': 'cafe',
                'rating': 4.8,
                'distance': 2.3,
                'coordinates': [126.3324, 33.4615],
                'description': '인생샷 남기는 감성 카페, 바다 전망 최고',
                'image_url': 'https://images.unsplash.com/photo-1554118811-1e0d58224f24?w=400'
            },
            {
                'id': 2,
                'name': '제주 흑돼지 맛집',
                'category': 'restaurant',
                'rating': 4.6,
                'distance': 1.8,
                'coordinates': [126.5312, 33.3617],
                'description': '현지인 추천 제주 특산품 요리',
                'image_url': 'https://images.unsplash.com/photo-1504674900247-0877df9cc836?w=400'
            },
            {
                'id': 3,
                'name': '성산일출봉',
                'category': 'tourist_attraction',
                'rating': 4.9,
                'distance': 15.2,
                'coordinates': [126.9423, 33.4586],
                'description': '유네스코 세계자연유산, 일출 명소',
                'image_url': 'https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=400'
            }
        ]
        
        # 카테고리별 필터링
        if category:
            pois = [poi for poi in pois if poi['category'] == category]
        
        # 검색어 필터링
        if query:
            pois = [poi for poi in pois if query.lower() in poi['name'].lower()]
        
        return jsonify({
            'success': True,
            'pois': pois,
            'total_count': len(pois)
        })
        
    except Exception as e:
        print(f"POI 검색 오류: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/recommendations/routes', methods=['GET'])
def get_recommended_routes():
    """추천 경로 가져오기"""
    try:
        # 이미지가 포함된 추천 경로 데이터
        routes = [
            {
                'id': 1,
                'title': '제주 해안도로 드라이브',
                'subtitle': '푸른 바다와 함께 달리는 환상적인 코스',
                'duration': 180,
                'distance': 45.2,
                'difficulty': 'easy',
                'scenery_score': 9.5,
                'image_url': 'https://images.unsplash.com/photo-1544273677-6aaf4f6a10e4?w=400&h=300&fit=crop&auto=format',
                'icon': 'car-outline',
                'waypoints': [
                    {'name': '제주공항', 'coordinates': [126.4933, 33.5066]},
                    {'name': '애월해안도로', 'coordinates': [126.3324, 33.4615]},
                    {'name': '한림공원', 'coordinates': [126.2411, 33.4154]},
                    {'name': '협재해수욕장', 'coordinates': [126.2396, 33.3940]}
                ]
            },
            {
                'id': 2,
                'title': '성산일출봉 + 우도 투어',
                'subtitle': '일출 명소와 아름다운 섬 여행',
                'duration': 240,
                'distance': 32.1,
                'difficulty': 'medium',
                'scenery_score': 10.0,
                'image_url': 'https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=400&h=300&fit=crop&auto=format',
                'icon': 'mountain-outline',
                'waypoints': [
                    {'name': '성산일출봉', 'coordinates': [126.9423, 33.4586]},
                    {'name': '우도선착장', 'coordinates': [126.9513, 33.5069]},
                    {'name': '우도 해안도로', 'coordinates': [126.9545, 33.5025]}
                ]
            },
            {
                'id': 3,
                'title': '오션뷰 에메 카페',
                'subtitle': '인생샷 남기는 감성 카페, 바다 전망 최고',
                'duration': 90,
                'distance': 12.5,
                'difficulty': 'easy',
                'scenery_score': 8.8,
                'image_url': 'https://images.unsplash.com/photo-1554118811-1e0d58224f24?w=400&h=300&fit=crop&auto=format',
                'icon': 'cafe-outline',
                'waypoints': [
                    {'name': '애월읍', 'coordinates': [126.3324, 33.4615]},
                    {'name': '한림해변카페거리', 'coordinates': [126.2400, 33.4100]}
                ]
            },
            {
                'id': 4,
                'title': '한라산 등반코스',
                'subtitle': '제주의 상징, 한라산 정상 정복하기',
                'duration': 480,
                'distance': 19.2,
                'difficulty': 'hard',
                'scenery_score': 9.8,
                'image_url': 'https://images.unsplash.com/photo-1578662996442-48f60103fc96?w=400&h=300&fit=crop&auto=format',
                'icon': 'trail-sign-outline',
                'waypoints': [
                    {'name': '어리목 탐방로입구', 'coordinates': [126.4833, 33.3500]},
                    {'name': '한라산 정상', 'coordinates': [126.5311, 33.3617]}
                ]
            },
            {
                'id': 5,
                'title': '제주 전통시장 탐방',
                'subtitle': '현지 맛과 문화를 체험하는 특별한 여행',
                'duration': 120,
                'distance': 8.3,
                'difficulty': 'easy',
                'scenery_score': 7.5,
                'image_url': 'https://images.unsplash.com/photo-1555396273-367ea4eb4db5?w=400&h=300&fit=crop&auto=format',
                'icon': 'storefront-outline',
                'waypoints': [
                    {'name': '동문시장', 'coordinates': [126.5219, 33.5126]},
                    {'name': '중앙지하상가', 'coordinates': [126.5200, 33.5100]}
                ]
            }
        ]
        
        return jsonify({
            'success': True,
            'routes': routes
        })
        
    except Exception as e:
        print(f"추천 경로 조회 오류: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    print("🏝️ VISTA API 서버 시작 중...")
    print("React Native 앱과 연동 준비 완료")
    print("서버 주소: http://localhost:5000")
    
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True
    ) 