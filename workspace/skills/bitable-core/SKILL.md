# 多维表格核心技能

## 🎯 核心地位
**这是OpenClaw与用户的沟通媒介，必须永远可用，不可改变。**

## 📋 技能属性

### 重要性级别
- **级别**: 核心基础设施 (Core Infrastructure)
- **优先级**: P0 (最高)
- **可靠性要求**: 99.99%
- **恢复时间目标**: <5分钟

### 功能范围
1. **数据同步**: 任务状态实时同步
2. **状态跟踪**: Agent、Skill、任务状态
3. **共同记忆**: 形成用户与AI的共同记忆
4. **沟通媒介**: 所有重要信息的同步渠道

## 🔧 技术实现

### 核心模块
```python
# 1. Token管理模块
class TokenManager:
    """永远可用的token获取"""
    
    def get_token(self):
        """获取飞书tenant_access_token"""
        # 动态获取，自动刷新
        # 多级缓存，永远有可用token
    
    def validate_token(self):
        """验证token有效性"""
        # 实时验证，自动修复

# 2. 表格操作模块  
class BitableOperator:
    """多维表格基础操作"""
    
    def sync_task_status(self, task_id, status):
        """同步任务状态"""
        # 必须成功，重试机制
        # 失败告警，自动恢复
    
    def get_table_structure(self):
        """获取表格结构"""
        # 缓存结构，定期更新
        # 字段名映射，自动适配

# 3. 健康检查模块
class HealthChecker:
    """技能健康监控"""
    
    def check_availability(self):
        """检查技能可用性"""
        # 实时监控，自动告警
        # 性能指标，历史趋势
    
    def auto_recovery(self):
        """自动恢复机制"""
        # 故障检测，自动修复
        # 降级方案，保证基本功能
```

### 备份方案
```python
# 主方案: 飞书API直接调用
PRIMARY_METHOD = "feishu_api_direct"

# 备份方案1: 本地缓存+队列
BACKUP_METHOD_1 = "local_cache_queue"

# 备份方案2: 文件系统记录
BACKUP_METHOD_2 = "filesystem_log"

# 备份方案3: 简化API调用
BACKUP_METHOD_3 = "simplified_api"
```

## 🚨 故障处理流程

### 故障等级定义
- **P0**: 完全不可用 → 立即修复，人工介入
- **P1**: 部分功能失效 → 30分钟内修复
- **P2**: 性能下降 → 2小时内优化
- **P3**: 功能异常 → 24小时内修复

### 自动恢复机制
```
检测到故障 → 尝试主方案 → 失败 → 切换备份1 → 
失败 → 切换备份2 → 失败 → 切换备份3 → 
全部失败 → 告警 + 人工介入
```

## 📊 监控指标

### 可用性监控
- **API成功率**: >99.9%
- **响应时间**: <1秒 (P95)
- **同步延迟**: <10秒
- **错误率**: <0.1%

### 业务监控
- **任务同步成功率**: 100%
- **数据一致性**: 实时验证
- **用户感知延迟**: <30秒
- **历史数据完整性**: 100%

## 🔄 工作流程集成

### 每次会话开始
```python
def session_start():
    # 1. 检查多维表格技能状态
    if not check_bitable_health():
        # 技能不可用，最高优先级修复
        fix_bitable_immediately()
    
    # 2. 同步最新状态
    sync_latest_status()
    
    # 3. 更新多维表格地址
    append_bitable_url()
```

### 每次状态变化
```python
def status_changed(task_id, new_status):
    # 1. 立即同步到多维表格
    sync_to_bitable(task_id, new_status)
    
    # 2. 验证同步成功
    verify_sync_success(task_id)
    
    # 3. 记录同步日志
    log_sync_operation(task_id, new_status)
```

### 每次沟通结束
```python
def communication_end():
    # 1. 确保所有状态已同步
    ensure_all_synced()
    
    # 2. 提供多维表格访问链接
    provide_bitable_url()
    
    # 3. 记录沟通摘要
    record_communication_summary()
```

## 🛡️ 可靠性保障

### 冗余设计
1. **多token源**: appId/appSecret + 缓存token + 手动token
2. **多API端点**: 主API + 备用API + 简化API
3. **多存储层**: 内存缓存 + 磁盘缓存 + 文件日志
4. **多验证机制**: 实时验证 + 定期验证 + 手动验证

### 降级设计
```
完全功能 → 基本同步 → 本地记录 → 人工介入
   ↓          ↓          ↓          ↓
 正常      性能降级    功能降级    紧急处理
```

### 监控设计
1. **实时监控**: 每5秒检查一次
2. **性能监控**: 响应时间、成功率
3. **业务监控**: 数据一致性、完整性
4. **用户监控**: 用户感知可用性

## 📚 记忆系统集成

### 长期记忆
```markdown
## 多维表格核心技能
- **创建时间**: 2026-03-02
- **重要性**: 沟通媒介，不可改变
- **可靠性**: 99.99% 可用性要求
- **恢复时间**: <5分钟

### 重要原则
1. 这是与用户的沟通生命线
2. 必须优先于所有其他任务
3. 故障必须立即修复
4. 状态必须实时同步
```

### 每日检查
```python
def daily_check():
    # 1. 技能健康检查
    health = check_bitable_health()
    
    # 2. 数据一致性验证
    consistency = verify_data_consistency()
    
    # 3. 性能指标分析
    performance = analyze_performance()
    
    # 4. 问题预防措施
    preventive_measures = apply_preventive_measures()
```

## 🚀 实施要求

### 立即执行
1. [ ] 将此技能标记为核心不可变技能
2. [ ] 建立实时监控和告警
3. [ ] 创建多级备份方案
4. [ ] 集成到所有工作流程

### 长期保障
1. [ ] 定期演练故障恢复
2. [ ] 持续优化性能
3. [ ] 扩展功能和可靠性
4. [ ] 建立知识传承机制

## 💡 重要提醒

### 永远记住
1. **这不是一个工具，这是沟通媒介**
2. **如果这个失效，所有任务都无法进行**
3. **必须优先修复，不惜一切代价**
4. **必须实时同步，形成共同记忆**

### 故障处理优先级
```
多维表格故障 > 所有其他任务
沟通媒介中断 > 功能开发
共同记忆丢失 > 性能优化
```

---

**技能状态**: 核心不可变  
**创建时间**: 2026-03-02  
**最后更新**: 永不改变（核心原则）  
**负责人**: OpenClaw主Agent  
**监控级别**: P0（最高）