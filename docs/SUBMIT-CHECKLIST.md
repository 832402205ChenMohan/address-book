# 提交清单（Post this, then submit）

> 一句话：**博客正文用 `docs/BLOG-en.md`，全选复制 → 粘进 CSDN 编辑器 → 直接发布**。图片已经全部换成在线链接，不需要你上传任何图片。

## 1. 最后要交的三样东西

| # | 交什么 | 具体内容 |
| --- | --- | --- |
| 1 | 仓库链接 | https://github.com/832402205ChenMohan/address-book （Public，已推送完毕） |
| 2 | 博客正文 | `docs/BLOG-en.md` 全文（英文，约 3200 词，9 张图已内嵌在线链接） |
| 3 | 演示视频 | 博客第五节已放了在线链接；若想要页面内直接播放，可在 CSDN 里手动上传 `screenshots/demo-run.mp4`（0.44 MB） |

## 2. 图片处理方式（不用再管）

9 张运行截图 + 仓库截图都已换成 GitHub raw 直链，实测全部可访问、字节数与本地一致（校验脚本 `scripts/check_preview.py` 会重新检查一遍）：

```
https://raw.githubusercontent.com/832402205ChenMohan/address-book/main/screenshots/01-home.png
https://raw.githubusercontent.com/832402205ChenMohan/address-book/main/screenshots/02-favorites-filter.png
https://raw.githubusercontent.com/832402205ChenMohan/address-book/main/screenshots/03-new-contact-dialog.png
https://raw.githubusercontent.com/832402205ChenMohan/address-book/main/screenshots/04-contact-saved.png
https://raw.githubusercontent.com/832402205ChenMohan/address-book/main/screenshots/05-search-by-phone.png
https://raw.githubusercontent.com/832402205ChenMohan/address-book/main/screenshots/06-import-result.png
https://raw.githubusercontent.com/832402205ChenMohan/address-book/main/screenshots/07-after-export.png
https://raw.githubusercontent.com/832402205ChenMohan/address-book/main/screenshots/08b-repo-overview.png
https://raw.githubusercontent.com/832402205ChenMohan/address-book/main/screenshots/08-git-history.png
```

若 CSDN 发布后出现裂图（极少数情况，CSDN 会拦截外链），退回方案：本地 `screenshots/` 里有同一批原图，逐张上传即可（文件名与博客里的图片标题一一对应）。另外一个零成本兜底：把博客里的 raw 链接换成仓库页面直链 `https://github.com/832402205ChenMohan/address-book/blob/main/screenshots/01-home.png`。

## 3. CSDN 发布三步

1. CSDN → 创作中心 → 写文章 → 编辑器右上角切换到 **Markdown** 模式。
2. 打开 `docs/BLOG-en.md`，**全选复制**，粘贴进去。标题用第一行：`Extreme Programming Assignment — Address Book (Flask + SQLite + Excel Import/Export)`；标签建议 `软件工程`、`极限编程`、`Flask`、`Python`、`Excel`。
3. 右侧选分类（作业所在专栏或 `2601_FZU-MU_SE` 相关），点「发布文章」，然后到作业帖按老师要求提交博客链接。

## 4. 发布前 60 秒自查

- [ ] 标题和正文是英文（作业要求英文版）
- [ ] 开头的 Assignment Information 表五行齐全（Course / Team Name / Assignment Requirements / Objectives / Other References）
- [ ] 9 张图都显示出来（尤其第二节的仓库概览、第六节的提交历史，这两张不在截图章节，最容易漏）
- [ ] 仓库链接点得开、代码规范链接点得开（`docs/CODE_STANDARD.md` 已是英文）
- [ ] 视频链接或内嵌播放器可用
- [ ] PSP 表里的「实际耗时」按你自己的真实感受改过
- [ ] 云部署若没做，第七节保持「not deployed」的诚实说明（该项是可选加分，不影响基础分）
- [ ] 发布成功并把链接提交到作业帖（博客发布后需要审核，别卡在截止前）

## 5. 仓库里还有什么（备用材料）

| 路径 | 用途 |
| --- | --- |
| `docs/BLOG-zh.md` | 中文版博客，答辩或老师追问时对照用 |
| `docs/STEP-BY-STEP.md` | 从建仓到提交的完整操作步骤（中文） |
| `docs/CODE_STANDARD.md` | 代码规范，博客里的「代码规范链接」指向它 |
| `docs/DEPLOY.md` | 云部署方案（想拿 +15 分就照它做） |
| `docs/git-log.txt` | 提交记录存档（含每次改动文件与行数） |
| `preview-blog.html` | 本机预览页，双击即可看博客最终排版与图片 |
| `screenshots/` | 全部原图 + 演示录像（mp4 / webm） |
