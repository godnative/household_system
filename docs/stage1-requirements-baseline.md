# 阶段 1：需求基线冻结

## 1. 目标
将当前 PyQt5 桌面系统的真实功能、页面、字段、权限、打印和静态资源固化为 Web 迁移的唯一真相源，避免后续实现过程中出现“桌面已支持但 Web 遗漏”或“错误复刻”的情况。

## 2. 功能矩阵

| 模块 | 页面/入口 | 核心功能 | 关键权限 | 当前实现依据 |
|---|---|---|---|---|
| 登录认证 | 登录页 | 用户名密码登录、登录失败提示、记住密码、登录成功进入主界面 | 无登录前权限；登录后按角色进入 | `src/views/login_view.py`、`src/app.py` |
| 首页/欢迎页 | 主界面主页 | 欢迎语、欢迎图片展示、退出登录 | 已登录用户 | `src/views/main_view.py` |
| 堂区管理 | 主界面→堂区管理 | 堂区列表、详情、添加、编辑、删除、照片上传 | `village_manage` | `src/views/village_view.py` |
| 家庭管理 | 主界面→家庭管理 | 选择堂区、家庭列表、查看、添加、编辑、删除、打印 | `household_manage` / `household_view` | `src/views/household_management_view.py` |
| 成员管理 | 家庭管理右侧标签区 | 成员列表、详情、添加、编辑、删除、照片处理、设置户主 | `member_manage` / `member_view` | `src/views/household_management_view.py` |
| 搜索 | 主界面→搜索 | 家庭搜索、成员搜索、结果家庭列表、成员详情、打印 | 家庭/成员查看或管理权限 | `src/views/search_view.py`、`src/services/search_service.py` |
| 用户角色管理 | 主界面→用户角色管理 | 管理员可管用户/角色/权限/堂区范围；普通用户看个人信息和改密码 | `user_manage` / `role_manage` | `src/views/user_role_management_view.py` |
| 系统设置 | 主界面→系统设置 | 数据库信息展示、打开数据库目录、还原数据库 | 实际由用户/角色管理权限控制入口 | `src/views/main_view.py`、`src/services/database_service.py` |
| 打印输出 | 家庭管理/搜索 | 家庭打印、成员打印、A3/A4 模板、分页打印 | 依赖可访问对应数据 | `src/views/household_management_view.py`、`src/views/search_view.py`、`src/views/member_excel_renderer.py`、`src/views/household_excel_renderer.py` |
| 静态资源展示 | 登录页/欢迎页/照片 | 登录背景、logo、欢迎图、堂区照片、成员照片 | 视图级展示 | `src/views/login_view.py`、`src/views/main_view.py`、`src/views/village_view.py`、`src/views/household_management_view.py` |

## 3. 页面映射表

| 现有 PyQt 页面 | 用户可见功能 | 建议 Web 对应形态 | 备注 |
|---|---|---|---|
| `LoginView` | 登录、记住密码、背景图、logo | 独立登录页 | 登录背景与 logo 必须复用或等价保留 |
| `MainView` 主页 | 欢迎语、欢迎图、退出 | Dashboard / Home 页面 | 欢迎图必须纳入迁移范围 |
| `VillageWidget` | 堂区列表 + 右侧详情 | 堂区管理页面（列表 + 详情抽屉/侧栏） | 含堂区照片 |
| `HouseholdManagementWidget` | 堂区切换、家庭列表、成员标签详情 | 家庭管理页 + 成员详情区域 | 当前是复合页面，Web 可拆分更清晰 |
| `SearchView` | 家庭搜索/成员搜索 | 搜索页 | 需保留家庭优先搜索逻辑 |
| `UserRoleManagementView` | 用户管理/角色管理/个人信息 | 用户角色管理页 | 管理员与普通用户看到的内容不同 |
| `SettingsView` | 数据库信息、导入导出 | 系统设置页 | Web 需重定义备份恢复交互 |

## 4. 关键业务实体与字段字典

### 4.1 Village（堂区）
来源：`src/models/household.py:6-23`
- `id`
- `name`
- `code`
- `establishment_date`
- `village_priest`
- `address`
- `description`
- `photo`
- `created_at`
- `updated_at`

业务说明：
- 堂区编码唯一。
- 堂区可关联多个家庭、多个用户。
- 堂区照片在管理页详情中展示。

