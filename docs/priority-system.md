# Priority System Guide

## 🎯 Overview

The Priority System organizes rules by importance (0-10), where lower numbers mean higher priority.

## 📊 Priority Levels

### Priority 0: Critical (Never Ignore)

**Characteristics**:
- `alwaysApply: true`
- `type: "always"`
- Must be followed without exception
- System will block violations

**Examples**:
- `f-drive-absolute-independence.mdc` - Environment rules
- `rules-priority-enforcement.mdc` - Rules enforcement

**Usage**:
```yaml
---
priority: 0
alwaysApply: true
type: "always"
tags: ["critical"]
---
```

### Priority 1-3: Important

**Characteristics**:
- `alwaysApply: true` or `false`
- `type: "always"` or `"intelligent"`
- Should be followed in most cases
- System will recommend

**Examples**:
- `athena-summon-protocol.mdc` (Priority 1)
- `daily-workflow.mdc` (Priority 1)
- `security-rules.mdc` (Priority 1)

### Priority 4-9: Optional

**Characteristics**:
- `alwaysApply: false`
- `type: "intelligent"` or `"file-specific"`
- Applied when relevant
- System will suggest

### Priority 10: Manual Only

**Characteristics**:
- `alwaysApply: false`
- `type: "manual"`
- Only applied when explicitly mentioned
- Reference guides

**Examples**:
- `emergency-recovery.mdc` (Priority 10)
- `setup-recovery.mdc` (Priority 10)

## 🔍 How Priority Works

### Automatic Application

1. **Priority 0**: Always applied automatically
2. **Priority 1-3**: Applied based on context
3. **Priority 4-9**: Suggested when relevant
4. **Priority 10**: Manual reference only

### Conflict Resolution

When multiple rules conflict:
- **Lower priority wins** (Priority 0 > Priority 1)
- **More specific rules win** (file-specific > always)
- **Recent rules win** (if same priority)

## 📝 Best Practices

### Choosing Priority

**Priority 0**:
- Safety-critical rules
- Environment rules
- System-critical rules

**Priority 1-3**:
- Important workflows
- Best practices
- Common patterns

**Priority 4-9**:
- Optional optimizations
- Nice-to-have rules
- Experimental rules

**Priority 10**:
- Reference guides
- Manual procedures
- Emergency procedures

### Metadata Guidelines

```yaml
---
priority: 1                    # Required
description: "Clear description"  # Required
alwaysApply: true             # Required
type: "always"                # Recommended
tags: ["tag1", "tag2"]        # Recommended
globs: ["**/*.py"]            # Optional
---
```

## 🎯 Examples

### Priority 0 Example

```yaml
---
priority: 0
description: "F drive must maintain absolute independence"
alwaysApply: true
type: "always"
tags: ["critical", "environment"]
globs: ["**/*"]
---
```

### Priority 1 Example

```yaml
---
priority: 1
description: "Daily workflow automation"
alwaysApply: true
type: "always"
tags: ["workflow", "automation"]
---
```

### Priority 10 Example

```yaml
---
priority: 10
description: "Emergency recovery guide"
alwaysApply: false
type: "manual"
tags: ["emergency", "recovery"]
---
```

## 💡 Tips

- Start with Priority 0 rules (most important)
- Use Priority 1-3 for common workflows
- Reserve Priority 10 for reference guides
- Review priorities regularly based on usage

---

**Need help?** [Contact Support](mailto:support@athena-rules.com)

