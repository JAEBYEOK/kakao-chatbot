#!/usr/bin/env python3
"""
관광정보 라벨링
"""

import json
import pandas as pd
from pathlib import Path
import yaml
import logging

class TourismLabeler:
    def __init__(self, config_path: str = "config/project_config.yaml"):
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = yaml.safe_load(f)
        
        self.setup_logging()
        
    def setup_logging(self):
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
    def load_data(self):
        """POI 매칭된 링크 데이터 로드"""
        processed_path = Path(self.config['data_paths']['processed_data'])
        
        with open(processed_path / "poi_matched_links.json", 'r', encoding='utf-8') as f:
            self.poi_matched_data = json.load(f)
            
        # 관광 정보 데이터 (예시)
        self.tourism_info = {
            'scenic_routes': ['해안도로', '한라산도로', '올레길'],
            'cultural_sites': ['성산일출봉', '만장굴', '돌하르방공원'],
            'restaurants': ['흑돼지맛집', '해산물전문점', '제주향토음식']
        }
        
    def label_tourism_features(self):
        """관광 특성 라벨링"""
        self.logger.info("관광 특성 라벨링 시작")
        
        labeled_links = []
        
        for match in self.poi_matched_data['matches']:
            # 기본 링크 정보 복사
            labeled_link = {
                'link_id': match['matched_link_id'],
                'poi_name': match['poi_name'],
                'poi_category': match['poi_category']
            }
            
            # 관광 특성 추가
            labeled_link.update(self.classify_tourism_features(match))
            
            labeled_links.append(labeled_link)
            
        return labeled_links
        
    def classify_tourism_features(self, match):
        """관광 특성 분류"""
        features = {
            'scenic_value': 'medium',
            'cultural_importance': 'low',
            'food_attractions': [],
            'difficulty': 'easy',
            'recommended_time': 'anytime'
        }
        
        # POI 카테고리별 특성 설정
        if match['poi_category'] == 'attraction':
            features['scenic_value'] = 'high'
            features['cultural_importance'] = 'high'
        elif match['poi_category'] == 'restaurant':
            features['food_attractions'] = ['local_cuisine']
            
        return features
        
    def create_attraction_categories(self):
        """관광지 카테고리 생성"""
        categories = [
            {'category': 'natural', 'description': '자연 관광지', 'examples': ['성산일출봉', '한라산']},
            {'category': 'cultural', 'description': '문화 관광지', 'examples': ['만장굴', '제주민속촌']},
            {'category': 'activity', 'description': '액티비티', 'examples': ['올레길', '해수욕장']},
            {'category': 'food', 'description': '맛집', 'examples': ['흑돼지', '해산물']}
        ]
        
        return categories
        
    def save_results(self, labeled_links, categories):
        """라벨링 결과 저장"""
        labeled_path = Path(self.config['data_paths']['labeled_data'])
        labeled_path.mkdir(parents=True, exist_ok=True)
        
        # 라벨링된 링크 저장
        labeled_data = {
            'links': labeled_links,
            'total_count': len(labeled_links),
            'labeled_at': pd.Timestamp.now().isoformat()
        }
        
        with open(labeled_path / "tourism_labeled_links.json", 'w', encoding='utf-8') as f:
            json.dump(labeled_data, f, ensure_ascii=False, indent=2)
            
        # 관광지 카테고리 저장
        categories_df = pd.DataFrame(categories)
        categories_df.to_csv(labeled_path / "attraction_categories.csv", index=False)
        
        self.logger.info("관광정보 라벨링 결과 저장 완료")
        
    def run(self):
        self.logger.info("관광정보 라벨링 파이프라인 시작")
        self.load_data()
        labeled_links = self.label_tourism_features()
        categories = self.create_attraction_categories()
        self.save_results(labeled_links, categories)
        self.logger.info("관광정보 라벨링 파이프라인 완료")

if __name__ == "__main__":
    labeler = TourismLabeler()
    labeler.run() 