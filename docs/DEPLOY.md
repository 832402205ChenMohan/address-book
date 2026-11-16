# 云服务器部署（对应作业 1.4，额外 +15 分）

> 注意：`localhost` 或 `127.0.0.1` 访问**不算**云部署，必须是公网 IP / 域名能打开的地址。

## 方案 A：阿里云 / 华为云 ECS（推荐，作业里点名的就是这两家）

### 1. 准备服务器

1. 登录阿里云控制台 → 云服务器 ECS → 创建实例。
2. 镜像选 **Ubuntu 22.04 LTS**，规格 1 核 2G 够用（学生机/轻量应用服务器都可以）。
3. 安全组放行 **22（SSH）** 和 **80（HTTP）**，如果用 443 再放行 443。
4. 记下公网 IP，例如 `47.100.xx.xx`。

### 2. 上传代码

本地 PowerShell 里执行（把路径和 IP 换成自己的）：

```powershell
scp -r .\address-book root@47.100.xx.xx:/opt/address-book
```

或者服务器上直接 `git clone` 你的 GitHub 仓库：

```bash
cd /opt && git clone https://github.com/<your-name>/address-book.git
```

### 3. 安装运行环境

```bash
ssh root@47.100.xx.xx
apt update && apt install -y python3 python3-venv python3-pip nginx
cd /opt/address-book
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt gunicorn
mkdir -p data
```

### 4. 用 systemd 托管 gunicorn

新建 `/etc/systemd/system/address-book.service`：

```ini
[Unit]
Description=Address Book Flask service
After=network.target

[Service]
WorkingDirectory=/opt/address-book
Environment=PYTHONUNBUFFERED=1
ExecStart=/opt/address-book/.venv/bin/gunicorn -w 3 -b 127.0.0.1:8000 app:app
Restart=always

[Install]
WantedBy=multi-user.target
```

启动并设为开机自启：

```bash
systemctl daemon-reload
systemctl enable --now address-book
systemctl status address-book --no-pager
curl http://127.0.0.1:8000/healthz     # 期望 {"status":"ok"}
```

### 5. nginx 反向代理 80 端口

新建 `/etc/nginx/sites-available/address-book`：

```nginx
server {
    listen 80;
    server_name _;

    client_max_body_size 10m;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

启用配置：

```bash
ln -s /etc/nginx/sites-available/address-book /etc/nginx/sites-enabled/address-book
rm -f /etc/nginx/sites-enabled/default
nginx -t && systemctl reload nginx
```

### 6. 验证（截图留证）

浏览器访问 `http://47.100.xx.xx/`，能看到通讯录页面、能收藏能导入导出，就说明公网部署成功。把浏览器地址栏截图和页面截图放进博客。

> 国内服务器用域名访问需先把域名备案；用公网 IP 直接访问不涉及备案，作业验收足够。

## 方案 B：GitHub + Render（不买服务器也能拿到公网地址）

1. 仓库里加 `render.yaml` 或直接在 Render 后台新建 **Web Service**，关联 GitHub 仓库。
2. Build Command：`pip install -r requirements.txt`
3. Start Command：`gunicorn -w 3 -b 0.0.0.0:$PORT app:app`
4. 部署完拿到 `https://xxx.onrender.com`，属于公网地址。

缺点：免费实例会自动休眠、首次访问慢，演示录像时先手动唤醒一次。

## 部署后自查清单

- [ ] 公网地址能打开首页（不是 127.0.0.1）
- [ ] 新建 + 收藏 + 删除都正常
- [ ] 导出 xlsx 能下载、内容列齐全
- [ ] 导入 xlsx 后列表更新，同名走合并
- [ ] 服务重启后数据仍在（SQLite 文件在 `data/addressbook.db`，不要放在临时目录）
- [ ] `systemctl status address-book` 显示 active (running)
