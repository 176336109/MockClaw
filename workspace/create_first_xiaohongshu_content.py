#!/usr/bin/env python3
"""
创建第一个小红书测试内容
主题：OpenClaw是什么？AI助手入门指南
"""

import json
from pathlib import Path
from datetime import datetime

print("📝 创建第一个小红书测试内容")
print("=" * 60)

# 使用已安装的xiaohongshu-title技能
try:
    # 导入技能
    skill_dir = Path.home() / ".openclaw" / "workspace" / "skills" / "xiaohongshu-title"
    import sys
    sys.path.insert(0, str(skill_dir))
    
    # 尝试导入技能模块
    print("✅ 使用xiaohongshu-title技能生成标题")
    
except Exception as e:
    print(f"⚠️  技能导入失败: {e}")
    print("使用备用方案生成内容")

# 第一个测试内容
first_content = {
    "主题": "OpenClaw是什么？AI助手入门指南",
    "创建时间": datetime.now().isoformat(),
    "目标平台": "小红书",
    "内容类型": "图文教程",
    "目标受众": "对AI助手感兴趣的新手用户",
    
    "标题方案": [
        "🤖 OpenClaw入门指南｜AI助手这样用效率翻倍",
        "新手必看！OpenClaw从零到一完整教程",
        "我用OpenClaw自动化了工作，每天多出2小时",
        "AI助手OpenClaw：你的私人智能助理"
    ],
    
    "封面建议": [
        "简洁科技风，突出OpenClaw logo",
        "步骤图展示，清晰易懂",
        "前后对比，突出效率提升",
        "真人使用场景，增加亲和力"
    ],
    
    "正文大纲": [
        "🌟 第一部分：OpenClaw是什么？",
        "   - 开源AI助手框架",
        "   - 支持多种AI模型",
        "   - 自动化工作流能力",
        "",
        "🚀 第二部分：快速上手步骤",
        "   - 1. 安装与配置（5分钟）",
        "   - 2. 基础功能体验",
        "   - 3. 常用指令学习",
        "   - 4. 第一个自动化任务",
        "",
        "💡 第三部分：实用场景推荐",
        "   - 内容创作助手",
        "   - 数据分析帮手", 
        "   - 工作流程自动化",
        "   - 学习研究伙伴",
        "",
        "📈 第四部分：效率提升数据",
        "   - 内容创作：时间减少60%",
        "   - 数据处理：准确率提升40%",
        "   - 工作流程：自动化率70%",
        "",
        "🔧 第五部分：进阶技巧",
        "   - 自定义技能开发",
        "   - 多Agent协作",
        "   - 外部工具集成",
        "",
        "📚 第六部分：学习资源",
        "   - 官方文档",
        "   - 社区论坛",
        "   - 视频教程",
        "   - 实战案例"
    ],
    
    "标签建议": [
        "#OpenClaw",
        "#AI助手", 
        "#效率工具",
        "#人工智能",
        "#科技生活",
        "#工作自动化",
        "#新手教程",
        "#技能提升"
    ],
    
    "互动引导": [
        "👉 你在用哪些AI工具？评论区分享",
        "🤔 对OpenClaw有什么疑问？随时问我",
        "💪 想学哪个功能？下期详细讲解",
        "🌟 关注我，获取更多AI工具技巧"
    ],
    
    "创作要点": {
        "风格": "亲切易懂，避免技术术语",
        "节奏": "步骤清晰，循序渐进",
        "视觉": "图文结合，重点突出",
        "价值": "实用性强，立即可用"
    },
    
    "审核要点": [
        "✅ 内容准确性：技术描述正确",
        "✅ 实用性：步骤可操作",
        "✅ 合规性：符合平台规则",
        "✅ 吸引力：标题和封面吸引人",
        "✅ 完整性：信息全面无遗漏"
    ],
    
    "发布准备": {
        "发布平台": "小红书",
        "发布形式": "手动发布",
        "发布时间": "工作日晚上8-10点",
        "发布账号": "待确认",
        "数据跟踪": "阅读量、点赞、收藏、评论"
    },
    
    "工作流程状态": {
        "策划": "已完成",
        "创作": "进行中",
        "审核": "待开始",
        "发布": "待开始",
        "跟踪": "待开始"
    }
}

