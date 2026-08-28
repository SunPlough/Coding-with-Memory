# Lisp

来源：<https://google.github.io/styleguide/lispguide.xml>（Google Lisp Style Guide；适用范围取决于方言）。

## 规则

- **MUST** 在执行格式和命名规则前确认方言、实现、包系统和构建入口；Common Lisp、Clojure、Emacs Lisp 等不能混用规则。
- **MUST** 遵循仓库现有的 Package/Namespace、文件布局、命名、Condition/Error、文档和测试模式；同一包内保持局部一致。
- **SHOULD** 优先使用普通函数表达业务逻辑；只有宏能清楚表达编译期变换、资源作用域或 DSL 语义时才新增 Macro，并说明求值次数和副作用。
- **MUST** 显式处理 Condition、异常、资源释放和动态绑定边界；不得用全局可变状态隐藏跨调用的生命周期。
- **SHOULD** 保持函数和宏短小，避免深层嵌套、隐式控制流和没有当前调用方的通用协议；公共包记录输入、输出和错误契约。
- **MUST** 遵循方言对应的 Formatter/Lint 和编译器告警；生成代码按生成器规则检查，手写代码仍需人工审查。

## 验证

```bash
# 按仓库声明替换命令；以下仅表示验证类别
<dialect-formatter> --check <changed-files>
<dialect-linter> <changed-files>
<dialect-compiler-or-loader> <project-entry>
<project-test-command>
```

工具不存在时标记 `not-found`，不得把未执行的方言检查报告为通过。
