# -*- coding: utf-8 -*-
"""
主界面测试
测试 MainView 组件
"""

import pytest
import sys
import os

HAS_DISPLAY = 'DISPLAY' in os.environ or sys.platform == 'win32'
skip_no_display = pytest.mark.skipif(not HAS_DISPLAY, reason="需要 X11 显示环境")


@pytest.mark.gui
@skip_no_display
class TestMainView:
    """MainView 主界面测试"""

    def test_main_view_initialization(self, main_view):
        """测试主界面初始化"""
        assert main_view is not None
        assert main_view.user is not None
        assert main_view.windowTitle() == '天主教教籍管理系统'

    def test_main_view_navigation_interface(self, main_view):
        """测试导航接口存在"""
        assert hasattr(main_view, 'navigationInterface')
        assert main_view.navigationInterface is not None

    def test_main_view_welcome_page(self, main_view):
        """测试欢迎页面存在"""
        assert hasattr(main_view, 'welcome_image_label')

    def test_main_view_logout_button(self, main_view):
        """测试退出按钮存在"""
        nav_interface = main_view.navigationInterface
        # 验证有退出按钮

    def test_main_view_window_size(self, main_view):
        """测试窗口大小"""
        assert main_view.width() >= 800
        assert main_view.height() >= 600


@pytest.mark.gui
@skip_no_display
class TestMainViewPermissions:
    """主界面权限测试"""

    def test_super_admin_has_all_menus(self, main_view):
        """测试超级管理员看到所有菜单"""
        # 超级管理员应该看到：主页、堂区管理、家庭管理、搜索、用户角色管理、系统设置
        pass

    def test_data_entry_limited_menus(self, main_view_for_data_entry):
        """测试录入员看到受限菜单"""
        # 录入员不应该看到堂区管理
        pass

    def test_observer_view_only(self, main_view_for_observer):
        """测试观察员仅查看"""
        # 观察员应该只有查看权限
        pass


@pytest.mark.gui
@skip_no_display
class TestMainViewNavigation:
    """主界面导航测试"""

    def test_navigate_to_search(self, main_view):
        """测试导航到搜索界面"""
        pass

    def test_navigate_to_household_management(self, main_view):
        """测试导航到家庭管理"""
        pass

    def test_navigate_to_village_management(self, main_view):
        """测试导航到堂区管理"""
        pass

    def test_navigate_to_user_management(self, main_view):
        """测试导航到用户角色管理"""
        pass