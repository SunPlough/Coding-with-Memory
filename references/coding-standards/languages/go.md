# Go

来源：<https://google.github.io/styleguide/go/>（Google Go Style Guide）

## 规则

- **MUST** 使用 `gofmt`；不得手工维护与格式化器相冲突的空白。长行没有固定硬折断限制，但换行必须服务于可读性。
- **MUST** 使用 `MixedCaps`/`mixedCaps`，不使用下划线命名；缩写保持一致（如 `HTTPServer`），包名简短、全小写且不含下划线。
- **SHOULD** 优先清晰、简单、简洁和可维护；当局部一致性与抽象洁癖冲突时，选择读者更容易验证的写法。
- **MUST** 立即检查并返回错误；不要用空白标识符丢弃错误，也不要把 panic 当作普通错误流。
- **SHOULD** 让包职责集中，接口保持最小；不要为测试替身或未来扩展预先创建接口层。
- **SHOULD** 通过 `defer` 管理成对资源释放，并明确 goroutine 的所有权、退出条件和取消路径。
- **MUST** 对导出的包、类型、函数和方法提供 Go doc；注释以被记录对象名称开头，并说明调用者可依赖的行为。
- **SHOULD** 使用表驱动测试覆盖边界和错误路径；新增并发代码在可用时运行 Race Detector。
- **MUST** 直接导入使用的包，不依赖间接导入；模块版本、生成代码和工具链版本以仓库声明为准。

## 验证

```bash
gofmt -l .
go vet ./...
go test ./...
go test -race ./...  # 项目支持并发时
```
