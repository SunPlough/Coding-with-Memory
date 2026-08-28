# Objective-C

来源：<https://google.github.io/styleguide/objcguide.html>（Google Objective-C Style Guide）

## 规则

- **MUST** 使用 2 个空格缩进、80 列、Google/仓库 Formatter；类、方法、属性和文件命名遵循 Objective-C Cocoa 约定。
- **MUST** 明确 `.h` 公共契约与 `.m` 实现边界；头文件直接 include/import 需要的声明，不依赖传递依赖。
- **SHOULD** 使用 ARC、明确 Nullability 和所有权；避免在公共 API 隐藏对象生命周期、副作用或线程要求。
- **MUST NOT** 使用 C++ 异常替代 Objective-C 错误模型；NSError、返回值和异常路径必须遵循仓库约定。
- **SHOULD** 类职责聚焦，方法短小；避免宏、隐式全局状态和没有当前用例的 category 扩展。
- **MUST** 为公共类、方法、属性和协议提供 HeaderDoc 风格契约；实现注释只解释非显然原因。
- **SHOULD** 用 `// NOLINT` 或 `// NOLINTNEXTLINE` 标记有意违反的局部规则，并说明原因，不用全文件关闭检查。

## 验证

```bash
clang-format --dry-run --Werror <changed-objc-files>
xcodebuild -scheme <scheme> build
xcodebuild -scheme <scheme> test
```
