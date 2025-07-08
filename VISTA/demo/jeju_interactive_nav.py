import json
import requests
import folium
import math
import os
import webbrowser
from datetime import datetime
from typing import Dict, List, Optional

class JejuDatabase:
    """jeju_database.json 파일을 관리하는 클래스"""
    def __init__(self, db_path='jeju_database.json'):
        self.db_path = db_path
        self.data = self._load_db()

    def _load_db(self) -> Dict:
        """JSON 데이터베이스 파일을 불러옵니다."""
        try:
            with open(self.db_path, 'r', encoding='utf-8') as f:
                print("✅ '{}' 데이터베이스를 성공적으로 불러왔습니다.".format(self.db_path))
                return json.load(f)
        except FileNotFoundError:
            print("❌ 에러: '{}' 파일을 찾을 수 없습니다.".format(self.db_path))
            return {}
        except json.JSONDecodeError:
            print("❌ 에러: '{}' 파일의 JSON 형식이 올바르지 않습니다.".format(self.db_path))
            return {}

    def get_poi(self, name: str) -> Optional[Dict]:
        return self.data.get('poi', {}).get(name)

    def get_all_pois(self) -> Dict:
        return self.data.get('poi', {})

class InteractiveSTT:
    """인터랙티브 STT 음성 인식 시스템"""
    
    def __init__(self, db: JejuDatabase):
        self.db = db
        self.keywords = {
            "경치": ["경치", "풍경", "아름다운", "예쁜", "바다", "해안", "자연", "뷰", "전망"],
            "맛집": ["맛집", "음식", "먹거리", "카페", "식당", "흑돼지", "해산물", "맛있는"],
            "빠른": ["빨리", "최단", "시간", "효율", "급해", "서둘러", "바로"],
            "여유": ["천천히", "여유", "둘러", "구경", "드라이브", "느긋", "편안"],
            "사진": ["사진", "인스타", "핫플", "포토존", "셀카", "인생샷", "예쁜곳"],
            "문화": ["문화", "역사", "전통", "박물관", "유적", "체험", "올레길"]
        }
        self.locations, self.location_aliases = self._initialize_locations()

    def _initialize_locations(self):
        locations = {}
        aliases = {}
        pois = self.db.get_all_pois()
        for name, info in pois.items():
            locations[name] = info['coordinates']
            for keyword in info.get('keywords', []):
                aliases[keyword] = name
        return locations, aliases
    
    def recognize_voice(self, command: str) -> Dict:
        print("🎤 명령 분석 중: '{}'".format(command))
        intents = []
        for intent, words in self.keywords.items():
            if any(word in command for word in words):
                intents.append(intent)
        
        start_location = None
        end_location = None
        mentioned_locations = set()
        
        for keyword in list(self.locations.keys()) + list(self.location_aliases.keys()):
            if keyword in command:
                location_name = self.location_aliases.get(keyword, keyword)
                mentioned_locations.add(location_name)

        mentioned_locations = list(mentioned_locations)

        for location in mentioned_locations:
            if any(marker in command for marker in ["에서", "출발", "시작"]):
                words = command.split()
                for i, word in enumerate(words):
                    if location in self.location_aliases.get(word, word) and i > 0:
                        if any(marker in words[i-1:i+2] for marker in ["에서", "출발", "시작"]):
                            start_location = location
                            break
            
            if any(marker in command for marker in ["까지", "으로", "로", "가자", "가고"]):
                words = command.split()
                for i, word in enumerate(words):
                    if location in self.location_aliases.get(word, word):
                        if any(marker in words[i:i+3] for marker in ["까지", "으로", "로", "가자", "가고"]):
                            end_location = location
                            break
        
        if not start_location and mentioned_locations:
            start_location = mentioned_locations[0]
        if not end_location and len(mentioned_locations) > 1:
            remaining_locations = [loc for loc in mentioned_locations if loc != start_location]
            if remaining_locations:
                end_location = remaining_locations[-1]

        start_location = start_location or "제주공항"
        end_location = end_location or "성산일출봉"
        
        confidence = 0.9 if intents and mentioned_locations else 0.7
        
        return {
            "command": command,
            "intents": intents if intents else ["일반"],
            "start": start_location,
            "end": end_location,
            "mentioned_locations": mentioned_locations,
            "confidence": confidence
        }

