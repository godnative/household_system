# -*- coding: utf-8 -*-
"""
搜索界面模块
提供家庭和成员的搜索功能
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidgetItem,
    QLabel, QScrollArea, QTextEdit, QStackedWidget, QLineEdit
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QTextDocument
from PyQt5.QtPrintSupport import QPrintDialog, QPrinter
from functools import partial

from qfluentwidgets import (
    PrimaryPushButton, PushButton, TableWidget, InfoBar,
    InfoBarPosition, Flyout, FlyoutView, TabBar, TabCloseButtonDisplayMode, LineEdit
)

from src.models import SessionLocal, Household, Member
from src.services.search_service import SearchService
from src.services.member_service import MemberService
from src.services.auth_service import AuthService
from src.views.member_excel_renderer import get_member_excel_html
from src.views.household_excel_renderer import get_household_excel_html
from src.constants import PERM_MEMBER_MANAGE


class SearchView(QWidget):
    """搜索视图类"""

    def __init__(self, user, parent=None):
        super().__init__(parent)
        self.user = user  # 保存用户对象
        self.current_household_id = None  # 当前选中的家庭 ID
        self.householdlayoutratio = 42  # 左右布局比例
        self.memberlayoutratio = 58
        self.init_ui()

    def init_ui(self):
        """初始化 UI"""
        # 最外层垂直布局
        main_layout = QVBoxLayout(self)

        # 顶部搜索区
        search_layout = QHBoxLayout()

        # 家庭搜索框
        search_layout.addWidget(QLabel('家庭搜索:'))
        self.household_search_input = LineEdit()
        self.household_search_input.setPlaceholderText('输入户主姓名、电话、地址等')
        self.household_search_input.returnPressed.connect(self.on_search_clicked)
        search_layout.addWidget(self.household_search_input)

        # 成员搜索框
        search_layout.addWidget(QLabel('成员搜索:'))
        self.member_search_input = LineEdit()
        self.member_search_input.setPlaceholderText('输入姓名、圣名、教友编号等')
        self.member_search_input.returnPressed.connect(self.on_search_clicked)
        search_layout.addWidget(self.member_search_input)

        # 搜索按钮
        self.search_btn = PrimaryPushButton('搜索')
        self.search_btn.clicked.connect(self.on_search_clicked)
        search_layout.addWidget(self.search_btn)

        # 重置按钮
        self.reset_btn = PushButton('重置')
        self.reset_btn.clicked.connect(self.on_reset_clicked)
        search_layout.addWidget(self.reset_btn)

        main_layout.addLayout(search_layout)

        # 中间内容区（左右布局）
        content_layout = QHBoxLayout()

        # 左侧家庭列表 (42%)
        left_layout = self._create_household_area()
        content_layout.addLayout(left_layout, self.householdlayoutratio)

        # 右侧成员详情 (58%)
        right_layout = self._create_member_area()
        content_layout.addLayout(right_layout, self.memberlayoutratio)

        main_layout.addLayout(content_layout)

    def _create_household_area(self):
        """创建左侧家庭列表区域"""
        left_layout = QVBoxLayout()

        # 标题栏
        household_title_layout = QHBoxLayout()
        household_title = QLabel('搜索结果')
        household_title.setStyleSheet('font-size: 16px; font-weight: bold;')
        household_title_layout.addWidget(household_title)

        self.refresh_household_btn = PushButton('刷新')
        self.refresh_household_btn.clicked.connect(self.on_refresh_household_clicked)
        household_title_layout.addWidget(self.refresh_household_btn)

        left_layout.addLayout(household_title_layout)

        # 家庭表格
        self.household_table = TableWidget()
        self.household_table.setBorderVisible(True)
        self.household_table.setBorderRadius(8)
        self.household_table.setWordWrap(False)
        self.household_table.setColumnCount(3)
        self.household_table.setHorizontalHeaderLabels(['ID', '堂区 - 户主', '操作'])
        self.household_table.verticalHeader().hide()
        self.household_table.verticalHeader().setDefaultSectionSize(60)
        self.household_table.itemClicked.connect(self.on_household_clicked)
        left_layout.addWidget(self.household_table)

        return left_layout

    def _create_member_area(self):
        """创建右侧成员详情区域"""
        right_layout = QVBoxLayout()

        # 标题栏
        member_title_layout = QHBoxLayout()
        member_title = QLabel('成员详情')
        member_title.setStyleSheet('font-size: 16px; font-weight: bold;')
        member_title_layout.addWidget(member_title)

        self.refresh_member_btn = PushButton('刷新')
        self.refresh_member_btn.clicked.connect(self.on_refresh_member_clicked)
        member_title_layout.addWidget(self.refresh_member_btn)

        right_layout.addLayout(member_title_layout)

        # 成员标签栏
        self.tab_bar = TabBar(self)
        self.tab_bar.setMovable(True)
        self.tab_bar.setTabMaximumWidth(220)
        self.tab_bar.setTabShadowEnabled(False)
        self.tab_bar.setScrollable(True)
        self.tab_bar.setCloseButtonDisplayMode(TabCloseButtonDisplayMode.NEVER)  # 搜索界面不支持删除
        self.tab_bar.currentChanged.connect(self.on_tab_changed)
        right_layout.addWidget(self.tab_bar)

        # 标签内容堆叠窗口
        self.stacked_widget = QStackedWidget(self)
        right_layout.addWidget(self.stacked_widget)

        return right_layout

    def on_search_clicked(self):
        """搜索按钮点击事件"""
        household_keyword = self.household_search_input.text().strip()
        member_keyword = self.member_search_input.text().strip()

        # 两个搜索框都为空
        if not household_keyword and not member_keyword:
            InfoBar.warning(
                title='提示',
                content='请输入搜索关键词',
                parent=self,
                position=InfoBarPosition.TOP
            )
            return

        # 家庭搜索优先
        if household_keyword:
            self.search_households(household_keyword)
        elif member_keyword:
            self.search_members(member_keyword)

    def search_households(self, keyword):
        """搜索家庭"""
        db = SessionLocal()
        try:
            households = SearchService.search_households(db, keyword, self.user)
            self.load_household_table(households)
            self.clear_member_area()

            if not households:
                InfoBar.info(
                    title='搜索结果',
                    content='未找到匹配的家庭',
                    parent=self,
                    position=InfoBarPosition.TOP
                )
            else:
                InfoBar.success(
                    title='搜索成功',
                    content=f'找到 {len(households)} 个匹配的家庭',
                    parent=self,
                    position=InfoBarPosition.TOP,
                    duration=2000
                )
        except Exception as e:
            InfoBar.error(
                title='搜索失败',
                content=str(e),
                parent=self,
                position=InfoBarPosition.TOP
            )
        finally:
            db.close()

    def search_members(self, keyword):
        """搜索成员"""
        db = SessionLocal()
        try:
            households = SearchService.search_members(db, keyword, self.user)
            self.load_household_table(households)
            self.clear_member_area()

            if not households:
                InfoBar.info(
                    title='搜索结果',
                    content='未找到匹配的成员',
                    parent=self,
                    position=InfoBarPosition.TOP
                )
            else:
                InfoBar.success(
                    title='搜索成功',
                    content=f'找到包含匹配成员的 {len(households)} 个家庭',
                    parent=self,
                    position=InfoBarPosition.TOP,
                    duration=2000
                )
        except Exception as e:
            InfoBar.error(
                title='搜索失败',
                content=str(e),
                parent=self,
                position=InfoBarPosition.TOP
            )
        finally:
            db.close()

    def load_household_table(self, households):
        """填充家庭表格"""
        self.household_table.clearContents()
        self.household_table.setRowCount(len(households))

        for row, household in enumerate(households):
            # 列 0: ID
            self.household_table.setItem(row, 0, QTableWidgetItem(str(household.id)))

            # 列 1: 堂区 - 户主
            village_name = household.village.name if household.village else '未知'
            display_text = f"{village_name} - {household.head_of_household if household.head_of_household else '无'}"
            self.household_table.setItem(row, 1, QTableWidgetItem(display_text))

            # 列 2: 操作按钮（查看、打印）
            btn_layout = QHBoxLayout()
            view_btn = PushButton('查看')
            print_btn = PushButton('打印')

            view_btn.clicked.connect(lambda _, h=household: self.view_household(h))
            print_btn.clicked.connect(lambda _, h=household: self.print_household(h))

            btn_widget = QWidget()
            btn_widget.setLayout(btn_layout)
            btn_layout.addWidget(view_btn)
            btn_layout.addWidget(print_btn)

            self.household_table.setCellWidget(row, 2, btn_widget)

        # 调整列宽
        self.household_table.resizeColumnsToContents()

    def on_household_clicked(self, item):
        """家庭点击事件"""
        row = self.household_table.row(item)
        household_id = int(self.household_table.item(row, 0).text())
        self.current_household_id = household_id
        self.load_members(household_id)

    def load_members(self, household_id=None):
        """加载成员数据（复用 household_management_view.py 逻辑）"""
        if not household_id:
            return

        # 清空成员标签
        self.clear_member_area()

        # 加载成员数据
        db = SessionLocal()
        try:
            members = MemberService.get_all_members(db, household_id=household_id)
            for member in members:
                # 创建标签
                tab_item = self.tab_bar.addTab(str(member.id), member.name)

                # 创建标签内容页面
                member_widget = QWidget()
                main_layout = QVBoxLayout(member_widget)

                # 创建滚动区域
                scroll_area = QScrollArea()
                scroll_content = QWidget()
                scroll_layout = QVBoxLayout(scroll_content)

                # 使用 QTextEdit 显示 HTML 表格
                text_edit = QTextEdit()
                text_edit.setHtml(get_member_excel_html(member))
                text_edit.setMinimumHeight(500)
                text_edit.setReadOnly(True)  # 搜索界面只读
                scroll_layout.addWidget(text_edit)

                # 搜索界面不添加"修改成员信息"按钮（只读界面）
                scroll_layout.addStretch()

                scroll_area.setWidget(scroll_content)
                scroll_area.setWidgetResizable(True)
                main_layout.addWidget(scroll_area)

                # 添加到堆叠窗口
                self.stacked_widget.addWidget(member_widget)

            # 默认选中第一个标签
            if members:
                self.tab_bar.setCurrentIndex(0)
        finally:
            db.close()

    def on_tab_changed(self, index):
        """标签切换事件"""
        if index >= 0:
            self.stacked_widget.setCurrentIndex(index)

    def view_household(self, household):
        """查看家庭详细信息（复用 household_management_view.py 逻辑）"""
        view = FlyoutView(
            title='家庭详细信息',
            content=f'家庭户号: {household.id}\n片号: {household.plot_number}\n堂区: {household.village.name if household.village else ""}\n家庭住址: {household.address if household.address else "无"}\n电话: {household.phone if household.phone else "无"}\n户主: {household.head_of_household if household.head_of_household else "无"}',
            isClosable=True
        )

        # 显示视图
        w = Flyout.make(view, self.sender(), self)
        view.closed.connect(w.close)

    def print_household(self, household):
        """打印家庭信息（复用 household_management_view.py 逻辑）"""
        db = SessionLocal()
        try:
            # 获取家庭的堂区信息
            village = household.village

            # 获取家庭所有成员
            members = MemberService.get_all_members(db, household_id=household.id)

            # 创建打印机对象
            printer = QPrinter(QPrinter.HighResolution)
            printer.setPageSize(QPrinter.A4)

            dialog = QPrintDialog(printer, self)
            if dialog.exec_() == QPrintDialog.Accepted:
                document = QTextDocument()

                household_html = get_household_excel_html(household, village, for_print=True)

                page_break = '<br/><br/><div style="page-break-after: always;">&nbsp;</div><br/><br/>'

                all_html = household_html
                for i, member in enumerate(members):
                    member_html = get_member_excel_html(member, for_print=True)
                    all_html += page_break + member_html

                document.setHtml(all_html)
                document.print_(printer)

                InfoBar.success(
                    title='打印成功',
                    content=f'已发送打印任务：家庭 {household.id} 及 {len(members)} 位成员',
                    parent=self,
                    position=InfoBarPosition.TOP
                )
        except Exception as e:
            InfoBar.error(
                title='打印失败',
                content=f'打印时发生错误: {str(e)}',
                parent=self,
                position=InfoBarPosition.TOP
            )
        finally:
            db.close()

    def on_reset_clicked(self):
        """重置按钮点击事件"""
        self.household_search_input.clear()
        self.member_search_input.clear()
        self.household_table.clearContents()
        self.household_table.setRowCount(0)
        self.clear_member_area()

    def on_refresh_household_clicked(self):
        """刷新家庭列表"""
        # 重新执行上一次搜索
        household_keyword = self.household_search_input.text().strip()
        member_keyword = self.member_search_input.text().strip()

        if household_keyword:
            self.search_households(household_keyword)
        elif member_keyword:
            self.search_members(member_keyword)

    def on_refresh_member_clicked(self):
        """刷新成员列表"""
        if self.current_household_id:
            self.load_members(self.current_household_id)

    def clear_member_area(self):
        """清空成员区域"""
        # 清空所有 Tab
        while self.tab_bar.count() > 0:
            self.tab_bar.removeTab(0)

        # 清空所有详情页
        while self.stacked_widget.count() > 0:
            widget = self.stacked_widget.widget(0)
            self.stacked_widget.removeWidget(widget)
            widget.deleteLater()

        # 清空当前家庭 ID
        self.current_household_id = None
