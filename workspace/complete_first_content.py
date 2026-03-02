#!/usr/bin/env python3
"""
完善第一个小红书内容，准备审核
"""

import json
from pathlib import Path
from datetime import datetime

print("🎨 完善第一个小红书内容")
print("=" * 60)

# 读取现有内容
content_file = Path.home() / ".openclaw" / "workspace" / "first_xiaohongshu_content.json"
with open(content_file, 'r', encoding='utf-8') as f:
    content = json.load(f)

# 1. 完善标题（使用xiaohongshu-title技能优化）
print("1. 优化标题方案...")
optimized_titles = [
    "🤖 OpenClaw保姆级教程｜AI助手这样用效率翻3倍",
    "新手必看！OpenClaw从安装到实战全流程",
    "每天多出2小时！我用OpenClaw自动化了这些工作",
    "AI助手OpenClaw：你的24小时私人智能助理",
    "后悔没早用！OpenClaw让工作效率起飞"
]

content['标题方案'] = optimized_titles
print(f"  生成{len(optimized_titles)}个优化标题")

# 2. 完善正文细节
print("\n2. 完善正文细节...")

# 添加具体的使用示例
usage_examples = [
    "📝 内容创作示例：",
    "   - 让OpenClaw帮你写小红书文案",
    "   - 自动生成文章大纲和标题",
    "   - 批量处理图片和视频素材",
    "",
    "📊 数据分析示例：",
    "   - 自动整理Excel表格数据",
    "   - 生成数据可视化报告",
    "   - 监控关键指标变化",
    "",
    "🤖 自动化示例：",
    "   - 定时发送日报邮件",
    "   - 自动回复常见问题",
    "   - 监控网站更新并通知",
    "",
    "🎯 学习研究示例：",
    "   - 快速查找学术资料",
    "   - 整理读书笔记",
    "   - 翻译外文文档"
]

# 插入到正文大纲中
insert_index = content['正文大纲'].index("💡 第三部分：实用场景推荐") + 1
for i, example in enumerate(reversed(usage_examples)):
    content['正文大纲'].insert(insert_index, example)

print("  添加具体使用示例")

# 3. 生成封面设计建议
print("\n3. 生成封面设计建议...")

cover_designs = [
    {
        "风格": "科技简约风",
        "元素": ["OpenClaw logo", "简洁线条", "渐变背景"],
        "配色": ["深蓝+白色", "科技感配色"],
        "文案": "OpenClaw入门指南",
        "适用标题": optimized_titles[0]
    },
    {
        "风格": "步骤图解风", 
        "元素": ["数字步骤", "图标", "箭头指引"],
        "配色": ["橙色+灰色", "清晰对比"],
        "文案": "5步快速上手",
        "适用标题": optimized_titles[1]
    },
    {
        "风格": "前后对比风",
        "元素": ["时间对比图", "效率提升数据", "表情符号"],
        "配色": ["绿色+红色", "对比强烈"],
        "文案": "效率提升300%",
        "适用标题": optimized_titles[2]
    },
    {
        "风格": "亲切场景风",
        "元素": ["工作场景", "设备展示", "人物剪影"],
        "配色": ["暖色调", "亲和力强"],
        "文案": "你的智能工作伙伴",
        "适用标题": optimized_titles[3]
    }
]

content['封面设计详情'] = cover_designs
print(f"  生成{len(cover_designs)}个封面设计方案")

# 4. 准备审核检查表
print("\n4. 准备审核检查表...")

audit_checklist = {
    "内容准确性": [
        "OpenClaw功能描述是否正确",
        "安装步骤是否准确",
        "使用示例是否真实可行",
        "数据引用是否准确"
    ],
    "实用性": [
        "步骤是否清晰可操作",
        "示例是否贴近实际需求",
        "技巧是否立即可用",
        "资源链接是否有效"
    ],
    "合规性": [
        "内容是否符合小红书社区规范",
        "是否有违规词汇",
        "图片版权是否合规",
        "是否涉及敏感话题"
    ],
    "吸引力": [
        "标题是否吸引目标用户",
        "封面设计是否突出",
        "开头是否引人入胜",
        "内容结构是否清晰"
    ],
    "完整性": [
        "是否涵盖核心功能",
        "是否有常见问题解答",
        "是否有后续学习指引",
        "是否有互动引导"
    ],
    "风格一致性": [
        "语言风格是否统一",
        "配图风格是否一致",
        "排版格式是否规范",
        "品牌露出是否恰当"
    ]
}

content['审核检查表'] = audit_checklist
print("  创建详细审核检查表")

# 5. 制定发布计划
print("\n5. 制定发布计划...")

