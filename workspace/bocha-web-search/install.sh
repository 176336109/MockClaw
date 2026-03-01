#!/bin/bash
# 博查AI Web Search技能安装脚本

set -e

echo "🔧 安装博查AI Web Search技能"
echo "=============================="

# 检查Python版本
echo "检查Python版本..."
python_version=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
if [[ $? -ne 0 ]]; then
    echo "❌ 未找到Python3，请先安装Python3.7或更高版本"
    exit 1
fi

major_version=$(echo $python_version | cut -d. -f1)
minor_version=$(echo $python_version | cut -d. -f2)

if [[ $major_version -lt 3 ]] || [[ $major_version -eq 3 && $minor_version -lt 7 ]]; then
    echo "❌ 需要Python 3.7或更高版本，当前版本: $python_version"
    exit 1
fi

echo "✅ Python版本: $python_version"

# 安装依赖
echo "安装Python依赖..."
pip3 install -r requirements.txt
if [[ $? -ne 0 ]]; then
    echo "❌ 依赖安装失败"
    exit 1
fi
echo "✅ 依赖安装完成"

# 创建配置文件
if [[ ! -f .env ]]; then
    echo "创建配置文件..."
    cp .env.example .env
    echo "✅ 配置文件已创建 (.env)"
    echo "⚠️  请编辑 .env 文件，添加您的API密钥"
else
    echo "✅ 配置文件已存在 (.env)"
fi

# 测试安装
echo "测试安装..."
python3 -c "from bocha_web_search import BochaWebSearch; print('✅ 导入成功')"
if [[ $? -ne 0 ]]; then
    echo "❌ 导入测试失败"
    exit 1
fi

# 运行简单测试
echo "运行简单测试..."
python3 examples/basic_usage.py > /dev/null 2>&1
if [[ $? -ne 0 ]]; then
    echo "⚠️  简单测试失败，但安装可能仍然可用"
else
    echo "✅ 简单测试通过"
fi

# 提示安装到OpenClaw
echo ""
echo "📦 安装到OpenClaw（可选）"
echo "--------------------------"
echo "要将此技能安装为OpenClaw技能，请执行："
echo ""
echo "1. 复制技能目录到OpenClaw skills目录："
echo "   cp -r $(pwd) ~/.openclaw/skills/bocha-web-search"
echo ""
echo "2. 在OpenClaw中使用："
echo "   openclaw bocha-web-search \"搜索关键词\""
echo ""
echo "3. 或添加别名（在 ~/.openclaw/config.yaml 中）："
echo "   aliases:"
echo "     search: \"bocha-web-search\""
echo "     bsearch: \"bocha-web-search --format json\""

echo ""
echo "🎉 安装完成！"
echo ""
echo "快速开始："
echo "  python3 bocha_web_search.py \"OpenAI最新进展\""
echo "  python3 examples/basic_usage.py"
echo ""
echo "获取API密钥：https://open.bocha.cn > API KEY管理"