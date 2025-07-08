#!/usr/bin/env python3
from jeju_interactive_nav import InteractiveNavigator, create_interactive_map
import webbrowser
import os

def demo_coastal_vs_fast():
    print("🌊 제주도 해안도로 vs 최적 경로 비교 데모")
    print("=" * 60)
    
    navigator = InteractiveNavigator()
    
    # 해안도로 경로 계산
    print("\n1️⃣ 해안도로 경로 (경치 좋은 길)")
    stt_scenic = {
        'command': '제주공항에서 성산일출봉까지 경치 좋은 해안도로로',
        'intents': ['경치'],
        'start': '제주공항',
        'end': '성산일출봉',
        'confidence': 0.9
    }
    
    route_plan_scenic = navigator.llm.analyze_and_plan(stt_scenic)
    final_route_scenic = navigator.execute_route(route_plan_scenic)
    
    if 'error' not in final_route_scenic:
        distance_scenic = final_route_scenic.get('distance', 0) / 1000
        duration_scenic = final_route_scenic.get('duration', 0) / 60
        print(f"   🌊 해안도로: {distance_scenic:.1f}km, {duration_scenic:.0f}분")
        
        # 해안도로 지도 생성
        map_file_scenic = create_interactive_map(final_route_scenic, "jeju_coastal_route.html")
        print(f"   💾 해안도로 지도: {map_file_scenic}")
    
    # 최적 경로 계산
    print("\n2️⃣ 최적 경로 (빠른 길)")
    stt_fast = {
        'command': '제주공항에서 성산일출봉까지 빨리',
        'intents': ['빠른'],
        'start': '제주공항',
        'end': '성산일출봉',
        'confidence': 0.9
    }
    
    route_plan_fast = navigator.llm.analyze_and_plan(stt_fast)
    final_route_fast = navigator.execute_route(route_plan_fast)
    
    if 'error' not in final_route_fast:
        distance_fast = final_route_fast.get('distance', 0) / 1000
        duration_fast = final_route_fast.get('duration', 0) / 60
        print(f"   🚗 최적경로: {distance_fast:.1f}km, {duration_fast:.0f}분")
        
        # 최적 경로 지도 생성
        map_file_fast = create_interactive_map(final_route_fast, "jeju_optimal_route.html")
        print(f"   💾 최적경로 지도: {map_file_fast}")
    
    # 비교 결과
    print("\n📊 경로 비교 결과")
    print("-" * 40)
    if 'error' not in final_route_scenic and 'error' not in final_route_fast:
        time_diff = duration_scenic - duration_fast
        distance_diff = distance_scenic - distance_fast
        
        print(f"🌊 해안도로:  {distance_scenic:.1f}km, {duration_scenic:.0f}분")
        print(f"🚗 최적경로:  {distance_fast:.1f}km, {duration_fast:.0f}분")
        print(f"📈 차이:      +{distance_diff:.1f}km, +{time_diff:.0f}분")
        print(f"💰 해안도로는 {time_diff/60:.1f}시간 더 걸리지만")
        print(f"   🌊 제주 바다의 절경을 만끽할 수 있습니다!")
        
        # 브라우저에서 해안도로 지도 열기
        try:
            file_path = os.path.abspath("jeju_coastal_route.html")
            webbrowser.open(f"file://{file_path}")
            print(f"\n🌐 브라우저에서 해안도로 지도가 열렸습니다!")
        except Exception as e:
            print(f"\n⚠️ 브라우저 열기 실패: {e}")

if __name__ == "__main__":
    demo_coastal_vs_fast() 