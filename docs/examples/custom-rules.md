# Creating Custom Rules

## 🎯 Overview

Learn how to create your own rules for Cursor AI.

## 📝 Basic Rule Structure

### Minimum Required

```yaml
---
description: "Your rule description"
alwaysApply: true
priority: 1
---
```

### Full Example

```yaml
---
description: "Always use TypeScript for new projects"
alwaysApply: true
priority: 1
type: "always"
tags: ["typescript", "project", "standards"]
globs: ["**/*.ts", "**/*.tsx"]
---
```

## 🎯 Rule Types

### 1. Always Rules

Applied automatically in all contexts.

```yaml
---
type: "always"
alwaysApply: true
priority: 1
---
```

### 2. Intelligent Rules

Applied when AI determines relevance.

```yaml
---
type: "intelligent"
alwaysApply: false
priority: 2
description: "Detailed description for AI to understand when to apply"
---
```

### 3. File-Specific Rules

Applied only to matching files.

```yaml
---
type: "file-specific"
alwaysApply: false
priority: 2
globs: ["**/*.py", "**/backend/**"]
---
```

### 4. Manual Rules

Only applied when explicitly mentioned.

```yaml
---
type: "manual"
alwaysApply: false
priority: 10
---
```

## 📋 Step-by-Step Guide

### Step 1: Define Purpose

What problem does this rule solve?
- Environment setup?
- Code standards?
- Workflow automation?

### Step 2: Choose Priority

- **Priority 0**: Critical, never ignore
- **Priority 1-3**: Important
- **Priority 4-9**: Optional
- **Priority 10**: Manual reference

### Step 3: Write Rule Content

```markdown
# Your Rule Title

## Purpose
What this rule does

## Rules
- Rule 1
- Rule 2

## Examples
Example usage
```

### Step 4: Add Metadata

```yaml
---
description: "Clear, concise description"
alwaysApply: true/false
priority: 1
type: "always" | "intelligent" | "file-specific" | "manual"
tags: ["tag1", "tag2"]
globs: ["**/*.py"]  # Optional
---
```

### Step 5: Test

1. Save rule to `.cursor/rules/`
2. Test with Cursor AI
3. Verify it applies correctly
4. Adjust if needed

## 💡 Best Practices

### 1. Clear Descriptions

✅ Good:
```yaml
description: "Always use SQLite for database operations"
```

❌ Bad:
```yaml
description: "Database stuff"
```

### 2. Appropriate Tags

✅ Good:
```yaml
tags: ["database", "sqlite", "preference"]
```

❌ Bad:
```yaml
tags: ["stuff", "things"]
```

### 3. Specific Globs

✅ Good:
```yaml
globs: ["**/*.py", "**/backend/**"]
```

❌ Bad:
```yaml
globs: ["**/*"]
```

## 📚 Example Rules

### Example 1: Project Standard

```yaml
---
description: "Use ESLint for all JavaScript files"
alwaysApply: true
priority: 2
type: "file-specific"
tags: ["javascript", "linting", "standards"]
globs: ["**/*.js", "**/*.jsx"]
---
```

### Example 2: Workflow Rule

```yaml
---
description: "Always run tests before committing"
alwaysApply: true
priority: 1
type: "always"
tags: ["testing", "workflow", "git"]
---
```

### Example 3: Manual Guide

```yaml
---
description: "Deployment checklist"
alwaysApply: false
priority: 10
type: "manual"
tags: ["deployment", "checklist"]
---
```

## 🚀 Sharing Rules

### Submit to Repository

1. Create your rule
2. Test thoroughly
3. Open Pull Request
4. Get community feedback

### Community Rules

Check out community-contributed rules:
- [Community Rules](https://github.com/yourusername/cursor-advanced-rules/discussions)

---

**Need help?** [Contact Support](mailto:support@athena-rules.com)

