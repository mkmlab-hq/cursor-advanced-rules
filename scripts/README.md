# Scripts

This directory contains utility scripts for managing Cursor Rules.

## Available Scripts

### Python Scripts

#### `check_rules_before_solution.py`

Basic Rules search functionality.

**Usage**:
```bash
python scripts/check_rules_before_solution.py "SSH 키 문제"
```

**Features**:
- Search rules by keywords
- Priority-based sorting
- Metadata parsing

**Note**: Advanced features (integrated search, auto-promotion) are available in Pro Tier.

### PowerShell Scripts

#### `validate-rules-consistency.ps1`

Validates consistency of Rules metadata.

**Usage**:
```powershell
.\scripts\validate-rules-consistency.ps1
```

**Checks**:
- Priority 0 → type: "always", alwaysApply: true
- Priority 10 → type: "manual", alwaysApply: false
- Type "always" → alwaysApply: true
- Type "manual" → alwaysApply: false

#### `search-rules-by-tag.ps1`

Search Rules files by tags.

**Usage**:
```powershell
.\scripts\search-rules-by-tag.ps1 "critical"
.\scripts\search-rules-by-tag.ps1 "critical", "security"
```

#### `rules-stats.ps1`

Generate statistics about Rules files.

**Usage**:
```powershell
.\scripts\rules-stats.ps1
```

**Output**:
- Total file count
- Priority distribution
- Type distribution
- Metadata completeness

## Requirements

- Python 3.8+ (for Python scripts)
- PowerShell 5.1+ (for PowerShell scripts)

## Pro Tier Features

Advanced scripts available in Pro Tier:

- `enhanced_rules_enforcement.py` - Integrated search engine
- `usage_pattern_tracker.py` - Usage pattern analysis
- `performance_optimizer.py` - Performance optimization
- `auto_priority_adjuster.py` - Auto priority adjustment

[Get Pro Tier →](../PRO_TIER.md)