### 4.2 Household（家庭）
来源：`src/models/household.py:24-39`
- `id`
- `village_id`
- `plot_number`
- `address`
- `phone`
- `head_of_household`
- `created_at`
- `updated_at`

业务说明：
- 家庭属于一个堂区。
- 家庭下可有多个成员。
- 户主字段可为空，通常由成员关系决定。
- 家庭支持打印。

### 4.3 Member（成员）
来源：`src/models/household.py:40-95`

基础字段：
- `id`
- `household_id`
- `name`
- `gender`
- `birth_date`
- `baptismal_name`
- `relation_to_head`
- `education`
- `move_in_date`
- `occupation`
- `church_id`
- `photo`
- `association`
- `note`

圣洗：
- `baptism_priest`
- `baptism_godparent`
- `baptism_date`
- `baptism_note`

初领圣体：
- `first_communion_date`

补礼：
- `supplementary_priest`
- `supplementary_place`
- `supplementary_date`

坚振：
- `confirmation_date`
- `confirmation_priest`
- `confirmation_godparent`
- `confirmation_name`
- `confirmation_age`
- `confirmation_place`

婚配：
- `marriage_date`
- `marriage_priest`
- `marriage_witness`
- `marriage_dispensation_item`
- `marriage_dispensation_priest`
- `marriage_place`

病人傅油 / 死亡：
- `anointing_date`
- `anointing_priest`
- `anointing_place`
- `death_date`
- `death_age`

业务说明：
- 成员详情是当前系统信息量最大的核心模块。
- 成员照片统一处理为 120x160。
- 搜索覆盖成员 20+ 字段。
- 成员详情可打印。

### 4.4 User（用户）
来源：`src/models/user.py:7-22`
- `id`
- `username`
- `password_hash`
- `role_id`
- `village_id`
- `created_at`
- `updated_at`
- `accessible_villages`（多对多关系）

业务说明：
- 录入员通过 `village_id` 绑定所属堂区。
- 观察员通过 `accessible_villages` 绑定多个可访问堂区。

### 4.5 Role / Permission（角色 / 权限）
来源：`src/models/auth.py:17-36`、`src/constants/permissions.py:1-18`

角色：
- 超级管理员
- 录入员
- 观察员

权限：
- `user_manage`
- `role_manage`
- `village_manage`
- `household_manage`
- `household_view`
- `member_manage`
- `member_view`

## 5. 权限矩阵

| 角色 | 用户/角色管理 | 堂区管理 | 家庭管理 | 家庭查看 | 成员管理 | 成员查看 | 数据范围 |
|---|---|---|---|---|---|---|---|
| 超级管理员 | 是 | 是 | 是 | 是 | 是 | 是 | 全部堂区 |
| 录入员 | 否 | 否 | 是 | 含在管理权限内 | 是 | 含在管理权限内 | 仅所属堂区 |
| 观察员 | 否 | 否 | 否 | 是 | 否 | 是 | 多个授权堂区 |

补充说明：
- UI 层会禁用无权限按钮，但真正的数据过滤由服务层完成。
- 搜索也必须套用堂区范围过滤。
- 用户角色管理页对管理员和普通用户是两套界面。

## 6. 服务层规则基线

### 6.1 AuthService
来源：`src/services/auth_service.py`
- 使用 bcrypt 做密码哈希与校验。
- 登录校验逻辑为：按用户名查用户 → 校验密码哈希 → 返回用户对象或 `None`。
- 权限判断逻辑为：遍历用户角色上的权限列表。
- 数据范围逻辑：
  - 若拥有 `user_manage` 或 `role_manage`，视为超级管理员，可访问全部堂区，返回 `None`。
  - 若有 `village_id`，视为录入员，仅返回所属堂区。
  - 若有 `accessible_villages`，视为观察员，返回可访问堂区列表。
- 还提供按堂区/家庭粒度判断访问权限的服务接口。
- 用户创建与更新时，密码必须重新哈希。

### 6.2 PermissionService
来源：`src/services/permission_service.py`
- 提供角色 CRUD。
- 提供权限列表读取。
- 支持为角色批量分配权限，分配时先清空旧权限再写入新权限。
- 支持为观察员分配可访问堂区，分配时先清空旧关联再写入新关联。
- 提供读取用户可访问堂区列表的能力。

