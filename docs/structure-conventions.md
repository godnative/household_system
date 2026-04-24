# 目录结构约定

## 顶层目录
- `frontend/`：Web 前端项目
- `backend/`：Web 后端项目
- `docs/`：迁移过程文档、规范、计划
- `scripts/`：环境与迁移辅助脚本
- `deploy/`：部署与环境模板
- `tests-e2e/`：端到端测试
- `artifacts/`：截图、报告、样张、对账输出

## frontend/
- `src/`：源码
- `src/assets/`：会被打包的静态资源
- `src/components/`：通用组件
- `src/views/`：页面视图
- `src/router/`：路由配置
- `src/stores/`：状态管理
- `src/api/`：接口封装
- `public/`：直接暴露的公共静态资源
- `public/images/login/`：登录页图片
- `public/images/branding/`：品牌 Logo 等
- `public/images/home/`：欢迎页图片

## backend/
- `app/`：应用代码
- `app/api/`：API 路由
- `app/core/`：配置、常量、中间件
- `app/models/`：ORM 模型
- `app/schemas/`：请求/响应模型
- `app/services/`：业务服务
- `app/repositories/`：数据访问层
- `app/static/uploads/`：上传文件
- `app/static/system/`：系统内置静态资源
- `tests/`：后端测试

## 约定
- 上传资源与内置资源必须分开。
- 业务代码不得再直接引用旧桌面端相对路径。
- 新 Web 资源路径必须通过前端 public 目录或后端静态服务统一暴露。
