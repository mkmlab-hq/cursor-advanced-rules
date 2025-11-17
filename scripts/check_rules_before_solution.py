#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Rules 파일 자동 확인 스크립트 (기본 버전)
문제 해결 전 관련 Rules 파일 검색 및 우선순위 확인

이 스크립트는 기본적인 Rules 검색 기능을 제공합니다.
고급 기능(통합 검색, 자동 승격 등)은 Pro Tier에서 제공됩니다.
"""

import os
import sys
import re
from pathlib import Path
from typing import Dict, List, Optional

# Windows 콘솔 UTF-8 인코딩 설정
if sys.platform == 'win32':
    try:
        import io
        if not sys.stdout.closed and not sys.stderr.closed:
            sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
            sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    except (AttributeError, ValueError):
        pass

def get_workspace_root() -> Path:
    """워크스페이스 루트 찾기"""
    # 현재 스크립트 위치에서 .cursor/rules 찾기
    current_dir = Path(__file__).parent.parent
    if (current_dir / ".cursor" / "rules").exists():
        return current_dir
    # 또는 환경 변수에서
    workspace = os.getenv("CURSOR_WORKSPACE", ".")
    return Path(workspace)

def parse_rule_metadata(rule_file: Path) -> Dict:
    """
    Rules 파일 메타데이터 파싱
    
    Returns:
        {
            'priority': int,
            'description': str,
            'alwaysApply': bool,
            'type': str,
            'tags': List[str],
            'globs': List[str],
            'keywords': List[str]
        }
    """
    try:
        content = rule_file.read_text(encoding='utf-8')
    except Exception as e:
        print(f"⚠️ 파일 읽기 실패: {rule_file} - {e}")
        return {
            'priority': 10,
            'description': '',
            'alwaysApply': False,
            'type': None,
            'tags': [],
            'globs': [],
            'keywords': []
        }
    
    metadata = {
        'priority': 10,  # 기본값
        'description': '',
        'alwaysApply': False,
        'type': None,
        'tags': [],
        'globs': [],
        'keywords': []
    }
    
    # YAML 프론트매터 파싱
    if content.startswith('---'):
        parts = content.split('---', 2)
        if len(parts) >= 3:
            yaml_content = parts[1]
            for line in yaml_content.split('\n'):
                if ':' in line:
                    key, value = line.split(':', 1)
                    key = key.strip()
                    value = value.strip().strip('"').strip("'")
                    
                    if key == 'priority':
                        metadata['priority'] = int(value) if value.isdigit() else 10
                    elif key == 'description':
                        metadata['description'] = value
                    elif key == 'alwaysApply':
                        metadata['alwaysApply'] = value.lower() in ['true', '1', 'yes']
                    elif key == 'type':
                        metadata['type'] = value.strip('"').strip("'")
                    elif key == 'tags':
                        try:
                            import ast
                            if value.strip().startswith('['):
                                tags_list = ast.literal_eval(value.strip())
                                metadata['tags'] = tags_list if isinstance(tags_list, list) else []
                            else:
                                metadata['tags'] = [value.strip()]
                        except:
                            metadata['tags'] = []
                    elif key == 'globs':
                        try:
                            import ast
                            if value.strip().startswith('['):
                                globs_list = ast.literal_eval(value.strip())
                                metadata['globs'] = globs_list if isinstance(globs_list, list) else []
                            else:
                                metadata['globs'] = [value.strip()]
                        except:
                            metadata['globs'] = []
    
    # 파일명에서 키워드 추출
    filename_lower = rule_file.stem.lower()
    metadata['keywords'] = filename_lower.replace('-', ' ').replace('_', ' ').split()
    
    return metadata

def extract_keywords(problem_description: str) -> List[str]:
    """문제 설명에서 키워드 추출"""
    keywords = []
    
    # 일반적인 키워드
    common_keywords = [
        'ssh', '키', 'hpanel', 'hostinger', 'vps', '배포',
        '보안', '에이전트', '암호', '비밀번호',
        'rules', '규칙', '우선순위', '무시',
        'f드라이브', 'f-drive', 'environment', '환경',
        'workflow', '워크플로우', 'daily', '일일'
    ]
    
    problem_lower = problem_description.lower()
    for keyword in common_keywords:
        if keyword in problem_lower:
            keywords.append(keyword)
    
    # 단어 추출 (간단한 방식)
    words = re.findall(r'\b\w+\b', problem_lower)
    keywords.extend([w for w in words if len(w) > 3])
    
    return list(set(keywords))  # 중복 제거

def search_rules_files(problem_description: str, rules_dir: Optional[Path] = None) -> List[Dict]:
    """
    문제 설명과 관련된 Rules 파일 검색
    
    Args:
        problem_description: 문제 설명
        rules_dir: Rules 디렉토리 경로 (None이면 자동 탐색)
    
    Returns:
        [
            {
                'file': 'ssh-key-hpanel-priority.mdc',
                'path': '.cursor/rules/ssh-key-hpanel-priority.mdc',
                'priority': 0,
                'description': 'SSH 키 문제 해결 시 hPanel 방법 우선 규칙',
                'keywords': ['ssh', 'hpanel', '키']
            },
            ...
        ]
    """
    if rules_dir is None:
        workspace_root = get_workspace_root()
        rules_dir = workspace_root / ".cursor" / "rules"
    
    if not rules_dir.exists():
        print(f"⚠️ Rules 디렉토리를 찾을 수 없습니다: {rules_dir}")
        return []
    
    # Rules 파일 목록
    rules_files = list(rules_dir.glob("*.mdc"))
    
    if not rules_files:
        return []
    
    # 문제 설명에서 키워드 추출
    keywords = extract_keywords(problem_description)
    
    # 각 Rules 파일 검색
    related_rules = []
    for rule_file in rules_files:
        # Rules 파일 메타데이터 읽기
        metadata = parse_rule_metadata(rule_file)
        
        # 키워드 매칭 확인
        matches = False
        
        # 1. 파일명에서 키워드 매칭
        filename_lower = rule_file.stem.lower()
        for keyword in keywords:
            if keyword.lower() in filename_lower:
                matches = True
                break
        
        # 2. Description에서 키워드 매칭
        if not matches:
            description_lower = metadata.get('description', '').lower()
            for keyword in keywords:
                if keyword.lower() in description_lower:
                    matches = True
                    break
        
        # 3. Tags에서 키워드 매칭
        if not matches:
            tags = metadata.get('tags', [])
            for tag in tags:
                if any(keyword.lower() in str(tag).lower() for keyword in keywords):
                    matches = True
                    break
        
        # 4. Keywords에서 매칭
        if not matches:
            rule_keywords = metadata.get('keywords', [])
            if any(kw.lower() in ' '.join(rule_keywords).lower() for kw in keywords):
                matches = True
        
        if matches:
            related_rules.append({
                'file': rule_file.name,
                'path': str(rule_file),
                'priority': metadata.get('priority', 10),
                'description': metadata.get('description', ''),
                'type': metadata.get('type'),
                'tags': metadata.get('tags', []),
                'keywords': keywords
            })
    
    # 우선순위 순 정렬
    related_rules.sort(key=lambda x: x['priority'])
    
    return related_rules

def main():
    """메인 함수 (테스트용)"""
    if len(sys.argv) > 1:
        problem = ' '.join(sys.argv[1:])
    else:
        problem = "SSH 키 문제 해결"
    
    print(f"🔍 검색 쿼리: {problem}\n")
    
    results = search_rules_files(problem)
    
    if not results:
        print("❌ 관련 Rules 파일을 찾을 수 없습니다.")
        return
    
    print(f"✅ {len(results)}개의 관련 Rules 파일 발견:\n")
    
    for rule in results:
        priority_icon = "🚨" if rule['priority'] == 0 else "📌"
        print(f"{priority_icon} [{rule['priority']}] {rule['file']}")
        print(f"   Description: {rule['description']}")
        if rule.get('tags'):
            print(f"   Tags: {', '.join(rule['tags'])}")
        print()

if __name__ == "__main__":
    main()

