# C 或 C++ 头文件

来源：C/C++ 语言判定流程；C++ 细则见 <https://google.github.io/styleguide/cppguide.html>，C 没有对应的 Google Style Guide。

仅凭 `.h` 扩展名无法判断头文件属于 C 还是 C++。先检查引用它的源码、构建目标、编译器和项目约定，再加载 `c.md` 或 `cpp.md`。默认不得把 C++ 专属规则应用到 C 头文件。

## 判定顺序

1. 查看目标的编译器和标准选项（如 `-std=c11` 或 `-std=c++20`）。
2. 查看 include 它的 `.c`/`.cc`/`.cpp` 文件以及构建系统 target。
3. 查看头文件是否使用 `namespace`、模板、类、引用或其他 C++ 语法。
4. 证据仍冲突时先询问，不把 C++ 所有权、异常和 RTTI 规则套到 C 项目。
