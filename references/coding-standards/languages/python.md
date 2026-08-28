# Python

来源：<https://google.github.io/styleguide/pyguide.html>（上游 `1809c769de31ba388c755ad15dd057a9ba8531fd`）

本文件提炼 Google Python Style Guide 的可执行规则；完整背景、例外和示例以上游原文为准。

## 规则

- **MUST** 使用 `pylint` 或仓库等价 Lint；格式化器、导入排序器和类型检查沿用仓库配置。
- **MUST** 使用 4 个空格缩进、禁止 Tab；单行最多一个语句；默认行宽 80 列，超长字符串、URL 和必要的导入可按上游例外处理。
- **MUST** 使用模块/包导入，不从模块导入单个类或函数；导入顺序按标准库、第三方、内部模块分组，并保持每组字典序。
- **MUST NOT** 使用可变对象作为默认参数；用 `None` 后在函数体内初始化。
- **MUST NOT** 用 `assert` 替代参数校验或生产逻辑；断言只能表达不应发生且可安全移除的内部不变量。
- **SHOULD** 只使用简单的列表/字典/集合推导式；禁止多个 `for` 或多个过滤条件叠在一个推导式中，复杂逻辑改用循环。
- **SHOULD** 使用内置异常类型或项目定义的具体异常，不能吞掉异常；异常处理应说明恢复、转换或重新抛出的原因。
- **SHOULD** 使用 `with` 管理文件、Socket、数据库连接等有状态资源；不得依赖析构函数及时释放资源。
- **MUST** 使用三引号模块/函数/类 docstring；公共 API、非显然逻辑和有副作用的函数必须说明调用契约。
- **SHOULD** 使用描述性命名：模块 `lower_with_underscore.py`、类 `CapWords`、函数和变量 `lower_with_underscore`、常量 `ALL_CAPS`；避免不熟悉缩写和类型后缀。
- **SHOULD** 入口放在 `main()`，并使用 `if __name__ == '__main__':`，保证模块可导入和测试。
- **SHOULD** 保持函数聚焦；函数超过约 40 行时检查是否能拆分，但不为指标机械切碎。
- **SHOULD** 给公共 API 和容易发生类型错误的稳定代码添加类型标注；可为 `None` 的值显式写成 `X | None`。
- **MUST** 延续文件既有 docstring/注释风格；TODO 必须带可追踪资源和完成条件，不能写裸 `TODO`。

## 验证

```bash
pylint <changed-python-files>
ruff format --check <changed-python-files>  # 若仓库使用 Ruff
ruff check <changed-python-files>           # 若仓库使用 Ruff
python -m compileall <changed-python-files>
```

工具不存在时报告 `not-found`，不要把人工阅读结果伪装成 Formatter/Lint 通过。
