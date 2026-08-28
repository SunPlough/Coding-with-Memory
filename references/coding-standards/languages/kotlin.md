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
