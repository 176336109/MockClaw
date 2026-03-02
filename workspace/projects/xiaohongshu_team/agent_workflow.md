# 小红书Agent团队工作流程

## 🏗️ 团队架构

### 管理层
1. **Agent Orchestrator** - 团队协调员
2. **Agent Council** - 决策委员会
3. **Agent Evaluation** - 绩效评估

### 内容创作层
4. **Trend Finder** - 热点发现
5. **Content Planner** - 内容策划
6. **Image Creator** - 图像生成
7. **Copywriter** - 文案创作
8. **Layout Designer** - 排版设计
9. **Quality Reviewer** - 质量审核

### 发布运营层
10. **Scheduler** - 排期管理
11. **Publisher** - 发布执行
12. **Engagement Manager** - 互动管理
13. **Data Analyst** - 数据分析

### 支持层
14. **Knowledge Manager** - 知识管理
15. **Tool Manager** - 工具管理
16. **Exception Handler** - 异常处理

## 🔄 工作流程

### 阶段1：内容策划
```
Trend Finder → Content Planner → Agent Council
    ↓
热点发现 → 内容策划 → 决策批准
```

### 阶段2：内容创作
```
Image Creator + Copywriter → Layout Designer → Quality Reviewer
    ↓
图像生成 + 文案创作 → 排版设计 → 质量审核
```

### 阶段3：发布运营
```
Scheduler → Publisher → Engagement Manager → Data Analyst
    ↓
排期管理 → 发布执行 → 互动管理 → 数据分析
```

### 阶段4：知识积累
```
所有Agent → Knowledge Manager → Tool Manager
    ↓
经验积累 → 知识管理 → 工具优化
```

## 📋 Agent职责定义

### Agent Orchestrator (团队协调员)
- **职责**: 协调各Agent工作，分配任务，监控进度
- **输入**: 宏观任务、成功标准
- **输出**: 分解的子任务、Agent分配、进度报告
- **工具**: agent-orchestrator技能

### Agent Council (决策委员会)
- **职责**: 重大决策，策略制定，冲突解决
- **输入**: 提案、选项分析、风险评估
- **输出**: 决策结果、策略指导、冲突解决方案
- **工具**: agent-council技能

### Trend Finder (热点发现Agent)
- **职责**: 发现小红书热点话题，趋势分析
- **输入**: 时间范围、话题领域
- **输出**: 热点话题列表、趋势分析报告
- **工具**: bocha-web-search技能

### Content Planner (内容策划Agent)
- **职责**: 制定内容策略，选题规划
- **输入**: 热点话题、品牌定位、目标受众
- **输出**: 内容策划方案、选题列表、排期建议
- **工具**: ontology技能

### Image Creator (图像生成Agent)
- **职责**: 生成小红书风格图片，封面设计
- **输入**: 内容主题、风格要求、尺寸规格
- **输出**: 图像文件、设计说明
- **工具**: nano-banana-pro技能

### Copywriter (文案创作Agent)
- **职责**: 撰写小红书文案，标题优化
- **输入**: 内容主题、目标受众、关键词
- **输出**: 文案内容、标题选项、标签建议
- **工具**: gemini、xiaohongshu-title技能

## 🛠️ 通信协议

### 文件通信机制
```
workspace/projects/xiaohongshu_team/
├── tasks/          # 任务文件
├── outputs/        # 输出文件
├── communications/ # 通信文件
└── knowledge/      # 知识文件
```

### 任务文件格式
```json
{
  "task_id": "TASK-20260302-001",
  "agent": "TrendFinder",
  "input": {
    "time_range": "24h",
    "topic_domain": "美妆护肤"
  },
  "output_expected": "热点话题列表",
  "deadline": "2026-03-02T12:00:00Z"
}
```

### 输出文件格式
```json
{
  "task_id": "TASK-20260302-001",
  "agent": "TrendFinder",
  "status": "completed",
  "output": {
    "hot_topics": [...],
    "trend_analysis": "..."
  },
  "timestamp": "2026-03-02T10:30:00Z"
}
```

## 🚀 第一阶段目标

### 目标1：建立基础通信机制
- [ ] 创建任务文件系统
- [ ] 建立输出文件标准
- [ ] 测试Agent间文件通信

### 目标2：实现简单工作流程
- [ ] Trend Finder → Content Planner 流程
- [ ] 测试热点发现到内容策划
- [ ] 验证文件传递机制

### 目标3：建立监控系统
- [ ] 任务状态跟踪
- [ ] 进度报告生成
- [ ] 异常处理机制

## 📊 成功标准

### 技术标准
- ✅ Agent间文件通信正常
- ✅ 任务分解和分配正确
- ✅ 输出文件格式统一

### 功能标准
- ✅ 热点发现功能正常
- ✅ 内容策划功能正常
- ✅ 决策流程正常

### 效率标准
- ✅ 任务完成时间 < 30分钟
- ✅ 文件传递延迟 < 1分钟
- ✅ 系统可用性 > 95%

## 🔧 实施步骤

### 步骤1：创建项目目录结构
```bash
mkdir -p projects/xiaohongshu_team/{tasks,outputs,communications,knowledge}
```

### 步骤2：创建第一个任务
创建热点发现任务文件

### 步骤3：启动Trend Finder Agent
使用bocha-web-search技能执行任务

### 步骤4：传递结果给Content Planner
将输出文件传递给下一个Agent

### 步骤5：验证完整流程
检查端到端工作流程

---

**创建时间**: 2026-03-02 00:56  
**版本**: v1.0  
**状态**: 实施中