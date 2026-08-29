# 代码规范索引

按层组合规范：

```text
base.md
  + languages/<language>.md
  + comments/{chinese-comments,language-formats}.md
  + frameworks/<framework>.md
  + project-template.md 对应的仓库覆盖规则
```

严格执行时必须先读取 [严格执行协议](strict.md)。它要求读取固定版本的 Google 官方全文快照，按章节记录检查状态，不得只依据下方语言摘要判断合规。

语言文件负责路由和项目化执行清单；固定版本的官方全文镜像位于 `upstream/google-styleguide/`，文件清单和哈希位于 [upstream-manifest.json](upstream-manifest.json)。每条规则必须保留来源章节、规范等级、适用范围和验证方式；需要完整背景时读取本地快照，而不是只看摘要。审查前先运行 `scripts/verify_upstream.py`。

只加载当前变更路径适用的文件。修改源码时必须加载 [注释规范](comments/index.md)。Google Style Guides 是默认语言来源；注释层补充跨语言语义和中文写作要求，不替代语言工具的格式规则。

## 优先级

```text
安全与合规 > 项目覆盖 > 框架/语言格式 > 注释语义 > 通用基线 > 用户偏好
```

项目覆盖必须声明作用域、原因、所有者和复核日期。用户偏好永远不是规范覆盖；仓库已有源码注释语言高于个人沟通语言偏好。

## 路由方法

1. 使用 [language-map.yaml](language-map.yaml) 根据路径识别语言。
2. `.h` 无法单独判断 C 或 C++，先读取 [c-or-cpp-header.md](languages/c-or-cpp-header.md)。
3. 加载一个或少数几个实际相关的语言文件，不批量加载整个目录。
4. 从依赖清单和现有源码确认框架，再按需加载 [框架索引](frameworks/index.md)。
5. 先应用语言文件的 MUST，再应用项目覆盖；发现冲突按上方优先级处理并记录原因。
6. 工具可表达的规则交给 Formatter/Lint/Compiler；工具不能表达的契约由 Agent 在 diff 审查中举证。

## 语言覆盖

| 本地规则 | Google/官方上游 | 状态 |
|---|---|---|
| `cpp.md` | C++ | 可用 |
| `csharp.md` | C# | 可用 |
| `dart.md` | Effective Dart | `external-source`，不是主仓库快照 |
| `go.md` | Go | 可用 |
| `html-css.md` | HTML/CSS | 可用 |
| `java.md` | Java | 可用 |
| `javascript.md` | JavaScript | 可用 |
| `json.md` | JSON | 可用 |
| `lisp.md` | Common Lisp | 仅 Common Lisp 使用 Google 细则；其他方言走项目/官方规则 |
| `markdown.md` | Markdown 文档 | 可用 |
| `objective-c.md` | Objective-C | 可用 |
| `python.md` | Python | 可用 |
| `r.md` | R | 可用 |
| `rust.md` | Google Rust Style Guide | `external-source`，不是主仓库快照 |
| `shell.md` | Shell | 可用 |
| `typescript.md` | TypeScript | 可用 |
| `vimscript.md` | Vimscript | 可用 |
| `xml.md` | XML | 可用 |
| `swift.md` | Google Swift Guide | `external-source`，独立 Google 仓库 |
| `kotlin.md` | Android Kotlin Style Guide | `external-source`，独立 Android 来源 |
| `c.md` | 无专门 Google C Guide | 必须由项目规则补充 |

固定上游版本、官方 URL 和许可说明见 [来源](sources.md)。
