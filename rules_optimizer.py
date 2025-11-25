#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Rules 최적화 실행 스크립트
- Priority 0 → 1 조정
- alwaysApply → intelligent 변경
- 안전한 변경만 실행 (백업 포함)
"""

import json
import shutil
from pathlib import Path
from datetime import datetime
import re

WORKSPACE = Path(__file__).parent.parent
RULES_DIR = WORKSPACE / ".cursor" / "rules"
BACKUP_DIR = WORKSPACE / ".cursor" / "rules_backup" / datetime.now().strftime("%Y%m%d_%H%M%S")
ANALYSIS_FILE = WORKSPACE / "daily" / datetime.now().strftime("%Y-%m-%d") / "rules_analysis.json"

def backup_rules():
    """Rules 백업"""
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    
    for rule_file in RULES_DIR.glob("*.mdc"):
        shutil.copy2(rule_file, BACKUP_DIR / rule_file.name)
    
    print(f"✅ 백업 완료: {BACKUP_DIR}")
    return BACKUP_DIR

def load_analysis():
    """분석 데이터 로드"""
    if not ANALYSIS_FILE.exists():
        print("❌ 분석 파일이 없습니다.")
        return None
    
    with open(ANALYSIS_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def adjust_priority_0_to_1(dry_run=True):
    """Priority 0 → 1 조정 (안전한 변경만)"""
    # 핵심 Priority 0 유지 목록
    keep_priority_0 = [
        "f-drive-absolute-independence.mdc",
        "rules-priority-enforcement.mdc",
        "CRITICAL-AUTO-EXECUTION.mdc",
        "mcp-auto-execution-enforcement.mdc",
        "layer0-autonomous-brain.mdc",
        "company-environment-mcp-mandatory.mdc",
        "subprocess-env-variable-rule.mdc",
        "ssh-key-hpanel-priority.mdc",
        "korean-medicine-verification-required.mdc",
        "date-validation-mandatory.mdc"
    ]
    
    changed = []
    
    for rule_file in RULES_DIR.glob("*.mdc"):
        if rule_file.name in keep_priority_0:
            continue
        
        try:
            content = rule_file.read_text(encoding='utf-8')
            
            # Priority 0인지 확인
            if re.search(r'priority:\s*0', content):
                # Priority 0 → 1로 변경
                new_content = re.sub(r'priority:\s*0', 'priority: 1', content)
                
                if not dry_run:
                    rule_file.write_text(new_content, encoding='utf-8')
                
                changed.append(rule_file.name)
                print(f"  {'[DRY RUN] ' if dry_run else ''}✅ {rule_file.name}: Priority 0 → 1")
        except Exception as e:
            print(f"  ⚠️ {rule_file.name}: {e}")
    
    return changed

def change_always_apply_to_intelligent(dry_run=True, max_changes=None):
    """alwaysApply → intelligent 변경"""
    # Priority 0 유지 (8개)
    keep_priority_0 = [
        "company-environment-mcp-mandatory.mdc",
        "CRITICAL-AUTO-EXECUTION.mdc",
        "date-validation-mandatory.mdc",
        "f-drive-absolute-independence.mdc",
        "layer0-autonomous-brain.mdc",
        "rules-priority-enforcement.mdc",
        "ssh-key-hpanel-priority.mdc",
        "subprocess-env-variable-rule.mdc"
    ]
    
    # Priority 1 핵심 유지 (8개)
    keep_priority_1 = [
        "athena-emergency-recovery-enhanced.mdc",
        "auto-memory-fusion.mdc",
        "auto-reflection-system.mdc",
        "mkm12-mandatory-application.mdc",
        "optimal-condition-enhancement.mdc",
        "memory-search-enhancement.mdc",
        "sqlite-auto-utilization.mdc",
        "metacognition-realistic.mdc"
    ]
    
    # Priority 1 추가 제거 대상 (4개)
    # - spice-auto-code-review: SPICE 자동 생성, file-specific 가능
    # - ssh-passphrase-hpanel-mandatory: ssh-key-hpanel-priority와 중복
    # - systematic-thinking-integration: intelligent로 변경 가능
    # - user-feedback-immediate-action: intelligent로 변경 가능
    
    keep_all = keep_priority_0 + keep_priority_1
    
    changed = []
    
    for rule_file in RULES_DIR.glob("*.mdc"):
        if rule_file.name in keep_all:
            continue
        
        if max_changes and len(changed) >= max_changes:
            break
        
        try:
            content = rule_file.read_text(encoding='utf-8')
            
            # alwaysApply: true인지 확인
            if re.search(r'alwaysApply:\s*true', content, re.IGNORECASE):
                # Priority 확인
                priority_match = re.search(r'priority:\s*(\d+)', content)
                priority = int(priority_match.group(1)) if priority_match else 5
                
                # globs 확인
                has_globs = bool(re.search(r'globs:\s*\[', content))
                
                # 타입 결정
                if has_globs:
                    target_type = "file-specific"
                else:
                    target_type = "intelligent"
                
                # alwaysApply: true → false
                new_content = re.sub(
                    r'alwaysApply:\s*true',
                    'alwaysApply: false',
                    content,
                    flags=re.IGNORECASE
                )
                
                # type 추가 또는 변경
                if not re.search(r'type:\s*', content):
                    # type 필드 추가 (alwaysApply 다음 줄에)
                    new_content = re.sub(
                        r'(alwaysApply:\s*false)',
                        f'\\1\ntype: "{target_type}"',
                        new_content
                    )
                else:
                    new_content = re.sub(
                        r'type:\s*"[^"]*"',
                        f'type: "{target_type}"',
                        new_content
                    )
                
                if not dry_run:
                    rule_file.write_text(new_content, encoding='utf-8')
                
                changed.append({
                    "name": rule_file.name,
                    "type": target_type,
                    "priority": priority
                })
                print(f"  {'[DRY RUN] ' if dry_run else ''}✅ {rule_file.name}: alwaysApply → {target_type} (P{priority})")
        except Exception as e:
            print(f"  ⚠️ {rule_file.name}: {e}")
    
    return changed

def main():
    """메인 실행"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Rules 최적화 실행")
    parser.add_argument("--dry-run", action="store_true", help="시뮬레이션 모드")
    parser.add_argument("--priority-only", action="store_true", help="Priority 조정만")
    parser.add_argument("--always-apply-only", action="store_true", help="alwaysApply 변경만")
    
    args = parser.parse_args()
    
    print("=" * 70)
    print("🔄 Rules 최적화 실행")
    print("=" * 70)
    print(f"모드: {'DRY RUN (시뮬레이션)' if args.dry_run else '실제 실행'}")
    print()
    
    # 백업
    if not args.dry_run:
        backup_dir = backup_rules()
        print()
    
    # Priority 0 → 1 조정
    if not args.always_apply_only:
        print("1️⃣ Priority 0 → 1 조정 중...")
        priority_changed = adjust_priority_0_to_1(dry_run=args.dry_run)
        print(f"   ✅ {len(priority_changed)}개 Rules 변경")
        print()
    
    # alwaysApply → intelligent 변경
    if not args.priority_only:
        print("2️⃣ alwaysApply → intelligent 변경 중...")
        always_changed = change_always_apply_to_intelligent(dry_run=args.dry_run, max_changes=20)
        print(f"   ✅ {len(always_changed)}개 Rules 변경")
        print()
    
    print("=" * 70)
    if args.dry_run:
        print("⚠️ DRY RUN 모드입니다. 실제로는 변경되지 않았습니다.")
        print("실제 실행하려면 --dry-run 옵션을 제거하세요.")
    else:
        print("✅ 최적화 완료!")
        print(f"💾 백업 위치: {backup_dir}")

if __name__ == "__main__":
    main()

