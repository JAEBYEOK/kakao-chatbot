import json
import requests
import folium
import math
from datetime import datetime
from typing import Dict, List, Optional

print("LLM 데모 시스템을 초기화합니다...")

class STTProcessor:
    """STT 음성 인식 시뮬레이션"""
    
    def __init__(self):
        self.keywords = {
            "경치": ["경치", "풍경", "아름다운", "예쁜", "바다", "해안", "자연"],
            "맛집": ["맛집", "음식", "먹거리", "카페", "식당", "흑돼지"],
            "빠른": ["빨리", "최단", "시간", "효율", "급해"],
            "여유": ["천천히", "여유", "둘러", "구경", "드라이브"],
            "사진": ["사진", "인스타", "핫플", "포토존", "셀카"]
        }
        
        self.locations = {
            "제주공항": [126.4930, 33.5107],
            "성산일출봉": [126.9423, 33.4586],
            "애월": [126.3094, 33.4647],
            "협재": [126.2397, 33.3948],
            "한라산": [126.5311, 33.3617],
            "서귀포": [126.5619, 33.2541]
        }
    
    def recognize_voice(self, command: str) -> Dict:
        """음성 명령 인식"""
        print(f"🎤 STT 인식: '{command}'")
        
        # 의도 분석
        intents = []
        for intent, words in self.keywords.items():
            if any(word in command for word in words):
                intents.append(intent)
        
        # 장소 추출
        start_location = None
        end_location = None
        
        for location in self.locations.keys():
            if location in command:
                if "에서" in command or "출발" in command:
                    start_location = location
                elif "까지" in command or "으로" in command:
                    end_location = location
        
        return {
            "command": command,
            "intents": intents,
            "start": start_location or "제주공항",
            "end": end_location or "성산일출봉",
            "confidence": 0.9
        }

