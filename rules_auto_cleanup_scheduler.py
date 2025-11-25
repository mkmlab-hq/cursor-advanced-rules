#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Rules 자동 최적화 스케줄러
- 주 1회 자동 실행
- 30일 미사용 룰 자동 아카이브
- 1000줄 이상 룰 경고 알림
- 주간 리포트 자동 생성
"""

import json
import shutil
from pathlib import Path
from datetime import datetime, timedelta
import re
from collections import defaultdict

WORKSPACE = Path(__file__).parent.parent
RULES_DIR = WORKSPACE / ".cursor" / "rules"
ARCHIVE_DIR = WORKSPACE / ".cursor" / "rules_archive"
DAILY_DIR = WORKSPACE / "daily" / datetime.now().strftime("%Y-%m-%d")

def ensure_dirs():
    """필요한 디렉토리 생성"""
    ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)
    DAILY_DIR.mkdir(parents=True, exist_ok=True)

def archive_unused_rules(days_threshold=30, dry_run=False):
    """30일 미사용 룰 자동 아카이브"""
    ensure_dirs()
    
    cutoff_date = datetime.now() - timedelta(days=days_threshold)
    archived = []
    
    for rule_file in RULES_DIR.glob("*.mdc"):
        try:
            # 마지막 수정 시간 확인
            mtime = datetime.fromtimestamp(rule_file.stat().st_mtime)
            
            if mtime < cutoff_date:
                # 아카이브 대상
                archive_path = ARCHIVE_DIR / rule_file.name
                
                if not dry_run:
                    shutil.move(str(rule_file), str(archive_path))
                
                archived.append({
                    "name": rule_file.name,
                    "last_modified": mtime.strftime("%Y-%m-%d"),
                    "days_unused": (datetime.now() - mtime).days
                })
                print(f"  {'[DRY RUN] ' if dry_run else ''}📦 {rule_file.name} → 아카이브 ({mtime.strftime('%Y-%m-%d')}, {days_threshold}일+ 미사용)")
        except Exception as e:
            print(f"  ⚠️ {rule_file.name}: {e}")
    
    return archived

def check_long_rules(line_threshold=1000):
    """1000줄 이상 룰 경고 알림"""
    warnings = []
    
    for rule_file in RULES_DIR.glob("*.mdc"):
        try:
            content = rule_file.read_text(encoding='utf-8')
            lines = len(content.split('\n'))
            
            if lines > line_threshold:
                warnings.append({
                    "name": rule_file.name,
                    "lines": lines,
                    "size_kb": rule_file.stat().st_size / 1024
                })
                print(f"  ⚠️ {rule_file.name}: {lines}줄 ({rule_file.stat().st_size / 1024:.1f}KB) - 너무 김!")
        except Exception as e:
            print(f"  ⚠️ {rule_file.name}: {e}")
    
    return warnings

def generate_weekly_report():
    """주간 리포트 자동 생성"""
    ensure_dirs()
    
    # 최근 7일 통계
    week_ago = datetime.now() - timedelta(days=7)
    
    stats = {
        "total_rules": len(list(RULES_DIR.glob("*.mdc"))),
        "always_apply": 0,
        "priority_distribution": defaultdict(int),
        "recently_modified": 0,
        "unused_rules": 0,
        "long_rules": 0
    }
    
    for rule_file in RULES_DIR.glob("*.mdc"):
        try:
            content = rule_file.read_text(encoding='utf-8')
            
            # alwaysApply 확인
            if re.search(r'alwaysApply:\s*true', content, re.IGNORECASE):
                stats["always_apply"] += 1
            
            # Priority 확인
            priority_match = re.search(r'priority:\s*(\d+)', content)
            if priority_match:
                priority = int(priority_match.group(1))
                stats["priority_distribution"][priority] += 1
            
            # 최근 수정 확인
            mtime = datetime.fromtimestamp(rule_file.stat().st_mtime)
            if mtime > week_ago:
                stats["recently_modified"] += 1
            
            # 미사용 확인 (30일+)
            if mtime < datetime.now() - timedelta(days=30):
                stats["unused_rules"] += 1
            
            # 긴 룰 확인 (1000줄+)
            if len(content.split('\n')) > 1000:
                stats["long_rules"] += 1
                
        except Exception as e:
            print(f"  ⚠️ {rule_file.name}: {e}")
    
    # 리포트 생성
    report = []
    report.append("=" * 70)
    report.append("📊 Rules 주간 리포트")
    report.append("=" * 70)
    report.append(f"생성 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append(f"기간: {week_ago.strftime('%Y-%m-%d')} ~ {datetime.now().strftime('%Y-%m-%d')}")
    report.append("")
    
    report.append("## 📈 기본 통계")
    report.append(f"총 Rules: {stats['total_rules']}개")
    report.append(f"alwaysApply: {stats['always_apply']}개")
    report.append(f"최근 수정 (7일): {stats['recently_modified']}개")
    report.append(f"미사용 (30일+): {stats['unused_rules']}개")
    report.append(f"긴 룰 (1000줄+): {stats['long_rules']}개")
    report.append("")
    
    report.append("## 🎯 Priority 분포")
    for priority in sorted(stats['priority_distribution'].keys()):
        report.append(f"Priority {priority}: {stats['priority_distribution'][priority]}개")
    report.append("")
    
    report.append("## 💡 권장 사항")
    recommendations = []
    
    if stats['always_apply'] > 20:
        recommendations.append(f"🔸 alwaysApply가 {stats['always_apply']}개입니다. 16개 이하로 줄이세요.")
    
    if stats['unused_rules'] > 10:
        recommendations.append(f"🔸 {stats['unused_rules']}개 Rules가 30일+ 미사용입니다. 아카이브를 고려하세요.")
    
    if stats['long_rules'] > 0:
        recommendations.append(f"🔸 {stats['long_rules']}개 Rules가 1000줄 이상입니다. 분할을 고려하세요.")
    
    if recommendations:
        for rec in recommendations:
            report.append(rec)
    else:
        report.append("✅ 현재 설정이 적절합니다!")
    
    report.append("")
    report.append("=" * 70)
    
    report_text = "\n".join(report)
    
    # 리포트 저장
    report_file = DAILY_DIR / f"rules_weekly_report_{datetime.now().strftime('%Y%m%d')}.txt"
    report_file.write_text(report_text, encoding='utf-8')
    
    # JSON 저장
    json_file = DAILY_DIR / f"rules_weekly_stats_{datetime.now().strftime('%Y%m%d')}.json"
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump({
            "generated_at": datetime.now().isoformat(),
            "stats": stats
        }, f, indent=2, ensure_ascii=False)
    
    print(f"  💾 리포트 저장: {report_file}")
    print(f"  💾 JSON 저장: {json_file}")
    
    return report_text

def main(dry_run=False, archive_unused=True, check_long=True, generate_report=True):
    """메인 실행"""
    print("=" * 70)
    print("🔄 Rules 자동 최적화 스케줄러")
    print("=" * 70)
    print(f"모드: {'DRY RUN (시뮬레이션)' if dry_run else '실제 실행'}")
    print(f"실행 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    results = {
        "archived": [],
        "warnings": [],
        "report": None
    }
    
    # 1. 미사용 룰 아카이브
    if archive_unused:
        print("1️⃣ 미사용 룰 아카이브 (30일+)...")
        results["archived"] = archive_unused_rules(days_threshold=30, dry_run=dry_run)
        print(f"  ✅ {len(results['archived'])}개 Rules 아카이브")
        print()
    
    # 2. 긴 룰 경고
    if check_long:
        print("2️⃣ 긴 룰 확인 (1000줄+)...")
        results["warnings"] = check_long_rules(line_threshold=1000)
        if results["warnings"]:
            print(f"  ⚠️ {len(results['warnings'])}개 Rules 경고")
        else:
            print("  ✅ 긴 룰 없음")
        print()
    
    # 3. 주간 리포트 생성
    if generate_report:
        print("3️⃣ 주간 리포트 생성...")
        results["report"] = generate_weekly_report()
        print("  ✅ 리포트 생성 완료")
        print()
    
    # 요약
    print("=" * 70)
    print("📊 실행 요약")
    print("=" * 70)
    print(f"아카이브: {len(results['archived'])}개")
    print(f"경고: {len(results['warnings'])}개")
    print(f"리포트: {'생성됨' if results['report'] else '생성 안 됨'}")
    print()
    
    if dry_run:
        print("⚠️ DRY RUN 모드입니다. 실제로는 변경되지 않았습니다.")
    else:
        print("✅ 자동 최적화 완료!")
    
    return results

if __name__ == "__main__":
    import sys
    
    dry_run = "--dry-run" in sys.argv
    main(dry_run=dry_run)

