# SimpleTrade AI协作指南

**最后更新**: 2024-04-17

## 1. 概述

本文档是为AI助手设计的指南，用于自动理解SimpleTrade项目的上下文和状态。当你（AI）看到这个文档时，应该主动查看下面列出的核心文档，以了解项目当前状态、工作重点和关键决策。

**重要提示**:
1. 所有应用安装必须使用conda安装，而非pip或其他安装方式。
2. 必须使用当前项目的simpletrade conda环境，不要创建新的conda环境。
3. 在不同的IDE（如PyCharm或VSCode）中工作时，始终使用同一个simpletrade conda环境。
4. **代码整洁**: 作为一个新项目，请在开发过程中协助保持代码库的整洁。及时识别并提议移除不再使用、废弃或重复的代码文件及代码片段，以避免混淆。
5. **合理设计优先**: 在思考和设计解决方案时，请始终以合理性、简洁性和可维护性为标准。不要受限于当前代码的实现方式（即使是 AI 生成的）。如果发现现有实现存在不合理之处，请大胆提出并实施改进方案。
6. **直面问题而非规避**: 遇到问题时，应该直接解决问题而不是尝试绕过它。只有在解决问题的方案明显不如规避方案优雅时，才考虑规避。优雅的系统建立在解决问题而非掩盖问题的基础上。
7. **文档维护**: 项目状态、任务进展和决策记录应该只在 `ai_context` 目录下的文件中维护，避免在多个地方重复记录相同的信息。主要的文档文件包括 CURRENT_STATUS.md、CONVERSATION_HISTORY.md 和 DECISIONS_LOG.md。

这些是项目的标准做法，以确保环境一致性、依赖兼容性和代码库的可维护性。

## 2. 核心文档

当开始新会话时，请主动查看以下文档：

1. **CURRENT_STATUS.md** - 项目当前状态和进度
   - 路径：`/Users/chengzheng/workspace/trade/simpletrade/ai_context/CURRENT_STATUS.md`
   - 包含项目概述、当前阶段、技术栈、已完成工作、进行中工作、待开始工作、遇到的问题和下一步计划

2. **CONVERSATION_HISTORY.md** - 最近对话的摘要
   - 路径：`/Users/chengzheng/workspace/trade/simpletrade/ai_context/CONVERSATION_HISTORY.md`
   - 包含最近对话的讨论内容、决策、行动项和下一步计划

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
请查看 ai_context/AI_COLLABORATION_GUIDE.md
```

AI会自动查看以下核心文档：
- CURRENT_STATUS.md - 了解项目当前状态和进度
- CONVERSATION_HISTORY.md - 了解最近对话的内容和决策
- DECISIONS_LOG.md - 了解项目关键决策

然后AI会主动提供项目状态概述，并询问您今天想要完成的具体任务。

### 4.2 会话进行中

AI会根据当前任务需要，主动查看相关的需求文档、设计文档、UI原型或代码。当遇到不清楚的问题时，AI会主动查询相关文档或询问您。

### 4.3 用户命令和AI响应

以下是您可以使用的命令和AI应该如何响应：

| 命令 | AI响应 |
|-------|--------|
| `更新项目状态` | AI会生成会话摘要，并更新CURRENT_STATUS.md和CONVERSATION_HISTORY.md文件，包括记录未完成的工作和遇到的问题 |
| `更新项目状态并提交到远程` | 除了更新项目状态外，还会将本地修改提交到远程仓库 |
| `查看项目状态` | AI会查看CURRENT_STATUS.md文件并提供项目状态概述 |
| `查看对话历史` | AI会查看CONVERSATION_HISTORY.md文件并提供最近对话的摘要 |
| `查看决策日志` | AI会查看DECISIONS_LOG.md文件并提供决策日志概述 |
| `记录决策` | AI会将新的决策添加到DECISIONS_LOG.md文件中 |

### 4.4 会话结束时

当您想要结束会话并更新项目状态时，只需说：
```
更新项目状态
```

如果您想要结束会话并更新项目状态，同时将本地修改提交到远程仓库，可以说：
```
更新项目状态并提交到远程
```

AI会自动生成会话摘要，并提出更新CURRENT_STATUS.md和CONVERSATION_HISTORY.md的建议，包括：
- 更新已完成/进行中/待开始工作的状态
- 记录未完成的工作和遇到的问题，如未解决的Bug和未成功运行的程序
- 更新最近更新记录
- 更新下一步计划
- 在CONVERSATION_HISTORY.md中添加新的对话摘要

如果有新的重要决策，AI会将其添加到DECISIONS_LOG.md文件中

如果选择"更新项目状态并提交到远程"，AI还会帮助将所有本地更改提交并推送到远程仓库。

## 5. 详细的自动化工作流程

### 5.1 会话开始时

当用户开始新会话并提到"请查看AI_COLLABORATION_GUIDE.md"或类似提示时，你应该：

1. 自动查看核心文档（CURRENT_STATUS.md、CONVERSATION_HISTORY.md和DECISIONS_LOG.md）
2. 根据这些文档的内容，主动提供当前项目状态和最近进展的概述
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
   - 遇到的问题和未解决的问题
   - 下一步计划

2. 提出更新CURRENT_STATUS.md的建议，包括：
   - 更新已完成/进行中/待开始工作的状态
   - 更新遇到的问题和解决方案
   - 更新最近更新记录
   - 更新下一步计划

3. 在CONVERSATION_HISTORY.md中添加新的对话摘要，包括讨论内容、决策、行动项和下一步计划

4. 如果有新的重要决策，将其添加到DECISIONS_LOG.md文件中

当用户说"更新项目状态并提交到远程"时，除了以上步骤外，你还应该：

5. 帮助用户将所有本地更改提交并推送到远程仓库：
   - 执行`git add .`添加所有更改
   - 执行`git commit -m "更新项目状态和相关文档"`提交更改
   - 执行`git push`推送到远程仓库
   - 如果遇到问题，提供相应的解决方案

## 6. 会话摘要格式

会话摘要应包含以下部分：

```markdown
## [日期 时间] - [主要任务]

