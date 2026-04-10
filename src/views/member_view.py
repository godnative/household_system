from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidgetItem, QFormLayout, QLineEdit, QLabel, QComboBox
from PyQt5.QtCore import Qt
from qfluentwidgets import PrimaryPushButton, PushButton, TableWidget, Dialog, InfoBar, InfoBarPosition
from src.services.member_service import MemberService
from src.services.household_service import HouseholdService
from src.models import SessionLocal, Member
from sqlalchemy.exc import IntegrityError

class MemberWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        self.load_members()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # 标题
        title_label = QLabel('成员管理')
        title_label.setStyleSheet('font-size: 18px; font-weight: bold;')
        layout.addWidget(title_label)
        
        # 操作按钮
        btn_layout = QHBoxLayout()
        add_btn = PrimaryPushButton('添加成员')
        add_btn.clicked.connect(self.add_member)
        btn_layout.addWidget(add_btn)
        
        refresh_btn = PushButton('刷新')
        refresh_btn.clicked.connect(self.load_members)
        btn_layout.addWidget(refresh_btn)
        
        layout.addLayout(btn_layout)
        
        # 表格
        self.table = TableWidget()
        self.table.setBorderVisible(True)
        self.table.setBorderRadius(8)
        self.table.setWordWrap(False)
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(['ID', '姓名', '身份证号', '家庭', '操作'])
        self.table.verticalHeader().hide()
        # 设置行高
        self.table.verticalHeader().setDefaultSectionSize(60)
        layout.addWidget(self.table)
    
    def load_members(self):
        # 清空表格
        self.table.setRowCount(0)
        
        # 加载成员数据
        db = SessionLocal()
        try:
            members = MemberService.get_all_members(db)
            for i, member in enumerate(members):
                self.table.insertRow(i)
                self.table.setItem(i, 0, QTableWidgetItem(str(member.id)))
                self.table.setItem(i, 1, QTableWidgetItem(member.name))
                self.table.setItem(i, 2, QTableWidgetItem(member.id_number))
                self.table.setItem(i, 3, QTableWidgetItem(f"家庭 {member.household.id}" if member.household else ''))
                
                # 操作按钮
                btn_layout = QHBoxLayout()
                edit_btn = PushButton('编辑')
                edit_btn.clicked.connect(lambda _, m=member: self.edit_member(m))
                delete_btn = PushButton('删除')
                delete_btn.clicked.connect(lambda _, m=member: self.delete_member(m))
                
                btn_widget = QWidget()
                btn_widget.setLayout(btn_layout)
                btn_layout.addWidget(edit_btn)
                btn_layout.addWidget(delete_btn)
                
                self.table.setCellWidget(i, 4, btn_widget)
            
            # 调整列宽
            self.table.resizeColumnsToContents()
        finally:
            db.close()
    
    def add_member(self):
        # 创建对话框
        dialog = Dialog('添加成员', '请输入成员信息', self)
        
        # 创建内容 widget
        content = QWidget()
        layout = QFormLayout(content)
        
        # 姓名
        name_edit = QLineEdit()
        layout.addRow('姓名:', name_edit)
        
        # 身份证号
        id_number_edit = QLineEdit()
        layout.addRow('身份证号:', id_number_edit)
        
        # 家庭选择
        household_combo = QComboBox()
        db = SessionLocal()
        try:
            households = HouseholdService.get_all_households(db)
            for household in households:
                display_text = f"家庭 {household.id}"
                if household.head_of_household:
                    display_text += f" - {household.head_of_household}"
                household_combo.addItem(display_text, household.id)
        finally:
            db.close()
        layout.addRow('所属家庭:', household_combo)
        
        # 替换对话框内容
        dialog.vBoxLayout.removeWidget(dialog.contentLabel)
        dialog.contentLabel.deleteLater()
        dialog.vBoxLayout.insertWidget(1, content)
        
        # 调整对话框大小
        dialog.resize(450, 300)
        
        # 处理对话框结果
        if dialog.exec():
            name = name_edit.text().strip()
            id_number = id_number_edit.text().strip()
            household_id = household_combo.currentData()
            if name and id_number and household_id:
                db = SessionLocal()
                try:
                    MemberService.create_member(db, name=name, id_number=id_number, household_id=household_id)
                    self.load_members()
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
        # 创建对话框
        dialog = Dialog('编辑成员', '请修改成员信息', self)
        
        # 创建内容 widget
        content = QWidget()
        layout = QFormLayout(content)
        
        # 姓名
        name_edit = QLineEdit(member.name)
        layout.addRow('姓名:', name_edit)
        
        # 身份证号
        id_number_edit = QLineEdit(member.id_number)
        layout.addRow('身份证号:', id_number_edit)
        
        # 家庭选择
        household_combo = QComboBox()
        db = SessionLocal()
        try:
            households = HouseholdService.get_all_households(db)
            for household in households:
                display_text = f"家庭 {household.id}"
                if household.head_of_household:
                    display_text += f" - {household.head_of_household}"
                household_combo.addItem(display_text, household.id)
                if household.id == member.household_id:
                    household_combo.setCurrentIndex(household_combo.count() - 1)
        finally:
            db.close()
        layout.addRow('所属家庭:', household_combo)
        
        # 替换对话框内容
        dialog.vBoxLayout.removeWidget(dialog.contentLabel)
        dialog.contentLabel.deleteLater()
        dialog.vBoxLayout.insertWidget(1, content)
        
        # 调整对话框大小
        dialog.resize(450, 300)
        
        # 处理对话框结果
        if dialog.exec():
            name = name_edit.text().strip()
            id_number = id_number_edit.text().strip()
            household_id = household_combo.currentData()
            if name and id_number and household_id:
                db = SessionLocal()
                try:
                    MemberService.update_member(db, member.id, name=name, id_number=id_number, household_id=household_id)
                    self.load_members()
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
    
    def delete_member(self, member):
        db = SessionLocal()
        try:
            if MemberService.delete_member(db, member.id):
                self.load_members()
        finally:
            db.close()