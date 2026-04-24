# 环境变量模板说明

## 前端
文件：`frontend/.env.example`

### 字段
- `APP_ENV`：环境名
- `APP_NAME`：应用名
- `API_BASE_URL`：后端 API 地址

## 后端
文件：`backend/.env.example`

### 字段
- `APP_ENV`：环境名
- `APP_NAME`：应用名
- `DEBUG`：调试开关
- `DATABASE_URL`：数据库连接串
- `UPLOAD_DIR`：上传目录
- `STATIC_SYSTEM_DIR`：系统静态资源目录
- `FRONTEND_ORIGIN`：允许的前端来源

## 约定
- 后端环境变量统一使用大写加下划线。
- 前端环境变量应在后续统一到 Vite 规范前缀。
- 本地、测试、生产的变量名保持一致，仅值不同。
- 禁止把敏感配置写入源码。
