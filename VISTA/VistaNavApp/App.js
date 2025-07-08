import React, { useState, useEffect } from 'react';
import { 
  StyleSheet, 
  Text, 
  View, 
  ScrollView, 
  TouchableOpacity, 
  TextInput,
  Image,
  Dimensions,
  StatusBar,
  SafeAreaView,
  Alert
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import VoiceService from './services/VoiceService';
import VistaAPI, { mockData } from './services/VistaAPI';

const { width, height } = Dimensions.get('window');

export default function App() {
  const [selectedLocation, setSelectedLocation] = useState('제주도');
  const [isVoiceListening, setIsVoiceListening] = useState(false);
  const [activeTab, setActiveTab] = useState('홈');
  const [voiceResult, setVoiceResult] = useState(null);
  const [recommendations, setRecommendations] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    // 초기 데이터 로드
    loadRecommendations();
    
    // 컴포넌트 언마운트 시 정리
    return () => {
      VoiceService.cleanup();
    };
  }, []);

  const loadRecommendations = async () => {
    try {
      setLoading(true);
      const response = await VistaAPI.getRecommendedRoutes();
      if (response.success) {
        setRecommendations(response.routes);
      } else {
        // 백엔드 연결 실패 시 모의 데이터 사용
        setRecommendations(mockData.recommendedRoutes);
      }
    } catch (error) {
      console.error('추천 경로 로드 실패:', error);
      // 오류 시 모의 데이터 사용
      setRecommendations(mockData.recommendedRoutes);
    } finally {
      setLoading(false);
    }
  };

  const handleVoiceCommand = async () => {
    try {
      if (!isVoiceListening) {
        // 음성 녹음 시작
        setIsVoiceListening(true);
        await VoiceService.announceNavigation('listening');
        await VoiceService.startRecording();
        
        // 3초 후 자동으로 녹음 중지 (실제로는 사용자가 버튼을 다시 눌러서 중지)
        setTimeout(async () => {
          if (VoiceService.getStatus().isRecording) {
            await stopVoiceRecording();
          }
        }, 3000);
      } else {
        // 음성 녹음 중지
        await stopVoiceRecording();
      }
    } catch (error) {
      console.error('음성 명령 처리 오류:', error);
      setIsVoiceListening(false);
      await VoiceService.announceNavigation('error');
      Alert.alert('오류', '음성 인식 중 오류가 발생했습니다.');
    }
  };

  const stopVoiceRecording = async () => {
    try {
      setIsVoiceListening(false);
      await VoiceService.announceNavigation('processing');
      
      const result = await VoiceService.stopRecording();
      setVoiceResult(result);
      
      // 결과에 따라 적절한 응답
      if (result.intent === 'route_navigation') {
        await VoiceService.announceNavigation('routeFound');
        await processRouteRequest(result);
      } else if (result.intent === 'poi_search') {
        await processPOISearch(result);
      }
      
      // 음성 인식 결과를 사용자에게 표시
      Alert.alert(
        '음성 인식 결과', 
        `인식된 내용: "${result.text}"\n\n어떻게 도와드릴까요?`,
        [{ text: '확인', onPress: () => {} }]
      );
    } catch (error) {
      console.error('음성 녹음 중지 오류:', error);
      await VoiceService.announceNavigation('error');
    }
  };

  const processRouteRequest = async (voiceResult) => {
    try {
      // 실제 환경에서는 VistaAPI.calculateRoute 사용
      console.log('경로 계산 요청:', voiceResult.entities);
      
      // 모의 데이터로 추천 업데이트
      const routeRecommendations = mockData.recommendedRoutes.filter(route => 
        route.title.includes(voiceResult.entities.destination) ||
        route.title.includes('해안도로')
      );
      
      if (routeRecommendations.length > 0) {
        setRecommendations(routeRecommendations);
      }
    } catch (error) {
      console.error('경로 처리 오류:', error);
    }
  };

  const processPOISearch = async (voiceResult) => {
    try {
      console.log('POI 검색 요청:', voiceResult.entities);
      
      // 모의 POI 데이터 업데이트
      const poiResults = mockData.nearbyPOIs.filter(poi => 
        poi.category === voiceResult.entities.category
      );
      
      console.log('POI 검색 결과:', poiResults);
    } catch (error) {
      console.error('POI 검색 오류:', error);
    }
  };



  return (
    <SafeAreaView style={styles.container}>
      <StatusBar barStyle="dark-content" backgroundColor="#ffffff" />
      
      {/* Header */}
      <View style={styles.header}>
        <Text style={styles.logo}>VISTA</Text>
        <View style={styles.locationContainer}>
          <Ionicons name="location-outline" size={16} color="#666" />
          <Text style={styles.locationText}>{selectedLocation}</Text>
          <Ionicons name="chevron-down-outline" size={16} color="#666" />
        </View>
        <TouchableOpacity>
          <Ionicons name="settings-outline" size={24} color="#666" />
        </TouchableOpacity>
      </View>

      <ScrollView style={styles.content} showsVerticalScrollIndicator={false}>
        {/* Main Title */}
        <View style={styles.titleContainer}>
          <Text style={styles.mainTitle}>여행의 모든 순간, VISTA와 함께</Text>
          <Text style={styles.subtitle}>
            당신만의 여정이 특별해지는 곳, 감성적인 추천과 미래지향적 경험을 지금 만나보세요.
          </Text>
        </View>

        {/* Description Card */}
        <View style={styles.descriptionCard}>
          <Text style={styles.descriptionText}>
            여행 목적, 분위기, 원하는 경험을 자유롭게 말씀해보세요. AI가 맞춤 경로와 장소를 추천합니다.
          </Text>
        </View>

        {/* Voice Command Button */}
        <TouchableOpacity 
          style={[styles.voiceButton, isVoiceListening && styles.voiceButtonActive]}
          onPress={handleVoiceCommand}
        >
          <Ionicons 
            name="mic" 
            size={24} 
            color={isVoiceListening ? "#ffffff" : "#4A90E2"} 
          />
          <Text style={[styles.voiceButtonText, isVoiceListening && styles.voiceButtonTextActive]}>
            여행 플랜 말하기
          </Text>
        </TouchableOpacity>

        {/* Recommendations */}
        <View style={styles.recommendationsContainer}>
          <Text style={styles.sectionTitle}>추천 코스/장소</Text>
          
          {loading ? (
            <View style={styles.loadingContainer}>
              <Text style={styles.loadingText}>추천 코스를 불러오는 중...</Text>
            </View>
          ) : (
            recommendations.map((item) => (
              <TouchableOpacity key={item.id} style={styles.recommendationCard}>
                <View style={styles.cardImageContainer}>
                  {item.image_url ? (
                    <Image 
                      source={{ uri: item.image_url }}
                      style={styles.cardImage}
                      resizeMode="cover"
                    />
                  ) : (
                    <View style={styles.cardImagePlaceholder}>
                      <Ionicons name={item.icon || 'location-outline'} size={40} color="#4A90E2" />
                    </View>
                  )}
                </View>
                <View style={styles.cardContent}>
                  <View style={styles.cardHeader}>
                    <Text style={styles.cardTitle}>{item.title}</Text>
                    {item.scenery_score && (
                      <View style={styles.scoreContainer}>
                        <Ionicons name="star" size={14} color="#FFD700" />
                        <Text style={styles.scoreText}>{item.scenery_score}</Text>
                      </View>
                    )}
                  </View>
                  <Text style={styles.cardSubtitle}>{item.subtitle}</Text>
                  {item.duration && (
                    <View style={styles.cardMetadata}>
                      <View style={styles.metadataItem}>
                        <Ionicons name="time-outline" size={14} color="#666" />
                        <Text style={styles.metadataText}>{Math.floor(item.duration / 60)}시간</Text>
                      </View>
                      {item.distance && (
                        <View style={styles.metadataItem}>
                          <Ionicons name="navigate-outline" size={14} color="#666" />
                          <Text style={styles.metadataText}>{item.distance}km</Text>
                        </View>
                      )}
                    </View>
                  )}
                </View>
              </TouchableOpacity>
            ))
          )}
        </View>
      </ScrollView>

      {/* Bottom Navigation */}
      <View style={styles.bottomNav}>
        {['홈', '추천', '내 여정', '프로필'].map((tab, index) => {
          const icons = ['home-outline', 'compass-outline', 'map-outline', 'person-outline'];
          const activeIcons = ['home', 'compass', 'map', 'person'];
          
          return (
            <TouchableOpacity 
              key={tab}
              style={styles.tabItem}
              onPress={() => setActiveTab(tab)}
            >
              <Ionicons 
                name={activeTab === tab ? activeIcons[index] : icons[index]} 
                size={24} 
                color={activeTab === tab ? '#4A90E2' : '#999'} 
              />
              <Text style={[styles.tabText, activeTab === tab && styles.tabTextActive]}>
                {tab}
              </Text>
            </TouchableOpacity>
          );
        })}
      </View>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#ffffff',
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: 20,
    paddingVertical: 15,
    backgroundColor: '#ffffff',
  },
  logo: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#000',
  },
  locationContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 12,
    paddingVertical: 8,
    backgroundColor: '#f8f9fa',
    borderRadius: 20,
  },
  locationText: {
    marginHorizontal: 5,
    fontSize: 14,
    color: '#666',
  },
  content: {
    flex: 1,
    paddingHorizontal: 20,
  },
  titleContainer: {
    marginTop: 20,
    marginBottom: 30,
  },
  mainTitle: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#000',
    textAlign: 'center',
    marginBottom: 15,
    lineHeight: 36,
  },
  subtitle: {
    fontSize: 16,
    color: '#666',
    textAlign: 'center',
    lineHeight: 24,
  },
  descriptionCard: {
    backgroundColor: '#f8f9fa',
    padding: 20,
    borderRadius: 16,
    marginBottom: 30,
  },
  descriptionText: {
    fontSize: 16,
    color: '#333',
    textAlign: 'center',
    lineHeight: 24,
  },
  voiceButton: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: '#ffffff',
    borderWidth: 2,
    borderColor: '#4A90E2',
    paddingVertical: 15,
    paddingHorizontal: 30,
    borderRadius: 50,
    marginBottom: 40,
    alignSelf: 'center',
    shadowColor: '#4A90E2',
    shadowOffset: {
      width: 0,
      height: 4,
    },
    shadowOpacity: 0.3,
    shadowRadius: 8,
    elevation: 8,
  },
  voiceButtonActive: {
    backgroundColor: '#4A90E2',
  },
  voiceButtonText: {
    marginLeft: 10,
    fontSize: 16,
    fontWeight: '600',
    color: '#4A90E2',
  },
  voiceButtonTextActive: {
    color: '#ffffff',
  },
  recommendationsContainer: {
    marginBottom: 100,
  },
  sectionTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#000',
    marginBottom: 20,
  },
  loadingContainer: {
    padding: 40,
    alignItems: 'center',
  },
  loadingText: {
    fontSize: 16,
    color: '#666',
  },
  recommendationCard: {
    flexDirection: 'row',
    backgroundColor: '#ffffff',
    borderRadius: 16,
    marginBottom: 15,
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 2,
    },
    shadowOpacity: 0.1,
    shadowRadius: 8,
    elevation: 4,
    overflow: 'hidden',
  },
  cardImageContainer: {
    width: 100,
    height: 100,
  },
  cardImage: {
    width: '100%',
    height: '100%',
  },
  cardImagePlaceholder: {
    flex: 1,
    backgroundColor: '#f0f8ff',
    justifyContent: 'center',
    alignItems: 'center',
  },
  cardContent: {
    flex: 1,
    padding: 15,
    justifyContent: 'center',
  },
  cardHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 5,
  },
  cardTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#000',
    flex: 1,
  },
  scoreContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#f8f9fa',
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 12,
  },
  scoreText: {
    fontSize: 12,
    fontWeight: '600',
    color: '#333',
    marginLeft: 4,
  },
  cardSubtitle: {
    fontSize: 14,
    color: '#666',
    lineHeight: 20,
    marginBottom: 8,
  },
  cardMetadata: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  metadataItem: {
    flexDirection: 'row',
    alignItems: 'center',
    marginRight: 12,
  },
  metadataText: {
    fontSize: 12,
    color: '#666',
    marginLeft: 4,
  },
  bottomNav: {
    flexDirection: 'row',
    backgroundColor: '#ffffff',
    paddingVertical: 10,
    paddingBottom: 20,
    borderTopWidth: 1,
    borderTopColor: '#f0f0f0',
  },
  tabItem: {
    flex: 1,
    alignItems: 'center',
    paddingVertical: 5,
  },
  tabText: {
    fontSize: 12,
    color: '#999',
    marginTop: 4,
  },
  tabTextActive: {
    color: '#4A90E2',
    fontWeight: '600',
  },
});
