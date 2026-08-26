# 中文注释参考来源

不同来源的证据强度不同。受欢迎的源码注解仓库不自动等于规范；复制上游文字前必须重新检查许可和版本。

## 规则来源

| 来源 | 固定版本 | 可借鉴内容 | 本 Skill 的使用方式 |
|---|---|---|---|
| [Alibaba P3C](https://github.com/alibaba/p3c) | `6c59c8c36ecd` | Java PMD 中可执行的 Javadoc、注释放置、枚举注释和禁止注释旧代码规则 | Java 强参考；提炼语义，不把所有 P3C 规则跨语言强制执行 |
| [FEX Style Guide](https://github.com/fex-team/styleguide) | `b1bc701d1c92` | 中文 JavaScript 注释分段和结构化 TODO/FIXME/HACK | 前端格式参考；不继承过时的 AMD/作者规则 |
| [EFE Specifications](https://github.com/ecomfe/spec) | `18a2da2fbc8c` | HTML/CSS/JavaScript 注释放置和文档示例 | 仅比较参考；根目录许可不清晰，不复制其原文 |
| [Chinese Copywriting Guidelines](https://github.com/sparanoid/chinese-copywriting-guidelines) | `9a5fbeb842f3` | 中英文间距与标点一致性 | 与源码 Formatter/工具不冲突时作为写作参考 |

## 示例语料

| 来源 | 固定版本 | 价值 | 限制 |
|---|---|---|---|
| [Hutool](https://github.com/dromara/hutool) | `8870454b2a0c` | 大型 Java 项目中的中文 Javadoc 和领域术语 | 只作语料；数量和局部约定不能成为通用规则 |
| [Redis 3.0 annotated](https://github.com/huangzworks/redis-3.0-annotated) | `8e60a75884e7` | 算法与数据结构的中文解释 | 旧版本教学注解，不是生产注释密度目标 |
| [source-code-hunter](https://github.com/doocs/source-code-hunter) | 使用前检查当前版本 | 框架内部实现的中文解释 | 主要是学习材料，不把教程段落蒸馏进生产注释 |
| [中文技术文档写作规范](https://github.com/ruanyf/document-style-guide) | `571951731efb` | 清晰中文技术表达 | 是文档写作参考，不是代码注释语法；审查时未发现清晰根许可 |

## 提炼结论

本 Skill 采用五个稳定原则：注释必须增加非显然信息、文档注释服从语言工具、解释性注释放在相关代码上方、旧代码直接删除、延迟工作标记必须可追踪。

明确拒绝：每个函数强制注释、永久作者/日期标签、遗留 AMD 专属规则和教学式高密度注释。
