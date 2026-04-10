# 家庭户籍管理系统 (Household Management System)

> 一个基于 PyQt5 开发的天主教堂家庭户籍管理系统，用于管理堂区、家庭、成员信息及圣事记录。

---

## 📑 文档导航

- 🚀 **新手？请先阅读：** [快速开始](#2-快速开始-quick-start)
- 🔍 **查找功能？请看：** [功能代码映射表](#131-功能代码映射表)
- 💻 **开发新功能？请看：** [开发指南](#7-开发指南-development-guide)
- ❓ **遇到问题？请看：** [常见问题](#11-常见问题-faq) 和 [技术要点](#9-技术要点与解决方案-technical-solutions)

---

## 目录

1. [项目概述](#1-项目概述-project-overview)
2. [快速开始](#2-快速开始-quick-start)
3. [项目架构](#3-项目架构-architecture)
4. [数据库设计](#4-数据库设计-database-design)
5. [核心模块详解](#5-核心模块详解-core-modules)
6. [功能实现详解](#6-功能实现详解-feature-implementation)
7. [开发指南](#7-开发指南-development-guide)
8. [API 参考](#8-api-参考-api-reference)
9. [技术要点与解决方案](#9-技术要点与解决方案-technical-solutions)
10. [部署指南](#10-部署指南-deployment)
11. [常见问题](#11-常见问题-faq)
12. [附录](#12-附录-appendix)
13. [速查表](#13-速查表-quick-reference)

---

## 1. 项目概述 (Project Overview)

### 1.1 项目简介

**家庭户籍管理系统**是一个专门为天主教堂设计的户籍管理应用程序，用于管理教区内的堂区、家庭成员信息以及重要的圣事记录（圣洗、坚振、婚配、病人傅油等）。

该系统采用桌面应用形式，基于现代化的 PyQt5 框架开发，提供了直观的图形界面和完善的权限管理功能。

### 1.2 主要功能

#### 核心功能模块

1. **用户认证与权限管理**
   - 基于角色的权限控制（RBAC）
   - 支持超级管理员、堂区管理员、操作员等多种角色
   - 密码加密存储（bcrypt）

2. **堂区管理**
   - 堂区信息的增删改查
   - 堂区照片上传管理
   - 堂区编码唯一性验证

3. **家庭户籍管理**
   - 家庭基本信息管理（地址、片号、电话等）
   - 家庭成员列表展示
   - 户主设置功能
   - 批量成员管理

4. **成员信息管理**
   - 成员基本信息（姓名、性别、出生日期、教籍证件号等）
   - 成员照片上传（自动缩放至标准尺寸）
   - 与户主关系管理
   - 职业、文化程度等详细信息

5. **圣事记录管理**
   - **圣洗记录**：施行人、代父、日期、备注
   - **坚振记录**：施行人、代父、圣名、年龄、地点
   - **婚配记录**：主礼神父、证人、地点、事项
   - **病人傅油记录**：施行人、地点、死亡信息
   - **初领圣体记录**：日期记录
   - **补礼记录**：神父、地点、日期

6. **数据导出与打印**
   - 成员信息 HTML 格式导出
   - 基于 QTextEdit 的富文本显示
   - 支持打印预览

### 1.3 技术栈

| 技术 | 版本 | 用途 |
|------|------|------|
| **Python** | 3.8+ | 核心编程语言 |
| **PyQt5** | 5.15.10 | GUI 框架 |
| **PyQt-Fluent-Widgets** | latest | 现代化 UI 组件库 |
| **SQLAlchemy** | 1.4.52 | ORM 数据库操作 |
| **SQLite** | 3.x | 嵌入式数据库 |
| **bcrypt** | 4.0.1 | 密码加密 |
| **Pillow** | 10.2.0 | 图片处理 |
| **pydantic** | 2.6.1 | 数据验证 |
| **python-dotenv** | 1.0.0 | 环境变量管理 |

### 1.4 适用场景

- ✅ 天主教堂的教区户籍管理
- ✅ 堂区级别的信徒信息登记
- ✅ 家庭成员圣事记录存档
- ✅ 教籍证件编号管理
- ✅ 单机或小型网络环境使用

### 1.5 项目特色

- **现代化界面**：采用 Fluent Design 风格，界面美观易用
- **权限灵活**：基于角色的权限控制，支持多级管理
- **数据完整**：覆盖天主教圣事的各个方面
- **照片管理**：自动缩放照片至标准尺寸，避免布局破坏
- **跨平台**：支持 Windows、Linux、macOS
- **轻量级**：使用 SQLite 数据库，无需额外配置

---

## 2. 快速开始 (Quick Start)

### 2.1 环境要求

- **Python**: 3.8 或更高版本
- **操作系统**: Windows 10+, macOS 10.14+, Ubuntu 18.04+
- **磁盘空间**: 至少 100MB 可用空间
- **内存**: 至少 2GB RAM

### 2.2 安装步骤

#### 步骤 1: 克隆或下载项目

```bash
# 如果使用 git
git clone <repository-url>
cd household_system

# 或者直接下载并解压项目到本地目录
```

#### 步骤 2: 创建虚拟环境（推荐）

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/macOS
python3 -m venv venv
source venv/bin/activate
```

#### 步骤 3: 安装依赖

```bash
pip install -r requirements.txt
```

**requirements.txt 包含的依赖：**
```
PyQt5==5.15.10
SQLAlchemy==1.4.52
bcrypt==4.0.1
pydantic==2.6.1
python-dotenv==1.0.0
Pillow==10.2.0
PyQt-Fluent-Widgets[full]
```

#### 步骤 4: 创建数据目录

```bash
# Windows
mkdir data

# Linux/macOS
mkdir -p data
```

### 2.3 初始化数据库

在首次运行前，必须初始化数据库：

```bash
python -m src.models.init_db
```

**初始化脚本会自动创建：**
- ✅ 所有数据表结构
- ✅ 默认权限（user_manage, role_manage, village_manage, household_manage, member_manage）
- ✅ 默认角色（超级管理员、堂区管理员、操作员）
- ✅ 默认超级管理员账号：
  - 用户名: `admin`
  - 密码: `admin123`
- ✅ 默认堂区（编码：001）

**预期输出：**
```
数据库初始化成功！
```

### 2.4 运行应用

#### 正常模式（需要登录）

```bash
python -m src.app
```

使用默认账号登录：
- 用户名: `admin`
- 密码: `admin123`

#### 调试模式（跳过登录）

```bash
python -m src.app --debug
```

调试模式会自动创建一个临时的超级管理员用户对象，直接进入主界面，方便开发调试。

**使用虚拟环境的完整命令：**

```bash
# Windows
venv\Scripts\python.exe -m src.app --debug

# Linux/macOS
./venv/bin/python -m src.app --debug
```

### 2.5 首次使用指南

1. **登录系统**
   - 使用默认账号 `admin/admin123` 登录

2. **创建堂区**（可选）
   - 进入"堂区管理"模块
   - 点击"添加村"按钮
   - 填写堂区信息

3. **添加家庭**
   - 进入"家庭管理"模块
   - 选择堂区
   - 点击"添加家庭"按钮
   - 输入家庭编号、片号、地址等信息

4. **添加成员**
   - 在家庭列表中选择一个家庭
   - 切换到"成员管理"标签页
   - 点击"添加成员"按钮
   - 填写成员信息（基本信息、圣事记录等）
   - 可上传成员照片（会自动缩放至 120x160 像素）

5. **查看成员详情**
   - 选择成员后点击"查看详情"按钮
   - 系统会以 HTML 表格形式展示成员的完整信息

### 2.6 项目目录说明

初始化完成后，项目目录结构：

```
household_system/
├── data/                    # 数据库文件目录
│   └── household.db        # SQLite 数据库文件
├── doc/                    # 文档和模板文件
│   └── a3.html            # 成员信息 HTML 模板
├── src/                    # 源代码目录
│   ├── models/            # 数据模型
│   ├── services/          # 业务逻辑
│   ├── views/             # 界面视图
│   └── app.py             # 应用入口
├── static/                 # 静态文件
│   └── member_photos/     # 成员照片存储
├── venv/                   # 虚拟环境（不纳入版本控制）
├── requirements.txt        # Python 依赖
├── .gitignore             # Git 忽略文件
└── PROJECT_DOCUMENTATION.md  # 本文档
```

---

## 3. 项目架构 (Architecture)

### 3.1 目录结构

```
household_system/
│
├── data/                           # 数据存储
│   └── household.db               # SQLite 数据库
│
├── doc/                           # 文档和模板
│   └── a3.html                   # 成员信息 HTML 模板
│
├── src/                           # 源代码根目录
│   ├── __init__.py
│   ├── app.py                    # 应用程序入口
│   │
│   ├── models/                   # 数据模型层
│   │   ├── __init__.py
│   │   ├── base.py              # 数据库配置和 Base 类
│   │   ├── auth.py              # 用户认证相关模型
│   │   ├── user.py              # 用户模型
│   │   ├── household.py         # 堂区、家庭、成员模型
│   │   └── init_db.py           # 数据库初始化脚本
│   │
│   ├── services/                 # 业务逻辑层
│   │   ├── __init__.py
│   │   ├── auth_service.py      # 认证服务
│   │   ├── permission_service.py # 权限服务
│   │   ├── village_service.py   # 堂区服务
│   │   ├── household_service.py # 家庭服务
│   │   └── member_service.py    # 成员服务
│   │
│   ├── views/                    # 视图层（UI）
│   │   ├── __init__.py
│   │   ├── login_view.py        # 登录界面
│   │   ├── main_view.py         # 主界面
│   │   ├── village_view.py      # 堂区管理界面
│   │   ├── household_management_view.py  # 家庭管理界面
│   │   ├── member_excel_renderer.py      # 成员信息 HTML 渲染
│   │   └── ui_components.py     # UI 通用组件
│   │
│   └── controllers/              # 控制器层（预留）
│       └── __init__.py
│
├── static/                        # 静态资源
│   └── member_photos/            # 成员照片存储
│
├── test/                          # 测试文件
│   └── test1.py
│
├── venv/                          # Python 虚拟环境（忽略）
├── .gitignore                     # Git 忽略配置
├── requirements.txt               # Python 依赖清单
└── PROJECT_DOCUMENTATION.md       # 项目文档（本文件）
```

### 3.2 架构设计

本项目采用 **MVC (Model-View-Controller)** 分层架构，并增加了 **Service 层**来处理业务逻辑。

```
┌─────────────────────────────────────────────────────┐
│                   用户界面 (User)                    │
└───────────────────┬─────────────────────────────────┘
                    │
        ┌───────────▼───────────┐
        │  Views 层 (视图层)     │  PyQt5 GUI 组件
        │  - login_view.py      │  负责展示和用户交互
        │  - main_view.py       │
        │  - village_view.py    │
        │  - household_*.py     │
        └───────────┬───────────┘
                    │
        ┌───────────▼────────────┐
        │ Controllers 层(控制器)  │  处理用户输入
        │  (预留，部分逻辑在 View) │  协调 View 和 Service
        └───────────┬────────────┘
                    │
        ┌───────────▼────────────┐
        │  Services 层(业务逻辑)  │  实现业务规则
        │  - auth_service.py     │  数据验证和转换
        │  - village_service.py  │  事务处理
        │  - household_service.py│
        │  - member_service.py   │
        └───────────┬────────────┘
                    │
        ┌───────────▼────────────┐
        │   Models 层(数据模型)   │  SQLAlchemy ORM
        │  - auth.py             │  数据库映射
        │  - user.py             │  数据持久化
        │  - household.py        │
        └───────────┬────────────┘
                    │
        ┌───────────▼────────────┐
        │   Database (数据库)     │  SQLite 3
        │   data/household.db    │  存储所有数据
        └────────────────────────┘
```

### 3.3 数据流向

#### 典型的数据流程（以"添加成员"为例）

```
1. 用户操作
   │
   ├─> [View] household_management_view.py
   │   └─> 用户点击"添加成员"按钮
   │   └─> 填写成员信息表单
   │   └─> 点击"确定"按钮
   │
2. 事件处理
   │
   ├─> [View] add_member() 方法
   │   └─> 验证表单数据
   │   └─> 处理照片上传（resize_and_save_photo）
   │   └─> 调用 Service 层
   │
3. 业务逻辑
   │
   ├─> [Service] member_service.py
   │   └─> create_member() 方法
   │   └─> 数据格式化和验证
   │   └─> 调用 Model 层
   │
4. 数据持久化
   │
   ├─> [Model] household.py
   │   └─> Member 模型
   │   └─> SQLAlchemy 处理
   │   └─> 写入数据库
   │
5. 返回结果
   │
   └─> 逐层返回 → View 更新界面 → 显示成功消息
```

### 3.4 模块依赖关系

```
app.py (应用入口)
├─> models.__init__.py (导入所有模型)
│   ├─> models.base (数据库配置)
│   ├─> models.auth (Role, Permission)
│   ├─> models.user (User)
│   └─> models.household (Village, Household, Member)
│
├─> views.login_view (登录界面)
│   └─> services.auth_service (认证服务)
│       └─> models.user
│
└─> views.main_view (主界面)
    ├─> views.village_view (堂区管理)
    │   └─> services.village_service
    │       └─> models.household (Village)
    │
    └─> views.household_management_view (家庭管理)
        ├─> services.household_service
        │   └─> models.household (Household)
        │
        ├─> services.member_service
        │   └─> models.household (Member)
        │
        └─> views.member_excel_renderer (HTML 渲染)
```

### 3.5 设计模式

项目中使用的主要设计模式：

1. **MVC 模式**
   - Model: models/ 目录
   - View: views/ 目录
   - Controller: 部分逻辑在 views 中，controllers/ 目录预留

2. **Service 层模式**
   - 将业务逻辑从 View 和 Model 中分离
   - 提高代码复用性和可测试性

3. **单例模式**
   - `SessionLocal` 数据库会话工厂
   - `Base` 声明式基类

4. **工厂模式**
   - `get_db()` 函数生成数据库会话

5. **策略模式**
   - 基于角色的权限检查 (`check_permission`)

### 3.6 技术选型理由

| 技术 | 选型理由 |
|------|---------|
| **PyQt5** | 成熟的跨平台 GUI 框架，性能优秀，组件丰富 |
| **SQLAlchemy** | 强大的 ORM 框架，简化数据库操作，支持多种数据库 |
| **SQLite** | 嵌入式数据库，无需单独安装，适合单机应用 |
| **bcrypt** | 业界标准的密码哈希算法，安全性高 |
| **Fluent-Widgets** | 现代化 UI 组件，符合 Microsoft Fluent Design 规范 |
| **Pillow** | Python 图像处理标准库，功能全面 |

---

## 4. 数据库设计 (Database Design)

### 4.1 ER 图

```
┌─────────────────┐         ┌──────────────────┐
│   permissions   │◄────┐   │      roles       │
│─────────────────│     │   │──────────────────│
│ id (PK)         │     │   │ id (PK)          │
│ name            │     │   │ name             │
│ description     │     │   │ description      │
└─────────────────┘     │   └────────┬─────────┘
                        │            │
                        │            │ 1
              ┌─────────┴────────┐   │
              │ role_permissions │   │
              │──────────────────│   │
              │ role_id (FK)     │   │
              │ permission_id(FK)│   │
              └──────────────────┘   │
                        M            │
                                     │
┌─────────────────┐                 │ M
│     users       │◄────────────────┘
│─────────────────│         1
│ id (PK)         │◄────────────────┐
│ username        │                 │
│ password_hash   │                 │
│ role_id (FK)    │                 │ 1
│ village_id (FK) │◄───┐            │
│ created_at      │    │            │
│ updated_at      │    │            │
└─────────────────┘    │            │
                       │            │
                       │ M          │
                       │            │
┌─────────────────┐    │            │
│    villages     │────┘            │
│─────────────────│    1            │
│ id (PK)         │                 │
│ name            │                 │
│ code (UNIQUE)   │                 │
│ establishment_  │                 │
│   date          │                 │
│ village_priest  │                 │
│ address         │                 │
│ description     │                 │
│ photo           │                 │
│ created_at      │                 │
│ updated_at      │                 │
└────────┬────────┘                 │
         │ 1                        │
         │                          │
         │ M                        │
┌────────▼────────┐                 │
│   households    │                 │
│─────────────────│                 │
│ id (PK)         │                 │
│ village_id (FK) │                 │
│ household_code  │                 │
│ plot_number     │                 │
│ address         │                 │
│ phone           │                 │
│ head_of_        │                 │
│   household     │                 │
│ created_at      │                 │
│ updated_at      │                 │
└────────┬────────┘                 │
         │ 1                        │
         │                          │
         │ M                        │
┌────────▼────────┐                 │
│     members     │                 │
│─────────────────│                 │
│ id (PK)         │                 │
│ household_id(FK)│                 │
│ name            │                 │
│ gender          │                 │
│ birth_date      │                 │
│ baptismal_name  │                 │
│ relation_to_head│                 │
│ education       │                 │
│ move_in_date    │                 │
│ occupation      │                 │
│ church_id       │                 │
│ photo           │                 │
│ [圣洗/坚振/婚配等]│                 │
│ created_at      │                 │
│ updated_at      │                 │
└─────────────────┘                 │
                                    │
           (堂区管理员可管理本村数据)  │
                └────────────────────┘
```

### 4.2 表结构说明

#### 4.2.1 用户权限表

**permissions (权限表)**

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| id | INTEGER | PRIMARY KEY | 权限 ID |
| name | VARCHAR(50) | UNIQUE, NOT NULL | 权限名称（如 user_manage） |
| description | TEXT | | 权限描述 |

**默认权限：**
- `user_manage` - 用户管理权限
- `role_manage` - 角色管理权限
- `village_manage` - 堂区管理权限
- `household_manage` - 家庭管理权限
- `member_manage` - 成员管理权限

---

**roles (角色表)**

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| id | INTEGER | PRIMARY KEY | 角色 ID |
| name | VARCHAR(50) | UNIQUE, NOT NULL | 角色名称 |
| description | TEXT | | 角色描述 |

**默认角色：**
1. **超级管理员** - 拥有所有权限
2. **堂区管理员** - 拥有 household_manage 和 member_manage 权限
3. **操作员** - 仅拥有 member_manage 权限

---

**role_permissions (角色权限关联表)**

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| role_id | INTEGER | PRIMARY KEY, FOREIGN KEY | 角色 ID |
| permission_id | INTEGER | PRIMARY KEY, FOREIGN KEY | 权限 ID |

多对多关系，一个角色可以有多个权限，一个权限可以属于多个角色。

---

**users (用户表)**

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| id | INTEGER | PRIMARY KEY | 用户 ID |
| username | VARCHAR(50) | UNIQUE, NOT NULL | 用户名 |
| password_hash | VARCHAR(128) | NOT NULL | 密码哈希值（bcrypt） |
| role_id | INTEGER | FOREIGN KEY | 所属角色 ID |
| village_id | INTEGER | FOREIGN KEY, NULLABLE | 管理的堂区 ID（可选） |
| created_at | DATETIME | DEFAULT now() | 创建时间 |
| updated_at | DATETIME | DEFAULT now() | 更新时间 |

**关联关系：**
- 一个用户属于一个角色（多对一）
- 一个用户可以管理一个堂区（多对一，可选）

---

#### 4.2.2 堂区表

**villages (堂区表)**

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| id | INTEGER | PRIMARY KEY | 堂区 ID |
| name | VARCHAR(100) | NOT NULL | 堂区名称 |
| code | VARCHAR(20) | UNIQUE, NOT NULL | 堂区编码（唯一） |
| establishment_date | DATE | NOT NULL | 建堂日期 |
| village_priest | VARCHAR(50) | NOT NULL | 本堂神父 |
| address | VARCHAR(200) | NOT NULL | 详细地址 |
| description | TEXT | | 堂区描述 |
| photo | VARCHAR(255) | | 堂区照片路径 |
| created_at | DATETIME | DEFAULT now() | 创建时间 |
| updated_at | DATETIME | DEFAULT now() | 更新时间 |

**关联关系：**
- 一个堂区可以有多个家庭（一对多）
- 一个堂区可以有多个管理用户（一对多）

---

#### 4.2.3 家庭表

**households (家庭表)**

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| id | INTEGER | PRIMARY KEY | 家庭 ID |
| village_id | INTEGER | FOREIGN KEY, NOT NULL | 所属堂区 ID |
| household_code | VARCHAR(20) | NOT NULL | 家庭编号 |
| plot_number | INTEGER | NOT NULL | 片号 |
| address | VARCHAR(200) | NOT NULL | 详细地址 |
| phone | VARCHAR(20) | | 联系电话 |
| head_of_household | VARCHAR(50) | | 户主姓名 |
| created_at | DATETIME | DEFAULT now() | 创建时间 |
| updated_at | DATETIME | DEFAULT now() | 更新时间 |

**关联关系：**
- 一个家庭属于一个堂区（多对一）
- 一个家庭可以有多个成员（一对多）

**索引：**
- `household_code` 字段建立索引，提高查询效率

---

#### 4.2.4 成员表

**members (成员表)**

这是系统中最复杂的表，包含成员基本信息和各种圣事记录。

##### 基本信息字段

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| id | INTEGER | PRIMARY KEY | 成员 ID |
| household_id | INTEGER | FOREIGN KEY, NOT NULL | 所属家庭 ID |
| name | VARCHAR(50) | NOT NULL | 姓名 |
| gender | VARCHAR(10) | NOT NULL | 性别（男/女） |
| birth_date | DATE | | 出生日期 |
| baptismal_name | VARCHAR(50) | | 圣名 |
| relation_to_head | VARCHAR(20) | | 与户主关系 |
| education | VARCHAR(50) | | 文化程度 |
| move_in_date | DATE | | 迁入日期 |
| occupation | VARCHAR(100) | | 从事职业 |
| church_id | VARCHAR(50) | | 教籍证件编号 |
| photo | VARCHAR(255) | | 照片路径 |

##### 圣洗信息字段

| 字段名 | 类型 | 说明 |
|--------|------|------|
| baptism_priest | VARCHAR(50) | 圣洗施行人（神父） |
| baptism_godparent | VARCHAR(50) | 圣洗代父/代母 |
| baptism_date | DATE | 领洗日期 |
| baptism_note | TEXT | 圣洗备注 |

##### 初领圣体信息

| 字段名 | 类型 | 说明 |
|--------|------|------|
| first_communion_date | DATE | 初领圣体日期 |

##### 补礼信息字段

| 字段名 | 类型 | 说明 |
|--------|------|------|
| supplementary_priest | VARCHAR(50) | 补礼神父 |
| supplementary_place | VARCHAR(100) | 补礼地点 |
| supplementary_date | DATE | 补礼日期 |

##### 坚振信息字段

| 字段名 | 类型 | 说明 |
|--------|------|------|
| confirmation_date | DATE | 坚振日期 |
| confirmation_priest | VARCHAR(50) | 坚振施行人（主教） |
| confirmation_godparent | VARCHAR(50) | 坚振代父/代母 |
| confirmation_name | VARCHAR(50) | 坚振圣名 |
| confirmation_age | INTEGER | 坚振年龄 |
| confirmation_place | VARCHAR(100) | 坚振地点 |

##### 婚配信息字段

| 字段名 | 类型 | 说明 |
|--------|------|------|
| marriage_date | DATE | 婚配日期 |
| marriage_priest | VARCHAR(50) | 婚配主礼神父 |
| marriage_witness | VARCHAR(100) | 婚配证人 |
| marriage_dispensation_item | VARCHAR(100) | 婚配事项 |
| marriage_dispensation_priest | VARCHAR(50) | 婚配神父 |
| marriage_place | VARCHAR(100) | 婚配地点 |

##### 病人傅油信息字段

| 字段名 | 类型 | 说明 |
|--------|------|------|
| anointing_date | DATE | 病人傅油日期 |
| anointing_priest | VARCHAR(50) | 病人傅油施行人 |
| anointing_place | VARCHAR(100) | 病人傅油地点 |
| death_date | DATE | 死亡日期 |
| death_age | INTEGER | 死亡年龄 |

##### 其他字段

| 字段名 | 类型 | 说明 |
|--------|------|------|
| association | VARCHAR(100) | 所属善会 |
| note | TEXT | 备注 |
| created_at | DATETIME | 创建时间 |
| updated_at | DATETIME | 更新时间 |

**关联关系：**
- 一个成员属于一个家庭（多对一）

### 4.3 字段说明

#### 日期字段默认值处理

系统中的日期字段如果为空，会使用默认值 `1752-09-14`（SQLite 支持的最小日期）。

在显示时，如果日期等于 `1752-09-14`，会显示为"无"。

**示例代码（member_excel_renderer.py:16）：**
```python
html = html.replace('出生日期占位', 
    f'{str(member.birth_date) if str(member.birth_date) != "1752-09-14" else "无"}', 1)
```

#### 照片字段处理

照片字段存储的是相对路径，格式为：`member_photos/文件名.jpg`

实际存储路径：`static/member_photos/文件名.jpg`

照片会在上传时自动缩放至 **120x160 像素**，使用中心裁剪方式保持纵横比。

### 4.4 数据库初始化流程

```python
# src/models/init_db.py

def init_database():
    1. 删除所有表（Base.metadata.drop_all）
    2. 重新创建所有表（Base.metadata.create_all）
    3. 创建默认权限（5个）
    4. 创建默认角色（3个）并分配权限
    5. 创建默认超级管理员用户（admin/admin123）
    6. 创建默认堂区（编码001）
    7. 提交事务
```

---

## 5. 核心模块详解 (Core Modules)

### 5.1 Models 层（数据模型）

Models 层负责定义数据结构和数据库映射，使用 SQLAlchemy ORM 框架。

#### 5.1.1 base.py - 数据库配置

**文件位置**: [src/models/base.py](src/models/base.py)

```python
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# 数据库文件路径
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data', 'household.db')

# 创建数据库引擎
engine = create_engine(f'sqlite:///{DB_PATH}', echo=False)

# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 创建基础模型类
Base = declarative_base()
```

**关键概念**:
- `DB_PATH`: 数据库文件路径，位于项目根目录的 `data/household.db`
- `engine`: SQLAlchemy 引擎，负责与数据库通信
- `SessionLocal`: 会话工厂，用于创建数据库会话
- `Base`: 声明式基类，所有模型类继承此类

#### 5.1.2 auth.py - 认证相关模型

**文件位置**: [src/models/auth.py](src/models/auth.py)

**定义的模型**:
- `Role` - 角色模型
- `Permission` - 权限模型
- `role_permissions` - 角色权限关联表（多对多）

**关键关系**:
```python
# 角色和权限的多对多关系
role_permissions = Table('role_permissions', Base.metadata,
    Column('role_id', Integer, ForeignKey('roles.id'), primary_key=True),
    Column('permission_id', Integer, ForeignKey('permissions.id'), primary_key=True)
)

class Role(Base):
    permissions = relationship('Permission', secondary=role_permissions, back_populates='roles')

class Permission(Base):
    roles = relationship('Role', secondary=role_permissions, back_populates='permissions')
```

#### 5.1.3 user.py - 用户模型

**文件位置**: [src/models/user.py](src/models/user.py)

**User 模型关联关系**:
- 属于一个角色 (多对一)
- 可以管理一个堂区 (多对一，可选)

```python
class User(Base):
    role = relationship('Role', back_populates='users')
    village = relationship('Village', back_populates='users')
```

#### 5.1.4 household.py - 教堂户籍模型

**文件位置**: [src/models/household.py](src/models/household.py)

**定义的模型**:
1. **Village (堂区)**
   - 关联: households (一对多), users (一对多)

2. **Household (家庭)**
   - 关联: village (多对一), members (一对多)
   - 重要字段: `household_code`, `plot_number`, `head_of_household`

3. **Member (成员)**
   - 关联: household (多对一)
   - 包含: 基本信息 + 5大类圣事记录（圣洗、坚振、婚配、病人傅油、补礼）

**级联删除**:
```python
class Village(Base):
    households = relationship('Household', back_populates='village', cascade='all, delete-orphan')

class Household(Base):
    members = relationship('Member', back_populates='household', cascade='all, delete-orphan')
```

删除堂区会自动删除其下所有家庭，删除家庭会自动删除其下所有成员。

#### 5.1.5 init_db.py - 数据库初始化

**文件位置**: [src/models/init_db.py](src/models/init_db.py)

**初始化流程**:
```python
def init_database():
    # 1. 删除并重建表结构
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    
    # 2. 创建默认权限
    permissions = [
        Permission(name='user_manage', description='用户管理'),
        Permission(name='role_manage', description='角色管理'),
        Permission(name='village_manage', description='堂区管理'),
        Permission(name='household_manage', description='家庭管理'),
        Permission(name='member_manage', description='成员管理')
    ]
    
    # 3. 创建默认角色并分配权限
    admin_role.permissions = permissions  # 超级管理员：所有权限
    village_admin_role.permissions = permissions[3:]  # 堂区管理员：家庭和成员
    operator_role.permissions = [permissions[4]]  # 操作员：仅成员
    
    # 4. 创建默认超级管理员用户（admin/admin123）
    # 5. 创建默认堂区（编码001）
```

---

### 5.2 Services 层（业务逻辑）

Services 层封装业务逻辑，提供数据操作接口，遵循单一职责原则。

#### 5.2.1 auth_service.py - 认证服务

**文件位置**: [src/services/auth_service.py](src/services/auth_service.py)

**主要方法**:

| 方法 | 功能 | 参数 | 返回值 |
|------|------|------|--------|
| `verify_password` | 验证密码 | plain_password, hashed_password | bool |
| `get_password_hash` | 获取密码哈希 | password | str |
| `authenticate_user` | 验证用户身份 | db, username, password | User 或 None |
| `check_permission` | 检查用户权限 | user, permission_name | bool |
| `create_user` | 创建新用户 | db, username, password, role_id, village_id | User |
| `update_user` | 更新用户信息 | db, user_id, **kwargs | User |
| `delete_user` | 删除用户 | db, user_id | bool |

**使用示例**:
```python
from src.services.auth_service import AuthService

# 验证用户
user = AuthService.authenticate_user(db, 'admin', 'admin123')

# 检查权限
has_permission = AuthService.check_permission(user, 'village_manage')
```

#### 5.2.2 village_service.py - 堂区服务

**主要方法**:
- `get_all_villages(db)` - 获取所有堂区
- `get_village_by_id(db, village_id)` - 根据 ID 获取堂区
- `search_villages(db, keyword)` - 搜索堂区
- `create_village(db, name, code, ...)` - 创建堂区
- `update_village(db, village_id, **kwargs)` - 更新堂区
- `delete_village(db, village_id)` - 删除堂区

#### 5.2.3 household_service.py - 家庭服务

**文件位置**: [src/services/household_service.py](src/services/household_service.py)

**主要方法**:

```python
class HouseholdService:
    @staticmethod
    def get_all_households(db: Session, village_id: int = None):
        """获取所有家庭，可按村过滤"""
        query = db.query(Household).options(joinedload(Household.village))
        if village_id:
            query = query.filter(Household.village_id == village_id)
        return query.all()
    
    @staticmethod
    def search_households(db: Session, keyword: str = None, village_id: int = None):
        """搜索家庭（支持家庭编号、户主姓名、地址、电话）"""
        query = db.query(Household).options(joinedload(Household.village))
        
        if keyword:
            query = query.filter(
                Household.household_code.ilike(f'%{keyword}%') |
                Household.head_of_household.ilike(f'%{keyword}%') |
                Household.address.ilike(f'%{keyword}%') |
                Household.phone.ilike(f'%{keyword}%')
            )
        
        return query.all()
```

**特点**:
- 使用 `joinedload` 预加载关联数据，减少 N+1 查询问题
- 支持模糊搜索（ilike）
- 支持按堂区过滤

#### 5.2.4 member_service.py - 成员服务

**主要方法**:
- `get_all_members(db, household_id)` - 获取家庭的所有成员
- `get_member_by_id(db, member_id)` - 根据 ID 获取成员
- `search_members(db, keyword, household_id)` - 搜索成员
- `create_member(db, household_id, name, gender, ...)` - 创建成员
- `update_member(db, member_id, **kwargs)` - 更新成员
- `delete_member(db, member_id)` - 删除成员

---

### 5.3 Views 层（界面视图）

Views 层负责界面展示和用户交互，基于 PyQt5 和 PyQt-Fluent-Widgets。

#### 5.3.1 login_view.py - 登录界面

**文件位置**: [src/views/login_view.py](src/views/login_view.py)

**功能**:
- 用户登录表单
- 用户名和密码验证
- 登录成功后发射信号 `login_success`

**信号**:
```python
class LoginView(QWidget):
    login_success = pyqtSignal(object)  # 登录成功信号，传递 User 对象
```

#### 5.3.2 main_view.py - 主界面

**文件位置**: [src/views/main_view.py](src/views/main_view.py)

**功能**:
- 使用 `MSFluentWindow` 实现现代化侧边导航栏
- 根据用户权限动态加载导航项
- 管理各个子界面的切换

**导航项权限控制**:
```python
# 系统管理（需要 user_manage 或 role_manage 权限）
if AuthService.check_permission(self.user, 'user_manage') or \
   AuthService.check_permission(self.user, 'role_manage'):
    self.addSubInterface(sys_page, FIF.SETTING, '系统管理')

# 堂区管理（需要 village_manage 权限）
if AuthService.check_permission(self.user, 'village_manage'):
    self.addSubInterface(village_page, FIF.HOME, '堂区管理')

# 家庭管理（需要 household_manage 或 member_manage 权限）
if AuthService.check_permission(self.user, 'household_manage') or \
   AuthService.check_permission(self.user, 'member_manage'):
    self.addSubInterface(household_management_page, FIF.HOME, '家庭管理')
```

#### 5.3.3 village_view.py - 堂区管理界面

**主要功能**:
- 堂区列表展示（表格）
- 添加/编辑/删除堂区
- 堂区照片上传
- 堂区搜索

#### 5.3.4 household_management_view.py - 家庭管理界面

**文件位置**: [src/views/household_management_view.py](src/views/household_management_view.py)  
**代码行数**: 约 1900 行（项目最大的视图文件）

**布局结构**:
```
┌─────────────────────────────────────────────────────┐
│  堂区选择下拉框                                        │
├────────────────────┬────────────────────────────────┤
│                    │                                │
│  左侧: 家庭管理     │  右侧: 成员管理 (TabBar)        │
│  - 家庭列表表格     │  - Tab 1: 成员表格             │
│  - 添加/编辑/删除   │  - Tab 2: 成员详情 (HTML)      │
│                    │  - Tab 3: 成员详情 (HTML)      │
│  (42% 宽度)        │  (58% 宽度)                    │
│                    │                                │
└────────────────────┴────────────────────────────────┘
```

**核心功能**:

1. **家庭管理（左侧）**
   - 家庭列表展示（家庭编号、片号、地址、电话、户主）
   - 添加家庭 (`add_household` 方法)
   - 编辑家庭 (`edit_household` 方法)
   - 删除家庭 (`delete_household` 方法)
   - 选择家庭后自动加载成员

2. **成员管理（右侧）**
   - 使用 `TabBar` 实现多标签页
   - Tab 1 固定为成员表格视图
   - 动态添加成员详情 Tab（每个成员一个 Tab）
   - 添加成员 (`add_member` 方法)
   - 编辑成员 (`edit_member` 方法)
   - 删除成员 (`delete_member` 方法)
   - 设为户主 (`set_as_head` 方法)
   - 查看成员详情 (`load_member_details` 方法)

**关键方法**:

```python
def resize_and_save_photo(source_path, target_path, target_width=120, target_height=160):
    """
    调整照片尺寸并保存
    
    使用 Qt.KeepAspectRatioByExpanding 确保填满目标尺寸
    使用中心裁剪避免变形
    """
    pixmap = QPixmap(source_path)
    scaled_pixmap = pixmap.scaled(
        target_width, target_height,
        Qt.KeepAspectRatioByExpanding,
        Qt.SmoothTransformation
    )
    
    # 居中裁剪
    if scaled_pixmap.width() > target_width or scaled_pixmap.height() > target_height:
        x = (scaled_pixmap.width() - target_width) // 2
        y = (scaled_pixmap.height() - target_height) // 2
        scaled_pixmap = scaled_pixmap.copy(x, y, target_width, target_height)
    
    scaled_pixmap.save(target_path, quality=90)
```

**成员信息表单字段** (add_member/edit_member 对话框):
- 基本信息: 姓名、性别、出生日期、圣名、与户主关系、文化程度、迁入日期、职业、教籍证件号
- 照片上传
- 圣洗信息: 施行人、代父、日期、备注
- 初领圣体时间
- 补礼信息: 神父、地点、日期
- 坚振信息: 日期、施行人、代父、圣名、年龄、地点
- 婚配信息: 日期、主礼神父、证人、事项、神父、地点
- 病人傅油信息: 日期、施行人、地点、死亡日期、年龄
- 其他: 所属善会、备注

#### 5.3.5 member_excel_renderer.py - 成员信息 HTML 渲染

**文件位置**: [src/views/member_excel_renderer.py](src/views/member_excel_renderer.py)

**核心函数**:
```python
def get_member_excel_html(member):
    """
    生成成员信息的 HTML 表格，使用 a3.html 模板
    
    返回: HTML 字符串，可直接用于 QTextEdit.setHtml()
    """
```

**工作流程**:
1. 读取 HTML 模板 (`doc/a3.html`)
2. 替换占位符为实际数据
3. 处理日期字段（`1752-09-14` 显示为"无"）
4. 处理照片路径（转换为 file:// URL）
5. 返回完整 HTML

**照片路径处理**:
```python
if member.photo:
    # 构建绝对路径
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    photo_abs_path = os.path.join(project_root, 'static', member.photo)
    
    # 转换为 file:// URL (QTextEdit 需要)
    photo_url = Path(photo_abs_path).as_uri()
    
    # 插入 img 标签
    html = html.replace('图片占位', 
        f'<img src="{photo_url}" style="width: 120px; height: 160px; object-fit: cover;" />')
```

---

## 6. 功能实现详解 (Feature Implementation)

### 6.1 用户认证与权限管理

#### 6.1.1 登录流程

```
1. 用户输入用户名和密码
   │
2. [LoginView] 验证表单
   │
3. [AuthService.authenticate_user()]
   ├─> 查询用户
   ├─> 验证密码 (bcrypt.checkpw)
   └─> 返回 User 对象
   │
4. [LoginView] 发射 login_success 信号
   │
5. [App] 接收信号，关闭登录窗口，打开主窗口
```

**代码位置**: [src/views/login_view.py](src/views/login_view.py), [src/services/auth_service.py](src/services/auth_service.py:17-24)

#### 6.1.2 权限检查机制

**实现原理**:
```python
def check_permission(user: User, permission_name: str) -> bool:
    """
    检查用户是否有指定权限
    
    通过用户的角色关联到权限表，遍历角色的所有权限进行匹配
    """
    if not user or not user.role:
        return False
    
    for permission in user.role.permissions:
        if permission.name == permission_name:
            return True
    return False
```

**使用场景**:
- 主界面动态加载导航项
- 视图中隐藏/禁用特定功能
- Service 层拦截非法操作

#### 6.1.3 角色管理

**默认角色及权限**:

| 角色 | 权限 | 用途 |
|------|------|------|
| 超级管理员 | user_manage, role_manage, village_manage, household_manage, member_manage | 系统管理员，拥有所有权限 |
| 堂区管理员 | household_manage, member_manage | 管理指定堂区的家庭和成员 |
| 操作员 | member_manage | 仅操作成员数据 |

---

### 6.2 堂区管理

**操作流程**:
1. 用户点击"添加村"按钮
2. 弹出对话框，填写堂区信息
3. 可选上传堂区照片
4. 保存到数据库
5. 刷新堂区列表

**关键验证**:
- 堂区编码唯一性
- 建堂日期格式
- 必填字段检查

**代码位置**: [src/views/village_view.py](src/views/village_view.py)

---

### 6.3 家庭户籍管理

#### 6.3.1 家庭信息管理

**家庭字段**:
- 家庭编号（household_code）：唯一标识
- 片号（plot_number）：用于分区管理
- 地址（address）：详细住址
- 电话（phone）：联系方式
- 户主姓名（head_of_household）：从成员中选择

**操作流程**:
```
添加家庭:
1. 选择堂区
2. 填写家庭编号、片号、地址、电话
3. 保存（户主暂为空）
4. 添加成员后，可设置户主

编辑家庭:
1. 选择家庭
2. 修改信息（户主只读，在成员管理中设置）
3. 保存更新

删除家庭:
1. 选择家庭
2. 确认删除
3. 级联删除所有成员
```

#### 6.3.2 成员信息管理

**成员添加流程**:
```
1. 选择家庭
2. 点击"添加成员"按钮
3. 填写成员信息:
   ├─ 基本信息（必填：姓名、性别）
   ├─ 圣事记录（选填）
   └─ 照片上传（可选）
4. 照片自动缩放至 120x160 像素
5. 保存到数据库
6. 刷新成员列表
```

**代码位置**: [src/views/household_management_view.py](src/views/household_management_view.py:800-1100) (add_member 方法)

#### 6.3.3 成员照片处理

**实现细节**:

```python
# 1. 用户选择照片文件
photo_path, _ = QFileDialog.getOpenFileName(
    self, '选择照片', '', 
    'Images (*.png *.jpg *.jpeg *.bmp *.gif)'
)

# 2. 生成唯一文件名
import uuid
photo_filename = f"{uuid.uuid4().hex}.jpg"
photo_path_save = os.path.join(photo_dir, photo_filename)

# 3. 调整照片尺寸并保存
if resize_and_save_photo(photo_path, photo_path_save, target_width=120, target_height=160):
    photo = f'member_photos/{photo_filename}'  # 保存相对路径到数据库
else:
    # 处理失败，显示警告
```

**照片处理原理**:
1. 使用 `Qt.KeepAspectRatioByExpanding` 缩放，确保填满目标尺寸
2. 如果缩放后超出目标尺寸，进行中心裁剪
3. 保存为 JPG 格式，quality=90

**为什么要自动缩放？**
- 避免大尺寸照片破坏 HTML 表格布局
- 减少存储空间占用
- 统一照片规格，美观整洁

**代码位置**: [src/views/household_management_view.py](src/views/household_management_view.py:16-50) (resize_and_save_photo 函数)

---

### 6.4 圣事记录管理

天主教七件圣事中，本系统管理以下圣事记录：

#### 6.4.1 圣洗记录

**字段**:
- 施行人（baptism_priest）：施洗神父
- 代父（baptism_godparent）：代父或代母
- 领洗日期（baptism_date）
- 备注（baptism_note）

#### 6.4.2 坚振记录

**字段**:
- 坚振日期（confirmation_date）
- 施行人（confirmation_priest）：通常是主教
- 代父（confirmation_godparent）
- 坚振圣名（confirmation_name）
- 坚振年龄（confirmation_age）
- 坚振地点（confirmation_place）

#### 6.4.3 婚配记录

**字段**:
- 婚配日期（marriage_date）
- 主礼神父（marriage_priest）
- 证人（marriage_witness）
- 事项（marriage_dispensation_item）
- 神父（marriage_dispensation_priest）
- 地点（marriage_place）

#### 6.4.4 病人傅油记录

**字段**:
- 傅油日期（anointing_date）
- 施行人（anointing_priest）
- 地点（anointing_place）
- 死亡日期（death_date）
- 死亡年龄（death_age）

#### 6.4.5 其他圣事

- **初领圣体**: first_communion_date
- **补礼**: supplementary_priest, supplementary_place, supplementary_date

---

### 6.5 数据导出与打印

#### 6.5.1 HTML 模板渲染

**模板文件**: [doc/a3.html](doc/a3.html)

**模板特点**:
- 使用 HTML 4.0 标准（QTextEdit 兼容）
- 使用 `table-layout: fixed` 固定列宽
- 所有 `<td>` 标签显式指定 `width` 属性
- 占位符格式：`姓名占位`, `性别占位` 等

**渲染流程**:
```
1. 读取 a3.html 模板
2. 替换所有占位符为实际数据
3. 处理日期（1752-09-14 显示为"无"）
4. 处理照片路径（转换为 file:// URL）
5. 返回完整 HTML 字符串
```

#### 6.5.2 QTextEdit HTML 适配

**QTextEdit HTML 渲染限制**:
- ❌ 不支持 HTML5/CSS3
- ❌ 不支持 `<col>` 标签
- ❌ 不支持复杂 CSS 布局
- ✅ 支持 HTML 4.0
- ✅ 支持部分 CSS 2.1
- ✅ 支持 `<img>` 标签（需要 file:// URL）

**解决方案**:

1. **列宽问题**:
   ```html
   <!-- 错误：QTextEdit 不支持 -->
   <col width="80">
   
   <!-- 正确：使用 table-layout: fixed 和 td width -->
   <style>
   table { table-layout: fixed; width: 600px; }
   </style>
   <td width="80">姓名</td>
   ```

2. **图片显示问题**:
   ```python
   # 错误：相对路径不工作
   <img src="static/member_photos/abc.jpg">
   
   # 正确：使用 file:// 协议的绝对路径
   <img src="file:///C:/path/to/project/static/member_photos/abc.jpg">
   ```

3. **跨平台路径**:
   ```python
   # 使用 pathlib.Path.as_uri() 自动处理 Windows/Unix 差异
   from pathlib import Path
   photo_url = Path(photo_abs_path).as_uri()
   # Windows: file:///C:/path/to/file.jpg
   # Linux: file:///home/user/path/to/file.jpg
   ```

**代码位置**: [src/views/member_excel_renderer.py](src/views/member_excel_renderer.py), [doc/a3.html](doc/a3.html)

---

## 7. 开发指南 (Development Guide)

### 7.1 开发环境搭建

#### 7.1.1 必需工具

| 工具 | 版本要求 | 说明 |
|------|---------|------|
| **Python** | 3.8+ | 核心开发语言 |
| **IDE** | VS Code / PyCharm | 推荐使用 VS Code + Python 扩展 |
| **Git** | 最新版本 | 版本控制 |
| **SQLite Browser** | 最新版本 | 数据库可视化工具（可选） |

#### 7.1.2 开发环境配置

```bash
# 1. 克隆项目
git clone <repository-url>
cd household_system

# 2. 创建虚拟环境
python -m venv venv

# 3. 激活虚拟环境
# Windows
venv\Scripts\activate
# Linux/macOS
source venv/bin/activate

# 4. 安装开发依赖
pip install -r requirements.txt

# 5. 初始化数据库
python -m src.models.init_db

# 6. 运行调试模式
python -m src.app --debug
```

#### 7.1.3 VS Code 配置

**推荐安装的扩展**:
- Python (Microsoft)
- Pylance
- SQLite Viewer
- Git Graph

**launch.json 配置**:
```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Python: App",
            "type": "python",
            "request": "launch",
            "module": "src.app",
            "console": "integratedTerminal",
            "justMyCode": true
        },
        {
            "name": "Python: App (Debug Mode)",
            "type": "python",
            "request": "launch",
            "module": "src.app",
            "args": ["--debug"],
            "console": "integratedTerminal",
            "justMyCode": true
        }
    ]
}
```

---

### 7.2 添加新功能的步骤

#### 7.2.1 添加新的数据模型

**场景**: 需要添加一个新表来存储"活动记录"

**步骤**:

1. **定义模型** ([src/models/household.py](src/models/household.py))
   ```python
   from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
   from sqlalchemy.orm import relationship
   from .base import Base
   import datetime
   
   class Activity(Base):
       __tablename__ = 'activities'
       
       id = Column(Integer, primary_key=True)
       village_id = Column(Integer, ForeignKey('villages.id'), nullable=False)
       title = Column(String(100), nullable=False)
       description = Column(String(500))
       activity_date = Column(DateTime, nullable=False)
       created_at = Column(DateTime, default=datetime.datetime.now)
       updated_at = Column(DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)
       
       # 关联关系
       village = relationship('Village', back_populates='activities')
   ```

2. **更新关联模型**
   ```python
   # 在 Village 类中添加
   activities = relationship('Activity', back_populates='village', cascade='all, delete-orphan')
   ```

3. **重新初始化数据库**
   ```bash
   python -m src.models.init_db
   ```

#### 7.2.2 添加新的 Service

**创建文件**: [src/services/activity_service.py](src/services/activity_service.py)

```python
from sqlalchemy.orm import Session
from src.models.household import Activity
from typing import List, Optional

class ActivityService:
    @staticmethod
    def get_all_activities(db: Session, village_id: int = None) -> List[Activity]:
        """获取所有活动"""
        query = db.query(Activity)
        if village_id:
            query = query.filter(Activity.village_id == village_id)
        return query.order_by(Activity.activity_date.desc()).all()
    
    @staticmethod
    def create_activity(db: Session, village_id: int, title: str, 
                        description: str, activity_date) -> Activity:
        """创建活动"""
        activity = Activity(
            village_id=village_id,
            title=title,
            description=description,
            activity_date=activity_date
        )
        db.add(activity)
        db.commit()
        db.refresh(activity)
        return activity
    
    @staticmethod
    def update_activity(db: Session, activity_id: int, **kwargs) -> Optional[Activity]:
        """更新活动"""
        activity = db.query(Activity).filter(Activity.id == activity_id).first()
        if activity:
            for key, value in kwargs.items():
                if hasattr(activity, key):
                    setattr(activity, key, value)
            db.commit()
            db.refresh(activity)
        return activity
    
    @staticmethod
    def delete_activity(db: Session, activity_id: int) -> bool:
        """删除活动"""
        activity = db.query(Activity).filter(Activity.id == activity_id).first()
        if activity:
            db.delete(activity)
            db.commit()
            return True
        return False
```

#### 7.2.3 添加新的视图

**创建文件**: [src/views/activity_view.py](src/views/activity_view.py)

```python
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QPushButton
from PyQt5.QtCore import Qt
from qfluentwidgets import PushButton, TableWidget, MessageBox
from src.models import SessionLocal
from src.services.activity_service import ActivityService

class ActivityView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.db = SessionLocal()
        self.init_ui()
        self.load_activities()
    
    def init_ui(self):
        """初始化界面"""
        layout = QVBoxLayout()
        
        # 工具栏
        toolbar = QHBoxLayout()
        self.add_btn = PushButton('添加活动')
        self.add_btn.clicked.connect(self.add_activity)
        toolbar.addWidget(self.add_btn)
        toolbar.addStretch()
        layout.addLayout(toolbar)
        
        # 表格
        self.table = TableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(['标题', '描述', '日期', '操作'])
        layout.addWidget(self.table)
        
        self.setLayout(layout)
    
    def load_activities(self):
        """加载活动列表"""
        activities = ActivityService.get_all_activities(self.db)
        self.table.setRowCount(len(activities))
        
        for row, activity in enumerate(activities):
            self.table.setItem(row, 0, QTableWidgetItem(activity.title))
            self.table.setItem(row, 1, QTableWidgetItem(activity.description or ''))
            self.table.setItem(row, 2, QTableWidgetItem(str(activity.activity_date)))
            # 操作按钮...
    
    def add_activity(self):
        """添加活动"""
        # 实现添加对话框...
        pass
```

#### 7.2.4 在主界面中注册视图

**编辑**: [src/views/main_view.py](src/views/main_view.py)

```python
from src.views.activity_view import ActivityView
from qfluentwidgets import FluentIcon as FIF

# 在 init_navigation 方法中添加
activity_page = ActivityView(self)
self.addSubInterface(activity_page, FIF.CALENDAR, '活动管理')
```

---

### 7.3 代码规范

#### 7.3.1 命名规范

| 类型 | 命名方式 | 示例 |
|------|---------|------|
| **类名** | PascalCase | `HouseholdService`, `MemberView` |
| **函数/方法** | snake_case | `get_all_households()`, `create_member()` |
| **变量** | snake_case | `household_id`, `member_name` |
| **常量** | UPPER_SNAKE_CASE | `DB_PATH`, `DEFAULT_DATE` |
| **私有成员** | _前缀 | `_internal_method()`, `_cache` |

#### 7.3.2 文档注释规范

```python
def create_household(db: Session, village_id: int, household_code: str, 
                    plot_number: int, address: str, phone: str = None) -> Household:
    """
    创建新家庭
    
    Args:
        db: 数据库会话对象
        village_id: 所属堂区 ID
        household_code: 家庭编号
        plot_number: 片号
        address: 详细地址
        phone: 联系电话（可选）
    
    Returns:
        Household: 创建的家庭对象
    
    Raises:
        ValueError: 如果家庭编号重复
    
    Example:
        >>> household = create_household(db, 1, 'H001', 1, '某某街道')
    """
    # 实现代码...
```

#### 7.3.3 导入顺序

```python
# 1. 标准库
import os
import sys
from datetime import datetime

# 2. 第三方库
from PyQt5.QtWidgets import QWidget, QVBoxLayout
from sqlalchemy.orm import Session

# 3. 本地模块
from src.models import Household, Member
from src.services.household_service import HouseholdService
```

---

### 7.4 调试技巧

#### 7.4.1 使用调试模式

```bash
# 跳过登录，直接进入主界面
python -m src.app --debug
```

调试模式会创建一个临时的超级管理员用户，拥有所有权限。

#### 7.4.2 数据库调试

**查看数据库内容**:
```bash
# 使用 SQLite 命令行
sqlite3 data/household.db

# 查看所有表
.tables

# 查看表结构
.schema members

# 查询数据
SELECT * FROM members LIMIT 10;
```

**使用 Python 查询**:
```python
from src.models import SessionLocal, Member

db = SessionLocal()
members = db.query(Member).all()
for member in members:
    print(f"{member.id}: {member.name}")
```

#### 7.4.3 日志记录

**添加日志**:
```python
import logging

# 配置日志
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# 使用日志
logger.debug("成员列表加载完成")
logger.info(f"创建成员: {member.name}")
logger.warning("照片路径不存在")
logger.error("数据库连接失败", exc_info=True)
```

#### 7.4.4 常见问题排查

**问题1: DetachedInstanceError**

```python
# 错误示例
member = db.query(Member).first()
db.close()
print(member.name)  # 报错：DetachedInstanceError

# 解决方案1：在会话关闭前访问数据
member = db.query(Member).first()
name = member.name  # 先取出数据
db.close()
print(name)

# 解决方案2：使用 joinedload 预加载关联数据
from sqlalchemy.orm import joinedload
member = db.query(Member).options(joinedload(Member.household)).first()
```

**问题2: QTextEdit HTML 不显示图片**

```python
# 错误：使用相对路径
html = '<img src="static/member_photos/abc.jpg">'

# 正确：使用 file:// 协议的绝对路径
from pathlib import Path
photo_abs_path = Path('static/member_photos/abc.jpg').resolve()
photo_url = photo_abs_path.as_uri()
html = f'<img src="{photo_url}">'
```

---

### 7.5 测试

#### 7.5.1 单元测试示例

**创建测试文件**: `test/test_household_service.py`

```python
import unittest
from src.models import SessionLocal, Base, engine
from src.services.household_service import HouseholdService

class TestHouseholdService(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        """创建测试数据库"""
        Base.metadata.create_all(bind=engine)
    
    def setUp(self):
        """每个测试前创建新会话"""
        self.db = SessionLocal()
    
    def tearDown(self):
        """每个测试后关闭会话"""
        self.db.close()
    
    def test_create_household(self):
        """测试创建家庭"""
        household = HouseholdService.create_household(
            self.db, 
            village_id=1,
            household_code='TEST001',
            plot_number=1,
            address='测试地址',
            phone='13800138000'
        )
        
        self.assertIsNotNone(household.id)
        self.assertEqual(household.household_code, 'TEST001')
        self.assertEqual(household.phone, '13800138000')
    
    def test_search_households(self):
        """测试搜索家庭"""
        # 先创建测试数据
        HouseholdService.create_household(
            self.db, 1, 'SEARCH001', 1, '搜索测试地址', '12345678'
        )
        
        # 执行搜索
        results = HouseholdService.search_households(self.db, keyword='搜索')
        
        self.assertGreater(len(results), 0)
        self.assertIn('搜索', results[0].address)

if __name__ == '__main__':
    unittest.main()
```

#### 7.5.2 运行测试

```bash
# 运行单个测试文件
python -m unittest test.test_household_service

# 运行所有测试
python -m unittest discover test

# 显示详细输出
python -m unittest discover test -v
```

---

### 7.6 版本控制

#### 7.6.1 Git 工作流

```bash
# 1. 创建功能分支
git checkout -b feature/activity-management

# 2. 开发过程中提交
git add src/services/activity_service.py
git commit -m "添加活动服务层"

git add src/views/activity_view.py
git commit -m "添加活动管理界面"

# 3. 合并到主分支
git checkout master
git merge feature/activity-management

# 4. 推送到远程
git push origin master
```

#### 7.6.2 提交消息规范

```bash
# 格式：<类型>: <简短描述>
#
# <详细描述>

# 类型:
# feat: 新功能
# fix: 修复bug
# docs: 文档更新
# style: 代码格式调整
# refactor: 重构
# test: 测试相关
# chore: 构建过程或辅助工具的变动

# 示例:
git commit -m "feat: 添加活动管理功能"
git commit -m "fix: 修复成员照片显示问题"
git commit -m "docs: 更新 README"
```

---

## 8. API 参考 (API Reference)

### 8.1 Services API

#### 8.1.1 AuthService

**文件**: [src/services/auth_service.py](src/services/auth_service.py)

##### `authenticate_user(db, username, password)`

验证用户身份

**参数**:
- `db` (Session): 数据库会话
- `username` (str): 用户名
- `password` (str): 明文密码

**返回**: User 对象或 None

**示例**:
```python
from src.services.auth_service import AuthService
from src.models import SessionLocal

db = SessionLocal()
user = AuthService.authenticate_user(db, 'admin', 'admin123')
if user:
    print(f"登录成功: {user.username}")
```

##### `check_permission(user, permission_name)`

检查用户权限

**参数**:
- `user` (User): 用户对象
- `permission_name` (str): 权限名称（如 'village_manage'）

**返回**: bool

**示例**:
```python
has_permission = AuthService.check_permission(user, 'household_manage')
```

##### `create_user(db, username, password, role_id, village_id=None)`

创建新用户

**参数**:
- `db` (Session): 数据库会话
- `username` (str): 用户名
- `password` (str): 明文密码
- `role_id` (int): 角色 ID
- `village_id` (int, optional): 管理的堂区 ID

**返回**: User 对象

---

#### 8.1.2 VillageService

**文件**: [src/services/village_service.py](src/services/village_service.py)

##### `get_all_villages(db)`

获取所有堂区

**返回**: List[Village]

##### `create_village(db, name, code, establishment_date, village_priest, address, description=None, photo=None)`

创建堂区

**返回**: Village 对象

##### `search_villages(db, keyword)`

搜索堂区（按名称、编码、神父、地址）

**返回**: List[Village]

---

#### 8.1.3 HouseholdService

**文件**: [src/services/household_service.py](src/services/household_service.py)

##### `get_all_households(db, village_id=None)`

获取所有家庭

**参数**:
- `village_id` (int, optional): 按堂区过滤

**返回**: List[Household]

##### `create_household(db, village_id, household_code, plot_number, address, phone=None)`

创建家庭

**返回**: Household 对象

##### `search_households(db, keyword=None, village_id=None)`

搜索家庭

**返回**: List[Household]

---

#### 8.1.4 MemberService

**文件**: [src/services/member_service.py](src/services/member_service.py)

##### `get_all_members(db, household_id)`

获取家庭的所有成员

**返回**: List[Member]

##### `create_member(db, household_id, name, gender, **kwargs)`

创建成员

**关键字参数**:
- `birth_date`: 出生日期
- `baptismal_name`: 圣名
- `relation_to_head`: 与户主关系
- `education`: 文化程度
- `occupation`: 职业
- `church_id`: 教籍证件号
- `photo`: 照片路径
- 以及所有圣事相关字段...

**返回**: Member 对象

##### `update_member(db, member_id, **kwargs)`

更新成员信息

**返回**: Member 对象或 None

---

### 8.2 Models API

#### 8.2.1 Village (堂区)

**表名**: `villages`

**字段**:
| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer | 主键 |
| name | String(100) | 堂区名称 |
| code | String(20) | 堂区编码（唯一） |
| establishment_date | Date | 建堂日期 |
| village_priest | String(50) | 本堂神父 |
| address | String(200) | 详细地址 |
| description | Text | 堂区描述 |
| photo | String(255) | 照片路径 |
| created_at | DateTime | 创建时间 |
| updated_at | DateTime | 更新时间 |

**关联**:
- `households`: 一对多关系，该堂区的所有家庭
- `users`: 一对多关系，管理该堂区的用户

---

#### 8.2.2 Household (家庭)

**表名**: `households`

**字段**:
| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer | 主键 |
| village_id | Integer | 所属堂区 ID（外键） |
| household_code | String(20) | 家庭编号 |
| plot_number | Integer | 片号 |
| address | String(200) | 详细地址 |
| phone | String(20) | 联系电话 |
| head_of_household | String(50) | 户主姓名 |
| created_at | DateTime | 创建时间 |
| updated_at | DateTime | 更新时间 |

**关联**:
- `village`: 多对一关系，所属堂区
- `members`: 一对多关系，该家庭的所有成员

---

#### 8.2.3 Member (成员)

**表名**: `members`

**主要字段**:
- 基本信息: `id`, `household_id`, `name`, `gender`, `birth_date`, `baptismal_name`, `relation_to_head`, `education`, `occupation`, `church_id`, `photo`
- 圣洗: `baptism_priest`, `baptism_godparent`, `baptism_date`, `baptism_note`
- 坚振: `confirmation_date`, `confirmation_priest`, `confirmation_godparent`, `confirmation_name`, `confirmation_age`, `confirmation_place`
- 婚配: `marriage_date`, `marriage_priest`, `marriage_witness`, `marriage_dispensation_item`, `marriage_dispensation_priest`, `marriage_place`
- 病人傅油: `anointing_date`, `anointing_priest`, `anointing_place`, `death_date`, `death_age`
- 其他: `first_communion_date`, `supplementary_priest`, `supplementary_place`, `supplementary_date`, `association`, `note`

**关联**:
- `household`: 多对一关系，所属家庭

---

### 8.3 工具函数

#### 8.3.1 resize_and_save_photo()

**文件**: [src/views/household_management_view.py](src/views/household_management_view.py:16-50)

**功能**: 调整照片尺寸并保存

**签名**:
```python
def resize_and_save_photo(source_path: str, target_path: str, 
                         target_width: int = 120, target_height: int = 160) -> bool
```

**参数**:
- `source_path`: 源照片路径
- `target_path`: 目标保存路径
- `target_width`: 目标宽度（默认 120px）
- `target_height`: 目标高度（默认 160px）

**返回**: bool（成功/失败）

**实现原理**:
1. 使用 `Qt.KeepAspectRatioByExpanding` 缩放
2. 如果缩放后超出目标尺寸，进行中心裁剪
3. 保存为 JPG 格式，quality=90

---

#### 8.3.2 get_member_excel_html()

**文件**: [src/views/member_excel_renderer.py](src/views/member_excel_renderer.py)

**功能**: 生成成员信息的 HTML 表格

**签名**:
```python
def get_member_excel_html(member: Member) -> str
```

**参数**:
- `member`: Member 对象

**返回**: str（HTML 字符串）

**使用示例**:
```python
from src.views.member_excel_renderer import get_member_excel_html

html = get_member_excel_html(member)
text_edit.setHtml(html)
```

---

## 9. 技术要点与解决方案 (Technical Solutions)

### 9.1 SQLAlchemy ORM 最佳实践

#### 9.1.1 避免 N+1 查询问题

**问题**: 循环查询关联数据导致大量 SQL 查询

```python
# 不好的做法（N+1 查询）
households = db.query(Household).all()
for household in households:
    print(household.village.name)  # 每次都查询一次数据库
```

**解决方案**: 使用 `joinedload` 预加载

```python
from sqlalchemy.orm import joinedload

# 好的做法（只查询一次）
households = db.query(Household).options(joinedload(Household.village)).all()
for household in households:
    print(household.village.name)  # 直接从内存读取
```

#### 9.1.2 DetachedInstanceError 问题

**问题**: 会话关闭后访问对象属性

```python
# 错误示例
member = db.query(Member).first()
db.close()
print(member.name)  # 抛出 DetachedInstanceError
```

**解决方案1**: 在会话关闭前访问所有需要的数据

```python
member = db.query(Member).first()
name = member.name  # 先访问数据
household_name = member.household.village.name  # 预加载关联数据
db.close()
print(name, household_name)
```

**解决方案2**: 使用 `joinedload` 预加载关联对象

```python
from sqlalchemy.orm import joinedload

member = db.query(Member).options(
    joinedload(Member.household).joinedload(Household.village)
).first()
db.close()
print(member.household.village.name)  # 不会报错
```

#### 9.1.3 会话管理

**推荐模式**: 使用上下文管理器

```python
from contextlib import contextmanager
from src.models import SessionLocal

@contextmanager
def get_db():
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()

# 使用
with get_db() as db:
    household = HouseholdService.create_household(db, ...)
```

---

### 9.2 PyQt5 常见问题

#### 9.2.1 QTextEdit HTML 渲染限制

**问题**: QTextEdit 不支持 HTML5/CSS3

**限制**:
- ❌ 不支持 `<col>` 标签
- ❌ 不支持 `flex` 布局
- ❌ 不支持 `grid` 布局
- ❌ 不支持 CSS 变量
- ✅ 支持 HTML 4.0
- ✅ 支持部分 CSS 2.1
- ✅ 支持 `<table>`, `<img>`, `<span>` 等基本标签

**解决方案**: 使用 HTML 4.0 + CSS 2.1

```html
<!-- 使用 table-layout: fixed 和 td width -->
<style>
table {
    table-layout: fixed;
    width: 600px;
    border-collapse: collapse;
}
td {
    border: 1px solid black;
}
</style>

<table>
    <tr>
        <td width="80">姓名</td>
        <td width="120">张三</td>
        <td width="80">性别</td>
        <td width="320">男</td>
    </tr>
</table>
```

#### 9.2.2 QTextEdit 显示本地图片

**问题**: 相对路径图片不显示

```html
<!-- 不工作 -->
<img src="static/member_photos/abc.jpg">
```

**解决方案**: 使用 `file://` 协议的绝对路径

```python
from pathlib import Path

# 构建绝对路径
photo_abs_path = Path('static/member_photos/abc.jpg').resolve()

# 转换为 file:// URL
photo_url = photo_abs_path.as_uri()
# Windows: file:///C:/path/to/project/static/member_photos/abc.jpg
# Linux: file:///home/user/project/static/member_photos/abc.jpg

html = f'<img src="{photo_url}" style="width: 120px; height: 160px;">'
text_edit.setHtml(html)
```

#### 9.2.3 照片尺寸控制

**问题**: 大尺寸照片破坏布局

**解决方案**: 上传时自动缩放至标准尺寸

```python
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt

def resize_and_save_photo(source_path, target_path, target_width=120, target_height=160):
    """
    调整照片尺寸并保存
    
    使用 KeepAspectRatioByExpanding 确保填满目标尺寸
    使用中心裁剪避免变形
    """
    pixmap = QPixmap(source_path)
    
    # 缩放至目标尺寸（可能超出）
    scaled_pixmap = pixmap.scaled(
        target_width, target_height,
        Qt.KeepAspectRatioByExpanding,
        Qt.SmoothTransformation
    )
    
    # 居中裁剪
    if scaled_pixmap.width() > target_width or scaled_pixmap.height() > target_height:
        x = (scaled_pixmap.width() - target_width) // 2
        y = (scaled_pixmap.height() - target_height) // 2
        scaled_pixmap = scaled_pixmap.copy(x, y, target_width, target_height)
    
    # 保存
    scaled_pixmap.save(target_path, quality=90)
    return True
```

---

### 9.3 日期字段处理

#### 9.3.1 默认日期问题

**问题**: SQLite 不支持 NULL 日期，但空日期在业务上有意义

**解决方案**: 使用最小日期 `1752-09-14` 作为"无日期"标志

**数据库中**:
```python
# models/household.py
birth_date = Column(Date, default=date(1752, 9, 14))
```

**显示时转换**:
```python
# views/member_excel_renderer.py
def format_date(date_value):
    if str(date_value) == '1752-09-14':
        return '无'
    return str(date_value)

html = html.replace('出生日期占位', format_date(member.birth_date))
```

---

### 9.4 性能优化

#### 9.4.1 数据库查询优化

**使用索引**:
```python
# 为常用查询字段添加索引
household_code = Column(String(20), nullable=False, index=True)
```

**批量操作**:
```python
# 不好：逐个插入
for data in data_list:
    member = Member(**data)
    db.add(member)
    db.commit()  # 每次提交

# 好：批量插入
for data in data_list:
    member = Member(**data)
    db.add(member)
db.commit()  # 一次提交
```

#### 9.4.2 界面性能优化

**延迟加载**:
```python
# 只在需要时加载成员详情，而不是一次性加载所有成员的所有数据
def on_member_selected(self):
    member_id = self.get_selected_member_id()
    if member_id:
        member = self.db.query(Member).filter(Member.id == member_id).first()
        self.load_member_details(member)
```

---

### 9.5 安全性

#### 9.5.1 密码安全

**使用 bcrypt 加密**:
```python
import bcrypt

def hash_password(password: str) -> str:
    """密码哈希"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """密码验证"""
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))
```

#### 9.5.2 SQL 注入防护

**使用 ORM 参数化查询**（SQLAlchemy 自动处理）:
```python
# 安全：参数化查询
households = db.query(Household).filter(
    Household.household_code == user_input
).all()

# 危险：字符串拼接（不要这样做）
# query = f"SELECT * FROM households WHERE household_code = '{user_input}'"
```

---

## 10. 部署指南 (Deployment)

### 10.1 Windows 部署

#### 10.1.1 使用 PyInstaller 打包

**安装 PyInstaller**:
```bash
pip install pyinstaller
```

**创建打包脚本** (`build.spec`):
```python
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['src/app.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('doc/a3.html', 'doc'),
        ('static', 'static'),
    ],
    hiddenimports=[
        'PyQt5',
        'PyQt5.QtCore',
        'PyQt5.QtWidgets',
        'PyQt5.QtGui',
        'sqlalchemy',
        'bcrypt',
        'Pillow',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyi_runtime = [x for x in a.binaries if 'python' in x[0].lower()]

pyt = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyt,
    a.scripts,
    [],
    exclude_binaries=True,
    name='家庭户籍管理系统',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # 不显示控制台窗口
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='icon.ico'  # 如果有图标
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='家庭户籍管理系统'
)
```

**执行打包**:
```bash
pyinstaller build.spec
```

**输出**:
- 可执行文件位于 `dist/家庭户籍管理系统/`
- 包含所有依赖和资源文件

#### 10.1.2 创建安装程序

**使用 Inno Setup**:
1. 下载并安装 [Inno Setup](https://jrsoftware.org/isinfo.php)
2. 创建安装脚本 `installer.iss`
3. 编译生成安装程序

---

### 10.2 Linux 部署

#### 10.2.1 安装依赖

```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install python3 python3-pip python3-venv
sudo apt-get install libxcb-xinerama0  # PyQt5 依赖

# CentOS/RHEL
sudo yum install python3 python3-pip
sudo yum install xcb-util-xinerama
```

#### 10.2.2 部署步骤

```bash
# 1. 创建应用目录
sudo mkdir -p /opt/household_system
cd /opt/household_system

# 2. 上传项目文件
# （使用 scp, rsync 或其他方式）

# 3. 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 4. 安装依赖
pip install -r requirements.txt

# 5. 初始化数据库
python -m src.models.init_db

# 6. 创建启动脚本
cat > start.sh << 'EOF'
#!/bin/bash
cd /opt/household_system
source venv/bin/activate
python -m src.app
EOF

chmod +x start.sh

# 7. 运行
./start.sh
```

---

### 10.3 macOS 部署

#### 10.3.1 打包为 .app

**使用 py2app**:
```bash
pip install py2app

# 创建配置文件
py2applet --make-setup src/app.py

# 打包
python setup.py py2app
```

---

### 10.4 数据库备份

#### 10.4.1 手动备份

```bash
# 复制数据库文件
cp data/household.db data/household_backup_$(date +%Y%m%d).db
```

#### 10.4.2 自动备份脚本

**Windows** (`backup.bat`):
```batch
@echo off
set TIMESTAMP=%date:~0,4%%date:~5,2%%date:~8,2%_%time:~0,2%%time:~3,2%
xcopy data\household.db backup\household_%TIMESTAMP%.db /Y
```

**Linux** (`backup.sh`):
```bash
#!/bin/bash
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
cp data/household.db backup/household_$TIMESTAMP.db

# 保留最近 30 天的备份
find backup/ -name "household_*.db" -mtime +30 -delete
```

#### 10.4.3 数据库恢复

```bash
# 停止应用
# 恢复数据库
cp backup/household_20260410.db data/household.db
# 重启应用
```

---

## 11. 常见问题 (FAQ)

### 11.1 安装和启动问题

**Q: 运行时提示 "No module named 'PyQt5'"**

A: 安装 PyQt5
```bash
pip install PyQt5==5.15.10
```

---

**Q: 运行时提示 "No module named 'qfluentwidgets'"**

A: 安装 PyQt-Fluent-Widgets
```bash
pip install PyQt-Fluent-Widgets[full]
```

---

**Q: 初始化数据库失败**

A: 检查以下几点：
1. `data` 目录是否存在
2. 是否有写入权限
3. 数据库文件是否被占用

```bash
# 删除旧数据库重新初始化
rm data/household.db
python -m src.models.init_db
```

---

**Q: 启动后立即崩溃**

A: 以调试模式运行查看错误信息
```bash
python -m src.app
```

---

### 11.2 功能使用问题

**Q: 忘记管理员密码怎么办？**

A: 重新初始化数据库（会清空所有数据）或手动修改密码哈希：
```python
from src.models import SessionLocal, User
from src.services.auth_service import AuthService

db = SessionLocal()
user = db.query(User).filter(User.username == 'admin').first()
user.password_hash = AuthService.get_password_hash('new_password')
db.commit()
```

---

**Q: 上传的照片不显示**

A: 检查以下几点：
1. `static/member_photos/` 目录是否存在
2. 照片路径是否正确保存到数据库
3. 照片文件是否损坏

---

**Q: 设置户主后，其他成员的关系没有自动更新**

A: 这是预期行为。设置户主时，只更新：
1. 家庭表的 `head_of_household` 字段
2. 被设为户主的成员的 `relation_to_head` 为"户主"

其他成员的关系需要手动编辑更新。

---

**Q: 成员信息显示为"无"的日期如何修改？**

A: 编辑成员信息，选择正确的日期即可。"无"表示 `1752-09-14`（默认日期）。

---

### 11.3 性能问题

**Q: 家庭列表加载缓慢**

A: 原因可能是：
1. 堂区下家庭过多
2. 没有使用预加载（joinedload）

解决方案：
- 使用搜索功能缩小范围
- 确保代码使用了 `joinedload`

---

**Q: 数据库文件过大**

A: SQLite 数据库文件可能包含已删除数据的空间，可以使用 VACUUM 命令压缩：
```bash
sqlite3 data/household.db "VACUUM;"
```

---

### 11.4 数据问题

**Q: 删除家庭时提示"有成员存在"**

A: 这不应该发生（有级联删除）。如果出现：
1. 检查数据库完整性
2. 先手动删除所有成员，再删除家庭

---

**Q: 如何批量导入数据？**

A: 目前不支持批量导入。可以编写脚本：
```python
from src.models import SessionLocal
from src.services.household_service import HouseholdService
import pandas as pd

db = SessionLocal()
df = pd.read_excel('data.xlsx')

for _, row in df.iterrows():
    HouseholdService.create_household(
        db, 
        village_id=row['village_id'],
        household_code=row['household_code'],
        ...
    )

db.close()
```

---

## 12. 附录 (Appendix)

### 12.1 数据字典

#### 12.1.1 性别选项
- 男
- 女

#### 12.1.2 与户主关系
- 户主
- 配偶
- 子女
- 父母
- 祖父母
- 孙子女
- 兄弟姐妹
- 其他

#### 12.1.3 文化程度
- 文盲
- 小学
- 初中
- 高中
- 中专
- 大专
- 本科
- 硕士
- 博士

---

### 12.2 数据库 Schema

**完整数据库结构**:
```sql
-- 权限表
CREATE TABLE permissions (
    id INTEGER PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL,
    description TEXT
);

-- 角色表
CREATE TABLE roles (
    id INTEGER PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL,
    description TEXT
);

-- 角色权限关联表
CREATE TABLE role_permissions (
    role_id INTEGER,
    permission_id INTEGER,
    PRIMARY KEY (role_id, permission_id),
    FOREIGN KEY (role_id) REFERENCES roles(id),
    FOREIGN KEY (permission_id) REFERENCES permissions(id)
);

-- 用户表
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(128) NOT NULL,
    role_id INTEGER,
    village_id INTEGER,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (role_id) REFERENCES roles(id),
    FOREIGN KEY (village_id) REFERENCES villages(id)
);

-- 堂区表
CREATE TABLE villages (
    id INTEGER PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    code VARCHAR(20) UNIQUE NOT NULL,
    establishment_date DATE NOT NULL,
    village_priest VARCHAR(50) NOT NULL,
    address VARCHAR(200) NOT NULL,
    description TEXT,
    photo VARCHAR(255),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 家庭表
CREATE TABLE households (
    id INTEGER PRIMARY KEY,
    village_id INTEGER NOT NULL,
    household_code VARCHAR(20) NOT NULL,
    plot_number INTEGER NOT NULL,
    address VARCHAR(200) NOT NULL,
    phone VARCHAR(20),
    head_of_household VARCHAR(50),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (village_id) REFERENCES villages(id)
);

CREATE INDEX idx_household_code ON households(household_code);

-- 成员表（字段较多，见文档第4章）
CREATE TABLE members (
    id INTEGER PRIMARY KEY,
    household_id INTEGER NOT NULL,
    -- 基本信息字段...
    -- 圣事字段...
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (household_id) REFERENCES households(id)
);
```

---

### 12.3 HTML 模板说明

**模板文件**: [doc/a3.html](doc/a3.html)

**占位符列表**:
- 基本信息: `姓名占位`, `性别占位`, `出生日期占位`, `教籍证件号占位`, `与户主关系占位`
- 照片: `图片占位`
- 圣事信息: `圣洗施行人占位`, `领洗日期占位`, `坚振日期占位`, `婚配日期占位` 等

**使用方式**:
```python
html = html.replace('姓名占位', member.name, 1)
html = html.replace('性别占位', member.gender, 1)
```

---

### 12.4 系统要求

#### 最低配置
- CPU: 双核 1.5GHz
- 内存: 2GB
- 硬盘: 100MB 可用空间
- 操作系统: Windows 7 / Ubuntu 18.04 / macOS 10.14

#### 推荐配置
- CPU: 四核 2.0GHz
- 内存: 4GB
- 硬盘: 500MB 可用空间
- 操作系统: Windows 10 / Ubuntu 20.04 / macOS 11

---

### 12.5 许可证

本项目采用 MIT 许可证。

---

### 12.6 贡献指南

欢迎提交 Issue 和 Pull Request！

**提交 Issue**:
1. 描述问题或建议
2. 提供复现步骤（如果是bug）
3. 附上错误信息或截图

**提交 Pull Request**:
1. Fork 项目
2. 创建功能分支
3. 提交代码并编写测试
4. 发起 Pull Request

---

## 13. 速查表 (Quick Reference)

### 13.1 功能代码映射表

| 功能 | 视图文件 | 服务文件 | 模型 |
|------|---------|---------|------|
| 用户登录 | [src/views/login_view.py](src/views/login_view.py) | [src/services/auth_service.py](src/services/auth_service.py) | [src/models/user.py](src/models/user.py) |
| 堂区管理 | [src/views/village_view.py](src/views/village_view.py) | [src/services/village_service.py](src/services/village_service.py) | [src/models/household.py](src/models/household.py) (Village) |
| 家庭管理 | [src/views/household_management_view.py](src/views/household_management_view.py) | [src/services/household_service.py](src/services/household_service.py) | [src/models/household.py](src/models/household.py) (Household) |
| 成员管理 | [src/views/household_management_view.py](src/views/household_management_view.py) | [src/services/member_service.py](src/services/member_service.py) | [src/models/household.py](src/models/household.py) (Member) |
| 成员详情 | [src/views/member_excel_renderer.py](src/views/member_excel_renderer.py) | - | - |
| 权限管理 | [src/views/main_view.py](src/views/main_view.py) | [src/services/auth_service.py](src/services/auth_service.py) | [src/models/auth.py](src/models/auth.py) |

---

### 13.2 常用命令

```bash
# 初始化数据库
python -m src.models.init_db

# 运行应用（正常模式）
python -m src.app

# 运行应用（调试模式）
python -m src.app --debug

# 运行测试
python -m unittest discover test

# 打包应用
pyinstaller build.spec

# 数据库备份
cp data/household.db backup/household_$(date +%Y%m%d).db

# 数据库压缩
sqlite3 data/household.db "VACUUM;"
```

---

### 13.3 关键文件路径

| 文件 | 路径 | 说明 |
|------|------|------|
| 应用入口 | [src/app.py](src/app.py) | 程序主入口 |
| 数据库配置 | [src/models/base.py](src/models/base.py) | 数据库连接配置 |
| 数据库初始化 | [src/models/init_db.py](src/models/init_db.py) | 数据库初始化脚本 |
| 数据库文件 | data/household.db | SQLite 数据库 |
| HTML 模板 | [doc/a3.html](doc/a3.html) | 成员信息模板 |
| 照片目录 | static/member_photos/ | 成员照片存储 |
| 依赖列表 | requirements.txt | Python 依赖包 |
| 项目文档 | [PROJECT_DOCUMENTATION.md](PROJECT_DOCUMENTATION.md) | 本文档 |

---

### 13.4 默认账号

| 用户名 | 密码 | 角色 | 权限 |
|--------|------|------|------|
| admin | admin123 | 超级管理员 | 所有权限 |

---

### 13.5 快捷键

| 功能 | 快捷键 |
|------|--------|
| 保存 | Ctrl+S |
| 搜索 | Ctrl+F |
| 刷新 | F5 |
| 退出 | Alt+F4 |

---

### 13.6 技术栈版本

```
Python >= 3.8
PyQt5 == 5.15.10
SQLAlchemy == 1.4.52
bcrypt == 4.0.1
pydantic == 2.6.1
python-dotenv == 1.0.0
Pillow == 10.2.0
PyQt-Fluent-Widgets == latest
```

---

## 结语

本文档全面介绍了家庭户籍管理系统的架构、功能、开发和部署。如有疑问或建议，请提交 Issue 或联系开发团队。

**文档版本**: 1.0  
**最后更新**: 2026-04-10  
**维护者**: 开发团队

---

**相关文档**:
- [快速开始指南](doc/STARTUP_GUIDE.md)
- [成员字段规范](doc/HOUSEHOLD_MEMBER_FIELDS_SPEC.md)
- [村字段规范](doc/VILLAGE_FIELDS_SPEC.md)

---

*本文档使用 Markdown 编写，可使用任意 Markdown 编辑器查看。*
