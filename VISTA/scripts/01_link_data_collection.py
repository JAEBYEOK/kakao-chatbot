#!/usr/bin/env python3
"""
제주도 링크데이터 수집 및 전처리
"""

import os
import json
import pandas as pd
import geopandas as gpd
import osmnx as ox
from pathlib import Path
import yaml
import logging
from typing import Dict, List, Tuple

class JejuLinkDataProcessor:
    def __init__(self, config_path: str = "config/project_config.yaml"):
        """제주도 링크데이터 처리기 초기화"""
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = yaml.safe_load(f)
        
        self.setup_logging()
        self.create_directories()
        
    def setup_logging(self):
        """로깅 설정"""
        logging.basicConfig(
            level=getattr(logging, self.config['logging']['level']),
            format=self.config['logging']['format'],
            handlers=[
                logging.FileHandler(self.config['logging']['file']),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
    def create_directories(self):
        """필요한 디렉토리 생성"""
        for path in self.config['data_paths'].values():
            Path(path).mkdir(parents=True, exist_ok=True)
            
    def download_osm_data(self) -> gpd.GeoDataFrame:
        """제주도 OSM 도로 네트워크 데이터 다운로드"""
        self.logger.info("제주도 OSM 데이터 다운로드 시작")
        
        bbox = self.config['jeju_region']['bbox']
        
        # 제주도 도로 네트워크 다운로드
        graph = ox.graph_from_bbox(
            bbox['north'], bbox['south'], 
            bbox['east'], bbox['west'],
            network_type='drive',
            simplify=True
        )
        
        # 그래프를 GeoDataFrame으로 변환
        nodes, edges = ox.graph_to_gdfs(graph)
        
        self.logger.info(f"노드 수: {len(nodes)}, 엣지 수: {len(edges)}")
        return edges
        
    def process_road_segments(self, edges: gpd.GeoDataFrame) -> Dict:
        """도로 세그먼트 처리 및 링크 ID 생성"""
        self.logger.info("도로 세그먼트 처리 시작")
        
        processed_links = []
        
        for idx, edge in edges.iterrows():
            link_data = {
                'link_id': f"jeju_link_{idx[0]}_{idx[1]}_{idx[2]}",
                'from_node': idx[0],
                'to_node': idx[1],
                'geometry': edge.geometry.wkt,
                'highway_type': edge.get('highway', 'unknown'),
                'length': edge.get('length', 0),
                'speed_limit': self.extract_speed_limit(edge),
                'name': edge.get('name', ''),
                'surface': edge.get('surface', 'unknown'),
                'lanes': edge.get('lanes', 1)
            }
            processed_links.append(link_data)
            
        return {
            'links': processed_links,
            'total_count': len(processed_links),
            'region': 'jeju',
            'processed_at': pd.Timestamp.now().isoformat()
        }
        
    def extract_speed_limit(self, edge) -> int:
        """속도 제한 추출"""
        max_speed = edge.get('maxspeed', '50')
        if isinstance(max_speed, str):
            try:
                return int(max_speed.split()[0])
            except:
                return 50
        return max_speed if max_speed else 50
        
    def load_poi_data(self) -> pd.DataFrame:
        """POI 데이터 로드"""
        poi_path = Path(self.config['data_paths']['raw_data']) / "jeju_poi_data.csv"
        
        if poi_path.exists():
            return pd.read_csv(poi_path)
        else:
            self.logger.warning("POI 데이터 파일이 없습니다. 빈 DataFrame을 반환합니다.")
            return pd.DataFrame(columns=['name', 'lat', 'lon', 'category'])
            
    def save_processed_data(self, links_data: Dict, edges: gpd.GeoDataFrame):
        """처리된 데이터 저장"""
        self.logger.info("처리된 데이터 저장 시작")
        
        # 링크 데이터를 JSON으로 저장
        links_path = Path(self.config['data_paths']['processed_data']) / "jeju_links.json"
        with open(links_path, 'w', encoding='utf-8') as f:
            json.dump(links_data, f, ensure_ascii=False, indent=2)
            
        # 도로 세그먼트를 GeoJSON으로 저장
        geojson_path = Path(self.config['data_paths']['processed_data']) / "road_segments.geojson"
        edges.to_file(geojson_path, driver='GeoJSON')
        
        self.logger.info(f"링크 데이터 저장 완료: {links_path}")
        self.logger.info(f"GeoJSON 저장 완료: {geojson_path}")
        
    def run(self):
        """전체 파이프라인 실행"""
        self.logger.info("제주도 링크데이터 수집 파이프라인 시작")
        
        try:
            # OSM 데이터 다운로드
            edges = self.download_osm_data()
            
            # 도로 세그먼트 처리
            links_data = self.process_road_segments(edges)
            
            # POI 데이터 로드
            poi_data = self.load_poi_data()
            self.logger.info(f"POI 데이터 로드 완료: {len(poi_data)} 개")
            
            # 데이터 저장
            self.save_processed_data(links_data, edges)
            
            self.logger.info("제주도 링크데이터 수집 파이프라인 완료")
            
        except Exception as e:
            self.logger.error(f"파이프라인 실행 중 오류 발생: {str(e)}")
            raise

if __name__ == "__main__":
    processor = JejuLinkDataProcessor()
    processor.run() 