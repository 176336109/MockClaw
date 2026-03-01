#!/bin/bash
# 博查AI搜索启动脚本

# 加载.env文件
if [ -f .env ]; then
    echo "📁 加载.env配置文件..."
    export $(grep -v '^#' .env | xargs)
fi

# 检查API Key
if [ -z "$BOCHA_API_KEY" ]; then
    echo "❌ 错误：未设置BOCHA_API_KEY环境变量"
    echo "请设置环境变量或创建.env文件"
    exit 1
fi

echo "✅ API Key已设置: ${BOCHA_API_KEY:0:10}..."

# 运行Python脚本
python3 bocha_web_search.py "$@"