### 6.3 VillageService
来源：`src/services/village_service.py`
- 提供堂区 CRUD。
- 提供按名称/代码搜索堂区。
- 删除堂区前会检查是否仍有关联家庭；若有家庭则删除失败。
- 创建堂区要求提供名称、编码、建立日期、堂区神父、地址。

### 6.4 HouseholdService
来源：`src/services/household_service.py`
- 提供家庭 CRUD。
- 提供按堂区过滤的家庭列表。
- 提供按户主、地址、电话搜索家庭。
- 删除家庭时直接删除记录；由于模型层配置了成员级联删除，因此家庭删除会连带删除成员。

### 6.5 MemberService
来源：`src/services/member_service.py`
- 提供成员 CRUD。
- 支持按家庭或堂区过滤成员。
- 当前服务层代码存在口径风险：`get_member_by_id_number()` 与 `search_members()` 使用了 `Member.id_number`，但现有 `Member` 模型中未见该字段。
- 这意味着“成员搜索字段”和“模型真实字段”之间存在不一致，必须在迁移前作为显式差异记录。

### 6.6 SearchService
来源：`src/services/search_service.py`
- 家庭搜索前先做堂区范围过滤。
- 家庭搜索字段：`head_of_household`、`address`、`phone`、`plot_number`。
- 成员搜索前先做堂区范围过滤。
- 成员搜索字段覆盖基础信息、圣事字段、备注字段，共 20+ 项。
- 成员搜索返回的是“包含匹配成员的家庭列表”，而不是直接返回成员列表。

### 6.7 DatabaseService
来源：`src/services/database_service.py`
- 当前桌面版数据库备份/恢复是文件系统级操作，不是逻辑导入导出。
- 支持：
  - 打开数据库目录
  - 校验 SQLite 文件头
  - 还原数据库前自动重命名原数据库作为备份
  - 读取数据库文件路径、大小、修改时间
- Web 迁移时不能平移交互，但此业务目标必须保留为需求基线。

## 7. 打印需求清单

### 7.1 家庭打印
来源：`src/views/household_management_view.py`、`src/views/household_excel_renderer.py`
- 支持家庭信息打印
- 支持从家庭管理页发起
- 支持从搜索页发起
- 使用 HTML 模板渲染
- 需要分页能力

### 7.2 成员打印
来源：`src/views/search_view.py:301-304`、`src/views/member_excel_renderer.py`
- 支持成员详情打印
- 每个成员单独页面
- 支持 HTML 模板渲染
- 含照片展示

### 7.3 模板资产
- `doc/a3.html`
- `doc/a4.html`
- `doc/a3_print.html`
- `doc/a4_print.html`

迁移要求：
- Web 端必须保留“家庭 + 成员”的打印能力。
- A3/A4 模板都应纳入需求基线。
- 分页逻辑、字段完整性、照片展示是重点验收项。

## 8. 打印字段映射基线

### 8.1 家庭打印字段
来源：`src/views/household_excel_renderer.py:16-21`
- 所属堂区占位 → `village.name`
- 家庭户号占位 → `household.id`
- 片号占位 → `household.plot_number`
- 家庭住址占位 → `household.address`
- 户主姓名占位 → `household.head_of_household`
- 电话占位 → `household.phone`

### 8.2 成员打印字段
来源：`src/views/member_excel_renderer.py:15-58`

基础信息：
- 姓名占位 → `member.name`
- 性别占位 → `member.gender`
- 圣名占位 → `member.baptismal_name`
- 出生日期占位 → `member.birth_date`
- 文化程度占位 → `member.education`
- 与户主关系占位 → `member.relation_to_head`
- 何时迁入占位 → `member.move_in_date`
- 从事职业占位 → `member.occupation`
- 教籍证件编号占位 → `member.church_id`

圣洗：
- 圣洗施行人占位 → `member.baptism_priest`
- 圣洗代父占位 → `member.baptism_godparent`
- 领洗时间占位 → `member.baptism_date`
- 圣洗备注占位 → `member.baptism_note`

初领圣体：
- 初领圣体时间占位 → `member.first_communion_date`

补礼：
- 补礼神父占位 → `member.supplementary_priest`
- 补礼地点占位 → `member.supplementary_place`
- 补礼日期占位 → `member.supplementary_date`

