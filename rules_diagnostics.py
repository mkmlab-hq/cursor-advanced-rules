#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cursor Rules 진단 및 관리 시스템

- 모든 Rules 스캔
- 충돌 감지
- 사용 통계
- 우선순위 분석
"""

import os
from pathlib import Path
from datetime import datetime
import json
import re
from collections import defaultdict
from typing import Dict, List, Tuple

WORKSPACE = Path(__file__).parent.parent
RULES_DIR = WORKSPACE / ".cursor" / "rules"

class RulesManager:
    """Rules 종합 관리"""
    
    def __init__(self):
        self.rules = self.scan_all_rules()
        self.conflicts = []
        self.usage_stats = {}
        self.priority_map = {}
    
    def scan_all_rules(self) -> List[Dict]:
        """모든 Rules 스캔"""
        rules = []
        
        if not RULES_DIR.exists():
            print("⚠️ Rules 디렉토리가 없습니다")
            return rules
        
        for rule_file in RULES_DIR.glob("*.mdc"):
            rule_info = self.parse_rule_file(rule_file)
            rules.append(rule_info)
        
        return rules
    
    def parse_rule_file(self, rule_path: Path) -> Dict:
        """Rule 파일 파싱"""
        try:
            content = rule_path.read_text(encoding='utf-8')
            
            # 메타데이터 추출
            metadata = {}
            if content.startswith("---"):
                parts = content.split("---", 2)
                if len(parts) >= 3:
                    front_matter = parts[1]
                    # YAML 파싱 (간단 버전)
                    for line in front_matter.split('\n'):
                        if ':' in line:
                            key, value = line.split(':', 1)
                            metadata[key.strip()] = value.strip().strip('"').strip("'")
            
            # Priority 추출 (숫자로 변환)
            priority = 5  # 기본값
            if 'priority' in metadata:
                try:
                    priority = int(metadata['priority'])
                except (ValueError, TypeError):
                    priority = 5
            
            # alwaysApply 추출
            always_apply = False
            if 'alwaysApply' in metadata:
                always_apply = metadata['alwaysApply'].lower() == "true"
            
            return {
                "name": rule_path.name,
                "path": str(rule_path.relative_to(WORKSPACE)),
                "size": rule_path.stat().st_size,
                "modified": datetime.fromtimestamp(rule_path.stat().st_mtime),
                "priority": priority,
                "always_apply": always_apply,
                "description": metadata.get("description", ""),
                "globs": metadata.get("globs", ""),
                "type": metadata.get("type", ""),
                "tags": metadata.get("tags", ""),
                "content_lines": len(content.split('\n')),
                "metadata": metadata
            }
        except Exception as e:
            return {
                "name": rule_path.name,
                "error": str(e),
                "priority": 5,
                "always_apply": False
            }
    
    def detect_conflicts(self):
        """Rules 충돌 감지"""
        conflicts = []
        
        # Priority 0-2 (항상 적용)는 충돌 가능성 높음
        always_apply = [r for r in self.rules if r.get("always_apply")]
        
        if len(always_apply) > 10:
            conflicts.append({
                "type": "too_many_always_apply",
                "severity": "high",
                "message": f"{len(always_apply)}개 Rules가 항상 적용됩니다. 컨텍스트 오버로드 위험",
                "rules": [r["name"] for r in always_apply]
            })
        
        # 같은 priority의 Rules
        priority_groups = defaultdict(list)
        for rule in self.rules:
            priority_groups[rule.get("priority", 5)].append(rule["name"])
        
        for priority, rules in priority_groups.items():
            if len(rules) > 15:
                conflicts.append({
                    "type": "same_priority_overload",
                    "severity": "medium",
                    "priority": priority,
                    "message": f"Priority {priority}에 {len(rules)}개 Rules. 적용 순서 불명확",
                    "rules": rules
                })
        
        # 유사한 이름 (중복 가능성)
        names = [r["name"] for r in self.rules]
        for i, name1 in enumerate(names):
            for name2 in names[i+1:]:
                similarity = self._similarity(name1, name2)
                if similarity > 0.8:
                    conflicts.append({
                        "type": "similar_names",
                        "severity": "low",
                        "message": f"유사한 이름: {name1} ↔ {name2}",
                        "similarity": f"{similarity*100:.0f}%"
                    })
        
        # Priority 0이 너무 많으면 경고
        priority_0_count = len([r for r in self.rules if r.get("priority") == 0])
        if priority_0_count > 10:
            conflicts.append({
                "type": "too_many_priority_0",
                "severity": "high",
                "message": f"Priority 0 Rules가 {priority_0_count}개입니다. 최우선 규칙이 너무 많아 효과가 떨어질 수 있습니다.",
                "rules": [r["name"] for r in self.rules if r.get("priority") == 0]
            })
        
        self.conflicts = conflicts
        return conflicts
    
    def _similarity(self, s1: str, s2: str) -> float:
        """문자열 유사도 (Jaccard)"""
        words1 = set(re.findall(r'\w+', s1.lower()))
        words2 = set(re.findall(r'\w+', s2.lower()))
        
        if not words1 or not words2:
            return 0.0
        
        intersection = len(words1 & words2)
        union = len(words1 | words2)
        
        return intersection / union if union > 0 else 0.0
    
    def analyze_usage(self):
        """Rules 사용 분석 (추정)"""
        usage = {}
        
        for rule in self.rules:
            # 마지막 수정 시간 기반 추정
            days_old = (datetime.now() - rule["modified"]).days
            
            if days_old < 7:
                estimated_usage = "high"
            elif days_old < 30:
                estimated_usage = "medium"
            else:
                estimated_usage = "low"
            
            usage[rule["name"]] = {
                "estimated": estimated_usage,
                "days_old": days_old,
                "last_modified": rule["modified"].strftime("%Y-%m-%d")
            }
        
        self.usage_stats = usage
        return usage
    
    def generate_priority_map(self):
        """우선순위 맵 생성"""
        priority_map = defaultdict(list)
        
        for rule in self.rules:
            priority = rule.get("priority", 5)
            priority_map[priority].append({
                "name": rule["name"],
                "always_apply": rule.get("always_apply"),
                "description": rule.get("description", "")[:50]
            })
        
        self.priority_map = dict(sorted(priority_map.items()))
        return self.priority_map
    
    def generate_report(self) -> str:
        """종합 리포트 생성"""
        report = []
        
        report.append("=" * 70)
        report.append("📊 Cursor Rules 진단 리포트")
        report.append("=" * 70)
        report.append(f"생성 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"Rules 디렉토리: {RULES_DIR}")
        report.append("")
        
        # 기본 통계
        report.append("## 📈 기본 통계")
        report.append(f"총 Rules 수: {len(self.rules)}")
        report.append(f"항상 적용 (alwaysApply): {sum(1 for r in self.rules if r.get('always_apply'))}")
        if self.rules:
            avg_size = sum(r.get('size', 0) for r in self.rules) / len(self.rules)
            report.append(f"평균 파일 크기: {avg_size:.0f} bytes ({avg_size/1024:.1f} KB)")
        report.append("")
        
        # Priority 분포
        report.append("## 🎯 Priority 분포")
        for priority, rules in self.priority_map.items():
            report.append(f"Priority {priority}: {len(rules)}개")
            if len(rules) <= 5:
                for rule in rules:
                    status = "✅" if rule["always_apply"] else "⚪"
                    report.append(f"  {status} {rule['name']}")
            else:
                report.append(f"  (많음 - {len(rules)}개)")
        report.append("")
        
        # 충돌 감지
        if self.conflicts:
            report.append("## ⚠️ 감지된 문제")
            for conflict in self.conflicts:
                severity_icon = {
                    "high": "🔴",
                    "medium": "🟡",
                    "low": "🟢"
                }.get(conflict["severity"], "⚪")
                
                report.append(f"{severity_icon} {conflict['type'].upper()}")
                report.append(f"   {conflict['message']}")
                if "rules" in conflict and len(conflict["rules"]) <= 10:
                    report.append(f"   영향받는 Rules: {', '.join(conflict['rules'][:5])}")
                    if len(conflict["rules"]) > 5:
                        report.append(f"   ... 외 {len(conflict['rules'])-5}개")
                report.append("")
        else:
            report.append("## ✅ 충돌 없음")
            report.append("")
        
        # 사용 분석
        report.append("## 📊 사용 분석 (추정)")
        high_usage = [k for k, v in self.usage_stats.items() if v["estimated"] == "high"]
        medium_usage = [k for k, v in self.usage_stats.items() if v["estimated"] == "medium"]
        low_usage = [k for k, v in self.usage_stats.items() if v["estimated"] == "low"]
        
        report.append(f"활발히 사용 (7일 이내): {len(high_usage)}개")
        report.append(f"보통 사용 (30일 이내): {len(medium_usage)}개")
        report.append(f"거의 안 씀 (30일+ 경과): {len(low_usage)}개")
        report.append("")
        
        if low_usage:
            report.append("### 🗑️ 아카이브 고려 대상 (30일+ 미사용)")
            for rule_name in low_usage[:10]:
                days = self.usage_stats[rule_name]["days_old"]
                report.append(f"  - {rule_name} ({days}일 경과)")
        report.append("")
        
        # 권장 사항
        report.append("## 💡 권장 사항")
        
        recommendations = []
        
        if len(self.rules) > 50:
            recommendations.append(f"🔸 Rules가 {len(self.rules)}개로 많습니다. 40개 이하로 줄이는 것을 권장합니다.")
        
        always_apply_count = sum(1 for r in self.rules if r.get('always_apply'))
        if always_apply_count > 10:
            recommendations.append(f"🔸 'alwaysApply' Rules가 {always_apply_count}개입니다. 7개 이하로 줄이세요.")
        
        if len(low_usage) > 20:
            recommendations.append(f"🔸 {len(low_usage)}개 Rules가 30일+ 미사용입니다. 아카이브를 고려하세요.")
        
        high_priority = len(self.priority_map.get(0, [])) + len(self.priority_map.get(1, []))
        if high_priority > 15:
            recommendations.append(f"🔸 높은 Priority (0-1) Rules가 {high_priority}개입니다. 우선순위를 재조정하세요.")
        
        if recommendations:
            for rec in recommendations:
                report.append(rec)
        else:
            report.append("✅ 현재 설정이 적절합니다!")
        
        report.append("")
        report.append("=" * 70)
        
        return "\n".join(report)
    
    def export_to_json(self, output_path: str = "rules_analysis.json"):
        """JSON으로 내보내기"""
        data = {
            "generated_at": datetime.now().isoformat(),
            "total_rules": len(self.rules),
            "rules": self.rules,
            "conflicts": self.conflicts,
            "usage_stats": self.usage_stats,
            "priority_map": self.priority_map
        }
        
        output_file = Path(output_path)
        output_file.write_text(json.dumps(data, indent=2, ensure_ascii=False, default=str), encoding='utf-8')
        return str(output_file)

def main():
    """메인 실행"""
    print("🔍 Cursor Rules 진단 시작...\n")
    
    manager = RulesManager()
    
    print(f"📁 Rules 디렉토리: {RULES_DIR}")
    print(f"📊 발견된 Rules: {len(manager.rules)}개\n")
    
    # 충돌 감지
    print("⚙️  충돌 감지 중...")
    manager.detect_conflicts()
    
    # 사용 분석
    print("📊 사용 분석 중...")
    manager.analyze_usage()
    
    # Priority 맵
    print("🎯 우선순위 분석 중...\n")
    manager.generate_priority_map()
    
    # 리포트 생성
    report = manager.generate_report()
    print(report)
    
    # 파일로 저장
    today = datetime.now().strftime("%Y-%m-%d")
    report_path = WORKSPACE / "daily" / today / "rules_diagnostic_report.txt"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(report, encoding='utf-8')
    
    # JSON 저장
    json_path = manager.export_to_json(str(report_path.parent / "rules_analysis.json"))
    
    print(f"\n💾 리포트 저장: {report_path}")
    print(f"💾 JSON 저장: {json_path}")
    print("\n✅ 진단 완료!")

if __name__ == "__main__":
    main()

