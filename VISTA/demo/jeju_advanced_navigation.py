import json
import requests
import folium
import math
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional

class JejuTourismDatabase:
    """제주도 관광 특화 데이터베이스"""
    
    def __init__(self):
        self.poi_data = self._initialize_poi_data()
        self.road_labels = self._initialize_road_labels()
        self.voice_landmarks = self._initialize_voice_landmarks()
        
    def _initialize_poi_data(self) -> Dict:
        """제주도 주요 POI 데이터 초기화"""
        return {
            "관광명소": {
                "성산일출봉": {
                    "coordinates": [126.9423, 33.4586],
                    "type": "자연경관",
                    "best_time": "일출",
                    "scenery_score": 10.0,
                    "voice_keywords": ["성산일출봉", "성산", "일출봉", "썽산"],
                    "description": "유네스코 세계자연유산, 일출 명소",
                    "visit_duration": 90  # 분
                },
                "한라산": {
                    "coordinates": [126.5311, 33.3617],
                    "type": "자연경관",
                    "best_time": "오전",
                    "scenery_score": 10.0,
                    "voice_keywords": ["한라산", "할라산", "한라"],
                    "description": "제주도 최고봉, 등산 명소",
                    "visit_duration": 480  # 8시간
                },
                "우도": {
                    "coordinates": [126.9513, 33.5069],
                    "type": "섬여행",
                    "best_time": "하루종일",
                    "scenery_score": 9.5,
                    "voice_keywords": ["우도", "소섬", "우도섬"],
                    "description": "제주 대표 부속섬, 해양 관광",
                    "visit_duration": 300  # 5시간
                },
                "애월카페거리": {
                    "coordinates": [126.3094, 33.4647],
                    "type": "카페문화",
                    "best_time": "오후",
                    "scenery_score": 8.5,
                    "voice_keywords": ["애월", "애월카페", "GD카페"],
                    "description": "해안 카페 거리, 인스타 핫플",
                    "visit_duration": 120
                },
                "협재해수욕장": {
                    "coordinates": [126.2397, 33.3948],
                    "type": "해수욕장",
                    "best_time": "여름",
                    "scenery_score": 9.0,
                    "voice_keywords": ["협재", "협재바다", "협재해변"],
                    "description": "에메랄드빛 바다, 해수욕",
                    "visit_duration": 180
                }
            },
            "맛집": {
                "흑돼지거리": {
                    "coordinates": [126.5219, 33.4996],
                    "type": "음식문화",
                    "best_time": "저녁",
                    "voice_keywords": ["흑돼지", "고기집", "돼지고기"],
                    "description": "제주 흑돼지 전문 거리"
                },
                "동문시장": {
                    "coordinates": [126.5258, 33.5145],
                    "type": "전통시장",
                    "best_time": "오전",
                    "voice_keywords": ["동문시장", "시장", "전통시장"],
                    "description": "제주 전통 음식과 특산물"
                }
            }
        }
    
    def _initialize_road_labels(self) -> Dict:
        """도로별 특성 라벨링"""
        return {
            "1132번도로": {  # 해안도로
                "road_type": "해안도로",
                "scenery_score": 9.8,
                "tourism_priority": "최우선",
                "congestion_pattern": {
                    "peak_months": [7, 8, 10],
                    "peak_hours": ["09:00-11:00", "15:00-17:00"]
                },
                "features": ["바다전망", "카페거리", "사진스팟"],
                "weather_sensitivity": "높음",  # 바람 영향
                "recommended_speed": "느림"  # 경치 감상
            },
            "516번도로": {  # 한라산 관통도로
                "road_type": "산악도로",
                "scenery_score": 9.5,
                "tourism_priority": "높음",
                "features": ["한라산뷰", "단풍길", "구름바다"],
                "weather_sensitivity": "매우높음",  # 안개, 눈
                "elevation_change": "대",
                "recommended_speed": "보통"
            },
            "일주도로": {
                "road_type": "순환도로",
                "scenery_score": 8.0,
                "tourism_priority": "보통",
                "features": ["제주일주", "다양한테마"],
                "weather_sensitivity": "보통",
                "recommended_speed": "보통"
            }
        }
    
    def _initialize_voice_landmarks(self) -> Dict:
        """음성 인식용 랜드마크 데이터"""
        return {
            "방향": {
                "북쪽": ["제주공항", "제주시", "애월", "한림"],
                "남쪽": ["서귀포", "중문", "성산"],
                "서쪽": ["한림", "협재", "애월"],
                "동쪽": ["성산", "우도", "표선"]
            },
            "테마": {
                "바다": ["협재", "애월", "함덕", "김녕"],
                "카페": ["애월", "성산", "우도"],
                "관광지": ["성산일출봉", "한라산", "천지연폭포"],
                "맛집": ["흑돼지거리", "동문시장", "서귀포매일올레시장"]
            }
        }

