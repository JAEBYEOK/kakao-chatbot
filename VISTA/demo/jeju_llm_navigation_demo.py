import json
import requests
import folium
import math
import re
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass

@dataclass
class UserPreferences:
    """사용자 선호도 데이터 클래스"""
    travel_style: str  # "leisurely", "efficient", "adventure"
    interests: List[str]  # ["nature", "food", "culture", "photo"]
    pace: str  # "slow", "normal", "fast"
    time_constraints: Optional[str] = None
    budget_level: str = "medium"  # "low", "medium", "high"
    group_type: str = "couple"  # "solo", "couple", "family", "friends"

class NaturalLanguageProcessor:
    """자연어 처리 및 STT 시뮬레이션"""
    
    def __init__(self):
        self.intent_patterns = self._initialize_intent_patterns()
        self.location_keywords = self._initialize_location_keywords()
        
    def _initialize_intent_patterns(self) -> Dict:
        """의도 파악을 위한 패턴 정의"""
        return {
            "scenic_route": [
                "경치", "풍경", "아름다운", "예쁜", "경관", "바다", "해안", "산", "자연"
            ],
            "food_focused": [
                "맛집", "음식", "먹거리", "카페", "식당", "흑돼지", "해산물", "갈치"
            ],
            "time_efficient": [
                "빨리", "최단", "시간", "효율", "바로", "직진", "급해"
            ],
            "leisurely": [
                "천천히", "여유", "둘러", "구경", "산책", "드라이브", "휴식"
            ],
            "cultural": [
                "문화", "역사", "전통", "박물관", "유적", "체험", "올레길"
            ],
            "photography": [
                "사진", "인스타", "핫플", "포토존", "인생샷", "셀카"
            ]
        }
    
    def _initialize_location_keywords(self) -> Dict:
        """지역별 키워드 매핑"""
        return {
            "성산일출봉": ["성산", "일출봉", "썽산", "해돋이"],
            "애월": ["애월", "애월카페", "GD카페", "애월해안"],
            "한라산": ["한라산", "할라산", "백록담", "등산"],
            "우도": ["우도", "소섬", "우도섬", "배타고"],
            "중문": ["중문", "여미지", "테디베어", "중문해변"],
            "서귀포": ["서귀포", "천지연", "정방폭포", "올레시장"],
            "협재": ["협재", "협재해변", "금능", "비양도"],
            "제주공항": ["공항", "제주공항", "출발", "시작"]
        }
    
    def process_voice_command(self, command: str) -> Dict:
        """음성 명령 처리 (STT 시뮬레이션)"""
        
        # 실제로는 STT API 호출
        # command = stt_api.recognize(audio_input)
        
        print(f"🎤 음성 명령 인식: '{command}'")
        
        # 의도 분석
        intents = self._extract_intents(command)
        
        # 장소 추출
        locations = self._extract_locations(command)
        
        # 시간 조건 추출
        time_conditions = self._extract_time_conditions(command)
        
        # 선호도 추출
        preferences = self._extract_preferences(command)
        
        return {
            "original_command": command,
            "intents": intents,
            "locations": locations,
            "time_conditions": time_conditions,
            "preferences": preferences,
            "confidence": 0.85  # STT 신뢰도
        }
    
    def _extract_intents(self, command: str) -> List[str]:
        """의도 추출"""
        intents = []
        
        for intent, keywords in self.intent_patterns.items():
            if any(keyword in command for keyword in keywords):
                intents.append(intent)
        
        return intents if intents else ["general_navigation"]
    
    def _extract_locations(self, command: str) -> Dict:
        """장소 추출"""
        locations = {"start": None, "end": None, "waypoints": []}
        
        for location, keywords in self.location_keywords.items():
            if any(keyword in command for keyword in keywords):
                if "에서" in command or "출발" in command:
                    locations["start"] = location
                elif "까지" in command or "으로" in command or "가자" in command:
                    locations["end"] = location
                else:
                    locations["waypoints"].append(location)
        
        return locations
    
    def _extract_time_conditions(self, command: str) -> Dict:
        """시간 조건 추출"""
        time_conditions = {}
        
        if any(word in command for word in ["급해", "빨리", "시간"]):
            time_conditions["urgency"] = "high"
        elif any(word in command for word in ["천천히", "여유"]):
            time_conditions["urgency"] = "low"
        else:
            time_conditions["urgency"] = "normal"
            
        if "오전" in command:
            time_conditions["preferred_time"] = "morning"
        elif "오후" in command:
            time_conditions["preferred_time"] = "afternoon"
        elif "저녁" in command:
            time_conditions["preferred_time"] = "evening"
            
        return time_conditions
    
    def _extract_preferences(self, command: str) -> UserPreferences:
        """사용자 선호도 추출"""
        
        # 여행 스타일 결정
        if any(word in command for word in ["천천히", "여유", "구경"]):
            travel_style = "leisurely"
        elif any(word in command for word in ["빨리", "효율", "시간"]):
            travel_style = "efficient"
        else:
            travel_style = "balanced"
        
        # 관심사 추출
        interests = []
        if any(word in command for word in ["경치", "바다", "산", "자연"]):
            interests.append("nature")
        if any(word in command for word in ["맛집", "음식", "카페"]):
            interests.append("food")
        if any(word in command for word in ["사진", "인스타", "포토"]):
            interests.append("photography")
        if any(word in command for word in ["문화", "역사", "체험"]):
            interests.append("culture")
            
        return UserPreferences(
            travel_style=travel_style,
            interests=interests if interests else ["general"],
            pace="slow" if "천천히" in command else "normal"
        )

