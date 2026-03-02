#!/bin/bash
# Skill状态报告

echo "=== OpenClaw Skill状态报告 ==="
echo "生成时间: $(date)"
echo ""

# 获取技能列表
echo "📋 技能列表 (来自 openclaw skills):"
echo "----------------------------------------"

# 解析技能状态
AVAILABLE_SKILLS=()
UNAVAILABLE_SKILLS=()
MISSING_SKILLS=()

# 检查每个技能
check_skill_availability() {
    local skill_name="$1"
    local skill_type="$2"
    
    case "$skill_type" in
        "feishu-doc"|"feishu-drive"|"feishu-perm"|"feishu-wiki")
            if openclaw "$skill_name" --help 2>&1 | grep -q "Registered"; then
                AVAILABLE_SKILLS+=("$skill_name")
                echo "✅ $skill_name: 可用 (飞书工具)"
            else
                UNAVAILABLE_SKILLS+=("$skill_name")
                echo "⚠️  $skill_name: 需要配置"
            fi
            ;;
        "apple-notes")
            if which memo >/dev/null 2>&1; then
                AVAILABLE_SKILLS+=("$skill_name")
                echo "✅ $skill_name: 可用"
            else
                UNAVAILABLE_SKILLS+=("$skill_name")
                echo "❌ $skill_name: 需要安装memo CLI"
            fi
            ;;
        "apple-reminders")
            if which remindctl >/dev/null 2>&1; then
                AVAILABLE_SKILLS+=("$skill_name")
                echo "✅ $skill_name: 可用"
            else
                UNAVAILABLE_SKILLS+=("$skill_name")
                echo "❌ $skill_name: 需要安装remindctl"
            fi
            ;;
        "blogwatcher")
            if which blogwatcher >/dev/null 2>&1; then
                AVAILABLE_SKILLS+=("$skill_name")
                echo "✅ $skill_name: 可用"
            else
                UNAVAILABLE_SKILLS+=("$skill_name")
                echo "❌ $skill_name: 需要安装blogwatcher"
            fi
            ;;
        "clawhub")
            if which clawhub >/dev/null 2>&1; then
                AVAILABLE_SKILLS+=("$skill_name")
                echo "✅ $skill_name: 可用"
            else
                UNAVAILABLE_SKILLS+=("$skill_name")
                echo "❌ $skill_name: 需要安装clawhub"
            fi
            ;;
        "coding-agent")
            if openclaw coding-agent --help 2>&1 | head -1 | grep -q "coding-agent"; then
                AVAILABLE_SKILLS+=("$skill_name")
                echo "✅ $skill_name: 可用"
            else
                UNAVAILABLE_SKILLS+=("$skill_name")
                echo "⚠️  $skill_name: 需要验证"
            fi
            ;;
        "gemini")
            if which gemini >/dev/null 2>&1; then
                AVAILABLE_SKILLS+=("$skill_name")
                echo "✅ $skill_name: 可用"
            else
                UNAVAILABLE_SKILLS+=("$skill_name")
                echo "❌ $skill_name: 需要安装gemini CLI"
            fi
            ;;
        "github")
            if which gh >/dev/null 2>&1; then
                AVAILABLE_SKILLS+=("$skill_name")
                echo "✅ $skill_name: 可用"
            else
                UNAVAILABLE_SKILLS+=("$skill_name")
                echo "❌ $skill_name: 需要安装GitHub CLI"
            fi
            ;;
        "healthcheck")
            if openclaw healthcheck --help 2>&1 | head -1 | grep -q "healthcheck"; then
                AVAILABLE_SKILLS+=("$skill_name")
                echo "✅ $skill_name: 可用"
            else
                UNAVAILABLE_SKILLS+=("$skill_name")
                echo "⚠️  $skill_name: 需要验证"
            fi
            ;;
        "nano-banana-pro")
            if which nano-banana-pro >/dev/null 2>&1; then
                AVAILABLE_SKILLS+=("$skill_name")
                echo "✅ $skill_name: 可用"
            else
                UNAVAILABLE_SKILLS+=("$skill_name")
                echo "❌ $skill_name: 需要安装nano-banana-pro"
            fi
            ;;
        "nano-pdf")
            if which nano-pdf >/dev/null 2>&1; then
                AVAILABLE_SKILLS+=("$skill_name")
                echo "✅ $skill_name: 可用"
            else
                UNAVAILABLE_SKILLS+=("$skill_name")
                echo "❌ $skill_name: 需要安装nano-pdf"
            fi
            ;;
        "things-mac")
            if which things >/dev/null 2>&1; then
                AVAILABLE_SKILLS+=("$skill_name")
                echo "✅ $skill_name: 可用"
            else
                UNAVAILABLE_SKILLS+=("$skill_name")
                echo "❌ $skill_name: 需要安装things CLI"
            fi
            ;;
        "weather")
            if which weather >/dev/null 2>&1; then
                AVAILABLE_SKILLS+=("$skill_name")
                echo "✅ $skill_name: 可用"
            else
                UNAVAILABLE_SKILLS+=("$skill_name")
                echo "❌ $skill_name: 需要安装weather CLI"
            fi
            ;;
        "session-logs")
            if openclaw session-logs --help 2>&1 | head -1 | grep -q "session-logs"; then
                AVAILABLE_SKILLS+=("$skill_name")
                echo "✅ $skill_name: 可用"
            else
                UNAVAILABLE_SKILLS+=("$skill_name")
                echo "⚠️  $skill_name: 需要验证"
            fi
            ;;
        "skill-creator")
            if openclaw skill-creator --help 2>&1 | head -1 | grep -q "skill-creator"; then
                AVAILABLE_SKILLS+=("$skill_name")
                echo "✅ $skill_name: 可用"
            else
                UNAVAILABLE_SKILLS+=("$skill_name")
                echo "⚠️  $skill_name: 需要验证"
            fi
            ;;
        *)
            UNAVAILABLE_SKILLS+=("$skill_name")
            echo "❓ $skill_name: 未知状态"
            ;;
    esac
}

