# Kotlin

来源：<https://developer.android.com/kotlin/style-guide>（Android Kotlin Style Guide，Google 维护）

## 规则

- **MUST** 使用 Kotlin 官方 Formatter/IDE 格式化；4 个空格缩进、禁止 Tab；文件名使用 `PascalCase.kt`，顶层声明保持聚焦。
- **SHOULD** 使用 `val` 优先于 `var`，不可变集合优先；公共 API 显式声明可见性和返回类型。
- **MUST** 显式表达 Nullability；不以 `!!` 代替边界校验，避免把平台类型直接传播到业务层。
- **SHOULD** 使用 `camelCase` 函数/变量、`PascalCase` 类/对象、`UPPER_SNAKE_CASE` 常量；缩写按普通单词处理。
- **SHOULD** 使用表达式、命名参数、窄作用域函数和 sealed 类型表达状态；复杂链式 scope function 改为命名步骤。
- **MUST** 使用结构化并发；Android 生命周期、主线程和取消语义必须遵循项目架构组件约定。
- **MUST** 为公共 API 和非显然扩展函数提供 KDoc；记录副作用、线程、异常和资源生命周期。

## 验证

```bash
./gradlew ktlintCheck detekt
./gradlew assemble
./gradlew test
```
## 严格执行清单

### 外部官方来源边界

Kotlin 不在 `google/styleguide` 主仓库中。本文件使用 <https://developer.android.com/kotlin/style-guide>，状态为 `external-source`，并受 Android/仓库版本约束；不得引用 Google 主仓库提交号作为 Kotlin 规范版本。

### 官方主题覆盖

必须逐项检查源文件组织、格式化、命名、文档注释、可见性、空值、集合、表达式、扩展函数、协程、Android 生命周期和测试。Kotlin 编译通过不能替代 KtLint/Detekt、KDoc、结构化并发和主线程证据。
