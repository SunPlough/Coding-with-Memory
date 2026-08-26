# 公开 Skill 调研

调研日期：2026-08-26。这里只记录影响当前设计的公开来源与取舍，不复制其完整实现。

| 来源 | 采用的思想 | 未直接采用的部分 |
|---|---|---|
| [女娲 Skill](https://github.com/alchaincyf/nuwa-skill) | 多层提炼、来源分级、反模式、诚实边界、自包含参考资料 | 人物角色与表达模仿不适用于工程规范 |
| [达尔文 Skill](https://github.com/alchaincyf/darwin-skill) | 基线、测试提示词、单变量实验、独立评估、人工检查点、保留/回滚棘轮 | 不用单一绝对分数自动决定 Skill 好坏 |
| [Superpowers](https://github.com/obra/superpowers) | 设计/计划/实现/评审/交付分阶段；完成声明必须有新鲜验证证据；根因调试 | 不把所有小任务都扩大成重型审批流程 |
| [Agent Skills](https://github.com/addyosmani/agent-skills) | 意图路由、退出条件、反自我说服、Definition of Done、按严重性评审 | 不拆成大量互相依赖的独立 Skill |
| [Karpathy-inspired Guidelines](https://github.com/multica-ai/andrej-karpathy-skills) | 显式假设、最小代码、手术式变更、目标驱动验证 | 不把所有不确定性都变成人工阻塞点 |
| [ECC](https://github.com/affaan-m/ECC) | 项目级 Memory 隔离、原子经验、置信度与证据、重叠能力合并 | 不引入持续监听 Hook、后台模型或自动发布规则 |
| [Evolve Skill](https://github.com/taneltaluri/evolve-skill) | 开发集/保留集、稳定性与功能保持门禁 | 第一版不引入复杂统计评分器 |

## 对 Coding with Memory 的约束

- 规范层保持冻结式管理：Memory 只能提出建议，不能自动改写。
- 演化层以行为回归为先，静态结构检查只用于发现缺口。
- 一轮只改变一个可归因短板；没有独立复核时不宣布改进成立。
- 失败机制、危险动作和诚实边界必须显式写出。
