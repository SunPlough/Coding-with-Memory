# Google Style Guide 严格执行协议

本文件是本 Skill 的规范执行入口。它把 Google Style Guide 的官方全文快照、语言适用范围、工具验证和人工审查绑定起来。语言摘要文件只负责路由和项目化解释，不能替代官方全文。

## 1. 规范来源

- 官方仓库：<https://github.com/google/styleguide>
- 固定分支：`gh-pages`
- 固定提交：`1809c769de31ba388c755ad15dd057a9ba8531fd`
- 核验日期：2026-08-28
- 官方许可：CC BY 3.0 Unported；归属和许可见 [NOTICE-google-styleguide.txt](NOTICE-google-styleguide.txt)。

`upstream/google-styleguide/` 保存上述提交的官方原文快照。快照只允许通过上游提交更新，不在本地翻译、删节或重排原文。项目使用的语言若没有对应快照，必须使用官方链接并记录 `external-source`，不得把其他语言规则冒充 Google 规则。

快照文件、官方路径、提交 blob SHA、文件大小和 SHA-256 记录在
[upstream-manifest.json](upstream-manifest.json)。执行任何规范审查前必须运行：

```bash
python <skill-dir>/scripts/verify_upstream.py --skill <skill-dir>
```

校验失败时，相关规范状态只能记为 `failed`，不得继续声称已按固定版本执行。

## 2. 严格加载顺序

对每个变更路径执行以下顺序：

1. 读取 `base.md` 和本文件。
2. 用 `language-map.yaml` 识别语言；`.h` 先完成 C/C++ 判定。
3. 读取 `languages/<language>.md`，获取适用范围、章节映射和验证命令。
4. 读取对应的 `upstream/google-styleguide/` 全文快照。全文很长时可以按章节检索，但不能只凭摘要作结论。
5. 读取注释规范、框架规范和项目覆盖规则。
6. 先执行官方原文的禁止项和强制项，再执行推荐项；项目规则只能收紧或明确例外，不能用个人偏好放宽。
7. 对每条规则写入审查证据：`source_section`、`scope`、`status`、`evidence`、`exception_reason`（如适用）。

## 3. 状态和例外

每项检查只能使用以下状态：

| 状态 | 含义 |
|---|---|
| `passed` | 工具或人工证据证明符合规则 |
| `failed` | 明确违反规则，必须修复或获得覆盖批准 |
| `manual-review` | 工具无法表达，需要人工逐项审查 |
| `not-found` | 所需 Formatter/Lint/编译器/文档工具不存在 |
| `skipped` | 规则不适用于当前路径，必须写适用性理由 |
| `exception-approved` | 有项目规则、兼容性、性能或安全证据，并记录所有者和复核日期 |

以下说法都不能替代证据：“Google 推荐，所以应该没问题”“格式化器没报错，所以全部通过”“旧代码太多所以跳过”。

## 4. 语言全文映射

| 语言 | 官方快照 | 重点章节 |
|---|---|---|
| C++ | `cppguide.html` | 版本、头文件、命名、格式、所有权、异常、RTTI、模板、注释、测试 |
| C# | `csharp-style.md` | 命名、文件、修饰符、成员顺序、常量、类/结构体、扩展方法、格式 |
| Go | `go/index.md`、`go/guide.md`、`go/decisions.md`、`go/best-practices.md` | 可读性、错误、接口、并发、命名、注释、测试 |
| HTML/CSS | `htmlcssguide.html` | 文档、格式、语义、资源、可访问性、CSS 选择器和验证 |
| Java | `javaguide.html` | 源文件、导入、格式、命名、类成员、异常、通用编程、Javadoc |
| JavaScript | `jsguide.html`、`javascriptguide.xml` | 模块、导出、变量、类型、控制流、类、Promise、注释、工具 |
| JSON | `jsoncstyleguide.xml` | 属性、类型、数组、空值、分页、错误、兼容和排序 |
| Common Lisp | `lispguide.xml` | 行宽、缩进、包、宏、条件、注释、命名、测试 |
| Markdown | `docguide/style.md`、`docguide/best_practices.md` | 结构、标题、链接、代码、表格、格式和可访问性 |
| Objective-C | `objcguide.md`、`objcguide.xml` | 文件、命名、ARC、所有权、头文件、错误、注释、格式 |
| Python | `pyguide.md`、`pylintrc`、`google_python_style.vim` | Lint、导入、异常、可变状态、推导式、资源、注释、命名、类型 |
| R | `Rguide.md`、`Rguide.xml` | 命名、格式、函数、包、文档、可复现性和工具 |
| Shell | `shellguide.md` | 文件、注释、格式、引用、ShellCheck、eval、数组、测试 |
| TypeScript | `tsguide.html` | 模块、导出、类型、nullability、any、错误、装饰器、JSDoc、安全 |
| Vimscript | `vimscriptguide.xml`、`vimscriptfull.xml` | 作用域、命名、缩进、正则、命令、自动命令、错误 |
| XML | `xmlstyle.html` | 文档、元素、属性、命名空间、缩进、注释、Schema |

Google 主仓库当前不包含 Dart、Kotlin、Rust、Swift 或专门的 C Guide。它们必须在本地文件中明确标记为 `external-source` 或 `no-google-guide`，遵循各自官方来源，不能声称来自 `google/styleguide`。

## 5. 逐项审查模板

```text
language: python
source_snapshot: upstream/google-styleguide/pyguide.md
source_section: 3.8 Comments and Docstrings
scope: changed-files
rule: MUST use triple-double-quote docstrings for modules, functions, and classes
status: passed | failed | manual-review | not-found | skipped | exception-approved
evidence: command output, diff location, or reviewer observation
exception_reason: required only for exception-approved
owner: required only for exception-approved
review_after: required only for exception-approved
```

## 6. 工具职责

- Formatter 只证明格式化器可接受，不证明命名、所有权、错误处理或 API 语义。
- Lint/静态分析只证明其规则集，不证明未启用的规则。
- 编译器/类型检查只证明编译和类型约束，不证明运行时契约。
- 测试只证明被覆盖的行为；没有测试覆盖的规则必须进入 `manual-review`。
- Agent 必须审查工具无法表达的条款，并绑定到 diff、测试、构建配置或项目规则。

## 7. 快照范围

manifest 当前纳入 Google 仓库中与代码规范直接相关的指南正文、文档规范、Go 分册、Python 配置和 IDE/Formatter 配置，共 43 个文件。仓库网站的主题 CSS、图片、构建脚本和其他展示资源不属于 Agent 规范正文，因此不纳入语言规则加载；如某个项目明确依赖这些资源，必须按来源单独登记，不能把它们当作已加载的规范条款。

## 8. 更新协议

更新官方快照前必须记录旧提交、新提交、变更文件、规则差异、许可检查和回归结果。只要快照与本地执行清单不一致，就不能声称“严格遵守最新 Google 标准”。
