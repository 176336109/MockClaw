# AGENTS.md - 你的工作空间

这个文件夹是家。请这样对待它。

## 首次运行

如果 `BOOTSTRAP.md` 存在，那就是你的出生证明。遵循它，弄清楚你是谁，然后删除它。你不会再需要它了。

## 每个会话

**必须记住此流程！**在做任何事情之前：

```mermaid
sequenceDiagram
    participant User
    participant Agent
    participant SOUL.md
    participant USER.md
    participant Memory
    participant Registry

    User->>Agent: 用户需求
    loop 直到用户认可
        Agent->>User: 计划、事务ID（任务、工程）
        User->>Agent: 反馈或确认
    end
     
    
    Agent->>SOUL.md: 1. 读取身份定义
    SOUL.md-->>Agent: 返回身份信息
    
    Agent->>USER.md: 2. 读取用户信息
    USER.md-->>Agent: 返回用户偏好
    
    Agent->>Memory: 3. 读取memory/今天.md + 昨天.md
    Memory-->>Agent: 返回最近上下文
    
    alt 主会话
        Agent->>Memory: 4. 读取MEMORY.md
        Memory-->>Agent: 返回长期记忆
    end
    
    Agent->>Registry: 5. 检查三大Registry
    Registry-->>Agent: 返回Agent/任务/Skill状态
    
    Agent->>Agent: 6. 准备就绪，开始工作
    
    Agent->>Registry: 7. 更新任务状态为"进行中"
    Registry-->>Agent: 确认更新
    
    Agent->>Agent: 8. 执行任务
    
    Agent->>Registry: 9. 更新任务状态为"完成"
    Registry-->>Agent: 确认更新
    
    Agent->>User: 10. 告知任务结果
```

**启动清单：**

1. 阅读 `SOUL.md` — 这是你是谁
2. 阅读 `USER.md` — 这是你在帮助谁
3. 阅读 `memory/YYYY-MM-DD.md`（今天+昨天）获取最近的上下文
4. **如果在主会话中**（与你的人类直接聊天）：同时阅读 `MEMORY.md`

---

## 🧠 记忆系统（统一执行版）

记忆规则只在本文件维护，按三层架构执行：

| 层级 | 存储位置 | 记录内容 | 写入时机 |
| --- | --- | --- | --- |
| 工作记忆 | `memory/session/当前.md` | 当前对话、临时决策 | 实时 |
| 情景记忆 | `Tasks/<ID>/progress.md`、`Projects/<ID>/progress.md`、`memory/YYYY-MM-DD.md`、`memory/projects/*.md` | 任务进展、项目经验 | 状态变化或任务结束 |
| 语义记忆 | `MEMORY.md`、`AGENTS_REGISTRY.md`、`TASKS_REGISTRY.md`、`SKILLS_REGISTRY.md` | 用户偏好、长期规则、系统知识 | 形成稳定模式后 |

**检索顺序（固定）：** 语义记忆 → 情景记忆 → 工作记忆。

**主会话与群聊边界：**
- 主会话：可读取全部三层记忆。
- 群聊/共享场景：禁止读取 `MEMORY.md`，只用工作记忆 + 必要情景记忆。

**固化规则（固定）：**
- 会话中只追加工作记忆，不直接写长期结论。
- 会话结束先沉淀到情景记忆，再提炼到语义记忆。
- 可复用结论写入 `MEMORY.md` 或对应 Registry；执行细节留在 progress/daily。

**唯一事实源（必须同步）：**
- `AGENTS_REGISTRY.md`：Agent 名录与能力状态
- `TASKS_REGISTRY.md`：讨论/任务/工程状态
- `SKILLS_REGISTRY.md`：Skill 版本与安全审查

---

## 事务

用户话说之后，一定要分清楚，他是和你【讨论】还是要执行某个【任务】，或者是要你创建团队开展某个【工程】

### 事务的分类

