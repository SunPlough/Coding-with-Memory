# Dart

来源：<https://dart.dev/effective-dart>（Google Style Guide 的 Dart 链接委托至 Effective Dart）

## 规则

- **MUST** 运行 `dart format`；使用 2 个空格缩进、尾逗号和仓库约定的文件布局。
- **MUST** 启用并遵循 Sound Null Safety；外部输入和异步边界不得用 `!` 代替检查。
- **SHOULD** 使用 `lowerCamelCase` 变量/成员、`UpperCamelCase` 类型/枚举、`lowercase_with_underscores` 库文件；避免缩写和冗余类型名。
- **SHOULD** 使用 `final`/不可变值；只有确有状态变化时才使用 `var` 或可变集合。
- **MUST** 为公共 API 提供 dartdoc；文档说明调用契约、异常、生命周期和异步语义，不重复显然类型。
- **SHOULD** 使用 `async`/`await` 保持异步控制流直接；取消、超时和 Stream 生命周期必须可观察。
- **MUST NOT** 在未有证据时引入全局状态、隐式动态类型或魔法扩展方法；优先项目已有 package 模式。

## 验证

```bash
dart format --output=none --set-exit-if-changed .
dart analyze
dart test
```