### 讨论内容
- [主要讨论点1]
- [主要讨论点2]
...

### 决策
- [决策1]: [简短描述]
- [决策2]: [简短描述]
...

### 行动项
- [行动项描述1]
- [行动项描述2]
...

### 下一步
- [下一步行动1]
- [下一步行动2]
...
```

**注意**: 在记录会话时间时，请使用"年-月-日 小时:分钟"的格式，例如"2023-10-15 14:30"，而不是仅仅记录日期。这样可以更精确地跟踪项目进展。

## 7. 项目状态更新建议格式

当建议更新项目状态时，使用以下格式：

```markdown
# CURRENT_STATUS.md 更新建议

## 已完成工作
- ✅ [新完成的工作项]

## 进行中工作
- 🔄 [更新的进行中工作项] (进度: XX%)

## 遇到的问题

### [问题类型1]
- **问题描述**: [详细描述]
- **解决方案**: [已尝试的解决方案]
- **状态**: [当前状态]

## 最近更新
- [2024-04-17 16:30] [更新简要描述]

## 下一步计划
1. [更新的下一步计划1]
2. [更新的下一步计划2]
...

# CONVERSATION_HISTORY.md 更新建议

## [2024-04-17 16:30] - [主要任务]

### 讨论内容
- [主要讨论点1]
- [主要讨论点2]
...

### 决策
- [决策1]: [简短描述]
- [决策2]: [简短描述]
...

### 行动项
- [行动项描述1]
- [行动项描述2]
...

### 下一步
- [下一步行动1]
- [下一步行动2]
...
```

**注意**: 在记录会话时间时，请使用"年-月-日 小时:分钟"的格式，例如"2023-10-15 14:30"，而不是仅仅记录日期。这样可以更精确地跟踪项目进展。

## 8. 决策记录建议格式

当有新决策需要记录时，使用以下格式：

```markdown
# DECISIONS_LOG.md 更新建议

## [2024-04-17 16:30]: [决策名称]
**决策**: [具体决策内容]
**原因**:
- [原因1]
- [原因2]
...
**替代方案**: [其他可能的选择]
**影响**: [这个决策对项目的影响]
**未解决的问题**:
- [问题描述1]
- [问题描述2]
```

**注意**: 在记录决策时间时，同样使用"年-月-日 小时:分钟"的格式，以便更精确地跟踪决策时间点。

---

通过遵循本指南，AI助手可以自动理解项目上下文，提供更有针对性的帮助，并在会话结束时协助更新项目状态文档，使项目信息保持一致性和最新状态。