class LLMRoutePlanner:
    """LLM 기반 경로 계획 시스템"""
    
    def __init__(self, jeju_db):
        self.jeju_db = jeju_db
        self.conversation_history = []
        
    def plan_personalized_route(self, nlp_result: Dict, user_profile: Dict = None) -> Dict:
        """개인화된 경로 계획"""
        
        print("🤖 LLM 경로 계획 시작...")
        
        # 사용자 의도 분석
        intents = nlp_result["intents"]
        locations = nlp_result["locations"]
        preferences = nlp_result["preferences"]
        
        # LLM 프롬프트 생성 (시뮬레이션)
        prompt = self._generate_planning_prompt(nlp_result)
        
        # LLM 응답 시뮬레이션
        llm_response = self._simulate_llm_response(prompt, intents, preferences)
        
        # 경로 계획 실행
        route_plan = self._execute_route_planning(llm_response, locations)
        
        # 대화 히스토리 업데이트
        self.conversation_history.append({
            "user_input": nlp_result["original_command"],
            "llm_analysis": llm_response,
            "route_plan": route_plan,
            "timestamp": datetime.now()
        })
        
        return route_plan
    
    def _generate_planning_prompt(self, nlp_result: Dict) -> str:
        """LLM용 프롬프트 생성"""
        command = nlp_result["original_command"]
        intents = nlp_result["intents"]
        locations = nlp_result["locations"]
        
        prompt = f"""
        제주도 여행 전문 AI 가이드로서 다음 요청을 분석하고 최적의 경로를 계획해주세요.

        사용자 요청: "{command}"
        감지된 의도: {intents}
        언급된 장소: {locations}
        
        고려사항:
        1. 제주도 지역 특성 (해안도로, 관광명소, 맛집 등)
        2. 사용자의 여행 스타일과 선호도
        3. 시간 효율성과 경험의 질 균형
        4. 제주도만의 특별한 매력 포인트
        
        응답 형식:
        - 추천 경로와 이유
        - 주요 경유지 및 체험 요소
        - 예상 소요시간과 하이라이트
        """
        
        return prompt
    
    def _simulate_llm_response(self, prompt: str, intents: List[str], preferences: UserPreferences) -> Dict:
        """LLM 응답 시뮬레이션"""
        
        # 실제로는 OpenAI API 호출
        # response = openai.ChatCompletion.create(...)
        
        # 의도별 가중치 계산
        weights = {
            "scenic_route": 1.0 if "scenic_route" in intents else 0.3,
            "food_focused": 1.0 if "food_focused" in intents else 0.2,
            "time_efficient": 1.0 if "time_efficient" in intents else 0.5,
            "leisurely": 1.0 if "leisurely" in intents else 0.4,
            "photography": 1.0 if "photography" in intents else 0.3
        }
        
        # 추천 경유지 선정
        recommended_waypoints = []
        
        if weights["scenic_route"] > 0.7:
            recommended_waypoints.extend(["애월해안도로", "협재해수욕장"])
        if weights["food_focused"] > 0.7:
            recommended_waypoints.extend(["동문시장", "흑돼지거리"])
        if weights["photography"] > 0.7:
            recommended_waypoints.extend(["성산일출봉", "애월카페거리"])
            
        # 여행 스타일별 조정
        if preferences.travel_style == "leisurely":
            route_priority = "경치와 여유"
            suggested_duration_multiplier = 1.5
        elif preferences.travel_style == "efficient":
            route_priority = "시간 효율성"
            suggested_duration_multiplier = 0.8
        else:
            route_priority = "균형잡힌 경험"
            suggested_duration_multiplier = 1.0
            
        return {
            "route_priority": route_priority,
            "recommended_waypoints": recommended_waypoints,
            "duration_multiplier": suggested_duration_multiplier,
            "reasoning": f"{', '.join(intents)} 의도를 반영한 {preferences.travel_style} 스타일 경로",
            "highlights": self._generate_highlights(intents, recommended_waypoints),
            "weights": weights
        }
    
    def _generate_highlights(self, intents: List[str], waypoints: List[str]) -> List[str]:
        """하이라이트 생성"""
        highlights = []
        
        if "scenic_route" in intents:
            highlights.append("🌊 에메랄드빛 제주 바다 전망")
        if "food_focused" in intents:
            highlights.append("🍖 제주 흑돼지와 특산물 맛보기")
        if "photography" in intents:
            highlights.append("📸 인스타그래머블한 포토존 탐방")
        if "cultural" in intents:
            highlights.append("🏛️ 제주의 역사와 문화 체험")
            
        return highlights
    
    def _execute_route_planning(self, llm_response: Dict, locations: Dict) -> Dict:
        """경로 계획 실행"""
        
        # 기본 좌표 설정
        coords_map = {
            "제주공항": [126.4930, 33.5107],
            "성산일출봉": [126.9423, 33.4586],
            "애월": [126.3094, 33.4647],
            "한라산": [126.5311, 33.3617],
            "우도": [126.9513, 33.5069],
            "협재": [126.2397, 33.3948],
            "서귀포": [126.5619, 33.2541]
        }
        
        start_location = locations.get("start") or "제주공항"
        end_location = locations.get("end") or "성산일출봉"
        
        start_coords = coords_map.get(start_location, coords_map["제주공항"])
        end_coords = coords_map.get(end_location, coords_map["성산일출봉"])
        
        # 추천 경유지를 고려한 최적 경로 생성
        optimized_waypoints = self._optimize_waypoint_order(
            start_coords, end_coords, llm_response["recommended_waypoints"], coords_map
        )
        
        return {
            "start": {"name": start_location, "coordinates": start_coords},
            "end": {"name": end_location, "coordinates": end_coords},
            "waypoints": optimized_waypoints,
            "llm_reasoning": llm_response["reasoning"],
            "highlights": llm_response["highlights"],
            "route_priority": llm_response["route_priority"],
            "estimated_duration_hours": self._estimate_total_duration(
                start_coords, end_coords, optimized_waypoints, llm_response["duration_multiplier"]
            )
        }
    
    def _optimize_waypoint_order(self, start: List[float], end: List[float], 
                                waypoints: List[str], coords_map: Dict) -> List[Dict]:
        """경유지 순서 최적화"""
        
        optimized = []
        for waypoint in waypoints:
            if waypoint in coords_map or any(key in waypoint for key in coords_map.keys()):
                # 키워드 매칭으로 좌표 찾기
                coord = None
                for location, coord_val in coords_map.items():
                    if location in waypoint:
                        coord = coord_val
                        break
                
                if coord:
                    optimized.append({
                        "name": waypoint,
                        "coordinates": coord,
                        "type": self._classify_waypoint_type(waypoint)
                    })
        
        return optimized
    
    def _classify_waypoint_type(self, waypoint: str) -> str:
        """경유지 타입 분류"""
        if any(word in waypoint for word in ["해안", "바다", "해수욕장"]):
            return "scenic"
        elif any(word in waypoint for word in ["시장", "맛집", "거리"]):
            return "food"
        elif any(word in waypoint for word in ["카페", "포토"]):
            return "photo"
        else:
            return "general"
    
    def _estimate_total_duration(self, start: List[float], end: List[float], 
                               waypoints: List[Dict], multiplier: float) -> float:
        """총 소요시간 추정"""
        base_duration = 2.0  # 기본 2시간
        waypoint_time = len(waypoints) * 0.5  # 경유지당 30분
        return (base_duration + waypoint_time) * multiplier

