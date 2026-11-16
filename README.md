# Address Book

一个用于软件工程课程「极限编程」作业的通讯录 Web 应用：支持收藏联系人、一个联系人挂多种联系方式、以及与 Excel 的双向导入导出。

仓库地址：<https://github.com/832402205ChenMohan/address-book>

## 功能与评分点对照

| 作业要求 | 分值 | 本项目实现 | 所在位置 |
| --- | --- | --- | --- |
| 收藏联系人 | 25 | 卡片右上角星标，一键收藏/取消，支持「仅看收藏」筛选 | `static/js/app.js`、`models.set_favorite` |
| 添加多种联系方式 | 10 | 每个联系人可挂多条 phone / email / wechat / address / other，各带自定义标签 | `models.normalise_payload`、`templates/index.html` |
| 导入与导出 | 25 | 导出真实 xlsx（一人一行、每类信息一列）；导入按表头识别列并合并 | `excel_io.py` |
| Web 部署（可选） | +15 | 提供云服务器部署脚本与步骤 | `docs/DEPLOY.md` |
| 页面样式 | 10 | 完整视觉设计：卡片栅格、状态统计、弹窗表单、Toast 提示 | `static/css/style.css` |

## 技术栈

- 后端：Python 3.13 + Flask 3.1
- 数据库：SQLite（`data/addressbook.db`，首次启动自动建表）
- Excel：openpyxl 3.1
- 前端：原生 HTML / CSS / JavaScript（无框架、无构建步骤）
- 测试：pytest

## 目录结构

```
address-book/
├── app.py                 # Flask 应用：页面路由 + JSON API
├── database.py            # SQLite 连接与建表
├── models.py              # 校验、增删改查、收藏、统计
├── excel_io.py            # Excel 导入导出
├── requirements.txt
├── scripts/seed_demo.py   # 插入示例数据
├── templates/index.html   # 页面骨架
├── static/css/style.css   # 样式
├── static/js/app.js       # 前端逻辑
├── tests/test_app.py      # 12 个自动化测试
├── docs/                  # 博客草稿、PSP、部署与操作步骤
└── screenshots/           # 运行截图与演示视频
```

## 快速开始

```powershell
cd address-book
python -m venv .venv
.\.venv\Scripts\Activate.ps1        # PowerShell
python -m pip install -r requirements.txt

python scripts\seed_demo.py         # 可选：插入示例数据
python -m pytest -q                 # 运行测试，应为 12 passed
python app.py                       # 启动服务
```

浏览器打开 <http://127.0.0.1:5000> 即可使用。

## API 一览

| 方法 | 路径 | 说明 |
| --- | --- | --- |
| GET | `/` | 通讯录页面 |
| GET | `/api/contacts?q=&favorite=1` | 查询联系人（支持关键字与收藏过滤） |
| POST | `/api/contacts` | 新建联系人 |
| PUT | `/api/contacts/<id>` | 更新联系人（整体替换联系方式） |
| DELETE | `/api/contacts/<id>` | 删除联系人（级联删除其联系方式） |
| POST | `/api/contacts/<id>/favorite` | 收藏/取消收藏（`{"favorite": true/false}`） |
| GET | `/api/export` | 导出 `contacts.xlsx` |
| GET | `/api/template` | 下载空白导入模板 |
| POST | `/api/import` | 上传 xlsx 导入（表单字段 `file`） |
| GET | `/healthz` | 健康检查，部署时用 |

## Excel 格式约定

- 行：一个联系人一行。列：`Name`、`Company`、`Title`、`Notes`、`Favorite`，之后是 `Phone 1`、`Phone 2`、`Email 1`、`WeChat 1`、`Address 1`、`Other 1`……
- 导出时按实际数据动态决定每类占几列（至少 1 列），表头带底色并冻结首行。
- 导入按表头文字识别列，大小写与空格不敏感；无法识别的列会被忽略，若整表都没有可识别列则提示错误。
- 导入时同名联系人会合并：保留原有联系方式，追加新的，不产生重复记录。
- 单元格内可用 `;` 或换行分隔多条同类型信息；`13800000000 (mobile)` 这种写法会把括号内容识别为标签。

## 测试

```powershell
python -m pytest -q
```

覆盖：页面渲染、新建/查询/更新/删除、收藏切换、按联系方式搜索、导出列结构、导出→导入往返、同名合并、缺名跳过、无表头报错。
