# Java

来源：<https://google.github.io/styleguide/javaguide.html>（上游 `1809c769de31ba388c755ad15dd057a9ba8531fd`）

## 规则

- **MUST** 使用 UTF-8；每行一个语句；2 个空格缩进、禁止 Tab；列宽上限 100；左大括号不换行，右大括号与 `else/catch/finally` 同行。
- **MUST** 按 `package`、静态导入、非静态导入、类声明的顺序组织文件；静态导入和普通导入分别成组，并按 ASCII 字典序排列。
- **MUST** 使用 Google Java Format 或仓库批准的等价格式化器；不要手工维护与格式化器冲突的例外。
- **SHOULD** 使用完整、可读的 `UpperCamelCase` 类/接口、`lowerCamelCase` 方法/变量、`CONSTANT_CASE` 常量；缩写按一个单词处理，如 `XmlParser` 而不是 `XMLParser`。
- **MUST** 为覆盖方法添加 `@Override`；不要忽略捕获到的异常，若确实无需处理也必须说明原因并使用项目批准的记录方式。
- **MUST NOT** 使用 finalizer；资源使用 `try-with-resources` 或项目的生命周期工具显式管理。
- **MAY** 使用 `final` 表达不会重新赋值的局部变量、参数和字段；是否统一添加由项目规则决定，不把个人偏好当成 Google 硬规则。
- **SHOULD** 让类职责聚焦，公共 API 的可见性、线程安全、异常和 null 语义在 Javadoc 中可被调用者依赖。
- **MUST** 公共类、方法、字段和复杂类型提供 Javadoc；第一句是简洁的 summary fragment，不重复名称或显然实现。
- **SHOULD** 优先使用不可变值对象和窄接口；避免为未来扩展预留空泛的基类、工厂或兼容层。

## 验证

```bash
google-java-format --dry-run <changed-java-files>
./gradlew check                 # Gradle 项目
mvn -DskipTests=false verify   # Maven 项目
```

具体静态分析工具以仓库配置为准；未发现的工具标记 `not-found`。
