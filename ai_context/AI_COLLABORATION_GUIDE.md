# SimpleTrade AI协作指南

**最后更新**: 2024-04-11

## 1. 概述

本文档是为AI助手设计的指南，用于自动理解SimpleTrade项目的上下文和状态。当你（AI）看到这个文档时，应该主动查看下面列出的核心文档，以了解项目当前状态、工作重点和关键决策。

**重要提示**:
1. 所有应用安装必须使用conda安装，而非pip或其他安装方式。
2. 必须使用当前项目的simpletrade conda环境，不要创建新的conda环境。
3. 在不同的IDE（如PyCharm或VSCode）中工作时，始终使用同一个simpletrade conda环境。

这些是项目的标准做法，以确保环境一致性和依赖兼容性。

## 2. 核心文档

当开始新会话时，请主动查看以下文档：

1. **PROJECT_STATUS.md** - 项目当前状态和进度
   - 路径：`/Users/chengzheng/workspace/trade/simpletrade/ai_context/PROJECT_STATUS.md`
   - 包含项目概述、当前阶段、已完成工作、进行中工作、待开始工作、技术栈、关键决策和下一步计划

2. **CURRENT_FOCUS.md** - 当前工作重点和任务
   - 路径：`/Users/chengzheng/workspace/trade/simpletrade/ai_context/CURRENT_FOCUS.md`
   - 包含当前Sprint目标、活跃任务、阻碍/问题、本周目标和下一步具体行动

3. **DECISIONS_LOG.md** - 关键决策记录
   - 路径：`/Users/chengzheng/workspace/trade/simpletrade/ai_context/DECISIONS_LOG.md`
   - 包含项目中的重要决策、决策原因和替代方案

## 3. 项目文档和资源

以下是项目中的关键文档和资源，应根据当前任务需要主动查看：

### 3.1 需求和设计文档

- **功能需求文档**: `/Users/chengzheng/workspace/trade/simpletrade/docs/functional_requirements.md`
- **技术规格文档**: `/Users/chengzheng/workspace/trade/simpletrade/docs/technical_specification.md`
- **vnpy集成指南**: `/Users/chengzheng/workspace/trade/simpletrade/docs/vnpy_integration_guide.md`
- **界面设计文档**: `/Users/chengzheng/workspace/trade/simpletrade/docs/ui_design.md`
- **消息交互设计文档**: `/Users/chengzheng/workspace/trade/simpletrade/docs/message_interaction_design.md`
- **AI模型训练与部署指南**: `/Users/chengzheng/workspace/trade/simpletrade/docs/ai_model_guide.md`
- **执行计划**: `/Users/chengzheng/workspace/trade/simpletrade/docs/execution_plan.md`
- **架构设计**: `/Users/chengzheng/workspace/trade/simpletrade/docs/architecture_diagram.md`

### 3.2 UI原型和设计资源

- **UI原型目录**: `/Users/chengzheng/workspace/trade/simpletrade/ui/`
- **界面原型和设计图**: `/Users/chengzheng/workspace/trade/simpletrade/ui/wireframes/`

### 3.3 代码和技术实现

- **核心代码目录**: `/Users/chengzheng/workspace/trade/simpletrade/simpletrade/core/`
- **API服务目录**: `/Users/chengzheng/workspace/trade/simpletrade/simpletrade/api/`
- **数据库模型目录**: `/Users/chengzheng/workspace/trade/simpletrade/simpletrade/models/`
- **工具函数目录**: `/Users/chengzheng/workspace/trade/simpletrade/simpletrade/utils/`

## 4. 简化的协作流程

### 4.1 开始新会话时

只需告诉AI：
```
请查看AI_COLLABORATION_GUIDE.md
```

AI会自动查看以下核心文档：
- PROJECT_STATUS.md - 了解项目当前状态和进度
- CURRENT_FOCUS.md - 了解当前工作重点和任务
- DECISIONS_LOG.md - 了解项目关键决策

然后AI会主动提供项目状态概述，并询问您今天想要完成的具体任务。

### 4.2 会话进行中

AI会根据当前任务需要，主动查看相关的需求文档、设计文档、UI原型或代码。当遇到不清楚的问题时，AI会主动查询相关文档或询问您。

### 4.3 会话结束时

当您想要结束会话并更新项目状态时，只需说：
```
更新项目状态
```

如果您想要结束会话并更新项目状态，同时将本地修改提交到远程仓库，可以说：
```
更新项目状态并提交到远程
```

