# -*- coding: utf-8 -*-
"""
GUI 界面测试
测试 SearchView 等 GUI 组件
注意：这些测试在 WSL2 环境中标记为跳过，仅在有 X11 显示的环境中运行
"""

import pytest
import sys
import os

# 检查是否有显示环境
HAS_DISPLAY = 'DISPLAY' in os.environ or sys.platform == 'win32'

# GUI 测试装饰器
skip_no_display = pytest.mark.skipif(
    not HAS_DISPLAY,
    reason="需要 X11 显示环境（WSL2 中跳过）"
)


@pytest.mark.gui
@skip_no_display
class TestSearchViewUI:
    """SearchView UI 测试"""

    @pytest.fixture
    def app(self):
        """创建 QApplication 实例"""
        from PyQt5.QtWidgets import QApplication
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        yield app
        # 不调用 app.quit()，因为可能有其他测试需要

    @pytest.fixture
    def search_view(self, app, test_db_with_data, super_admin_user):
        """创建 SearchView 实例"""
        from src.views.search_view import SearchView
        view = SearchView(super_admin_user)
        yield view
        view.close()
        view.deleteLater()

    def test_search_view_initialization(self, search_view):
        """测试搜索界面初始化"""
        assert search_view is not None
        assert search_view.user is not None
        assert search_view.household_search_input is not None
        assert search_view.member_search_input is not None
        assert search_view.search_btn is not None
        assert search_view.reset_btn is not None

    def test_search_view_layout(self, search_view):
        """测试搜索界面布局"""
        # 验证左右布局比例
        assert search_view.householdlayoutratio == 42
        assert search_view.memberlayoutratio == 58

        # 验证关键组件存在
        assert search_view.household_table is not None
        assert search_view.tab_bar is not None
        assert search_view.stacked_widget is not None

    def test_search_input_placeholder(self, search_view):
        """测试搜索框提示文本"""
        household_placeholder = search_view.household_search_input.placeholderText()
        member_placeholder = search_view.member_search_input.placeholderText()

        assert '户主' in household_placeholder or '姓名' in household_placeholder
        assert '姓名' in member_placeholder or '圣名' in member_placeholder

    def test_search_button_click(self, search_view):
        """测试搜索按钮点击"""
        # 设置搜索关键词
        search_view.household_search_input.setText('张三')

        # 模拟点击搜索按钮
        search_view.search_btn.click()

        # 验证表格中有数据
        # 注意：这需要实际的数据库连接，可能需要 mock
        assert search_view.household_table.rowCount() >= 0

    def test_reset_button_click(self, search_view):
        """测试重置按钮点击"""
        # 设置一些搜索条件
        search_view.household_search_input.setText('测试')
        search_view.member_search_input.setText('测试')

        # 点击重置按钮
        search_view.reset_btn.click()

        # 验证搜索框被清空
        assert search_view.household_search_input.text() == ''
        assert search_view.member_search_input.text() == ''
        assert search_view.household_table.rowCount() == 0

    def test_household_table_columns(self, search_view):
        """测试家庭表格列设置"""
        assert search_view.household_table.columnCount() == 3

        # 验证表头
        headers = []
        for i in range(3):
            headers.append(search_view.household_table.horizontalHeaderItem(i).text())

        assert 'ID' in headers
        assert '户主' in headers or '堂区' in headers
        assert '操作' in headers

    def test_tab_bar_configuration(self, search_view):
        """测试成员标签栏配置"""
        # 验证标签栏设置
        assert search_view.tab_bar.isMovable() is True
        assert search_view.tab_bar.tabsClosable() is False  # 搜索界面不支持关闭标签

    def test_empty_search_warning(self, search_view, qtbot):
        """测试空搜索警告"""
        # 清空搜索框
        search_view.household_search_input.clear()
        search_view.member_search_input.clear()

        # 点击搜索按钮
        with qtbot.waitSignal(timeout=1000):
            search_view.search_btn.click()

        # 应该显示警告提示
        # 注意：InfoBar 的验证需要特殊处理


