# 环境搭建说明

## 目标
为 Web 迁移建立统一、可复现、可并行协作的前后端开发环境。

## 当前技术基线
- 前端：Vue 3 + TypeScript + Vite + Element Plus + Pinia + Vue Router
- 后端：FastAPI + SQLAlchemy 2.x + Alembic + Pydantic
- 数据库：PostgreSQL（开发阶段优先），SQLite 仅允许作为临时替代
- 包管理：前端统一使用 pnpm；后端统一使用 venv + pip

## 目录结构
- `frontend/`：前端工程
- `backend/`：后端工程
- `docs/`：迁移文档
- `scripts/`：辅助脚本
- `deploy/`：部署模板
- `tests-e2e/`：端到端测试
- `artifacts/`：报告与产物

## 本地环境要求
### 前端
- Node.js：22.x LTS
- pnpm：9.x

### 后端
- Python：3.12.x
- 虚拟环境：`backend/.venv`

## 安装步骤
### 前端
```bash
cd frontend
pnpm install
```

### 后端
```bash
python3 -m venv backend/.venv
backend/.venv/bin/pip install -r backend/requirements.txt
```

## 启动步骤
### 启动后端
```bash
backend/.venv/bin/uvicorn app.main:app --app-dir backend --reload --host 0.0.0.0 --port 8000
```

### 启动前端
```bash
cd frontend
pnpm dev --host 0.0.0.0 --port 5173
```

## 基础验证
### 后端健康检查
- URL: `http://127.0.0.1:8000/health`
- 预期返回：`{"status":"ok"}`

### 前端构建
```bash
cd frontend
pnpm exec vite build
```

## 环境变量
- 前端模板：`frontend/.env.example`
- 后端模板：`backend/.env.example`

## 静态资源目录约定
- 登录页背景：`frontend/public/images/login/`
- 品牌 Logo：`frontend/public/images/branding/`
- 欢迎页图片：`frontend/public/images/home/`
- 上传图片：`backend/app/static/uploads/`
- 系统静态资源：`backend/app/static/system/`

## 当前已完成项
- 前后端骨架目录已创建
- 前端依赖已安装
- 后端虚拟环境与依赖已安装
- 前端基础构建已验证
- 后端基础代码已通过编译检查
- `static/welcome_image.jpg` 已复制到 `frontend/public/images/home/welcome-image.jpg`

## 待确认项
- PostgreSQL 本地统一启动方式
- 登录页背景图与 logo 的真实源文件位置
- 前端 lint / test 命令标准化
- 后端 pytest 与 Alembic 初始化细节
