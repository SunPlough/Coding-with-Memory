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
