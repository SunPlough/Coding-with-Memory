# Vimscript

来源：<https://google.github.io/styleguide/vimscriptguide.xml>（Google Vimscript Style Guide）

## 规则

- **MUST** 使用 2 个空格缩进、80 列、禁止 Tab、操作符周围留空格；续行缩进 4 个空格且不对齐命令参数。
- **MUST** 明确变量作用域前缀：全局 `g:`、脚本局部 `s:`、参数 `a:`、局部 `l:`、缓冲区 `b:`、内置 `v:`。
- **MUST** 使用 `=~#`/`=~?` 明确大小写匹配，正则默认加 `\\m\\C`；不要依赖用户的 `ignorecase`、`smartcase` 或 `nomagic` 设置。
- **MUST** 使用 `normal!` 而不是依赖用户映射的 `normal`；优先使用副作用更小的函数替代命令。
- **SHOULD** 在 `autoload/` 定义带 `[abort]` 的函数，避免全局函数；命令放在 `plugin/commands.vim` 并避免静默覆盖用户命令。
- **MUST** 将自动命令放入唯一 augroup，先 `autocmd!` 再定义，保证插件可重复加载。
- **SHOULD** 用错误码而非本地化错误文本判断失败；严格检查类型，避免 `0 == 'foo'` 等隐式比较。

## 验证

```bash
vim -Nu NONE -n -es -V1 -c 'set nomore' -c 'source <file.vim>' -c 'qa!'
```
## 严格执行清单

### 官方章节覆盖

必须读取 `upstream/google-styleguide/vimscriptguide.xml` 和需要完整背景时的 `vimscriptfull.xml`，逐项审查作用域、命名、缩进、空白、正则、命令、自动命令、错误、兼容性和测试。短版用于路由，full 版用于无法由短版定位的条款。

`normal!`、唯一 augroup、作用域前缀、大小写敏感正则和 `abort` 是可观察行为，不能由 Vim 解析成功替代。对用户映射、全局选项、缓冲区副作用和插件重复加载必须提供人工证据。
