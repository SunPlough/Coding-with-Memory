# Markdown

来源：<https://google.github.io/styleguide/docguide/style.html>（Google Markdown Style Guide）

## 规则

- **MUST** 使用一个唯一 H1；标题采用 ATX 风格并按层级递进，不跳级；标题使用一致的 Title Case/句式。
- **SHOULD** 在长文档中使用 `[TOC]`，放在介绍之后；每个标题名称完整、唯一且能表达章节内容。
- **MUST** 使用显式链接文本和仓库内明确路径；链接文本不能写“点击这里”，外部链接需要可访问并避免泄漏私人 URL。
- **MUST** 为代码围栏写语言标识；示例代码应可运行或明确标注伪代码，命令不得包含秘密。
- **SHOULD** 使用 Markdown 原生语法而非 HTML；列表、表格、标题和代码围栏前后保留必要空行。
- **MUST** 去除行尾空格；单行默认不超过 80 列，URL、表格和代码可按可读性例外。
- **SHOULD** 图片提供有意义的 alt 文本；表格只用于字段关系，不用空格伪造布局。

## 验证

```bash
prettier --check <changed-markdown-files>
markdownlint <changed-markdown-files>
lychee <changed-markdown-files>  # 若仓库配置链接检查
```
## 严格执行清单

### 官方章节覆盖

必须读取 `upstream/google-styleguide/docguide/style.md` 与 `docguide/best_practices.md`：

| 正文 | 必查主题 |
|---|---|
| style.md | 最小文档、标题和大小写、布局、TOC、行宽、尾随空白、列表、代码围栏、链接、图片、表格和避免 HTML |
| best_practices.md | 随代码更新文档、删除死文档、避免重复、记录代码故事和最小可用文档 |
| philosophy.md | 文档的目的和读者边界 |

每个链接、代码围栏、标题层级、表格和图片 alt 都要绑定到具体文件证据；Markdown 渲染成功不能证明链接可达或内容与实现同步。
