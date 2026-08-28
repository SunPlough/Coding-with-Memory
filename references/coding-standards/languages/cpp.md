# C++

来源：<https://google.github.io/styleguide/cppguide.html>（上游 `1809c769de31ba388c755ad15dd057a9ba8531fd`）

本文件提炼 Google C++ Style Guide 的可执行规则；完整背景、例外和理由以上游原文为准。

## 规则

- **SHOULD** 以 C++20 为目标且不得使用 C++23 特性；**MUST** 遵循项目实际声明的语言版本，不能为了套用风格指南擅自升级工具链或标准。
- **MUST** 让头文件自包含、使用项目路径下的 `#define` include guard，并直接 include 所依赖的声明；不得依赖传递 include。
- **MUST** 按相关头文件、C 系统头、C++ 标准库、其他库、项目头文件的顺序组织 include；每组内部按字典序。
- **MUST** 使用 2 个空格缩进、每行一个语句、默认 80 列；左大括号不换行，控制语句即使可省略也优先保留大括号。
- **SHOULD** 保持动态对象的单一固定所有者；优先用 RAII 和 `std::unique_ptr` 表达独占所有权，裸指针或引用只表达不拥有的观察关系。只有性能证据或不可避免的共享生命周期才使用 `std::shared_ptr<const T>`，不用 `new/delete` 手工管理常规生命周期。
- **SHOULD** 优先值语义、`std::optional`/`std::variant` 和窄接口；避免多重继承、隐式转换、宏和没有当前用例的模板抽象。
- **MUST NOT** 在 Google 风格代码中使用 C++ 异常；**AVOID** RTTI，只有成熟层次结构无法合理改造或测试确有需要时例外。错误模型遵循项目批准的 status/status-or 或等价契约。
- **MUST** 使用 C++ 风格 cast（`static_cast`/`const_cast`/`reinterpret_cast`/`dynamic_cast`）或花括号数值转换；禁止 C 风格 cast。
- **SHOULD** 将短小定义放在头文件，复杂实现放在 `.cc`；公共头文件中不得暴露不必要的实现细节。
- **MUST** 使用小写文件名（项目已有约定可选下划线或短横线）、`PascalCase` 普通函数和类型、`snake_case` 变量/数据成员/命名空间、`kConstantCase` 常量、`ALL_CAPS` 仅用于宏；访问器可使用 `snake_case`。命名应完整、可读且避免缩写。
- **SHOULD** 明确拷贝/移动/析构语义；需要自定义其中一个特殊成员函数时检查 Rule of Five 和资源所有权。
- **MUST** 通过编译器告警、格式化器、单元测试和 Sanitizer 证明变更；性能例外必须附基准或测量证据。
- **SHOULD** 注释“为什么”而不是复述语句；所有权转移、线程约束、单位、协议和不变量必须在调用点可见。

## 验证

```bash
clang-format --dry-run --Werror <changed-cc-and-h-files>
cmake --build <build-dir> --config Debug --parallel
ctest --test-dir <build-dir> --output-on-failure
```

使用 `include-what-you-use`、Clang-Tidy、Sanitizer 时以仓库配置为准。
