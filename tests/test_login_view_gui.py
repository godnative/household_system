# -*- coding: utf-8 -*-
"""
登录界面集成测试
"""

import os
import sys

import pytest

pytestmark = pytest.mark.gui

HAS_DISPLAY = 'DISPLAY' in os.environ or sys.platform == 'win32'
skip_no_display = pytest.mark.skipif(
    not HAS_DISPLAY,
    reason="需要 X11 显示环境（WSL2 中跳过）"
)


@pytest.fixture
def app():
    """创建 QApplication 实例"""
    from PyQt5.QtWidgets import QApplication

    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    yield app


@skip_no_display
def test_login_view_initialization(app):
    """测试登录窗口可正常创建"""
    try:
        from src.views.login_view import LoginView
    except ModuleNotFoundError as exc:
        pytest.skip(f"缺少 GUI 依赖: {exc.name}")

    login_window = LoginView()
    try:
        assert login_window is not None
        assert login_window.ui is not None
        assert login_window.ui.usernameLineEdit is not None
        assert login_window.ui.passwordLineEdit is not None
        assert login_window.ui.rememberCheckBox is not None
        assert login_window.ui.loginButton is not None
    finally:
        login_window.close()
        login_window.deleteLater()
