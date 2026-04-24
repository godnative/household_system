# PyQt5 vs Web 功能对比分析

## 一、关键缺失功能

### 1. 家庭-成员联动逻辑 ❌
**PyQt5实现**：
- 选择堂区后，加载该堂区的家庭列表
- 点击家庭行，自动加载该家庭的所有成员
- 成员以标签页形式显示（TabBar）
- 每个成员一个标签，点击标签查看详情
- 关闭标签可删除成员

**Web当前状态**：家庭和成员完全分离，无联动

### 2. 成员照片功能 ❌
**PyQt5实现**：
- 上传时自动缩放至120x160像素
- 存储在 `static/member_photos/` 目录
- 打印时嵌入HTML模板

**Web当前状态**：照片字段存在但功能不完整

### 3. 圣事记录完整编辑 ❌
**PyQt5实现**：
- 基本信息：姓名、性别、出生日期、圣名、与户主关系、文化程度、何时迁入、从事职业、教籍证件编号
- 圣洗：施行人、代父/母、领洗时间、备注
- 初领圣体时间
- 补礼：神父、地点、日期
- 坚振：年月日、施行人、代父/母、圣名、年龄、地点
- 婚配：年月日、主礼神父、证人、宽免事项、宽免神父、地点
- 病人傅油：年月日、施行人、地点、死亡日期、年龄
- 其他：所属善会、备注

**Web当前状态**：部分字段缺失或不可编辑

### 4. PDF打印功能 ❌
**PyQt5实现**：
- 使用HTML模板（doc/a3.html, a4.html）
- 家庭打印：家庭信息页 + 每个成员单独一页
- 成员打印：完整圣事记录表格
- 照片嵌入打印输出

**Web当前状态**：无PDF导出功能

### 5. 数据库导入功能 ❌
**PyQt5实现**：
- 导出：打开数据库文件夹
- 还原：选择.db文件，自动备份当前数据库后替换

**Web当前状态**：只有导出，无导入功能

### 6. 设为户主功能 ❌
**PyQt5实现**：
- 编辑成员时可点击"设为户主"
- 自动更新家庭户主姓名
- 自动设置成员关系为"本人"

**Web当前状态**：缺失

---

## 二、PyQt5完整字段清单

### 成员表 (members)

| 字段名 | 类型 | 说明 | Web状态 |
|--------|------|------|---------|
| id | Integer | 主键 | ✅ |
| household_id | Integer | 外键-家庭 | ✅ |
| name | String(50) | 姓名 | ✅ |
| gender | String(10) | 性别 | ✅ |
| birth_date | Date | 出生日期 | ✅ |
| baptismal_name | String(50) | 圣名 | ✅ |
| relation_to_head | String(20) | 与户主关系 | ✅ |
| education | String(50) | 文化程度 | ✅ |
| move_in_date | Date | 何时迁入 | ✅ |
| occupation | String(100) | 从事职业 | ✅ |
| church_id | String(50) | 教籍证件编号 | ✅ |
| photo | String(255) | 照片路径 | ⚠️ 功能不完整 |
| baptism_priest | String(50) | 圣洗-施行人 | ✅ |
| baptism_godparent | String(50) | 圣洗-代父/母 | ✅ |
| baptism_date | Date | 圣洗-领洗时间 | ✅ |
| baptism_note | Text | 圣洗-备注 | ✅ |
| first_communion_date | Date | 初领圣体时间 | ✅ |
| supplementary_priest | String(50) | 补礼-神父 | ✅ |
| supplementary_place | String(100) | 补礼-地点 | ✅ |
| supplementary_date | Date | 补礼-日期 | ✅ |
| confirmation_date | Date | 坚振-年月日 | ✅ |
| confirmation_priest | String(50) | 坚振-施行人 | ✅ |
| confirmation_godparent | String(50) | 坚振-代父/母 | ✅ |
| confirmation_name | String(50) | 坚振-圣名 | ✅ |
| confirmation_age | Integer | 坚振-年龄 | ✅ |
| confirmation_place | String(100) | 坚振-地点 | ✅ |
| marriage_date | Date | 婚配-年月日 | ✅ |
| marriage_priest | String(50) | 婚配-主礼神父 | ✅ |
| marriage_witness | String(100) | 婚配-证人 | ✅ |
| marriage_dispensation_item | String(100) | 婚配-宽免事项 | ✅ |
| marriage_dispensation_priest | String(50) | 婚配-宽免神父 | ✅ |
| marriage_place | String(100) | 婚配-地点 | ✅ |
| anointing_date | Date | 病人傅油-年月日 | ✅ |
| anointing_priest | String(50) | 病人傅油-施行人 | ✅ |
| anointing_place | String(100) | 病人傅油-地点 | ✅ |
| death_date | Date | 死亡日期 | ✅ |
| death_age | Integer | 死亡年龄 | ✅ |
| association | String(100) | 所属善会 | ✅ |
| note | Text | 备注 | ✅ |

### 家庭表 (households)

| 字段名 | 类型 | 说明 | Web状态 |
|--------|------|------|---------|
| id | Integer | 主键 | ✅ |
| village_id | Integer | 外键-堂区 | ✅ |
| plot_number | Integer | 片号 | ✅ |
| address | String(200) | 家庭住址 | ✅ |
| phone | String(20) | 电话 | ✅ |
| head_of_household | String(50) | 户主姓名 | ✅ |

---

## 三、交互逻辑对比

### PyQt5 交互流程
```
选择堂区 → 加载家庭列表 → 点击家庭行 → 加载成员标签页
                                    ↓
                            点击成员标签 → 显示成员详情
                                    ↓
                            点击"修改"按钮 → 编辑成员弹窗
                                    ↓
                            点击"设为户主" → 更新家庭户主
```

### Web 需要实现的交互
```
选择堂区 → 加载家庭列表 → 点击家庭行 → 右侧显示成员列表
                                    ↓
                            点击成员 → 显示成员详情卡片
                                    ↓
                            点击"编辑" → 编辑成员对话框
                                    ↓
                            点击"设为户主" → 更新家庭户主
```

---

## 四、整改优先级

| 优先级 | 功能 | 原因 |
|--------|------|------|
| P0 | 家庭-成员联动 | 核心交互逻辑，影响所有操作 |
| P0 | 成员照片功能 | 打印必需，用户可见 |
| P0 | 圣事记录编辑 | 核心业务字段 |
| P1 | PDF打印 | 重要输出功能 |
| P1 | 数据库导入 | 管理员必需功能 |
| P2 | 设为户主 | 便捷功能 |
