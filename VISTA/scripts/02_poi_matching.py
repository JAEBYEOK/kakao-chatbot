#!/usr/bin/env python3
"""
POI와 링크데이터 매칭
"""

import json
import pandas as pd
import geopandas as gpd
from pathlib import Path
import yaml
import logging
from shapely.geometry import Point
from sklearn.neighbors import BallTree
import numpy as np

class POILinkMatcher:
    def __init__(self, config_path: str = "config/project_config.yaml"):
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = yaml.safe_load(f)
        
        self.setup_logging()
        
    def setup_logging(self):
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
    def load_data(self):
        """링크 데이터와 POI 데이터 로드"""
        # 링크 데이터 로드
        links_path = Path(self.config['data_paths']['processed_data']) / "jeju_links.json"
        with open(links_path, 'r', encoding='utf-8') as f:
            self.links_data = json.load(f)
            
        # POI 데이터 로드 (예시)
        poi_data = {
            'pois': [
                {'id': 1, 'name': '성산일출봉', 'lat': 33.4583, 'lon': 126.9427, 'category': 'attraction'},
                {'id': 2, 'name': '한림공원', 'lat': 33.3940, 'lon': 126.2418, 'category': 'attraction'},
                {'id': 3, 'name': '제주국제공항', 'lat': 33.5067, 'lon': 126.4930, 'category': 'transport'},
            ]
        }
        self.poi_data = poi_data
        
    def match_poi_to_links(self):
        """POI를 가장 가까운 링크에 매칭"""
        self.logger.info("POI-링크 매칭 시작")
        
        matched_results = []
        
        for poi in self.poi_data['pois']:
            poi_point = Point(poi['lon'], poi['lat'])
            closest_link = self.find_closest_link(poi_point)
            
            matched_results.append({
                'poi_id': poi['id'],
                'poi_name': poi['name'],
                'poi_category': poi['category'],
                'matched_link_id': closest_link['link_id'],
                'distance_meters': closest_link['distance']
            })
            
        return matched_results
        
    def find_closest_link(self, poi_point):
        """POI에 가장 가까운 링크 찾기"""
        min_distance = float('inf')
        closest_link = None
        
        for link in self.links_data['links']:
            # 링크 중점 계산 (실제로는 geometry를 사용해야 함)
            link_distance = 100  # 임시값
            
            if link_distance < min_distance:
                min_distance = link_distance
                closest_link = {
                    'link_id': link['link_id'],
                    'distance': link_distance
                }
                
        return closest_link
        
    def save_results(self, matched_data):
        """매칭 결과 저장"""
        processed_path = Path(self.config['data_paths']['processed_data'])
        
        # POI 매칭 결과 저장
        with open(processed_path / "poi_matched_links.json", 'w', encoding='utf-8') as f:
            json.dump({'matches': matched_data}, f, ensure_ascii=False, indent=2)
            
        # POI 좌표 CSV 저장
        poi_df = pd.DataFrame(self.poi_data['pois'])
        poi_df.to_csv(processed_path / "poi_coordinates.csv", index=False)
        
        self.logger.info("POI 매칭 결과 저장 완료")
        
    def run(self):
        self.logger.info("POI 매칭 파이프라인 시작")
        self.load_data()
        matched_data = self.match_poi_to_links()
        self.save_results(matched_data)
        self.logger.info("POI 매칭 파이프라인 완료")

if __name__ == "__main__":
    matcher = POILinkMatcher()
    matcher.run() 