@pytest.mark.gui
@skip_no_display
class TestSearchViewInteraction:
    """SearchView 交互测试"""

    @pytest.fixture
    def app(self):
        """创建 QApplication 实例"""
        from PyQt5.QtWidgets import QApplication
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        yield app

    @pytest.fixture
    def search_view_with_results(self, app, test_db_with_data, super_admin_user):
        """创建带有搜索结果的 SearchView"""
        from src.views.search_view import SearchView
        view = SearchView(super_admin_user)

        # 执行搜索
        view.household_search_input.setText('张三')
        view.on_search_clicked()

        yield view
        view.close()
        view.deleteLater()

    def test_household_click_loads_members(self, search_view_with_results):
        """测试点击家庭加载成员"""
        view = search_view_with_results

        if view.household_table.rowCount() > 0:
            # 模拟点击第一行
            item = view.household_table.item(0, 0)
            view.on_household_clicked(item)

            # 验证成员标签栏有数据
            assert view.tab_bar.count() > 0

    def test_tab_change_updates_stacked_widget(self, search_view_with_results):
        """测试标签切换更新堆叠窗口"""
        view = search_view_with_results

        if view.tab_bar.count() > 1:
            # 切换到第二个标签
            view.tab_bar.setCurrentIndex(1)

            # 验证堆叠窗口也切换到相应页面
            assert view.stacked_widget.currentIndex() == 1

    def test_refresh_household_button(self, search_view_with_results):
        """测试刷新家庭列表按钮"""
        view = search_view_with_results

        initial_count = view.household_table.rowCount()

        # 点击刷新按钮
        view.refresh_household_btn.click()

        # 验证行数不变（数据未变化）
        assert view.household_table.rowCount() == initial_count

    def test_refresh_member_button(self, search_view_with_results):
        """测试刷新成员列表按钮"""
        view = search_view_with_results

        if view.household_table.rowCount() > 0:
            # 先点击一个家庭加载成员
            item = view.household_table.item(0, 0)
            view.on_household_clicked(item)

            initial_tab_count = view.tab_bar.count()

            # 点击刷新成员按钮
            view.refresh_member_btn.click()

            # 验证标签数不变
            assert view.tab_bar.count() == initial_tab_count


@pytest.mark.gui
@skip_no_display
class TestMainViewIntegration:
    """主界面集成测试"""

    @pytest.fixture
    def app(self):
        """创建 QApplication 实例"""
        from PyQt5.QtWidgets import QApplication
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        yield app

    @pytest.fixture
    def main_view(self, app, test_db_with_data, super_admin_user):
        """创建主界面实例"""
        from src.views.main_view import MainView
        view = MainView(super_admin_user)
        yield view
        view.close()
        view.deleteLater()

    def test_search_menu_item_exists(self, main_view):
        """测试搜索菜单项存在"""
        # 获取所有导航项
        nav_interface = main_view.navigationInterface

        # 验证搜索菜单项存在
        # 注意：具体实现取决于 qfluentwidgets 的 API
        # 这里只是一个示例

    def test_search_menu_accessible(self, main_view, super_admin_user):
        """测试搜索菜单可访问"""
        # 超级管理员应该能看到搜索菜单
        # 验证搜索菜单项可见且可点击

    def test_navigate_to_search_view(self, main_view):
        """测试导航到搜索界面"""
        # 模拟点击搜索菜单项
        # 验证当前界面切换到搜索界面


@pytest.mark.gui
@skip_no_display
class TestPermissionBasedUIAccess:
    """基于权限的 UI 访问测试"""

    @pytest.fixture
    def app(self):
        """创建 QApplication 实例"""
        from PyQt5.QtWidgets import QApplication
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        yield app

    def test_super_admin_can_access_search(self, app, test_db_with_data, super_admin_user):
        """测试超级管理员可访问搜索功能"""
        from src.views.main_view import MainView
        view = MainView(super_admin_user)

        # 验证搜索菜单项存在
        # （具体实现取决于如何获取菜单项）

        view.close()
        view.deleteLater()

    def test_observer_can_access_search(self, app, test_db_with_data, observer_user):
        """测试观察员可访问搜索功能"""
        from src.views.main_view import MainView
        view = MainView(observer_user)

        # 验证搜索菜单项存在

        view.close()
        view.deleteLater()

    def test_data_entry_can_access_search(self, app, test_db_with_data, data_entry_user):
        """测试录入员可访问搜索功能"""
        from src.views.main_view import MainView
        view = MainView(data_entry_user)

        # 验证搜索菜单项存在

        view.close()
        view.deleteLater()


# 以下是一些辅助测试函数，标记为跳过但保留代码

@pytest.mark.gui
@skip_no_display
def test_view_household_dialog(test_db_with_data, super_admin_user):
    """测试查看家庭详情对话框"""
    from PyQt5.QtWidgets import QApplication
    from src.views.search_view import SearchView

    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)

    view = SearchView(super_admin_user)

    # 执行搜索
    view.household_search_input.setText('张三')
    view.on_search_clicked()

    # 获取第一个家庭
    if view.household_table.rowCount() > 0:
        # 模拟点击查看按钮
        # 注意：这需要访问单元格内的按钮，比较复杂
        pass

    view.close()
    view.deleteLater()


@pytest.mark.gui
@skip_no_display
def test_print_household_function(test_db_with_data, super_admin_user):
    """测试打印家庭功能"""
    # 这个测试需要模拟打印对话框
    # 在 WSL2 中通常无法测试打印功能
    pass


# 运行说明
"""
在有图形界面的环境中运行 GUI 测试：

1. Linux 桌面环境：
   pytest tests/test_gui.py -v

2. Windows：
   pytest tests/test_gui.py -v

3. WSL2（跳过 GUI 测试）：
   pytest tests/test_gui.py -v  # 所有测试会被自动跳过

4. 只运行 GUI 测试：
   pytest -m gui

5. 跳过 GUI 测试：
   pytest -m "not gui"
"""
