# Swift

来源：<https://google.github.io/swift/>（独立 Google Swift Style Guide，不属于 `google/styleguide` 主仓库）。

## 规则

- **MUST** 使用仓库批准的 Swift Format/SwiftLint 配置；不要手工保留与格式化器冲突的空白、括号或换行例外。
- **MUST** 遵循 Swift API Design Guidelines 的命名和调用标签；类型使用 `UpperCamelCase`，变量、函数和成员使用 `lowerCamelCase`，缩写在同一 API 表面保持一致。
- **MUST** 显式处理 Optional、错误和并发取消；不得用强制解包 `!`、`try!` 或 `fatalError` 掩盖外部输入、网络、持久化和用户操作失败。
- **SHOULD** 优先值语义、不可变 `let`、窄协议和结构化并发；只有当前调用方需要时才引入 protocol、泛型或兼容层。
- **MUST** 明确引用生命周期、Task/Actor 隔离、Sendability 和 UI 主线程约束；资源和任务必须有可观察的结束或取消路径。
- **SHOULD** 为公共 API 提供文档注释，记录前置条件、线程/Actor、错误、生命周期和弃用迁移；普通注释记录原因而不是复述代码。

## 验证

```bash
swift format lint --strict <changed-swift-files>  # 按仓库工具版本调整
swiftlint lint --strict
swift build
swift test
```

平台专属构建（如 Xcode scheme）以仓库配置为准；工具不存在时标记 `not-found`。
