#!/usr/bin/env python3
from jeju_interactive_nav import InteractiveNavigator

def test_coastal_route():
    print("🧪 제주도 해안도로 경로 테스트")
    print("=" * 50)
    
    navigator = InteractiveNavigator()
    
    # 테스트 케이스 1: 경치 좋은 길
    print("\n🎬 테스트 1: 제주공항에서 성산일출봉까지 경치 좋은 길로")
    stt_result = {
        'command': '제주공항에서 성산일출봉까지 경치 좋은 길로',
        'intents': ['경치'],
        'start': '제주공항',
        'end': '성산일출봉',
        'confidence': 0.9
    }
    
    print(f"🎤 입력: {stt_result['command']}")
    route_plan = navigator.llm.analyze_and_plan(stt_result)
    print(f"🎯 여행 스타일: {route_plan['travel_style']}")
    
    final_route = navigator.execute_route(route_plan)
    if 'error' not in final_route:
        distance = final_route.get('distance', 0) / 1000
        duration = final_route.get('duration', 0) / 60
        print(f"✅ 해안도로 경로: {distance:.1f}km, {duration:.0f}분")
    else:
        print(f"❌ 에러: {final_route['error']}")
    
    # 테스트 케이스 2: 빠른 길
    print("\n🎬 테스트 2: 제주공항에서 성산일출봉까지 빨리")
    stt_result2 = {
        'command': '제주공항에서 성산일출봉까지 빨리',
        'intents': ['빠른'],
        'start': '제주공항',
        'end': '성산일출봉',
        'confidence': 0.9
    }
    
    print(f"🎤 입력: {stt_result2['command']}")
    route_plan2 = navigator.llm.analyze_and_plan(stt_result2)
    print(f"🎯 여행 스타일: {route_plan2['travel_style']}")
    
    final_route2 = navigator.execute_route(route_plan2)
    if 'error' not in final_route2:
        distance2 = final_route2.get('distance', 0) / 1000
        duration2 = final_route2.get('duration', 0) / 60
        print(f"✅ 최적 경로: {distance2:.1f}km, {duration2:.0f}분")
    else:
        print(f"❌ 에러: {final_route2['error']}")

if __name__ == "__main__":
    test_coastal_route() 