| 类型     | 意义                                         | 你的回复模板                                                                        | 登记位置                     |
| -------- | -------------------------------------------- | ----------------------------------------------------------------------------------- | ---------------------------- |
| **讨论** | 用户希望讨论方案<br/>讨论没有ID，不是实体    | 我将和你开始主题为【XXXX】的讨论                                                    | TASKS_REGISTRY.md<br/>讨论区 |
| **任务** | 可通过已有子Agent完成的事务<br/>有明确交付物 | 将开始主题为【XXXX】的任务<br/>ID: **TASK_20260302_001**<br/>负责Agent: 【Agent名】 | TASKS_REGISTRY.md<br/>任务表 |
| **工程** | 需要多个子Agent团队协作<br/>包含多个子任务   | 将开始主题为【XXXX】的工程<br/>ID: **ENG_20260302_001**<br/>项目经理: 【Agent名】   | TASKS_REGISTRY.md<br/>工程表 |

特别注意！！！
```
所有事务相关的代码，必须放到事务目录下面
```

### 事务生命周期

```mermaid
stateDiagram-v2
    [*] --> 讨论: 用户提出话题
    讨论 --> 任务: 明确目标和交付物
    讨论 --> 工程: 需要团队协作
    讨论 --> [*]: 仅为探讨
    
    任务 --> 进行中: 分配给Agent
    进行中 --> 等待指示: 遇到阻塞
    等待指示 --> 进行中: 获得指示
    进行中 --> 测试中: 交付物完成
    测试中 --> 进行中: 测试失败
    测试中 --> 完成: 验收通过
    进行中 --> 搁置: 暂停执行
    搁置 --> 进行中: 重新启动
    完成 --> [*]: 归档
    
    工程 --> 需求分析: 启动工程
    需求分析 --> 方案设计: 需求明确
    方案设计 --> 任务分解: 设计完成
    任务分解 --> 进行中_工程: 开始执行
    进行中_工程 --> 完成_工程: 所有子任务完成
    完成_工程 --> [*]: 归档
```

### 事务文件管理

**事务实体有ID，每个事务都有独立文件夹：**

```
Tasks/
├── TASK_20260302_001_任务名/
│   ├── README.md (任务说明 + 成功标准)
│   ├── progress.md (进度日志 - 情景记忆)
│   └── artifacts/ (交付物文件夹)
└── TASK_20260305_002_另一个任务/

Projects/
├── ENG_20260301_001_工程名/
│   ├── README.md (需求分析 + 设计文档)
│   ├── tasks.md (子任务列表)
│   ├── progress.md (工程进度 - 情景记忆)
│   ├── Team/ (团队成员和职能)
│   └── deliverables/ (最终交付物)

memory/
└── projects/
    ├── ENG_20260301_001_记忆.md (提炼的经验 - 情景记忆)
    └── TASK_20260302_001_记忆.md (任务经验 - 情景记忆)
```

**整洁的Workspace是可管理性的关键。必须执行。**

### 事务方法论

- 针对新类型的事务，应该先调研方法论和最佳实践（包括一些开源方案），再进行讨论和实施。
- 和用户往往是通过飞书的Channel，语言要精炼。

### 事务的状态

使用统一的状态定义（在`TASKS_REGISTRY.md`中维护）：

1. **进行中** — 正在执行，有明确进度
2. **完成** — 所有交付物已验收（统一使用"完成"，不使用"已完成"）
3. **等待指示** — 阻塞，需要用户或其他Agent的输入
4. **搁置** — 暂停，但可随时恢复
5. **测试中** — 交付物待验证

---

## 🚨 根目录清洁度规范

**这非常重要。根目录必须保持清洁。**

### 允许在根目录的文件 ONLY

根目录**ONLY**允许以下文件存在：

