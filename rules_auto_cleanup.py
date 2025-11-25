#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Rules 자동 정리 시스템
- 중복 Rules 자동 제거
- 오래된 자동 학습 Rules 아카이브
- Rules 구조 최적화
- 정기 정리 프로세스
"""

import os
import sys
import json
import shutil
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Any
import re

WORKSPACE_ROOT = Path(__file__).parent.parent
RULES_DIR = WORKSPACE_ROOT / ".cursor" / "rules"
PATTERNS_DIR = WORKSPACE_ROOT / ".cursor" / "patterns"
ARCHIVE_DIR = WORKSPACE_ROOT / ".cursor" / "rules_archive"
ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)

# Rules 최적화 기준
OPTIMAL_RULES_COUNT = 42  # 최소 Rules 파일 수
TARGET_RULES_COUNT = 6  # 최적 Layer 구조
MAX_AUTO_LEARNED_AGE_DAYS = 30  # 30일 이상 사용되지 않은 자동 학습 Rules 아카이브


class RulesAutoCleanup:
    """Rules 자동 정리 시스템"""
    
    def __init__(self):
        self.rules_dir = RULES_DIR
        self.archive_dir = ARCHIVE_DIR
        self.cleanup_stats = {
            "duplicates_removed": 0,
            "old_rules_archived": 0,
            "total_rules_before": 0,
            "total_rules_after": 0,
            "removed_files": [],
            "archived_files": []
        }
    
    def cleanup_all(self, dry_run: bool = False) -> Dict[str, Any]:
        """전체 정리 프로세스 실행"""
        print("="*70)
        print("🔄 Rules 자동 정리 시스템")
        print("="*70)
        print(f"⏰ 실행 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"모드: {'DRY RUN (시뮬레이션)' if dry_run else '실제 실행'}")
        print()
        
        # 현재 Rules 파일 수
        all_rules = list(self.rules_dir.glob("*.mdc"))
        self.cleanup_stats["total_rules_before"] = len(all_rules)
        print(f"📊 현재 Rules 파일 수: {len(all_rules)}개")
        print()
        
        # 1. 중복 Rules 제거
        print("1️⃣ 중복 Rules 감지 및 제거 중...")
        duplicates_removed = self.remove_duplicate_rules(dry_run)
        self.cleanup_stats["duplicates_removed"] = duplicates_removed
        print(f"   ✅ 중복 제거: {duplicates_removed}개")
        print()
        
        # 2. 오래된 자동 학습 Rules 아카이브
        print("2️⃣ 오래된 자동 학습 Rules 아카이브 중...")
        old_archived = self.archive_old_auto_learned(dry_run)
        self.cleanup_stats["old_rules_archived"] = old_archived
        print(f"   ✅ 아카이브: {old_archived}개")
        print()
        
        # 3. Rules 구조 최적화
        print("3️⃣ Rules 구조 최적화 중...")
        optimized = self.optimize_rules_structure(dry_run)
        print(f"   ✅ 최적화 완료")
        print()
        
        # 최종 결과
        all_rules_after = list(self.rules_dir.glob("*.mdc"))
        self.cleanup_stats["total_rules_after"] = len(all_rules_after)
        
        print("="*70)
        print("📊 정리 결과")
        print("="*70)
        print(f"정리 전: {self.cleanup_stats['total_rules_before']}개")
        print(f"정리 후: {self.cleanup_stats['total_rules_after']}개")
        print(f"감소: {self.cleanup_stats['total_rules_before'] - self.cleanup_stats['total_rules_after']}개")
        print()
        
        if duplicates_removed > 0:
            print(f"✅ 중복 제거: {duplicates_removed}개")
        if old_archived > 0:
            print(f"✅ 아카이브: {old_archived}개")
        
        print()
        
        if dry_run:
            print("⚠️ DRY RUN 모드입니다. 실제로는 변경되지 않았습니다.")
        else:
            print("✅ Rules 정리 완료!")
        
        return self.cleanup_stats
    
    def remove_duplicate_rules(self, dry_run: bool = False) -> int:
        """중복 Rules 제거"""
        all_rules = list(self.rules_dir.glob("*.mdc"))
        removed_count = 0
        
        # 파일 내용 기반 유사도 검사
        rule_contents = {}
        for rule_file in all_rules:
            try:
                content = rule_file.read_text(encoding='utf-8')
                # 메타데이터 제거 후 핵심 내용만 추출
                core_content = self._extract_core_content(content)
                rule_contents[rule_file] = core_content
            except Exception as e:
                print(f"   ⚠️ 파일 읽기 실패: {rule_file.name} - {e}")
                continue
        
        # 유사도 기반 중복 감지
        processed = set()
        duplicate_groups = []
        
        for rule1, content1 in rule_contents.items():
            if rule1 in processed:
                continue
            
            group = [rule1]
            
            for rule2, content2 in rule_contents.items():
                if rule1 == rule2 or rule2 in processed:
                    continue
                
                # 유사도 계산 (간단한 Jaccard 유사도)
                similarity = self._calculate_similarity(content1, content2)
                
                if similarity > 0.8:  # 80% 이상 유사하면 중복으로 간주
                    group.append(rule2)
                    processed.add(rule2)
            
            if len(group) > 1:
                duplicate_groups.append(group)
                processed.add(rule1)
        
        # 중복 그룹에서 품질이 높은 것만 남기고 나머지 제거
        for group in duplicate_groups:
            # 우선순위: priority 낮을수록, 파일 크기 적절한 것, 최근 수정된 것
            best_rule = self._select_best_rule(group)
            others = [r for r in group if r != best_rule]
            
            for rule_file in others:
                if not dry_run:
                    # 백업 후 제거
                    backup_path = self.archive_dir / f"duplicate_{rule_file.name}"
                    shutil.copy2(rule_file, backup_path)
                    rule_file.unlink()
                    self.cleanup_stats["removed_files"].append(str(rule_file.relative_to(WORKSPACE_ROOT)))
                
                removed_count += 1
                print(f"   ❌ 중복 제거: {rule_file.name} (유지: {best_rule.name})")
        
        return removed_count
    
    def archive_old_auto_learned(self, dry_run: bool = False) -> int:
        """오래된 자동 학습 Rules 아카이브"""
        auto_learned_rules = list(self.rules_dir.glob("*auto-learned*.mdc"))
        archived_count = 0
        cutoff_date = datetime.now() - timedelta(days=MAX_AUTO_LEARNED_AGE_DAYS)
        
        for rule_file in auto_learned_rules:
            try:
                # 파일 수정 시간 확인
                mtime = datetime.fromtimestamp(rule_file.stat().st_mtime)
                
                if mtime < cutoff_date:
                    if not dry_run:
                        # 아카이브로 이동
                        archive_path = self.archive_dir / rule_file.name
                        shutil.move(str(rule_file), str(archive_path))
                        self.cleanup_stats["archived_files"].append(str(rule_file.relative_to(WORKSPACE_ROOT)))
                    
                    archived_count += 1
                    print(f"   📦 아카이브: {rule_file.name} ({mtime.strftime('%Y-%m-%d')})")
            except Exception as e:
                print(f"   ⚠️ 아카이브 실패: {rule_file.name} - {e}")
        
        return archived_count
    
    def optimize_rules_structure(self, dry_run: bool = False) -> bool:
        """Rules 구조 최적화"""
        # Layer 구조 유지 확인
        layer1_rules = list(self.rules_dir.glob("layer1-*.mdc"))
        layer2_rules = list(self.rules_dir.glob("layer2-*.mdc"))
        
        print(f"   📋 Layer 1 Rules: {len(layer1_rules)}개")
        print(f"   📋 Layer 2 Rules: {len(layer2_rules)}개")
        
        # 자동 생성 Rules는 별도 폴더로 이동 (선택적)
        # 현재는 아카이브만 수행
        
        return True
    
    def _extract_core_content(self, content: str) -> str:
        """Rules 파일에서 핵심 내용만 추출"""
        # 프론트매터 제거
        if content.startswith("---"):
            parts = content.split("---", 2)
            if len(parts) >= 3:
                content = parts[2]
        
        # 주석 제거
        lines = content.split('\n')
        core_lines = []
        for line in lines:
            # 주석 제거 (단, 중요한 섹션은 유지)
            if line.strip().startswith('#') and '핵심' not in line and '원칙' not in line:
                continue
            core_lines.append(line)
        
        return '\n'.join(core_lines)
    
    def _calculate_similarity(self, content1: str, content2: str) -> float:
        """유사도 계산 (Jaccard 유사도)"""
        # 단어 집합으로 변환
        words1 = set(re.findall(r'\w+', content1.lower()))
        words2 = set(re.findall(r'\w+', content2.lower()))
        
        if not words1 or not words2:
            return 0.0
        
        intersection = len(words1 & words2)
        union = len(words1 | words2)
        
        return intersection / union if union > 0 else 0.0
    
    def _select_best_rule(self, rule_files: List[Path]) -> Path:
        """중복 그룹에서 가장 좋은 Rules 선택"""
        best_rule = None
        best_score = -1
        
        for rule_file in rule_files:
            try:
                content = rule_file.read_text(encoding='utf-8')
                
                # 점수 계산
                score = 0
                
                # 1. Priority 낮을수록 좋음 (0이 최고)
                priority_match = re.search(r'priority:\s*(\d+)', content)
                if priority_match:
                    priority = int(priority_match.group(1))
                    score += (10 - priority) * 10  # priority 0 = 100점, 1 = 90점, ...
                
                # 2. alwaysApply 있으면 가점
                if 'alwaysApply: true' in content:
                    score += 20
                
                # 3. 파일 크기 적절 (500-2000 바이트)
                file_size = rule_file.stat().st_size
                if 500 <= file_size <= 2000:
                    score += 10
                elif file_size > 5000:  # 너무 크면 감점
                    score -= 10
                
                # 4. 최근 수정된 것 가점
                mtime = datetime.fromtimestamp(rule_file.stat().st_mtime)
                days_old = (datetime.now() - mtime).days
                if days_old < 7:
                    score += 5
                
                if score > best_score:
                    best_score = score
                    best_rule = rule_file
            except Exception as e:
                print(f"   ⚠️ Rules 평가 실패: {rule_file.name} - {e}")
                continue
        
        return best_rule or rule_files[0]  # 기본값: 첫 번째 파일


def main():
    """메인 실행 함수"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Rules 자동 정리 시스템")
    parser.add_argument("--dry-run", action="store_true", help="시뮬레이션 모드 (실제 변경 없음)")
    parser.add_argument("--archive-only", action="store_true", help="아카이브만 실행")
    parser.add_argument("--duplicates-only", action="store_true", help="중복 제거만 실행")
    
    args = parser.parse_args()
    
    cleanup = RulesAutoCleanup()
    
    if args.archive_only:
        result = cleanup.archive_old_auto_learned(dry_run=args.dry_run)
        print(f"✅ 아카이브 완료: {result}개")
    elif args.duplicates_only:
        result = cleanup.remove_duplicate_rules(dry_run=args.dry_run)
        print(f"✅ 중복 제거 완료: {result}개")
    else:
        stats = cleanup.cleanup_all(dry_run=args.dry_run)
        
        # 결과를 JSON으로 저장
        report_path = WORKSPACE_ROOT / "daily" / datetime.now().strftime("%Y-%m-%d") / f"rules_cleanup_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        report_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(stats, f, indent=2, ensure_ascii=False)
        
        print(f"📄 보고서 저장: {report_path}")


if __name__ == "__main__":
    main()

