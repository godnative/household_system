from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel
from qfluentwidgets import MSFluentWindow, NavigationItemPosition, FluentIcon as FIF
from src.views.village_view import VillageWidget
from src.views.household_management_view import HouseholdManagementWidget
from src.views.settings_view import SettingsView
from src.services.auth_service import AuthService

class MainView(MSFluentWindow):
    logout = pyqtSignal()
    
    def __init__(self, user, parent=None):
        super().__init__(parent)
        self.user = user
        self.setWindowTitle('户籍管理系统')
        self.resize(1200, 600)
        self.init_navigation()
    
    def init_navigation(self):
        # 欢迎页面
        welcome_page = QWidget(self)
        welcome_layout = QVBoxLayout(welcome_page)
        welcome_label = QLabel(f'欢迎回来，{self.user.username}！')
        welcome_label.setStyleSheet('font-size: 20px; font-weight: bold;')
        welcome_label.setAlignment(Qt.AlignCenter)
        welcome_layout.addWidget(welcome_label)
        welcome_page.setObjectName('welcome')
        
        # 添加欢迎页面
        self.addSubInterface(welcome_page, FIF.HOME, '主页')
        
        # 系统管理
        if AuthService.check_permission(self.user, 'user_manage') or AuthService.check_permission(self.user, 'role_manage'):
            # 创建系统设置页面
            settings_page = SettingsView(self)
            settings_page.setObjectName('settings')
            self.addSubInterface(settings_page, FIF.SETTING, '系统设置')
        
        # 堂区管理
        if AuthService.check_permission(self.user, 'village_manage'):
            village_page = VillageWidget(self)
            village_page.setObjectName('village')
            self.addSubInterface(village_page, FIF.HOME, '堂区管理')
        
        # 家庭管理
        if AuthService.check_permission(self.user, 'household_manage') or AuthService.check_permission(self.user, 'member_manage'):
            household_management_page = HouseholdManagementWidget(self)
            household_management_page.setObjectName('household_management')
            self.addSubInterface(household_management_page, FIF.HOME, '家庭管理')
        
        # 退出按钮
        self.navigationInterface.addItem(
            routeKey='logout',
            icon=FIF.CLOSE, 
            text='退出',
            onClick=self.handle_logout,
            selectable=False,
            position=NavigationItemPosition.BOTTOM,
        )
        
        # 设置当前页面
        self.navigationInterface.setCurrentItem('welcome')
    
    def handle_logout(self):
        # 退出登录，发射信号
        self.logout.emit()
        self.close()