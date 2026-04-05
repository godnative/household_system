from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel
from qfluentwidgets import MSFluentWindow, NavigationItemPosition, FluentIcon as FIF
from src.views.village_view import VillageWidget
from src.views.household_view import HouseholdWidget
from src.views.member_view import MemberWidget
from src.views.view_window import ViewWindow
from src.services.auth_service import AuthService

class MainView(MSFluentWindow):
    logout = pyqtSignal()
    
    def __init__(self, user, parent=None):
        super().__init__(parent)
        self.user = user
        self.setWindowTitle('户籍管理系统')
        self.resize(1000, 600)
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
            sys_page = QWidget(self)
            sys_layout = QVBoxLayout(sys_page)
            sys_label = QLabel('系统管理')
            sys_label.setAlignment(Qt.AlignCenter)
            sys_layout.addWidget(sys_label)
            sys_page.setObjectName('system')
            self.addSubInterface(sys_page, FIF.SETTING, '系统管理')
        
        # 村管理
        if AuthService.check_permission(self.user, 'village_manage'):
            village_page = VillageWidget(self)
            village_page.setObjectName('village')
            self.addSubInterface(village_page, FIF.HOME, '村管理')
        
        # 家庭管理
        if AuthService.check_permission(self.user, 'household_manage'):
            household_page = HouseholdWidget(self)
            household_page.setObjectName('household')
            self.addSubInterface(household_page, FIF.HOME, '家庭管理')
        
        # 成员管理
        if AuthService.check_permission(self.user, 'member_manage'):
            member_page = MemberWidget(self)
            member_page.setObjectName('member')
            self.addSubInterface(member_page, FIF.PEOPLE, '成员管理')
        
        # 查看窗口
        if AuthService.check_permission(self.user, 'village_manage'):
            view_page = ViewWindow(self)
            view_page.setObjectName('view')
            self.addSubInterface(view_page, FIF.HOME, '查看窗口')
        
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