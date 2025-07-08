import { Audio } from 'expo-av';
import * as Speech from 'expo-speech';
import * as FileSystem from 'expo-file-system';
import VistaAPI from './VistaAPI';

class VoiceService {
  constructor() {
    this.isRecording = false;
    this.recording = null;
    this.isSpeaking = false;
  }

  // 음성 녹음 시작
  async startRecording() {
    try {
      console.log('음성 녹음 시작...');
      
      // 오디오 권한 요청
      const { status } = await Audio.requestPermissionsAsync();
      if (status !== 'granted') {
        throw new Error('오디오 권한이 필요합니다.');
      }

      // 녹음 설정
      await Audio.setAudioModeAsync({
        allowsRecordingIOS: true,
        playsInSilentModeIOS: true,
      });

      const recordingOptions = {
        android: {
          extension: '.m4a',
          outputFormat: Audio.RECORDING_OPTION_ANDROID_OUTPUT_FORMAT_MPEG_4,
          audioEncoder: Audio.RECORDING_OPTION_ANDROID_AUDIO_ENCODER_AAC,
          sampleRate: 44100,
          numberOfChannels: 2,
          bitRate: 128000,
        },
        ios: {
          extension: '.m4a',
          outputFormat: Audio.RECORDING_OPTION_IOS_OUTPUT_FORMAT_MPEG4AAC,
          audioQuality: Audio.RECORDING_OPTION_IOS_AUDIO_QUALITY_HIGH,
          sampleRate: 44100,
          numberOfChannels: 2,
          bitRate: 128000,
          linearPCMBitDepth: 16,
          linearPCMIsBigEndian: false,
          linearPCMIsFloat: false,
        },
      };

      const { recording } = await Audio.Recording.createAsync(recordingOptions);
      this.recording = recording;
      this.isRecording = true;

      console.log('녹음 시작됨');
      return true;
    } catch (error) {
      console.error('녹음 시작 실패:', error);
      throw error;
    }
  }

  // 음성 녹음 중지 및 처리
  async stopRecording() {
    try {
      if (!this.recording || !this.isRecording) {
        throw new Error('녹음이 진행중이지 않습니다.');
      }

      console.log('녹음 중지...');
      this.isRecording = false;
      await this.recording.stopAndUnloadAsync();
      
      const uri = this.recording.getURI();
      this.recording = null;

      console.log('녹음 파일 저장됨:', uri);
      
      // 음성 인식 처리
      return await this.processVoiceRecognition(uri);
    } catch (error) {
      console.error('녹음 중지 실패:', error);
      throw error;
    }
  }

  // 음성 인식 처리
  async processVoiceRecognition(audioUri) {
    try {
      console.log('음성 인식 처리 중...');
      
      // 실제 환경에서는 VISTA API를 사용
      // const result = await VistaAPI.processVoiceCommand(audioFile);
      
      // 개발용 모의 응답
      const mockResults = [
        {
          text: "제주공항에서 성산일출봉까지 경치 좋은 길로 안내해주세요",
          intent: "route_navigation",
          entities: {
            start: "제주공항",
            destination: "성산일출봉",
            preference: "scenic_route"
          }
        },
        {
          text: "카페 추천해주세요",
          intent: "poi_search",
          entities: {
            category: "cafe",
            location: "current"
          }
        },
        {
          text: "바다 보이는 식당 찾아주세요",
          intent: "poi_search",
          entities: {
            category: "restaurant",
            preference: "ocean_view"
          }
        }
      ];

      // 랜덤하게 모의 결과 반환
      const randomResult = mockResults[Math.floor(Math.random() * mockResults.length)];
      
      console.log('음성 인식 결과:', randomResult);
      return randomResult;
    } catch (error) {
      console.error('음성 인식 실패:', error);
      throw error;
    }
  }

  // 텍스트를 음성으로 변환 (TTS)
  async speak(text, options = {}) {
    try {
      if (this.isSpeaking) {
        await Speech.stop();
      }

      const speechOptions = {
        language: 'ko-KR',
        pitch: 1.0,
        rate: 0.8,
        voice: null, // 기본 음성 사용
        ...options
      };

      this.isSpeaking = true;
      
      return new Promise((resolve, reject) => {
        Speech.speak(text, {
          ...speechOptions,
          onStart: () => {
            console.log('TTS 시작:', text);
          },
          onDone: () => {
            this.isSpeaking = false;
            console.log('TTS 완료');
            resolve();
          },
          onStopped: () => {
            this.isSpeaking = false;
            console.log('TTS 중지됨');
            resolve();
          },
          onError: (error) => {
            this.isSpeaking = false;
            console.error('TTS 오류:', error);
            reject(error);
          }
        });
      });
    } catch (error) {
      this.isSpeaking = false;
      console.error('TTS 실패:', error);
      throw error;
    }
  }

  // 음성 안내 메시지들
  getNavigationMessages() {
    return {
      welcome: "VISTA에 오신 것을 환영합니다. 어떤 여행을 계획하고 계신가요?",
      listening: "말씀해 주세요.",
      processing: "음성을 분석하고 있습니다.",
      routeFound: "맞춤 경로를 찾았습니다.",
      noRoute: "경로를 찾을 수 없습니다. 다시 시도해 주세요.",
      error: "오류가 발생했습니다. 다시 시도해 주세요."
    };
  }

  // 내비게이션 안내 음성
  async announceNavigation(message, type = 'info') {
    const messages = this.getNavigationMessages();
    const textToSpeak = messages[message] || message;
    
    const speechOptions = {
      language: 'ko-KR',
      pitch: type === 'warning' ? 1.2 : 1.0,
      rate: type === 'urgent' ? 1.0 : 0.8
    };

    await this.speak(textToSpeak, speechOptions);
  }

  // 음성 중지
  async stopSpeaking() {
    if (this.isSpeaking) {
      await Speech.stop();
      this.isSpeaking = false;
    }
  }

  // 현재 상태 확인
  getStatus() {
    return {
      isRecording: this.isRecording,
      isSpeaking: this.isSpeaking
    };
  }

  // 리소스 정리
  async cleanup() {
    try {
      if (this.isRecording && this.recording) {
        await this.recording.stopAndUnloadAsync();
        this.recording = null;
        this.isRecording = false;
      }
      
      if (this.isSpeaking) {
        await Speech.stop();
        this.isSpeaking = false;
      }
    } catch (error) {
      console.error('VoiceService cleanup 오류:', error);
    }
  }
}

export default new VoiceService(); 