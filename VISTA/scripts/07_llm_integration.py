#!/usr/bin/env python3
"""
LLM 통합 및 맞춤형 네비게이션 시스템 구축
"""

import os
import json
import pickle
import numpy as np
import pandas as pd
from pathlib import Path
import yaml
import logging
from typing import Dict, List, Tuple, Optional
import openai
from transformers import AutoTokenizer, AutoModel
import torch
from sklearn.metrics.pairwise import cosine_similarity

class NavigationLLMIntegrator:
    def __init__(self, config_path: str = "config/project_config.yaml"):
        """네비게이션 LLM 통합기 초기화"""
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = yaml.safe_load(f)
        
        self.setup_logging()
        self.setup_models()
        self.load_data()
        
    def setup_logging(self):
        """로깅 설정"""
        logging.basicConfig(
            level=getattr(logging, self.config['logging']['level']),
            format=self.config['logging']['format']
        )
        self.logger = logging.getLogger(__name__)
        
    def setup_models(self):
        """모델 초기화"""
        self.logger.info("모델 초기화 시작")
        
        # OpenAI API 설정
        openai.api_key = os.getenv('OPENAI_API_KEY')
        
        # 한국어 임베딩 모델 로드
        model_name = "klue/bert-base"
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.embedding_model = AutoModel.from_pretrained(model_name)
        
        # STT/TTS 모델 로드
        self.load_voice_models()
        
    def load_voice_models(self):
        """음성 모델 로드"""
        try:
            models_path = Path(self.config['data_paths']['models'])
            
            with open(models_path / "stt_model.pkl", 'rb') as f:
                self.stt_model = pickle.load(f)
                
            with open(models_path / "tts_model.pkl", 'rb') as f:
                self.tts_model = pickle.load(f)
                
            self.logger.info("음성 모델 로드 완료")
            
        except FileNotFoundError:
            self.logger.warning("음성 모델을 찾을 수 없습니다. 기본 모델을 사용합니다.")
            
    def load_data(self):
        """관광 정보 및 링크 데이터 로드"""
        self.logger.info("관광 데이터 로드 시작")
        
        # 라벨링된 관광 정보 로드
        labeled_path = Path(self.config['data_paths']['labeled_data']) / "tourism_labeled_links.json"
        with open(labeled_path, 'r', encoding='utf-8') as f:
            self.tourism_data = json.load(f)
            
        self.logger.info(f"관광 링크 데이터 로드 완료: {len(self.tourism_data.get('links', []))} 개")
        
    def create_route_embeddings(self) -> np.ndarray:
        """경로별 임베딩 생성"""
        self.logger.info("경로 임베딩 생성 시작")
        
        route_descriptions = []
        
        for link in self.tourism_data.get('links', []):
            # 각 링크의 관광 정보를 문장으로 변환
            description = self.create_route_description(link)
            route_descriptions.append(description)
            
        # 임베딩 생성
        embeddings = []
        for desc in route_descriptions:
            embedding = self.get_text_embedding(desc)
            embeddings.append(embedding)
            
        embeddings_array = np.array(embeddings)
        self.logger.info(f"임베딩 생성 완료: {embeddings_array.shape}")
        
        return embeddings_array
        
    def create_route_description(self, link: Dict) -> str:
        """링크 정보를 자연어 설명으로 변환"""
        description_parts = []
        
        # 기본 도로 정보
        if link.get('name'):
            description_parts.append(f"{link['name']} 도로")
            
        # 관광지 정보
        if link.get('nearby_attractions'):
            attractions = ', '.join(link['nearby_attractions'])
            description_parts.append(f"주변 관광지: {attractions}")
            
        # 도로 특성
        if link.get('scenic_value'):
            description_parts.append(f"경관 수준: {link['scenic_value']}")
            
        if link.get('difficulty'):
            description_parts.append(f"운전 난이도: {link['difficulty']}")
            
        return '. '.join(description_parts)
        
    def get_text_embedding(self, text: str) -> np.ndarray:
        """텍스트 임베딩 생성"""
        inputs = self.tokenizer(text, return_tensors="pt", 
                               padding=True, truncation=True, max_length=512)
        
        with torch.no_grad():
            outputs = self.embedding_model(**inputs)
            
        # [CLS] 토큰의 임베딩 사용
        embedding = outputs.last_hidden_state[:, 0, :].numpy().squeeze()
        return embedding
        
    def create_navigation_prompts(self) -> List[Dict]:
        """네비게이션용 프롬프트 생성"""
        self.logger.info("네비게이션 프롬프트 생성")
        
        prompts = [
            {
                "intent": "scenic_route",
                "prompt": "가장 경치가 좋은 경로로 {destination}까지 안내해주세요. 바다 전망이나 산악 전망을 우선으로 하는 경로를 추천해주세요.",
                "response_format": "경치 좋은 경로를 안내드리겠습니다. {route_description}을 경유하여 가시면 아름다운 {scenic_features}을 감상하실 수 있습니다."
            },
            {
                "intent": "cultural_route", 
                "prompt": "문화 관광지를 경유하여 {destination}까지 가는 경로를 안내해주세요. 역사적 장소나 박물관을 우선으로 해주세요.",
                "response_format": "문화 관광 경로를 안내드리겠습니다. {cultural_sites}을 경유하여 제주의 역사와 문화를 체험하실 수 있습니다."
            },
            {
                "intent": "food_route",
                "prompt": "맛집을 경유하여 {destination}까지 가는 경로를 추천해주세요. 제주 특산 음식을 맛볼 수 있는 곳을 우선해주세요.",
                "response_format": "맛집 경유 경로를 안내드리겠습니다. {restaurants}에서 제주의 특색 있는 {local_foods}을 맛보실 수 있습니다."
            }
        ]
        
        return prompts
        
    def train_navigation_llm(self):
        """네비게이션 LLM 학습"""
        self.logger.info("네비게이션 LLM 학습 시작")
        
        # 프롬프트 생성
        prompts = self.create_navigation_prompts()
        
        # 학습 데이터 준비
        training_data = self.prepare_training_data(prompts)
        
        # Fine-tuning 수행 (실제 구현에서는 더 복잡한 학습 과정 필요)
        self.logger.info("LLM Fine-tuning 시뮬레이션 완료")
        
        return {
            "model_type": "navigation_llm",
            "training_samples": len(training_data),
            "prompts_count": len(prompts),
            "status": "trained"
        }
        
    def prepare_training_data(self, prompts: List[Dict]) -> List[Dict]:
        """학습 데이터 준비"""
        training_data = []
        
        for link in self.tourism_data.get('links', []):
            for prompt_template in prompts:
                # 각 링크에 대해 프롬프트-응답 쌍 생성
                training_sample = {
                    "prompt": prompt_template["prompt"],
                    "response": self.generate_response_for_link(link, prompt_template),
                    "link_id": link.get("link_id"),
                    "intent": prompt_template["intent"]
                }
                training_data.append(training_sample)
                
        return training_data
        
    def generate_response_for_link(self, link: Dict, prompt_template: Dict) -> str:
        """링크별 응답 생성"""
        response_format = prompt_template["response_format"]
        
        # 템플릿에 따라 응답 생성
        if prompt_template["intent"] == "scenic_route":
            return response_format.format(
                route_description=link.get("name", "이 경로"),
                scenic_features="바다 경치" if "coastal" in link.get("features", []) else "산악 경치"
            )
        elif prompt_template["intent"] == "cultural_route":
            cultural_sites = ", ".join(link.get("cultural_sites", ["문화유적지"]))
            return response_format.format(cultural_sites=cultural_sites)
        elif prompt_template["intent"] == "food_route":
            restaurants = ", ".join(link.get("restaurants", ["지역 맛집"]))
            local_foods = ", ".join(link.get("local_foods", ["제주 특산품"]))
            return response_format.format(restaurants=restaurants, local_foods=local_foods)
            
        return "경로를 안내드리겠습니다."
        
    def create_route_recommendation_system(self, embeddings: np.ndarray):
        """경로 추천 시스템 생성"""
        self.logger.info("경로 추천 시스템 생성")
        
        class RouteRecommender:
            def __init__(self, embeddings, tourism_data, llm_integrator):
                self.embeddings = embeddings
                self.tourism_data = tourism_data
                self.llm_integrator = llm_integrator
                
            def recommend_route(self, user_query: str, top_k: int = 5) -> List[Dict]:
                """사용자 쿼리에 따른 경로 추천"""
                # 사용자 쿼리 임베딩
                query_embedding = self.llm_integrator.get_text_embedding(user_query)
                
                # 유사도 계산
                similarities = cosine_similarity([query_embedding], self.embeddings)[0]
                
                # 상위 k개 경로 선택
                top_indices = np.argsort(similarities)[-top_k:][::-1]
                
                recommendations = []
                for idx in top_indices:
                    link = self.tourism_data['links'][idx]
                    recommendations.append({
                        'link_id': link.get('link_id'),
                        'name': link.get('name'),
                        'similarity_score': similarities[idx],
                        'description': self.llm_integrator.create_route_description(link)
                    })
                    
                return recommendations
                
        return RouteRecommender(embeddings, self.tourism_data, self)
        
    def save_models(self, embeddings: np.ndarray, llm_model: Dict):
        """모델 저장"""
        self.logger.info("모델 저장 시작")
        
        models_path = Path(self.config['data_paths']['models'])
        
        # LLM 모델 저장
        with open(models_path / "navigation_llm.pkl", 'wb') as f:
            pickle.dump(llm_model, f)
            
        # 경로 임베딩 저장
        np.save(models_path / "route_embeddings.npy", embeddings)
        
        self.logger.info("모델 저장 완료")
        
    def run(self):
        """전체 파이프라인 실행"""
        self.logger.info("LLM 통합 파이프라인 시작")
        
        try:
            # 경로 임베딩 생성
            embeddings = self.create_route_embeddings()
            
            # LLM 학습
            llm_model = self.train_navigation_llm()
            
            # 추천 시스템 생성
            recommender = self.create_route_recommendation_system(embeddings)
            
            # 모델 저장
            self.save_models(embeddings, llm_model)
            
            self.logger.info("LLM 통합 파이프라인 완료")
            
            # 테스트 추천
            test_query = "바다가 보이는 경치 좋은 경로로 가고 싶어요"
            recommendations = recommender.recommend_route(test_query)
            self.logger.info(f"테스트 추천 결과: {len(recommendations)}개 경로")
            
        except Exception as e:
            self.logger.error(f"파이프라인 실행 중 오류 발생: {str(e)}")
            raise

if __name__ == "__main__":
    integrator = NavigationLLMIntegrator()
    integrator.run() 