# 检查关键技能
echo "🔍 检查关键技能可用性:"
echo ""

check_skill_availability "feishu-doc" "feishu-doc"
check_skill_availability "feishu-drive" "feishu-drive"
check_skill_availability "feishu-perm" "feishu-perm"
check_skill_availability "feishu-wiki" "feishu-wiki"
check_skill_availability "apple-notes" "apple-notes"
check_skill_availability "apple-reminders" "apple-reminders"
check_skill_availability "blogwatcher" "blogwatcher"
check_skill_availability "clawhub" "clawhub"
check_skill_availability "coding-agent" "coding-agent"
check_skill_availability "gemini" "gemini"
check_skill_availability "github" "github"
check_skill_availability "healthcheck" "healthcheck"
check_skill_availability "nano-banana-pro" "nano-banana-pro"
check_skill_availability "nano-pdf" "nano-pdf"
check_skill_availability "things-mac" "things-mac"
check_skill_availability "weather" "weather"
check_skill_availability "session-logs" "session-logs"
check_skill_availability "skill-creator" "skill-creator"

echo ""
echo "📊 已安装的技能目录 (~/.openclaw/skills/):"
echo "----------------------------------------"
for skill_dir in ~/.openclaw/skills/*; do
    if [ -d "$skill_dir" ]; then
        skill_name=$(basename "$skill_dir")
        if [ -f "$skill_dir/SKILL.md" ]; then
            echo "✅ $skill_name: 已封装"
        else
            echo "⚠️  $skill_name: 未封装"
        fi
    fi
done

echo ""
echo "📈 统计:"
echo "----------------------------------------"
echo "可用技能: ${#AVAILABLE_SKILLS[@]}个"
echo "不可用技能: ${#UNAVAILABLE_SKILLS[@]}个"
echo "缺失技能: ${#MISSING_SKILLS[@]}个"
echo ""
echo "💡 建议:"
echo "1. 安装缺失的CLI工具 (gh, gemini, weather等)"
echo "2. 验证飞书工具配置"
echo "3. 封装所有技能目录"
echo "4. 更新多维表格中的技能状态"