class LLMPlanner:
    """LLM 기반 경로 계획 엔진"""
    
    def __init__(self):
        self.user_profiles = {}
        
    def analyze_user_intent(self, stt_result: Dict) -> Dict:
        """사용자 의도 분석 (LLM 시뮬레이션)"""
        
        print("🤖 LLM 의도 분석 중...")
        
        command = stt_result["command"]
        intents = stt_result["intents"]
        
        # LLM 프롬프트 시뮬레이션
        analysis = {
            "travel_style": self._determine_travel_style(intents),
            "preferences": self._extract_preferences(intents),
            "priority_weights": self._calculate_weights(intents),
            "reasoning": self._generate_reasoning(command, intents)
        }
        
        return analysis
    
    def _determine_travel_style(self, intents: List[str]) -> str:
        """여행 스타일 결정"""
        if "여유" in intents:
            return "leisurely"  # 여유로운
        elif "빠른" in intents:
            return "efficient"  # 효율적
        else:
            return "balanced"  # 균형잡힌
    
    def _extract_preferences(self, intents: List[str]) -> List[str]:
        """선호도 추출"""
        preferences = []
        
        if "경치" in intents:
            preferences.append("scenic_route")
        if "맛집" in intents:
            preferences.append("food_stops")
        if "사진" in intents:
            preferences.append("photo_spots")
            
        return preferences if preferences else ["general"]
    
    def _calculate_weights(self, intents: List[str]) -> Dict:
        """가중치 계산"""
        weights = {
            "scenery": 0.5,
            "efficiency": 0.3,
            "food": 0.2,
            "photo": 0.2
        }
        
        if "경치" in intents:
            weights["scenery"] = 1.0
        if "빠른" in intents:
            weights["efficiency"] = 1.0
        if "맛집" in intents:
            weights["food"] = 0.8
        if "사진" in intents:
            weights["photo"] = 0.8
            
        return weights
    
    def _generate_reasoning(self, command: str, intents: List[str]) -> str:
        """추천 이유 생성"""
        
        if "경치" in intents and "여유" in intents:
            return "경치를 천천히 감상할 수 있는 해안도로 중심 경로"
        elif "맛집" in intents:
            return "제주 특산물과 맛집을 경험할 수 있는 미식 여행 경로"
        elif "사진" in intents:
            return "인스타그래머블한 포토존 중심의 SNS 여행 경로"
        elif "빠른" in intents:
            return "목적지까지 가장 효율적인 최단 시간 경로"
        else:
            return "제주도의 다양한 매력을 균형있게 경험할 수 있는 경로"
    
    def plan_route(self, stt_result: Dict, analysis: Dict) -> Dict:
        """맞춤형 경로 계획"""
        
        print("🗺️ LLM 맞춤형 경로 계획 생성...")
        
        start = stt_result["start"]
        end = stt_result["end"]
        weights = analysis["priority_weights"]
        preferences = analysis["preferences"]
        
        # 추천 경유지 선정
        waypoints = self._select_waypoints(preferences, weights)
        
        # 경로 최적화
        optimized_route = self._optimize_route(start, end, waypoints)
        
        return {
            "start_location": start,
            "end_location": end,
            "waypoints": optimized_route["waypoints"],
            "reasoning": analysis["reasoning"],
            "estimated_time": optimized_route["time"],
            "highlights": optimized_route["highlights"],
            "llm_score": self._calculate_llm_score(weights, optimized_route)
        }
    
    def _select_waypoints(self, preferences: List[str], weights: Dict) -> List[Dict]:
        """경유지 선정"""
        
        waypoint_pool = {
            "scenic_route": [
                {"name": "애월해안도로", "coords": [126.3094, 33.4647], "type": "scenic"},
                {"name": "협재해수욕장", "coords": [126.2397, 33.3948], "type": "scenic"}
            ],
            "food_stops": [
                {"name": "동문시장", "coords": [126.5258, 33.5145], "type": "food"},
                {"name": "흑돼지거리", "coords": [126.5219, 33.4996], "type": "food"}
            ],
            "photo_spots": [
                {"name": "애월카페거리", "coords": [126.3094, 33.4647], "type": "photo"},
                {"name": "성산일출봉전망대", "coords": [126.9423, 33.4586], "type": "photo"}
            ]
        }
        
        selected_waypoints = []
        
        for pref in preferences:
            if pref in waypoint_pool:
                selected_waypoints.extend(waypoint_pool[pref])
        
        # 중복 제거
        unique_waypoints = []
        seen_names = set()
        for wp in selected_waypoints:
            if wp["name"] not in seen_names:
                unique_waypoints.append(wp)
                seen_names.add(wp["name"])
        
        return unique_waypoints[:3]  # 최대 3개
    
    def _optimize_route(self, start: str, end: str, waypoints: List[Dict]) -> Dict:
        """경로 최적화"""
        
        # 기본 소요시간 계산
        base_time = 1.5  # 기본 1.5시간
        waypoint_time = len(waypoints) * 0.5  # 경유지당 30분
        total_time = base_time + waypoint_time
        
        # 하이라이트 생성
        highlights = []
        for wp in waypoints:
            if wp["type"] == "scenic":
                highlights.append(f"🌊 {wp['name']}에서의 환상적인 바다 전망")
            elif wp["type"] == "food":
                highlights.append(f"🍽️ {wp['name']}에서 제주 특산물 맛보기")
            elif wp["type"] == "photo":
                highlights.append(f"📸 {wp['name']}에서 인생샷 촬영")
        
        return {
            "waypoints": waypoints,
            "time": total_time,
            "highlights": highlights
        }
    
    def _calculate_llm_score(self, weights: Dict, route: Dict) -> float:
        """LLM 만족도 점수"""
        score = 0.0
        
        # 경유지 타입별 점수
        for wp in route["waypoints"]:
            if wp["type"] == "scenic":
                score += weights.get("scenery", 0) * 2
            elif wp["type"] == "food":
                score += weights.get("food", 0) * 2
            elif wp["type"] == "photo":
                score += weights.get("photo", 0) * 2
        
        return min(score / len(route["waypoints"]), 10.0) if route["waypoints"] else 5.0

