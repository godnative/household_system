import sys
from PyQt5.QtWidgets import QApplication
from src.views.login_view import LoginView
from src.views.main_view import MainView
from src.models import SessionLocal, User, Role, Permission

class App(QApplication):
    def __init__(self, argv):
        super().__init__(argv)
        self.user = None
        self.main_window = None
        self.login_window = None
        
        # 检查是否有debug参数
        debug_mode = '--debug' in argv
        
        if debug_mode:
            # 调试模式：跳过登录，直接进入主界面
            self.create_default_user()
            self.show_main_window()
        else:
            # 正常模式：显示登录界面
            self.show_login_window()
    
    def create_default_user(self):
        """创建默认用户对象"""
        # 创建默认权限
        permissions = [
            Permission(id=1, name='user_manage', description='用户管理权限'),
            Permission(id=2, name='role_manage', description='角色管理权限'),
            Permission(id=3, name='village_manage', description='堂区管理权限'),
            Permission(id=4, name='household_manage', description='家庭管理权限'),
            Permission(id=5, name='member_manage', description='成员管理权限')
        ]
        
        # 创建一个默认的超级管理员用户对象
        default_role = Role(id=1, name='超级管理员', description='拥有所有权限')
        default_role.permissions = permissions
        
        self.user = User(
            id=1,
            username='admin',
            password_hash='',
            role_id=1,
            role=default_role,
            village_id=None
        )
    
    def show_login_window(self):
        """显示登录窗口"""
        self.login_window = LoginView()
        self.login_window.login_success.connect(self.on_login_success)
        self.login_window.show()
    
    def on_login_success(self, user):
        """登录成功回调"""
        self.user = user
        self.login_window.close()
        self.show_main_window()
    
    def show_main_window(self):
        """显示主窗口"""
        self.main_window = MainView(self.user)
        self.main_window.logout.connect(self.on_logout)
        self.main_window.show()
    
    def on_logout(self):
        """退出登录回调"""
        self.main_window.close()
        self.show_login_window()

if __name__ == '__main__':
    app = App(sys.argv)
    sys.exit(app.exec_())