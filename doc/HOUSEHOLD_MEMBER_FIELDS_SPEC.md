# 家庭和成员字段说明文档

## 1. 家庭字段结构

| 字段名 | 数据类型 | 约束 | 描述 |
|-------|---------|------|------|
| id | Integer | 主键，自增 | 家庭户号，唯一标识，用户不可编辑 |
| village_id | Integer | 外键，非空 | 所属堂区ID（保存时按照堂区id保存，显示时按照堂区名称显示） |
| household_code | String(20) | 非空，索引 | 家庭编号 |
| plot_number | Integer | 非空 | 片号（必须为数字） |
| address | String(200) | 非空 | 家庭住址 |
| phone | String(20) | 可选 | 电话（必须为数字） |
| head_of_household | String(50) | 可选 | 户主姓名（从家庭的成员中选择） |
| created_at | DateTime | 自动生成 | 创建时间 |
| updated_at | DateTime | 自动更新 | 更新时间 |

## 2. 成员字段结构

| 字段名 | 数据类型 | 约束 | 描述 |
|-------|---------|------|------|
| id | Integer | 主键，自增 | 成员唯一标识，内部使用，不暴露给用户 |
| household_id | Integer | 外键，非空 | 所属家庭ID |
| name | String(50) | 非空 | 成员姓名 |
| gender | String(10) | 可选 | 性别 |
| birth_date | Date | 可选 | 出生日期 |
| id_number | String(18) | 唯一，索引 | 身份证号 |
| relation_to_head | String(20) | 可选 | 与户主关系 |
| status | String(20) | 可选 | 成员状态 |
| created_at | DateTime | 自动生成 | 创建时间 |
| updated_at | DateTime | 自动更新 | 更新时间 |

## 3. 操作函数

### 3.1 HouseholdService 类

#### get_all_households(db: Session, village_id: int = None)
- **功能**：获取所有家庭或指定堂区的家庭
- **参数**：
  - 数据库会话
  - 堂区ID（可选，指定后只返回该堂区的家庭）
- **返回值**：家庭列表

#### get_household_by_id(db: Session, household_id: int)
- **功能**：根据ID获取家庭
- **参数**：数据库会话，家庭ID
- **返回值**：家庭对象或None

#### create_household(db: Session, village_id: int, household_code: str, plot_number: int, address: str, phone: str = None, head_of_household: str = None)
- **功能**：创建新家庭
- **参数**：
  - 数据库会话
  - 堂区ID
  - 家庭编号
  - 片号（必须为数字）
  - 家庭住址（非空）
  - 电话（可选，必须为数字）
  - 户主姓名（可选，从成员中选择）
- **返回值**：创建的家庭对象

#### update_household(db: Session, household_id: int, **kwargs)
- **功能**：更新家庭信息
- **参数**：
  - 数据库会话
  - 家庭ID
  - 要更新的字段（village_id, household_code, plot_number, address, phone, head_of_household）
- **返回值**：更新后的家庭对象或None

#### delete_household(db: Session, household_id: int)
- **功能**：删除家庭
- **参数**：数据库会话，家庭ID
- **返回值**：布尔值，表示删除是否成功

### 3.2 MemberService 类

#### get_all_members(db: Session, household_id: int = None)
- **功能**：获取所有成员或指定家庭的成员
- **参数**：
  - 数据库会话
  - 家庭ID（可选，指定后只返回该家庭的成员）
- **返回值**：成员列表

#### get_member_by_id(db: Session, member_id: int)
- **功能**：根据ID获取成员
- **参数**：数据库会话，成员ID
- **返回值**：成员对象或None

#### create_member(db: Session, household_id: int, name: str, id_number: str, gender: str = None, birth_date: date = None, relation_to_head: str = None, status: str = None)
- **功能**：创建新成员
- **参数**：
  - 数据库会话
  - 家庭ID
  - 成员姓名
  - 身份证号
  - 性别（可选）
  - 出生日期（可选）
  - 与户主关系（可选）
  - 成员状态（可选）
- **返回值**：创建的成员对象

#### update_member(db: Session, member_id: int, **kwargs)
- **功能**：更新成员信息
- **参数**：
  - 数据库会话
  - 成员ID
  - 要更新的字段（name, gender, birth_date, id_number, relation_to_head, status）
- **返回值**：更新后的成员对象或None

#### delete_member(db: Session, member_id: int)
- **功能**：删除成员
- **参数**：数据库会话，成员ID
- **返回值**：布尔值，表示删除是否成功

## 4. 操作说明

### 4.1 家庭管理
- **添加家庭**：填写家庭编号、片号（必须为数字）、家庭住址（非空）、电话（可选，必须为数字），选择所属堂区
- **编辑家庭**：修改家庭信息，包括家庭编号、片号（必须为数字）、家庭住址（非空）、电话（可选，必须为数字）、所属堂区
- **删除家庭**：删除家庭及其所有成员
- **查看家庭**：点击查看按钮，通过浮层显示家庭详细信息

### 4.2 成员管理
- **添加成员**：为选中的家庭添加成员，填写成员姓名、身份证号等信息
- **编辑成员**：点击成员卡片，弹出对话框可查看和编辑成员详细信息
- **设为户主**：在成员编辑对话框中点击"设为户主"按钮，将当前成员设为对应家庭的户主
- **删除成员**：在成员编辑对话框中删除成员

## 5. 注意事项

- 家庭编号和成员身份证号为唯一标识，不可重复
- 家庭必须属于某个堂区
- 成员必须属于某个家庭
- 在添加或编辑成员时，身份证号必须符合18位身份证号格式
- 成员卡片显示采用可滚动组件，当成员数量较多时可通过滚动查看
- 家庭查看功能使用Flyout浮层显示，提供良好的用户体验

## 6. 家庭管理模块函数实现

### 6.1 堂区选择下拉菜单
- **初始化**：在 `init_ui` 方法中创建 `self.village_combo` 组件
- **加载数据**：`load_villages()` 方法 - 从数据库获取所有堂区并填充到下拉菜单
- **选择变化处理**：`on_village_changed()` 方法 - 当选择不同堂区时，加载对应堂区的家庭数据

### 6.2 家庭管理
- **添加家庭**：`add_household()` 方法 - 打开添加家庭对话框，收集家庭信息并创建新家庭
- **编辑家庭**：`edit_household(household)` 方法 - 打开编辑家庭对话框，修改家庭信息
- **删除家庭**：`delete_household(household)` 方法 - 删除指定家庭及其成员
- **查看家庭**：`view_household(household)` 方法 - 以Flyout浮层显示家庭详细信息
- **刷新家庭**：`load_households(village_id)` 方法 - 加载指定堂区的家庭数据到表格
- **家庭选择**：`on_household_clicked(item)` 方法 - 当点击家庭表格时，加载对应家庭的成员数据

### 6.3 成员管理
- **添加成员**：`add_member()` 方法 - 打开添加成员对话框，为选中家庭添加新成员
- **编辑成员**：`edit_member(member)` 方法 - 打开编辑成员对话框，修改成员信息
- **刷新成员**：`refresh_all()` 方法 - 刷新所有数据，包括堂区、家庭和成员
- **加载成员**：`load_members(household_id)` 方法 - 加载指定家庭的成员数据到卡片容器
- **清空成员**：`clear_member_cards()` 方法 - 清空成员卡片容器中的所有卡片