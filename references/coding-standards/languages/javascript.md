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
npx google-closure-compiler --formatting=PRETTY_PRINT <changed-files>  # 若项目使用 Closure
npx eslint <changed-files>
npm test
```

不要假设仓库一定使用 Closure；以 `package.json` 和锁文件为事实。
