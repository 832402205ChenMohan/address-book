# Code Standard

本仓库遵循的编码规范，供代码复审与博客中的「代码规范链接」引用。

## Python

- 遵循 [PEP 8](https://peps.python.org/pep-0008/)，单行不超过 100 字符。
- 命名：模块/函数/变量 `snake_case`，类 `PascalCase`，常量 `UPPER_CASE`。
- 每个模块、每个公开函数都写 docstring，说明职责与返回值；复杂分支用行内注释解释「为什么」而不是「是什么」。
- 类型提示：函数签名标注参数与返回类型，对外返回的字典用 `dict[str, Any]` 表达。
- 校验失败统一抛 `models.ValidationError`，由 `app.py` 的 `errorhandler` 转成 400 JSON，不在业务层拼 HTTP 响应。
- SQL 只写在 `models.py` 与 `database.py`（`excel_io.py` 只通过 models 的函数访问数据），禁止在视图层直接写 SQL。
- 表名、字段名小写下划线风格；所有外键显式声明并在连接上开启 `PRAGMA foreign_keys = ON`。

## 前端

- 原生 ES6，不用框架、不加构建步骤；一个模块一个职责（`app.js` 只做渲染与请求）。
- 变量命名 `camelCase`；DOM 节点集中在 `el` 对象里统一取，避免散落的 `document.getElementById`。
- 所有请求走 `api()` 统一封装，非 2xx 与业务错误都用 `toast()` 反馈，不静默失败。
- CSS 用 `--变量` 管理配色与圆角，类名 `block-element` 语义化，避免深层嵌套选择器。

## 数据与文件

- 数据库文件、导出的 xlsx、虚拟环境目录都进 `.gitignore`，仓库只放代码、文档、测试与截图。
- 示例数据由 `scripts/seed_demo.py` 生成，保证任何机器 clone 后一条命令即可复现演示效果。

## Git

- 提交信息采用 `type(scope): summary` 形式，例如 `feat(excel): support tagged method import`；type 取 `feat`/`fix`/`test`/`docs`/`refactor`/`chore`。
- 一次提交只做一件事；提交前跑 `python -m pytest -q`，必须全绿。
