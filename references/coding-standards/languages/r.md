# R

来源：<https://google.github.io/styleguide/Rguide.html>（Google R Style Guide，基于 Tidyverse 并包含 Google 差异）

## 规则

- **MUST** 使用 `BigCamelCase` 命名函数；私有函数以点号开头；对象、参数和文件名保持项目一致。
- **MUST NOT** 使用 `attach()` 或右向赋值 `->`；它们会隐藏对象来源并增加名称冲突风险。
- **MUST** 对函数使用显式 `return()`，不要依赖隐式返回；外部包函数使用显式命名空间 `pkg::fun()`。
- **SHOULD** 在包级文件提供文档和 NAMESPACE；避免用 `@import` 导入整包，优先 `@importFrom`。
- **SHOULD** 保持数据转换可复现、避免隐藏全局状态；向量化和 pipe 链必须服务于可读性。
- **MUST** 为公共函数记录参数、返回值、副作用和错误；注释不重复表达式本身。

## 验证

```bash
Rscript -e "styler::style_pkg(dry = 'fail')"
Rscript -e "quit(status = length(lintr::lint_package()))"
R CMD check <package>
```
## 严格执行清单

### 官方章节覆盖

Google R 正文由 `upstream/google-styleguide/Rguide.md` 与 `Rguide.xml` 提供，必须覆盖：

| 官方主题 | 审查重点 |
|---|---|
| Syntax | 命名、格式、函数、控制流和避免隐式状态 |
| Naming conventions | 函数、对象、参数、文件和大小写 |
| Namespace/Packages | `pkg::fun()`、NAMESPACE、导入粒度和包文档 |
| Pipes | 管道可读性、右向赋值禁用和中间状态 |
| Documentation | Roxygen2、参数、返回值、副作用和错误 |
| Reproducibility | 随机性、全局状态、数据和版本 |

`styler` 通过不证明向量化语义、缺失值处理、包导出或可复现性；这些需要测试、R CMD check 或人工证据。
