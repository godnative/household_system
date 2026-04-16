# -*- coding: utf-8 -*-
"""
登录界面视图
使用 PyQt-Fluent-Widgets 实现的现代化登录界面
保留原有登录逻辑和功能
"""

import os
import base64
from PyQt5.QtWidgets import QWidget, QMessageBox
from PyQt5.QtCore import Qt, pyqtSignal, QSize
from PyQt5.QtGui import QPixmap
from qframelesswindow import FramelessWindow
from qfluentwidgets import setThemeColor
from src.views.login_ui import Ui_LoginForm
from src.services.auth_service import AuthService
from src.models import SessionLocal


class LoginView(FramelessWindow):
    """登录界面"""
    login_success = pyqtSignal(object)  # 登录成功信号，传递 User 对象

    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_LoginForm()
        self.ui.setupUi(self)

        # 设置主题色
        setThemeColor('#667eea')

        # 设置窗口属性
        self.setWindowTitle('天主教教籍管理系统')
        self.resize(1000, 650)
        self.centerWindow()

        # 加载背景图片（如果存在）
        self.loadBackgroundImage()

        # 加载Logo图片（如果存在）
        self.loadLogoImage()

        # 连接信号槽
        self.connectSignals()

        # 加载上次登录信息
        self.loadLastLoginInfo()

        # 设置焦点到用户名输入框
        self.ui.usernameLineEdit.setFocus()

    def centerWindow(self):
        """将窗口居中显示"""
        screen = self.screen().availableGeometry()
        size = self.geometry()
        self.move(
            (screen.width() - size.width()) // 2,
            (screen.height() - size.height()) // 2
        )

    def loadBackgroundImage(self):
        """加载背景图片"""
        # 尝试加载背景图片
        bg_paths = [
            'resource/images/login_background.jpg',
            'resource/images/background.jpg',
            'static/login_background.jpg',
        ]

        for path in bg_paths:
            if os.path.exists(path):
                pixmap = QPixmap(path)
                if not pixmap.isNull():
                    # 缩放图片以适应标签大小，保持宽高比
                    self.ui.backgroundLabel.setPixmap(pixmap)
                    self.ui.backgroundLabel.setScaledContents(False)
                    break

    def loadLogoImage(self):
        """加载Logo图片"""
        # 尝试加载Logo图片
        logo_paths = [
            'resource/images/logo.png',
            'static/logo.png',
        ]

        for path in logo_paths:
            if os.path.exists(path):
                pixmap = QPixmap(path)
                if not pixmap.isNull():
                    scaled_pixmap = pixmap.scaled(
                        100, 100,
                        Qt.KeepAspectRatio,
                        Qt.SmoothTransformation
                    )
                    self.ui.logoLabel.setPixmap(scaled_pixmap)
                    self.ui.logoLabel.setStyleSheet("")  # 清除默认样式
                    self.ui.logoLabel.setText("")
                    break

    def resizeEvent(self, event):
        """窗口大小改变事件"""
        super().resizeEvent(event)
        # 如果背景标签有图片，重新缩放
        if not self.ui.backgroundLabel.pixmap().isNull():
            # 保持原图比例，填充整个标签
            pixmap = self.ui.backgroundLabel.pixmap()
            scaled_pixmap = pixmap.scaled(
                self.ui.backgroundLabel.size(),
                Qt.KeepAspectRatioByExpanding,
                Qt.SmoothTransformation
            )
            self.ui.backgroundLabel.setPixmap(scaled_pixmap)

    def connectSignals(self):
        """连接信号槽"""
        # 登录按钮点击事件
        self.ui.loginButton.clicked.connect(self.handleLogin)

        # 回车键登录
        self.ui.passwordLineEdit.returnPressed.connect(self.handleLogin)
        self.ui.usernameLineEdit.returnPressed.connect(
            lambda: self.ui.passwordLineEdit.setFocus()
        )

    def handleLogin(self):
        """处理登录事件"""
        username = self.ui.usernameLineEdit.text().strip()
        password = self.ui.passwordLineEdit.text().strip()

        # 验证输入
        if not username or not password:
            QMessageBox.warning(self, '提示', '请输入用户名和密码')
            return

        # 禁用登录按钮，防止重复点击
        self.ui.loginButton.setEnabled(False)
        self.ui.loginButton.setText('登录中...')

        # 验证用户
        db = SessionLocal()
        try:
            user = AuthService.authenticate_user(db, username, password)
            if user:
                # 如果勾选了"记住密码"，保存登录信息
                if self.ui.rememberCheckBox.isChecked():
                    self.saveLastLoginInfo(username, password)
                else:
                    # 否则清除保存的登录信息
                    self.clearLastLoginInfo()

                # 登录成功，发射信号
                self.login_success.emit(user)
                self.close()
            else:
                QMessageBox.warning(self, '登录失败', '用户名或密码错误')
                self.ui.loginButton.setEnabled(True)
                self.ui.loginButton.setText('登录')
        except Exception as e:
            QMessageBox.critical(self, '错误', f'登录失败: {str(e)}')
            self.ui.loginButton.setEnabled(True)
            self.ui.loginButton.setText('登录')
        finally:
            db.close()

    def saveLastLoginInfo(self, username, password):
        """保存上次登录信息"""
        try:
            # 使用 base64 简单编码密码（不是加密，只是混淆）
            encoded_password = base64.b64encode(password.encode()).decode()

            # 保存到配置文件
            config_dir = 'config'
            if not os.path.exists(config_dir):
                os.makedirs(config_dir)

            config_file = os.path.join(config_dir, 'login_info.txt')
            with open(config_file, 'w', encoding='utf-8') as f:
                f.write(f"{username}\n{encoded_password}")
        except Exception as e:
            print(f"保存登录信息失败: {str(e)}")

    def loadLastLoginInfo(self):
        """加载上次登录信息"""
        try:
            config_file = os.path.join('config', 'login_info.txt')
            if os.path.exists(config_file):
                with open(config_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    if len(lines) >= 2:
                        username = lines[0].strip()
                        encoded_password = lines[1].strip()

                        # 解码密码
                        password = base64.b64decode(encoded_password).decode()

                        # 填充到输入框
                        self.ui.usernameLineEdit.setText(username)
                        self.ui.passwordLineEdit.setText(password)
                        self.ui.rememberCheckBox.setChecked(True)
        except Exception as e:
            print(f"加载登录信息失败: {str(e)}")

    def clearLastLoginInfo(self):
        """清除保存的登录信息"""
        try:
            config_file = os.path.join('config', 'login_info.txt')
            if os.path.exists(config_file):
                os.remove(config_file)
        except Exception as e:
            print(f"清除登录信息失败: {str(e)}")