坚振：
- 坚振日期占位 → `member.confirmation_date`
- 坚振施行人占位 → `member.confirmation_priest`
- 坚振代父占位 → `member.confirmation_godparent`
- 坚振圣名占位 → `member.confirmation_name`
- 坚振年龄占位 → `member.confirmation_age`
- 坚振地点占位 → `member.confirmation_place`

婚配：
- 婚配日期占位 → `member.marriage_date`
- 婚配主礼神父占位 → `member.marriage_priest`
- 婚配证人占位 → `member.marriage_witness`
- 婚配事项占位 → `member.marriage_dispensation_item`
- 婚配神父占位 → `member.marriage_dispensation_priest`
- 婚配地点占位 → `member.marriage_place`

病人傅油 / 死亡：
- 病人傅油日期占位 → `member.anointing_date`
- 病人傅油施行人占位 → `member.anointing_priest`
- 病人傅油地点占位 → `member.anointing_place`
- 病人傅油死亡日期占位 → `member.death_date`
- 病人傅油年龄占位 → `member.death_age`

其他：
- 备注占位 → `member.note`
- 所属善会占位 → `member.association`
- 图片区域 → `member.photo`，尺寸要求 `120x160`

### 8.3 打印渲染规则
- 空值显示为“无”。
- 某些日期字段若等于 `1752-09-14` 也被视为“无”。
- 成员打印模板里若有照片，则替换“图片”占位区域为 `<img>` 标签。
- 家庭与成员打印模板的 HTML 文件名由 `for_print` 参数决定。

## 9. 静态资源迁移清单

### 9.1 登录页候选资源
来源：`src/views/login_view.py`
- `resource/images/login_background.jpg`
- `resource/images/background.jpg`
- `static/login_background.jpg`
- `resource/images/logo.png`
- `static/logo.png`

### 9.2 欢迎页资源
来源：`src/views/main_view.py`
- `static/welcome_image.jpg`

### 9.3 业务图片资源
- 堂区照片：`src/views/village_view.py`
- 成员照片：`src/views/household_management_view.py`

### 9.4 当前已确认存在
- `/root/household_system/static/welcome_image.jpg`

### 9.5 当前待确认存在
- `resource/images/login_background.jpg`
- `resource/images/background.jpg`
- `static/login_background.jpg`
- `resource/images/logo.png`
- `static/logo.png`

## 10. 页面与交互规则摘要

### 登录页
- 启动时显示登录页，登录成功后进入主界面。
- 支持用户名、密码、回车登录。
- 支持记住密码（桌面版为本地文件 + Base64 混淆，Web 不可照搬实现，但功能语义要记录）。

### 欢迎页
- 显示欢迎语和欢迎图片。
- 提供退出入口。

### 堂区管理
- 列表 + 详情双栏。
- 添加/编辑堂区时支持照片上传。
- 堂区详情可展示简介、地址、神父、照片。

### 家庭管理
- 先选堂区，再加载家庭。
- 切换堂区时会刷新家庭列表，同时清空右侧成员标签区域，并禁用“添加成员”按钮。
- 家庭列表每行有查看、编辑、删除、打印。
- “查看”以浮层方式展示家庭户号、片号、堂区、地址、电话、户主等摘要信息。
- 无权限时编辑/删除按钮禁用。
- 添加家庭时，家庭户号由系统自动生成并只读；户主姓名字段只读，需后续在成员管理中设置。
- 新增/编辑家庭时均可重新选择所属堂区，候选堂区来自全量堂区列表。
- 添加家庭时校验片号为数字、地址不能为空、电话为数字。
- 删除家庭成功后，会刷新家庭列表、清空成员标签，并再次禁用“添加成员”按钮。
- 家庭打印为“一次打印整个家庭包”，内容顺序是：家庭页在前，其后按成员顺序逐个追加成员页，中间插入分页符。
- 家庭打印成功提示会显示“家庭编号 + 成员数量”；失败时显示错误提示。