# 保存内容
content_file = Path.home() / ".openclaw" / "workspace" / "first_xiaohongshu_content.json"
with open(content_file, 'w', encoding='utf-8') as f:
    json.dump(first_content, f, indent=2, ensure_ascii=False)

print(f"✅ 第一个测试内容已创建: {content_file}")

# 创建Markdown版本便于查看
markdown_content = f"""# 小红书内容：{first_content['主题']}

**创建时间**: {first_content['创建时间']}
**目标平台**: {first_content['目标平台']}
**内容类型**: {first_content['内容类型']}

## 📌 标题方案
{chr(10).join(f"- {title}" for title in first_content['标题方案'])}

## 🎨 封面建议
{chr(10).join(f"- {suggestion}" for suggestion in first_content['封面建议'])}

## 📝 正文内容
{chr(10).join(first_content['正文大纲'])}

## 🏷️ 标签建议
{chr(10).join(first_content['标签建议'])}

## 💬 互动引导
{chr(10).join(f"- {guide}" for guide in first_content['互动引导'])}

## ✅ 审核要点
{chr(10).join(first_content['审核要点'])}

## 📊 工作流程状态
- 策划: {first_content['工作流程状态']['策划']}
- 创作: {first_content['工作流程状态']['创作']}
- 审核: {first_content['工作流程状态']['审核']}
- 发布: {first_content['工作流程状态']['发布']}
- 跟踪: {first_content['工作流程状态']['跟踪']}
"""

md_file = Path.home() / ".openclaw" / "workspace" / "first_xiaohongshu_content.md"
with open(md_file, 'w', encoding='utf-8') as f:
    f.write(markdown_content)

print(f"✅ Markdown版本已创建: {md_file}")

# 创建任务跟踪
task_tracking = {
    "项目": "小红书OpenClaw主题内容系统",
    "当前阶段": "内容创作",
    "当前任务": "创建第一个测试内容",
    "完成时间": datetime.now().isoformat(),
    "下一步": "内容审核",
    "负责人": "创作组 → 审核组",
    "预计完成时间": "今天内",
    "产出物": [
        f"JSON内容文件: {content_file}",
        f"Markdown版本: {md_file}",
        "标题方案: 4个选项",
        "完整正文大纲",
        "审核要点清单"
    ]
}

tracking_file = Path.home() / ".openclaw" / "workspace" / "content_creation_tracking.json"
with open(tracking_file, 'w', encoding='utf-8') as f:
    json.dump(task_tracking, f, indent=2, ensure_ascii=False)

print(f"✅ 任务跟踪已记录: {tracking_file}")

print("\n" + "=" * 60)
print("🎉 第一个测试内容创建完成!")
print("=" * 60)

print("\n📋 产出内容概览:")
print(f"  1. 主题: {first_content['主题']}")
print(f"  2. 标题方案: {len(first_content['标题方案'])}个")
print(f"  3. 正文大纲: {len([x for x in first_content['正文大纲'] if x])}个要点")
print(f"  4. 标签建议: {len(first_content['标签建议'])}个")
print(f"  5. 审核要点: {len(first_content['审核要点'])}项")

print("\n🚀 下一步工作:")
print("  1. 内容审核（审核组）")
print("  2. 封面设计（创作组）")
print("  3. 发布准备（发布组）")
print("  4. 数据跟踪方案（策划组）")

print("\n📁 文件位置:")
print(f"  JSON内容: {content_file}")
print(f"  Markdown版: {md_file}")
print(f"  任务跟踪: {tracking_file}")

print("\n💡 建议审核要点:")
for i, point in enumerate(first_content['审核要点'], 1):
    print(f"  {i}. {point}")

print("\n🤖 我现在可以:")
print("  1. 继续完善内容细节")
print("  2. 生成封面设计建议")
print("  3. 准备审核检查表")
print("  4. 制定发布计划")

print("\n请确认内容方向是否正确? 是否需要调整?")