class PersonalizedNavigator:
    """개인화 내비게이션 시스템"""
    
    def __init__(self, jeju_db):
        self.jeju_db = jeju_db
        
    def execute_navigation(self, route_plan: Dict) -> Dict:
        """개인화된 내비게이션 실행"""
        
        print("🗺️ 개인화 내비게이션 실행 중...")
        
        # OSRM으로 실제 경로 계산
        navigation_route = self._calculate_actual_route(route_plan)
        
        if not navigation_route:
            return {"error": "경로 계산 실패"}
        
        # LLM 기반 개인화 적용
        personalized_route = self._apply_personalization(navigation_route, route_plan)
        
        return personalized_route
    
    def _calculate_actual_route(self, route_plan: Dict) -> Dict:
        """실제 OSRM 경로 계산"""
        
        start_coords = route_plan["start"]["coordinates"]
        end_coords = route_plan["end"]["coordinates"]
        
        # OSRM API 호출
        osrm_url = f"http://router.project-osrm.org/route/v1/driving/{start_coords[0]},{start_coords[1]};{end_coords[0]},{end_coords[1]}"
        params = {
            'overview': 'full',
            'geometries': 'geojson',
            'steps': 'true'
        }
        
        try:
            response = requests.get(osrm_url, params=params)
            data = response.json()
            
            if data['code'] == 'Ok':
                return data['routes'][0]
        except Exception as e:
            print(f"OSRM 에러: {e}")
        
        return None
    
    def _apply_personalization(self, navigation_route: Dict, route_plan: Dict) -> Dict:
        """개인화 요소 적용"""
        
        # 기본 경로 정보
        enhanced_route = {
            **navigation_route,
            "llm_features": {
                "personalized_highlights": route_plan["highlights"],
                "reasoning": route_plan["llm_reasoning"],
                "route_priority": route_plan["route_priority"],
                "planned_waypoints": route_plan["waypoints"],
                "estimated_duration": route_plan["estimated_duration_hours"],
                "personalized_messages": self._generate_personalized_messages(route_plan),
                "smart_recommendations": self._generate_smart_recommendations(route_plan)
            }
        }
        
        return enhanced_route

    def _generate_personalized_messages(self, route_plan: Dict) -> List[str]:
        """개인화된 메시지 생성"""
        messages = []
        
        # 출발 메시지
        messages.append(f"✨ {route_plan['route_priority']} 중심의 제주도 여행을 시작합니다!")
        
        # 하이라이트별 메시지
        for highlight in route_plan["highlights"]:
            if "바다" in highlight:
                messages.append("🌊 곧 제주의 아름다운 해안선을 만나실 수 있어요")
            elif "맛" in highlight:
                messages.append("🍽️ 제주의 특별한 맛집들이 여러분을 기다리고 있어요")
            elif "사진" in highlight:
                messages.append("📸 인생샷을 남길 수 있는 포토존에 도착했어요")
        
        # 도착 메시지
        messages.append(f"🎯 {route_plan['end']['name']}에 도착했습니다. 멋진 여행 되세요!")
        
        return messages
    
    def _generate_smart_recommendations(self, route_plan: Dict) -> List[Dict]:
        """스마트 추천 생성"""
        recommendations = []
        
        current_hour = datetime.now().hour
        
        # 시간대별 추천
        if 5 <= current_hour <= 7:
            recommendations.append({
                "type": "time_based",
                "message": "일출 시간대입니다. 성산일출봉에서의 일출 감상을 추천드려요!",
                "action": "성산일출봉 우선 방문"
            })
        elif 11 <= current_hour <= 14:
            recommendations.append({
                "type": "time_based", 
                "message": "점심시간입니다. 제주 흑돼지나 해산물 맛집 방문을 추천드려요!",
                "action": "근처 맛집 안내"
            })
        elif 17 <= current_hour <= 19:
            recommendations.append({
                "type": "time_based",
                "message": "일몰 시간대입니다. 서쪽 해안에서의 일몰 감상을 추천드려요!",
                "action": "서쪽 해안 이동"
            })
        
        # 경유지별 추천
        for waypoint in route_plan["waypoints"]:
            if waypoint["type"] == "scenic":
                recommendations.append({
                    "type": "scenic",
                    "message": f"{waypoint['name']}에서 사진 촬영 시간을 충분히 가지세요",
                    "action": "포토존 안내"
                })
        
        return recommendations

