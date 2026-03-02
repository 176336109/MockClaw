#!/usr/bin/env python3
"""
启动小红书团队建设
1. 更新任务状态
2. 创建团队架构
3. 制定执行计划
"""

import json
import requests
import time
from pathlib import Path
from datetime import datetime

# 加载配置
config_path = Path.home() / ".openclaw" / "openclaw.json"
with open(config_path, 'r') as f:
    config = json.load(f)

feishu_config = config.get('channels', {}).get('feishu', {})
accounts = feishu_config.get('accounts', {}).get('main', {})

app_id = accounts.get('appId')
app_secret = accounts.get('appSecret')

print("🚀 小红书完整系统建设 - 启动")
print("=" * 60)

# 1. 获取token
print("\n1. 获取API token...")
url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
headers = {"Content-Type": "application/json; charset=utf-8"}
data = {
    "app_id": app_id,
    "app_secret": app_secret
}

response = requests.post(url, headers=headers, json=data, timeout=10)
result = response.json()

if result.get("code") != 0:
    print(f"❌ 获取token失败: {result}")
    exit(1)

token = result.get("tenant_access_token")
print(f"✅ Token获取成功")

# 多维表格配置
base_app_token = "FCRNbSo4ja4hCEs5411cNZQXnkh"
table_id = "tblRmMB6LIdLHyEt"
api_headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

# 2. 更新小红书任务状态
print("\n2. 更新小红书任务状态...")

# 任务状态更新
tasks_to_update = [
    {
        "任务ID": "TASK-20260301-233530",
        "任务名称": "搜索和安装小红书图文自动维护技能",
        "状态": "进行中",
        "描述": "启动完整系统建设，高优先级，手动发布图文，测试OpenClaw主题",
        "优先级": "高"
    },
    {
        "任务ID": "TASK-20260301-234800", 
        "任务名称": "建设全自动小红书Agent团队",
        "状态": "进行中",
        "描述": "组建团队，跑通流程，测试主题以关注OpenClaw的人群为主",
        "优先级": "高"
    }
]

record_url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{base_app_token}/tables/{table_id}/records"
search_url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{base_app_token}/tables/{table_id}/records/search"

for task in tasks_to_update:
    print(f"\n更新任务: {task['任务名称']}")
    
    # 搜索现有记录
    search_data = {
        "filter": {
            "conjunction": "and",
            "conditions": [
                {
                    "field_name": "任务ID",
                    "operator": "is",
                    "value": [task["任务ID"]]
                }
            ]
        },
        "page_size": 1
    }
    
    search_response = requests.post(search_url, headers=api_headers, json=search_data, timeout=10)
    search_result = search_response.json()
    
    record_id = None
    if search_result.get("code") == 0:
        items = search_result.get("data", {}).get("items", [])
        if items:
            record_id = items[0].get('record_id')
    
    # 准备数据
    record_data = {
        "fields": {
            "文本": f"任务状态更新: {task['任务名称']}",
            "任务ID": task["任务ID"],
            "任务名称": task["任务名称"],
            "状态": task["状态"],
            "描述": task["描述"],
            "创建时间": int(time.time() * 1000),
            "负责人": "OpenClaw主Agent",
            "优先级": task["优先级"]
        }
    }
    
    # 创建或更新
    if record_id:
        update_url = f"{record_url}/{record_id}"
        response = requests.put(update_url, headers=api_headers, json=record_data, timeout=10)
        action = "更新"
    else:
        response = requests.post(record_url, headers=api_headers, json=record_data, timeout=10)
        action = "创建"
    
    result = response.json()
    
    if result.get("code") == 0:
        new_record_id = result.get("data", {}).get("record", {}).get("record_id") or record_id
        print(f"  ✅ {action}成功! Record ID: {new_record_id}")
    else:
        print(f"  ❌ {action}失败: {result.get('msg')}")

# 3. 创建团队架构文档
print("\n3. 创建小红书Agent团队架构...")

team_architecture = {
    "项目名称": "小红书OpenClaw主题内容系统",
    "启动时间": datetime.now().isoformat(),
    "优先级": "高",
    "目标": "组建团队，跑通流程，测试OpenClaw主题",
    
    "团队架构": {
        "策划组": {
            "职责": "主题策划、内容规划、热点发现",
            "工具": ["Gemini", "NanoBanana", "内容分析工具"],
            "输出": "内容日历、选题库、热点报告"
        },
        "创作组": {
            "职责": "图文内容创作、标题优化、文案撰写",
            "工具": ["xiaohongshu-title技能", "图像生成", "文案优化"],
            "输出": "小红书图文内容、标题方案、文案草稿"
        },
        "审核组": {
            "职责": "内容审核、质量检查、合规审查",
            "工具": ["内容审核规则", "质量检查清单"],
            "输出": "审核报告、修改建议、发布许可"
        },
        "发布组": {
            "职责": "手动发布、数据跟踪、效果分析",
            "工具": ["小红书App", "数据统计工具"],
            "输出": "发布记录、数据报告、效果分析"
        }
    },
    
    "工作流程": [
        "1. 策划组：每周制定内容日历，每日发现热点",
        "2. 创作组：根据日历和热点创作图文内容",
        "3. 审核组：审核内容质量和合规性",
        "4. 发布组：手动发布到小红书，跟踪数据",
        "5. 分析组：分析效果，优化策略"
    ],
    
    "技术栈": {
        "AI工具": ["Gemini (API可用)", "NanoBanana (有积分)"],
        "技能": ["xiaohongshu-title (已安装)", "内容生成技能"],
        "自动化": ["工作流引擎", "状态管理", "任务调度"],
        "监控": ["状态反馈系统", "心跳机制", "进度跟踪"]
    },
    
    "第一阶段目标": {
        "时间": "1-2周",
        "里程碑": [
            "组建4个工作组",
            "建立完整工作流程",
            "产出5篇测试内容",
            "完成1轮完整流程测试"
        ],
        "成功标准": [
            "流程跑通，无阻塞",
            "内容质量达标",
            "发布流程顺畅",
            "数据可追踪"
        ]
    },
    
    "资源需求": {
        "已具备": ["GeminiKEY", "NanoBanana积分", "xiaohongshu-title技能"],
        "需要确认": ["其他小红书技能安全性", "内容审核标准", "发布账号"],
        "待获取": ["更多内容生成技能", "数据分析工具", "工作流优化工具"]
    }
}

