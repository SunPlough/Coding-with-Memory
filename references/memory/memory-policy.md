# Memory 策略

Memory 是有证据、可撤销的未来工作建议，不是第二套代码标准。

## 优先级与隔离

```text
安全与合规 > 项目/团队规范 > 已批准决策 > 已批准用户偏好 > 候选 Memory
```

将 `preferences.jsonl` 与工程决策、模式和事故分别保存。偏好只能影响：

- `communication_language`：与用户沟通的语言；
- `planning_granularity`：计划的展开程度；
- `tool_preference`：同等可行工具之间的选择；
- `interaction_pace`：汇报与确认节奏；
- `report_format`：最终报告格式。

偏好不得改变代码规范、注释语言、安全要求、架构边界、测试范围或质量门禁。源码注释语言和文档格式属于项目事实，应从仓库规则和相邻代码检测，而不是从用户对话语言推断。

## 提取边界

从以下证据提出候选条目：

- 用户明确说出的偏好或纠正；
- 在多个任务中重复出现、且不存在反例的选择；
- 有明确适用条件的成功路径；
- 已定位根因和预防方式的失败；
- 当前信息、工具或 Agent 能力的边界。

只保存结论和最小证据引用，不保存整段对话、完整源文件、凭据、个人或客户数据。写入前脱敏、去重并限制作用域。

## 原子条目

候选 Memory 尽量表达为一个触发条件和一个动作，避免把多个偏好或工程规则捆成一条：

```text
trigger: 什么时候适用
action: Agent 应采取的低风险动作
domain: communication | planning | tool | delivery | pattern | incident
```

例如“用户要求最终报告先给结论”可以成为 `delivery` 域的偏好；“所有 API 都必须重试三次”不是偏好，应进入项目决策评审。原子字段帮助去重、回放和停用，但不改变 Memory 的批准边界。

## 生命周期

```text
trace -> classify -> redact/deduplicate -> candidate
candidate -> approved | rejected | deprecated
approved -> deprecated
```

- 自动提取只能创建 `candidate`。
- 用户偏好必须由 `human` 明确批准。
- 工程模式可以在可重复回放后由 `replay` 批准；失败回放形成反例，不覆盖原证据。
- `rejected` 和 `deprecated` 保留历史，不物理删除。
- 默认检索只返回 `approved`，并按当前任务、路径、语言和作用域过滤。
- `review_after` 到期后先复核，不自动续期或自动废弃。

强制标准的变化只能形成带来源、影响、验证和回滚方案的建议，进入项目版本化评审，不能由 Memory 自动晋级。