class InteractiveLLM:
    def __init__(self, db: JejuDatabase):
        self.db = db
        self.conversation_history = []
        self.user_preferences = {}
        
    def analyze_and_plan(self, stt_result: Dict) -> Dict:
        print("🤖 LLM이 여행 계획을 수립 중...")
        command = stt_result["command"]
        intents = stt_result["intents"]
        start = stt_result["start"]
        end = stt_result["end"]
        
        travel_style = self._analyze_travel_style(intents, command)
        weights = self._calculate_preference_weights(intents)
        waypoints = self._select_optimal_waypoints(start, end, intents, weights)
        reasoning = self._generate_ai_reasoning(command, intents, travel_style)
        highlights = self._create_travel_highlights(intents, waypoints)
        estimated_time = self._estimate_journey_time(start, end, waypoints, travel_style)
        satisfaction_score = self._calculate_satisfaction_score(intents, waypoints, weights)
        
        route_plan = {
            "start_location": start, "end_location": end, "waypoints": waypoints,
            "travel_style": travel_style, "reasoning": reasoning, "highlights": highlights,
            "estimated_time": estimated_time, "satisfaction_score": satisfaction_score,
            "preference_weights": weights
        }
        
        self.conversation_history.append({
            "timestamp": datetime.now(), "user_command": command,
            "stt_result": stt_result, "route_plan": route_plan
        })
        
        return route_plan
    
    def _analyze_travel_style(self, intents: List[str], command: str) -> str:
        if "여유" in intents: return "여유로운 힐링 여행"
        if "빠른" in intents: return "효율적인 일정 소화"
        if "사진" in intents: return "SNS 인증샷 여행"
        if "맛집" in intents: return "제주 미식 탐방"
        if "경치" in intents: return "자연 경관 감상"
        if "문화" in intents: return "문화 체험 중심"
        return "균형잡힌 제주 탐방"
    
    def _calculate_preference_weights(self, intents: List[str]) -> Dict:
        weights = {"scenery": 0.4, "efficiency": 0.3, "food": 0.3, "photo": 0.2, "culture": 0.2, "relaxation": 0.3}
        if "경치" in intents: weights["scenery"] = 1.0
        if "빠른" in intents: weights["efficiency"] = 1.0
        if "맛집" in intents: weights["food"] = 0.9
        if "사진" in intents: weights["photo"] = 0.9
        if "문화" in intents: weights["culture"] = 0.8
        if "여유" in intents: weights["relaxation"] = 0.9
        return weights
    
    def _select_optimal_waypoints(self, start: str, end: str, intents: List[str], weights: Dict) -> List[Dict]:
        all_pois = self.db.get_all_pois()
        candidate_pois = []
        for name, poi in all_pois.items():
            if name == start or name == end: continue
            poi_intents = []
            if poi['category'] in ['관광명소', '핫플레이스']:
                if poi['type'] in ['자연경관', '해수욕장', '섬여행']: poi_intents.append('경치')
                if poi['type'] in ['카페문화']: poi_intents.append('사진')
                if poi['type'] in ['문화체험']: poi_intents.append('문화')
            if poi['category'] == '맛집': poi_intents.append('맛집')
            if any(intent in intents for intent in poi_intents):
                candidate_pois.append(poi)

        for poi in candidate_pois:
            score = poi.get('rating', 3.0)
            if '경치' in intents and poi.get('type') == '자연경관': score *= (1 + weights['scenery'])
            if '맛집' in intents and poi.get('category') == '맛집': score *= (1 + weights['food'])
            if '사진' in intents and poi.get('type') == '카페문화': score *= (1 + weights['photo'])
            poi['calculated_score'] = score

        candidate_pois.sort(key=lambda x: x.get('calculated_score', 0), reverse=True)
        
        final_waypoints = []
        for poi in candidate_pois[:2]:
            poi_name = [name for name, p in self.db.get_all_pois().items() if p == poi][0]
            final_waypoints.append({
                "name": poi_name,
                "coords": poi['coordinates'],
                "score": poi['rating'],
                "description": poi['description']
            })
        return final_waypoints

    def _generate_ai_reasoning(self, command: str, intents: List[str], travel_style: str) -> str:
        base_reasons = {
            "경치": "제주의 아름다운 자연 경관을 만끽할 수 있도록", "맛집": "제주만의 특별한 미식 경험을 위해",
            "사진": "SNS에 올릴 만한 인생샷을 남기기 위해", "여유": "바쁜 일상을 벗어나 힐링할 수 있도록",
            "빠른": "한정된 시간을 효율적으로 활용하기 위해", "문화": "제주의 역사와 문화를 깊이 있게 체험하기 위해"
        }
        primary_intent = intents[0] if intents and intents[0] != "일반" else "경치"
        base_reason = base_reasons.get(primary_intent, "제주도의 매력을 다양하게 경험하기 위해")
        return "{} 맞춤형 {} 경로를 계획했습니다".format(base_reason, travel_style)

    def _create_travel_highlights(self, intents: List[str], waypoints: List[Dict]) -> List[str]:
        highlights = []
        if "경치" in intents: highlights.append("🌊 제주 바다의 에메랄드빛 절경 감상")
        if "맛집" in intents: highlights.append("🍖 제주 흑돼지와 신선한 해산물 맛보기")
        if "사진" in intents: highlights.append("📸 인스타그래머블한 포토존에서 인생샷 촬영")
        if "문화" in intents: highlights.append("🏛️ 제주의 깊은 역사와 전통문화 체험")
        if "여유" in intents: highlights.append("🌺 제주의 여유로운 분위기 속에서 힐링")
        for wp in waypoints:
            highlights.append("✨ {}: {}".format(wp['name'], wp['description']))
        return highlights[:5]

    def _estimate_journey_time(self, start: str, end: str, waypoints: List[Dict], travel_style: str) -> float:
        base_time = 1.5
        waypoint_time = len(waypoints) * 0.5
        style_multiplier = {"여유로운 힐링 여행": 1.5, "효율적인 일정 소화": 0.8, "SNS 인증샷 여행": 1.3, "제주 미식 탐방": 1.4, "자연 경관 감상": 1.2, "문화 체험 중심": 1.3}.get(travel_style, 1.0)
        return (base_time + waypoint_time) * style_multiplier

    def _calculate_satisfaction_score(self, intents: List[str], waypoints: List[Dict], weights: Dict) -> float:
        if not waypoints: return 5.0
        total_score = sum(wp.get('score', 3.0) for wp in waypoints)
        average_score = total_score / len(waypoints) * 2
        return min(average_score, 10.0)

