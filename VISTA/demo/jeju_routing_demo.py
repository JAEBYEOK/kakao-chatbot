import json
import requests
import folium

def test_jeju_routing():
    """제주도 OSRM 라우팅 테스트"""
    
    # 제주공항 좌표
    jeju_airport = [126.4930, 33.5107]
    
    # 애월해안도로 (애월읍) 좌표  
    aewol_coast = [126.2394, 33.3895]
    
    # OSRM API 호출
    osrm_url = f"http://router.project-osrm.org/route/v1/driving/{jeju_airport[0]},{jeju_airport[1]};{aewol_coast[0]},{aewol_coast[1]}"
    params = {
        'overview': 'full',
        'geometries': 'geojson',
        'steps': 'true'
    }
    
    try:
        response = requests.get(osrm_url, params=params)
        data = response.json()
        
        if data['code'] == 'Ok':
            route = data['routes'][0]
            
            print("=== 제주공항 → 애월해안도로 경로 정보 ===")
            print(f"총 거리: {route['distance']/1000:.1f} km")
            print(f"예상 시간: {route['duration']/60:.0f} 분")
            print(f"경로 좌표 수: {len(route['geometry']['coordinates'])}")
            
            # 지도 생성
            m = folium.Map(
                location=[33.45, 126.35],  # 제주도 중심
                zoom_start=10,
                tiles='OpenStreetMap'
            )
            
            # 출발지 마커
            folium.Marker(
                [jeju_airport[1], jeju_airport[0]],
                popup="제주공항",
                icon=folium.Icon(color='green', icon='plane')
            ).add_to(m)
            
            # 도착지 마커  
            folium.Marker(
                [aewol_coast[1], aewol_coast[0]],
                popup="애월해안도로",
                icon=folium.Icon(color='red', icon='car')
            ).add_to(m)
            
            # 경로 표시
            coordinates = route['geometry']['coordinates']
            # 좌표 순서를 [lat, lon]으로 변경
            folium_coords = [[coord[1], coord[0]] for coord in coordinates]
            
            folium.PolyLine(
                folium_coords,
                weight=5,
                color='blue',
                opacity=0.7,
                popup=f"거리: {route['distance']/1000:.1f}km, 시간: {route['duration']/60:.0f}분"
            ).add_to(m)
            
            # 지도 저장
            m.save('jeju_routing_demo.html')
            print("\n지도가 'jeju_routing_demo.html'로 저장되었습니다!")
            
            return route
            
    except Exception as e:
        print(f"에러 발생: {e}")
        return None

def analyze_route_for_stt_navigation(route_data):
    """STT 내비게이션을 위한 경로 분석"""
    
    if not route_data:
        return
        
    print("\n=== STT 내비게이션 특화 분석 ===")
    
    # 주요 경유 포인트 추출 (간단한 예시)
    coordinates = route_data['geometry']['coordinates']
    total_points = len(coordinates)
    
    # 경로를 4등분하여 주요 지점 추출
    key_points = []
    for i in [0, total_points//4, total_points//2, 3*total_points//4, -1]:
        coord = coordinates[i]
        key_points.append([coord[1], coord[0]])  # [lat, lon]
    
    print("주요 경유 지점 좌표:")
    locations = ["제주공항", "1/4 지점", "중간 지점", "3/4 지점", "애월해안도로"]
    for i, (point, name) in enumerate(zip(key_points, locations)):
        print(f"{i+1}. {name}: 위도 {point[0]:.4f}, 경도 {point[1]:.4f}")
    
    # 여행자 맞춤 음성 안내 예시
    print("\n=== 여행자 맞춤 음성 안내 예시 ===")
    navigation_messages = [
        "제주공항에서 출발합니다. 서쪽 해안도로 방향으로 이동하겠습니다.",
        "현재 제주시 중심가를 지나고 있습니다. 좌측으로 한라산이 보입니다.",
        "애월읍에 진입합니다. 유명한 카페들이 많은 지역입니다.",
        "해안도로에 거의 도착했습니다. 아름다운 바다 전망을 감상하세요.",
        "애월해안도로에 도착했습니다. 해변 산책을 즐기세요!"
    ]
    
    for i, message in enumerate(navigation_messages, 1):
        print(f"{i}. {message}")

if __name__ == "__main__":
    # 라우팅 테스트 실행
    route = test_jeju_routing()
    
    # STT 내비게이션 분석
    analyze_route_for_stt_navigation(route)
    
    print("\n=== 추가 개발 고려사항 ===")
    print("1. 제주도 관광지 POI 데이터베이스 연동")
    print("2. 실시간 교통정보 반영")
    print("3. 날씨에 따른 경로 조정")
    print("4. 사용자 음성 명령 처리 ('바다 보이는 길로 가줘')")
    print("5. 제주 사투리 음성 인식 고도화") 