### 成员管理
- 必须先选定家庭，才能新增成员；未选家庭时会直接提示错误。
- 家庭被选中后才会加载成员；只有具备 `member_manage` 权限时，“添加成员”按钮才会启用。
- 成员以标签页形式展示；每个标签保存成员 ID，并与右侧堆叠内容区域一一对应。
- 关闭成员标签的行为实际是“删除成员”，不是单纯关闭视图；系统会先做权限校验，再弹出确认框，确认后才真正删除成员。
- 成员新增/编辑表单覆盖完整业务分组：基础信息、圣洗、初领圣体、补礼、坚振、婚配、病人傅油、其他信息。
- 基础信息至少包括：姓名、性别、出生日期、圣名、与户主关系、文化程度、何时迁入、从事职业、教籍证件编号、照片。
- 成员详情当前通过 HTML 渲染结果嵌入 `QTextEdit` 展示，而不是结构化表单只读页。
- 成员详情页默认带“修改成员信息”按钮；若当前用户无 `member_manage` 权限，按钮显示但禁用。
- 成员照片通过文件选择器选择后，统一裁剪/缩放为 120x160，并保存到 `static/member_photos/`。
- 新增成员时，照片处理失败不会阻断保存，而是提示“照片处理失败，将不保存照片”。
- 编辑成员时，若新照片处理失败，则保留原有照片，并提示“照片处理失败，保留原有照片”。
- 日期型字段在界面保存时允许为空；若日期控件无效则按 `None` 处理。
- 多个日期控件在新增表单里通过设置非法日期表达“未填写”状态，这是一条现有交互语义。
- 数值型字段中，`confirmation_age` 与 `death_age` 仅在输入为纯数字时转换为整数，否则按空值处理。
- 成员保存成功后，界面会新增对应成员详情标签页，并使用 HTML 渲染展示成员详情，同时提供“修改成员信息”按钮。
- 无权限时不能删除成员。
- 成员详情使用 HTML 视图展示，当前搜索页为只读。
- 成员编辑时会预填全部现有字段；若已有照片则优先展示旧照片，只有用户重新选择图片时才覆盖原文件。
- 成员编辑界面提供“设为户主”操作。
- “设为户主”业务规则为：将当前家庭 `head_of_household` 更新为该成员姓名，将该成员 `relation_to_head` 更新为“本人”，并把同家庭其他原本 `relation_to_head == "本人"` 的成员统一改为“无”。
- “设为户主”完成后需刷新家庭列表与成员列表，并给出成功提示。
- 成员编辑保存成功后，若姓名变更，还会同步更新对应标签标题。
- 成员编辑保存后会重建当前标签内容区，而不是只局部更新字段；这是现有桌面实现方式。

### 搜索
- 家庭搜索优先于成员搜索。
- 家庭搜索支持户主、地址、电话、片号。
- 成员搜索支持姓名、圣名、教友编号、职业、善会、各类圣事字段、备注等。
- 搜索结果左侧是家庭列表，右侧是成员详情。

### 用户角色管理
- 管理员可切换“用户管理”和“角色管理”。
- 普通用户只看“我的信息”和“修改密码”。
- 用户可配置所属堂区或可访问堂区。

### 系统设置 / 数据库
- 当前桌面版设置页会展示数据库路径、文件大小、最后修改时间。
- “导出数据库”实际行为是打开数据库所在目录，便于用户手工复制 SQLite 文件，并不是生成逻辑导出包。
- “还原数据库”流程为：先弹确认框提示风险 → 选择 SQLite 文件 → 校验并导入 → 成功后提示“请重启应用以使更改生效”。
- Web 化后不能平移交互方式，但需求必须保留为“可备份/可恢复数据库”，且需显式定义替代桌面文件操作的交互。

## 10.1 家庭管理页面流程细化

### 初始化与堂区切换
- 页面初始化时先根据当前用户数据范围加载可访问堂区。
- 超级管理员看到全部堂区；录入员和观察员只看到授权堂区。
- 若存在可访问堂区，页面会自动触发首次堂区切换逻辑。
- 切换堂区后会：
  1. 加载该堂区家庭列表；
  2. 清空当前成员标签与右侧详情区域；
  3. 禁用“添加成员”按钮，直到用户重新选中某个家庭。

### 家庭选择
- 点击家庭列表行后，系统取当前行第 1 列的家庭 ID。
- 随后加载该家庭全部成员。
- 若当前用户具有 `member_manage` 权限，则启用“添加成员”按钮，否则保持禁用。

### 家庭查看
- 点击“查看”按钮后，以浮层方式展示家庭摘要信息。
- 展示字段包括：家庭户号、片号、堂区、家庭住址、电话、户主。
- 该查看动作不进入编辑态，也不改变当前成员标签状态。

### 家庭新增
- 通过对话框录入家庭信息。
- `household_id` 只读显示“系统自动生成”。
- `head_of_household` 只读显示“请在成员管理中设置”。
- 保存成功后刷新当前堂区家庭列表。
- 保存失败时会回滚事务，并提示错误信息。

