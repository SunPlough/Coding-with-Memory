# Rust

来源：<https://google.github.io/styleguide/rust/>（Google Rust Style Guide；若上游内容不可用，遵循仓库 rustfmt/Clippy 配置）

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
