# AI_CONTEXT目录说明

**最后更新**: 2024-04-17

## 目录用途

AI_CONTEXT目录是SimpleTrade项目的AI协作管理中心，用于存储与AI助手协作相关的所有上下文文件。这个目录的设计目的是减少重复说明上下文的需求，保持项目信息的一致性，并提高AI协作的质量和效率。

## 目录结构

```
ai_context/
├── CURRENT_STATUS.md        # 项目当前状态和进度
├── CONVERSATION_HISTORY.md  # 最近对话的摘要
├── DECISIONS_LOG.md         # 关键决策记录
├── AI_COLLABORATION_GUIDE.md  # AI协作指南
├── README.md               # 本文件
├── REFERENCE/              # 参考资料目录
│   ├── README.md           # 参考资料说明
│   ├── VNPY_KEY_COMPONENTS.md
│   ├── TECHNICAL_INDICATORS.md
│   ├── API_OVERVIEW.md
│   └── ...
└── archive/                # 归档目录
    ├── PROJECT_STATUS.md      # 已归档
    ├── CURRENT_FOCUS.md       # 已归档
    └── SESSION_SUMMARIES/     # 已归档
```

## 核心文件说明

### CURRENT_STATUS.md

**用途**: 提供项目的整体状态和进度概览。

**内容**:
- 项目概述
- 当前阶段
- 技术栈
- 已完成工作
- 进行中工作
- 待开始工作
- 遇到的问题
- 下一步计划
- 最近更新

**更新频率**: 每次会话后

### CONVERSATION_HISTORY.md

**用途**: 记录最近与AI助手对话的摘要。

**内容**:
- 对话日期和主题
- 讨论内容
- 决策
- 行动项
- 下一步计划

**更新频率**: 每次会话后

### DECISIONS_LOG.md

**用途**: 记录所有重要的项目决策。

**内容**:
- 决策日期和名称
- 决策内容
- 决策原因
- 替代方案
- 影响

**更新频率**: 做出新决策时

### AI_COLLABORATION_GUIDE.md

**用途**: 提供AI协作的详细指南。

**内容**:
- 协作流程
- 文件维护指南
- 最佳实践
- 故障排除
- 示例

**更新频率**: 协作方式变化时

## 子目录说明

### SESSION_SUMMARIES/

**用途**: 存储每次与AI助手会话的摘要记录。

**内容**:
- 会话主题
- 主要讨论内容
- 关键决策
- 生成的代码/文档
- 下一步计划

**更新频率**: 每次会话后添加新文件

### REFERENCE/

**用途**: 存储不常变动但重要的技术参考资料。

**内容**:
- 技术规范
- API文档
- 算法说明
- 架构图表

**更新频率**: 低，仅在核心技术变化时更新

## 使用方法

### 开始新会话

只需告诉AI：

```
请查看 ai_context/AI_COLLABORATION_GUIDE.md
```

AI会自动查看以下核心文档：
- CURRENT_STATUS.md - 了解项目当前状态和进度
- CONVERSATION_HISTORY.md - 了解最近对话的内容和决策
- DECISIONS_LOG.md - 了解项目关键决策

然后AI会主动提供项目状态概述，并询问您今天想要完成的具体任务。

### 会话进行中

可以使用以下命令：

| 命令 | 说明 |
|-------|--------|
| `查看项目状态` | 查看CURRENT_STATUS.md文件并提供项目状态概述 |
| `查看对话历史` | 查看CONVERSATION_HISTORY.md文件并提供最近对话的摘要 |
| `查看决策日志` | 查看DECISIONS_LOG.md文件并提供决策日志概述 |
| `记录决策` | 将新的决策添加到DECISIONS_LOG.md文件中 |

### 结束会话

当想要结束会话并更新项目状态时，只需说：

```
更新项目状态
```

AI会自动生成会话摘要，并更新：
1. CURRENT_STATUS.md - 更新项目状态、进度和下一步计划
2. CONVERSATION_HISTORY.md - 添加新的对话摘要
3. 如有新的重要决策，更新DECISIONS_LOG.md

## 维护指南

1. **保持文件更新**:
   - 每次会话后使用“更新项目状态”命令自动更新相关文件
   - 不要积累未记录的变更

2. **定期整理**:
   - 定期审查CURRENT_STATUS.md，移除不再相关的信息
   - 当CONVERSATION_HISTORY.md变得过长时，将旧的对话摘要移动到archive目录

3. **版本控制**:
   - 将ai_context目录纳入版本控制
   - 这样可以追踪项目状态的变化历史

4. **定期回顾**:
   - 每周回顾项目进度和AI协作效果
   - 根据需要调整协作流程和文件结构

通过这个简化的AI上下文管理框架，可以显著提高与AI助手的协作效率，减少重复工作，保持项目信息的一致性，并建立完整的项目知识库。详细的使用指南请参考`AI_COLLABORATION_GUIDE.md`文件。
