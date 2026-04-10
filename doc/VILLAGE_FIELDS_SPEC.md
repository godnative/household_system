# 堂区字段说明文档

## 1. 字段结构

| 字段名 | 数据类型 | 约束 | 描述 |
|-------|---------|------|------|
| id | Integer | 主键，自增 | 堂区唯一标识，内部使用，不暴露给用户 |
| name | String(100) | 非空 | 堂区名称 |
| establishment_date | Date | 非空 | 堂区建立日期 |
| village_priest | String(50) | 非空 | 堂区神父 |
| address | String(200) | 非空 | 堂区地址 |
| description | Text | 可选 | 堂区简介 |
| photo | String(255) | 可选 | 堂区照片路径，为空时显示"暂无图片" |
| created_at | DateTime | 自动生成 | 创建时间 |
| updated_at | DateTime | 自动更新 | 更新时间 |

## 2. 操作函数

### 2.1 VillageService 类

#### get_all_villages(db: Session)
- **功能**：获取所有堂区
- **参数**：数据库会话
- **返回值**：堂区列表

#### get_village_by_id(db: Session, village_id: int)
- **功能**：根据ID获取堂区
- **参数**：数据库会话，堂区ID
- **返回值**：堂区对象或None

#### get_village_by_code(db: Session, code: str)
- **功能**：根据代码获取堂区
- **参数**：数据库会话，堂区代码
- **返回值**：堂区对象或None

#### search_villages(db: Session, keyword: str = None)
- **功能**：搜索堂区
- **参数**：数据库会话，搜索关键词
- **返回值**：符合条件的堂区列表

#### create_village(db: Session, name: str, establishment_date: date, village_priest: str, address: str, description: str = None, photo: str = None)
- **功能**：创建新堂区
- **参数**：
  - 数据库会话
  - 堂区名称
  - 建立日期
  - 堂区神父
  - 堂区地址
  - 堂区简介（可选）
  - 堂区照片（可选）
- **返回值**：创建的堂区对象

#### update_village(db: Session, village_id: int, **kwargs)
- **功能**：更新堂区信息
- **参数**：
  - 数据库会话
  - 堂区ID
  - 要更新的字段（name, establishment_date, village_priest, address, description, photo）
- **返回值**：更新后的堂区对象或None

#### delete_village(db: Session, village_id: int)
- **功能**：删除堂区
- **参数**：数据库会话，堂区ID
- **返回值**：布尔值，表示删除是否成功

## 3. 照片处理

- 照片路径存储在photo字段中
- 为空时显示"暂无图片"
- 有照片时，需要将照片尺寸缩放到合适的尺寸（建议最大宽度800px，高度自适应）
- 在创建堂区和更新堂区时可以点击对应位置更新图片
- 在查看堂区信息时不可以更改照片

## 4. 删除检查

- 删除堂区时，必须检查当前堂区下是否有家庭
- 如果有家庭，应弹窗提醒用户删除干净家庭后才能删除堂区
- 只有当堂区下没有家庭时，才能执行删除操作

## 5. 注意事项

- 堂区ID为自增主键，自动生成，不允许修改
- 堂区名称、建立日期、堂区神父、堂区地址为必填字段
- 堂区照片为可选字段