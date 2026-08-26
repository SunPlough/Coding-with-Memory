# Rust

来源：https://google.github.io/styleguide/rust/

使用仓库的 `rustfmt` 与 Clippy 配置。保持所有权和生命周期表达直接，错误类型与边界明确；优先标准库和当前项目模式，不为未来场景增加 Trait、泛型层或异步抽象。

检查：`cargo fmt --all -- --check`、Clippy、测试、已配置的 Miri/Sanitizer 和依赖审计。
