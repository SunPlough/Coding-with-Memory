# TypeScript

来源：<https://google.github.io/styleguide/tsguide.html>（上游 `1809c769de31ba388c755ad15dd057a9ba8531fd`）

## 规则

- **MUST** 使用 UTF-8、2 个空格缩进、行宽 80；由仓库 Formatter 和 ESLint 统一处理空白、导入和尾逗号。
- **MUST** 使用具名导出并避免模块循环；导入真实依赖且路径、类型导入和别名遵循仓库模块解析配置。
- **MUST** 使用 TypeScript 编译器的严格配置；不得为了让修改通过而降低 `strict`、`noImplicitAny`、`strictNullChecks` 或已有项目选项。
- **MUST NOT** 使用 `@ts-ignore`、`@ts-nocheck` 或把 `@ts-expect-error` 当生产修复；测试中的例外也必须限制到单个表达式并说明原因。
- **SHOULD** 依赖类型推断减少冗余标注，但公共 API、复杂泛型和容易出错的边界必须有明确类型。
- **SHOULD** 优先接口表达可扩展对象契约；联合类型保持范围窄，避免用宽泛 `any` 逃避建模。
- **SHOULD** 显式处理 `undefined`/`null`；不要用非空断言 `!` 掩盖未验证的外部输入。
- **SHOULD** 使用 `camelCase` 变量/函数、`PascalCase` 类/接口/类型、`CONSTANT_CASE` 常量；缩写按普通单词处理。
- **MUST** 用 JSDoc 记录用户依赖的导出契约，使用普通 `//` 记录实现原因；多行注释使用连续单行注释，不画星号框。
- **MUST** 公共导出、弃用 API 和装饰器类的文档放在装饰器之前；JSDoc 不重复 TypeScript 已表达的类型。
- **SHOULD** 将复杂或复用的 lambda 提取为命名函数；异步错误、取消和资源清理必须可观察。
- **MUST** 遵循适用的 Tsetse/tsec 或项目安全规则，特别是动态代码执行、危险 DOM 写入和未受控全局。

## 验证

```bash
npx --no-install prettier --check <changed-files>  # 若仓库使用 Prettier
npx --no-install eslint <changed-files>
npx --no-install tsc --noEmit
npm test
```
## 严格执行清单

### 官方章节覆盖

必须读取 `upstream/google-styleguide/tsguide.html` 的全部章节：

| 官方章节 | 必查主题 |
|---|---|
| Introduction | 术语、TypeScript 与 JavaScript 关系 |
| Source file basics / structure | UTF-8、模块、导入导出、循环依赖、文件组织和可见性 |
| Language features | 控制流、类、函数、异步、Promise、装饰器、动态代码和错误 |
| Naming | 文件、标识符、属性、类型、泛型、常量、缩写 |
| Type system | nullability、类型推断、联合/交叉、`any`、断言、重载和类型边界 |
| Toolchain requirements | tsc、格式化、lint、安全规则和配置不能互相替代 |
| Comments and documentation | JSDoc/TSDoc、公共导出、弃用、装饰器前文档和实现原因 |
| Policies | 禁止项、兼容性、生成代码和例外 |

每条 TypeScript 规则必须保留官方章节和工具/人工证据；`tsc --noEmit` 不能证明命名、文档、模块循环和运行时验证通过。
