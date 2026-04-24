# 启动与联调说明

## 推荐启动顺序
1. 启动数据库
2. 启动后端
3. 启动前端
4. 打开前端页面
5. 验证后端健康检查
6. 验证登录、当前用户、受保护接口与上传链路

## 后端启动
```bash
backend/.venv/bin/uvicorn app.main:app --app-dir backend --reload --host 0.0.0.0 --port 8000
```

## 前端启动
```bash
cd frontend
pnpm dev --host 0.0.0.0 --port 5173
```

## 健康检查
- 后端：`http://127.0.0.1:8000/health`
- OpenAPI：`http://127.0.0.1:8000/docs`
- 前端：`http://127.0.0.1:5173`

## 当前联调边界
当前阶段已具备以下最小联调能力：
- 登录接口：`POST /api/v1/auth/login`
- 当前用户接口：`GET /api/v1/auth/me`
- 受保护首页占位接口：`GET /api/v1/dashboard`
- 图片上传接口：`POST /api/v1/uploads`

详细字段说明见：`docs/stage3-api-spec.md`

## 阶段 3 smoke 检查清单

### 1. 后端健康检查
1. 访问 `http://127.0.0.1:8000/health`。
2. 预期返回：
```json
{"status":"ok"}
```

### 2. OpenAPI 可访问
1. 打开 `http://127.0.0.1:8000/docs`。
2. 预期 Swagger 页面正常加载。

### 3. 登录链路
1. 打开前端登录页：`http://127.0.0.1:5173/login`。
2. 使用默认账号登录：
   - 用户名：`admin`
   - 密码：`admin123`
3. 预期登录成功并跳转到 `/dashboard`。

### 4. 当前用户初始化
1. 登录成功后刷新浏览器。
2. 预期前端可基于本地 token 重新调用 `/api/v1/auth/me`。
3. 系统首页应显示当前用户、角色与权限数量。

### 5. 受保护接口验证
1. 登录状态下访问首页。
2. 预期首页可正常读取 `/api/v1/dashboard`，并显示“阶段 3 业务占位接口已就绪”。
3. 清空浏览器 localStorage 中 token 后再次访问受保护页面。
4. 预期前端跳回 `/login`。

### 6. 上传链路验证
1. 登录后进入“上传验证”页面。
2. 上传一张 png、jpg 或 webp 图片。
3. 预期上传成功，并显示：
   - `filename`
   - `size`
   - `content_type`
   - `url`
4. 使用返回的 `url` 直接访问文件，预期返回 200 且图片可见。

### 7. 权限门控示例验证
1. 登录后进入任意占位页，如 `/users` 或 `/members`。
2. 预期页面中能看到通过 `PermissionGate` 控制的示例区块。
3. 默认管理员应至少能看到：
   - `member_view` 区块
   - `user_manage` 区块
4. `observer` 专属区块在默认管理员下不显示。

## 最小验证命令

### 前端
```bash
cd frontend
pnpm exec tsc --noEmit
pnpm exec vite build
```

### 后端
```bash
backend/.venv/bin/python -m pytest backend/tests
```

## 端口约定
- 前端：5173
- 后端：8000
- 数据库：5432（推荐 PostgreSQL 默认端口）
