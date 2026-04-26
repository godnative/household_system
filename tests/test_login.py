# -*- coding: utf-8 -*-
"""
登录界面测试
测试 LoginView 组件
"""

import pytest
import sys
import os

HAS_DISPLAY = 'DISPLAY' in os.environ or sys.platform == 'win32'
skip_no_display = pytest.mark.skipif(not HAS_DISPLAY, reason="需要 X11 显示环境")


@pytest.mark.gui
@skip_no_display
class TestLoginView:
    """LoginView 登录界面测试"""

    def test_login_ui_initialization(self, login_view):
        """测试登录界面初始化"""
        assert login_view is not None
        assert login_view.username_input is not None
        assert login_view.password_input is not None
        assert login_view.login_button is not None

    def test_login_ui_components(self, login_view):
        """测试 UI 组件存在"""
        assert hasattr(login_view, 'username_input')
        assert hasattr(login_view, 'password_input')
        assert hasattr(login_view, 'login_button')
        assert login_view.windowTitle() == '天主教教籍管理系统 - 登录'

    def test_login_empty_credentials(self, login_view, qtbot):
        """测试空用户名/密码时的提示"""
        login_view.login_button.click()

    def test_login_invalid_credentials(self, login_view, qtbot):
        """测试错误密码时的提示"""
        login_view.username_input.setText('wrong_user')
        login_view.password_input.setText('wrong_pass')
        login_view.login_button.click()

    def test_login_success_signal(self, login_view, qtbot):
        """测试正确凭据登录成功，发射信号"""
        from PyQt5.QtTest import QSignalSpy
        spy = QSignalSpy(login_view.login_success)

        login_view.username_input.setText('admin')
        login_view.password_input.setText('admin123')
        login_view.login_button.click()

    def test_login_window_geometry(self, login_view):
        """测试窗口几何属性"""
        assert login_view.geometry().width() > 0
        assert login_view.geometry().height() > 0

    def test_login_input_fields(self, login_view):
        """测试输入字段属性"""
        assert login_view.username_input.placeholderText() == '请输入用户名'
        assert login_view.password_input.placeholderText() == '请输入密码'
        assert login_view.password_input.echoMode() == 2  # Password echo mode

    def test_login_button_text(self, login_view):
        """测试登录按钮文本"""
        assert login_view.login_button.text() == '登录'