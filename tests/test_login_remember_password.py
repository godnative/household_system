# -*- coding: utf-8 -*-
"""
登录界面记住密码功能测试
"""

import os
import sys
import types

import pytest
from PyQt5.QtWidgets import QApplication, QCheckBox, QLineEdit, QPushButton, QWidget

pytestmark = pytest.mark.unit


class DummyFramelessWindow(QWidget):
    """测试用无边框窗口替身"""

    def centerWindow(self):
        pass


class DummyUiLoginForm:
    """测试用登录 UI 替身，仅提供记住密码相关控件"""

    def setupUi(self, form):
        self.backgroundLabel = types.SimpleNamespace(
            pixmap=lambda: types.SimpleNamespace(isNull=lambda: True),
            setPixmap=lambda *args, **kwargs: None,
            setScaledContents=lambda *args, **kwargs: None,
            size=lambda: None,
        )
        self.logoLabel = types.SimpleNamespace(
            setPixmap=lambda *args, **kwargs: None,
            setStyleSheet=lambda *args, **kwargs: None,
            setText=lambda *args, **kwargs: None,
        )
        self.usernameLineEdit = QLineEdit(form)
        self.passwordLineEdit = QLineEdit(form)
        self.rememberCheckBox = QCheckBox(form)
        self.loginButton = QPushButton(form)


sys.modules.setdefault(
    'qframelesswindow',
    types.SimpleNamespace(FramelessWindow=DummyFramelessWindow)
)
sys.modules.setdefault(
    'qfluentwidgets',
    types.SimpleNamespace(setThemeColor=lambda *args, **kwargs: None)
)
sys.modules.setdefault(
    'src.views.login_ui',
    types.SimpleNamespace(Ui_LoginForm=DummyUiLoginForm)
)

from src.views.login_view import LoginView


@pytest.fixture
def app():
    """创建 QApplication 实例"""
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    yield app


@pytest.fixture
def login_view(app, tmp_path, monkeypatch):
    """创建隔离配置目录的 LoginView 实例"""
    monkeypatch.chdir(tmp_path)
    view = LoginView()
    yield view
    view.close()
    view.deleteLater()


def test_save_last_login_info_persists_encoded_password(login_view):
    """测试保存登录信息时会写入用户名和 Base64 编码密码"""
    login_view.saveLastLoginInfo('tester', 'secret123')

    config_file = os.path.join('config', 'login_info.txt')
    assert os.path.exists(config_file)

    with open(config_file, 'r', encoding='utf-8') as f:
        lines = [line.strip() for line in f.readlines()]

    assert lines[0] == 'tester'
    assert lines[1] == 'c2VjcmV0MTIz'


def test_load_last_login_info_restores_fields_and_checkbox(login_view):
    """测试加载登录信息时会恢复用户名、密码和勾选状态"""
    login_view.saveLastLoginInfo('admin', 'admin123')

    login_view.ui.usernameLineEdit.clear()
    login_view.ui.passwordLineEdit.clear()
    login_view.ui.rememberCheckBox.setChecked(False)

    login_view.loadLastLoginInfo()

    assert login_view.ui.usernameLineEdit.text() == 'admin'
    assert login_view.ui.passwordLineEdit.text() == 'admin123'
    assert login_view.ui.rememberCheckBox.isChecked() is True


def test_clear_last_login_info_removes_saved_file(login_view):
    """测试取消记住密码后会删除保存的登录信息"""
    login_view.saveLastLoginInfo('tester', 'secret123')
    config_file = os.path.join('config', 'login_info.txt')

    assert os.path.exists(config_file)

    login_view.clearLastLoginInfo()

    assert not os.path.exists(config_file)
