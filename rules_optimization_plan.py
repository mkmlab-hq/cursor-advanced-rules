#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Rules 최적화 계획 생성
- Priority 0 Rules 분석 및 재조정 제안
- alwaysApply Rules 분석 및 축소 제안
"""

import json
from pathlib import Path
from datetime import datetime
from collections import defaultdict

WORKSPACE = Path(__file__).parent.parent
ANALYSIS_FILE = WORKSPACE / "daily" / datetime.now().strftime("%Y-%m-%d") / "rules_analysis.json"

def load_analysis():
    """분석 데이터 로드"""
    if not ANALYSIS_FILE.exists():
        print("❌ 분석 파일이 없습니다. 먼저 rules_diagnostics.py를 실행하세요.")
        return None
    
    with open(ANALYSIS_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def analyze_priority_0_rules(data):
    """Priority 0 Rules 분석"""
    priority_0 = [r for r in data['rules'] if r.get('priority') == 0]
    
    print("=" * 70)
    print("🎯 Priority 0 Rules 분석 (18개)")
    print("=" * 70)
    
    # 카테고리별 분류
    categories = defaultdict(list)
    
    for rule in priority_0:
        name = rule['name']
        desc = rule.get('description', '')
        
        # 카테고리 분류
        if 'layer0' in name.lower() or 'autonomous' in name.lower():
            categories['Layer 0 (자율 시스템)'].append(rule)
        elif 'critical' in name.lower() or 'auto-execution' in name.lower():
            categories['Critical (필수 실행)'].append(rule)
        elif 'f-drive' in name.lower() or 'independence' in name.lower():
            categories['환경 독립성'].append(rule)
        elif 'mcp' in name.lower() or 'mandatory' in name.lower():
            categories['MCP 필수'].append(rule)
        elif 'rules-priority' in name.lower() or 'enforcement' in name.lower():
            categories['Rules 관리'].append(rule)
        elif 'ssh' in name.lower() or 'key' in name.lower():
            categories['SSH/보안'].append(rule)
        elif 'subprocess' in name.lower() or 'env' in name.lower():
            categories['환경 변수'].append(rule)
        elif 'korean-medicine' in name.lower() or 'verification' in name.lower():
            categories['검증 필수'].append(rule)
        elif 'date' in name.lower() or 'validation' in name.lower():
            categories['날짜 검증'].append(rule)
        else:
            categories['기타'].append(rule)
    
    # 카테고리별 출력
    for category, rules in categories.items():
        print(f"\n📁 {category} ({len(rules)}개)")
        for rule in rules:
            always = "✅ Always" if rule.get('always_apply') else "⚪"
            print(f"  {always} {rule['name']}")
            if rule.get('description'):
                print(f"     └─ {rule['description'][:60]}...")
    
    # 권장 사항
    print("\n" + "=" * 70)
    print("💡 Priority 0 최적화 제안")
    print("=" * 70)
    
    recommendations = []
    
    # Layer 0 통합 제안
    layer0_count = len(categories.get('Layer 0 (자율 시스템)', []))
    if layer0_count > 3:
        recommendations.append({
            "action": "통합",
            "target": f"Layer 0 Rules {layer0_count}개",
            "suggestion": "layer0-*.mdc 파일들을 하나로 통합 (layer0-core.mdc)",
            "priority": "high"
        })
    
    # Critical 통합 제안
    critical_count = len(categories.get('Critical (필수 실행)', []))
    if critical_count > 1:
        recommendations.append({
            "action": "통합",
            "target": f"Critical Rules {critical_count}개",
            "suggestion": "CRITICAL-*.mdc 파일들을 하나로 통합",
            "priority": "high"
        })
    
    # Priority 0 → 1 조정 제안
    if len(priority_0) > 10:
        # 핵심만 Priority 0 유지, 나머지는 Priority 1로
        keep_priority_0 = [
            "f-drive-absolute-independence.mdc",
            "rules-priority-enforcement.mdc",
            "CRITICAL-AUTO-EXECUTION.mdc",
            "mcp-auto-execution-enforcement.mdc"
        ]
        
        move_to_1 = [r for r in priority_0 if r['name'] not in keep_priority_0]
        
        recommendations.append({
            "action": "Priority 조정",
            "target": f"{len(move_to_1)}개 Rules",
            "suggestion": f"Priority 0 → 1로 조정: {', '.join([r['name'] for r in move_to_1[:5]])}...",
            "priority": "high"
        })
    
    for rec in recommendations:
        print(f"\n🔸 [{rec['priority'].upper()}] {rec['action']}: {rec['target']}")
        print(f"   → {rec['suggestion']}")
    
    return {
        "total": len(priority_0),
        "categories": {k: len(v) for k, v in categories.items()},
        "recommendations": recommendations
    }

def analyze_always_apply_rules(data):
    """alwaysApply Rules 분석"""
    always_apply = [r for r in data['rules'] if r.get('always_apply')]
    
    print("\n" + "=" * 70)
    print("📊 alwaysApply Rules 분석 (77개)")
    print("=" * 70)
    
    # Priority별 분류
    by_priority = defaultdict(list)
    for rule in always_apply:
        priority = rule.get('priority', 5)
        by_priority[priority].append(rule)
    
    print("\nPriority별 분포:")
    for priority in sorted(by_priority.keys()):
        count = len(by_priority[priority])
        print(f"  Priority {priority}: {count}개")
    
    # 권장 사항
    print("\n" + "=" * 70)
    print("💡 alwaysApply 최적화 제안")
    print("=" * 70)
    
    recommendations = []
    
    # 목표: 77개 → 7개 이하
    target_count = 7
    reduce_count = len(always_apply) - target_count
    
    # Priority 0, 1만 alwaysApply 유지
    keep_always = [
        r for r in always_apply 
        if r.get('priority') in [0, 1] and r.get('name') in [
            "f-drive-absolute-independence.mdc",
            "rules-priority-enforcement.mdc",
            "CRITICAL-AUTO-EXECUTION.mdc",
            "mcp-auto-execution-enforcement.mdc",
            "layer0-autonomous-brain.mdc",
            "global.mdc",
            "company-environment-mcp-mandatory.mdc"
        ]
    ]
    
    # 나머지는 intelligent 또는 file-specific로 변경
    change_to_intelligent = [
        r for r in always_apply 
        if r not in keep_always and r.get('priority') in [1, 2]
    ]
    
    change_to_file_specific = [
        r for r in always_apply 
        if r not in keep_always and r.get('priority') >= 2 and r.get('globs')
    ]
    
    recommendations.append({
        "action": "alwaysApply → intelligent",
        "count": len(change_to_intelligent),
        "target": "Priority 1-2 Rules",
        "suggestion": f"{len(change_to_intelligent)}개 Rules를 intelligent 타입으로 변경"
    })
    
    recommendations.append({
        "action": "alwaysApply → file-specific",
        "count": len(change_to_file_specific),
        "target": "Priority 2+ Rules (globs 있음)",
        "suggestion": f"{len(change_to_file_specific)}개 Rules를 file-specific 타입으로 변경"
    })
    
    for rec in recommendations:
        print(f"\n🔸 {rec['action']}: {rec['count']}개")
        print(f"   → {rec['suggestion']}")
    
    print(f"\n✅ 최종 목표: {len(keep_always)}개 alwaysApply 유지")
    
    return {
        "total": len(always_apply),
        "keep": len(keep_always),
        "change_to_intelligent": len(change_to_intelligent),
        "change_to_file_specific": len(change_to_file_specific),
        "recommendations": recommendations
    }

def generate_optimization_plan():
    """최적화 계획 생성"""
    data = load_analysis()
    if not data:
        return
    
    print("🔍 Rules 최적화 계획 생성 중...\n")
    
    # Priority 0 분석
    priority_0_analysis = analyze_priority_0_rules(data)
    
    # alwaysApply 분석
    always_apply_analysis = analyze_always_apply_rules(data)
    
    # 최종 계획
    print("\n" + "=" * 70)
    print("📋 최종 최적화 계획")
    print("=" * 70)
    
    plan = {
        "generated_at": datetime.now().isoformat(),
        "current_state": {
            "total_rules": data['total_rules'],
            "always_apply_count": always_apply_analysis['total'],
            "priority_0_count": priority_0_analysis['total']
        },
        "optimization_plan": {
            "step_1": {
                "action": "미사용 Rules 아카이브",
                "status": "✅ 완료",
                "count": 3
            },
            "step_2": {
                "action": "Priority 0 최적화",
                "target": "18개 → 10개 이하",
                "recommendations": priority_0_analysis['recommendations']
            },
            "step_3": {
                "action": "alwaysApply 축소",
                "target": "77개 → 7개 이하",
                "keep": always_apply_analysis['keep'],
                "change_to_intelligent": always_apply_analysis['change_to_intelligent'],
                "change_to_file_specific": always_apply_analysis['change_to_file_specific']
            }
        }
    }
    
    # 계획 저장
    plan_file = WORKSPACE / "daily" / datetime.now().strftime("%Y-%m-%d") / "rules_optimization_plan.json"
    plan_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(plan_file, 'w', encoding='utf-8') as f:
        json.dump(plan, f, indent=2, ensure_ascii=False, default=str)
    
    print(f"\n💾 최적화 계획 저장: {plan_file}")
    print("\n✅ 분석 완료!")

if __name__ == "__main__":
    generate_optimization_plan()

