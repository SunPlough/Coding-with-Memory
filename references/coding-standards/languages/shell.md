# Shell

来源：<https://google.github.io/styleguide/shellguide.html>（Google Shell Style Guide）

## 规则

- **MUST** 明确解释器（通常 `#!/bin/bash`）和文件扩展名；非 Bash 脚本不得偷偷使用 Bash 专属语法。
- **SHOULD** 使用 2 个空格缩进、行宽 80；复杂命令换行时以管道或逻辑运算符开头并保持层级清楚。
- **MUST** 正确引用变量、命令替换和路径；默认使用 `"$var"`、`"$(command)"` 和 `"$@"`，不要用未引用的 `$*` 传递参数。
- **SHOULD** 在脚本开头按项目约定启用 `set -euo pipefail`，并逐项验证外部命令失败、空值和管道状态。
- **MUST NOT** 使用 `eval` 拼接不受信任输入；破坏性命令必须验证目标范围，并支持 dry-run 时优先提供预览。
- **SHOULD** 函数注释说明 Globals、Arguments、Outputs 和 Returns；实现注释解释副作用原因，不翻译命令。
- **MUST** 使用 ShellCheck；TODO 带可追踪 Issue 和完成条件。

## 验证

```bash
shellcheck <changed-shell-files>
bash -n <changed-shell-files>
```
## 严格执行清单

### 官方章节覆盖

必须读取 `upstream/google-styleguide/shellguide.md`：

| 官方章节 | 必查主题 |
|---|---|
| Shell Files and Interpreter Invocation | shebang、解释器、文件名和 Bash 兼容 |
| Environment | 环境变量、路径、临时目录和依赖 |
| Comments | 文件/函数注释、Globals、Arguments、Outputs、Returns |
| Formatting | 2 空格、80 列、换行、引用和命令布局 |
| Features and Bugs | ShellCheck、命令替换、test、字符串、glob、eval、数组、管道和算术 |
| Aliases / Naming Conventions | alias、函数、变量、常量、文件名、局部变量和 main |
| Calling Commands | 返回值、内置命令和外部命令 |
| When in Doubt | 局部一致性和例外边界 |

`shellcheck`、`bash -n` 和测试分别记录；任何破坏性命令必须人工验证目标范围和失败路径。
