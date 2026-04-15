# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

这是一个基于 PyQt5 开发的天主教堂家庭户籍管理系统，用于管理堂区、家庭成员信息及圣事记录（圣洗、坚振、婚配、病人傅油等）。采用 MVC 架构，使用 SQLAlchemy ORM 和 SQLite 数据库，实现了基于角色的权限控制系统（RBAC）。

## 常用命令

### 开发环境设置
```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境 (Windows)
venv\Scripts\activate

# 激活虚拟环境 (Linux/macOS)
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### 数据库初始化
```bash
# 首次运行前必须初始化数据库
python -m src.models.init_db
```

这将创建：
- 所有数据表结构
- 默认权限（7 种）和角色（3 种）
- 默认超级管理员账号：`admin/admin123`
- 默认堂区（编码：001）

### 运行应用
```bash
# 正常模式（需要登录）
python -m src.app

# 调试模式（跳过登录，直接以超级管理员身份进入主界面）
python -m src.app --debug
```

### 测试
```bash
# 运行登录测试
python test_login.py

# 运行权限测试
python test_permissions.py
```

## 代码架构

### 目录结构
```
src/
├── app.py                      # 应用入口，处理登录流程和窗口切换
├── models/                     # 数据模型层（SQLAlchemy ORM）
│   ├── base.py                # 数据库配置和 Base 类
│   ├── auth.py                # Role, Permission 模型（权限和角色）
│   ├── user.py                # User 模型（用户和登录）
│   ├── household.py           # Village, Household, Member 模型（堂区/家庭/成员）
│   └── init_db.py             # 数据库初始化脚本
├── services/                   # 业务逻辑层
│   ├── auth_service.py        # 认证服务（登录、密码验证）
│   ├── permission_service.py  # 权限检查服务
│   ├── database_service.py    # 数据库备份/还原服务
│   ├── village_service.py     # 堂区业务逻辑
│   ├── household_service.py   # 家庭业务逻辑
│   └── member_service.py      # 成员业务逻辑
├── views/                      # 视图层（PyQt5 GUI）
│   ├── login_view.py          # 登录界面（含记住密码功能）
│   ├── main_view.py           # 主界面框架（NavigationInterface）
│   ├── village_view.py        # 堂区管理界面
│   ├── household_management_view.py  # 家庭和成员管理主界面
│   ├── user_role_management_view.py  # 用户和角色管理界面
│   ├── settings_view.py       # 设置界面（数据库备份/还原）
│   ├── member_excel_renderer.py      # 成员信息 HTML 渲染
│   ├── household_excel_renderer.py   # 家庭信息 HTML 渲染
│   └── ui_components.py       # 通用 UI 组件
└── constants/
    └── permissions.py          # 权限和角色常量定义