### 家庭编辑
- 编辑对话框会预填当前家庭已有数据。
- 家庭户号只读。
- 户主姓名只读，仍要求通过成员管理界面设定。
- 保存成功后刷新当前堂区家庭列表。
- 保存失败时会回滚事务，并提示错误信息。

### 家庭删除
- 删除成功后会同时触发三件事：
  1. 刷新当前堂区家庭列表；
  2. 清空右侧成员标签；
  3. 禁用“添加成员”按钮。
- 当前删除逻辑未在该视图中再次弹确认框；需求基线需如实记录这一实现现状。

### 家庭打印
- 当前为“家庭 + 全部成员合并打印”。
- 使用 A4 打印机设置。
- 打印内容顺序：家庭 HTML → 分页符 → 每个成员的 HTML。
- 成员页按 `MemberService.get_all_members(db, household_id=...)` 返回顺序拼接。
- 用户确认打印对话框后才会真正发送打印任务。
- 成功提示中会回显家庭编号和成员数量。

## 10.2 成员管理页面流程细化

### 成员加载与展示
- 选择家庭后，系统会先清空所有已有成员标签。
- 然后按成员列表逐个创建标签和右侧详情页。
- 每个标签标题显示成员姓名，内部属性保存成员 ID。
- 右侧详情页由滚动区包裹，核心内容是 `get_member_excel_html(member)` 的 HTML 渲染结果。

### 成员标签关闭
- 标签关闭并非单纯隐藏，而是删除成员。
- 删除前会先检查 `member_manage` 权限。
- 无权限时直接弹“您没有删除成员的权限”。
- 有权限时还会弹确认框，确认后才调用 `MemberService.delete_member()`。
- 删除成功后会移除对应标签和堆叠页。

### 成员新增
- 必须先选中家庭。
- 新增对话框使用滚动区域承载长表单。
- 表单中多个日期字段默认初始化为非法日期，表示当前未填写。
- 照片先本地预览，保存时再写入 `static/member_photos/`。
- 成功后会直接在当前界面新增一个成员标签，而不是整页重新加载。
- 新增完成后界面会自动切换到新标签。

### 成员编辑
- 编辑对话框同样使用滚动区域承载完整长表单。
- 所有已有字段都需要预填，包括日期、文本、多行备注和照片。
- 若已有照片且文件存在，编辑弹窗内会先展示旧照片缩略图。
- 保存成功后会同步更新标签标题与对应内容区域。
- 当前桌面版不是重新调用 HTML 模板刷新详情，而是在部分路径下直接重建 QWidget 内容。

### 设为户主
- 该操作位于编辑成员对话框中。
- 点击后立即修改家庭户主与成员关系，并关闭当前编辑对话框。
- 执行顺序是：
  1. 更新家庭 `head_of_household`；
  2. 更新当前成员 `relation_to_head = "本人"`；
  3. 将同家庭其他“本人”成员改为“无”；
  4. 刷新家庭列表与成员列表；
  5. 提示成功。
- 这说明“户主”并不是家庭表单中独立维护，而是由成员操作反向驱动。

| 模块 | 字段/场景 | 当前规则 | 来源 |
|---|---|---|---|
| 登录 | 用户名、密码 | 两者都不能为空 | `src/views/login_view.py:131-134` |
| 家庭新增/编辑 | `plot_number` | 必须为数字 | `src/views/household_management_view.py:362-370` |
| 家庭新增/编辑 | `address` | 不能为空 | `src/views/household_management_view.py:372-379` |
| 家庭新增/编辑 | `phone` | 若填写则必须为数字 | `src/views/household_management_view.py:381-388` |
| 堂区新增 | `name` / `village_priest` / `address` | 必填 | `src/views/village_view.py:298-320` |
| 堂区照片 | 上传图片 | 允许选择图片文件并缩放保存 | `src/views/village_view.py:273-285`、`23-46` |
| 成员新增 | 前置条件 | 必须先选家庭，否则拒绝新增并提示错误 | `src/views/household_management_view.py` |
| 成员新增/编辑 | `name` / `gender` | 保存时必须指定，否则提示错误 | `src/views/household_management_view.py` |
| 成员新增/编辑 | `confirmation_age` / `death_age` | 仅输入纯数字时才转为整数，否则按空值处理 | `src/views/household_management_view.py` |
| 成员新增 | 保存异常 | `IntegrityError` 时提示“身份证号已存在，请使用其他身份证号” | `src/views/household_management_view.py` |
| 成员照片 | 上传图片 | 统一裁剪/缩放为 120x160 | `src/views/household_management_view.py:20-54` |
| 成员照片 | 预览与替换 | 新增时先本地预览；编辑时优先显示旧照片，重新选择后才替换 | `src/views/household_management_view.py` |
| 成员日期字段 | 空值表达 | 多个日期控件通过非法日期表示“未填写”，保存时转为 `None` | `src/views/household_management_view.py` |
| 权限操作 | 编辑/删除/添加 | 无权限时按钮禁用或操作拒绝 | `src/views/household_management_view.py:92-97`、`210-218` |