class SmartNavigator:
    """스마트 내비게이션 실행 엔진"""
    
    def __init__(self):
        self.stt = STTProcessor()
        self.llm = LLMPlanner()
        
    def execute_navigation(self, route_plan: Dict) -> Dict:
        """내비게이션 실행"""
        
        print("🚗 스마트 내비게이션 실행...")
        
        # OSRM으로 실제 경로 계산
        start_coords = self.stt.locations[route_plan["start_location"]]
        end_coords = self.stt.locations[route_plan["end_location"]]
        
        actual_route = self._get_osrm_route(start_coords, end_coords)
        
        if actual_route:
            # LLM 계획과 실제 경로 통합
            enhanced_route = self._enhance_with_llm_plan(actual_route, route_plan)
            return enhanced_route
        else:
            return {"error": "경로 계산 실패"}
    
    def _get_osrm_route(self, start: List[float], end: List[float]) -> Dict:
        """OSRM 경로 조회"""
        
        osrm_url = f"http://router.project-osrm.org/route/v1/driving/{start[0]},{start[1]};{end[0]},{end[1]}"
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
    
    def _enhance_with_llm_plan(self, osrm_route: Dict, llm_plan: Dict) -> Dict:
        """LLM 계획으로 경로 강화"""
        
        enhanced = {
            **osrm_route,
            "llm_enhancements": {
                "reasoning": llm_plan["reasoning"],
                "waypoints": llm_plan["waypoints"],
                "highlights": llm_plan["highlights"],
                "estimated_time": llm_plan["estimated_time"],
                "llm_score": llm_plan["llm_score"],
                "voice_guidance": self._generate_voice_guidance(llm_plan)
            }
        }
        
        return enhanced
    
    def _generate_voice_guidance(self, llm_plan: Dict) -> List[str]:
        """음성 안내 생성"""
        
        guidance = []
        
        # 시작 안내
        reasoning = llm_plan["reasoning"]
        guidance.append(f"✨ {reasoning}으로 여행을 시작하겠습니다!")
        
        # 경유지 안내
        for i, wp in enumerate(llm_plan["waypoints"], 1):
            guidance.append(f"🎯 {i}번째 경유지: {wp['name']}입니다")
        
        # 하이라이트 안내
        for highlight in llm_plan["highlights"]:
            guidance.append(f"💫 {highlight}")
        
        # 도착 안내
        guidance.append(f"🏁 {llm_plan['end_location']}에 도착했습니다. 즐거운 제주 여행 되세요!")
        
        return guidance

def create_llm_demo_visualization(route_data: Dict, output_file: str = "jeju_llm_demo.html"):
    """LLM 데모 지도 시각화"""
    
    if "error" in route_data:
        print(f"시각화 불가: {route_data['error']}")
        return
    
    # 제주도 중심 지도
    m = folium.Map(
        location=[33.3617, 126.5312],
        zoom_start=10,
        tiles='OpenStreetMap'
    )
    
    # OSRM 경로 표시
    coordinates = route_data['geometry']['coordinates']
    folium_coords = [[coord[1], coord[0]] for coord in coordinates]
    
    folium.PolyLine(
        folium_coords,
        weight=6,
        color='purple',
        opacity=0.8,
        popup=f"🤖 LLM 맞춤형 경로: {route_data['distance']/1000:.1f}km"
    ).add_to(m)
    
    # LLM 강화 정보
    llm_info = route_data.get("llm_enhancements", {})
    
    # LLM 추천 경유지 표시
    for i, waypoint in enumerate(llm_info.get("waypoints", []), 1):
        coords = waypoint["coords"]
        wp_type = waypoint["type"]
        
        # 타입별 아이콘
        icon_map = {
            "scenic": {"color": "green", "icon": "camera"},
            "food": {"color": "orange", "icon": "cutlery"},
            "photo": {"color": "red", "icon": "star"}
        }
        
        icon_info = icon_map.get(wp_type, {"color": "blue", "icon": "info-sign"})
        
        folium.Marker(
            [coords[1], coords[0]],
            popup=f"""
            <b>🤖 LLM 추천 {i}번째</b><br>
            <b>{waypoint['name']}</b><br>
            타입: {wp_type}<br>
            AI 선정 이유: 사용자 선호도 반영
            """,
            icon=folium.Icon(
                color=icon_info["color"], 
                icon=icon_info["icon"]
            )
        ).add_to(m)
    
    # LLM 정보 패널
    reasoning = llm_info.get("reasoning", "")
    highlights = llm_info.get("highlights", [])
    llm_score = llm_info.get("llm_score", 0)
    
    info_panel = f"""
    <div style="position: fixed; 
                top: 10px; left: 50px; width: 400px; height: 350px; 
                background-color: white; border: 3px solid purple; z-index: 9999; 
                font-size: 14px; padding: 15px; border-radius: 15px; box-shadow: 0 4px 8px rgba(0,0,0,0.1);">
    <h3>🤖 LLM 맞춤형 내비게이션</h3>
    
    <p><b>🧠 AI 추천 이유:</b><br>{reasoning}</p>
    
    <p><b>📊 LLM 만족도:</b> {llm_score:.1f}/10</p>
    
    <p><b>⏱️ 예상 시간:</b> {llm_info.get('estimated_time', 0):.1f}시간</p>
    
    <p><b>✨ 여행 하이라이트:</b></p>
    <ul style="margin: 0; padding-left: 20px;">
    {''.join([f"<li style='margin-bottom: 5px;'>{h}</li>" for h in highlights])}
    </ul>
    
    <p style="margin-top: 10px; font-size: 12px; color: #666;">
    💡 실제 구현시 OpenAI GPT + STT/TTS 연동
    </p>
    </div>
    """
    
    m.get_root().html.add_child(folium.Element(info_panel))
    
    # 지도 저장
    m.save(output_file)
    print(f"🤖 LLM 데모 지도가 '{output_file}'로 저장되었습니다!")

