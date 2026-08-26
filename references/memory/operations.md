# Memory 操作

运行时数据始终存放在目标项目根目录 `.coding-memory/`，不要写入 Skill 目录。

## 初始化

```bash
python <skill-dir>/scripts/memory_tool.py --repo <repo> init
```

该命令创建英文结构化字段和追加式 JSONL 文件。默认 `.gitignore` 忽略运行时 Memory；只有项目明确批准共享时，才调整版本控制策略。

## 任务开始检索

默认只读已批准条目：

```bash
python <skill-dir>/scripts/memory_tool.py --repo <repo> search --query "错误处理"
python <skill-dir>/scripts/memory_tool.py --repo <repo> list --category preference
```

检索结果仍受强制优先级约束。发现冲突时忽略 Memory，并记录冲突证据。

## 记录轨迹

```bash
python <skill-dir>/scripts/memory_tool.py --repo <repo> trace \
  --task-id task-0001 --event feedback --outcome success \
  --summary "用户要求最终报告先给结论" \
  --evidence "本次任务中的用户明确反馈"
```

只记录对复用或复盘有价值的事件，不把每次工具调用完整复制进轨迹。

## 提出候选偏好

```bash
python <skill-dir>/scripts/memory_tool.py --repo <repo> add \
  --category preference \
  --summary "最终报告先给结论，再列验证证据" \
  --trigger "交付报告" \
  --action "先输出结果摘要，再列验证证据" \
  --domain delivery \
  --scope repository \
  --source explicit-feedback \
  --effect report_format \
  --evidence "用户明确要求：先说结果"
```

新增条目固定为 `candidate`。同一类别、作用域和归一化摘要重复时返回已有条目，不重复写入。

优先填写 `trigger`、`action` 和 `domain`，让条目保持原子、可回放；字段缺失时仍兼容旧条目。

工程决策、可复用模式和事故分别使用 `decision`、`pattern`、`incident`，不得伪装成用户偏好。

## 审核状态

```bash
python <skill-dir>/scripts/memory_tool.py --repo <repo> transition mem-xxxxxxxxxxxx \
  --status approved --actor human \
  --reason "用户确认在本项目持续采用" \
  --evidence "评审记录或用户明确确认"
```

拒绝使用 `--status rejected`，失效使用 `--status deprecated`。每次转换必须提供操作者、原因和证据；历史事件不会被覆盖。

## 重建索引

```bash
python <skill-dir>/scripts/memory_tool.py --repo <repo> index
```

`index.json` 是可重建派生数据，只汇总当前状态和审核队列。原始条目、轨迹和转换事件仍保留在 JSONL 中。

## 自动提取流程

1. 从本次对话和执行轨迹识别明确反馈、重复选择、成功路径与失败原因。
2. 删除整段对话、源码、秘密、个人数据和无关细节。
3. 分类为偏好、决策、模式或事故，写明作用域、证据和置信度。
4. 与当前条目去重，仅创建候选。
5. 在交付报告中公开列出候选内容和影响范围。
6. 未经批准，不在后续任务中应用候选偏好。