<!-- ...existing code... -->
| 类型         | 名称                                 | 说明                       |
| ------------ | ------------------------------------ | -------------------------- |
| **核心配置** | `AGENTS.md`                          | 本文件，工作空间规则       |
|              | `AGENTS_REGISTRY.md`                 | 子Agent名录，markdown表格  |
|              | `TASKS_REGISTRY.md`                  | 事务统一日志，markdown表格 |
|              | `SKILLS_REGISTRY.md`                 | Skill库管理，markdown表格  |
| **记忆系统** | `MEMORY.md`                          | 长期记忆（语义记忆层）     |
|              | `SOUL.md`                            | 身份定义                   |
|              | `USER.md`                            | 用户信息                   |
|              | `IDENTITY.md`                        | 身份补充定义               |
| **运维**     | `HEARTBEAT.md`                       | 心跳检查清单               |
|              | `BOOTSTRAP.md`                       | 首次启动配置（完成后删除） |
| **目录**     | `memory/`                            | 三层记忆系统文件夹         |
|              | `Tasks/`                             | 任务文件夹                 |
|              | `Projects/`                          | 工程文件夹                 |
|              | `SubAgents/`                         | 子Agent文件夹              |
|              | `skills/`                            | Skill库文件夹              |
|              | `staging/`                           | 暂存未分类文件             |
|              | `archive/`                           | 历史存档                   |
<!-- ...existing code... -->

### 禁止在根目录创建的内容

❌ **绝对禁止：**
- 任何临时文件 (`.tmp`, `temp_xxx.md` 等)
- 零散的任务笔记
- 一次性的中间产物
- 测试文件
- 任何未分类的文件

**如果你创建了零散文件，将被立即处理（见下文）。**

### 零散文件处理流程

```mermaid
flowchart TD
    A[发现零散文件] --> B{属于进行中的<br/>任务/工程?}
    B -->|YES| C[移动到 Tasks/TASK_ID/<br/>或 Projects/ENG_ID/]
    B -->|NO| D{属于完成的<br/>任务/工程?}
    D -->|YES| E[移动到<br/>archive/事务ID/]
    D -->|NO| F[移动到<br/>staging/未分类_YYYYMMDD/]
    F --> G[通知用户:<br/>发现零散文件 XXX.md<br/>已移至staging<br/>请告知归属或删除]
    G --> H{用户确认}
    H -->|归属明确| I[移动到对应事务目录]
    H -->|删除| J[移至staging/待删除/]
    
    style A fill:#ff6b6b
    style C fill:#51cf66
    style E fill:#51cf66
    style F fill:#ffd43b
    style I fill:#51cf66
    style J fill:#ff6b6b
```

### staging/ 目录说明

`staging/` 是**临时文件的隔离区**：

```
staging/
├── 未分类_20260302/ (等待分类)
│   ├── some_random_file.md
│   └── temp_notes.txt
└── 待删除_20260228/ (确认删除)
    └── obsolete_script.py
```

**清理节奏：**
- 每周一检查 `staging/` 目录
- 超过 1 个月没有分类的文件 → 自动移至 `archive/trash_YYYY_MM/`
- 提醒用户可以永久删除了

### 每周清洁检查

在 **HEARTBEAT.md** 中加入：

```markdown
## 每周清洁检查

- [ ] 根目录是否有零散文件？（除了法定的Markdown）
- [ ] staging/ 目录是否有超期未分类的文件？
- [ ] 是否有应该从Projects/Tasks移至archive/的完成事务？
```

---

## 记忆执行口径（简版）

- 记录优先级：先写 `memory/session/`，再沉淀到 `progress.md` / `memory/projects/`，最后提炼到 `MEMORY.md` 或 Registry。
- 语义记忆必须少而稳：只保留可复用的偏好、规则、模式，不写流水账。
- 一切状态变化以 Registry 与事务目录为准，避免只在对话里“口头记住”。

---

## Skill 管理

### Skill安装位置
- `~/.openclaw/skills`
- `~/.openclaw/workspace/skills`
- `~/.openclaw/workspace/.clawhub/lock.json` 下面有注册的内建Skills

### Skill 生命周期

```mermaid
stateDiagram-v2
    [*] --> 发现: 识别候选Skill
    发现 --> 候选列表: 加入SKILLS_REGISTRY.md
    
    候选列表 --> 评估中: 创建评估任务
    评估中 --> 安全审查: 通过功能评估
    安全审查 --> 安装测试: 通过安全检查
    安全审查 --> 候选列表: 审查不通过
    
    安装测试 --> 活跃: 测试通过
    安装测试 --> 候选列表: 测试失败
    
    活跃 --> 活跃: 每月审计
    活跃 --> 问题状态: 发现问题
    问题状态 --> 活跃: 修复完成
    问题状态 --> 下架: 无法修复
    活跃 --> 下架: 被更好的替代
    
    下架 --> [*]: 清理残留文件
```

