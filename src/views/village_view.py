from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidgetItem, QFormLayout, QLineEdit, QLabel
from PyQt5.QtCore import Qt
from qfluentwidgets import PrimaryPushButton, PushButton, TableWidget, Dialog
from src.services.village_service import VillageService
from src.models import SessionLocal, Village

class VillageWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        self.load_villages()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # 标题
        title_label = QLabel('村庄管理')
        title_label.setStyleSheet('font-size: 18px; font-weight: bold;')
        layout.addWidget(title_label)
        
        # 操作按钮
        btn_layout = QHBoxLayout()
        add_btn = PrimaryPushButton('添加村庄')
        add_btn.clicked.connect(self.add_village)
        btn_layout.addWidget(add_btn)
        
        refresh_btn = PushButton('刷新')
        refresh_btn.clicked.connect(self.load_villages)
        btn_layout.addWidget(refresh_btn)
        
        layout.addLayout(btn_layout)
        
        # 表格
        self.table = TableWidget()
        self.table.setBorderVisible(True)
        self.table.setBorderRadius(8)
        self.table.setWordWrap(False)
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(['ID', '村庄名称', '操作'])
        self.table.verticalHeader().hide()
        # 设置行高
        self.table.verticalHeader().setDefaultSectionSize(60)
        layout.addWidget(self.table)
    
    def load_villages(self):
        # 清空表格
        self.table.setRowCount(0)
        
        # 加载村庄数据
        db = SessionLocal()
        try:
            villages = VillageService.get_all_villages(db)
            for i, village in enumerate(villages):
                self.table.insertRow(i)
                self.table.setItem(i, 0, QTableWidgetItem(str(village.id)))
                self.table.setItem(i, 1, QTableWidgetItem(village.name))
                
                # 操作按钮
                btn_layout = QHBoxLayout()
                edit_btn = PushButton('编辑')
                edit_btn.clicked.connect(lambda _, v=village: self.edit_village(v))
                delete_btn = PushButton('删除')
                delete_btn.clicked.connect(lambda _, v=village: self.delete_village(v))
                
                btn_widget = QWidget()
                btn_widget.setLayout(btn_layout)
                btn_layout.addWidget(edit_btn)
                btn_layout.addWidget(delete_btn)
                
                self.table.setCellWidget(i, 2, btn_widget)
            
            # 调整列宽
            self.table.resizeColumnsToContents()
        finally:
            db.close()
    
    def add_village(self):
        # 创建对话框
        dialog = Dialog('添加村庄', '请输入村庄信息', self)
        
        # 创建内容 widget
        content = QWidget()
        layout = QFormLayout(content)
        
        name_edit = QLineEdit()
        layout.addRow('村庄名称:', name_edit)
        
        code_edit = QLineEdit()
        layout.addRow('村庄代码:', code_edit)
        
        # 替换对话框内容
        dialog.vBoxLayout.removeWidget(dialog.contentLabel)
        dialog.contentLabel.deleteLater()
        dialog.vBoxLayout.insertWidget(1, content)
        
        # 调整对话框大小
        dialog.resize(400, 200)
        
        # 处理对话框结果
        if dialog.exec():
            name = name_edit.text().strip()
            code = code_edit.text().strip()
            if name and code:
                db = SessionLocal()
                try:
                    VillageService.create_village(db, name=name, code=code)
                    self.load_villages()
                finally:
                    db.close()
    
    def edit_village(self, village):
        # 创建对话框
        dialog = Dialog('编辑村庄', '请修改村庄信息', self)
        
        # 创建内容 widget
        content = QWidget()
        layout = QFormLayout(content)
        
        name_edit = QLineEdit(village.name)
        layout.addRow('村庄名称:', name_edit)
        
        code_edit = QLineEdit(village.code)
        layout.addRow('村庄代码:', code_edit)
        
        # 替换对话框内容
        dialog.vBoxLayout.removeWidget(dialog.contentLabel)
        dialog.contentLabel.deleteLater()
        dialog.vBoxLayout.insertWidget(1, content)
        
        # 调整对话框大小
        dialog.resize(400, 200)
        
        # 处理对话框结果
        if dialog.exec():
            name = name_edit.text().strip()
            code = code_edit.text().strip()
            if name and code:
                db = SessionLocal()
                try:
                    VillageService.update_village(db, village.id, name=name, code=code)
                    self.load_villages()
                finally:
                    db.close()
    
    def delete_village(self, village):
        db = SessionLocal()
        try:
            if VillageService.delete_village(db, village.id):
                self.load_villages()
        finally:
            db.close()