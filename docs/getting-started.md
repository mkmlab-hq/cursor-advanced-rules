# Getting Started

Welcome to Cursor Advanced Rules System! 🚀

## 📋 Prerequisites

- Cursor AI installed and running
- Basic knowledge of Cursor Rules
- Python 3.8+ (for scripts)

## 🚀 Installation

### Step 1: Clone Repository

```bash
git clone https://github.com/yourusername/cursor-advanced-rules.git
cd cursor-advanced-rules
```

### Step 2: Copy Rules to Your Project

```bash
# Copy free rules to your project
cp -r rules/* /your/project/.cursor/rules/
```

### Step 3: Verify Installation

```bash
# Check if rules are installed
ls /your/project/.cursor/rules/

# You should see 10 rules:
# - f-drive-absolute-independence.mdc
# - rules-priority-enforcement.mdc
# - athena-summon-protocol.mdc
# - ... (7 more)
```

## 🎯 Quick Start

### 1. Basic Usage

Just use Cursor AI as usual! The rules will automatically apply.

**Example**:
```
You: "SSH 키 문제 해결해줘"
Cursor: [Automatically checks Priority 0 rules]
        [Applies relevant rules]
        [Provides solution]
```

### 2. Check Rules

```powershell
# Validate rules consistency
.\scripts\validate-rules-consistency.ps1

# Search rules by tag
.\scripts\search-rules-by-tag.ps1 "critical"

# Get rules statistics
.\scripts\rules-stats.ps1
```

### 3. Understand Priority System

- **Priority 0**: Never ignore (Critical)
- **Priority 1-3**: Important
- **Priority 10**: Manual only

See [Priority System Guide](priority-system.md) for details.

## 📚 Next Steps

1. **Read Documentation**:
   - [Priority System](priority-system.md)
   - [Memory Integration](memory-integration-concept.md)

2. **Try Examples**:
   - [Basic Usage Examples](examples/basic-usage.md)
   - [Custom Rules](examples/custom-rules.md)

3. **Upgrade to Pro**:
   - Get all 54 rules
   - Advanced features
   - [Learn More](../PRO_TIER.md)

## ❓ Troubleshooting

### Rules Not Applying?

1. Check if rules are in `.cursor/rules/` directory
2. Verify Cursor is reading the directory
3. Restart Cursor if needed

### Scripts Not Working?

1. Ensure Python 3.8+ is installed
2. Check PowerShell execution policy:
   ```powershell
   Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
   ```

## 💡 Tips

- Start with Priority 0 rules (they're most important)
- Use tags to find related rules
- Check rules statistics regularly
- Upgrade to Pro for full power

## 🆘 Need Help?

- 📧 Email: support@athena-rules.com
- 💬 Discord: [Join community](https://discord.gg/athena-rules)
- 🐛 Issues: [GitHub Issues](https://github.com/yourusername/cursor-advanced-rules/issues)

---

**Ready to boost your productivity?** [Get Pro Tier →](../PRO_TIER.md)