说明：
- 当前系统大量校验仍在视图层完成，迁移到 Web 时需下沉为前后端双层校验。
- 阶段 1 只记录“已有规则”，不改规则。

## 12. 测试覆盖矩阵

| 模块 | 现有测试文件 | 当前状态 |
|---|---|---|
| 认证服务 | `tests/test_auth_service.py` | 已覆盖核心认证逻辑 |
| 权限服务 | `tests/test_permission_service.py` | 已覆盖角色/权限相关逻辑 |
| 堂区服务 | `tests/test_village_service.py` | 已覆盖 CRUD 与搜索核心路径 |
| 家庭服务 | `tests/test_household_service.py` | 已覆盖 CRUD 核心路径 |
| 成员服务 | `tests/test_member_service.py` | 已覆盖大部分核心路径，但需警惕 `id_number` 口径问题 |
| 搜索服务 | `tests/test_search_service.py` | 已覆盖家庭/成员搜索及权限过滤 |
| 模型关系 | `tests/test_models.py` | 已覆盖模型结构与关系 |
| GUI | `tests/test_gui.py` | 有覆盖，但对 Web 迁移不能直接复用 |
| 数据库备份恢复 | 无专门测试 | 明显缺失 |
| 打印模板与打印链路 | 无有效自动化测试 | 明显缺失 |
| 静态资源显示 | 无专门测试 | 明显缺失 |

## 13. 差异与风险清单

### 13.1 代码与资源差异风险
- 登录页代码引用了多个背景图和 logo 候选路径，但当前仓库中尚未全部确认存在。
- 欢迎页图片已确认存在并已迁移到 Web 资源目录。

### 13.2 桌面端特性风险
- 数据库备份/还原依赖本地文件系统和系统文件管理器，Web 需要重新设计。
- 打印依赖 Qt 打印链路，Web 需改为浏览器打印或 PDF 服务。
- 记住密码依赖本地文件存储，Web 需转为安全认证机制。

### 13.3 业务一致性风险
- 搜索服务覆盖大量成员字段，Web 若遗漏字段会导致功能不等价。
- 成员信息字段非常多，任何字段遗漏都会影响教籍记录完整性。
- 权限不只是页面显隐，还包括数据范围过滤，必须以后端为准。

### 13.4 模型/实现口径风险
- `MemberService` 使用了 `Member.id_number`，但当前 `Member` 模型未见该字段，这是显式不一致项。
- 成员新增失败提示里仍存在“身份证号已存在”的界面文案，说明当前视图交互与模型字段命名之间可能还有未梳理完的历史遗留口径。
- 打印模板使用了 `1752-09-14` 作为日期空值哨兵，这属于隐藏业务规则，必须保留或显式替换。
- 家庭管理页中的“关闭成员标签”实际语义是删除成员，而不是普通关闭标签；若 Web 端误实现为无副作用关闭，会造成功能偏差。
- 当前家庭删除流程在该视图内未再次弹确认框，属于真实现状，但 Web 迁移阶段需要明确这是要保持还是要改进的交互差异。
- 视图层中存在大量表单校验和图片处理逻辑，若只迁服务层会漏掉行为。

## 14. 阶段 1 交付物
本阶段应产出并持续更新：
- 本文档：需求基线冻结稿
- 功能矩阵
- 页面映射表
- 字段字典
- 权限矩阵
- 服务层规则基线
- 打印字段映射基线
- 字段校验矩阵
- 测试覆盖矩阵
- 静态资源迁移清单
- 差异与风险清单
