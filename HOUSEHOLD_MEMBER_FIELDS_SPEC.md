# 家庭和成员字段说明文档

## 1. 家庭字段结构

| 字段名 | 数据类型 | 约束 | 描述 |
|-------|---------|------|------|
| id | Integer | 主键，自增 | 家庭唯一标识，内部使用，不暴露给用户 |
| village_id | Integer | 外键，非空 | 所属村庄ID |
| household_code | String(20) | 非空，索引 | 家庭编号 |
| address | String(200) | 可选 | 家庭地址 |
| head_of_household | String(50) | 可选 | 户主姓名 |
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
- **功能**：获取所有家庭或指定村庄的家庭
- **参数**：
  - 数据库会话
  - 村庄ID（可选，指定后只返回该村庄的家庭）
- **返回值**：家庭列表

#### get_household_by_id(db: Session, household_id: int)
- **功能**：根据ID获取家庭
- **参数**：数据库会话，家庭ID
- **返回值**：家庭对象或None

#### create_household(db: Session, village_id: int, household_code: str, address: str = None, head_of_household: str = None)
- **功能**：创建新家庭
- **参数**：
  - 数据库会话
  - 村庄ID
  - 家庭编号
  - 家庭地址（可选）
  - 户主姓名（可选）
- **返回值**：创建的家庭对象

#### update_household(db: Session, household_id: int, **kwargs)
- **功能**：更新家庭信息
- **参数**：
  - 数据库会话
  - 家庭ID
  - 要更新的字段（village_id, household_code, address, head_of_household）
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
- **添加家庭**：填写家庭编号、选择所属村庄，可选择填写家庭地址和户主姓名
- **编辑家庭**：修改家庭信息，包括家庭编号、所属村庄、家庭地址和户主姓名
- **删除家庭**：删除家庭及其所有成员
- **查看家庭**：点击查看按钮，通过浮层显示家庭详细信息

### 4.2 成员管理
- **添加成员**：为选中的家庭添加成员，填写成员姓名、身份证号等信息
- **编辑成员**：点击成员卡片，弹出对话框可查看和编辑成员详细信息
- **删除成员**：在成员编辑对话框中删除成员

## 5. 注意事项

- 家庭编号和成员身份证号为唯一标识，不可重复
- 家庭必须属于某个村庄
- 成员必须属于某个家庭
- 在添加或编辑成员时，身份证号必须符合18位身份证号格式
- 成员卡片显示采用可滚动组件，当成员数量较多时可通过滚动查看
- 家庭查看功能使用Flyout浮层显示，提供良好的用户体验