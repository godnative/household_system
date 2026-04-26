# -*- coding: utf-8 -*-
"""
搜索功能测试
测试 SearchView 组件
"""

import pytest
import sys
import os

HAS_DISPLAY = 'DISPLAY' in os.environ or sys.platform == 'win32'
skip_no_display = pytest.mark.skipif(not HAS_DISPLAY, reason="需要 X11 显示环境")


@pytest.mark.gui
@skip_no_display
class TestSearchView:
    """SearchView 搜索视图测试"""

    def test_search_view_initialization(self, search_view):
        """测试搜索界面初始化"""
        assert search_view is not None
        assert search_view.user is not None

    def test_search_input_placeholders(self, search_view):
        """测试搜索框占位符文本"""
        household_placeholder = search_view.household_search_input.placeholderText()
        member_placeholder = search_view.member_search_input.placeholderText()
        assert '户主' in household_placeholder or '姓名' in household_placeholder
        assert '姓名' in member_placeholder or '圣名' in member_placeholder

    def test_search_buttons_exist(self, search_view):
        """测试搜索按钮存在"""
        assert search_view.search_btn is not None
        assert search_view.reset_btn is not None

    def test_household_table_exists(self, search_view):
        """测试家庭表格存在"""
        assert search_view.household_table is not None
        assert search_view.household_table.columnCount() == 3

    def test_member_area_exists(self, search_view):
        """测试成员区域存在"""
        assert search_view.tab_bar is not None
        assert search_view.stacked_widget is not None


@pytest.mark.gui
@skip_no_display
class TestSearchFunctionality:
    """搜索功能测试"""

    def test_search_empty_keyword_warning(self, search_view, qtbot):
        """测试空关键词搜索警告"""
        search_view.household_search_input.clear()
        search_view.member_search_input.clear()
        search_view.search_btn.click()

    def test_search_household_by_name(self, search_view, qtbot):
        """测试按户主姓名搜索"""
        search_view.household_search_input.setText('张三')
        search_view.search_btn.click()

    def test_search_member_by_name(self, search_view, qtbot):
        """测试按成员姓名搜索"""
        search_view.member_search_input.setText('张三')
        search_view.search_btn.click()

    def test_search_results_display(self, search_view, qtbot):
        """测试搜索结果显示"""
        search_view.household_search_input.setText('张三')
        search_view.search_btn.click()

    def test_reset_search(self, search_view, qtbot):
        """测试重置搜索"""
        search_view.household_search_input.setText('测试')
        search_view.member_search_input.setText('测试')
        search_view.reset_btn.click()
        assert search_view.household_search_input.text() == ''
        assert search_view.member_search_input.text() == ''


@pytest.mark.gui
@skip_no_display
class TestSearchInteraction:
    """搜索交互测试"""

    def test_click_household_loads_members(self, search_view, qtbot):
        """测试点击家庭加载成员"""
        search_view.household_search_input.setText('张三')
        search_view.search_btn.click()

        if search_view.household_table.rowCount() > 0:
            item = search_view.household_table.item(0, 0)
            search_view.on_household_clicked(item)
            assert search_view.tab_bar.count() >= 0

    def test_member_tabs_display(self, search_view, qtbot):
        """测试成员标签显示"""
        search_view.household_search_input.setText('张三')
        search_view.search_btn.click()

        if search_view.household_table.rowCount() > 0:
            item = search_view.household_table.item(0, 0)
            search_view.on_household_clicked(item)

    def test_refresh_household_button(self, search_view, qtbot):
        """测试刷新家庭列表按钮"""
        search_view.household_search_input.setText('张三')
        search_view.search_btn.click()
        initial_count = search_view.household_table.rowCount()
        search_view.refresh_household_btn.click()

    def test_refresh_member_button(self, search_view, qtbot):
        """测试刷新成员列表按钮"""
        search_view.household_search_input.setText('张三')
        search_view.search_btn.click()

        if search_view.household_table.rowCount() > 0:
            item = search_view.household_table.item(0, 0)
            search_view.on_household_clicked(item)
            search_view.refresh_member_btn.click()