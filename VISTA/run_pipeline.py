#!/usr/bin/env python3
"""
제주도 내비게이션 시스템 파이프라인 실행기
"""

import argparse
import subprocess
import sys
import yaml
from pathlib import Path
import logging
from typing import List, Dict

class PipelineRunner:
    def __init__(self, workflow_path: str = "workflow.yaml"):
        """파이프라인 실행기 초기화"""
        with open(workflow_path, 'r', encoding='utf-8') as f:
            self.workflow = yaml.safe_load(f)
        
        self.setup_logging()
        
    def setup_logging(self):
        """로깅 설정"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('logs/pipeline_runner.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
    def create_directories(self):
        """필요한 디렉토리 생성"""
        directories = [
            "data/raw", "data/processed", "data/labeled", 
            "data/voice", "models", "osrm_data", 
            "mobile_app", "logs", "config"
        ]
        
        for directory in directories:
            Path(directory).mkdir(parents=True, exist_ok=True)
            
        self.logger.info("프로젝트 디렉토리 생성 완료")
        
    def get_stage_dependencies(self, stage_name: str) -> List[str]:
        """스테이지 의존성 조회"""
        for stage in self.workflow['stages']:
            if stage['name'] == stage_name:
                return stage.get('dependencies', [])
        return []
        
    def run_stage(self, stage_name: str) -> bool:
        """개별 스테이지 실행"""
        self.logger.info(f"스테이지 '{stage_name}' 실행 시작")
        
        # 스테이지 정보 찾기
        stage_info = None
        for stage in self.workflow['stages']:
            if stage['name'] == stage_name:
                stage_info = stage
                break
                
        if not stage_info:
            self.logger.error(f"스테이지 '{stage_name}'를 찾을 수 없습니다.")
            return False
            
        # 의존성 확인
        dependencies = stage_info.get('dependencies', [])
        for dep in dependencies:
            if not self.check_stage_output(dep):
                self.logger.error(f"의존성 스테이지 '{dep}'의 출력이 없습니다.")
                return False
                
        # 스크립트 실행
        for script_path in stage_info.get('scripts', []):
            try:
                result = subprocess.run([
                    sys.executable, script_path
                ], capture_output=True, text=True, timeout=7200)  # 2시간 제한
                
                if result.returncode != 0:
                    self.logger.error(f"스크립트 실행 실패: {script_path}")
                    self.logger.error(f"오류 출력: {result.stderr}")
                    return False
                    
                self.logger.info(f"스크립트 실행 완료: {script_path}")
                
            except subprocess.TimeoutExpired:
                self.logger.error(f"스크립트 실행 시간 초과: {script_path}")
                return False
            except Exception as e:
                self.logger.error(f"스크립트 실행 중 오류: {script_path}, {str(e)}")
                return False
                
        self.logger.info(f"스테이지 '{stage_name}' 실행 완료")
        return True
        
    def check_stage_output(self, stage_name: str) -> bool:
        """스테이지 출력 파일 존재 확인"""
        for stage in self.workflow['stages']:
            if stage['name'] == stage_name:
                outputs = stage.get('outputs', [])
                for output_path in outputs:
                    if not Path(output_path).exists():
                        return False
                return True
        return False
        
    def run_full_pipeline(self):
        """전체 파이프라인 실행"""
        self.logger.info("전체 파이프라인 실행 시작")
        
        # 디렉토리 생성
        self.create_directories()
        
        # 스테이지 순서대로 실행
        stages = [
            'link_data_processing',
            'poi_matching', 
            'tourism_labeling',
            'voice_data_collection',
            'stt_tts_training',
            'osrm_server_setup',
            'llm_integration',
            'mobile_app_deployment'
        ]
        
        for stage_name in stages:
            if not self.run_stage(stage_name):
                self.logger.error(f"파이프라인 실행 중단: {stage_name} 단계 실패")
                return False
                
        self.logger.info("전체 파이프라인 실행 완료")
        return True
        
    def run_specific_stage(self, stage_name: str):
        """특정 스테이지만 실행"""
        self.logger.info(f"특정 스테이지 실행: {stage_name}")
        self.create_directories()
        return self.run_stage(stage_name)
        
    def show_pipeline_status(self):
        """파이프라인 상태 출력"""
        print("\n=== 제주도 내비게이션 파이프라인 상태 ===")
        
        for stage in self.workflow['stages']:
            stage_name = stage['name']
            outputs = stage.get('outputs', [])
            
            # 출력 파일 존재 확인
            all_outputs_exist = all(Path(output).exists() for output in outputs)
            status = "✅ 완료" if all_outputs_exist else "❌ 미완료"
            
            print(f"{stage_name:25} | {status}")
            
        print("\n")

def main():
    parser = argparse.ArgumentParser(description='제주도 내비게이션 파이프라인 실행기')
    parser.add_argument('--stage', help='실행할 특정 스테이지 이름')
    parser.add_argument('--status', action='store_true', help='파이프라인 상태 확인')
    parser.add_argument('--full', action='store_true', help='전체 파이프라인 실행')
    
    args = parser.parse_args()
    
    runner = PipelineRunner()
    
    if args.status:
        runner.show_pipeline_status()
    elif args.stage:
        success = runner.run_specific_stage(args.stage)
        sys.exit(0 if success else 1)
    elif args.full:
        success = runner.run_full_pipeline()
        sys.exit(0 if success else 1)
    else:
        parser.print_help()

if __name__ == "__main__":
    main() 