class JejuNavigationSystem:
    """제주도 특화 내비게이션 시스템"""
    
    def __init__(self):
        self.db = JejuTourismDatabase()
        self.current_weather = "맑음"
        self.current_time = datetime.now()
        
    def calculate_scenic_route(self, start: List[float], end: List[float], 
                             preferences: Dict = None) -> Dict:
        """경치 좋은 경로 계산 (관광 특화)"""
        
        # 기본 OSRM 경로 조회
        base_route = self._get_osrm_route(start, end)
        if not base_route:
            return None
            
        # 제주도 특화 라벨링 적용
        enhanced_route = self._apply_jeju_labeling(base_route, preferences)
        
        return enhanced_route
    
    def _get_osrm_route(self, start: List[float], end: List[float]) -> Dict:
        """OSRM 기본 경로 조회"""
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
    
    def _apply_jeju_labeling(self, route: Dict, preferences: Dict = None) -> Dict:
        """제주도 특화 라벨링 적용"""
        
        if not preferences:
            preferences = {"priority": "scenic", "pace": "leisurely"}
        
        # 경로상 POI 식별
        route_pois = self._identify_route_pois(route['geometry']['coordinates'])
        
        # 경치 점수 계산
        scenery_score = self._calculate_route_scenery_score(route['geometry']['coordinates'])
        
        # 여행자 맞춤 정보 추가
        enhanced_route = {
            **route,
            "jeju_features": {
                "total_scenery_score": scenery_score,
                "route_pois": route_pois,
                "best_photo_spots": self._find_photo_spots(route['geometry']['coordinates']),
                "weather_advisory": self._get_weather_advisory(),
                "time_recommendations": self._get_time_recommendations(route_pois),
                "voice_navigation": self._generate_voice_navigation(route, route_pois)
            }
        }
        
        return enhanced_route
    
    def _identify_route_pois(self, coordinates: List[List[float]]) -> List[Dict]:
        """경로상 POI 식별"""
        route_pois = []
        
        for category, pois in self.db.poi_data.items():
            for poi_name, poi_info in pois.items():
                poi_coord = poi_info['coordinates']
                
                # 경로에서 POI까지의 최단거리 계산
                min_distance = min([
                    self._calculate_distance(coord, poi_coord) 
                    for coord in coordinates[::20]  # 20개마다 샘플링
                ])
                
                # 5km 이내면 경로상 POI로 판단 (제주도는 작은 섬이므로)
                if min_distance < 5.0:
                    route_pois.append({
                        "name": poi_name,
                        "category": category,
                        "distance_from_route": min_distance,
                        "info": poi_info
                    })
        
        return sorted(route_pois, key=lambda x: x['distance_from_route'])
    
    def _calculate_distance(self, coord1: List[float], coord2: List[float]) -> float:
        """두 좌표간 거리 계산 (km)"""
        lon1, lat1 = coord1
        lon2, lat2 = coord2
        
        # 하버사인 공식
        R = 6371  # 지구 반지름 (km)
        dLat = math.radians(lat2 - lat1)
        dLon = math.radians(lon2 - lon1)
        
        a = (math.sin(dLat/2) * math.sin(dLat/2) + 
             math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * 
             math.sin(dLon/2) * math.sin(dLon/2))
        
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        return R * c
    
    def _calculate_route_scenery_score(self, coordinates: List[List[float]]) -> float:
        """경로 전체 경치 점수 계산"""
        total_score = 0
        sample_points = coordinates[::30]  # 샘플링
        
        for coord in sample_points:
            # 해안선 근접도 (제주도는 해안 경치가 중요)
            coast_score = self._get_coast_proximity_score(coord)
            
            # 한라산 조망 점수
            hallasan_view_score = self._get_hallasan_view_score(coord)
            
            point_score = (coast_score + hallasan_view_score) / 2
            total_score += point_score
        
        return total_score / len(sample_points) if sample_points else 0
    
    def _get_coast_proximity_score(self, coord: List[float]) -> float:
        """해안선 근접도 점수 (0-10)"""
        # 제주도 중심에서의 거리로 근사 계산
        jeju_center = [126.5312, 33.3617]
        distance_from_center = self._calculate_distance(coord, jeju_center)
        
        # 중심에서 멀수록 (해안에 가까울수록) 높은 점수
        if distance_from_center > 15:  # 해안 근처
            return 9.5
        elif distance_from_center > 10:
            return 7.5
        elif distance_from_center > 5:
            return 5.5
        else:
            return 4.0
    
    def _get_hallasan_view_score(self, coord: List[float]) -> float:
        """한라산 조망 점수"""
        hallasan_coord = [126.5311, 33.3617]
        distance = self._calculate_distance(coord, hallasan_coord)
        
        # 한라산에서 적절한 거리일 때 높은 점수
        if 5 <= distance <= 20:
            return 8.5
        elif distance < 5:
            return 7.0
        else:
            return 5.0
    
    def _find_photo_spots(self, coordinates: List[List[float]]) -> List[Dict]:
        """사진 스팟 추천"""
        photo_spots = []
        
        # 경치 점수가 높은 지점들을 사진 스팟으로 추천
        for i, coord in enumerate(coordinates[::50]):  # 50개마다 샘플링
            coast_score = self._get_coast_proximity_score(coord)
            hallasan_score = self._get_hallasan_view_score(coord)
            total_score = (coast_score + hallasan_score) / 2
            
            if total_score > 7.5:
                photo_spots.append({
                    "coordinates": coord,
                    "scenery_score": total_score,
                    "description": "해안 전망 포인트" if coast_score > hallasan_score else "한라산 조망 포인트"
                })
        
        return photo_spots[:5]  # 상위 5개
    
    def _get_weather_advisory(self) -> Dict:
        """날씨 기반 조언"""
        return {
            "current_weather": self.current_weather,
            "advisory": "맑은 날씨로 해안도로 드라이브에 최적입니다",
            "visibility": "양호",
            "wind_warning": False
        }
    
    def _get_time_recommendations(self, route_pois: List[Dict]) -> Dict:
        """시간대별 추천"""
        current_hour = self.current_time.hour
        
        recommendations = {
            "current_time": self.current_time.strftime("%H:%M"),
            "suggestions": []
        }
        
        if 5 <= current_hour <= 7:
            recommendations["suggestions"].append("일출 감상하기 좋은 시간입니다")
        elif 17 <= current_hour <= 19:
            recommendations["suggestions"].append("일몰 감상하기 좋은 시간입니다")
        elif 10 <= current_hour <= 16:
            recommendations["suggestions"].append("관광지 방문하기 좋은 시간입니다")
        
        return recommendations
    
    def _generate_voice_navigation(self, route: Dict, route_pois: List[Dict]) -> List[str]:
        """제주도 특화 음성 안내 생성"""
        navigation_messages = []
        
        # 출발 안내
        navigation_messages.append("제주도 여행을 시작합니다. 아름다운 경치를 감상하며 안전하게 이동하겠습니다.")
        
        # POI 기반 안내
        for poi in route_pois[:3]:  # 주요 3개 POI
            poi_name = poi['name']
            poi_category = poi['category']
            
            if poi_category == "관광명소":
                message = f"{poi_name} 근처를 지나갑니다. "
                if poi['info'].get('best_time'):
                    message += f"{poi['info']['best_time']}에 방문하시면 더욱 좋습니다."
                navigation_messages.append(message)
            
            elif poi_category == "맛집":
                navigation_messages.append(f"맛집이 많은 {poi_name} 지역입니다. 제주 특산 음식을 즐겨보세요.")
        
        # 도착 안내
        navigation_messages.append("목적지에 도착했습니다. 제주도 여행을 즐기세요!")
        
        return navigation_messages

