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
## 严格执行清单

### 外部官方来源边界

Dart 不在 `google/styleguide` 主仓库中。本文件使用 <https://dart.dev/effective-dart>，状态为 `external-source`；更新时记录 Effective Dart 的版本或页面快照，不能使用 Google 主仓库提交号冒充来源。

### Effective Dart 覆盖

| 官方分组 | 执行要点 |
|---|---|
| Style | `dart format`、命名、文件布局、空白和尾逗号 |
| Documentation | dartdoc、句子、示例和公共 API 契约 |
| Usage | null safety、async/await、异常、资源和集合 API |
| Design | 类型、不可变性、API 形状、命名参数和扩展边界 |

项目不存在 Dart 工具时只能记 `not-found`；不要用 Flutter 构建成功替代格式、分析和 API 文档证据。
