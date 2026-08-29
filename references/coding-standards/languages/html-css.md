# HTML/CSS

来源：<https://google.github.io/styleguide/htmlcssguide.html>（Google HTML/CSS Style Guide）

## 规则

- **MUST** 使用 UTF-8；HTML 元素、属性和 CSS 属性使用小写；HTML 文档提供 `<!doctype html>` 和有效的 `lang`。
- **MUST** 在资源提供 HTTPS 时为嵌入式图片、媒体、样式表和脚本使用 HTTPS；资源确实不提供 HTTPS 时，必须记录例外原因，不使用协议相对 URL。
- **MUST** 保持 2 个空格缩进、每行一个结构关注点；属性按可读性分行，避免为了视觉对齐加入无意义空格。
- **MUST** 使用语义元素表达结构；可交互元素优先使用原生 `<button>`、`<a>`、`<input>` 等，不用 `div` 模拟控件。
- **MUST** 为图片提供有意义的 `alt`，为表单控件提供可访问名称；键盘焦点、顺序和错误状态必须可观察。
- **SHOULD** 使用小写短横线 CSS 类名；避免 ID 作为样式钩子、避免 `!important` 和深层选择器；复用项目 Design Token。
- **SHOULD** 将结构、样式和行为分离；脚本加载、资源路径和第三方内容遵循 CSP、性能和许可证约束。
- **MUST** 明确响应式断点、溢出、文本换行和加载失败状态；不得用隐藏溢出掩盖内容不可见。
- **SHOULD** 通过 CSS Formatter/Lint、HTML 校验、可访问性扫描和真实浏览器测试验证变更。

## 验证

```bash
npx --no-install prettier --check <changed-html-css-files>
npx --no-install stylelint <changed-css-files>
npx --no-install html-validate <changed-html-files>
npm test
```
## 严格执行清单

### 官方章节覆盖

来源为 `upstream/google-styleguide/htmlcssguide.html`，按以下章节逐项审查：

| 官方章节 | 必查主题 |
|---|---|
| General | HTTPS 协议、UTF-8、缩进、大小写、尾随空白、注释和 action item |
| HTML | doctype、有效性、语义、媒体 fallback、关注点分离、实体引用、可选标签、type 和 id 属性、换行与引号 |
| CSS | 有效性、类/id 命名、前缀、type/id 选择器、缩写属性、零值单位、前导零、十六进制、`!important`、hack、声明顺序和注释 |

HTML/CSS 格式化器只能证明排版；语义、资源协议、可访问性、内容溢出和浏览器行为必须通过校验器、可访问性扫描和真实浏览器测试分别记录。