def create_enhanced_visualization(route_data: Dict, output_file: str = "jeju_enhanced_navigation.html"):
    """강화된 지도 시각화"""
    
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
        weight=4,
        color='blue',
        opacity=0.8,
        popup=f"총 거리: {route_data['distance']/1000:.1f}km"
    ).add_to(m)
    
    # 제주도 특화 정보 표시
    jeju_features = route_data.get('jeju_features', {})
    
    # POI 마커 추가
    for poi in jeju_features.get('route_pois', []):
        poi_coord = poi['info']['coordinates']
        
        # POI 타입별 아이콘 설정
        if poi['category'] == '관광명소':
            icon_color = 'red'
            icon = 'star'
        elif poi['category'] == '맛집':
            icon_color = 'orange' 
            icon = 'cutlery'
        else:
            icon_color = 'blue'
            icon = 'info-sign'
        
        folium.Marker(
            [poi_coord[1], poi_coord[0]],
            popup=f"""
            <b>{poi['name']}</b><br>
            분류: {poi['category']}<br>
            설명: {poi['info'].get('description', '')}<br>
            경치점수: {poi['info'].get('scenery_score', 0)}/10
            """,
            icon=folium.Icon(color=icon_color, icon=icon)
        ).add_to(m)
    
    # 사진 스팟 표시
    for i, spot in enumerate(jeju_features.get('best_photo_spots', [])):
        folium.CircleMarker(
            [spot['coordinates'][1], spot['coordinates'][0]],
            radius=8,
            popup=f"📸 사진스팟 {i+1}<br>경치점수: {spot['scenery_score']:.1f}",
            color='yellow',
            fill=True,
            fillColor='yellow'
        ).add_to(m)
    
    # 정보 패널 추가
    info_html = f"""
    <div style="position: fixed; 
                top: 10px; left: 50px; width: 300px; height: 200px; 
                background-color: white; border:2px solid grey; z-index:9999; 
                font-size:14px; padding: 10px">
    <h4>🏝️ 제주도 특화 내비게이션</h4>
    <p><b>경치 점수:</b> {jeju_features.get('total_scenery_score', 0):.1f}/10</p>
    <p><b>경로상 관광지:</b> {len(jeju_features.get('route_pois', []))}개</p>
    <p><b>사진 스팟:</b> {len(jeju_features.get('best_photo_spots', []))}개</p>
    <p><b>날씨:</b> {jeju_features.get('weather_advisory', {}).get('current_weather', '정보없음')}</p>
    </div>
    """
    m.get_root().html.add_child(folium.Element(info_html))
    
    # 지도 저장
    m.save(output_file)
    print(f"강화된 지도가 '{output_file}'로 저장되었습니다!")

