# Rust

来源：<https://google.github.io/styleguide/rust/>（独立 Google Rust Style Guide，`external-source`，不属于 `google/styleguide` 主仓库快照；若上游内容不可用，遵循仓库 rustfmt/Clippy 配置）

## 规则

- **MUST** 使用 `rustfmt` 和仓库锁定的 Rust edition；不提交格式化器无法稳定重现的手工排版。
- **MUST** 让所有权、借用和生命周期由类型表达；避免不必要的 `clone()`、`Rc<RefCell<_>>` 和 `'static` 泄漏。
- **SHOULD** 使用 `Result`/`Option` 和 `?` 传播错误；不要用 `unwrap`/`expect` 处理外部输入，除非不变量有明确证据。
- **SHOULD** 优先枚举、迭代器和小型 trait；不为未来场景新增泛型层、宏或异步抽象。
- **MUST** 公共项提供 rustdoc，说明 panic、错误、线程安全、生命周期和特性开关语义。
- **SHOULD** 遵循 `snake_case` 函数/模块、`UpperCamelCase` 类型、`SCREAMING_SNAKE_CASE` 常量；避免缩写。
- **MUST** 处理 Clippy 警告；允许的 lint 例外必须最小化并在行或块附近说明原因。

## 验证

```bash
cargo fmt --all -- --check
cargo clippy --all-targets --all-features -- -D warnings
cargo test --all-features
```
## 严格执行清单

### 外部官方来源边界

Rust 不在 `google/styleguide` 主仓库中。本文件使用独立的 <https://google.github.io/styleguide/rust/>，状态为 `external-source`；固定提交的 Google 主仓库快照不包含 Rust 正文。仓库若采用其他 Rust 官方规范，必须在项目覆盖文件中记录来源和版本。

### 逐项检查域

必须分别审查 rustfmt、命名和模块、所有权/借用/生命周期、错误与 panic、trait/generic、unsafe、并发、公共 rustdoc、Clippy 和测试。编译成功不能替代 Clippy、rustdoc、unsafe 边界和线程安全证据；`unwrap`、`expect`、`unsafe` 和 lint 例外必须绑定不变量或安全证明。
