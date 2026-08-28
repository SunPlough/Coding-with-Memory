# JSON

来源：<https://google.github.io/styleguide/jsoncstyleguide.xml>（Google JSON Style Guide）

## 规则

- **MUST** 把 JSON 当作 API 数据契约；严格 JSON 对象中禁止注释、尾逗号、函数、变量和 JavaScript 表达式。
- **MUST** 使用双引号包裹所有属性名和字符串值；布尔值、数字、对象、数组和 `null` 保持原生 JSON 类型。
- **MUST** 使用有明确语义的 ASCII camelCase 属性名；数组属性通常使用复数，单值属性通常使用单数。
- **SHOULD** 不为方便而任意嵌套；只有表示一个有语义的结构（例如地址）时才保留对象层级。
- **SHOULD** 谨慎发送空值和 `null`；若缺失与 `null` 语义相同则省略，若 `0`、`false` 或 `null` 有明确业务语义则保留并写入 Schema。
- **MUST** 用字符串表达可扩展枚举值，避免用整数序号让客户端依赖顺序。
- **MUST** 对日期、时间、时长、字节和大整数使用 API Schema 声明的字符串格式；不要依赖 JavaScript `number` 精确表示所有整数。
- **SHOULD** 区分普通对象与 map；map 的 key 可以不同于普通属性命名规则，但必须在接口文档中明确。
- **MUST** 变更公共字段时检查兼容性、版本和未知字段处理；不得把用户偏好或未批准字段偷偷写入 API 契约。

## 验证

```bash
python -m json.tool <file.json>
npx prettier --check <changed-json-files>  # 若仓库使用 Prettier
<project-schema-validator> <changed-json-files>
```

`jsonc` 只有在消费者明确支持时使用；不要把 JSONC 注释文件当作严格 JSON API 发送。
