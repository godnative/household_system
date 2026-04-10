"""
权限和角色常量定义
"""

# 权限名称常量
PERM_USER_MANAGE = 'user_manage'          # 用户管理权限
PERM_ROLE_MANAGE = 'role_manage'          # 角色管理权限
PERM_VILLAGE_MANAGE = 'village_manage'    # 堂区管理权限
PERM_HOUSEHOLD_MANAGE = 'household_manage'  # 家庭完整管理权限（CRUD）
PERM_HOUSEHOLD_VIEW = 'household_view'    # 家庭查看权限（只读）
PERM_MEMBER_MANAGE = 'member_manage'      # 成员完整管理权限（CRUD）
PERM_MEMBER_VIEW = 'member_view'          # 成员查看权限（只读）

# 角色名称常量
ROLE_SUPER_ADMIN = '超级管理员'
ROLE_DATA_ENTRY = '录入员'
ROLE_OBSERVER = '观察员'