class VoiceAssistant:
    """음성 안내 시스템"""
    
    def __init__(self):
        self.tts_enabled = True  # 실제로는 TTS 엔진 연동
        
    def generate_voice_guidance(self, personalized_route: Dict) -> List[str]:
        """음성 안내 생성"""
        
        llm_features = personalized_route.get("llm_features", {})
        
        # 자연어 기반 안내 메시지
        guidance_messages = []
        
        # 여행 시작 안내
        guidance_messages.extend(llm_features.get("personalized_messages", []))
        
        # 경로 상세 안내
        distance_km = personalized_route["distance"] / 1000
        duration_min = personalized_route["duration"] / 60
        
        guidance_messages.append(
            f"📍 총 거리 {distance_km:.1f}킬로미터, 예상 시간 {duration_min:.0f}분 경로로 안내하겠습니다."
        )
        
        # LLM 추천 이유 설명
        reasoning = llm_features.get("reasoning", "")
        if reasoning:
            guidance_messages.append(f"💭 {reasoning}으로 이 경로를 선택했어요.")
        
        # 스마트 추천 안내
        for rec in llm_features.get("smart_recommendations", []):
            guidance_messages.append(f"💡 {rec['message']}")
        
        return guidance_messages
    
    def speak(self, message: str):
        """TTS 음성 출력 (시뮬레이션)"""
        print(f"🔊 TTS: {message}")
        # 실제로는 TTS API 호출
        # tts_engine.speak(message)