```

### 数据流向
典型的操作流程（例如"添加成员"）：
1. **View 层**：用户在 `household_management_view.py` 中填写表单并点击"添加成员"
2. **View 层验证**：验证表单数据，处理照片上传（自动缩放至 120x160 像素）
3. **Service 层**：调用 `member_service.create_member()` 执行业务逻辑
4. **Model 层**：通过 SQLAlchemy 的 `Member` 模型写入数据库
5. **返回结果**：逐层返回 → View 刷新列表 → 显示成功消息

## 权限系统架构

### 三种角色
1. **超级管理员**（`ROLE_SUPER_ADMIN`）
   - 拥有所有权限（7 种权限）
   - 可访问所有堂区数据
   - 可管理用户和角色

2. **录入员**（`ROLE_DATA_ENTRY`）
   - 拥有 `household_manage` 和 `member_manage` 权限
   - 只能管理**所属堂区**的数据（由 `User.village_id` 指定）
   - 完整 CRUD 权限

3. **观察员**（`ROLE_OBSERVER`）
   - 拥有 `household_view` 和 `member_view` 权限
   - 可访问**多个堂区**（由 `User.accessible_villages` JSON 字段指定）
   - 只读权限，界面操作按钮自动禁用

### 七种权限
```python
# 定义在 src/constants/permissions.py
PERM_USER_MANAGE = 'user_manage'          # 用户管理
PERM_ROLE_MANAGE = 'role_manage'          # 角色管理
PERM_VILLAGE_MANAGE = 'village_manage'    # 堂区管理
PERM_HOUSEHOLD_MANAGE = 'household_manage'  # 家庭完整管理（CRUD）
PERM_HOUSEHOLD_VIEW = 'household_view'    # 家庭查看（只读）
PERM_MEMBER_MANAGE = 'member_manage'      # 成员完整管理（CRUD）
PERM_MEMBER_VIEW = 'member_view'          # 成员查看（只读）
```

### 权限检查机制
- **界面层**：`PermissionService.has_permission(user, permission_name)` 检查是否有权限
- **数据过滤**：
  - 超级管理员：查询所有堂区数据
  - 录入员：`query.filter(Village.id == user.village_id)`
  - 观察员：`query.filter(Village.id.in_(user.accessible_villages))`
- **操作限制**：根据权限动态禁用按钮（`setEnabled(False)`）

## 关键技术要点

### 数据库关系
- `User` ↔ `Role` (多对一)
- `Role` ↔ `Permission` (多对多，通过 `role_permissions` 关联表)
- `Village` ↔ `Household` (一对多)
- `Household` ↔ `Member` (一对多)
- `User.village_id`: 录入员所属堂区（外键）
- `User.accessible_villages`: 观察员可访问的堂区列表（JSON 字段）

### 照片处理
- 成员照片统一缩放至 **120x160 像素**（`Pillow` 库）
- 存储路径：`static/member_photos/{member_id}.jpg`
- 上传时自动 EXIF 方向校正
- HTML 模板中使用 Base64 编码嵌入照片

### 打印功能
- 使用 `QTextDocument` 加载 HTML 模板（`doc/a3.html` 和 `doc/a4.html`）
- 通过 `QPrinter` 调用系统打印对话框
- 支持分页打印：家庭信息第一页，每个成员单独一页
- HTML 模板使用 `{变量名}` 占位符，通过 `.replace()` 填充数据

### 登录界面
- 实现了现代化的 UI 设计（`login_ui.py` 和 `login_view.py`）
- 支持"记住密码"功能（密码使用 Base64 简单编码存储）
- 登录成功后发射 `login_success` 信号传递 `User` 对象

### 数据库备份与还原
- 备份：打开 `data/` 目录，用户手动复制 `household.db`
- 还原：选择备份文件，自动备份当前数据库（时间戳命名），然后替换
- 验证 SQLite 文件头（`SQLite format 3`）确保文件有效性

## 开发注意事项

### 添加新功能时
1. **检查权限**：确定操作需要哪个权限，在 `permissions.py` 中查找或添加常量
2. **Service 层优先**：业务逻辑应放在 `services/` 层，View 层只负责界面交互
3. **数据库迁移**：修改 Model 后需重新运行 `init_db.py`（会清空数据）
4. **权限过滤**：查询数据时必须根据用户角色过滤堂区（参考 `household_management_view.py`）

### 常见模式
- **获取当前用户权限**：`self.permission_service.has_permission(self.user, PERM_XXX_MANAGE)`
- **过滤堂区数据**：
  ```python
  if self.user.role.name == ROLE_SUPER_ADMIN:
      villages = db.query(Village).all()
  elif self.user.role.name == ROLE_DATA_ENTRY:
      villages = db.query(Village).filter(Village.id == self.user.village_id).all()
  elif self.user.role.name == ROLE_OBSERVER:
      villages = db.query(Village).filter(Village.id.in_(self.user.accessible_villages)).all()
  ```
- **禁用无权限按钮**：
  ```python
  self.add_button.setEnabled(self.can_manage_household)
  ```

### PyQt5 / PyQt-Fluent-Widgets
- 主界面使用 `FluentWindow` 和 `NavigationInterface` 提供侧边栏导航
- 列表使用 `TableWidget` 配合 `QStandardItemModel`
- 对话框使用 `MessageBox`（成功/错误提示）
- 信号槽连接：`button.clicked.connect(self.on_button_click)`

### 数据库会话管理
- 使用 `SessionLocal()` 创建会话
- 必须在 `finally` 块中调用 `db.close()`
- 事务失败时调用 `db.rollback()`

## 文档参考

- 完整开发文档：`PROJECT_DOCUMENTATION.md`（详细的 API 和功能说明）
- 登录界面文档：`LOGIN_UI_README.md`
- 项目结构说明：`PROJECT_STRUCTURE_LOGIN.md`
- 变更日志：`CHANGELOG_LOGIN_UI.md`
