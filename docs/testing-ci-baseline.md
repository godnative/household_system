# 测试与 CI 最小门禁说明

## 阶段 0 目标
先建立最小可执行门禁，确保环境不是一次性搭建，而是可重复验证。

## 当前最小门禁
### 前端
- 依赖可安装：`pnpm install`
- 构建可执行：`pnpm exec vite build`

### 后端
- 虚拟环境可创建
- 依赖可安装：`pip install -r backend/requirements.txt`
- 代码可通过基础编译检查：`python -m compileall backend/app`

## 后续建议纳入
### 前端
- lint
- type-check
- 单元测试
- E2E 测试

### 后端
- pytest
- API 集成测试
- Alembic 迁移检查

## 静态资源检查
当前最小要求：
- `frontend/public/images/` 目录存在
- 欢迎页图片目录存在
- 关键迁移资源有明确映射路径

## CI 第一阶段建议
- 安装前端依赖
- 安装后端依赖
- 执行前端构建
- 执行后端基础编译检查
- 检查关键静态资源目录是否存在