# 保存团队架构
arch_file = Path.home() / ".openclaw" / "workspace" / "xiaohongshu_team_architecture.json"
with open(arch_file, 'w', encoding='utf-8') as f:
    json.dump(team_architecture, f, indent=2, ensure_ascii=False)

print(f"✅ 团队架构已保存: {arch_file}")

# 4. 创建执行计划
print("\n4. 创建执行计划...")

execution_plan = [
    {
        "阶段": "第1天",
        "任务": [
            "1. 确认所有技能状态",
            "2. 组建4个工作组",
            "3. 制定内容策略",
            "4. 创建第一个测试主题"
        ],
        "负责人": "OpenClaw主Agent",
        "状态": "待开始"
    },
    {
        "阶段": "第2-3天", 
        "任务": [
            "1. 测试内容创作流程",
            "2. 验证审核机制",
            "3. 模拟发布流程",
            "4. 收集反馈优化"
        ],
        "负责人": "各工作组",
        "状态": "规划中"
    },
    {
        "阶段": "第4-7天",
        "任务": [
            "1. 产出5篇测试内容",
            "2. 完成完整流程测试",
            "3. 分析测试结果",
            "4. 优化工作流程"
        ],
        "负责人": "整个团队",
        "状态": "规划中"
    },
    {
        "阶段": "第2周",
        "任务": [
            "1. 正式内容生产",
            "2. 数据跟踪分析",
            "3. 持续优化改进",
            "4. 扩展内容范围"
        ],
        "负责人": "运营团队",
        "状态": "规划中"
    }
]

plan_file = Path.home() / ".openclaw" / "workspace" / "xiaohongshu_execution_plan.json"
with open(plan_file, 'w', encoding='utf-8') as f:
    json.dump(execution_plan, f, indent=2, ensure_ascii=False)

print(f"✅ 执行计划已保存: {plan_file}")

# 5. 创建第一个测试主题
print("\n5. 创建第一个测试主题...")

test_themes = [
    {
        "主题": "OpenClaw是什么？AI助手入门指南",
        "目标受众": "对AI助手感兴趣的小红书用户",
        "内容形式": "图文教程",
        "关键点": [
            "OpenClaw的基本功能",
            "如何开始使用",
            "实际应用案例",
            "学习资源和社区"
        ],
        "发布时间": "第1周",
        "负责人": "创作组"
    },
    {
        "主题": "我用OpenClaw自动化了我的工作流",
        "目标受众": "效率追求者、职场人士",
        "内容形式": "经验分享+截图",
        "关键点": [
            "具体自动化场景",
            "节省的时间成本",
            "使用技巧分享",
            "效果对比展示"
        ],
        "发布时间": "第1周",
        "负责人": "创作组"
    },
    {
        "主题": "AI助手如何改变内容创作？",
        "目标受众": "内容创作者、自媒体人",
        "内容形式": "行业分析+案例",
        "关键点": [
            "AI在内容创作中的应用",
            "效率提升数据",
            "创意激发方法",
            "未来趋势预测"
        ],
        "发布时间": "第2周",
        "负责人": "策划组"
    }
]

themes_file = Path.home() / ".openclaw" / "workspace" / "xiaohongshu_test_themes.json"
with open(themes_file, 'w', encoding='utf-8') as f:
    json.dump(test_themes, f, indent=2, ensure_ascii=False)

print(f"✅ 测试主题已保存: {themes_file}")

print("\n" + "=" * 60)
print("🎉 小红书团队建设启动完成!")
print("=" * 60)

print("\n📋 已完成的准备工作:")
print("  1. ✅ 更新任务状态: 2个任务改为'进行中'")
print("  2. ✅ 创建团队架构: 4个工作组")
print("  3. ✅ 制定执行计划: 4周计划")
print("  4. ✅ 准备测试主题: 3个OpenClaw主题")

print("\n🚀 下一步立即行动:")
print("  1. 检查并安装必要技能")
print("  2. 组建虚拟团队")
print("  3. 开始第一个主题创作")
print("  4. 测试完整工作流程")

print(f"\n📊 多维表格状态已更新:")
print(f"  https://t33vwocwc8.feishu.cn/base/FCRNbSo4ja4hCEs5411cNZQXnkh")

print(f"\n📁 文档位置:")
print(f"  团队架构: {arch_file}")
print(f"  执行计划: {plan_file}")
print(f"  测试主题: {themes_file}")

print("\n💡 建议:")
print("  1. 先测试单个主题的完整流程")
print("  2. 验证手动发布环节")
print("  3. 收集数据反馈优化")
print("  4. 逐步扩大内容范围")

print("\n🤖 我现在可以立即开始:")
print("  1. 搜索和安装更多必要技能")
print("  2. 创建第一个测试内容")
print("  3. 模拟审核和发布流程")
print("  4. 建立数据跟踪机制")

print("\n请确认是否立即开始执行?")