# 阶段 3 接口说明

## 1. 目标
本文档补充阶段 3 已落地的最小接口闭环，覆盖认证、当前用户、受保护首页占位接口与上传接口，作为前后端联调和阶段 3 验收的接口基线。

当前阶段接口以“最小可启动、最小可联调”为目标，后续阶段可在此基础上扩展统一错误码、分页、审计、真实业务字段与更完整的安全策略。

## 2. 通用约定

### 2.1 Base URL
- 后端开发地址：`http://127.0.0.1:8000`
- API 前缀：`/api/v1`

### 2.2 认证方式
- 当前采用 Bearer Token。
- 登录成功后，前端应在后续请求头中附带：

```http
Authorization: Bearer <access_token>
```

### 2.3 响应约定
- 当前阶段以直接返回 JSON 对象为主，不额外包裹 `code` / `data` / `message` 结构。
- 认证失败返回 `401`。
- 权限不足返回 `403`。
- 上传校验失败返回 `400`。

## 3. 认证接口

### 3.1 登录
- 方法：`POST`
- 路径：`/api/v1/auth/login`
- 鉴权：否
- 说明：使用用户名与密码换取访问 token。

#### 请求体
```json
{
  "username": "admin",
  "password": "admin123"
}
```

#### 成功响应 `200`
```json
{
  "access_token": "<token>",
  "token_type": "bearer"
}
```

#### 失败响应 `401`
```json
{
  "detail": "用户名或密码错误"
}
```

#### 联调说明
- 默认开发账号为 `admin / admin123`。
- 登录成功后，前端应保存 `access_token`，并用于调用 `/api/v1/auth/me`、`/api/v1/dashboard`、`/api/v1/uploads`。

### 3.2 当前用户
- 方法：`GET`
- 路径：`/api/v1/auth/me`
- 鉴权：是
- 说明：返回当前登录用户的最小信息，用于前端初始化登录态、角色与权限展示。

#### 请求头
```http
Authorization: Bearer <access_token>
```

#### 成功响应 `200`
```json
{
  "id": 1,
  "username": "admin",
  "role_names": ["super_admin"],
  "permission_names": [
    "user_manage",
    "role_manage",
    "village_manage",
    "household_manage",
    "household_view",
    "member_manage",
    "member_view"
  ],
  "created_at": "2026-04-23T00:00:00Z"
}
```

#### 失败响应 `401`
```json
{
  "detail": "无效登录状态"
}
```

#### 联调说明
- 前端首次进入受保护页面前，应调用该接口确认当前 token 是否有效。
- 若返回 `401`，前端应清理本地 token 并跳转登录页。

## 4. 首页占位接口

### 4.1 Dashboard 占位接口
- 方法：`GET`
- 路径：`/api/v1/dashboard`
- 鉴权：是
- 权限：`member_view`
- 说明：阶段 3 的受保护业务占位接口，用于验证登录态、权限依赖和前后端最小受保护链路。

#### 请求头
```http
Authorization: Bearer <access_token>
```

#### 成功响应 `200`
```json
{
  "message": "阶段 3 业务占位接口已就绪",
  "current_user": "admin"
}
```

#### 未登录响应 `401`
```json
{
  "detail": "未登录或认证信息无效"
}
```

#### 权限不足响应 `403`
```json
{
  "detail": "权限不足"
}
```

#### 联调说明
- 当前默认管理员具备 `member_view`，可直接访问。
- 前端首页 `frontend/src/views/DashboardView.vue` 已接入此接口，可用来验证 Bearer Token 是否正确注入。

## 5. 上传接口

### 5.1 文件上传
- 方法：`POST`
- 路径：`/api/v1/uploads`
- 鉴权：是
- 说明：阶段 3 的最小上传接口，当前用于验证登录态保护、文件类型/大小校验与静态访问路径返回。

#### 请求头
```http
Authorization: Bearer <access_token>
Content-Type: multipart/form-data
```

#### 表单字段
- `file`：上传文件，当前仅支持图片。

#### 当前校验规则
- 允许类型：
  - `image/jpeg`
  - `image/png`
  - `image/webp`
- 大小限制：5MB

#### 成功响应 `200`
```json
{
  "uploaded_by": "admin",
  "filename": "generated-name.png",
  "content_type": "image/png",
  "size": 12345,
  "url": "/static/uploads/generated-name.png"
}
```

#### 未登录响应 `401`
```json
{
  "detail": "未登录或认证信息无效"
}
```

#### 校验失败响应 `400`
```json
{
  "detail": "不支持的文件类型"
}
```

#### 联调说明
- 前端上传验证页 `frontend/src/views/UploadDemoView.vue` 已接入该接口。
- 上传成功后，可使用返回的 `url` 验证静态访问路径是否可用。
- 当前阶段只提供最小上传能力，尚未实现成员照片命名规则、图片缩放、元数据入库和对象存储切换。

## 6. 最小联调顺序
1. 启动后端服务。
2. 打开 `http://127.0.0.1:8000/docs` 确认 OpenAPI 可访问。
3. 调用 `POST /api/v1/auth/login` 获取 token。
4. 使用该 token 调用 `GET /api/v1/auth/me`。
5. 使用该 token 调用 `GET /api/v1/dashboard`。
6. 使用该 token 调用 `POST /api/v1/uploads` 上传一张 png/jpg/webp 图片。
7. 验证返回的 `url` 可通过后端静态服务访问。

## 7. 阶段 3 接口验收点
- 登录成功可拿到 Bearer Token。
- 无 token 调用 `/api/v1/auth/me`、`/api/v1/dashboard`、`/api/v1/uploads` 时返回 `401`。
- 默认管理员调用 `/api/v1/dashboard` 返回 200。
- 上传图片时类型与大小校验生效。
- 上传成功后返回文件元信息与静态访问 URL。
- 前端已接入以上最小闭环接口，可完成基础联调。
