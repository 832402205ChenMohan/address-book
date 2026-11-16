# 极限编程作业：完整操作步骤（从零到提交）

> 对应作业：《Extreme Programming（Deadline: November 17, 2026 23:59）》，课程「软件工程（FZU–MU）」。
> 本文按时间顺序给出每一步的实际操作，命令都能直接复制执行。

---

## 阶段 0：开始前 5 分钟确认

| 确认项 | 说明 |
| --- | --- |
| 截止时间 | 2026-11-17 23:59，博客要**先发后审**，建议 11-16 当天就发 |
| 提交方式 | 每人各交自己的博客（个人项目只交一篇），博客里要有项目地址 |
| 仓库要求 | GitHub 仓库提交次数 **≥ 3**，代码能构建 |
| 基础分 | 100 分：基本要求 30（博客排版 + 链接 + 实现思路 + 截图）+ 编码 70（样式 10、收藏 25、多联系方式 10、导入导出 25） |
| 加分项 | 1.4 云部署 +15 |
| 课程目标 | 目标 2（基本要求）、目标 4（编码实现），博客里最好点明这两条 |

---

## 阶段 1：建仓库（15 分钟）

1. 登录 GitHub，新建仓库 `address-book`，**不要**勾选自动生成 README（本地已有内容，避免冲突）。
2. 本地初始化并关联远程（PowerShell，在 `address-book` 目录下）：

```powershell
git init
git add .
git commit -m "chore: scaffold address book project"
git branch -M main
git remote add origin https://github.com/<your-name>/address-book.git
git push -u origin main
```

3. 如果老师给了模板仓库，先点 **Fork**，再 `git clone` 自己的 Fork 地址，往上叠加代码；没有模板就直接用上面的方式建自己的仓库。
4. 提交次数 ≥ 3 的达成方式：按功能拆成多次提交，而不是一次 `git add .` 全推上去。本项目的参考提交顺序：

```
chore: scaffold address book project          # 骨架、依赖、.gitignore
feat(db): add sqlite schema and contact model  # 数据层
feat(api): expose contact CRUD and favorite    # 接口层
feat(ui): build card grid and contact dialog   # 页面
feat(excel): export and import with merge rule # 导入导出
test: cover api and excel round trip           # 测试
docs: add readme, code standard and deploy doc # 文档
```

---

## 阶段 2：本地跑通（10 分钟）

```powershell
cd address-book
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python scripts\seed_demo.py
python -m pytest -q          # 期望 12 passed
python app.py                # 打开 http://127.0.0.1:5000
```

手工验收四个评分点（每做完一步截一张图，博客要用）：

1. **收藏**：点卡片右上角星标 → 星标变实心、卡片出现 FAVORITE 标签、顶部 Favorites 计数 +1；点「Favorites only」只剩收藏的人。
2. **多联系方式**：New Contact → 点「+ Add method」加第二条 → 类型选 email、标签填 work → 保存后卡片上出现 PHONE 和 EMAIL 两个 chip。
3. **导出**：点 Export Excel → 下载 `contacts.xlsx` → 打开确认「一人一行、每类信息一列」（Name / Company / Title / Notes / Favorite / Phone 1 / Phone 2 / Email 1 …）。
4. **导入**：点 Import Excel → 选 `samples\import-demo.xlsx` → 提示 `Imported 2, merged 1 row(s)` → 列表多出两人，Grace Wang 原有的电话被保留、新增的没重复。

---

## 阶段 3：截图与录像（20 分钟）

博客明确要求「程序截图 + 完整运行视频」，漏了直接丢 20 分里的截图部分。

**录像建议流程（一次录完，别剪辑）**：打开首页 → 收藏一个人 → 新建一个人（含两种联系方式）→ 搜索手机号 → 导入 Excel → 导出 Excel → 结束。

- Windows 自带 `Win + G`（Xbox Game Bar）或 `Win + Alt + R` 直接录屏，产物是 mp4。
- 也可以用仓库里的 `scripts\shoot.py`（Playwright）自动生成截图和 webm 录像。

**截图清单（6 张起）**：

- [ ] 首页完整列表（体现卡片样式与统计条）
- [ ] 收藏后的状态（星标实心 + FAVORITE 标签 + 计数变化）
- [ ] 新建/编辑联系人弹窗（体现多联系方式输入）
- [ ] 导出得到的 Excel 打开效果（体现列结构）
- [ ] 导入后的提示与列表变化
- [ ] （若做了）云部署的公网地址页面 + 浏览器地址栏可见公网 IP

---

## 阶段 4：云部署（30 分钟，可选 +15 分）

按 `docs\DEPLOY.md` 走一遍：买 ECS / 轻量服务器 → 上传代码 → gunicorn + systemd → nginx 反代 → 公网访问验证。
必须留下**浏览器地址栏是公网 IP 或域名**的截图，否则老师无法判断是不是真部署。

---

## 阶段 5：写博客（40 分钟，最容易丢分的一步）

打开 `docs\BLOG-en.md`（英文提交版），它是按评分表逐条对齐写的草稿，你只需要：

1. 把 `{{REPO_URL}}`、`{{DEPLOY_URL}}` 之类占位符换成真实地址。
2. 把 `screenshots/` 里的图片上传到 CSDN 博客（本地相对路径在 CSDN 上不显示，必须用编辑器「上传图片」）。
3. 把 `{{}}` 形式的 PSP 实际耗时改成你自己的真实数字。
4. 补一张 GitHub 提交历史截图（仓库首页 → Commits → 最上面显示 `N commits`，点进去能看到每个 commit 的作者）。

**开头必须有这张说明表**（作业 4. 规则与格式 要求）：

| 项目 | 内容 |
| --- | --- |
| 本次作业所属课程 | 软件工程（FZU–MU） |
| 团队名称 | 个人项目（陈墨瀚） |
| 作业要求 | 极限编程：通讯录收藏、多联系方式、Excel 导入导出、可选云部署 |
| 本次作业的目标 | 通过一次完整的小型项目实践，体验结对/独立开发的完整流程：需求拆分、编码、测试、部署、文档 |
| 其他参考资料 | GitHub 仓库、代码规范文档、Flask / openpyxl 官方文档 |

---

## 阶段 6：发布与提交（15 分钟）

1. CSDN 博客标题建议：`极限编程作业——通讯录（Flask + SQLite + Excel 导入导出）`。
2. 发布前自查（作业给了明确清单，逐条打勾）：

- [ ] 博客用 Markdown 排版，有目录
- [ ] GitHub 仓库链接可点开，代码规范链接可点开（`docs/CODE_STANDARD.md`）
- [ ] 功能实现思路写得具体（哪一层做什么、为什么这样设计），不是空话
- [ ] 程序截图齐全、有完整运行视频
- [ ] PSP 表格（一人一张）
- [ ] 提交次数 ≥ 3，仓库里代码 + 文档都在
- [ ] 博客已发布（**不要卡在 23:59 前发，审核要时间**）

3. 把博客链接和仓库链接按老师要求提交（作业里写的是「每位同学提交自己的博客」）。

---

## 时间不够时的取舍顺序

1. **必须保**：仓库 ≥ 3 次提交、收藏、多联系方式、导入导出、博客有截图 —— 这四项共 95 分。
2. **可砍**：云部署（15 分加分），砍掉不影响基础分。
3. **别省**：测试不必写很多，但 `python -m pytest -q` 全绿这件事值得写进博客的「实现思路」，是「代码质量」的实证。
