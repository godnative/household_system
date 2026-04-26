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


def test_login_view_has_required_components(login_view):
    """测试登录视图具有必要的组件"""
    assert login_view is not None
    assert hasattr(login_view, 'username_input')
    assert hasattr(login_view, 'password_input')
    assert hasattr(login_view, 'login_button')


def test_login_view_initial_state(login_view):
    """测试登录视图的初始状态"""
    assert login_view.username_input.text() == ''
    assert login_view.password_input.text() == ''


def test_login_view_window_properties(login_view):
    """测试登录视图的窗口属性"""
    assert login_view.windowTitle() == '天主教教籍管理系统 - 登录'
    assert login_view.geometry().width() == 400
    assert login_view.geometry().height() == 300
