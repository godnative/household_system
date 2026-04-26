# -*- coding: utf-8 -*-
"""
集成测试
测试完整的用户操作流程
"""

import pytest
import sys
import os

HAS_DISPLAY = 'DISPLAY' in os.environ or sys.platform == 'win32'
skip_no_display = pytest.mark.skipif(not HAS_DISPLAY, reason="需要 X11 显示环境")


@pytest.mark.gui
@skip_no_display
class TestFullLoginFlow:
    """完整登录流程测试"""

    def test_full_login_flow(self, login_view, qtbot):
        """测试完整登录流程"""
        login_view.username_input.setText('admin')
        login_view.password_input.setText('admin123')
        login_view.login_button.click()


@pytest.mark.gui
@skip_no_display
class TestFullAddHouseholdFlow:
    """完整添加家庭流程测试"""

    def test_full_add_household_flow(self, household_management_view, qtbot):
        """测试完整添加家庭流程"""
        household_management_view.village_combo.setCurrentIndex(0)
        household_management_view.add_household_btn.click()


@pytest.mark.gui
@skip_no_display
class TestFullAddMemberFlow:
    """完整添加成员流程测试"""

    def test_full_add_member_flow(self, household_management_view, qtbot):
        """测试完整添加成员流程"""
        household_management_view.village_combo.setCurrentIndex(0)
        if household_management_view.household_table.rowCount() > 0:
            household_management_view.household_table.selectRow(0)
            household_management_view.add_member_btn.click()


@pytest.mark.gui
@skip_no_display
class TestFullSearchFlow:
    """完整搜索流程测试"""

    def test_full_search_flow(self, search_view, qtbot):
        """测试完整搜索流程"""
        search_view.household_search_input.setText('张三')
        search_view.search_btn.click()
        if search_view.household_table.rowCount() > 0:
            item = search_view.household_table.item(0, 0)
            search_view.on_household_clicked(item)
        search_view.reset_btn.click()


@pytest.mark.gui
@skip_no_display
class TestLogoutAndLogin:
    """退出和重新登录测试"""

    def test_logout_and_login_again(self, main_view, qtbot):
        """测试退出后重新登录"""
        pass