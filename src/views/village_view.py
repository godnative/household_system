from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidgetItem, QFormLayout, QLineEdit, QLabel, QDateEdit, QTextEdit, QFileDialog
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QPixmap
from qfluentwidgets import PrimaryPushButton, PushButton, TableWidget, Dialog, InfoBar, InfoBarPosition
from src.services.village_service import VillageService
from src.models import SessionLocal, Village
from sqlalchemy.exc import IntegrityError
from PIL import Image
import os
import shutil
import time

class VillageWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        # 初始化照片存储目录
        self.photo_dir = os.path.join(os.path.dirname(__file__), '..', 'static', 'village_photos')
        if not os.path.exists(self.photo_dir):
            os.makedirs(self.photo_dir)
        self.init_ui()
        self.load_villages()
    
    def save_photo(self, photo_path):
        """保存照片并调整尺寸"""
        if not photo_path:
            return None
        
        try:
            # 生成唯一文件名
            filename = f"village_{int(time.time())}_{os.path.basename(photo_path)}"
            save_path = os.path.join(self.photo_dir, filename)
            
            # 调整照片尺寸
            img = Image.open(photo_path)
            max_width = 800
            if img.width > max_width:
                ratio = max_width / img.width
                new_height = int(img.height * ratio)
                img = img.resize((max_width, new_height), Image.LANCZOS)
            
            # 保存照片
            img.save(save_path)
            return os.path.basename(filename)
        except Exception as e:
            print(f"保存照片失败: {e}")
            return None
    
    def get_photo_path(self, photo_filename):
        """获取照片完整路径"""
        if not photo_filename:
            return None
        return os.path.join(self.photo_dir, photo_filename)
    
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
        
        # 新增字段
        establishment_date_edit = QDateEdit()
        establishment_date_edit.setCalendarPopup(True)
        establishment_date_edit.setDate(QDate.currentDate())
        layout.addRow('建立日期:', establishment_date_edit)
        
        village_priest_edit = QLineEdit()
        layout.addRow('村庄神父:', village_priest_edit)
        
        address_edit = QLineEdit()
        layout.addRow('村庄地址:', address_edit)
        
        description_edit = QTextEdit()
        layout.addRow('村庄简介:', description_edit)
        
        # 照片上传
        photo_layout = QHBoxLayout()
        photo_label = QLabel('暂无图片')
        photo_label.setFixedSize(100, 100)
        photo_label.setStyleSheet('border: 1px solid #ddd;')
        photo_layout.addWidget(photo_label)
        
        photo_path = None
        def select_photo():
            nonlocal photo_path
            file_path, _ = QFileDialog.getOpenFileName(self, '选择照片', '', 'Image Files (*.jpg *.jpeg *.png *.bmp)')
            if file_path:
                photo_path = file_path
                pixmap = QPixmap(file_path)
                pixmap = pixmap.scaled(100, 100, Qt.KeepAspectRatio)
                photo_label.setPixmap(pixmap)
                photo_label.setText('')
        
        photo_btn = PushButton('选择照片')
        photo_btn.clicked.connect(select_photo)
        photo_layout.addWidget(photo_btn)
        layout.addRow('村庄照片:', photo_layout)
        
        # 替换对话框内容
        dialog.vBoxLayout.removeWidget(dialog.contentLabel)
        dialog.contentLabel.deleteLater()
        dialog.vBoxLayout.insertWidget(1, content)
        
        # 调整对话框大小
        dialog.resize(500, 400)
        
        # 处理对话框结果
        if dialog.exec():
            name = name_edit.text().strip()
            establishment_date = establishment_date_edit.date().toPyDate()
            village_priest = village_priest_edit.text().strip()
            address = address_edit.text().strip()
            description = description_edit.toPlainText().strip()
            
            if name and village_priest and address:
                db = SessionLocal()
                try:
                    # 自动生成村庄代码
                    import time
                    code = f"V{int(time.time())}"
                    
                    # 保存照片
                    photo_filename = self.save_photo(photo_path)
                    VillageService.create_village(
                        db, 
                        name=name, 
                        code=code, 
                        establishment_date=establishment_date,
                        village_priest=village_priest,
                        address=address,
                        description=description,
                        photo=photo_filename
                    )
                    self.load_villages()
                except IntegrityError:
                    db.rollback()
                    InfoBar.error(
                        title='添加失败',
                        content='村庄代码已存在，请使用其他代码',
                        parent=self,
                        position=InfoBarPosition.TOP
                    )
                except Exception as e:
                    db.rollback()
                    InfoBar.error(
                        title='添加失败',
                        content=f'添加村庄失败: {str(e)}',
                        parent=self,
                        position=InfoBarPosition.TOP
                    )
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
        
        # 新增字段
        establishment_date_edit = QDateEdit()
        establishment_date_edit.setCalendarPopup(True)
        if village.establishment_date:
            establishment_date_edit.setDate(QDate.fromString(str(village.establishment_date), 'yyyy-MM-dd'))
        else:
            establishment_date_edit.setDate(QDate.currentDate())
        layout.addRow('建立日期:', establishment_date_edit)
        
        village_priest_edit = QLineEdit(village.village_priest)
        layout.addRow('村庄神父:', village_priest_edit)
        
        address_edit = QLineEdit(village.address)
        layout.addRow('村庄地址:', address_edit)
        
        description_edit = QTextEdit(village.description or '')
        layout.addRow('村庄简介:', description_edit)
        
        # 照片上传
        photo_layout = QHBoxLayout()
        photo_label = QLabel('暂无图片')
        photo_label.setFixedSize(100, 100)
        photo_label.setStyleSheet('border: 1px solid #ddd;')
        
        # 显示现有照片
        if village.photo:
            print(f"Village photo filename: {village.photo}")
            photo_path = self.get_photo_path(village.photo)
            print(f"Photo path: {photo_path}")
            if photo_path and os.path.exists(photo_path):
                print(f"Photo exists: {os.path.exists(photo_path)}")
                pixmap = QPixmap(photo_path)
                pixmap = pixmap.scaled(100, 100, Qt.KeepAspectRatio)
                photo_label.setPixmap(pixmap)
                photo_label.setText('')
            else:
                print(f"Photo not found: {photo_path}")
        
        photo_layout.addWidget(photo_label)
        
        photo_path = None
        def select_photo():
            nonlocal photo_path
            file_path, _ = QFileDialog.getOpenFileName(self, '选择照片', '', 'Image Files (*.jpg *.jpeg *.png *.bmp)')
            if file_path:
                photo_path = file_path
                pixmap = QPixmap(file_path)
                pixmap = pixmap.scaled(100, 100, Qt.KeepAspectRatio)
                photo_label.setPixmap(pixmap)
                photo_label.setText('')
        
        photo_btn = PushButton('选择照片')
        photo_btn.clicked.connect(select_photo)
        photo_layout.addWidget(photo_btn)
        layout.addRow('村庄照片:', photo_layout)
        
        # 替换对话框内容
        dialog.vBoxLayout.removeWidget(dialog.contentLabel)
        dialog.contentLabel.deleteLater()
        dialog.vBoxLayout.insertWidget(1, content)
        
        # 调整对话框大小
        dialog.resize(500, 400)
        
        # 处理对话框结果
        if dialog.exec():
            name = name_edit.text().strip()
            establishment_date = establishment_date_edit.date().toPyDate()
            village_priest = village_priest_edit.text().strip()
            address = address_edit.text().strip()
            description = description_edit.toPlainText().strip()
            
            if name and village_priest and address:
                db = SessionLocal()
                try:
                    # 保存照片
                    photo_filename = self.save_photo(photo_path) if photo_path else village.photo
                    VillageService.update_village(
                        db, 
                        village.id, 
                        name=name, 
                        establishment_date=establishment_date,
                        village_priest=village_priest,
                        address=address,
                        description=description,
                        photo=photo_filename
                    )
                    self.load_villages()
                except IntegrityError:
                    db.rollback()
                    InfoBar.error(
                        title='修改失败',
                        content='村庄代码已存在，请使用其他代码',
                        parent=self,
                        position=InfoBarPosition.TOP
                    )
                except Exception as e:
                    db.rollback()
                    InfoBar.error(
                        title='修改失败',
                        content=f'修改村庄失败: {str(e)}',
                        parent=self,
                        position=InfoBarPosition.TOP
                    )
                finally:
                    db.close()
    
    def delete_village(self, village):
        db = SessionLocal()
        try:
            # 重新从数据库获取村庄对象，避免DetachedInstanceError
            village_obj = VillageService.get_village_by_id(db, village.id)
            if not village_obj:
                return
            
            # 检查是否有家庭
            if village_obj.households:
                InfoBar.error(
                    title='删除失败',
                    content='该村庄下有家庭，需删除所有家庭后才能删除村庄',
                    parent=self,
                    position=InfoBarPosition.TOP
                )
                return
            
            if VillageService.delete_village(db, village.id):
                self.load_villages()
        finally:
            db.close()