#!/usr/bin/env python3
"""
Taskmaster 태스크 실행 헬퍼 스크립트
"""

import sys
import subprocess
import json
import logging
from pathlib import Path

def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    return logging.getLogger(__name__)

def run_task(task_id: str):
    """특정 태스크 실행"""
    logger = setup_logging()
    
    # 태스크 정보 로드
    tasks_file = Path(".taskmaster/tasks/tasks.json")
    with open(tasks_file, 'r', encoding='utf-8') as f:
        tasks_data = json.load(f)
    
    # 해당 태스크 찾기
    task = None
    for t in tasks_data['tasks']:
        if t['id'] == task_id:
            task = t
            break
    
    if not task:
        logger.error(f"태스크 '{task_id}'를 찾을 수 없습니다.")
        return False
    
    logger.info(f"태스크 실행 시작: {task['name']}")
    
    try:
        # Python 스크립트 실행
        if task['type'] == 'python_script':
            result = subprocess.run([
                sys.executable, task['script']
            ], capture_output=True, text=True, timeout=task.get('timeout_minutes', 60) * 60)
            
            if result.returncode == 0:
                logger.info(f"태스크 완료: {task_id}")
                return True
            else:
                logger.error(f"태스크 실패: {task_id}")
                logger.error(f"오류: {result.stderr}")
                return False
                
    except Exception as e:
        logger.error(f"태스크 실행 중 오류: {str(e)}")
        return False

def main():
    if len(sys.argv) != 2:
        print("사용법: python run_task.py <task_id>")
        sys.exit(1)
    
    task_id = sys.argv[1]
    success = run_task(task_id)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main() 