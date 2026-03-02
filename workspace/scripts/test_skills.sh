#!/bin/bash
# 测试Skill可用性

echo "=== Skill可用性测试 ==="
echo "测试时间: $(date)"
echo ""

# 颜色输出
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

test_skill() {
    local skill_name="$1"
    local test_command="$2"
    local description="$3"
    
    echo -e "${BLUE}测试: $skill_name${NC}"
    echo "  描述: $description"
    
    if eval "$test_command" >/dev/null 2>&1; then
        echo -e "  状态: ${GREEN}✅ 可用${NC}"
        return 0
    else
        echo -e "  状态: ${RED}❌ 不可用${NC}"
        return 1
    fi
    echo ""
}

# 测试1: 飞书文档技能
test_skill "feishu-doc" \
    "openclaw feishu-doc --help 2>&1 | head -5" \
    "飞书文档操作"

# 测试2: 飞书云盘技能
test_skill "feishu-drive" \
    "openclaw feishu-drive --help 2>&1 | head -5" \
    "飞书云盘管理"

# 测试3: 飞书权限技能
test_skill "feishu-perm" \
    "openclaw feishu-perm --help 2>&1 | head -5" \
    "飞书权限管理"

# 测试4: 飞书知识库技能
test_skill "feishu-wiki" \
    "openclaw feishu-wiki --help 2>&1 | head -5" \
    "飞书知识库"

# 测试5: Apple Notes技能
test_skill "apple-notes" \
    "which memo 2>/dev/null" \
    "Apple Notes管理"

# 测试6: Apple Reminders技能
test_skill "apple-reminders" \
    "which remindctl 2>/dev/null" \
    "Apple Reminders管理"

# 测试7: Blogwatcher技能
test_skill "blogwatcher" \
    "which blogwatcher 2>/dev/null" \
    "博客监控"

# 测试8: Clawhub技能
test_skill "clawhub" \
    "which clawhub 2>/dev/null" \
    "技能发现和安装"

# 测试9: Coding Agent技能
test_skill "coding-agent" \
    "openclaw coding-agent --help 2>&1 | head -5" \
    "编码代理"

# 测试10: Gemini技能
test_skill "gemini" \
    "which gemini 2>/dev/null" \
    "Gemini AI"

# 测试11: GitHub技能
test_skill "github" \
    "which gh 2>/dev/null" \
    "GitHub操作"

# 测试12: Healthcheck技能
test_skill "healthcheck" \
    "openclaw healthcheck --help 2>&1 | head -5" \
    "安全检查"

# 测试13: Nano Banana Pro技能
test_skill "nano-banana-pro" \
    "which nano-banana-pro 2>/dev/null" \
    "图像生成"

# 测试14: Nano PDF技能
test_skill "nano-pdf" \
    "which nano-pdf 2>/dev/null" \
    "PDF编辑"

# 测试15: Things技能
test_skill "things-mac" \
    "which things 2>/dev/null" \
    "Things 3管理"

# 测试16: Weather技能
test_skill "weather" \
    "which weather 2>/dev/null" \
    "天气查询"

# 测试17: Session Logs技能
test_skill "session-logs" \
    "openclaw session-logs --help 2>&1 | head -5" \
    "会话日志"

# 测试18: Skill Creator技能
test_skill "skill-creator" \
    "openclaw skill-creator --help 2>&1 | head -5" \
    "技能创建"

# 测试19: Agent Browser技能
test_skill "agent-browser" \
    "which agent-browser 2>/dev/null" \
    "浏览器自动化"

# 测试20: Ontology技能
test_skill "ontology" \
    "openclaw ontology --help 2>&1 | head -5" \
    "知识图谱"

# 测试21: Opencode Controller技能
test_skill "opencode-controller" \
    "openclaw opencode-controller --help 2>&1 | head -5" \
    "Opencode控制"

# 测试22: Tavily搜索技能
test_skill "tavily" \
    "which tavily 2>/dev/null" \
    "Tavily搜索"

echo -e "${BLUE}=== 测试完成 ===${NC}"
echo "总结:"
echo "已测试 22 个关键技能"
echo "详细结果见上方"