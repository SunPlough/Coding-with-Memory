# Definition of Done

完成编码不等于完成交付。只有满足适用门禁并保留证据，任务才可标记为完成。

## 必须项

- 目标和非目标与实际 diff 一致。
- 变更路径使用了仓库规则、语言规范和注释规范。
- 行为变化有测试或其他明确可重复的验证。
- 外部输入、I/O、权限、持久化和第三方调用的失败路径已检查。
- 未引入密钥、个人数据、无依据的注释或无关改动。
- 运行适用的构建、类型、Lint、测试和安全检查；未发现的检查单独报告。
- 交付报告区分 `passed`、`failed`、`skipped` 和 `not-found`。

## 按风险增加

| 变更类型 | 额外证据 |
|---|---|
| S 级单点修改 | 变更卡、定向测试或检查、diff 复核 |
| M 级多文件修改 | 增量切片记录、受影响测试、注释审计 |
| L 级公共 API/迁移/权限/生产操作 | 方案批准、兼容性与回滚路径、完整门禁、安全复核、人工确认 |

## 证据包

每次交付至少保留以下信息：

```text
task_id
changed_paths
acceptance_criteria
commands_and_exit_codes
observed_results
unrun_checks_and_reasons
known_risks_and_rollback
memory_applied_or_proposed
```

不要用“看起来正常”、覆盖率单一数字或 Agent 自述替代命令输出、测试结果和人工复核。
