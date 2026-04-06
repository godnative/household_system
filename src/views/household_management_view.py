from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidgetItem, QFormLayout, QLineEdit, QLabel, QComboBox, QScrollArea, QDateEdit, QTextEdit, QStackedWidget, QGroupBox, QGridLayout
from PyQt5.QtCore import Qt
from functools import partial
from qfluentwidgets import PrimaryPushButton, PushButton, TableWidget, Dialog, InfoBar, InfoBarPosition, ComboBox, FlowLayout, ElevatedCardWidget, BodyLabel, CaptionLabel, TitleLabel, Flyout, FlyoutView, TabBar, TabCloseButtonDisplayMode
from src.services.household_service import HouseholdService
from src.services.member_service import MemberService
from src.services.village_service import VillageService
from src.models import SessionLocal, Household, Member
from src.views.member_excel_renderer import get_member_excel_html
from sqlalchemy.exc import IntegrityError



class HouseholdManagementWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        self.load_villages()
    
    def init_ui(self):
        layout = QVBoxLayout(self)

        self.householdlayoutratio = 42
        self.memberlayoutratio    = 100 - self.householdlayoutratio
        
        # 顶部村庄选择（占10%高度）
        village_layout = QHBoxLayout()
        village_label = QLabel('选择村庄:')
        self.village_combo = ComboBox()
        self.village_combo.currentIndexChanged.connect(self.on_village_changed)
        village_layout.addWidget(village_label)
        village_layout.addWidget(self.village_combo)
        village_layout.addStretch()
        layout.addLayout(village_layout)
        
        # 下方主布局（占90%高度）
        main_layout = QHBoxLayout()
        
        # 左侧家庭管理模块
        left_layout = QVBoxLayout()
        
        # 家庭管理标题和操作按钮
        household_title_layout = QHBoxLayout()
        household_title = QLabel('家庭管理')
        household_title.setStyleSheet('font-size: 16px; font-weight: bold;')
        household_title_layout.addWidget(household_title)
        
        add_household_btn = PrimaryPushButton('添加家庭')
        add_household_btn.clicked.connect(self.add_household)
        household_title_layout.addWidget(add_household_btn)
        
        refresh_household_btn = PushButton('刷新')
        refresh_household_btn.clicked.connect(self.load_households)
        household_title_layout.addWidget(refresh_household_btn)
        
        left_layout.addLayout(household_title_layout)
        
        # 家庭表格
        self.household_table = TableWidget()
        self.household_table.setBorderVisible(True)
        self.household_table.setBorderRadius(8)
        self.household_table.setWordWrap(False)
        self.household_table.setColumnCount(4)
        self.household_table.setHorizontalHeaderLabels(['ID', '家庭编号', '户主', '操作'])
        self.household_table.verticalHeader().hide()
        self.household_table.verticalHeader().setDefaultSectionSize(60)
        self.household_table.itemClicked.connect(self.on_household_clicked)
        left_layout.addWidget(self.household_table)
        
        main_layout.addLayout(left_layout, self.householdlayoutratio)
        
        # 右侧成员管理模块
        right_layout = QVBoxLayout()
        
        # 成员管理标题和操作按钮
        member_title_layout = QHBoxLayout()
        member_title = QLabel('成员管理')
        member_title.setStyleSheet('font-size: 16px; font-weight: bold;')
        member_title_layout.addWidget(member_title)
        
        self.add_member_btn = PrimaryPushButton('添加成员')
        self.add_member_btn.clicked.connect(self.add_member)
        self.add_member_btn.setEnabled(False)
        member_title_layout.addWidget(self.add_member_btn)
        
        refresh_member_btn = PushButton('刷新')
        refresh_member_btn.clicked.connect(self.load_members)
        member_title_layout.addWidget(refresh_member_btn)
        
        right_layout.addLayout(member_title_layout)
        
        # 成员标签栏
        self.tab_bar = TabBar(self)
        self.tab_bar.setMovable(True)
        self.tab_bar.setTabMaximumWidth(220)
        self.tab_bar.setTabShadowEnabled(False)
        self.tab_bar.setScrollable(True)
        self.tab_bar.setCloseButtonDisplayMode(TabCloseButtonDisplayMode.ON_HOVER)
        self.tab_bar.tabCloseRequested.connect(self.on_tab_close_requested)
        self.tab_bar.currentChanged.connect(self.on_tab_changed)
        right_layout.addWidget(self.tab_bar)
        
        # 标签内容堆叠窗口
        self.stacked_widget = QStackedWidget(self)
        right_layout.addWidget(self.stacked_widget)
        
        main_layout.addLayout(right_layout, self.memberlayoutratio)
        
        layout.addLayout(main_layout)
    
    def load_villages(self):
        """ 加载村庄数据 """
        db = SessionLocal()
        try:
            villages = VillageService.get_all_villages(db)
            self.village_combo.clear()
            for village in villages:
                self.village_combo.addItem(village.name)
                self.village_combo.setItemData(self.village_combo.count() - 1, village.id)
            if villages:
                self.on_village_changed(0)
        finally:
            db.close()
    
    def on_village_changed(self, index):
        """ 村庄选择变化时的处理 """
        village_id = self.village_combo.currentData()
        if village_id:
            self.load_households(village_id)
            self.clear_member_cards()
            self.add_member_btn.setEnabled(False)
    
    def on_household_clicked(self, item):
        """ 家庭选择变化时的处理 """
        row = self.household_table.row(item)
        household_id = int(self.household_table.item(row, 0).text())
        if household_id:
            self.load_members(household_id)
            self.add_member_btn.setEnabled(True)
    
    def on_tab_changed(self, index):
        """ 标签切换时的处理 """
        if index >= 0:
            self.stacked_widget.setCurrentIndex(index)
    
    def on_tab_close_requested(self, index):
        """ 标签关闭时的处理 """
        # 获取成员ID
        if index < len(self.tab_bar.items):
            tab_item = self.tab_bar.items[index]
            if tab_item:
                member_id = tab_item.property('member_id')
                if member_id:
                    # 确认删除
                    dialog = Dialog('确认删除', f'确定要删除成员吗？', self)
                    if dialog.exec():
                        # 删除成员
                        db = SessionLocal()
                        try:
                            if MemberService.delete_member(db, member_id):
                                # 移除标签和内容页面
                                self.tab_bar.removeTab(index)
                                widget = self.stacked_widget.widget(index)
                                self.stacked_widget.removeWidget(widget)
                                widget.deleteLater()
                        finally:
                            db.close()
    
    def load_households(self, village_id=None):
        """ 加载家庭数据 """
        # 清空表格
        self.household_table.setRowCount(0)

        if village_id is False:
            village_id = self.village_combo.currentData()
        
        # 加载家庭数据
        db = SessionLocal()
        try:
            households = HouseholdService.get_all_households(db, village_id=village_id)
            for i, household in enumerate(households):
                self.household_table.insertRow(i)
                self.household_table.setItem(i, 0, QTableWidgetItem(str(household.id)))
                self.household_table.setItem(i, 1, QTableWidgetItem(household.household_code))
                self.household_table.setItem(i, 2, QTableWidgetItem(household.head_of_household if household.head_of_household else '无'))
                
                # 操作按钮
                btn_layout = QHBoxLayout()
                view_btn = PushButton('查看')
                view_btn.clicked.connect(lambda _, h=household: self.view_household(h))
                edit_btn = PushButton('编辑')
                edit_btn.clicked.connect(lambda _, h=household: self.edit_household(h))
                delete_btn = PushButton('删除')
                delete_btn.clicked.connect(lambda _, h=household: self.delete_household(h))
                
                btn_widget = QWidget()
                btn_widget.setLayout(btn_layout)
                btn_layout.addWidget(view_btn)
                btn_layout.addWidget(edit_btn)
                btn_layout.addWidget(delete_btn)
                
                self.household_table.setCellWidget(i, 3, btn_widget)
            
            # 调整列宽
            self.household_table.resizeColumnsToContents()
        finally:
            db.close()
    
    def view_household(self, household):
        """ 查看家庭详细信息 """
        view = FlyoutView(
            title='家庭详细信息',
            content=f'家庭户号: {household.id}\n家庭编号: {household.household_code}\n片号: {household.plot_number}\n村庄: {household.village.name if household.village else ""}\n家庭住址: {household.address if household.address else "无"}\n电话: {household.phone if household.phone else "无"}\n户主: {household.head_of_household if household.head_of_household else "无"}',
            isClosable=True
        )
        
        # 显示视图
        w = Flyout.make(view, self.sender(), self)
        view.closed.connect(w.close)
    
    def add_household(self):
        """ 添加家庭 """
        dialog = Dialog('添加家庭', '请输入家庭信息', self)
        
        # 创建内容 widget
        content = QWidget()
        layout = QFormLayout(content)
        
        # 家庭户号（只读）
        household_id_edit = QLineEdit()
        household_id_edit.setText('系统自动生成')
        household_id_edit.setReadOnly(True)
        layout.addRow('家庭户号:', household_id_edit)
        
        # 家庭编号
        household_code_edit = QLineEdit()
        layout.addRow('家庭编号:', household_code_edit)
        
        # 片号
        plot_number_edit = QLineEdit()
        layout.addRow('片号:', plot_number_edit)
        
        # 村庄选择
        village_combo = QComboBox()
        db = SessionLocal()
        try:
            villages = VillageService.get_all_villages(db)
            for village in villages:
                village_combo.addItem(village.name, village.id)
        finally:
            db.close()
        layout.addRow('所属村庄:', village_combo)
        
        # 家庭地址
        address_edit = QLineEdit()
        layout.addRow('家庭住址:', address_edit)
        
        # 电话
        phone_edit = QLineEdit()
        layout.addRow('电话:', phone_edit)
        
        # 户主姓名（空，后续从成员中选择）
        head_of_household_edit = QLineEdit()
        head_of_household_edit.setText('请在成员管理中设置')
        head_of_household_edit.setReadOnly(True)
        layout.addRow('户主姓名:', head_of_household_edit)
        
        # 替换对话框内容
        dialog.vBoxLayout.removeWidget(dialog.contentLabel)
        dialog.contentLabel.deleteLater()
        dialog.vBoxLayout.insertWidget(1, content)
        
        # 调整对话框大小
        dialog.resize(450, 450)
        
        # 处理对话框结果
        if dialog.exec():
            household_code = household_code_edit.text().strip()
            plot_number = plot_number_edit.text().strip()
            village_id = village_combo.currentData()
            address = address_edit.text().strip()
            phone = phone_edit.text().strip()
            
            # 验证输入
            if not household_code:
                InfoBar.error(
                    title='添加失败',
                    content='家庭编号不能为空',
                    parent=self,
                    position=InfoBarPosition.TOP
                )
                return
            
            if not plot_number or not plot_number.isdigit():
                InfoBar.error(
                    title='添加失败',
                    content='片号必须为数字',
                    parent=self,
                    position=InfoBarPosition.TOP
                )
                return
            
            if not address:
                InfoBar.error(
                    title='添加失败',
                    content='家庭住址不能为空',
                    parent=self,
                    position=InfoBarPosition.TOP
                )
                return
            
            if phone and not phone.isdigit():
                InfoBar.error(
                    title='添加失败',
                    content='电话必须为数字',
                    parent=self,
                    position=InfoBarPosition.TOP
                )
                return
            
            if village_id:
                db = SessionLocal()
                try:
                    HouseholdService.create_household(
                        db, 
                        village_id=village_id, 
                        household_code=household_code, 
                        plot_number=int(plot_number),
                        address=address,
                        phone=phone,
                        head_of_household=None
                    )
                    self.load_households(self.village_combo.currentData())
                except IntegrityError:
                    db.rollback()
                    InfoBar.error(
                        title='添加失败',
                        content='家庭编号已存在，请使用其他编号',
                        parent=self,
                        position=InfoBarPosition.TOP
                    )
                finally:
                    db.close()
    
    def edit_household(self, household):
        """ 编辑家庭 """
        dialog = Dialog('编辑家庭', '请修改家庭信息', self)
        
        # 创建内容 widget
        content = QWidget()
        layout = QFormLayout(content)
        
        # 家庭户号（只读）
        household_id_edit = QLineEdit(str(household.id))
        household_id_edit.setReadOnly(True)
        layout.addRow('家庭户号:', household_id_edit)
        
        # 家庭编号
        household_code_edit = QLineEdit(household.household_code)
        layout.addRow('家庭编号:', household_code_edit)
        
        # 片号
        plot_number_edit = QLineEdit(str(household.plot_number))
        layout.addRow('片号:', plot_number_edit)
        
        # 村庄选择
        village_combo = QComboBox()
        db = SessionLocal()
        try:
            villages = VillageService.get_all_villages(db)
            for village in villages:
                village_combo.addItem(village.name, village.id)
                if village.id == household.village_id:
                    village_combo.setCurrentIndex(village_combo.count() - 1)
        finally:
            db.close()
        layout.addRow('所属村庄:', village_combo)
        
        # 家庭地址
        address_edit = QLineEdit(household.address if household.address else '')
        layout.addRow('家庭住址:', address_edit)
        
        # 电话
        phone_edit = QLineEdit(household.phone if household.phone else '')
        layout.addRow('电话:', phone_edit)
        
        # 户主姓名（只读，从成员中选择）
        head_of_household_edit = QLineEdit(household.head_of_household if household.head_of_household else '请在成员管理中设置')
        head_of_household_edit.setReadOnly(True)
        layout.addRow('户主姓名:', head_of_household_edit)
        
        # 替换对话框内容
        dialog.vBoxLayout.removeWidget(dialog.contentLabel)
        dialog.contentLabel.deleteLater()
        dialog.vBoxLayout.insertWidget(1, content)
        
        # 调整对话框大小
        dialog.resize(450, 450)
        
        # 处理对话框结果
        if dialog.exec():
            household_code = household_code_edit.text().strip()
            plot_number = plot_number_edit.text().strip()
            village_id = village_combo.currentData()
            address = address_edit.text().strip()
            phone = phone_edit.text().strip()
            
            # 验证输入
            if not household_code:
                InfoBar.error(
                    title='修改失败',
                    content='家庭编号不能为空',
                    parent=self,
                    position=InfoBarPosition.TOP
                )
                return
            
            if not plot_number or not plot_number.isdigit():
                InfoBar.error(
                    title='修改失败',
                    content='片号必须为数字',
                    parent=self,
                    position=InfoBarPosition.TOP
                )
                return
            
            if not address:
                InfoBar.error(
                    title='修改失败',
                    content='家庭住址不能为空',
                    parent=self,
                    position=InfoBarPosition.TOP
                )
                return
            
            if phone and not phone.isdigit():
                InfoBar.error(
                    title='修改失败',
                    content='电话必须为数字',
                    parent=self,
                    position=InfoBarPosition.TOP
                )
                return
            
            if household_code and village_id:
                db = SessionLocal()
                try:
                    HouseholdService.update_household(
                        db, 
                        household.id, 
                        village_id=village_id, 
                        household_code=household_code, 
                        plot_number=int(plot_number),
                        address=address,
                        phone=phone
                    )
                    self.load_households(self.village_combo.currentData())
                except IntegrityError:
                    db.rollback()
                    InfoBar.error(
                        title='修改失败',
                        content='家庭编号已存在，请使用其他编号',
                        parent=self,
                        position=InfoBarPosition.TOP
                    )
                finally:
                    db.close()
    
    def delete_household(self, household):
        """ 删除家庭 """
        db = SessionLocal()
        try:
            if HouseholdService.delete_household(db, household.id):
                self.load_households(self.village_combo.currentData())
                self.clear_member_cards()
                self.add_member_btn.setEnabled(False)
        finally:
            db.close()
    
    def clear_member_cards(self):
        """ 清空成员标签 """
        # 清空标签栏
        while self.tab_bar.count() > 0:
            self.tab_bar.removeTab(0)
        
        # 清空堆叠窗口
        while self.stacked_widget.count() > 0:
            widget = self.stacked_widget.widget(0)
            self.stacked_widget.removeWidget(widget)
            widget.deleteLater()
    
    def refresh_all(self):
        """ 刷新所有数据 """
        # 刷新村庄数据
        self.load_villages()
    
    def load_members(self, household_id=None):
        """ 加载成员数据 """
        if not household_id:
            return
        
        # 清空成员标签
        self.clear_member_cards()
        
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
                
                # 创建富文本编辑器显示表格
                text_edit = QTextEdit()
                text_edit.setReadOnly(True)
                text_edit.setHtml(get_member_excel_html(member))
                scroll_layout.addWidget(text_edit)
                
                # 添加修改按钮
                edit_btn = PrimaryPushButton('修改成员信息')
                edit_btn.clicked.connect(partial(self.edit_member, member))
                scroll_layout.addWidget(edit_btn)
                scroll_layout.addStretch()
                
                scroll_area.setWidget(scroll_content)
                scroll_area.setWidgetResizable(True)
                main_layout.addWidget(scroll_area)
                
                # 添加到堆叠窗口
                self.stacked_widget.addWidget(member_widget)
                
                # 连接标签和内容页面
                # 保存成员ID到标签项的属性中
                if tab_item:
                    tab_item.setProperty('member_id', member.id)
        finally:
            db.close()
    
    def add_member(self):
        """ 添加成员 """
        # 获取选中的家庭
        selected_row = self.household_table.currentRow()
        if selected_row == -1:
            InfoBar.error(
                title='操作失败',
                content='请先选择一个家庭',
                parent=self,
                position=InfoBarPosition.TOP
            )
            return
        
        household_id = int(self.household_table.item(selected_row, 0).text())
        
        dialog = Dialog('添加成员', '请输入成员信息', self)
        
        # 创建内容 widget
        content = QWidget()
        layout = QVBoxLayout(content)
        
        # 添加滚动区域
        scroll_area = QScrollArea()
        scroll_content = QWidget()
        main_layout = QVBoxLayout(scroll_content)
        
        # 基本信息分组
        basic_group = QGroupBox('基本信息')
        basic_layout = QGridLayout(basic_group)
        
        # 姓名
        name_edit = QLineEdit()
        basic_layout.addWidget(QLabel('姓名:'), 0, 0)
        basic_layout.addWidget(name_edit, 0, 1, 1, 3)
        
        # 性别
        gender_combo = QComboBox()
        gender_combo.addItems(['', '男', '女'])
        basic_layout.addWidget(QLabel('性别:'), 1, 0)
        basic_layout.addWidget(gender_combo, 1, 1)
        
        # 出生日期
        birth_date_edit = QDateEdit()
        birth_date_edit.setCalendarPopup(True)
        basic_layout.addWidget(QLabel('出生日期:'), 1, 2)
        basic_layout.addWidget(birth_date_edit, 1, 3)
        
        # 圣名
        baptismal_name_edit = QLineEdit()
        basic_layout.addWidget(QLabel('圣名:'), 2, 0)
        basic_layout.addWidget(baptismal_name_edit, 2, 1, 1, 3)
        
        # 与户主关系
        relation_edit = QLineEdit()
        basic_layout.addWidget(QLabel('与户主关系:'), 3, 0)
        basic_layout.addWidget(relation_edit, 3, 1)
        
        # 文化程度
        education_edit = QLineEdit()
        basic_layout.addWidget(QLabel('文化程度:'), 3, 2)
        basic_layout.addWidget(education_edit, 3, 3)
        
        # 何时迁入
        move_in_date_edit = QDateEdit()
        move_in_date_edit.setCalendarPopup(True)
        basic_layout.addWidget(QLabel('何时迁入:'), 4, 0)
        basic_layout.addWidget(move_in_date_edit, 4, 1)
        
        # 从事职业
        occupation_edit = QLineEdit()
        basic_layout.addWidget(QLabel('从事职业:'), 4, 2)
        basic_layout.addWidget(occupation_edit, 4, 3)
        
        # 教籍证件编号
        church_id_edit = QLineEdit()
        basic_layout.addWidget(QLabel('教籍证件编号:'), 5, 0)
        basic_layout.addWidget(church_id_edit, 5, 1, 1, 3)
        
        main_layout.addWidget(basic_group)
        
        # 圣洗相关信息分组
        baptism_group = QGroupBox('圣洗相关信息')
        baptism_layout = QGridLayout(baptism_group)
        
        # 施行人
        baptism_priest_edit = QLineEdit()
        baptism_layout.addWidget(QLabel('施行人:'), 0, 0)
        baptism_layout.addWidget(baptism_priest_edit, 0, 1, 1, 3)
        
        # 代父\母
        baptism_godparent_edit = QLineEdit()
        baptism_layout.addWidget(QLabel('代父\母:'), 1, 0)
        baptism_layout.addWidget(baptism_godparent_edit, 1, 1, 1, 3)
        
        # 领洗时间
        baptism_date_edit = QDateEdit()
        baptism_date_edit.setCalendarPopup(True)
        baptism_layout.addWidget(QLabel('领洗时间:'), 2, 0)
        baptism_layout.addWidget(baptism_date_edit, 2, 1)
        
        # 备注
        baptism_note_edit = QTextEdit()
        baptism_note_edit.setFixedHeight(80)
        baptism_layout.addWidget(QLabel('备注:'), 3, 0)
        baptism_layout.addWidget(baptism_note_edit, 3, 1, 1, 3)
        
        main_layout.addWidget(baptism_group)
        
        # 初领圣体和补礼信息分组
        communion_group = QGroupBox('初领圣体和补礼信息')
        communion_layout = QGridLayout(communion_group)
        
        # 初领圣体时间
        first_communion_date_edit = QDateEdit()
        first_communion_date_edit.setCalendarPopup(True)
        communion_layout.addWidget(QLabel('初领圣体时间:'), 0, 0)
        communion_layout.addWidget(first_communion_date_edit, 0, 1)
        
        # 神父
        supplementary_priest_edit = QLineEdit()
        communion_layout.addWidget(QLabel('补礼神父:'), 1, 0)
        communion_layout.addWidget(supplementary_priest_edit, 1, 1, 1, 3)
        
        # 地点
        supplementary_place_edit = QLineEdit()
        communion_layout.addWidget(QLabel('补礼地点:'), 2, 0)
        communion_layout.addWidget(supplementary_place_edit, 2, 1, 1, 3)
        
        # 日期
        supplementary_date_edit = QDateEdit()
        supplementary_date_edit.setCalendarPopup(True)
        communion_layout.addWidget(QLabel('补礼日期:'), 3, 0)
        communion_layout.addWidget(supplementary_date_edit, 3, 1)
        
        main_layout.addWidget(communion_group)
        
        # 坚振相关信息分组
        confirmation_group = QGroupBox('坚振相关信息')
        confirmation_layout = QGridLayout(confirmation_group)
        
        # 年月日
        confirmation_date_edit = QDateEdit()
        confirmation_date_edit.setCalendarPopup(True)
        confirmation_layout.addWidget(QLabel('年月日:'), 0, 0)
        confirmation_layout.addWidget(confirmation_date_edit, 0, 1)
        
        # 施行人
        confirmation_priest_edit = QLineEdit()
        confirmation_layout.addWidget(QLabel('施行人:'), 1, 0)
        confirmation_layout.addWidget(confirmation_priest_edit, 1, 1, 1, 3)
        
        # 代父\母
        confirmation_godparent_edit = QLineEdit()
        confirmation_layout.addWidget(QLabel('代父\母:'), 2, 0)
        confirmation_layout.addWidget(confirmation_godparent_edit, 2, 1, 1, 3)
        
        # 圣名
        confirmation_name_edit = QLineEdit()
        confirmation_layout.addWidget(QLabel('圣名:'), 3, 0)
        confirmation_layout.addWidget(confirmation_name_edit, 3, 1)
        
        # 年龄
        confirmation_age_edit = QLineEdit()
        confirmation_layout.addWidget(QLabel('年龄:'), 3, 2)
        confirmation_layout.addWidget(confirmation_age_edit, 3, 3)
        
        # 地点
        confirmation_place_edit = QLineEdit()
        confirmation_layout.addWidget(QLabel('地点:'), 4, 0)
        confirmation_layout.addWidget(confirmation_place_edit, 4, 1, 1, 3)
        
        main_layout.addWidget(confirmation_group)
        
        # 婚配相关信息分组
        marriage_group = QGroupBox('婚配相关信息')
        marriage_layout = QGridLayout(marriage_group)
        
        # 年月日
        marriage_date_edit = QDateEdit()
        marriage_date_edit.setCalendarPopup(True)
        marriage_layout.addWidget(QLabel('年月日:'), 0, 0)
        marriage_layout.addWidget(marriage_date_edit, 0, 1)
        
        # 主礼神父
        marriage_priest_edit = QLineEdit()
        marriage_layout.addWidget(QLabel('主礼神父:'), 1, 0)
        marriage_layout.addWidget(marriage_priest_edit, 1, 1, 1, 3)
        
        # 证人
        marriage_witness_edit = QLineEdit()
        marriage_layout.addWidget(QLabel('证人:'), 2, 0)
        marriage_layout.addWidget(marriage_witness_edit, 2, 1, 1, 3)
        
        # 事项
        marriage_dispensation_item_edit = QLineEdit()
        marriage_layout.addWidget(QLabel('宽免事项:'), 3, 0)
        marriage_layout.addWidget(marriage_dispensation_item_edit, 3, 1, 1, 3)
        
        # 神父
        marriage_dispensation_priest_edit = QLineEdit()
        marriage_layout.addWidget(QLabel('宽免神父:'), 4, 0)
        marriage_layout.addWidget(marriage_dispensation_priest_edit, 4, 1, 1, 3)
        
        # 地点
        marriage_place_edit = QLineEdit()
        marriage_layout.addWidget(QLabel('地点:'), 5, 0)
        marriage_layout.addWidget(marriage_place_edit, 5, 1, 1, 3)
        
        main_layout.addWidget(marriage_group)
        
        # 病人傅油相关信息分组
        anointing_group = QGroupBox('病人傅油相关信息')
        anointing_layout = QGridLayout(anointing_group)
        
        # 年月日
        anointing_date_edit = QDateEdit()
        anointing_date_edit.setCalendarPopup(True)
        anointing_layout.addWidget(QLabel('年月日:'), 0, 0)
        anointing_layout.addWidget(anointing_date_edit, 0, 1)
        
        # 施行人
        anointing_priest_edit = QLineEdit()
        anointing_layout.addWidget(QLabel('施行人:'), 1, 0)
        anointing_layout.addWidget(anointing_priest_edit, 1, 1, 1, 3)
        
        # 地点
        anointing_place_edit = QLineEdit()
        anointing_layout.addWidget(QLabel('地点:'), 2, 0)
        anointing_layout.addWidget(anointing_place_edit, 2, 1, 1, 3)
        
        # 死亡日期
        death_date_edit = QDateEdit()
        death_date_edit.setCalendarPopup(True)
        anointing_layout.addWidget(QLabel('死亡日期:'), 3, 0)
        anointing_layout.addWidget(death_date_edit, 3, 1)
        
        # 年龄
        death_age_edit = QLineEdit()
        anointing_layout.addWidget(QLabel('年龄:'), 3, 2)
        anointing_layout.addWidget(death_age_edit, 3, 3)
        
        main_layout.addWidget(anointing_group)
        
        # 其他信息分组
        other_group = QGroupBox('其他信息')
        other_layout = QGridLayout(other_group)
        
        # 所属善会
        association_edit = QLineEdit()
        other_layout.addWidget(QLabel('所属善会:'), 0, 0)
        other_layout.addWidget(association_edit, 0, 1, 1, 3)
        
        # 备注
        note_edit = QTextEdit()
        note_edit.setFixedHeight(100)
        other_layout.addWidget(QLabel('备注:'), 1, 0)
        other_layout.addWidget(note_edit, 1, 1, 1, 3)
        
        main_layout.addWidget(other_group)
        
        scroll_area.setWidget(scroll_content)
        scroll_area.setWidgetResizable(True)
        layout.addWidget(scroll_area)
        
        # 替换对话框内容
        dialog.vBoxLayout.removeWidget(dialog.contentLabel)
        dialog.contentLabel.deleteLater()
        dialog.vBoxLayout.insertWidget(1, content)
        
        # 调整对话框大小为父窗口的80%
        parent_width = self.width()
        parent_height = self.height()
        dialog.resize(int(parent_width * 0.8), int(parent_height * 0.8))
        
        # 处理对话框结果
        if dialog.exec():
            name = name_edit.text().strip()
            gender = gender_combo.currentText()
            birth_date = birth_date_edit.date().toPyDate() if birth_date_edit.date().isValid() else None
            baptismal_name = baptismal_name_edit.text().strip()
            relation_to_head = relation_edit.text().strip()
            education = education_edit.text().strip()
            move_in_date = move_in_date_edit.date().toPyDate() if move_in_date_edit.date().isValid() else None
            occupation = occupation_edit.text().strip()
            church_id = church_id_edit.text().strip()
            
            # 圣洗相关信息
            baptism_priest = baptism_priest_edit.text().strip()
            baptism_godparent = baptism_godparent_edit.text().strip()
            baptism_date = baptism_date_edit.date().toPyDate() if baptism_date_edit.date().isValid() else None
            baptism_note = baptism_note_edit.toPlainText().strip()
            
            # 初领圣体时间
            first_communion_date = first_communion_date_edit.date().toPyDate() if first_communion_date_edit.date().isValid() else None
            
            # 补礼相关信息
            supplementary_priest = supplementary_priest_edit.text().strip()
            supplementary_place = supplementary_place_edit.text().strip()
            supplementary_date = supplementary_date_edit.date().toPyDate() if supplementary_date_edit.date().isValid() else None
            
            # 坚振相关信息
            confirmation_date = confirmation_date_edit.date().toPyDate() if confirmation_date_edit.date().isValid() else None
            confirmation_priest = confirmation_priest_edit.text().strip()
            confirmation_godparent = confirmation_godparent_edit.text().strip()
            confirmation_name = confirmation_name_edit.text().strip()
            confirmation_age = int(confirmation_age_edit.text().strip()) if confirmation_age_edit.text().strip().isdigit() else None
            confirmation_place = confirmation_place_edit.text().strip()
            
            # 婚配相关信息
            marriage_date = marriage_date_edit.date().toPyDate() if marriage_date_edit.date().isValid() else None
            marriage_priest = marriage_priest_edit.text().strip()
            marriage_witness = marriage_witness_edit.text().strip()
            marriage_dispensation_item = marriage_dispensation_item_edit.text().strip()
            marriage_dispensation_priest = marriage_dispensation_priest_edit.text().strip()
            marriage_place = marriage_place_edit.text().strip()
            
            # 病人傅油相关信息
            anointing_date = anointing_date_edit.date().toPyDate() if anointing_date_edit.date().isValid() else None
            anointing_priest = anointing_priest_edit.text().strip()
            anointing_place = anointing_place_edit.text().strip()
            death_date = death_date_edit.date().toPyDate() if death_date_edit.date().isValid() else None
            death_age = int(death_age_edit.text().strip()) if death_age_edit.text().strip().isdigit() else None
            
            # 所属善会和备注
            association = association_edit.text().strip()
            note = note_edit.toPlainText().strip()
            
            if name and gender:
                db = SessionLocal()
                try:
                    new_member = MemberService.create_member(
                        db, 
                        household_id=household_id, 
                        name=name, 
                        gender=gender, 
                        birth_date=birth_date, 
                        baptismal_name=baptismal_name, 
                        relation_to_head=relation_to_head, 
                        education=education, 
                        move_in_date=move_in_date, 
                        occupation=occupation, 
                        church_id=church_id, 
                        baptism_priest=baptism_priest, 
                        baptism_godparent=baptism_godparent, 
                        baptism_date=baptism_date, 
                        baptism_note=baptism_note, 
                        first_communion_date=first_communion_date, 
                        supplementary_priest=supplementary_priest, 
                        supplementary_place=supplementary_place, 
                        supplementary_date=supplementary_date, 
                        confirmation_date=confirmation_date, 
                        confirmation_priest=confirmation_priest, 
                        confirmation_godparent=confirmation_godparent, 
                        confirmation_name=confirmation_name, 
                        confirmation_age=confirmation_age, 
                        confirmation_place=confirmation_place, 
                        marriage_date=marriage_date, 
                        marriage_priest=marriage_priest, 
                        marriage_witness=marriage_witness, 
                        marriage_dispensation_item=marriage_dispensation_item, 
                        marriage_dispensation_priest=marriage_dispensation_priest, 
                        marriage_place=marriage_place, 
                        anointing_date=anointing_date, 
                        anointing_priest=anointing_priest, 
                        anointing_place=anointing_place, 
                        death_date=death_date, 
                        death_age=death_age, 
                        association=association, 
                        note=note
                    )
                    # 创建新标签
                    tab_item = self.tab_bar.addTab(str(new_member.id), new_member.name)
                    
                    # 创建标签内容页面
                    member_widget = QWidget()
                    main_layout = QVBoxLayout(member_widget)
                    
                    # 创建滚动区域
                    scroll_area = QScrollArea()
                    scroll_content = QWidget()
                    scroll_layout = QVBoxLayout(scroll_content)
                    
                    # 创建富文本编辑器显示表格
                    text_edit = QTextEdit()
                    text_edit.setReadOnly(True)
                    text_edit.setHtml(get_member_excel_html(new_member))
                    scroll_layout.addWidget(text_edit)
                    
                    # 添加修改按钮
                    edit_btn = PrimaryPushButton('修改成员信息')
                    edit_btn.clicked.connect(partial(self.edit_member, new_member))
                    scroll_layout.addWidget(edit_btn)
                    scroll_layout.addStretch()
                    
                    scroll_area.setWidget(scroll_content)
                    scroll_area.setWidgetResizable(True)
                    main_layout.addWidget(scroll_area)
                    
                    # 添加到堆叠窗口
                    self.stacked_widget.addWidget(member_widget)
                    
                    # 连接标签和内容页面
                    # 保存成员ID到标签项的属性中
                    if tab_item:
                        tab_item.setProperty('member_id', new_member.id)
                    
                    # 切换到新标签
                    # 新添加的标签在最后，所以索引是count-1
                    self.tab_bar.setCurrentIndex(self.tab_bar.count() - 1)
                except IntegrityError:
                    db.rollback()
                    InfoBar.error(
                        title='添加失败',
                        content='身份证号已存在，请使用其他身份证号',
                        parent=self,
                        position=InfoBarPosition.TOP
                    )
                finally:
                    db.close()
    
    def edit_member(self, member):
        """ 编辑成员 """
        dialog = Dialog('编辑成员', '请修改成员信息', self)
        
        # 创建内容 widget
        content = QWidget()
        layout = QVBoxLayout(content)
        
        # 添加滚动区域
        scroll_area = QScrollArea()
        scroll_content = QWidget()
        main_layout = QVBoxLayout(scroll_content)
        
        # 基本信息分组
        basic_group = QGroupBox('基本信息')
        basic_layout = QGridLayout(basic_group)
        
        # 姓名
        name_edit = QLineEdit(member.name)
        basic_layout.addWidget(QLabel('姓名:'), 0, 0)
        basic_layout.addWidget(name_edit, 0, 1, 1, 3)
        
        # 性别
        gender_combo = QComboBox()
        gender_combo.addItems(['', '男', '女'])
        if member.gender:
            gender_combo.setCurrentText(member.gender)
        basic_layout.addWidget(QLabel('性别:'), 1, 0)
        basic_layout.addWidget(gender_combo, 1, 1)
        
        # 出生日期
        birth_date_edit = QDateEdit()
        birth_date_edit.setCalendarPopup(True)
        if member.birth_date:
            from PyQt5.QtCore import QDate
            birth_date_edit.setDate(QDate(member.birth_date.year, member.birth_date.month, member.birth_date.day))
        basic_layout.addWidget(QLabel('出生日期:'), 1, 2)
        basic_layout.addWidget(birth_date_edit, 1, 3)
        
        # 圣名
        baptismal_name_edit = QLineEdit(member.baptismal_name if member.baptismal_name else '')
        basic_layout.addWidget(QLabel('圣名:'), 2, 0)
        basic_layout.addWidget(baptismal_name_edit, 2, 1, 1, 3)
        
        # 与户主关系
        relation_edit = QLineEdit(member.relation_to_head if member.relation_to_head else '')
        basic_layout.addWidget(QLabel('与户主关系:'), 3, 0)
        basic_layout.addWidget(relation_edit, 3, 1)
        
        # 文化程度
        education_edit = QLineEdit(member.education if member.education else '')
        basic_layout.addWidget(QLabel('文化程度:'), 3, 2)
        basic_layout.addWidget(education_edit, 3, 3)
        
        # 何时迁入
        move_in_date_edit = QDateEdit()
        move_in_date_edit.setCalendarPopup(True)
        if member.move_in_date:
            from PyQt5.QtCore import QDate
            move_in_date_edit.setDate(QDate(member.move_in_date.year, member.move_in_date.month, member.move_in_date.day))
        basic_layout.addWidget(QLabel('何时迁入:'), 4, 0)
        basic_layout.addWidget(move_in_date_edit, 4, 1)
        
        # 从事职业
        occupation_edit = QLineEdit(member.occupation if member.occupation else '')
        basic_layout.addWidget(QLabel('从事职业:'), 4, 2)
        basic_layout.addWidget(occupation_edit, 4, 3)
        
        # 教籍证件编号
        church_id_edit = QLineEdit(member.church_id if member.church_id else '')
        basic_layout.addWidget(QLabel('教籍证件编号:'), 5, 0)
        basic_layout.addWidget(church_id_edit, 5, 1, 1, 3)
        
        main_layout.addWidget(basic_group)
        
        # 圣洗相关信息分组
        baptism_group = QGroupBox('圣洗相关信息')
        baptism_layout = QGridLayout(baptism_group)
        
        # 施行人
        baptism_priest_edit = QLineEdit(member.baptism_priest if member.baptism_priest else '')
        baptism_layout.addWidget(QLabel('施行人:'), 0, 0)
        baptism_layout.addWidget(baptism_priest_edit, 0, 1, 1, 3)
        
        # 代父\母
        baptism_godparent_edit = QLineEdit(member.baptism_godparent if member.baptism_godparent else '')
        baptism_layout.addWidget(QLabel('代父\母:'), 1, 0)
        baptism_layout.addWidget(baptism_godparent_edit, 1, 1, 1, 3)
        
        # 领洗时间
        baptism_date_edit = QDateEdit()
        baptism_date_edit.setCalendarPopup(True)
        if member.baptism_date:
            from PyQt5.QtCore import QDate
            baptism_date_edit.setDate(QDate(member.baptism_date.year, member.baptism_date.month, member.baptism_date.day))
        baptism_layout.addWidget(QLabel('领洗时间:'), 2, 0)
        baptism_layout.addWidget(baptism_date_edit, 2, 1)
        
        # 备注
        baptism_note_edit = QTextEdit(member.baptism_note if member.baptism_note else '')
        baptism_note_edit.setFixedHeight(80)
        baptism_layout.addWidget(QLabel('备注:'), 3, 0)
        baptism_layout.addWidget(baptism_note_edit, 3, 1, 1, 3)
        
        main_layout.addWidget(baptism_group)
        
        # 初领圣体和补礼信息分组
        communion_group = QGroupBox('初领圣体和补礼信息')
        communion_layout = QGridLayout(communion_group)
        
        # 初领圣体时间
        first_communion_date_edit = QDateEdit()
        first_communion_date_edit.setCalendarPopup(True)
        if member.first_communion_date:
            from PyQt5.QtCore import QDate
            first_communion_date_edit.setDate(QDate(member.first_communion_date.year, member.first_communion_date.month, member.first_communion_date.day))
        communion_layout.addWidget(QLabel('初领圣体时间:'), 0, 0)
        communion_layout.addWidget(first_communion_date_edit, 0, 1)
        
        # 神父
        supplementary_priest_edit = QLineEdit(member.supplementary_priest if member.supplementary_priest else '')
        communion_layout.addWidget(QLabel('补礼神父:'), 1, 0)
        communion_layout.addWidget(supplementary_priest_edit, 1, 1, 1, 3)
        
        # 地点
        supplementary_place_edit = QLineEdit(member.supplementary_place if member.supplementary_place else '')
        communion_layout.addWidget(QLabel('补礼地点:'), 2, 0)
        communion_layout.addWidget(supplementary_place_edit, 2, 1, 1, 3)
        
        # 日期
        supplementary_date_edit = QDateEdit()
        supplementary_date_edit.setCalendarPopup(True)
        if member.supplementary_date:
            from PyQt5.QtCore import QDate
            supplementary_date_edit.setDate(QDate(member.supplementary_date.year, member.supplementary_date.month, member.supplementary_date.day))
        communion_layout.addWidget(QLabel('补礼日期:'), 3, 0)
        communion_layout.addWidget(supplementary_date_edit, 3, 1)
        
        main_layout.addWidget(communion_group)
        
        # 坚振相关信息分组
        confirmation_group = QGroupBox('坚振相关信息')
        confirmation_layout = QGridLayout(confirmation_group)
        
        # 年月日
        confirmation_date_edit = QDateEdit()
        confirmation_date_edit.setCalendarPopup(True)
        if member.confirmation_date:
            from PyQt5.QtCore import QDate
            confirmation_date_edit.setDate(QDate(member.confirmation_date.year, member.confirmation_date.month, member.confirmation_date.day))
        confirmation_layout.addWidget(QLabel('年月日:'), 0, 0)
        confirmation_layout.addWidget(confirmation_date_edit, 0, 1)
        
        # 施行人
        confirmation_priest_edit = QLineEdit(member.confirmation_priest if member.confirmation_priest else '')
        confirmation_layout.addWidget(QLabel('施行人:'), 1, 0)
        confirmation_layout.addWidget(confirmation_priest_edit, 1, 1, 1, 3)
        
        # 代父\母
        confirmation_godparent_edit = QLineEdit(member.confirmation_godparent if member.confirmation_godparent else '')
        confirmation_layout.addWidget(QLabel('代父\母:'), 2, 0)
        confirmation_layout.addWidget(confirmation_godparent_edit, 2, 1, 1, 3)
        
        # 圣名
        confirmation_name_edit = QLineEdit(member.confirmation_name if member.confirmation_name else '')
        confirmation_layout.addWidget(QLabel('圣名:'), 3, 0)
        confirmation_layout.addWidget(confirmation_name_edit, 3, 1)
        
        # 年龄
        confirmation_age_edit = QLineEdit(str(member.confirmation_age) if member.confirmation_age else '')
        confirmation_layout.addWidget(QLabel('年龄:'), 3, 2)
        confirmation_layout.addWidget(confirmation_age_edit, 3, 3)
        
        # 地点
        confirmation_place_edit = QLineEdit(member.confirmation_place if member.confirmation_place else '')
        confirmation_layout.addWidget(QLabel('地点:'), 4, 0)
        confirmation_layout.addWidget(confirmation_place_edit, 4, 1, 1, 3)
        
        main_layout.addWidget(confirmation_group)
        
        # 婚配相关信息分组
        marriage_group = QGroupBox('婚配相关信息')
        marriage_layout = QGridLayout(marriage_group)
        
        # 年月日
        marriage_date_edit = QDateEdit()
        marriage_date_edit.setCalendarPopup(True)
        if member.marriage_date:
            from PyQt5.QtCore import QDate
            marriage_date_edit.setDate(QDate(member.marriage_date.year, member.marriage_date.month, member.marriage_date.day))
        marriage_layout.addWidget(QLabel('年月日:'), 0, 0)
        marriage_layout.addWidget(marriage_date_edit, 0, 1)
        
        # 主礼神父
        marriage_priest_edit = QLineEdit(member.marriage_priest if member.marriage_priest else '')
        marriage_layout.addWidget(QLabel('主礼神父:'), 1, 0)
        marriage_layout.addWidget(marriage_priest_edit, 1, 1, 1, 3)
        
        # 证人
        marriage_witness_edit = QLineEdit(member.marriage_witness if member.marriage_witness else '')
        marriage_layout.addWidget(QLabel('证人:'), 2, 0)
        marriage_layout.addWidget(marriage_witness_edit, 2, 1, 1, 3)
        
        # 事项
        marriage_dispensation_item_edit = QLineEdit(member.marriage_dispensation_item if member.marriage_dispensation_item else '')
        marriage_layout.addWidget(QLabel('宽免事项:'), 3, 0)
        marriage_layout.addWidget(marriage_dispensation_item_edit, 3, 1, 1, 3)
        
        # 神父
        marriage_dispensation_priest_edit = QLineEdit(member.marriage_dispensation_priest if member.marriage_dispensation_priest else '')
        marriage_layout.addWidget(QLabel('宽免神父:'), 4, 0)
        marriage_layout.addWidget(marriage_dispensation_priest_edit, 4, 1, 1, 3)
        
        # 地点
        marriage_place_edit = QLineEdit(member.marriage_place if member.marriage_place else '')
        marriage_layout.addWidget(QLabel('地点:'), 5, 0)
        marriage_layout.addWidget(marriage_place_edit, 5, 1, 1, 3)
        
        main_layout.addWidget(marriage_group)
        
        # 病人傅油相关信息分组
        anointing_group = QGroupBox('病人傅油相关信息')
        anointing_layout = QGridLayout(anointing_group)
        
        # 年月日
        anointing_date_edit = QDateEdit()
        anointing_date_edit.setCalendarPopup(True)
        if member.anointing_date:
            from PyQt5.QtCore import QDate
            anointing_date_edit.setDate(QDate(member.anointing_date.year, member.anointing_date.month, member.anointing_date.day))
        anointing_layout.addWidget(QLabel('年月日:'), 0, 0)
        anointing_layout.addWidget(anointing_date_edit, 0, 1)
        
        # 施行人
        anointing_priest_edit = QLineEdit(member.anointing_priest if member.anointing_priest else '')
        anointing_layout.addWidget(QLabel('施行人:'), 1, 0)
        anointing_layout.addWidget(anointing_priest_edit, 1, 1, 1, 3)
        
        # 地点
        anointing_place_edit = QLineEdit(member.anointing_place if member.anointing_place else '')
        anointing_layout.addWidget(QLabel('地点:'), 2, 0)
        anointing_layout.addWidget(anointing_place_edit, 2, 1, 1, 3)
        
        # 死亡日期
        death_date_edit = QDateEdit()
        death_date_edit.setCalendarPopup(True)
        if member.death_date:
            from PyQt5.QtCore import QDate
            death_date_edit.setDate(QDate(member.death_date.year, member.death_date.month, member.death_date.day))
        anointing_layout.addWidget(QLabel('死亡日期:'), 3, 0)
        anointing_layout.addWidget(death_date_edit, 3, 1)
        
        # 年龄
        death_age_edit = QLineEdit(str(member.death_age) if member.death_age else '')
        anointing_layout.addWidget(QLabel('年龄:'), 3, 2)
        anointing_layout.addWidget(death_age_edit, 3, 3)
        
        main_layout.addWidget(anointing_group)
        
        # 其他信息分组
        other_group = QGroupBox('其他信息')
        other_layout = QGridLayout(other_group)
        
        # 所属善会
        association_edit = QLineEdit(member.association if member.association else '')
        other_layout.addWidget(QLabel('所属善会:'), 0, 0)
        other_layout.addWidget(association_edit, 0, 1, 1, 3)
        
        # 备注
        note_edit = QTextEdit(member.note if member.note else '')
        note_edit.setFixedHeight(100)
        other_layout.addWidget(QLabel('备注:'), 1, 0)
        other_layout.addWidget(note_edit, 1, 1, 1, 3)
        
        main_layout.addWidget(other_group)
        
        # 设为户主按钮
        set_head_btn = PrimaryPushButton('设为户主')
        main_layout.addWidget(set_head_btn)
        
        scroll_area.setWidget(scroll_content)
        scroll_area.setWidgetResizable(True)
        layout.addWidget(scroll_area)
        
        # 替换对话框内容
        dialog.vBoxLayout.removeWidget(dialog.contentLabel)
        dialog.contentLabel.deleteLater()
        dialog.vBoxLayout.insertWidget(1, content)
        
        # 调整对话框大小为父窗口的80%
        parent_width = self.width()
        parent_height = self.height()
        dialog.resize(int(parent_width * 0.8), int(parent_height * 0.8))
        
        # 设为户主按钮点击事件
        def set_as_head():
            db = SessionLocal()
            try:
                # 更新家庭的户主姓名
                HouseholdService.update_household(
                    db, 
                    member.household_id, 
                    head_of_household=member.name
                )
                # 刷新家庭信息和成员列表
                self.load_households(self.village_combo.currentData())
                self.load_members(member.household_id)
                InfoBar.success(
                    title='操作成功',
                    content=f'已将 {member.name} 设为户主',
                    parent=self,
                    position=InfoBarPosition.TOP
                )
                dialog.accept()
            finally:
                db.close()
        
        set_head_btn.clicked.connect(set_as_head)
        
        # 处理对话框结果
        if dialog.exec():
            name = name_edit.text().strip()
            gender = gender_combo.currentText()
            birth_date = birth_date_edit.date().toPyDate() if birth_date_edit.date().isValid() else None
            baptismal_name = baptismal_name_edit.text().strip()
            relation_to_head = relation_edit.text().strip()
            education = education_edit.text().strip()
            move_in_date = move_in_date_edit.date().toPyDate() if move_in_date_edit.date().isValid() else None
            occupation = occupation_edit.text().strip()
            church_id = church_id_edit.text().strip()
            
            # 圣洗相关信息
            baptism_priest = baptism_priest_edit.text().strip()
            baptism_godparent = baptism_godparent_edit.text().strip()
            baptism_date = baptism_date_edit.date().toPyDate() if baptism_date_edit.date().isValid() else None
            baptism_note = baptism_note_edit.toPlainText().strip()
            
            # 初领圣体时间
            first_communion_date = first_communion_date_edit.date().toPyDate() if first_communion_date_edit.date().isValid() else None
            
            # 补礼相关信息
            supplementary_priest = supplementary_priest_edit.text().strip()
            supplementary_place = supplementary_place_edit.text().strip()
            supplementary_date = supplementary_date_edit.date().toPyDate() if supplementary_date_edit.date().isValid() else None
            
            # 坚振相关信息
            confirmation_date = confirmation_date_edit.date().toPyDate() if confirmation_date_edit.date().isValid() else None
            confirmation_priest = confirmation_priest_edit.text().strip()
            confirmation_godparent = confirmation_godparent_edit.text().strip()
            confirmation_name = confirmation_name_edit.text().strip()
            confirmation_age = int(confirmation_age_edit.text().strip()) if confirmation_age_edit.text().strip().isdigit() else None
            confirmation_place = confirmation_place_edit.text().strip()
            
            # 婚配相关信息
            marriage_date = marriage_date_edit.date().toPyDate() if marriage_date_edit.date().isValid() else None
            marriage_priest = marriage_priest_edit.text().strip()
            marriage_witness = marriage_witness_edit.text().strip()
            marriage_dispensation_item = marriage_dispensation_item_edit.text().strip()
            marriage_dispensation_priest = marriage_dispensation_priest_edit.text().strip()
            marriage_place = marriage_place_edit.text().strip()
            
            # 病人傅油相关信息
            anointing_date = anointing_date_edit.date().toPyDate() if anointing_date_edit.date().isValid() else None
            anointing_priest = anointing_priest_edit.text().strip()
            anointing_place = anointing_place_edit.text().strip()
            death_date = death_date_edit.date().toPyDate() if death_date_edit.date().isValid() else None
            death_age = int(death_age_edit.text().strip()) if death_age_edit.text().strip().isdigit() else None
            
            # 所属善会和备注
            association = association_edit.text().strip()
            note = note_edit.toPlainText().strip()
            
            if name and gender:
                db = SessionLocal()
                try:
                    # 更新成员信息
                    updated_member = MemberService.update_member(
                        db, 
                        member.id, 
                        name=name, 
                        gender=gender, 
                        birth_date=birth_date, 
                        baptismal_name=baptismal_name, 
                        relation_to_head=relation_to_head, 
                        education=education, 
                        move_in_date=move_in_date, 
                        occupation=occupation, 
                        church_id=church_id, 
                        baptism_priest=baptism_priest, 
                        baptism_godparent=baptism_godparent, 
                        baptism_date=baptism_date, 
                        baptism_note=baptism_note, 
                        first_communion_date=first_communion_date, 
                        supplementary_priest=supplementary_priest, 
                        supplementary_place=supplementary_place, 
                        supplementary_date=supplementary_date, 
                        confirmation_date=confirmation_date, 
                        confirmation_priest=confirmation_priest, 
                        confirmation_godparent=confirmation_godparent, 
                        confirmation_name=confirmation_name, 
                        confirmation_age=confirmation_age, 
                        confirmation_place=confirmation_place, 
                        marriage_date=marriage_date, 
                        marriage_priest=marriage_priest, 
                        marriage_witness=marriage_witness, 
                        marriage_dispensation_item=marriage_dispensation_item, 
                        marriage_dispensation_priest=marriage_dispensation_priest, 
                        marriage_place=marriage_place, 
                        anointing_date=anointing_date, 
                        anointing_priest=anointing_priest, 
                        anointing_place=anointing_place, 
                        death_date=death_date, 
                        death_age=death_age, 
                        association=association, 
                        note=note
                    )
                    
                    # 更新标签名称（如果修改了姓名）
                    for i in range(self.tab_bar.count()):
                        if i < len(self.tab_bar.items):
                            tab_item = self.tab_bar.items[i]
                            if tab_item and tab_item.property('member_id') == member.id:
                                if name != member.name:
                                    self.tab_bar.setTabText(i, name)
                                
                                # 更新标签内容
                                widget = self.stacked_widget.widget(i)
                                if widget:
                                    # 清空原有内容
                                    for child in widget.children():
                                        if hasattr(child, 'close'):
                                            child.close()
                                    
                                    # 重新创建布局
                                    main_layout = QVBoxLayout(widget)
                                    
                                    # 第一部分：基本信息和照片
                                    basic_info_layout = QHBoxLayout()
                                    
                                    # 左侧基本信息
                                    left_basic_layout = QVBoxLayout()
                                    
                                    # 第一行：姓名和性别
                                    row1_layout = QHBoxLayout()
                                    row1_layout.addWidget(QLabel('姓名:'))
                                    row1_layout.addWidget(QLabel(updated_member.name))
                                    row1_layout.addWidget(QLabel('性别:'))
                                    row1_layout.addWidget(QLabel(updated_member.gender if updated_member.gender else '无'))
                                    row1_layout.addStretch()
                                    left_basic_layout.addLayout(row1_layout)
                                    
                                    # 第二行：圣名和出生日期
                                    row2_layout = QHBoxLayout()
                                    row2_layout.addWidget(QLabel('圣名:'))
                                    row2_layout.addWidget(QLabel(updated_member.baptismal_name if updated_member.baptismal_name else '无'))
                                    row2_layout.addWidget(QLabel('出生日期:'))
                                    row2_layout.addWidget(QLabel(str(updated_member.birth_date) if updated_member.birth_date else '无'))
                                    row2_layout.addStretch()
                                    left_basic_layout.addLayout(row2_layout)
                                    
                                    # 第三行：文化程度和与户主关系
                                    row3_layout = QHBoxLayout()
                                    row3_layout.addWidget(QLabel('文化程度:'))
                                    row3_layout.addWidget(QLabel(updated_member.education if updated_member.education else '无'))
                                    row3_layout.addWidget(QLabel('与户主关系:'))
                                    row3_layout.addWidget(QLabel(updated_member.relation_to_head if updated_member.relation_to_head else '无'))
                                    row3_layout.addStretch()
                                    left_basic_layout.addLayout(row3_layout)
                                    
                                    # 第四行：何时迁入和从事职业
                                    row4_layout = QHBoxLayout()
                                    row4_layout.addWidget(QLabel('何时迁入:'))
                                    row4_layout.addWidget(QLabel(str(updated_member.move_in_date) if updated_member.move_in_date else '无'))
                                    row4_layout.addWidget(QLabel('从事职业:'))
                                    row4_layout.addWidget(QLabel(updated_member.occupation if updated_member.occupation else '无'))
                                    row4_layout.addStretch()
                                    left_basic_layout.addLayout(row4_layout)
                                    
                                    basic_info_layout.addLayout(left_basic_layout)
                                    
                                    # 右侧照片
                                    photo_layout = QVBoxLayout()
                                    photo_label = QLabel('照片')
                                    photo_label.setAlignment(Qt.AlignCenter)
                                    photo_layout.addWidget(photo_label)
                                    # 这里可以添加照片显示逻辑
                                    basic_info_layout.addLayout(photo_layout)
                                    
                                    main_layout.addLayout(basic_info_layout)
                                    
                                    # 第二部分：教籍证件编号
                                    church_id_layout = QHBoxLayout()
                                    church_id_layout.addWidget(QLabel('教籍证件编号:'))
                                    church_id_layout.addWidget(QLabel(updated_member.church_id if updated_member.church_id else '无'))
                                    church_id_layout.addStretch()
                                    main_layout.addLayout(church_id_layout)
                                    
                                    # 第三部分：圣洗、初领圣体和补礼信息
                                    sacraments_layout = QHBoxLayout()
                                    
                                    # 圣洗信息
                                    baptism_layout = QVBoxLayout()
                                    baptism_layout.addWidget(QLabel('圣洗'))
                                    
                                    baptism_row1 = QHBoxLayout()
                                    baptism_row1.addWidget(QLabel('施行人:'))
                                    baptism_row1.addWidget(QLabel(updated_member.baptism_priest if updated_member.baptism_priest else '无'))
                                    baptism_layout.addLayout(baptism_row1)
                                    
                                    baptism_row2 = QHBoxLayout()
                                    baptism_row2.addWidget(QLabel('代父\母:'))
                                    baptism_row2.addWidget(QLabel(updated_member.baptism_godparent if updated_member.baptism_godparent else '无'))
                                    baptism_layout.addLayout(baptism_row2)
                                    
                                    baptism_row3 = QHBoxLayout()
                                    baptism_row3.addWidget(QLabel('领洗时间:'))
                                    baptism_row3.addWidget(QLabel(str(updated_member.baptism_date) if updated_member.baptism_date else '无'))
                                    baptism_layout.addLayout(baptism_row3)
                                    
                                    baptism_row4 = QHBoxLayout()
                                    baptism_row4.addWidget(QLabel('备注:'))
                                    baptism_row4.addWidget(QLabel(updated_member.baptism_note if updated_member.baptism_note else '无'))
                                    baptism_layout.addLayout(baptism_row4)
                                    
                                    sacraments_layout.addLayout(baptism_layout)
                                    
                                    # 初领圣体和补礼信息
                                    communion_layout = QVBoxLayout()
                                    
                                    communion_row1 = QHBoxLayout()
                                    communion_row1.addWidget(QLabel('初领圣体时间:'))
                                    communion_row1.addWidget(QLabel(str(updated_member.first_communion_date) if updated_member.first_communion_date else '无'))
                                    communion_layout.addLayout(communion_row1)
                                    
                                    communion_row2 = QHBoxLayout()
                                    communion_row2.addWidget(QLabel('补礼'))
                                    communion_layout.addLayout(communion_row2)
                                    
                                    communion_row3 = QHBoxLayout()
                                    communion_row3.addWidget(QLabel('神父:'))
                                    communion_row3.addWidget(QLabel(updated_member.supplementary_priest if updated_member.supplementary_priest else '无'))
                                    communion_layout.addLayout(communion_row3)
                                    
                                    communion_row4 = QHBoxLayout()
                                    communion_row4.addWidget(QLabel('地点:'))
                                    communion_row4.addWidget(QLabel(updated_member.supplementary_place if updated_member.supplementary_place else '无'))
                                    communion_layout.addLayout(communion_row4)
                                    
                                    communion_row5 = QHBoxLayout()
                                    communion_row5.addWidget(QLabel('日期:'))
                                    communion_row5.addWidget(QLabel(str(updated_member.supplementary_date) if updated_member.supplementary_date else '无'))
                                    communion_layout.addLayout(communion_row5)
                                    
                                    sacraments_layout.addLayout(communion_layout)
                                    
                                    main_layout.addLayout(sacraments_layout)
                                    
                                    # 第四部分：坚振、婚配和病人傅油信息
                                    other_sacraments_layout = QHBoxLayout()
                                    
                                    # 坚振信息
                                    confirmation_layout = QVBoxLayout()
                                    confirmation_layout.addWidget(QLabel('坚振'))
                                    
                                    confirmation_row1 = QHBoxLayout()
                                    confirmation_row1.addWidget(QLabel('年月日:'))
                                    confirmation_row1.addWidget(QLabel(str(updated_member.confirmation_date) if updated_member.confirmation_date else '无'))
                                    confirmation_layout.addLayout(confirmation_row1)
                                    
                                    confirmation_row2 = QHBoxLayout()
                                    confirmation_row2.addWidget(QLabel('施行人:'))
                                    confirmation_row2.addWidget(QLabel(updated_member.confirmation_priest if updated_member.confirmation_priest else '无'))
                                    confirmation_layout.addLayout(confirmation_row2)
                                    
                                    confirmation_row3 = QHBoxLayout()
                                    confirmation_row3.addWidget(QLabel('代父\母:'))
                                    confirmation_row3.addWidget(QLabel(updated_member.confirmation_godparent if updated_member.confirmation_godparent else '无'))
                                    confirmation_layout.addLayout(confirmation_row3)
                                    
                                    confirmation_row4 = QHBoxLayout()
                                    confirmation_row4.addWidget(QLabel('圣名:'))
                                    confirmation_row4.addWidget(QLabel(updated_member.confirmation_name if updated_member.confirmation_name else '无'))
                                    confirmation_layout.addLayout(confirmation_row4)
                                    
                                    confirmation_row5 = QHBoxLayout()
                                    confirmation_row5.addWidget(QLabel('年龄:'))
                                    confirmation_row5.addWidget(QLabel(str(updated_member.confirmation_age) if updated_member.confirmation_age else '无'))
                                    confirmation_layout.addLayout(confirmation_row5)
                                    
                                    confirmation_row6 = QHBoxLayout()
                                    confirmation_row6.addWidget(QLabel('地点:'))
                                    confirmation_row6.addWidget(QLabel(updated_member.confirmation_place if updated_member.confirmation_place else '无'))
                                    confirmation_layout.addLayout(confirmation_row6)
                                    
                                    other_sacraments_layout.addLayout(confirmation_layout)
                                    
                                    # 婚配信息
                                    marriage_layout = QVBoxLayout()
                                    marriage_layout.addWidget(QLabel('婚配'))
                                    
                                    marriage_row1 = QHBoxLayout()
                                    marriage_row1.addWidget(QLabel('年月日:'))
                                    marriage_row1.addWidget(QLabel(str(updated_member.marriage_date) if updated_member.marriage_date else '无'))
                                    marriage_layout.addLayout(marriage_row1)
                                    
                                    marriage_row2 = QHBoxLayout()
                                    marriage_row2.addWidget(QLabel('主礼神父:'))
                                    marriage_row2.addWidget(QLabel(updated_member.marriage_priest if updated_member.marriage_priest else '无'))
                                    marriage_layout.addLayout(marriage_row2)
                                    
                                    marriage_row3 = QHBoxLayout()
                                    marriage_row3.addWidget(QLabel('证人:'))
                                    marriage_row3.addWidget(QLabel(updated_member.marriage_witness if updated_member.marriage_witness else '无'))
                                    marriage_layout.addLayout(marriage_row3)
                                    
                                    marriage_row4 = QHBoxLayout()
                                    marriage_row4.addWidget(QLabel('宽免'))
                                    marriage_layout.addLayout(marriage_row4)
                                    
                                    marriage_row5 = QHBoxLayout()
                                    marriage_row5.addWidget(QLabel('事项:'))
                                    marriage_row5.addWidget(QLabel(updated_member.marriage_dispensation_item if updated_member.marriage_dispensation_item else '无'))
                                    marriage_layout.addLayout(marriage_row5)
                                    
                                    marriage_row6 = QHBoxLayout()
                                    marriage_row6.addWidget(QLabel('神父:'))
                                    marriage_row6.addWidget(QLabel(updated_member.marriage_dispensation_priest if updated_member.marriage_dispensation_priest else '无'))
                                    marriage_layout.addLayout(marriage_row6)
                                    
                                    marriage_row7 = QHBoxLayout()
                                    marriage_row7.addWidget(QLabel('地点:'))
                                    marriage_row7.addWidget(QLabel(updated_member.marriage_place if updated_member.marriage_place else '无'))
                                    marriage_layout.addLayout(marriage_row7)
                                    
                                    other_sacraments_layout.addLayout(marriage_layout)
                                    
                                    # 病人傅油信息
                                    anointing_layout = QVBoxLayout()
                                    anointing_layout.addWidget(QLabel('病人傅油'))
                                    
                                    anointing_row1 = QHBoxLayout()
                                    anointing_row1.addWidget(QLabel('年月日:'))
                                    anointing_row1.addWidget(QLabel(str(updated_member.anointing_date) if updated_member.anointing_date else '无'))
                                    anointing_layout.addLayout(anointing_row1)
                                    
                                    anointing_row2 = QHBoxLayout()
                                    anointing_row2.addWidget(QLabel('施行人:'))
                                    anointing_row2.addWidget(QLabel(updated_member.anointing_priest if updated_member.anointing_priest else '无'))
                                    anointing_layout.addLayout(anointing_row2)
                                    
                                    anointing_row3 = QHBoxLayout()
                                    anointing_row3.addWidget(QLabel('地点:'))
                                    anointing_row3.addWidget(QLabel(updated_member.anointing_place if updated_member.anointing_place else '无'))
                                    anointing_layout.addLayout(anointing_row3)
                                    
                                    anointing_row4 = QHBoxLayout()
                                    anointing_row4.addWidget(QLabel('死亡日期:'))
                                    anointing_row4.addWidget(QLabel(str(updated_member.death_date) if updated_member.death_date else '无'))
                                    anointing_layout.addLayout(anointing_row4)
                                    
                                    anointing_row5 = QHBoxLayout()
                                    anointing_row5.addWidget(QLabel('年龄:'))
                                    anointing_row5.addWidget(QLabel(str(updated_member.death_age) if updated_member.death_age else '无'))
                                    anointing_layout.addLayout(anointing_row5)
                                    
                                    other_sacraments_layout.addLayout(anointing_layout)
                                    
                                    main_layout.addLayout(other_sacraments_layout)
                                    
                                    # 第五部分：所属善会和备注
                                    association_layout = QHBoxLayout()
                                    association_layout.addWidget(QLabel('所属善会:'))
                                    association_layout.addWidget(QLabel(updated_member.association if updated_member.association else '无'))
                                    association_layout.addStretch()
                                    main_layout.addLayout(association_layout)
                                    
                                    note_layout = QHBoxLayout()
                                    note_layout.addWidget(QLabel('备注:'))
                                    note_layout.addWidget(QLabel(updated_member.note if updated_member.note else '无'))
                                    note_layout.addStretch()
                                    main_layout.addLayout(note_layout)
                                    
                                    # 添加修改按钮
                                    edit_btn = PrimaryPushButton('修改成员信息')
                                    edit_btn.clicked.connect(partial(self.edit_member, updated_member))
                                    main_layout.addWidget(edit_btn)
                                    main_layout.addStretch()
                                break
                except IntegrityError:
                    db.rollback()
                    InfoBar.error(
                        title='修改失败',
                        content='身份证号已存在，请使用其他身份证号',
                        parent=self,
                        position=InfoBarPosition.TOP
                    )
                finally:
                    db.close()
