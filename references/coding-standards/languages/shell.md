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
