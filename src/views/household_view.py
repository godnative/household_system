from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidgetItem, QDialog, QFormLayout, QLineEdit, QLabel, QComboBox
from PyQt5.QtCore import Qt
from qfluentwidgets import PrimaryPushButton, PushButton, TableWidget
from src.services.household_service import HouseholdService
from src.services.village_service import VillageService
from src.models import SessionLocal, Household

class HouseholdWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        self.load_households()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # 标题
        title_label = QLabel('家庭管理')
        title_label.setStyleSheet('font-size: 18px; font-weight: bold;')
        layout.addWidget(title_label)
        
        # 操作按钮
        btn_layout = QHBoxLayout()
        add_btn = PrimaryPushButton('添加家庭')
        add_btn.clicked.connect(self.add_household)
        btn_layout.addWidget(add_btn)
        
        refresh_btn = PushButton('刷新')
        refresh_btn.clicked.connect(self.load_households)
        btn_layout.addWidget(refresh_btn)
        
        layout.addLayout(btn_layout)
        
        # 表格
        self.table = TableWidget()
        self.table.setBorderVisible(True)
        self.table.setBorderRadius(8)
        self.table.setWordWrap(False)
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(['ID', '家庭编号', '村庄', '操作'])
        self.table.verticalHeader().hide()
        layout.addWidget(self.table)
    
    def load_households(self):
        # 清空表格
        self.table.setRowCount(0)
        
        # 加载家庭数据
        db = SessionLocal()
        try:
            households = HouseholdService.get_all_households(db)
            for i, household in enumerate(households):
                self.table.insertRow(i)
                self.table.setItem(i, 0, QTableWidgetItem(str(household.id)))
                self.table.setItem(i, 1, QTableWidgetItem(household.household_code))
                self.table.setItem(i, 2, QTableWidgetItem(household.village.name if household.village else ''))
                
                # 操作按钮
                btn_layout = QHBoxLayout()
                edit_btn = PushButton('编辑')
                edit_btn.clicked.connect(lambda _, h=household: self.edit_household(h))
                delete_btn = PushButton('删除')
                delete_btn.clicked.connect(lambda _, h=household: self.delete_household(h))
                
                btn_widget = QWidget()
                btn_widget.setLayout(btn_layout)
                btn_layout.addWidget(edit_btn)
                btn_layout.addWidget(delete_btn)
                
                self.table.setCellWidget(i, 3, btn_widget)
            
            # 调整列宽
            self.table.resizeColumnsToContents()
        finally:
            db.close()
    
    def add_household(self):
        dialog = QDialog(self)
        dialog.setWindowTitle('添加家庭')
        dialog.resize(400, 250)
        
        layout = QFormLayout(dialog)
        
        # 家庭编号
        household_number_edit = QLineEdit()
        layout.addRow('家庭编号:', household_number_edit)
        
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
        
        btn_layout = QHBoxLayout()
        ok_btn = PrimaryPushButton('确定')
        cancel_btn = PushButton('取消')
        
        btn_layout.addStretch()
        btn_layout.addWidget(ok_btn)
        btn_layout.addWidget(cancel_btn)
        
        layout.addRow(btn_layout)
        
        def on_ok():
            household_number = household_number_edit.text().strip()
            village_id = village_combo.currentData()
            if household_number and village_id:
                db = SessionLocal()
                try:
                    HouseholdService.create_household(db, village_id=village_id, household_code=household_number)
                    self.load_households()
                    dialog.accept()
                finally:
                    db.close()
        
        ok_btn.clicked.connect(on_ok)
        cancel_btn.clicked.connect(dialog.reject)
        
        dialog.exec_()
    
    def edit_household(self, household):
        dialog = QDialog(self)
        dialog.setWindowTitle('编辑家庭')
        dialog.resize(400, 250)
        
        layout = QFormLayout(dialog)
        
        # 家庭编号
        household_number_edit = QLineEdit(household.household_code)
        layout.addRow('家庭编号:', household_number_edit)
        
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
        
        btn_layout = QHBoxLayout()
        ok_btn = PrimaryPushButton('确定')
        cancel_btn = PushButton('取消')
        
        btn_layout.addStretch()
        btn_layout.addWidget(ok_btn)
        btn_layout.addWidget(cancel_btn)
        
        layout.addRow(btn_layout)
        
        def on_ok():
            household_number = household_number_edit.text().strip()
            village_id = village_combo.currentData()
            if household_number and village_id:
                db = SessionLocal()
                try:
                    HouseholdService.update_household(db, household.id, household_code=household_number, village_id=village_id)
                    self.load_households()
                    dialog.accept()
                finally:
                    db.close()
        
        ok_btn.clicked.connect(on_ok)
        cancel_btn.clicked.connect(dialog.reject)
        
        dialog.exec_()
    
    def delete_household(self, household):
        db = SessionLocal()
        try:
            if HouseholdService.delete_household(db, household.id):
                self.load_households()
        finally:
            db.close()