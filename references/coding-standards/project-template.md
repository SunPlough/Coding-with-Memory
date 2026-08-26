# 项目覆盖模板

需要项目专属规则时，将以下结构写入仓库 `coding-standards/project.md` 或项目约定的位置。

```yaml
version: 1
scope: "repo or path glob"
owner: "team or maintainer"
review_after: "YYYY-MM-DD"
source: "issue, ADR, or review link"
comment_policy:
  language: "zh-CN|en|inherit-by-path"
  public_api_language: "zh-CN|en|inherit"
  todo_reference_pattern: "PROJ-[0-9]+ or repository convention"
  documentation_tool: "Javadoc|KDoc|TSDoc|Google docstring|Go Doc|none"
overrides:
  - rule: "precise local rule"
    reason: "why the Google/base rule is insufficient here"
    applies_to: ["path/glob"]
    verification: "command or review check"
```

覆盖必须范围窄、可验证，并能追溯到团队决策。不要在这里放个人沟通偏好。

注释语言属于仓库规则，应从项目政策和相邻源码确定；不得从用户对话语言推断。
