# JavaScript

来源：<https://google.github.io/styleguide/jsguide.html>（上游 `1809c769de31ba388c755ad15dd057a9ba8531fd`）

Google 已停止更新 JavaScript Guide，并建议迁移到 TypeScript；维护遗留 JavaScript 时仍按本文件执行，新模块优先评估 TypeScript。

## 规则

- **MUST** 使用 UTF-8、2 个空格缩进、行宽 80；语句以分号结束；使用 Google JavaScript Formatter 或仓库批准的等价工具。
- **MUST** 使用 ES modules 的 `import/export` 或项目既定的 `goog.module`；新文件明确选择模块系统，不在同一文件混用 Closure、CommonJS 和 ES modules。
- **MUST** 在 ES modules 中使用具名导出、在导入路径保留 `.js` 扩展名，并避免模块循环；不要新增 default export。
- **MUST** 优先 `const`，需要重新赋值时使用 `let`；**MUST NOT** 新增 `var`，除非项目有明确的遗留兼容约束。
- **MUST** 对块控制结构使用大括号；左大括号不换行；函数、类和对象的换行遵循格式化器。
- **SHOULD** 使用单引号字符串；模板字符串只用于插值或多行文本；避免通过 `+` 拼接复杂字符串。
- **SHOULD** 使用 `===`/`!==`；不要依赖隐式类型转换。异步函数必须显式处理拒绝、取消和超时语义。
- **MUST NOT** 使用 `eval`、`with`、隐式全局变量或未批准的动态代码执行；不得为了绕过类型/工具检查增加兼容分支。
- **SHOULD** 使用 `camelCase` 变量/函数、`PascalCase` 类/构造器、`CONSTANT_CASE` 常量；名称应完整表达含义，避免任意缩写。
- **MUST** 使用 JSDoc `/** */` 描述调用者需要知道的导出契约；实现原因使用普通 `//` 注释，不把两者混用。
- **MUST** 为弃用的公共 API 写 `@deprecated` 和迁移方向；生成代码可按生成器规则例外，但手写导出名称仍需符合命名规则。
- **SHOULD** 保持函数短小、模块边界清楚；长链式转换或复杂匿名函数改为命名函数以便测试和复用。

## 验证

```bash
npx --no-install google-closure-compiler --formatting=PRETTY_PRINT <changed-files>  # 若项目使用 Closure
npx --no-install eslint <changed-files>
npm test
```

不要假设仓库一定使用 Closure；以 `package.json` 和锁文件为事实。
## 严格执行清单

### 官方章节覆盖

必须读取 `upstream/google-styleguide/jsguide.html` 与 `javascriptguide.xml`：

| 官方章节 | 必查主题 |
|---|---|
| 1 Introduction | 术语和适用边界 |
| 2 Source file basics | 文件名、UTF-8、特殊字符和非 ASCII |
| 3 Source file structure | fileoverview、goog.module、ES modules、导入导出、循环依赖、Closure 互操作、test-only 和 require |
| 4 Formatting | 括号、缩进、语句、分号、80 列、换行、空白、数组/对象/class/function/switch |
| 5 Language features | 类型转换、对象、类、函数、控制流、异常、Promise、模块和动态代码 |
| 6 Naming | 文件、标识符、属性、常量、私有成员和缩写 |
| 7 JSDoc | 标签、类型、模板、可见性、弃用和导出契约 |
| 8 Policies / 9 Appendices | 禁止项、工具、兼容和附录约定 |

新模块优先 TypeScript，但遗留 JavaScript 不能用迁移意愿跳过本指南。Closure、ESLint、测试和人工语义审查分别记录状态。
