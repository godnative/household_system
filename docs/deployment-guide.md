# 部署文档

## 一、系统架构

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│                 │     │                 │     │                 │
│   Nginx/反向代理  │────▶│   FastAPI 后端   │────▶│   PostgreSQL    │
│   静态资源服务    │     │                 │     │                 │
│                 │     │                 │     │                 │
└─────────────────┘     └─────────────────┘     └─────────────────┘
        │
        │ 静态文件
        ▼
┌─────────────────┐
│  Vue 3 前端      │
│  构建产物         │
└─────────────────┘
```

---

## 二、环境要求

### 2.1 服务器配置

| 配置项 | 最低要求 | 推荐配置 |
|--------|---------|---------|
| CPU | 2核 | 4核+ |
| 内存 | 4GB | 8GB+ |
| 磁盘 | 50GB | 100GB+ SSD |
| 操作系统 | Ubuntu 20.04+ / CentOS 7+ | Ubuntu 22.04 LTS |

### 2.2 软件依赖

| 软件 | 版本要求 |
|------|---------|
| Python | 3.10+ |
| Node.js | 18.x LTS |
| PostgreSQL | 14+ |
| Nginx | 1.18+ |

---

## 三、安装部署步骤

### 3.1 安装系统依赖

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install -y python3 python3-pip python3-venv nodejs npm postgresql postgresql-contrib nginx

# CentOS/RHEL
sudo yum install -y python3 python3-pip nodejs npm postgresql-server postgresql-contrib nginx
sudo postgresql-setup initdb
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

### 3.2 配置 PostgreSQL

```bash
# 创建数据库和用户
sudo -u postgres psql

# 在 psql 中执行
CREATE DATABASE household_system;
CREATE USER household_user WITH ENCRYPTED PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE household_system TO household_user;
\q
```

### 3.3 部署后端

```bash
# 创建应用目录
sudo mkdir -p /opt/household_system
sudo chown $USER:$USER /opt/household_system

# 克隆代码
cd /opt/household_system
git clone <repository_url> .

# 创建虚拟环境
cd backend
python3 -m venv venv
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env 文件，配置数据库连接等

# 运行数据库迁移
alembic upgrade head

# 初始化基础数据
python -c "from app.core.init_db import init_database; init_database()"
```

### 3.4 部署前端

```bash
# 安装依赖
cd /opt/household_system/frontend
npm install

# 配置环境变量
cp .env.example .env
# 编辑 .env 文件，配置 API 地址

# 构建生产版本
npm run build

# 部署到 Nginx 目录
sudo mkdir -p /var/www/household_system
sudo cp -r dist/* /var/www/household_system/
```

### 3.5 配置 Nginx

```nginx
# /etc/nginx/sites-available/household_system

server {
    listen 80;
    server_name your-domain.com;

    # 前端静态文件
    location / {
        root /var/www/household_system;
        try_files $uri $uri/ /index.html;
    }

    # API 代理
    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # 上传文件访问
    location /uploads/ {
        alias /opt/household_system/backend/static/uploads/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
}
```

```bash
# 启用站点
sudo ln -s /etc/nginx/sites-available/household_system /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### 3.6 配置 Systemd 服务

```ini
# /etc/systemd/system/household-backend.service

[Unit]
Description=Household System Backend API
After=network.target postgresql.service

[Service]
Type=simple
User=www-data
Group=www-data
WorkingDirectory=/opt/household_system/backend
Environment="PATH=/opt/household_system/backend/venv/bin"
ExecStart=/opt/household_system/backend/venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
```

```bash
# 启用服务
sudo systemctl daemon-reload
sudo systemctl enable household-backend
sudo systemctl start household-backend
```

---

## 四、环境变量配置

### 4.1 后端环境变量 (.env)

```bash
# 应用配置
APP_NAME="天主教家庭教籍管理系统"
APP_ENV=production
DEBUG=false

# 数据库配置
DATABASE_URL=postgresql://household_user:your_secure_password@localhost:5432/household_system

# 安全配置
SECRET_KEY=your-secret-key-change-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# 文件上传配置
UPLOAD_DIR=/opt/household_system/backend/static/uploads
MAX_UPLOAD_SIZE=10485760
```

### 4.2 前端环境变量 (.env)

```bash
# API 配置
VITE_API_BASE_URL=/api/v1

# 应用配置
VITE_APP_TITLE=天主教家庭教籍管理系统
```

---

## 五、上线切换方案

### 5.1 灰度切换步骤

1. **准备阶段**
   - 确认新系统部署完成
   - 确认数据库迁移完成
   - 准备回滚方案

2. **切换阶段**
   ```bash
   # 停止旧系统（如有）
   sudo systemctl stop old-household-system

   # 启动新系统
   sudo systemctl start household-backend
   sudo systemctl reload nginx
   ```

3. **验证阶段**
   - 访问系统登录页
   - 使用测试账号登录
   - 执行冒烟测试

4. **监控阶段**
   - 监控系统日志
   - 监控数据库连接
   - 监控响应时间

### 5.2 回滚方案

```bash
# 如需回滚
sudo systemctl stop household-backend
sudo systemctl start old-household-system
sudo nginx -s reload
```

---

## 六、备份与恢复

### 6.1 数据库备份

```bash
# 手动备份
pg_dump -U household_user household_system > backup_$(date +%Y%m%d_%H%M%S).sql

# 自动备份脚本 (crontab)
0 2 * * * pg_dump -U household_user household_system | gzip > /backup/household_$(date +\%Y\%m\%d).sql.gz
```

### 6.2 数据库恢复

```bash
# 恢复数据库
psql -U household_user household_system < backup.sql
```

---

## 七、监控与日志

### 7.1 日志位置

| 服务 | 日志路径 |
|------|---------|
| 后端 API | `/var/log/household/backend.log` |
| Nginx 访问日志 | `/var/log/nginx/access.log` |
| Nginx 错误日志 | `/var/log/nginx/error.log` |

### 7.2 健康检查

```bash
# 检查后端服务状态
curl http://localhost:8000/api/v1/health

# 检查数据库连接
curl http://localhost:8000/api/v1/health/db
```

---

## 八、安全配置

### 8.1 HTTPS 配置（推荐）

```bash
# 安装 Certbot
sudo apt install certbot python3-certbot-nginx

# 获取证书
sudo certbot --nginx -d your-domain.com

# 自动续期
sudo certbot renew --dry-run
```

### 8.2 防火墙配置

```bash
# 开放必要端口
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw allow 22/tcp
sudo ufw enable
```

---

## 九、常见问题

### Q1: 后端启动失败
- 检查数据库连接配置
- 检查 Python 依赖是否完整
- 查看后端日志

### Q2: 前端页面空白
- 检查 Nginx 配置
- 检查构建产物是否正确部署
- 检查浏览器控制台错误

### Q3: API 请求 502
- 检查后端服务是否运行
- 检查 Nginx 代理配置
- 检查端口占用情况
