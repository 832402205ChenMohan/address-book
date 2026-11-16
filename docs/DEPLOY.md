# Cloud deployment (assignment section 1.4, +15 points)

> Note: `localhost` or `127.0.0.1` does **not** count as cloud deployment. The address must open through a public IP or a domain name.

## Option A: Alibaba Cloud / Huawei Cloud ECS (the two providers named in the brief)

### 1. Prepare the server

1. Sign in to the Alibaba Cloud console, go to Elastic Compute Service (ECS), create an instance.
2. Choose **Ubuntu 22.04 LTS**; 1 vCPU / 2 GB is enough (a student or lightweight instance works too).
3. Open **22 (SSH)** and **80 (HTTP)** in the security group; add 443 if you terminate TLS.
4. Note the public IP, e.g. `47.100.xx.xx`.

### 2. Upload the code

From local PowerShell (replace the path and IP):

```powershell
scp -r .\address-book root@47.100.xx.xx:/opt/address-book
```

Or clone directly on the server:

```bash
cd /opt && git clone https://github.com/832402205ChenMohan/address-book.git
```

### 3. Install the runtime

```bash
ssh root@47.100.xx.xx
apt update && apt install -y python3 python3-venv python3-pip nginx
cd /opt/address-book
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt gunicorn
mkdir -p data
```

### 4. Run gunicorn under systemd

Create `/etc/systemd/system/address-book.service`:

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

Enable and start it:

```bash
systemctl daemon-reload
systemctl enable --now address-book
systemctl status address-book --no-pager
curl http://127.0.0.1:8000/healthz     # expect {"status":"ok"}
```

### 5. Reverse-proxy port 80 with nginx

Create `/etc/nginx/sites-available/address-book`:

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

Enable it:

```bash
ln -s /etc/nginx/sites-available/address-book /etc/nginx/sites-enabled/address-book
rm -f /etc/nginx/sites-enabled/default
nginx -t && systemctl reload nginx
```

### 6. Verify and keep evidence

Open `http://47.100.xx.xx/` in a browser. If the page loads, bookmarks work and a round trip of import/export succeeds, the public deployment is done. Capture a screenshot that shows the address bar with the public IP — that is the evidence the marker needs.

> Serving through a domain name on a mainland China server requires ICP filing; accessing through the public IP does not, which is sufficient for this assignment.

## Option B: GitHub + Render (a public URL without buying a server)

1. In the Render dashboard create a **Web Service** and connect the GitHub repository.
2. Build command: `pip install -r requirements.txt`
3. Start command: `gunicorn -w 3 -b 0.0.0.0:$PORT app:app`
4. The service is published at `https://xxx.onrender.com`, which is a public address.

Caveat: the free tier sleeps when idle, so wake it once before recording the demo.

## Post-deployment checklist

- [ ] The public address opens the home page (not 127.0.0.1)
- [ ] Create, bookmark and delete all work
- [ ] Export downloads an xlsx with the full column set
- [ ] Import updates the list, and duplicate names merge
- [ ] Data survives a service restart (the SQLite file lives in `data/addressbook.db`, not in a temporary directory)
- [ ] `systemctl status address-book` reports active (running)
