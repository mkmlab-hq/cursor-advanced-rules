# Basic Usage Examples

## 📋 Example 1: Environment Rules

### Scenario
You want to ensure F drive independence.

### Rule Applied
`f-drive-absolute-independence.mdc` (Priority 0)

### Result
```
You: "파일을 C 드라이브에 저장해줘"
Cursor: ⚠️ Priority 0 Rule Violation
        F drive must maintain absolute independence
        C drive access is prohibited
        → Solution: Use F drive instead
```

## 📋 Example 2: Rules Enforcement

### Scenario
You ask for help with SSH keys.

### Rule Applied
`rules-priority-enforcement.mdc` (Priority 0)

### Result
```
You: "SSH 키 문제 해결해줘"
Cursor: 1. Checking Rules...
        2. Found Priority 0 rule: ssh-key-hpanel-priority.mdc
        3. Applying rule...
        4. Solution: Use hPanel method (required)
```

## 📋 Example 3: Daily Workflow

### Scenario
You start your daily work.

### Rule Applied
`daily-workflow.mdc` (Priority 1)

### Result
```
You: "오늘 작업 시작할게"
Cursor: [Automatically applies daily workflow]
        - Checks system status
        - Validates environment
        - Prepares workspace
        → Ready to work!
```

## 📋 Example 4: Security Rules

### Scenario
You're working with sensitive data.

### Rule Applied
`security-rules.mdc` (Priority 1)

### Result
```
You: "API 키를 코드에 넣을게"
Cursor: ⚠️ Security Rule Alert
        API keys should not be hardcoded
        → Solution: Use environment variables
```

## 💡 Tips

1. **Priority 0 rules** are automatically enforced
2. **Priority 1-3 rules** are applied based on context
3. **Check rules** before starting work
4. **Use tags** to find related rules

---

**Want more examples?** [Custom Rules →](custom-rules.md)

