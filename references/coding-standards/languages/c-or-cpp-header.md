# C 或 C++ 头文件

来源：C/C++ 语言判定流程；C++ 细则见 <https://google.github.io/styleguide/cppguide.html>，C 没有对应的 Google Style Guide。

仅凭 `.h` 扩展名无法判断头文件属于 C 还是 C++。先检查引用它的源码、构建目标、编译器和项目约定，再加载 `c.md` 或 `cpp.md`。默认不得把 C++ 专属规则应用到 C 头文件。

## 判定顺序

1. 查看目标的编译器和标准选项（如 `-std=c11` 或 `-std=c++20`）。
2. 查看 include 它的 `.c`/`.cc`/`.cpp` 文件以及构建系统 target。
3. 查看头文件是否使用 `namespace`、模板、类、引用或其他 C++ 语法。
4. 证据仍冲突时先询问，不把 C++ 所有权、异常和 RTTI 规则套到 C 项目。
## 严格执行清单

本文件是 `.h` 文件的强制路由门禁，不是 C++ 规范的替代品。判定完成前，状态只能是 `manual-review`。

| 判定证据 | C | C++ |
|---|---|---|
| 编译器/标准 | `cc -std=c11/c17` 等 | `c++ -std=c++20` 等 |
| 语法信号 | 预处理器、C 链接约定 | namespace、模板、类、引用、重载 |
| 构建归属 | C target 或 C API | C++ target 或 C++ API |
| 规范来源 | `c.md`，状态 `no-google-guide` | `cpp.md` + `upstream/google-styleguide/cppguide.html` |

只有在证据一致后才能加载对应文档；不能因文件扩展名、个人习惯或历史命名直接决定语言。