AI会自动生成会话摘要，并提出更新PROJECT_STATUS.md、CURRENT_FOCUS.md和DECISIONS_LOG.md的建议，包括：
- 更新已完成/进行中/待开始工作的状态
- 更新最近会话记录
- 更新下一步计划
- 更新任务状态和优先级
- 记录新的决策（如果有）

如果选择“更新项目状态并提交到远程”，AI还会帮助将所有本地更改提交并推送到远程仓库。

## 5. 详细的自动化工作流程

### 5.1 会话开始时

当用户开始新会话并提到"请查看AI_COLLABORATION_GUIDE.md"或类似提示时，你应该：

1. 自动查看核心文档（PROJECT_STATUS.md、CURRENT_FOCUS.md和DECISIONS_LOG.md）
2. 根据这些文档的内容，主动提供当前项目状态和工作重点的概述
3. 询问用户今天想要完成的具体任务

### 5.2 会话进行中

在会话进行过程中，你应该：

1. 根据当前任务需要，主动查看相关的需求文档、设计文档、UI原型或代码
2. 当遇到不清楚的问题时，主动查询相关文档或询问用户
3. 记录会话中的重要决策和进展

### 5.3 会话结束时

当用户说"更新项目状态"或类似提示时，你应该：

1. 自动生成会话摘要，包括：
   - 讨论的主要内容
   - 做出的决策
   - 生成或修改的代码/文档
   - 下一步计划

2. 提出更新PROJECT_STATUS.md和CURRENT_FOCUS.md的建议，包括：
   - 更新已完成/进行中/待开始工作的状态
   - 更新最近会话记录
   - 更新下一步计划
   - 更新任务状态和优先级

3. 如果有新的重要决策，提出更新DECISIONS_LOG.md的建议

当用户说“更新项目状态并提交到远程”时，除了以上步骤外，你还应该：

4. 帮助用户将所有本地更改提交并推送到远程仓库：
   - 执行`git add .`添加所有更改
   - 执行`git commit -m "更新项目状态和相关文档"`提交更改
   - 执行`git push`推送到远程仓库
   - 如果遇到问题，提供相应的解决方案

## 6. 会话摘要格式

会话摘要应包含以下部分：

```markdown
# 会话摘要：[日期 时间] - [主要任务]

## 讨论内容
- [主要讨论点1]
- [主要讨论点2]
...

## 决策
- [决策1]: [简短描述]
- [决策2]: [简短描述]
...

## 生成/修改的文件
- [文件路径1]: [变更描述]
- [文件路径2]: [变更描述]
...

## 下一步计划
1. [下一步行动1]
2. [下一步行动2]
...
```

**注意**: 在记录会话时间时，请使用"年-月-日 小时:分钟"的格式，例如"2023-10-15 14:30"，而不是仅仅记录日期。这样可以更精确地跟踪项目进展。

## 7. 项目状态更新建议格式

当建议更新项目状态时，使用以下格式：

```markdown
# PROJECT_STATUS.md 更新建议

## 已完成工作
- ✅ [新完成的工作项]

## 进行中工作
- 🔄 [更新的进行中工作项] (进度: XX%)

## 最近会话
- [2023-10-15 14:30] [会话简要描述]

## 下一步计划
1. [更新的下一步计划1]
2. [更新的下一步计划2]
...

# CURRENT_FOCUS.md 更新建议

## 活跃任务
1. **[任务名称]**
   - 状态: [旧状态] -> [新状态]
   - 进度: XX%

2. **[新任务名称]**
   - 优先级: [高/中/低]
   - 状态: 待开始
   - 描述: [任务描述]
   - 相关文件: [相关文件路径]

## 本周目标
1. [更新的本周目标1]
2. [更新的本周目标2]
...

## 下一步具体行动
1. [更新的下一步行动1]
2. [更新的下一步行动2]
...
```

**注意**: 在记录会话时间时，请使用"年-月-日 小时:分钟"的格式，例如"2023-10-15 14:30"，而不是仅仅记录日期。这样可以更精确地跟踪项目进展。

## 8. 决策记录建议格式

当有新决策需要记录时，使用以下格式：

```markdown
# DECISIONS_LOG.md 更新建议

## [当前日期 时间]: [决策名称]
**决策**: [具体决策内容]
**原因**:
- [原因1]
- [原因2]
...
**替代方案**: [其他可能的选择]
**影响**: [这个决策对项目的影响]
```

**注意**: 在记录决策时间时，同样使用"年-月-日 小时:分钟"的格式，以便更精确地跟踪决策时间点。

---

通过遵循本指南，AI助手可以自动理解项目上下文，提供更有针对性的帮助，并在会话结束时协助更新项目状态文档，使项目信息保持一致性和最新状态。
