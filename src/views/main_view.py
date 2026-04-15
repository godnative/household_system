from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt5.QtGui import QPixmap
from qfluentwidgets import MSFluentWindow, NavigationItemPosition, FluentIcon as FIF
from src.views.village_view import VillageWidget
from src.views.household_management_view import HouseholdManagementWidget
from src.views.settings_view import SettingsView
from src.views.user_role_management_view import UserRoleManagementView
from src.services.auth_service import AuthService
from src.constants import PERM_VILLAGE_MANAGE, PERM_HOUSEHOLD_MANAGE, PERM_HOUSEHOLD_VIEW, PERM_MEMBER_MANAGE, PERM_MEMBER_VIEW

class MainView(MSFluentWindow):
    logout = pyqtSignal()

    def __init__(self, user, parent=None):
        super().__init__(parent)
        self.user = user
        self.setWindowTitle('天主教教籍管理系统')
        self.resize(1200, 600)
        self.welcome_image_label = None
        self.init_navigation()

    def init_navigation(self):
        # 欢迎页面
        welcome_page = QWidget(self)
        welcome_layout = QVBoxLayout(welcome_page)
        welcome_label = QLabel(f'欢迎回来，{self.user.username}！')
        welcome_label.setStyleSheet('font-size: 20px; font-weight: bold;')
        welcome_label.setAlignment(Qt.AlignCenter)
        
        # 添加图片组件
        self.welcome_image_label = QLabel(welcome_page)
        self.welcome_image_label.setAlignment(Qt.AlignCenter)
        welcome_layout.addWidget(self.welcome_image_label)
        welcome_layout.addWidget(welcome_label)
        
        # 加载图片
        self.load_welcome_image()
        
        welcome_page.setObjectName('welcome')

        # 添加欢迎页面
        self.addSubInterface(welcome_page, FIF.HOME, '主页')

        # 堂区管理（超级管理员）
        if AuthService.check_permission(self.user, PERM_VILLAGE_MANAGE):
            village_page = VillageWidget(self)
            village_page.setObjectName('village')
            self.addSubInterface(village_page, FIF.MARKET, '堂区管理')

        # 家庭管理（有家庭管理或查看权限的用户）
        if AuthService.check_permission(self.user, PERM_HOUSEHOLD_MANAGE) or \
           AuthService.check_permission(self.user, PERM_HOUSEHOLD_VIEW):
            household_management_page = HouseholdManagementWidget(self.user, self)
            household_management_page.setObjectName('household_management')
            self.addSubInterface(household_management_page, FIF.IOT, '家庭管理')

        # 搜索功能（有家庭或成员查看/管理权限的用户）
        if (AuthService.check_permission(self.user, PERM_HOUSEHOLD_VIEW) or
            AuthService.check_permission(self.user, PERM_HOUSEHOLD_MANAGE) or
            AuthService.check_permission(self.user, PERM_MEMBER_VIEW) or
            AuthService.check_permission(self.user, PERM_MEMBER_MANAGE)):
            from src.views.search_view import SearchView
            search_page = SearchView(self.user, self)
            search_page.setObjectName('search')
            self.addSubInterface(search_page, FIF.SEARCH, '搜索')

        # 用户角色管理（所有用户都能访问，但内容不同）
        user_role_page = UserRoleManagementView(self.user, self)
        user_role_page.setObjectName('user_role')
        self.addSubInterface(user_role_page, FIF.PEOPLE, '用户角色管理')

        # 系统设置（超级管理员）
        if AuthService.check_permission(self.user, 'user_manage') or AuthService.check_permission(self.user, 'role_manage'):
            # 创建系统设置页面
            settings_page = SettingsView(self)
            settings_page.setObjectName('settings')
            self.addSubInterface(settings_page, FIF.SETTING, '系统设置')
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

    def load_welcome_image(self):
        # 加载欢迎图片
        image_path = 'static/welcome_image.jpg'
        pixmap = QPixmap(image_path)
        if not pixmap.isNull():
            # 缩放到窗口大小的80%
            window_size = self.size()
            scaled_width = int(window_size.width() * 0.9)
            scaled_height = int(window_size.height() * 0.9)
            scaled_pixmap = pixmap.scaled(scaled_width, scaled_height, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.welcome_image_label.setPixmap(scaled_pixmap)

    def resizeEvent(self, event):
        # 窗口大小变化时，重新缩放图片
        super().resizeEvent(event)
        if self.welcome_image_label:
            self.load_welcome_image()

    def handle_logout(self):
        # 退出登录，发射信号
        self.logout.emit()
        self.close()