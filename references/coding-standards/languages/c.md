# C

来源：Google Style Guide 没有专门的 C Guide；本文件明确采用项目声明的 C 标准（如 C11/C17）和编译器/安全工具规则，不冒充 Google C 规范。

跨语言通用层仍然适用。若项目同时含 C++，先按 [C 或 C++ 头文件判定](c-or-cpp-header.md) 识别语言，不得把 C++ 规则直接套用到 C。

## 规则

- **MUST** 明确 C 标准和编译器告警级别；不使用编译器扩展，除非项目覆盖规则说明兼容范围。
- **MUST** 让头文件自包含、使用 include guard、直接声明所需依赖；公共头文件不得依赖调用者的 include 顺序。
- **MUST** 明确指针所有权、缓冲区容量、生命周期、错误码和线程安全；公共函数在头文件注释中记录调用契约。
- **SHOULD** 使用 4 个空格或仓库统一的缩进、每行一个语句、短函数和小模块；避免宏模拟复杂控制流。
- **MUST** 检查返回值和边界；不得忽略分配、I/O、字符串和系统调用失败。
- **SHOULD** 使用 `snake_case` 标识符和有语义的命名；宏使用全大写并带项目命名空间前缀。
- **MUST** 通过编译器 `-Wall`/`-Wextra` 等项目告警、静态分析、Sanitizer 和测试；具体级别以仓库配置为准。

## 验证

```bash
clang-format --dry-run --Werror <changed-c-files-and-headers>
cc -std=<project-standard> -Wall -Wextra -Werror -fsyntax-only <changed-files>
```
## 严格执行清单

- `source_status`: `no-google-guide`。Google `styleguide` 主仓库没有独立 C 语言指南；快照中的 `google-c-style.el` 只是编辑器配置，不能冒充规范正文。
- C 代码必须先声明 C 标准、ABI、编译器和告警基线；这些项目事实高于本文件的 MAY 选择。
- C 头文件必须先通过 [C 或 C++ 头文件判定](c-or-cpp-header.md)，未经判定不得套用 C++ 的类、异常、RTTI 或智能指针规则。

| 检查层 | 必须证明的内容 | 推荐证据 |
|---|---|---|
| 语言版本 | C11/C17 等版本与扩展 | 构建文件、编译命令 |
| 接口契约 | 所有权、容量、生命周期、错误码、线程安全 | 头文件文档、测试 |
| 内存与边界 | 分配、I/O、字符串和整数边界均处理失败 | 静态分析、Sanitizer、负例测试 |
| 工具 | 格式、告警和测试实际执行 | 命令退出码 |

没有专门 Google C Guide 的条款必须标记 `external-source` 或 `no-google-guide`，不能写成“Google 要求”。