class InteractiveNavigator:
    def __init__(self, db_path='jeju_database.json'):
        self.db = JejuDatabase(db_path)
        self.stt = InteractiveSTT(self.db)
        self.llm = InteractiveLLM(self.db)
        
    def execute_route(self, route_plan: Dict) -> Dict:
        print("🗺️  경로 계산을 시작합니다...")
        start_poi = self.db.get_poi(route_plan["start_location"])
        end_poi = self.db.get_poi(route_plan["end_location"])

        if not start_poi or not end_poi:
            return {"error": "출발지 또는 목적지 정보를 찾을 수 없습니다."}

        start_coords = start_poi['coordinates']
        end_coords = end_poi['coordinates']
        
        travel_style = route_plan.get("travel_style", "")
        is_scenic_route = "경관" in travel_style or "힐링" in travel_style or "해안" in travel_style

        if is_scenic_route:
            print("   🌊 해안도로 우선 경로로 계획합니다!")
            osrm_route = self._get_scenic_coastal_route(start_coords, end_coords, route_plan)
        else:
            print("   🚗 최적 경로로 계획합니다!")
            osrm_route = self._get_osrm_route(start_coords, end_coords)
        
        if osrm_route:
            final_route = {**osrm_route, "llm_plan": route_plan, "voice_guidance": self._generate_voice_guidance(route_plan)}
            return final_route
        else:
            return {"error": "경로 계산에 실패했습니다"}
    
    def _get_scenic_coastal_route(self, start: List[float], end: List[float], route_plan: Dict) -> Optional[Dict]:
        print("   🌊 해안도로 경유지를 추가하여 경로를 계산 중...")
        all_pois = self.db.get_all_pois()
        coastal_waypoints_info = [poi for poi in all_pois.values() if poi.get('road_type') == '해안도로' or '해안' in poi.get('type', '')]
        coastal_waypoints_info.sort(key=lambda p: (-p['coordinates'][1], p['coordinates'][0]))
        coastal_waypoints = [p['coordinates'] for p in coastal_waypoints_info]

        def find_nearest_coastal_point(coords):
            min_dist = float('inf')
            nearest_point = None
            for point in coastal_waypoints:
                dist = math.sqrt((coords[0] - point[0])**2 + (coords[1] - point[1])**2)
                if dist < min_dist:
                    min_dist = dist
                    nearest_point = point
            return nearest_point

        start_coastal = find_nearest_coastal_point(start)
        end_coastal = find_nearest_coastal_point(end)
        start_idx = coastal_waypoints.index(start_coastal)
        end_idx = coastal_waypoints.index(end_coastal)
        
        if start_idx <= end_idx:
            selected_waypoints = coastal_waypoints[start_idx:end_idx+1]
        else:
            selected_waypoints = coastal_waypoints[start_idx:] + coastal_waypoints[:end_idx+1]
        
        if len(selected_waypoints) > 4:
            step = len(selected_waypoints) // 4
            selected_waypoints = [selected_waypoints[i] for i in range(0, len(selected_waypoints), step)][:4]
        
        final_waypoint_coords = [start] + [wp['coords'] for wp in route_plan.get('waypoints', [])] + [end]
        
        print("   📍 해안도로 경유지 포함 {}개 지점으로 경로 탐색".format(len(final_waypoint_coords)))
        return self._get_osrm_route_with_waypoints(final_waypoint_coords)
    
    def _get_osrm_route_with_waypoints(self, waypoints: List[List[float]]) -> Optional[Dict]:
        if len(waypoints) < 2: return None
        coordinates_str = ";".join([f"{wp[0]},{wp[1]}" for wp in waypoints])
        osrm_url = f"http://router.project-osrm.org/route/v1/driving/{coordinates_str}"
        params = {'overview': 'full', 'geometries': 'geojson', 'steps': 'true'}
        
        try:
            response = requests.get(osrm_url, params=params, timeout=15)
            data = response.json()
            if data['code'] == 'Ok':
                print("   ✅ 경로 계산 완료!")
                return data['routes'][0]
            else:
                print("   ⚠️ 경로 계산 실패, 기본 경로로 재시도")
                return self._get_osrm_route(waypoints[0], waypoints[-1])
        except Exception as e:
            print("   ⚠️ OSRM 에러: {}, 기본 경로로 재시도".format(e))
            return self._get_osrm_route(waypoints[0], waypoints[-1])

    def _get_osrm_route(self, start: List[float], end: List[float]) -> Optional[Dict]:
        return self._get_osrm_route_with_waypoints([start, end])
    
    def _generate_voice_guidance(self, route_plan: Dict) -> List[str]:
        guidance = []
        reasoning = route_plan["reasoning"]
        guidance.append("🎯 {}".format(reasoning))
        distance_info = "📍 {}에서 {}까지".format(route_plan['start_location'], route_plan['end_location'])
        time_info = "⏱️ 예상 소요시간 {:.1f}시간".format(route_plan['estimated_time'])
        guidance.append("{}, {}".format(distance_info, time_info))
        waypoints = route_plan["waypoints"]
        if waypoints:
            guidance.append("🎯 추천 경유지: {}".format(', '.join([wp['name'] for wp in waypoints])))
        for highlight in route_plan["highlights"][:3]:
            guidance.append("✨ {}".format(highlight))
        score = route_plan["satisfaction_score"]
        guidance.append("🎵 이 경로의 예상 만족도는 {:.1f}/10점입니다!".format(score))
        return guidance

