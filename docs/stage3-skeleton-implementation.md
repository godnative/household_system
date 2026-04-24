# 阶段 3：工程骨架搭建说明

## 1. 目标
当前阶段已将阶段 2 的架构设计转化为可运行的最小工程骨架，目标是形成“可启动、可联调、可扩展”的业务空壳。

已落地内容包括：
- 前端路由、布局、登录页、鉴权 store、API client、业务占位页
- 后端 FastAPI 入口、认证最小闭环、上传接口、受保护业务占位接口
- SQLite 默认开发配置与自动种子数据初始化
- Alembic 环境接入与首个认证基础 migration
- 后端最小测试用例
- 阶段 3 接口说明与 smoke 联调检查文档

## 2. 前端结构
- `frontend/src/router/index.ts`：路由与导航守卫
- `frontend/src/layouts/BasicLayout.vue`：统一业务壳布局
- `frontend/src/views/LoginView.vue`：登录页
- `frontend/src/views/DashboardView.vue`：首页，接入 `/api/v1/dashboard`
- `frontend/src/views/PlaceholderView.vue`：阶段 3 占位页面，接入 `PermissionGate` 示例
- `frontend/src/views/UploadDemoView.vue`：上传验证页，接入 `/api/v1/uploads`
- `frontend/src/stores/auth.ts`：登录态与当前用户管理
- `frontend/src/api/client.ts`：Axios 封装、Bearer Token 注入与 401 处理
- `frontend/src/components/PageContainer.vue`：页面容器
- `frontend/src/components/PermissionGate.vue`：权限门控组件

## 3. 后端结构
- `backend/app/main.py`：FastAPI 应用入口、CORS、静态上传目录挂载、启动时初始化
- `backend/app/core/settings.py`：配置与默认环境变量
- `backend/app/core/db.py`：数据库 engine / session / Base
- `backend/app/core/security.py`：Bearer 鉴权与权限依赖
- `backend/app/models/auth.py`：用户、角色、权限模型
- `backend/app/services/auth_service.py`：认证、token、种子数据初始化
- `backend/app/services/upload_service.py`：上传保存逻辑
- `backend/app/api/auth.py`：登录与当前用户接口
- `backend/app/api/uploads.py`：上传接口
- `backend/app/api/router.py`：总路由与受保护占位接口
- `backend/alembic/env.py`：Alembic 环境配置
- `backend/alembic/versions/0001_auth_base.py`：认证基础表 migration
- `backend/tests/test_health.py`：健康检查测试
- `backend/tests/test_auth.py`：登录闭环测试
- `backend/tests/test_uploads.py`：上传鉴权测试

## 4. 默认开发账号
启动后端后会自动初始化默认账号：
- 用户名：`admin`
- 密码：`admin123`

## 5. 当前阶段已打通的最小链路
### 5.1 认证闭环
- `POST /api/v1/auth/login`
- `GET /api/v1/auth/me`
- 前端登录页提交用户名和密码后保存 Bearer Token
- 路由守卫在进入受保护页面前自动拉取当前用户
- token 失效或缺失时自动跳回登录页

### 5.2 受保护接口闭环
- `GET /api/v1/dashboard`
- 首页在挂载时调用该接口
- 当前默认管理员具备访问权限，可用于验证 Bearer Token 注入与权限依赖生效

### 5.3 上传闭环
- `POST /api/v1/uploads`
- 前端“上传验证”页面已接入真实接口
- 当前支持 jpeg/png/webp，大小限制 5MB
- 上传成功后返回文件元信息与静态访问 URL

## 6. 启动方式

### 后端
```bash
backend/.venv/bin/uvicorn app.main:app --app-dir backend --reload --host 0.0.0.0 --port 8000
```

### 前端
```bash
cd frontend
pnpm dev --host 0.0.0.0 --port 5173
```

## 7. 最小联调链路
1. 启动后端。
2. 打开 `http://127.0.0.1:8000/docs`，确认 OpenAPI 可用。
3. 启动前端。
4. 打开 `http://127.0.0.1:5173/login`。
5. 使用 `admin / admin123` 登录。
6. 登录成功后跳转 `/dashboard`。
7. 首页读取 `/api/v1/dashboard` 并显示占位消息。
8. 访问堂区/家庭/成员/用户角色管理占位页，确认权限门控示例已显示。
9. 访问“上传验证”页面并上传图片，确认返回 `filename`、`size`、`content_type`、`url`。
10. 清空浏览器 localStorage 中 token 后再次访问业务页，应跳回登录页。

## 8. 相关文档
- `docs/stage3-api-spec.md`：阶段 3 接口说明
- `docs/startup-and-integration.md`：启动与 smoke 联调检查清单

## 9. 最小验证命令

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

## 10. 当前阶段验收点
- 前端可启动并访问登录页与业务壳
- 后端可启动并提供 `/health` 与 `/docs`
- 登录 / 当前用户最小认证闭环可用
- Alembic 可执行且认证基础表已建模
- 上传接口可用并具备基础校验
- 前端已接入真实的 dashboard 与 upload 接口
- `PermissionGate` 已在页面中实际接入
- 最小测试链路已具备

## 11. 下一步衔接
阶段 3 收口后，可进入阶段 4：底座能力迁移，优先接入：
- 用户/角色/权限真实管理能力
- 堂区范围控制
- 核心领域模型
- 通用分页/查询能力
- 图片元数据与上传规则
