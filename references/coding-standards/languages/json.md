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
npx --no-install prettier --check <changed-json-files>  # 若仓库使用 Prettier
<project-schema-validator> <changed-json-files>
```

`jsonc` 只有在消费者明确支持时使用；不要把 JSONC 注释文件当作严格 JSON API 发送。
## 严格执行清单

### 官方章节覆盖

必须读取 `upstream/google-styleguide/jsoncstyleguide.xml`，并按正文的属性、类型、数组、空值、分页、错误和兼容章节审查。渲染入口 `jsoncstyleguide.html` 只用于定位，不替代 XML 正文。

| 检查域 | 必须证明的内容 |
|---|---|
| 语法 | 严格 JSON，无注释、尾逗号、函数或表达式 |
| 命名与结构 | 属性命名、单复数、嵌套边界、map 与普通对象区分 |
| 类型与空值 | 字符串、数字、布尔、数组、对象和 null 语义稳定 |
| API 契约 | 日期/时长/大整数格式、枚举可扩展性、未知字段和兼容策略 |
| 变更验证 | Schema、消费者兼容性、版本和错误响应均有证据 |

JSON 不能用注释承载契约；需要说明时更新 Schema、接口文档或测试，不把 JSONC 当作严格 JSON。