def create_llm_enhanced_visualization(route_data: Dict, output_file: str = "jeju_llm_navigation.html"):
    """LLM 강화 지도 시각화"""
    
    if not route_data:
        print("경로 데이터가 없습니다.")
        return
    
    # 제주도 중심 지도 생성
    m = folium.Map(
        location=[33.3617, 126.5312],
        zoom_start=10,
        tiles='OpenStreetMap'
    )
    
    # 기본 경로 표시
    coordinates = route_data['geometry']['coordinates']
    folium_coords = [[coord[1], coord[0]] for coord in coordinates]
    
    folium.PolyLine(
        folium_coords,
        weight=5,
        color='purple',
        opacity=0.8,
        popup=f"🤖 LLM 추천 경로: {route_data['distance']/1000:.1f}km"
    ).add_to(m)
    
    # LLM 특화 정보 표시
    llm_features = route_data.get('llm_features', {})
    
    # 계획된 경유지 표시
    for i, waypoint in enumerate(llm_features.get('planned_waypoints', [])):
        wp_coord = waypoint['coordinates']
        wp_type = waypoint.get('type', 'general')
        
        # 타입별 색상 설정
        color_map = {
            'scenic': 'green',
            'food': 'orange', 
            'photo': 'red',
            'general': 'blue'
        }
        
        folium.Marker(
            [wp_coord[1], wp_coord[0]],
            popup=f"""
            <b>🎯 LLM 추천: {waypoint['name']}</b><br>
            타입: {wp_type}<br>
            순서: {i+1}번째 경유지
            """,
            icon=folium.Icon(color=color_map.get(wp_type, 'blue'), icon='star')
        ).add_to(m)
    
    # LLM 하이라이트 정보 패널
    highlights = llm_features.get('personalized_highlights', [])
    reasoning = llm_features.get('reasoning', '')
    
    info_html = f"""
    <div style="position: fixed; 
                top: 10px; left: 50px; width: 350px; height: 300px; 
                background-color: white; border:2px solid purple; z-index:9999; 
                font-size:14px; padding: 15px; border-radius: 10px;">
    <h4>🤖 LLM 기반 제주도 내비게이션</h4>
    <p><b>🎯 경로 우선순위:</b> {llm_features.get('route_priority', '균형')}</p>
    <p><b>⏱️ 예상 소요시간:</b> {llm_features.get('estimated_duration', 0):.1f}시간</p>
    <p><b>🧠 AI 추천 이유:</b><br>{reasoning}</p>
    <p><b>✨ 여행 하이라이트:</b></p>
    <ul>
    {''.join([f"<li>{h}</li>" for h in highlights])}
    </ul>
    </div>
    """
    m.get_root().html.add_child(folium.Element(info_html))
    
    # 지도 저장
    m.save(output_file)
    print(f"🤖 LLM 강화 지도가 '{output_file}'로 저장되었습니다!")

