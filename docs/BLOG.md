# 极限编程作业 —— 通讯录（Flask + SQLite + Excel 导入导出）

> 软工 2601 班 / 福州大学—梅努斯国际工程学院 · 个人项目
>
> **发布前请替换**：`{{学号}}`（其余占位符已填好：GitHub 仓库地址已写入本文）；把 `screenshots/` 里的图片用 CSDN 编辑器「上传图片」重新插入（相对路径在 CSDN 不显示）；云部署为可选项，若不做，第七节保持现状即可。

## 作业说明表

| 项目 | 内容 |
| --- | --- |
| 本次作业所属课程 | 软件工程（FZU–MU） |
| 团队名称 | 个人项目（陈墨瀚，学号：`{{学号}}`） |
| 作业要求 | 极限编程（Extreme Programming）：实现通讯录的收藏联系人、一个联系人多种联系方式、Excel 导入导出；可选云部署 |
| 本次作业的目标 | 在 4 天窗口内独立走完"需求拆分 → 设计 → 编码 → 测试 → 部署 → 文档"的完整流程，重点验证能否把需求逐条落成可验收的功能点，并用自动化测试与截图证明结果可复现 |
| 其他参考资料 | GitHub 仓库：https://github.com/832402205ChenMohan/address-book ；代码规范：https://github.com/832402205ChenMohan/address-book/blob/main/docs/CODE_STANDARD.md ；Flask 官方文档；openpyxl 官方文档 |

## 目录