def create_interactive_map(route_data: Dict, db: JejuDatabase, filename: str = None) -> str:
    if "error" in route_data:
        print("❌ 지도 생성 실패: {}".format(route_data['error']))
        return ""
    
    if not filename:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = "jeju_navigation_{}.html".format(timestamp)
    
    m = folium.Map(location=[33.3617, 126.5312], zoom_start=10, tiles='OpenStreetMap')
    
    if 'geometry' in route_data:
        coordinates = route_data['geometry']['coordinates']
        folium_coords = [[coord[1], coord[0]] for coord in coordinates]
        llm_plan = route_data.get("llm_plan", {})
        travel_style = llm_plan.get("travel_style", "")
        is_coastal = any(keyword in travel_style for keyword in ["경관", "힐링", "해안", "경치"])
        route_color = '#00CED1' if is_coastal else 'blue'
        route_weight = 8 if is_coastal else 6
        route_popup = "🌊 해안도로: {:.1f}km".format(route_data.get('distance', 0)/1000) if is_coastal else "🚗 최적경로: {:.1f}km".format(route_data.get('distance', 0)/1000)
        folium.PolyLine(folium_coords, weight=route_weight, color=route_color, opacity=0.9, popup=route_popup).add_to(m)
    
    llm_plan = route_data.get("llm_plan", {})
    
    start_name = llm_plan.get("start_location", "출발지")
    start_poi = db.get_poi(start_name)
    if start_poi:
        folium.Marker([start_poi['coordinates'][1], start_poi['coordinates'][0]], popup="🚀 출발: {}".format(start_name), icon=folium.Icon(color='green', icon='play')).add_to(m)
    
    end_name = llm_plan.get("end_location", "목적지")
    end_poi = db.get_poi(end_name)
    if end_poi:
        folium.Marker([end_poi['coordinates'][1], end_poi['coordinates'][0]], popup="🏁 도착: {}".format(end_name), icon=folium.Icon(color='red', icon='stop')).add_to(m)
    
    waypoints = llm_plan.get("waypoints", [])
    for i, wp in enumerate(waypoints, 1):
        wp_poi = db.get_poi(wp['name'])
        if not wp_poi: continue
        
        wp_type = wp_poi.get("type", "general")
        type_config = {
            "자연경관": {"color": "lightgreen", "icon": "camera"}, "음식문화": {"color": "orange", "icon": "cutlery"},
            "카페문화": {"color": "pink", "icon": "star"}, "문화체험": {"color": "purple", "icon": "book"},
            "일반": {"color": "lightblue", "icon": "info-sign"}
        }
        config = type_config.get(wp_type, type_config["일반"])
        
        folium.Marker(
            [wp_poi['coordinates'][1], wp_poi['coordinates'][0]],
            popup="<b>🤖 AI 추천 {}번째</b><br><b>{}</b><br>{}<br>평점: {}/10".format(i, wp['name'], wp['description'], wp['score']),
            icon=folium.Icon(color=config["color"], icon=config["icon"])
        ).add_to(m)
    
    travel_style = llm_plan.get("travel_style", "제주 여행")
    reasoning = llm_plan.get("reasoning", "")
    satisfaction = llm_plan.get("satisfaction_score", 0)
    estimated_time = llm_plan.get("estimated_time", 0)
    
    info_html = '''
    <div style="position: fixed; top: 10px; left: 50px; width: 420px; height: 400px; background-color: white; border: 3px solid #4CAF50; z-index: 9999; font-size: 14px; padding: 20px; border-radius: 15px; box-shadow: 0 6px 12px rgba(0,0,0,0.15);">
        <h2 style="color: #4CAF50; margin-top: 0;">🏝️ 제주도 AI 내비게이션</h2>
        <div style="background-color: #f8f9fa; padding: 10px; border-radius: 8px; margin-bottom: 15px;">
            <h4 style="margin: 0; color: #333;">🎯 {travel_style}</h4>
        </div>
        <p><b>🧠 AI 추천 이유:</b><br><span style="color: #666; font-style: italic;">{reasoning}</span></p>
        <div style="display: flex; justify-content: space-between; margin: 15px 0;">
            <div style="text-align: center;">
                <div style="font-size: 24px;">⏱️</div>
                <div><b>{estimated_time:.1f}시간</b></div>
                <div style="font-size: 12px; color: #666;">예상 소요</div>
            </div>
            <div style="text-align: center;">
                <div style="font-size: 24px;">⭐</div>
                <div><b>{satisfaction:.1f}/10</b></div>
                <div style="font-size: 12px; color: #666;">만족도 예측</div>
            </div>
            <div style="text-align: center;">
                <div style="font-size: 24px;">📍</div>
                <div><b>{waypoints_len}개</b></div>
                <div style="font-size: 12px; color: #666;">추천 경유지</div>
            </div>
        </div>
        <div style="background-color: #e8f5e8; padding: 10px; border-radius: 8px; margin-top: 15px;">
            <p style="margin: 0; font-size: 12px; color: #666; text-align: center;">
            💡 실시간 STT → LLM → 경로 생성<br>
            🔄 새로운 명령어로 언제든 재계획 가능
            </p>
        </div>
    </div>
    '''.format(travel_style=travel_style, reasoning=reasoning, estimated_time=estimated_time, satisfaction=satisfaction, waypoints_len=len(waypoints))
    m.get_root().html.add_child(folium.Element(info_html))
    m.save(filename)
    return filename

