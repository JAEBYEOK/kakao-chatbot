import axios from 'axios';

// VISTA 백엔드 API 베이스 URL (로컬 개발 서버)
const BASE_URL = 'http://localhost:5000/api';

class VistaAPI {
  constructor() {
    this.client = axios.create({
      baseURL: BASE_URL,
      timeout: 10000,
      headers: {
        'Content-Type': 'application/json',
      },
    });
  }

  // 제주도 경로 계산 (기존 VISTA 시스템 연동)
  async calculateRoute(startPoint, endPoint, preferences = {}) {
    try {
      const response = await this.client.post('/route/calculate', {
        start: startPoint,
        end: endPoint,
        preferences: {
          travel_style: preferences.travel_style || 'scenic',
          time_of_day: preferences.time_of_day || 'morning',
          weather: preferences.weather || 'clear',
          ...preferences
        }
      });
      return response.data;
    } catch (error) {
      console.error('Route calculation error:', error);
      throw error;
    }
  }

  // 음성 인식 처리 (STT)
  async processVoiceCommand(audioData) {
    try {
      const formData = new FormData();
      formData.append('audio', audioData);
      
      const response = await this.client.post('/stt/recognize', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      return response.data;
    } catch (error) {
      console.error('Voice recognition error:', error);
      throw error;
    }
  }

  // LLM 기반 여행 계획 생성
  async generateTravelPlan(userQuery, currentLocation = null) {
    try {
      const response = await this.client.post('/llm/travel-plan', {
        query: userQuery,
        current_location: currentLocation,
        context: 'jeju_tourism'
      });
      return response.data;
    } catch (error) {
      console.error('Travel plan generation error:', error);
      throw error;
    }
  }

  // 제주도 POI 검색
  async searchPOI(query, category = null, location = null) {
    try {
      const response = await this.client.get('/poi/search', {
        params: {
          q: query,
          category: category,
          lat: location?.latitude,
          lng: location?.longitude,
        }
      });
      return response.data;
    } catch (error) {
      console.error('POI search error:', error);
      throw error;
    }
  }

  // 추천 여행 코스 가져오기
  async getRecommendedRoutes(userPreferences = {}) {
    try {
      const response = await this.client.get('/recommendations/routes', {
        params: userPreferences
      });
      return response.data;
    } catch (error) {
      console.error('Recommendations error:', error);
      throw error;
    }
  }

  // 실시간 교통 정보
  async getTrafficInfo(routeId) {
    try {
      const response = await this.client.get(`/traffic/route/${routeId}`);
      return response.data;
    } catch (error) {
      console.error('Traffic info error:', error);
      throw error;
    }
  }

  // 날씨 정보
  async getWeatherInfo(location) {
    try {
      const response = await this.client.get('/weather/current', {
        params: {
          lat: location.latitude,
          lng: location.longitude,
        }
      });
      return response.data;
    } catch (error) {
      console.error('Weather info error:', error);
      throw error;
    }
  }

  // 사용자 여행 히스토리 저장
  async saveTravelHistory(travelData) {
    try {
      const response = await this.client.post('/user/travel-history', travelData);
      return response.data;
    } catch (error) {
      console.error('Save travel history error:', error);
      throw error;
    }
  }

  // 음성 안내 메시지 생성 (TTS)
  async generateVoiceNavigation(route, currentStep) {
    try {
      const response = await this.client.post('/tts/navigation', {
        route_id: route.id,
        current_step: currentStep,
        style: 'friendly'
      });
      return response.data;
    } catch (error) {
      console.error('Voice navigation error:', error);
      throw error;
    }
  }
}

// 모의 데이터 (개발용)
export const mockData = {
  recommendedRoutes: [
    {
      id: 1,
      title: '제주 해안도로 드라이브',
      subtitle: '푸른 바다와 함께 달리는 환상적인 코스',
      duration: 180, // 분
      distance: 45.2, // km
      difficulty: 'easy',
      scenery_score: 9.5,
      image_url: 'https://images.unsplash.com/photo-1544273677-6aaf4f6a10e4?w=400&h=300&fit=crop&auto=format',
      icon: 'car-outline',
      waypoints: [
        { name: '제주공항', coordinates: [126.4933, 33.5066] },
        { name: '애월해안도로', coordinates: [126.3324, 33.4615] },
        { name: '한림공원', coordinates: [126.2411, 33.4154] },
        { name: '협재해수욕장', coordinates: [126.2396, 33.3940] }
      ]
    },
    {
      id: 2,
      title: '성산일출봉 + 우도 투어',
      subtitle: '일출 명소와 아름다운 섬 여행',
      duration: 240,
      distance: 32.1,
      difficulty: 'medium',
      scenery_score: 10.0,
      image_url: 'https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=400&h=300&fit=crop&auto=format',
      icon: 'mountain-outline',
      waypoints: [
        { name: '성산일출봉', coordinates: [126.9423, 33.4586] },
        { name: '우도선착장', coordinates: [126.9513, 33.5069] },
        { name: '우도 해안도로', coordinates: [126.9545, 33.5025] }
      ]
    },
    {
      id: 3,
      title: '오션뷰 에메 카페',
      subtitle: '인생샷 남기는 감성 카페, 바다 전망 최고',
      duration: 90,
      distance: 12.5,
      difficulty: 'easy',
      scenery_score: 8.8,
      image_url: 'https://images.unsplash.com/photo-1554118811-1e0d58224f24?w=400&h=300&fit=crop&auto=format',
      icon: 'cafe-outline',
      waypoints: [
        { name: '애월읍', coordinates: [126.3324, 33.4615] },
        { name: '한림해변카페거리', coordinates: [126.2400, 33.4100] }
      ]
    }
  ],

  nearbyPOIs: [
    {
      id: 1,
      name: '오션뷰 에메 카페',
      category: 'cafe',
      rating: 4.8,
      distance: 2.3,
      coordinates: [126.3324, 33.4615],
      description: '인생샷 남기는 감성 카페, 바다 전망 최고'
    },
    {
      id: 2,
      name: '제주 흑돼지 맛집',
      category: 'restaurant',
      rating: 4.6,
      distance: 1.8,
      coordinates: [126.5312, 33.3617],
      description: '현지인 추천 제주 특산품 요리'
    }
  ]
};

export default new VistaAPI(); 