# 测试套件使用指南

## 概述

本项目包含完整的测试套件，覆盖数据模型、业务逻辑和 GUI 界面（GUI 测试在 WSL2 环境中自动跳过）。

## 测试结构

```
tests/
├── __init__.py              # 测试模块初始化
├── conftest.py              # pytest 配置和共享 fixtures
├── test_models.py           # 数据模型测试
├── test_auth_service.py     # 权限服务测试
├── test_search_service.py   # 搜索服务测试
└── test_gui.py              # GUI 界面测试（WSL2 中跳过）
```

## 安装测试依赖

```bash
pip install pytest pytest-cov
```

## 运行测试

### 1. 运行所有测试（跳过 GUI）

```bash
./run_tests.sh --no-gui
```

或直接使用 pytest：

```bash
pytest tests/ -m "not gui" -v
```

### 2. 运行特定类型的测试

**只运行单元测试：**
```bash
./run_tests.sh --unit
```

**只运行集成测试：**
```bash
./run_tests.sh --integration
```

**运行特定文件的测试：**
```bash
pytest tests/test_search_service.py -v
```

**运行特定测试类：**
```bash
pytest tests/test_search_service.py::TestSearchServiceHouseholdSearch -v
```

**运行特定测试方法：**
```bash
pytest tests/test_search_service.py::TestSearchServiceHouseholdSearch::test_search_households_by_head_name -v
```

### 3. 生成覆盖率报告

```bash
./run_tests.sh --coverage --no-gui
```

覆盖率报告会生成在 `htmlcov/index.html`，可以用浏览器打开查看。

### 4. 快速运行（无详细输出）

```bash
./run_tests.sh --fast --no-gui
```

## 测试标记

测试使用 pytest 标记进行分类：

- `@pytest.mark.unit` - 单元测试
- `@pytest.mark.integration` - 集成测试
- `@pytest.mark.gui` - GUI 测试（WSL2 中自动跳过）
- `@pytest.mark.slow` - 慢速测试

### 使用标记过滤测试

```bash
# 只运行单元测试
pytest -m unit

# 只运行集成测试
pytest -m integration

# 跳过慢速测试
pytest -m "not slow"

# 跳过 GUI 测试
pytest -m "not gui"

# 组合多个标记
pytest -m "unit and not slow"
```

## 测试覆盖范围

### 1. 数据模型测试 (`test_models.py`)

测试内容：
- ✅ Village 模型：创建、唯一性约束、关系
- ✅ Household 模型：创建、关系（村庄、成员）
- ✅ Member 模型：创建、可选字段、关系
- ✅ Permission 模型：创建、唯一性
- ✅ Role 模型：创建、权限关系
- ✅ User 模型：创建、密码加密、角色关系、可访问村庄
- ✅ 级联删除测试
- ✅ 数据完整性链测试

### 2. 权限服务测试 (`test_auth_service.py`)

测试内容：
- ✅ 超级管理员权限检查
- ✅ 录入员权限检查
- ✅ 观察员权限检查
- ✅ 空用户/无角色用户处理
- ✅ 可访问村庄获取（三种角色）
- ✅ 用户认证（成功/失败/空凭据）
- ✅ 权限层级测试
- ✅ 数据访问范围测试
- ✅ RBAC 集成测试

### 3. 搜索服务测试 (`test_search_service.py`)

测试内容：
- ✅ 家庭搜索：户主、电话、地址、地块编号
- ✅ 成员搜索：姓名、圣名、教友编号、职业、善会
- ✅ 仪式字段搜索：神父、代父母、地点
- ✅ 空关键词处理
- ✅ 无结果处理
- ✅ 成员搜索去重
- ✅ 权限过滤（三种角色）
- ✅ 搜索工作流测试
- ✅ 跨字段搜索
- ✅ 大数据集性能测试

### 4. GUI 界面测试 (`test_gui.py`)

测试内容（仅代码，WSL2 中跳过）：
- ⚠️ SearchView 初始化
- ⚠️ 界面布局验证
- ⚠️ 搜索框提示文本
- ⚠️ 按钮点击事件
- ⚠️ 表格配置
- ⚠️ 标签栏配置
- ⚠️ 家庭点击加载成员
- ⚠️ 标签切换
- ⚠️ 刷新功能
- ⚠️ 主界面集成
- ⚠️ 基于权限的 UI 访问

