# XML

来源：<https://google.github.io/styleguide/xmlstyle.html>（Google XML Style Guide）

## 规则

- **MUST** 使用 UTF-8、明确 XML declaration、统一 2 个空格缩进和元素大小写；不得混用空格与 Tab。
- **MUST** 保持元素和属性命名、命名空间、顺序和 Schema 契约稳定；外部实体、DTD 和 XPath 输入按安全规则处理。
- **SHOULD** 属性值使用双引号，特殊字符正确转义；文本内容与属性选择依据语义而非排版便利。
- **MUST NOT** 手改生成 XML，除非生成器、Schema 和版本化流程允许；生成文件变更需说明生成命令。
- **SHOULD** 为公共 XML Schema/配置文档记录元素用途、必需性、默认值、兼容性和未知字段行为。

## 验证

```bash
xmllint --noout <changed-xml-files>
xmllint --schema <schema.xsd> --noout <changed-xml-files>
```