def main():
    print("🏝️🤖 제주도 AI 인터랙티브 내비게이션 (DB 연동 버전)")
    print("=" * 60)
    
    try:
        navigator = InteractiveNavigator(db_path='/Users/choijaehyeok/Desktop/VISTA/demo/jeju_database.json')
        if not navigator.db.data:
            print("DB 로딩 실패로 프로그램을 종료합니다.")
            return
    except Exception as e:
        print("초기화 실패: {}".format(e))
        return

    print("💬 음성 명령을 텍스트로 입력하세요! (예: '제주공항에서 성산까지 경치 좋은 길로')")
    print("   종료하시려면 'quit' 또는 'exit'을 입력하세요.")
    print("=" * 60)
    
    session_count = 0
    while True:
        try:
            print("\n🎤 [{}번째 여행 계획]".format(session_count + 1))
            user_input = input("👤 여행 명령을 입력하세요: ").strip()
            
            if user_input.lower() in ['quit', 'exit', '종료', '끝']:
                print("👋 제주도 AI 내비게이션을 종료합니다. 안전한 여행 되세요!")
                break
            
            if not user_input:
                print("❌ 명령을 입력해주세요.")
                continue
            
            print("\n" + "="*50)
            
            print("1️⃣ STT 음성 인식 처리...")
            stt_result = navigator.stt.recognize_voice(user_input)
            print("   ✅ 인식된 의도: {}, 출발지: {}, 목적지: {}".format(stt_result['intents'], stt_result['start'], stt_result['end']))
            
            print("\n2️⃣ LLM 여행 계획 수립...")
            route_plan = navigator.llm.analyze_and_plan(stt_result)
            print("   🎯 여행 스타일: {}".format(route_plan['travel_style']))
            print("   📍 추천 경유지: {}".format([wp['name'] for wp in route_plan['waypoints']]))
            
            print("\n3️⃣ 실제 경로 계산 (OSRM)...")
            final_route = navigator.execute_route(route_plan)
            
            if "error" not in final_route:
                print("   ✅ 실제 거리: {:.1f}km, 실제 시간: {:.0f}분".format(final_route.get('distance', 0)/1000, final_route.get('duration', 0)/60))
                
                print("\n4️⃣ 개인화된 음성 안내:")
                for i, guidance in enumerate(final_route.get("voice_guidance", []), 1):
                    print("   🔊 {}. {}".format(i, guidance))
                
                print("\n5️⃣ 인터랙티브 지도 생성...")
                map_filename = create_interactive_map(final_route, navigator.db)
                
                if map_filename:
                    print("   ✅ 지도 저장: {}".format(map_filename))
                    try:
                        file_path = os.path.abspath(map_filename)
                        webbrowser.open("file://" + file_path)
                        print("   🌐 브라우저에서 지도가 열렸습니다!")
                    except Exception as e:
                        print("   ⚠️ 브라우저 열기 실패: {}".format(e))
                
                session_count += 1
            else:
                print("   ❌ 에러: {}".format(final_route['error']))
            
            print("\n" + "="*50)
            
        except KeyboardInterrupt:
            print("\n\n👋 사용자가 중단했습니다. 안전한 여행 되세요!")
            break
        except Exception as e:
            print("\n❌ 예상치 못한 오류가 발생했습니다: {}".format(e))

if __name__ == "__main__":
    main()