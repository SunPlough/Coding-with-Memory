---
name: coding-with-memory
description: Plan, implement, debug, review, and verify repository changes with layered Google-based language standards, Chinese comment rules, complexity guardrails, deterministic quality gates, auditable preference memory, and validation-gated skill evolution. Use for feature development, bug fixes, refactoring, code review, repository standardization, or improving an agent-led coding workflow.
---

# Coding with Memory

使用本 Skill 完成 Agent 主导的软件开发任务。始终以仓库事实为依据，以最小可验证变更为默认方案。

## 0. 选择工作流

先阅读[任务意图路由](references/intent-routing.md)，判断当前主要意图，再按需加载规范、调试、增量实现或交付参考。路由只决定流程，不改变规范优先级。

## 不可覆盖的优先级

```text
安全与合规
> 仓库/团队规则
> 已批准架构决策
> 框架与语言格式
> 注释语义与通用工程基线
> 已批准用户协作偏好
> 候选 Memory
```

用户偏好只能影响沟通语言、计划粒度、工具选择、交互节奏和报告格式。不得用偏好降低测试、安全、架构、注释或质量要求。

## 1. 建立上下文

先读取仓库中的 `AGENTS.md`、`CONTRIBUTING*`、`STYLE*`、项目配置和相关目录代码。运行：

```bash
python <skill-dir>/scripts/collect_context.py --repo <repo> --format markdown
```

只收集目录、语言、清单文件、规则文件、Git 状态和可用检查命令；不得在此阶段修改仓库。

然后按路径加载：

1. [规范索引](references/coding-standards/index.md)、[严格执行协议](references/coding-standards/strict.md) 与 [通用工程基线](references/coding-standards/base.md)。
2. `references/coding-standards/languages/` 中当前文件对应的语言规范；再读取 `references/coding-standards/upstream/google-styleguide/` 中固定版本的官方全文。不得只依据摘要执行；逐章节记录 MUST/MUST NOT/SHOULD/MAY/AVOID 的状态，SHOULD 例外必须有证据。
3. [中文注释规范](references/coding-standards/comments/index.md)，修改源码时必读。
4. 仓库实际使用的框架规范；没有对应文件时遵循官方文档与仓库事实，不自行发明规则。Google 主仓库没有覆盖的语言必须标记 `external-source` 或 `no-google-guide`。
5. [架构边界](references/architecture/boundaries.md)、[安全清单](references/security/checklist.md) 和项目覆盖规则。
6. 从项目 `.coding-memory/` 中只检索与任务相关且已批准的 Memory。

不要一次加载所有语言或无关框架文件；但对当前语言不能跳过官方全文快照。全文较长时按 `strict.md` 的章节映射分段检索并保留证据。

加载规范前先校验固定快照：

```bash
python <skill-dir>/scripts/verify_upstream.py --skill <skill-dir>
```

校验失败时不得声称已按 Google 固定版本执行；交付报告中记录 `failed` 及具体文件。

## 2. 给任务分级

- **S：微小修改**：单点、低风险、无公共接口变化。可用一段话说明目标后直接执行。
- **M：普通开发**：跨多个文件、有行为变化或需要新增测试。先给出目标、非目标、步骤、风险和验收标准。
- **L：高风险修改**：公共 API、数据迁移、权限、安全、依赖主版本、架构边界或生产操作。必须先展示方案与回滚路径；需要新授权的动作必须等待用户确认。

任务等级不能用来跳过适用的验证。

开始实现前，明确写出假设、不确定点和取舍。若存在会实质改变结果的多种解释，先停下并请求确认；不要把沉默猜测写进代码。

## 3. 计划与实现

计划必须说明：

- 要解决的真实问题和可观察验收结果；
- 修改范围与明确非目标；
- 受影响的接口、数据、依赖和测试；
- 风险、假设、人工确认点和回滚方式。
- 可观察的 Definition of Done；完成编码不等于满足交付门禁。

实现时：

- 优先复用仓库已有模式，保持补丁小而完整。
- 不为未出现的需求增加分支、配置、抽象层、基类、插件点或兼容路径。
- 不顺手重构无关模块；功能修改和大规模整理分开。
- 复杂控制流先考虑早返回、命名和拆分，但不要为了指标机械切碎函数。
- 对外部输入、I/O、并发、持久化、权限和第三方 API 显式处理失败。
- 注释只记录代码无法稳定表达的契约、约束和原因；遵循仓库既有注释语言。
- 不臆测 API、文件、命令、规范来源、事项编号或测试结果。
- 多文件任务按小的垂直切片实现；每个切片完成后运行定向验证，再进入下一切片。