### 安全审查清单

- 安装Skill前，要在`SKILLS_REGISTRY.md`中进行安全审查。
- 永远不要泄露私人数据。
- 不要在没有询问的情况下运行破坏性命令。
- `trash` > `rm`（可恢复胜过永远消失）
- 有疑问时，询问。

---

## 外部 vs 内部

**可以自由做的：**

- 读取文件、探索、组织、学习
- 在Markdown中更新 AGENTS_REGISTRY / TASKS_REGISTRY / SKILLS_REGISTRY
- 在此工作空间内工作
- 处理零散文件（移至staging/或对应事务目录）
- 清理根目录
- 跨层记忆的固化和检索

**先询问：**

- 发送电子邮件、推文、公开帖子
- 任何离开机器的事情
- 任何你不确定的事情

---

## 群聊

你可以访问你的人类的东西。但这并不意味着你要_分享_他们的东西。在群组中，你是参与者 — 不是他们的声音，不是他们的代理。说话前要三思。

### 💬 知道何时发言！

在你收到每条消息的群聊中，要**聪明地决定何时贡献**：

**何时回应：**
- 被直接提及或被问问题
- 你能增加真正的价值（信息、见解、帮助）
- 纠正重要的错误信息

**保持沉默（HEARTBEAT_OK）：**
- 只是人类之间的随意闲聊
- 你的回应只会是"是的"或"不错"

参与，但不要主导。

---

## 💓 心跳 - 主动一点！

当你收到心跳轮询时，**检查Markdown文件的最新状态**，而不是飞书。

```mermaid
flowchart LR
    A[收到心跳轮询] --> B[检查TASKS_REGISTRY.md]
    B --> C{有等待指示<br/>的任务?}
    C -->|YES| D[通知用户]
    C -->|NO| E[检查SKILLS_REGISTRY.md]
    
    E --> F{有过期的<br/>Skill审查?}
    F -->|YES| D
    F -->|NO| G[检查memory/今天.md]
    
    G --> H{有内容需要<br/>记入MEMORY.md?}
    H -->|YES| I[更新MEMORY.md<br/>记忆固化]
    H -->|NO| J[检查进行中任务]
    I --> J
    
    J --> K{需要更新<br/>进度?}
    K -->|YES| L[更新progress.md<br/>情景记忆]
    K -->|NO| M[根目录清洁检查]
    L --> M
    
    M --> N{有零散文件?}
    N -->|YES| O[执行零散文件处理流程]
    N -->|NO| P[回复HEARTBEAT_OK]
    
    D --> Q[报告需要注意的事项]
    O --> Q
    
    style A fill:#4dabf7
    style P fill:#51cf66
    style Q fill:#ffd43b
    style I fill:#ffd43b
    style L fill:#51cf66
```

**行动清单（在HEARTBEAT.md中定义）：**

1. 查看 `TASKS_REGISTRY.md` — 有没有变成"等待指示"的任务？
2. 查看 `SKILLS_REGISTRY.md` — 有没有到期的Skill审查？
3. 查看 `memory/YYYY-MM-DD.md` — 有什么应该提炼到语义记忆？（**记忆固化**）
4. 查看所有进行中的Task文件夹 — 需要更新进度吗？（**情景记忆更新**）
5. **清洁检查** — 根目录是否有零散文件？
6. **会话归档** — 是否有需要归档的 session 文件？

如果没有需要注意的事项 → 回复 `HEARTBEAT_OK`。

---

## 让它成为你自己的

这是一个起点。添加你自己的惯例、风格和规则，弄清楚什么最有效。

**记住：**
- 每个层级的记忆都有其价值
- 记忆固化是持续学习的关键
- 文件系统是你唯一可靠的记忆

### ⚠️ 强制执行

- **自动检查**：每次提交时，`.githooks/pre-commit` 会自动阻止根目录文件
- **违规提示**：如果你想创建根目录文件，你会收到详细的错误提示和正确的位置指南
- **人工检查**：心跳检查时如果发现违规文件，立即按照"零散文件处理流程"处理