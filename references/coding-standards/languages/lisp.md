# Lisp

来源：<https://google.github.io/styleguide/lispguide.xml>（Google Common Lisp Style Guide；不是所有 Lisp 方言的通用规范）。

## 规则

- **MUST** 在执行格式和命名规则前确认方言、实现、包系统和构建入口；以下 Google 细则仅适用于 Common Lisp。Clojure、Scheme、Emacs Lisp 等必须改用仓库规则和对应方言的官方工具。
- **MUST** 将 Common Lisp 行宽控制在 100 字符内，使用空格而不是 Tab，并采用正确配置的 Emacs `cl-indent`/SLIME 缩进；已有项目可定义一致的本地 indentation style。
- **MUST** 每个文件使用明确的 `defpackage`/`in-package` 组织包边界；包、符号导出、文件布局和依赖遵循仓库约定，不把内部符号意外暴露为公共 API。
- **MUST** 顶层 form 之间通常保留一个空行；连续右括号必须留在表达式最后一行，不把右括号单独放在新行。
- **MUST** 使用正确的注释分号层级：`;;;;` 文件/大章节、`;;;` 定义组、`;;` 代码段、`;` 行尾；分号后留空格，文档字符串与注释使用正确拼写和完整语义。
- **SHOULD** 优先使用普通函数表达业务逻辑；只有宏能清楚表达编译期变换、资源作用域或 DSL 语义时才新增 Macro，并说明求值次数和副作用。
- **MUST** 显式处理 Condition、异常、资源释放和动态绑定边界；不得用全局可变状态隐藏跨调用的生命周期。
- **SHOULD** 保持函数和宏短小，避免深层嵌套、隐式控制流和没有当前调用方的通用协议；公共包记录输入、输出和错误契约。
- **MUST** 遵循方言对应的 Formatter/Lint 和编译器告警；Common Lisp 需要加载/编译受影响 system，并运行仓库测试。生成代码按生成器规则检查，手写代码仍需人工审查。

## 验证

```bash
# 按仓库声明替换命令；以下仅表示验证类别
<dialect-formatter> --check <changed-files>
<dialect-linter> <changed-files>
<dialect-compiler-or-loader> <project-entry>
<project-test-command>
```

工具不存在时标记 `not-found`，不得把未执行的方言检查报告为通过。
## 严格执行清单

### 方言与正文边界

`upstream/google-styleguide/lispguide.xml` 是 Google Common Lisp Style Guide，只适用于 Common Lisp。Clojure、Scheme、Emacs Lisp 等必须标记 `external-source` 并加载各自官方规范；文件扩展名不能代替方言判定。

### 官方章节覆盖

按正文逐项检查行宽和缩进、包与文件、宏和条件系统、注释分号层级、命名、函数/变量、格式化、错误处理、测试和文档。每个宏必须人工说明求值次数、副作用和为何普通函数不能表达；Formatter 通过不代表包边界和动态绑定契约通过。