详细行为见 [Agent 工作流](references/ai-workflow.md)。

## 4. 反过度工程门禁

新增下列内容前，必须指出当前调用方、当前验收需求或已批准决策：

- 新抽象、接口、基类或通用工具；
- 新分支、开关、配置项、重试或回退路径；
- 新依赖、缓存、队列、并发或分布式机制；
- 为“以后可能需要”保留的兼容层。

没有现实证据时删除该设计。安全边界、协议兼容和已确认迁移窗口可以例外，但必须记录理由和测试。

### 反自我说服清单

| 可能的借口 | 正确动作 |
|---|---|
| “任务太小，不需要验证” | 选择最小的定向检查，并记录结果 |
| “我大概知道根因，先改再看” | 切换到调试路由，先复现并验证单一假设 |
| “顺手重构一下更干净” | 只保留与验收标准直接相关的行 |
| “评审意见应该都对” | 先核对仓库事实，再逐项采纳或提出技术异议 |
| “测试以后再补” | 行为变化先建立可失败的测试或探针 |

## 5. 验证

遇到 Bug、测试失败或异常行为时，先加载[系统化调试](references/debugging.md)，未定位根因前不提交修复。

进行代码评审或处理评审意见时，加载[代码评审](references/review.md)，按严重性输出发现，不以礼貌性总结替代技术判断。

先查看将运行的门禁：

```bash
python <skill-dir>/scripts/run_quality_gate.py --repo <repo> --list
```

确认后执行：

```bash
python <skill-dir>/scripts/run_quality_gate.py --repo <repo> --format markdown
```

门禁优先读取项目 `.planning-coding.json`；没有配置时只运行能从仓库清单中保守识别的命令。实际适用但未发现的检查必须在交付报告中说明。不得把“修改完成”表述为“验证通过”。

按[Definition of Done](references/definition-of-done.md)整理证据包，明确区分 `passed`、`failed`、`skipped` 和 `not-found`。

项目需要稳定门禁配置时，以 `assets/project-config/.planning-coding.json` 为起点，只加入仓库真实存在且使用检查模式的命令；不得照抄项目不支持的示例。

对新增或修改的注释，再运行：

```bash
python <skill-dir>/scripts/comment_audit.py --repo <repo> --format markdown
```

语义价值仍需 diff 审查，禁止采用注释率作为质量指标。

## 6. Memory 闭环

运行时 Memory 默认存放在项目根目录 `.coding-memory/`，不写入 Skill 安装目录。先初始化：

```bash
python <skill-dir>/scripts/memory_tool.py --repo <repo> init
```

任务开始只查询 `approved` 条目。任务结束自动检查用户明确反馈、重复选择、成功路径和失败原因；存在有效信号时记录轻量轨迹并调用 `memory_tool.py add` 创建候选，不必为“创建候选”单独打断用户。没有证据时不创建条目。候选未经批准不得在本次或后续任务中生效，必须在交付报告中公开，并按 [Memory 策略](references/memory/memory-policy.md) 和 [Memory 操作](references/memory/operations.md) 审核。

严禁自动把候选 Memory 写入代码规范、安全规则、架构文件或质量门禁。标准变更只能形成带证据的建议并进入版本化评审。

## 7. Skill 自进化

当用户要求优化、评分或自我改进本 Skill 时，先加载[Skill 演化协议](references/evolution.md)，运行：

```bash
python <skill-dir>/scripts/skill_health.py --skill <skill-dir> --format markdown
```

使用 `assets/evolution/test-prompts.json` 做基线和回归提示词。每轮只改一个明确短板，保留旧版本和验证证据；失败、回归或无法复核时恢复到上一个已批准版本。不得由同一个 Agent 单独完成修改、评估和批准。

调研来源与取舍见[公开 Skill 调研](references/research-sources.md)。

## 8. 交付格式

最终报告必须包含：

1. 结果与变更范围；
2. 实际运行的验证命令及结果；
3. 未运行或失败的检查及原因；
4. 已知风险、兼容性和回滚说明；
5. 本次应用、创建或停用的 Memory，不得隐藏偏好影响。

使用 [交付模板](references/delivery-template.md)，根据任务大小压缩篇幅。