publish_plan = {
    "发布前准备": [
        "确认内容最终版本",
        "准备封面图片",
        "检查标签和话题",
        "准备互动话术"
    ],
    "发布时间建议": [
        "最佳时间: 工作日晚上8-10点",
        "备选时间: 周末下午3-5点",
        "避开时间: 工作日早上、深夜"
    ],
    "发布操作步骤": [
        "1. 打开小红书App",
        "2. 点击底部'+'号",
        "3. 选择'发布笔记'",
        "4. 上传封面图片",
        "5. 粘贴正文内容",
        "6. 添加标签和话题",
        "7. 选择合适分类",
        "8. 点击发布"
    ],
    "发布后操作": [
        "监控前30分钟数据",
        "及时回复评论",
        "观察互动趋势",
        "记录关键数据"
    ],
    "数据跟踪指标": [
        "阅读量 (24小时)",
        "点赞数",
        "收藏数", 
        "评论数",
        "分享数",
        "粉丝增长"
    ]
}

content['发布计划'] = publish_plan
print("  制定详细发布计划")

# 6. 更新工作流程状态
content['工作流程状态']['创作'] = "已完成"
content['工作流程状态']['审核'] = "待审核"
content['最后更新时间'] = datetime.now().isoformat()

# 保存更新后的内容
with open(content_file, 'w', encoding='utf-8') as f:
    json.dump(content, f, indent=2, ensure_ascii=False)

print(f"\n✅ 内容完善完成，已保存到: {content_file}")

# 创建审核准备包
audit_package = {
    "审核项目": "小红书内容审核",
    "审核内容": content['主题'],
    "提交时间": datetime.now().isoformat(),
    "提交人": "创作组",
    "审核人": "审核组",
    "紧急程度": "正常",
    
    "审核材料": [
        f"完整内容JSON: {content_file}",
        f"Markdown版本: {Path.home() / '.openclaw' / 'workspace' / 'first_xiaohongshu_content.md'}",
        "标题方案: 5个选项",
        "封面设计方案: 4个",
        "审核检查表: 6个维度",
        "发布计划: 完整流程"
    ],
    
    "审核要求": {
        "审核时间": "2小时内",
        "审核方式": "内容审查 + 合规检查",
        "审核标准": "参考审核检查表",
        "审核结果": "通过/修改/重做"
    },
    
    "审核流程": [
        "1. 下载审核材料",
        "2. 按照检查表逐项审核",
        "3. 记录审核意见",
        "4. 给出审核结论",
        "5. 反馈给创作组"
    ],
    
    "审核工具": [
        "小红书社区规范",
        "内容质量检查表",
        "合规性检查工具",
        "数据准确性验证"
    ]
}

audit_file = Path.home() / ".openclaw" / "workspace" / "audit_package.json"
with open(audit_file, 'w', encoding='utf-8') as f:
    json.dump(audit_package, f, indent=2, ensure_ascii=False)

print(f"✅ 审核准备包已创建: {audit_file}")

# 创建飞书消息格式
feishu_message = f"""📋 小红书内容审核请求

**项目**: 小红书OpenClaw主题内容系统
**内容**: {content['主题']}
**状态**: 创作完成，等待审核
**提交时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

**📌 核心信息**
- 标题方案: {len(content['标题方案'])}个
- 正文要点: {len([x for x in content['正文大纲'] if x])}个
- 封面设计: {len(content['封面设计详情'])}个方案
- 标签建议: {len(content['标签建议'])}个

**✅ 已完成**
1. 内容创作完成
2. 标题优化完成  
3. 封面设计建议
4. 审核检查表准备
5. 发布计划制定

**📁 文件附件**
1. 完整内容JSON
2. Markdown版本
3. 审核准备包
4. 任务跟踪文件

**⏰ 审核要求**
- 审核时间: 2小时内
- 审核标准: 参考审核检查表
- 审核结论: 通过/修改/重做

**🚀 下一步**
审核通过后 → 准备发布材料 → 手动发布 → 数据跟踪

请审核组开始工作，完成后反馈审核结果。
"""

feishu_file = Path.home() / ".openclaw" / "workspace" / "feishu_audit_message.txt"
with open(feishu_file, 'w', encoding='utf-8') as f:
    f.write(feishu_message)

print(f"✅ 飞书消息已准备: {feishu_file}")

print("\n" + "=" * 60)
print("🎉 第一个内容完善完成，准备审核!")
print("=" * 60)

print("\n📋 产出概览:")
print(f"  1. 优化标题: {len(content['标题方案'])}个")
print(f"  2. 封面设计: {len(content['封面设计详情'])}个方案")
print(f"  3. 审核检查: {sum(len(v) for v in audit_checklist.values())}个检查点")
print(f"  4. 发布计划: {len(publish_plan)}个部分")

print("\n📁 生成的文件:")
print(f"  • 完善内容: {content_file}")
print(f"  • 审核包: {audit_file}")
print(f"  • 飞书消息: {feishu_file}")

print("\n🚀 下一步行动:")
print("  1. 发送审核请求到飞书")
print("  2. 等待审核组审核")
print("  3. 根据反馈修改内容")
print("  4. 准备发布材料")

print("\n💡 审核要点提醒:")
for category, items in audit_checklist.items():
    print(f"  {category}: {len(items)}个检查点")

print("\n现在需要将审核请求发送到飞书聊天。")