## 测试数据

测试使用内存数据库（SQLite），每个测试函数都有独立的数据库实例。

### 预设测试数据

`test_db_with_data` fixture 提供：

**堂区：**
- 测试堂区1（编码 001）
- 测试堂区2（编码 002）
- 测试堂区3（编码 003）

**用户：**
- admin（超级管理员，密码：admin123）
- entry1（录入员，所属堂区1，密码：entry123）
- observer1（观察员，可访问堂区1和2，密码：observer123）

**家庭：**
- 家庭1（堂区1，户主：张三）
- 家庭2（堂区2，户主：王五）
- 家庭3（堂区3，户主：赵六）

**成员：**
- 张三（家庭1，圣名：若瑟，教友编号：CH001）
- 李四（家庭1，圣名：玛利亚，教友编号：CH002）
- 王五（家庭2，圣名：保禄，教友编号：CH003）
- 赵六（家庭3，圣名：伯多禄，教友编号：CH004）

## WSL2 特别说明

在 WSL2 环境中，GUI 测试会自动跳过，因为没有 X11 显示环境。

**自动跳过的原理：**
- 检测 `DISPLAY` 环境变量
- 使用 `@skip_no_display` 装饰器
- pytest 会显示 "SKIPPED [1] ... 需要 X11 显示环境（WSL2 中跳过）"

**推荐运行方式：**
```bash
# 显式跳过 GUI 测试
./run_tests.sh --no-gui

# 或使用 pytest 标记
pytest -m "not gui" -v
```

## 持续集成（CI）

在 CI 环境中运行测试：

```yaml
# .github/workflows/test.yml 示例
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.12'
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-cov
      - name: Run tests
        run: |
          pytest tests/ -m "not gui" --cov=src --cov-report=xml
      - name: Upload coverage
        uses: codecov/codecov-action@v2
```

## 调试测试

### 查看详细输出

```bash
pytest tests/ -v -s
```

- `-v`: 详细模式
- `-s`: 显示 print 输出

### 只运行失败的测试

```bash
pytest --lf
```

### 进入调试器

在测试中添加：
```python
import pdb; pdb.set_trace()
```

或使用 pytest 的调试模式：
```bash
pytest --pdb
```

### 查看最慢的测试

```bash
pytest --durations=10
```

## 编写新测试

### 测试命名规范

- 测试文件：`test_*.py`
- 测试类：`Test*`
- 测试方法：`test_*`

### 使用 fixtures

```python
def test_my_feature(test_db_with_data, super_admin_user):
    """使用共享的 fixtures"""
    data = test_db_with_data
    db = data['db']
    # 测试代码...
```

### 添加测试标记

```python
@pytest.mark.unit
def test_something():
    pass

@pytest.mark.integration
def test_integration():
    pass

@pytest.mark.slow
def test_slow_operation():
    pass
```

## 常见问题

### Q: 测试失败：ModuleNotFoundError

**A:** 设置 PYTHONPATH：
```bash
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
pytest tests/
```

### Q: GUI 测试无法运行

**A:** 在 WSL2 中这是正常的。使用 `--no-gui` 跳过：
```bash
./run_tests.sh --no-gui
```

### Q: 如何查看覆盖率报告

**A:** 生成并打开覆盖率报告：
```bash
./run_tests.sh --coverage --no-gui
xdg-open htmlcov/index.html  # Linux
open htmlcov/index.html      # macOS
```

### Q: 测试数据库污染

**A:** 每个测试函数使用独立的内存数据库，不会互相影响。

## 测试最佳实践

1. **每个测试只测试一个功能点**
2. **使用有意义的测试名称**
3. **避免测试之间的依赖**
4. **使用 fixtures 共享测试数据**
5. **测试边界条件和异常情况**
6. **保持测试快速运行**
7. **定期运行测试**
8. **保持高测试覆盖率（目标 >80%）**

## 参考资源

- [pytest 文档](https://docs.pytest.org/)
- [pytest-cov 文档](https://pytest-cov.readthedocs.io/)
- [SQLAlchemy 测试](https://docs.sqlalchemy.org/en/14/orm/session_transaction.html#session-faq-whentocreate)
- [PyQt 测试](https://doc.qt.io/qt-5/qtest.html)
