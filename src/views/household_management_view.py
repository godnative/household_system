from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidgetItem, QFormLayout, QLineEdit, QLabel, QComboBox, QScrollArea, QDateEdit, QTextEdit, QStackedWidget
from PyQt5.QtCore import Qt
from functools import partial
from qfluentwidgets import PrimaryPushButton, PushButton, TableWidget, Dialog, InfoBar, InfoBarPosition, ComboBox, FlowLayout, ElevatedCardWidget, BodyLabel, CaptionLabel, TitleLabel, Flyout, FlyoutView, TabBar, TabCloseButtonDisplayMode
from src.services.household_service import HouseholdService
from src.services.member_service import MemberService
from src.services.village_service import VillageService
from src.models import SessionLocal, Household, Member
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
                layout = QVBoxLayout(member_widget)
                
                # 添加成员详细信息
                info_layout = QFormLayout()
                info_layout.addRow('姓名:', QLabel(member.name))
                info_layout.addRow('性别:', QLabel(member.gender if member.gender else '无'))
                info_layout.addRow('出生日期:', QLabel(str(member.birth_date) if member.birth_date else '无'))
                info_layout.addRow('身份证号:', QLabel(member.id_number))
                info_layout.addRow('与户主关系:', QLabel(member.relation_to_head if member.relation_to_head else '无'))
                info_layout.addRow('状态:', QLabel(member.status if member.status else '无'))
                
                # 添加修改按钮
                edit_btn = PrimaryPushButton('修改成员信息')
                edit_btn.clicked.connect(partial(self.edit_member, member))
                
                layout.addLayout(info_layout)
                layout.addWidget(edit_btn)
                layout.addStretch()
                
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
        layout = QFormLayout(content)
        
        # 姓名
        name_edit = QLineEdit()
        layout.addRow('姓名:', name_edit)
        
        # 性别
        gender_combo = QComboBox()
        gender_combo.addItems(['', '男', '女'])
        layout.addRow('性别:', gender_combo)
        
        # 出生日期
        birth_date_edit = QDateEdit()
        birth_date_edit.setCalendarPopup(True)
        layout.addRow('出生日期:', birth_date_edit)
        
        # 身份证号
        id_number_edit = QLineEdit()
        layout.addRow('身份证号:', id_number_edit)
        
        # 与户主关系
        relation_edit = QLineEdit()
        layout.addRow('与户主关系:', relation_edit)
        
        # 状态
        status_edit = QLineEdit()
        layout.addRow('状态:', status_edit)
        
        # 替换对话框内容
        dialog.vBoxLayout.removeWidget(dialog.contentLabel)
        dialog.contentLabel.deleteLater()
        dialog.vBoxLayout.insertWidget(1, content)
        
        # 调整对话框大小
        dialog.resize(450, 450)
        
        # 处理对话框结果
        if dialog.exec():
            name = name_edit.text().strip()
            gender = gender_combo.currentText()
            birth_date = birth_date_edit.date().toPyDate() if birth_date_edit.date().isValid() else None
            id_number = id_number_edit.text().strip()
            relation_to_head = relation_edit.text().strip()
            status = status_edit.text().strip()
            
            if name and id_number:
                db = SessionLocal()
                try:
                    new_member = MemberService.create_member(
                        db, 
                        household_id=household_id, 
                        name=name, 
                        gender=gender, 
                        birth_date=birth_date, 
                        id_number=id_number, 
                        relation_to_head=relation_to_head, 
                        status=status
                    )
                    # 创建新标签
                    tab_item = self.tab_bar.addTab(str(new_member.id), new_member.name)
                    
                    # 创建标签内容页面
                    member_widget = QWidget()
                    layout = QVBoxLayout(member_widget)
                    
                    # 添加成员详细信息
                    info_layout = QFormLayout()
                    info_layout.addRow('姓名:', QLabel(new_member.name))
                    info_layout.addRow('性别:', QLabel(new_member.gender if new_member.gender else '无'))
                    info_layout.addRow('出生日期:', QLabel(str(new_member.birth_date) if new_member.birth_date else '无'))
                    info_layout.addRow('身份证号:', QLabel(new_member.id_number))
                    info_layout.addRow('与户主关系:', QLabel(new_member.relation_to_head if new_member.relation_to_head else '无'))
                    info_layout.addRow('状态:', QLabel(new_member.status if new_member.status else '无'))
                    
                    # 添加修改按钮
                    edit_btn = PrimaryPushButton('修改成员信息')
                    edit_btn.clicked.connect(partial(self.edit_member, new_member))
                    
                    layout.addLayout(info_layout)
                    layout.addWidget(edit_btn)
                    layout.addStretch()
                    
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
        layout = QFormLayout(content)
        
        # 姓名
        name_edit = QLineEdit(member.name)
        layout.addRow('姓名:', name_edit)
        
        # 性别
        gender_combo = QComboBox()
        gender_combo.addItems(['', '男', '女'])
        if member.gender:
            gender_combo.setCurrentText(member.gender)
        layout.addRow('性别:', gender_combo)
        
        # 出生日期
        birth_date_edit = QDateEdit()
        birth_date_edit.setCalendarPopup(True)
        if member.birth_date:
            from PyQt5.QtCore import QDate
            birth_date_edit.setDate(QDate(member.birth_date.year, member.birth_date.month, member.birth_date.day))
        layout.addRow('出生日期:', birth_date_edit)
        
        # 身份证号
        id_number_edit = QLineEdit(member.id_number)
        layout.addRow('身份证号:', id_number_edit)
        
        # 与户主关系
        relation_edit = QLineEdit(member.relation_to_head if member.relation_to_head else '')
        layout.addRow('与户主关系:', relation_edit)
        
        # 状态
        status_edit = QLineEdit(member.status if member.status else '')
        layout.addRow('状态:', status_edit)
        
        # 设为户主按钮
        set_head_btn = PrimaryPushButton('设为户主')
        layout.addRow(set_head_btn)
        
        # 替换对话框内容
        dialog.vBoxLayout.removeWidget(dialog.contentLabel)
        dialog.contentLabel.deleteLater()
        dialog.vBoxLayout.insertWidget(1, content)
        
        # 调整对话框大小
        dialog.resize(450, 500)
        
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
            id_number = id_number_edit.text().strip()
            relation_to_head = relation_edit.text().strip()
            status = status_edit.text().strip()
            
            if name and id_number:
                db = SessionLocal()
                try:
                    # 更新成员信息
                    updated_member = MemberService.update_member(
                        db, 
                        member.id, 
                        name=name, 
                        gender=gender, 
                        birth_date=birth_date, 
                        id_number=id_number, 
                        relation_to_head=relation_to_head, 
                        status=status
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
                                    layout = QVBoxLayout(widget)
                                    
                                    # 添加成员详细信息
                                    info_layout = QFormLayout()
                                    info_layout.addRow('姓名:', QLabel(updated_member.name))
                                    info_layout.addRow('性别:', QLabel(updated_member.gender if updated_member.gender else '无'))
                                    info_layout.addRow('出生日期:', QLabel(str(updated_member.birth_date) if updated_member.birth_date else '无'))
                                    info_layout.addRow('身份证号:', QLabel(updated_member.id_number))
                                    info_layout.addRow('与户主关系:', QLabel(updated_member.relation_to_head if updated_member.relation_to_head else '无'))
                                    info_layout.addRow('状态:', QLabel(updated_member.status if updated_member.status else '无'))
                                    
                                    # 添加修改按钮
                                    edit_btn = PrimaryPushButton('修改成员信息')
                                    edit_btn.clicked.connect(partial(self.edit_member, updated_member))
                                    
                                    layout.addLayout(info_layout)
                                    layout.addWidget(edit_btn)
                                    layout.addStretch()
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
