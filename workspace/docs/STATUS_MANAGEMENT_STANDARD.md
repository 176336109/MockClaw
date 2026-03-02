# 📋 任务状态管理标准

## 🎯 目的
确保多维表格中的任务状态统一、一致，避免"已完成" vs "完成"等不统一问题。

## 📊 标准状态枚举

### 核心状态（必须使用）
| 状态 | 含义 | 使用场景 | 示例 |
|------|------|----------|------|
| **进行中** | 任务正在执行 | 任务已开始，正在处理中 | "修复API问题"、"开发新功能" |
| **完成** | 任务已完成并验证 | 任务已成功完成，已验证 | "Skill状态检查完成"、"文档创建完成" |
| **等待指示** | 需要用户决策 | 需要用户确认、选择或提供信息 | "等待确认是否继续安装" |
| **搁置** | 任务已停止 | 任务暂停、取消或暂时不处理 | "功能暂时搁置"、"优先级调整" |

### 扩展状态（根据需要）
| 状态 | 含义 | 使用场景 | 示例 |
|------|------|----------|------|
| **测试中** | 任务处于测试阶段 | 功能开发完成，正在测试验证 | "API接口测试"、"功能验证测试" |

## 🔄 状态统一规则

### 映射规则（旧状态 → 新状态）
| 旧状态 | 新状态 | 说明 |
|--------|--------|------|
| 已完成 | 完成 | 统一使用"完成" |
| 已完 | 完成 | 统一使用"完成" |
| 完成✅ | 完成 | 移除表情符号 |
| 进行中🚀 | 进行中 | 移除表情符号 |
| 等待中 | 等待指示 | 统一使用"等待指示" |
| 待处理 | 等待指示 | 统一使用"等待指示" |
| 暂停 | 搁置 | 统一使用"搁置" |
| 取消 | 搁置 | 统一使用"搁置" |

### 禁止使用的状态
- ❌ "已完成"（使用"完成"）
- ❌ "已完"（使用"完成"）
- ❌ 带表情符号的状态（如"完成✅"）
- ❌ 英文状态（如"Done"、"In Progress"）
- ❌ 自定义状态（除非添加到扩展状态）

## 🛠️ 状态管理流程

### 1. 状态设置
```python
# 正确
status = "完成"

# 错误  
status = "已完成"
status = "完成✅"
```

### 2. 状态更新
- **实时更新**：任务状态变化时立即更新
- **批量同步**：定期同步所有任务状态
- **验证检查**：更新后验证状态一致性

### 3. 状态验证
```python
def validate_status(status):
    """验证状态是否标准"""
    standard_statuses = ["进行中", "完成", "等待指示", "搁置", "测试中"]
    return status in standard_statuses
```

## 📈 状态统计指标

### 健康指标
| 指标 | 目标 | 说明 |
|------|------|------|
| 状态一致性 | 100% | 所有任务使用标准状态 |
| 更新及时性 | <5分钟 | 状态变化后5分钟内更新 |
| 错误率 | <1% | 状态更新失败率 |

### 监控方法
1. **定期检查**：每天检查状态一致性
2. **自动验证**：API调用时验证状态
3. **手动抽查**：随机抽查任务状态

## 🔧 技术实现

### Python状态管理类
```python
class StatusManager:
    """状态管理器"""
    
    STANDARD_STATUSES = ["进行中", "完成", "等待指示", "搁置", "测试中"]
    
    STATUS_MAPPING = {
        "已完成": "完成",
        "已完": "完成",
        "完成✅": "完成",
        "进行中🚀": "进行中",
        "等待中": "等待指示",
        "待处理": "等待指示",
        "暂停": "搁置",
        "取消": "搁置"
    }
    
    def normalize_status(self, status):
        """标准化状态"""
        return self.STATUS_MAPPING.get(status, status)
    
    def is_standard_status(self, status):
        """检查是否标准状态"""
        return status in self.STANDARD_STATUSES
    
    def validate_and_fix(self, task_id, current_status):
        """验证并修复状态"""
        normalized = self.normalize_status(current_status)
        
        if not self.is_standard_status(normalized):
            # 记录非标准状态
            self.log_non_standard_status(task_id, current_status, normalized)
            
        return normalized
```

### API调用规范
```python
# 更新任务状态
def update_task_status(task_id, task_name, status, details=""):
    """更新任务状态（自动标准化）"""
    status_manager = StatusManager()
    normalized_status = status_manager.validate_and_fix(task_id, status)
    
    # 调用API
    record_data = {
        "fields": {
            "任务ID": task_id,
            "任务名称": task_name,
            "状态": normalized_status,  # 使用标准化后的状态
            "描述": details
        }
    }
    
    # ... API调用逻辑
```

## 📝 维护责任

### 我的责任
1. **状态标准化**：确保所有API调用使用标准状态
2. **定期检查**：每天检查表格状态一致性
3. **及时修复**：发现非标准状态立即修复
4. **更新记忆**：状态标准变化时更新MEMORY.md

### 验证方法
1. **查看多维表格**：https://t33vwocwc8.feishu.cn/base/FCRNbSo4ja4hCEs5411cNZQXnkh
2. **检查状态分布**：确保只有标准状态
3. **验证映射规则**：检查"已完成"是否已全部改为"完成"

## 🚨 问题处理

### 常见问题
1. **状态不统一**：运行状态统一脚本
2. **API调用失败**：检查token和字段名
3. **新增状态需求**：先更新本标准文档

### 紧急修复
```bash
# 运行状态统一脚本
cd ~/.openclaw/workspace
python3 unify_table_status.py
```

## 📚 相关文档
- [MEMORY.md](../MEMORY.md) - 长期记忆，包含状态标准
- [多维表格地址](https://t33vwocwc8.feishu.cn/base/FCRNbSo4ja4hCEs5411cNZQXnkh) - 任务状态看板

## 📅 更新记录
| 日期 | 版本 | 变更说明 |
|------|------|----------|
| 2026-03-02 | 1.0 | 初始版本，统一"已完成"→"完成" |
| 2026-03-02 | 1.1 | 新增"测试中"为扩展状态 |

---

**最后更新**: 2026-03-02  
**维护者**: OpenClaw主Agent  
**验证状态**: ✅ 已统一11条"已完成"记录为"完成"