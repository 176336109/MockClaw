# OpenClaw Workspace

整理后的工作区结构，保持清晰有序。

## 📁 目录结构

### `core/` - 核心配置文件
- `AGENTS.md` - Agent工作指南
- `MEMORY.md` - 长期记忆
- `SOUL.md` - 身份定义
- `USER.md` - 用户信息
- `TOOLS.md` - 工具配置
- `IDENTITY.md` - 身份标识
- `HEARTBEAT.md` - 心跳任务
- `BOOTSTRAP.md` - 启动指南

### `scripts/` - 工具脚本
- `bitable_updater.sh` - 多维表格更新引擎
- `update_task.sh` - 标准化任务更新
- `update_bitable.py` - Python更新脚本
- `read_and_update_bitable.sh` - 读取和更新脚本

### `skills/` - 技能目录
- `bocha-web-search/` - 博查搜索技能
- `find-skills/` - 技能发现
- `multi-search-engine/` - 多搜索引擎
- `evomap-tools/` - EvoMap工具

### `projects/` - 项目文件
- 飞书API相关项目
- 任务管理工具
- 代码示例和原型

### `docs/` - 文档资料
- 各种研究文档
- 技术指南
- 总结报告

### `memory/` - 记忆文件
- 每日记忆记录
- 会话历史

### `temp/` - 临时文件
- 临时工作文件
- 缓存数据

### `backups/` - 备份文件
- 重要数据备份

## 🔧 使用说明

### 更新多维表格
```bash
# 标准化任务更新
./scripts/update_task.sh

# 自定义更新
source ./scripts/bitable_updater.sh
TOKEN=$(get_token)
add_task_record "$TOKEN" "TASK-ID" "任务名" "描述" "状态" "分类" "产出"
```

### 核心配置
- 编辑 `core/` 目录下的文件修改身份、记忆等
- `MEMORY.md` 包含重要系统信息（如多维表格地址）

## 📊 系统状态

### 已建立的系统
1. ✅ 多维表格自动更新机制
2. ✅ 标准化工作流程
3. ✅ 整理的工作区结构
4. ✅ 实时任务跟踪

### 维护原则
- 保持目录结构清晰
- 及时清理临时文件
- 重要文件备份
- 脚本路径使用相对引用

## 🔄 更新日志

### 2026-03-01
- 整理工作区，创建清晰目录结构
- 建立多维表格自动更新系统
- 标准化任务跟踪流程