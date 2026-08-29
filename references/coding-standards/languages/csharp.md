# C#

来源：<https://google.github.io/styleguide/csharp-style.html>（上游 Google C# Style Guide；命名规则参考 Microsoft/CoreFX）

## 规则

- **MUST** 使用 2 个空格缩进、禁止 Tab、列宽上限 100、每行最多一个语句；左大括号不换行，控制结构即使可省略也使用大括号。
- **MUST** 使用 `PascalCase` 类、方法、枚举、公共字段、公共属性和命名空间；局部变量与参数使用 `camelCase`；私有/受保护字段使用 `_camelCase`。
- **MUST** 按 `public protected internal private new abstract virtual override sealed static readonly extern unsafe volatile async` 顺序排列修饰符；`using` 位于命名空间之前，`System` 组排在最前。
- **SHOULD** 每个文件保持一个核心类，文件名与核心类一致并使用 `PascalCase.cs`；类成员按嵌套类型、静态/const/readonly、字段/属性、构造器、方法分组，组内按可见性排序。
- **MUST** 能使用 `const` 就使用 `const`；无法使用时考虑 `readonly`，用命名常量替代魔法数字。
- **SHOULD** 输入参数使用最窄的只读集合类型（如 `IReadOnlyList`/`IEnumerable`），输出按是否转移所有权选择 `IList` 或只读接口。
- **SHOULD** 单行只读属性使用表达式体；复杂 lambda 或复用 lambda 提取为命名方法；避免长链式 LINQ 混淆控制流。
- **SHOULD** 几乎总是使用 class；只有小型、短生命周期、值语义明确且有性能理由时才使用 struct。
- **SHOULD** 谨慎使用 extension method，只在无法修改原类型且功能确实属于核心能力时使用；`ref` 只用于必要的输入变更，`out` 放在其他参数之后。
- **MUST** 对异步、Nullability、异常和公共 API 变化遵循项目 Analyzer/编译器配置；不得吞掉异常或用 nullable 警告抑制掩盖未验证输入。
- **MUST** 公共 API 的 XML 文档说明调用契约；实现原因使用普通注释，避免注释与命名、类型和代码重复。

## 验证

```bash
dotnet format --verify-no-changes
dotnet build --no-restore
dotnet test --no-build
```

若项目使用 StyleCop、Roslyn Analyzer 或 `.editorconfig`，这些配置高于本文件的 MAY 选择。
## 严格执行清单

### 官方章节覆盖

来源正文为 `upstream/google-styleguide/csharp-style.md`，必须覆盖以下两组章节：

| 官方章节 | 执行要点 |
|---|---|
| Formatting guidelines | 命名、文件名、成员组织、空白、括号和示例保持统一 |
| C# coding guidelines | 常量、集合接口、生成器、属性、表达式体、struct/class、lambda、初始化器、扩展方法、ref/out、LINQ、数组/List、目录、tuple、字符串、using、namespace、默认值、迭代删除、delegate、var、attribute、参数命名 |

规则等级必须按正文语气判断；本地 `MUST` 只表示仓库执行门禁或正文明确要求，不把示例偏好升级成强制规范。XML 文档、nullable、Analyzer 和异步行为必须分别给出工具或人工证据。