def main():
    """LLM 통합 내비게이션 데모 실행"""
    
    print("🤖 제주도 LLM 통합 내비게이션 데모")
    print("=" * 50)
    
    # 시스템 초기화
    navigator = SmartNavigator()
    
    # 데모 시나리오들
    demo_scenarios = [
        "제주공항에서 성산일출봉까지 경치 좋은 길로 천천히 가고 싶어",
        "협재해변에서 맛집 들러서 서귀포까지 빨리 가자",
        "애월에서 사진 찍기 좋은 곳들 위주로 한라산까지"
    ]
    
    for i, scenario in enumerate(demo_scenarios, 1):
        print(f"\n🎬 데모 시나리오 {i}")
        print(f"📱 사용자: '{scenario}'")
        print("-" * 40)
        
        # 1단계: STT 음성 인식
        stt_result = navigator.stt.recognize_voice(scenario)
        print(f"✅ STT 결과: {stt_result['intents']} ({stt_result['confidence']*100:.0f}% 신뢰도)")
        
        # 2단계: LLM 의도 분석
        llm_analysis = navigator.llm.analyze_user_intent(stt_result)
        print(f"🧠 LLM 분석: {llm_analysis['travel_style']} 스타일, {llm_analysis['preferences']}")
        
        # 3단계: LLM 경로 계획
        route_plan = navigator.llm.plan_route(stt_result, llm_analysis)
        print(f"🗺️ 경로 계획: {route_plan['start_location']} → {route_plan['end_location']}")
        print(f"📍 경유지: {[wp['name'] for wp in route_plan['waypoints']]}")
        
        # 4단계: 스마트 내비게이션 실행
        final_route = navigator.execute_navigation(route_plan)
        
        if "error" not in final_route:
            print(f"✅ 내비게이션 성공!")
            print(f"📏 실제 거리: {final_route['distance']/1000:.1f}km")
            print(f"⏱️ 실제 시간: {final_route['duration']/60:.0f}분")
            print(f"🎯 LLM 점수: {final_route['llm_enhancements']['llm_score']:.1f}/10")
            
            # 음성 안내 시뮬레이션
            guidance = final_route['llm_enhancements']['voice_guidance']
            print(f"\n🔊 음성 안내 미리보기:")
            for j, msg in enumerate(guidance[:3], 1):
                print(f"  {j}. {msg}")
            
            # 첫 번째 시나리오만 지도로 시각화
            if i == 1:
                create_llm_demo_visualization(final_route)
                print(f"🗺️ 지도 시각화 완료")
        else:
            print(f"❌ 오류: {final_route['error']}")
        
        print()
    
    print("🎉 LLM 통합 내비게이션 데모 완료!")
    print("\n📋 구현된 주요 기능:")
    print("  ✓ STT 음성 명령 인식")
    print("  ✓ LLM 기반 사용자 의도 분석")
    print("  ✓ 맞춤형 경로 계획")
    print("  ✓ OSRM 실시간 라우팅")
    print("  ✓ 개인화된 음성 안내")
    print("  ✓ 인터랙티브 지도 시각화")
    print("\n💡 실제 프로덕션에서는:")
    print("  • OpenAI GPT-4 API 연동")
    print("  • NVIDIA Riva STT/TTS 엔진")
    print("  • 실시간 교통정보 반영")
    print("  • 사용자 학습 데이터 축적")

if __name__ == "__main__":
    main() 