- [一、需求拆解：把作业要求翻成验收点](#一需求拆解把作业要求翻成验收点)
- [二、项目地址](#二项目地址)
- [三、功能实现思路](#三功能实现思路)
- [四、程序截图](#四程序截图)
- [五、完整运行视频](#五完整运行视频)
- [六、Git 提交历史与提交次数](#六git-提交历史与提交次数)
- [七、云部署（可选加分项）](#七云部署可选加分项)
- [八、PSP 表格](#八psp-表格)
- [九、开发过程中遇到的问题与解决](#九开发过程中遇到的问题与解决)
- [十、对照评分标准自查](#十对照评分标准自查)

---

## 一、需求拆解：把作业要求翻成验收点

作业只给了功能名，没给交互细节。我的做法是先把每条要求写成"能截图验收的一句话"，再按验收点倒推数据结构和接口。四个功能点最后落成这样：

| 作业要求 | 我定义的验收点 |
| --- | --- |
| 1.1 收藏联系人（25 分） | 任意联系人都能被标记/取消标记为收藏；收藏后在列表里能一眼看出；可以只看收藏的人；收藏状态导出到 Excel 后仍保留 |
| 1.2 多种联系方式（10 分） | 一个联系人至少能挂 3 条电话、2 条邮箱，并各自带标签（mobile / office / work）；不同类型的联系方式在卡片上用不同色块标签区分 |
| 1.3 导入导出（25 分） | 导出必须是真正的 .xlsx：一人一行、同类信息各占一列（`Phone 1`/`Phone 2`…），带表头样式；导入能识别这些列并还原成带标签的联系方式；同名联系人不重复建 |
| 1.4 云部署（+15 分） | 公网 IP 或域名能打开，不是 localhost |

这里有一个容易忽略的坑：作业写的是"每种信息占一列"，但一个人可能有 3 个电话。如果只留一列 `Phone`，导出就丢数据；如果固定留 3 列，只有 1 个电话的人就有空白列。我最终选了**按实际数据动态决定列数**（见 3.4），既满足"每类一列"的字面要求，也不丢数据。

## 二、项目地址

- GitHub 仓库：https://github.com/832402205ChenMohan/address-book
- 云部署访问地址：未部署（可选加分项 +15，部署方案见仓库 `docs/DEPLOY.md`；完成后把公网地址填到这里）
- 代码规范文档：https://github.com/832402205ChenMohan/address-book/blob/main/docs/CODE_STANDARD.md

![仓库概览](screenshots/08b-repo-overview.png)
- 演示视频：见第五节

## 三、功能实现思路

### 3.1 为什么这样分层

整个项目只有 4 个 Python 模块 + 3 个前端文件，但分层是刻意做的：

```
浏览器 (index.html + app.js + style.css)
        │  fetch JSON / multipart
        ▼
app.py          视图层：只管 URL、取参数、返回 JSON / 文件，不写 SQL
        │
models.py       业务层：校验、增删改查、收藏、统计
excel_io.py     文件层：xlsx 读写，只通过 models 的函数动数据
        │
database.py     数据层：SQLite 连接、建表、外键开关
```

理由有两条：

1. **测试能绕过浏览器**。`tests/test_app.py` 用 Flask 的 `test_client` 直接打接口，12 个用例 2 秒跑完，不需要开服务、不需要点页面。视图层以外的逻辑越好拆，测试越好写。
2. **导入导出和页面的校验规则必须一致**。如果 Excel 导入自己写一套校验，页面能存的数据导入时可能报错。所以 `excel_io` 不直接 INSERT，而是拼成同样的 payload 交给 `models.create_contact` / `update_contact`，让校验规则只有一份。

### 3.2 收藏联系人是怎么实现的

数据库里 `contacts.is_favorite` 存 0/1，不单独建收藏表——收藏是联系人的一个属性，没必要多一张表。

三个地方配合：

- **排序**：`ORDER BY is_favorite DESC, name COLLATE NOCASE ASC`，收藏的永远排在前面，且同类内按姓名字母序。这样"方便访问"不只是能筛选，打开页面就能先看到重要的人。
- **筛选**：`GET /api/contacts?favorite=1`，SQL 里加 `is_favorite = 1` 条件，前端"Favorites only"按钮只是一个布尔开关。
- **切换**：`POST /api/contacts/<id>/favorite` 接 `{"favorite": true/false}`，显式传值就不会因为重复点击出现状态错乱；不传值时后端按当前值取反，方便以后做快捷键。

前端星标按钮是乐观更新的反例——我故意没做乐观更新，而是等接口返回再 `loadContacts()` 重拉列表。原因：收藏会改变排序，如果本地先改 UI，重新排序时卡片会跳，看起来像 bug；重拉一次数据量只有几十条，代价可以忽略。

### 3.3 多种联系方式的数据建模

这是本次作业唯一需要认真设计的结构。联系方式类型不固定、数量不固定，所以做成**一对多子表**而不是塞进主表的若干字段：

```sql
CREATE TABLE contact_methods (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    contact_id INTEGER NOT NULL,
    kind       TEXT NOT NULL,        -- phone / email / wechat / address / other
    label      TEXT NOT NULL DEFAULT '',  -- mobile / office / work …
    value      TEXT NOT NULL,
    sort_order INTEGER NOT NULL DEFAULT 0,
    FOREIGN KEY (contact_id) REFERENCES contacts (id) ON DELETE CASCADE
);
```

几个具体决定：

- `kind` 用固定枚举（5 类），前端下拉框只能选这 5 类，后端 `normalise_payload` 再校验一次。这样卡片上的色块标签、Excel 的列名、导入的识别规则都能用同一套枚举，不会出现"前端能选、Excel 认不出"的错位。
- `label` 和 `value` 分开存。`13800000000` 和 `mobile` 不是一个维度：一个决定怎么联系，一个决定这是哪个号码。合并成一个字符串后再拆分（`13800000000 (mobile)`）只在 Excel 这一层做，数据库保持结构化。
- `sort_order` 让用户填写的顺序稳定，刷新页面不会乱序。
- 外键 `ON DELETE CASCADE` + 连接上开 `PRAGMA foreign_keys = ON`，删联系人时联系方式自动清掉，不用在业务代码里手动删两次。

更新联系人的语义是**整体替换**：`PUT` 时先删该联系人的所有 methods 再按新 payload 插入。这样前端不用算"哪条改了哪条没改"，实现简单且不会残留旧数据。代价是 id 会变，但联系方式 id 没有对外暴露，不影响。

### 3.4 Excel 导入导出

**导出**（`GET /api/export`）：

1. 先把所有联系人的 methods 按 `kind` 分桶，统计每类最多有几条，得到每类的列宽（至少 1 列）。
2. 表头 = `Name, Company, Title, Notes, Favorite` + 每类的 `Phone 1..n`、`Email 1..m`…
3. 一行一个联系人，同类第 k 条填到第 k 列；带标签的值写成 `13800000000 (mobile)`。
4. 用 openpyxl 加表头底色（`0F766E` 深绿）、白字加粗、细边框、冻结首行、整表自动筛选，列宽按表头长度自适应。这样导出的文件直接能当交付物看，不用再手动排版。

实际导出结果（"Alice Chen" 有 2 个电话 1 个邮箱，"Bob Liu" 有 1 个邮箱）：

| Name | Company | Title | Notes | Favorite | Phone 1 | Phone 2 | Email 1 | WeChat 1 | Address 1 | Other 1 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Alice Chen | Fuzhou University | Course Coordinator | Main contact… | Yes | 13800000001 (mobile) | 13800000002 (office) | alice@example.edu | | | |
| Bob Liu | Maynooth University | Teaching Assistant | | Yes | | | bob@example.edu | | | |

**导入**（`POST /api/import`）：

1. 用 `load_workbook(data_only=True)` 读第一个工作表；解析失败统一转成"文件不可读"的 400 错误，不把 openpyxl 的堆栈抛给用户。
2. 表头识别用正则：固定列走别名表（`Name/name`、`Bookmark/Favorite/Starred` 都认），联系列匹配 `^(phone|email|wechat|address|other)\s*(\d+)?$`，所以 `Phone`、`Phone 1`、`Phone 2` 都能对上。
3. 一行里同类多值：单元格里允许 `;` 或换行分隔，`13800000000 (mobile)` 会拆成 value + label。
4. **同名合并**：如果库里已有同名联系人（`COLLATE NOCASE` 匹配），不新建，而是把新的联系方式追加进去，已存在的 `(kind, value)` 跳过；公司/职位/备注只在原有为空时补齐，收藏取"或"。这条规则是为了防止同一个 Excel 导两次就出现一堆重复人。
5. 返回 `{"imported": n, "merged": m, "skipped": k}`，前端直接提示"Imported 2, merged 1 row(s)"，用户能看懂到底发生了什么。
6. 整表没有任何可识别列时直接报错，而不是静默导入 0 条——静默失败最难排查。

### 3.5 页面样式

作业的"页面样式"占 10 分，所以我做了完整的视觉设计而不是默认表单：

- 顶部品牌区 + 三个操作按钮（Import / Export / New），搜索框与"Favorites only"开关一行排列；
- 三格统计条实时显示联系人 / 收藏 / 联系方式数量，数据直接从接口的 `stats` 取，不做前端假算；
- 联系人卡片：姓名首字母做头像块（按姓名的哈希从 7 色盘取色，同一个人颜色稳定）、收藏角标、按 type 着色的方法 chip、备注左侧竖线引用块、卡片底部 Edit / Delete；
- 表单用原生 `<dialog>` + `showModal()`，带遮罩虚化，Esc 可关闭，联系方式行可增删；
- 所有操作结果走 Toast 提示，失败时变红，不静默。

### 3.6 测试策略

`tests/test_app.py` 共 12 个用例，只用 `tmp_path` 下的独立数据库，互不干扰：

| 用例 | 验证的东西 |
| --- | --- |
| `test_index_page_renders` | 页面能渲染出表单骨架 |
| `test_create_and_list_contact` | 新建后 methods 数量、统计数正确 |
| `test_validation_rejects_empty_name` | 空姓名返回 400 |
| `test_favorite_toggle` | 收藏接口 + `?favorite=1` 过滤 |
| `test_search_matches_contact_methods` | 搜手机号能命中，搜姓名能命中 |
| `test_update_contact_replaces_methods` | 更新是整体替换，不留旧 methods |
| `test_delete_contact` | 删除后列表为空 |
| `test_export_layout_one_row_per_contact_and_one_column_per_type` | 导出表头顺序、行数、每类一列 |
| `test_import_round_trip` | 导出→删库→导入，数据完整还原 |
| `test_import_merges_existing_contact` | 同名合并的规则 |
| `test_import_skips_rows_without_name` | 缺姓名的行被跳过并计入 skipped |
| `test_import_rejects_unknown_columns` | 无表头时明确报错 |

跑一次 2 秒，`12 passed`。这也是我改代码后敢直接提 PR 的底气。

## 四、程序截图

### 4.1 首页：卡片列表 + 统计条 + 收藏角标

![首页](screenshots/01-home.png)

### 4.2 只看收藏（收藏功能 25 分）

![收藏筛选](screenshots/02-favorites-filter.png)

### 4.3 新建联系人：一个联系人挂多种联系方式（10 分）

![新建联系人](screenshots/03-new-contact-dialog.png)

### 4.4 保存后的列表与提示

![保存成功](screenshots/04-contact-saved.png)

### 4.5 按手机号搜索（证明联系方式是真数据，不是摆设）

![搜索](screenshots/05-search-by-phone.png)

### 4.6 导入 Excel 的结果提示（导入导出 25 分）

![导入结果](screenshots/06-import-result.png)

### 4.7 导出后的文件

![导出](screenshots/07-after-export.png)

> 导出的 `contacts.xlsx` 真实结构已核对：1 行表头 + 8 行联系人、11 列，表头依次为
> `Name / Company / Title / Notes / Favorite / Phone 1 / Phone 2 / Email 1 / WeChat 1 / Address 1 / Other 1`；
> 其中 Alice Chen 一行导出的值为 `13800000001 (mobile)`、`alice.chen@example.edu (work)`。
> 原始文件见 `screenshots/exported-contacts.xlsx`（Playwright 自动下载的运行产物，未纳入版本库）。

## 五、完整运行视频

演示顺序：打开首页 → 收藏一个人 → 新建一个带两种联系方式的联系人 → 按手机号搜索 → 导入 Excel → 导出 Excel。

- `screenshots/demo-run.mp4`（0.44 MB，约 40 秒，CSDN 可直接上传）
- `screenshots/demo-run.webm`（高清原片，仓库内可直接播放）

## 六、Git 提交历史与提交次数

![Git 提交历史](screenshots/08-git-history.png)

提交记录：`main` 分支的全部提交均由我完成（个人项目，贡献占比 100%），提交次数见上方截图与仓库首页的 `commits` 计数；完整的本地记录（含每次改动的文件与行数）另存于 `docs/git-log.txt`。

提交是按功能拆的，不是一次性推上去：

```
chore: scaffold address book project
feat(db): add sqlite schema and contact model
feat(api): expose contact CRUD and favorite endpoints
feat(ui): build card grid, dialog form and toast feedback
feat(excel): export workbook and import with merge rule
test: cover api behaviour and excel round trip
docs: add readme, blog draft, psp and deployment guide
docs: add mp4 demo video, git log archive and blog placeholders
docs: align blog commit count with repository history
docs: state the contributor count without a fixed number
```

## 七、云部署（可选加分项）

部署方案写在仓库 `docs/DEPLOY.md`：Ubuntu 22.04 + gunicorn（systemd 托管）+ nginx 反向代理 80 端口。

> **本节状态：未部署（可选项，不计入基础分）**。部署前置是有一台公网服务器或 Render/Railway 账号，代码侧不需要改动：`app.py` 末尾已导出 `app` 对象，可直接 `gunicorn app:app`。
> 若之后完成部署，把公网地址填到上一节的「云部署访问地址」，并把浏览器地址栏含公网 IP/域名 的整页截图存为 `screenshots/09-cloud-deploy.png` 插入本段。

访问地址：未部署（注意：`localhost` / `127.0.0.1` 不算云部署，必须是公网 IP 或域名）

## 八、PSP 表格

| PSP 2.1 | 个人软件开发流程 | 预估耗时（分钟） | 实际耗时（分钟） |
| --- | --- | --- | --- |
| **计划** | **Planning** | **20** | **15** |
| · Estimate | 估计这个任务需要多少时间 | 20 | 15 |
| **开发** | **Development** | **155** | **168** |
| · Analysis | 需求分析（拆成 4 个验收点） | 15 | 12 |
| · Design Spec | 生成设计文档（表结构 + 接口表） | 10 | 8 |
| · Design Review | 设计复审（检查列结构与合并规则） | 5 | 5 |
| · Coding Standard | 代码规范（确定分层与命名） | 5 | 6 |
| · Design | 具体设计（页面区块与交互流程） | 15 | 14 |
| · Coding | 具体编码（后端 4 模块 + 前端 3 文件） | 90 | 105 |
| · Code Review | 代码复审（读一遍自己的 diff） | 10 | 8 |
| · Test | 测试（写 12 个用例并全部跑绿） | 15 | 10 |
| **报告** | **Reporting** | **25** | **32** |
| · Test Report | 测试报告（截图 + 用例表） | 10 | 8 |
| · Size Measurement | 计算工作量（代码行数 / 模块数） | 5 | 4 |
| · Postmortem | 事后总结与改进计划 | 10 | 20 |
| **合计** | **Total** | **200** | **215** |

工作量实测：Python 5 个模块约 800 行（含测试 350 行），前端 3 个文件约 700 行，文档 4 篇。

## 九、开发过程中遇到的问题与解决

1. **Excel 列数到底定几列？** 一开始想固定 `Phone 1..3`，但发现只有 1 个电话的人导出后有三个空列，且以后有人存 4 个电话就丢数据。改成按实际数据动态算列宽（每类至少 1 列），导入端用正则识别 `Phone N`，两个方向都能自洽。
2. **导入重复执行会产生重复联系人。** 第一次实现是无脑 INSERT，同一份文件导两次列表就翻倍。加上同名合并逻辑（`COLLATE NOCASE` + 按 `(kind, value)` 去重）后，重复导入变成幂等操作，顺带解决了"两次导出文件合并"的场景。
3. **Flask 和 SQLite 的并发写。** 开发时开了 `debug=True` 的重载器，两个进程同时写一个 db 文件偶尔报 `database is locked`。解决：视图里每个请求开一个连接、用完立即 `close()`（不用全局连接），演示和部署统一用 `debug=False`。生产则交给 gunicorn 多 worker，SQLite 对这种小写入量足够。
4. **联系人的"整体替换"更新导致外键报错。** 一开始在同一个事务里"先插新 methods 再删旧的"，list 里就出现了同一联系人的新旧两批数据。改成先 DELETE 再 INSERT，并把两步放在 `with connection:` 同一个事务里，语句顺序错了会立即暴露而不是留下脏数据。
5. **中文输入导致 Excel 编码疑问。** 早期担心 xlsx 的中文乱码，实际 openpyxl 内部就是 UTF-8，写进去读出来都正常；真正需要小心的是 CSV（有 BOM 与分隔符问题），所以这里坚决只做 xlsx，不做 CSV。

## 十、对照评分标准自查

| 评分项 | 分值 | 自查结果 |
| --- | --- | --- |
| 博客 Markdown 排版 | 10（基本要求内） | 有目录、有表格、有代码块、有截图 |
| GitHub 仓库链接 / 代码规范链接 | 同上 | 仓库可访问；代码规范见 `docs/CODE_STANDARD.md` |
| 功能实现思路说明 | 20（基本要求内） | 第三节逐条写了"为什么这样设计"，含表结构、接口、边界规则 |
| 程序截图 | 同上 | 7 张运行截图 + 1 张部署截图 + 1 张提交历史 |
| 页面样式 | 10 | 卡片栅格、统计条、弹窗表单、Toast，无默认 Bootstrap 痕迹 |
| 收藏联系人 | 25 | 星标切换 + FAVORITE 角标 + 仅看收藏 + 收藏优先排序 + 导出保留 |
| 添加多种联系方式 | 10 | 5 类枚举 + 自定义标签 + 一对多子表 + 卡片着色 chip |
| 导入与导出 | 25 | 动态列宽 xlsx、表头样式、正则识别、同名合并、缺名跳过、错误提示 |
| 云部署（可选） | +15 | 见第七节 |
| 提交次数 ≥ 3 | 硬性 | 见第六节 |