def main():
    """메인 실행 함수"""
    print("🏝️ 제주도 특화 내비게이션 시스템 (라벨링 적용)")
    
    # 내비게이션 시스템 초기화
    nav_system = JejuNavigationSystem()
    
    # 테스트 경로: 제주공항 → 성산일출봉
    start_coords = [126.4930, 33.5107]  # 제주공항
    end_coords = [126.9423, 33.4586]    # 성산일출봉
    
    print(f"\n📍 경로 계산: 제주공항 → 성산일출봉")
    print("제주도 특화 라벨링 적용 중...")
    
    # 경치 좋은 경로 계산
    preferences = {
        "priority": "scenic",
        "pace": "leisurely",
        "interests": ["자연경관", "사진스팟"]
    }
    
    enhanced_route = nav_system.calculate_scenic_route(start_coords, end_coords, preferences)
    
    if enhanced_route:
        jeju_features = enhanced_route['jeju_features']
        
        print(f"\n✅ 경로 계산 완료!")
        print(f"📏 총 거리: {enhanced_route['distance']/1000:.1f} km")
        print(f"⏱️ 예상 시간: {enhanced_route['duration']/60:.0f} 분")
        print(f"🌅 경치 점수: {jeju_features['total_scenery_score']:.1f}/10")
        print(f"📍 경로상 관광지: {len(jeju_features['route_pois'])}개")
        print(f"📸 추천 사진스팟: {len(jeju_features['best_photo_spots'])}개")
        
        # 발견된 POI 출력
        print(f"\n🎯 경로상 주요 관광지:")
        for poi in jeju_features['route_pois']:
            print(f"  • {poi['name']} ({poi['category']}) - 경로에서 {poi['distance_from_route']:.1f}km")
        
        # 음성 안내 출력
        print(f"\n🔊 음성 안내 메시지:")
        for i, message in enumerate(jeju_features['voice_navigation'], 1):
            print(f"  {i}. {message}")
        
        # 시간 추천
        time_rec = jeju_features['time_recommendations']
        print(f"\n⏰ 시간 추천:")
        print(f"  현재 시간: {time_rec['current_time']}")
        for suggestion in time_rec['suggestions']:
            print(f"  • {suggestion}")
        
        # 지도 시각화
        create_enhanced_visualization(enhanced_route)
        
    else:
        print("❌ 경로 계산 실패")

if __name__ == "__main__":
    main() 