def main():
    """LLM 통합 내비게이션 데모"""
    print("🤖 제주도 LLM 통합 내비게이션 데모 시작")
    print("=" * 50)
    
    # 시스템 컴포넌트 초기화
    nlp = NaturalLanguageProcessor()
    
    # 제주도 DB 더미 (기존 코드에서 가져올 수 있음)
    jeju_db = {}  
    
    llm_planner = LLMRoutePlanner(jeju_db)
    navigator = PersonalizedNavigator(jeju_db)
    voice_assistant = VoiceAssistant()
    
    # 데모 시나리오
    demo_commands = [
        "제주공항에서 성산일출봉까지 경치 좋은 길로 천천히 가고 싶어",
        "애월카페거리에서 맛집 들러서 협재해변까지",
        "사진 찍기 좋은 곳들 위주로 제주 일주하고 싶어"
    ]
    
    for i, command in enumerate(demo_commands, 1):
        print(f"\n🎬 데모 시나리오 {i}")
        print("-" * 30)
        
        # 1단계: STT + 자연어 처리
        nlp_result = nlp.process_voice_command(command)
        
        # 2단계: LLM 기반 경로 계획
        route_plan = llm_planner.plan_personalized_route(nlp_result)
        
        # 3단계: 개인화 내비게이션 실행
        personalized_route = navigator.execute_navigation(route_plan)
        
        if "error" not in personalized_route:
            # 4단계: 음성 안내 생성
            guidance_messages = voice_assistant.generate_voice_guidance(personalized_route)
            
            # 결과 출력
            print(f"\n✅ 시나리오 {i} 결과:")
            print(f"🎯 경로 우선순위: {route_plan['route_priority']}")
            print(f"📍 경유지: {[w['name'] for w in route_plan['waypoints']]}")
            print(f"✨ 하이라이트: {route_plan['highlights']}")
            
            print(f"\n🔊 음성 안내:")
            for msg in guidance_messages[:3]:  # 처음 3개만 출력
                voice_assistant.speak(msg)
            
            # 첫 번째 시나리오만 지도로 시각화
            if i == 1:
                create_llm_enhanced_visualization(personalized_route, f"jeju_llm_demo_{i}.html")
        
        else:
            print(f"❌ 시나리오 {i} 실패: {personalized_route['error']}")
    
    print(f"\n🎉 LLM 통합 내비게이션 데모 완료!")
    print("실제 구현시에는 OpenAI GPT, STT/TTS 엔진이 통합됩니다.")

if __name__ == "__main__":
    main() 