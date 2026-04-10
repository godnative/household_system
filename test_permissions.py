"""
测试权限系统
"""
from src.models import SessionLocal, User, Role, Permission, Village
from src.services.auth_service import AuthService
from src.services.permission_service import PermissionService
from src.constants import (
    PERM_USER_MANAGE, PERM_HOUSEHOLD_MANAGE, PERM_HOUSEHOLD_VIEW,
    ROLE_SUPER_ADMIN, ROLE_DATA_ENTRY, ROLE_OBSERVER
)

def test_permissions():
    """测试权限系统"""
    db = SessionLocal()

    try:
        print("=" * 60)
        print("测试权限系统")
        print("=" * 60)

        # 1. 验证角色和权限
        print("\n1. 验证角色和权限")
        print("-" * 60)

        roles = PermissionService.get_all_roles(db)
        print(f"总共有 {len(roles)} 个角色:")
        for role in roles:
            perms = [p.name for p in role.permissions]
            print(f"  - {role.name}: {', '.join(perms)}")

        permissions = PermissionService.get_all_permissions(db)
        print(f"\n总共有 {len(permissions)} 个权限:")
        for perm in permissions:
            print(f"  - {perm.name}: {perm.description}")

        # 2. 验证默认管理员用户
        print("\n2. 验证默认管理员用户")
        print("-" * 60)

        admin_user = AuthService.get_user_by_username(db, 'admin')
        if admin_user:
            print(f"用户名: {admin_user.username}")
            print(f"角色: {admin_user.role.name}")
            print(f"拥有 {len(admin_user.role.permissions)} 个权限")
            print(f"可以访问所有堂区: {AuthService.get_user_accessible_villages(admin_user) is None}")
        else:
            print("错误：默认管理员用户不存在！")
            return

        # 3. 创建测试用户
        print("\n3. 创建测试用户")
        print("-" * 60)

        # 获取角色
        data_entry_role = db.query(Role).filter(Role.name == ROLE_DATA_ENTRY).first()
        observer_role = db.query(Role).filter(Role.name == ROLE_OBSERVER).first()

        # 获取默认堂区
        default_village = db.query(Village).first()
        if not default_village:
            print("警告：没有堂区数据，无法测试录入员和观察员")
        else:
            print(f"默认堂区: {default_village.name} (ID: {default_village.id})")

            # 创建录入员用户
            data_entry_user = AuthService.create_user(
                db, 'data_entry1', 'password123',
                data_entry_role.id, default_village.id
            )
            print(f"\n创建录入员: {data_entry_user.username}")
            print(f"  角色: {data_entry_user.role.name}")
            print(f"  所属堂区: {data_entry_user.village.name if data_entry_user.village else '无'}")
            accessible_villages = AuthService.get_user_accessible_villages(data_entry_user)
            print(f"  可访问堂区: {accessible_villages}")

            # 创建观察员用户
            observer_user = AuthService.create_user(
                db, 'observer1', 'password123',
                observer_role.id, None
            )
            # 为观察员分配可访问堂区
            PermissionService.assign_villages_to_user(db, observer_user.id, [default_village.id])
            # 重新获取用户以更新关系
            observer_user = db.query(User).filter(User.id == observer_user.id).first()

            print(f"\n创建观察员: {observer_user.username}")
            print(f"  角色: {observer_user.role.name}")
            print(f"  可访问堂区: {[v.name for v in observer_user.accessible_villages]}")

        # 4. 测试权限检查
        print("\n4. 测试权限检查")
        print("-" * 60)

        test_users = [
            (admin_user, '超级管理员'),
            (data_entry_user, '录入员'),
            (observer_user, '观察员')
        ] if default_village else [(admin_user, '超级管理员')]

        for user, role_desc in test_users:
            print(f"\n{role_desc} ({user.username}):")
            print(f"  - 用户管理权限: {AuthService.check_permission(user, PERM_USER_MANAGE)}")
            print(f"  - 家庭管理权限: {AuthService.check_permission(user, PERM_HOUSEHOLD_MANAGE)}")
            print(f"  - 家庭查看权限: {AuthService.check_permission(user, PERM_HOUSEHOLD_VIEW)}")

        # 5. 测试堂区访问控制
        if default_village:
            print("\n5. 测试堂区访问控制")
            print("-" * 60)

            for user, role_desc in test_users:
                can_access = AuthService.check_village_access(user, default_village.id)
                print(f"{role_desc} 可以访问堂区 '{default_village.name}': {can_access}")

        print("\n" + "=" * 60)
        print("测试完成！")
        print("=" * 60)
        print("\n提示：现在可以运行应用并测试：")
        print("  1. 使用 admin/admin123 登录（超级管理员）")
        print("  2. 在'用户角色管理'中查看用户和角色")
        if default_village:
            print("  3. 使用 data_entry1/password123 登录（录入员）")
            print("  4. 使用 observer1/password123 登录（观察员）")

    except Exception as e:
        print(f"\n错误：{e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()

if __name__ == '__main__':
    test_permissions()
