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
        # 主布局改为水平布局
        main_layout = QHBoxLayout(self)
        
        # 左侧布局（堂区列表）
        left_layout = QVBoxLayout()
        
        # 标题
        title_label = QLabel('堂区管理')
        title_label.setStyleSheet('font-size: 18px; font-weight: bold;')
        left_layout.addWidget(title_label)

        # 操作按钮
        btn_layout = QHBoxLayout()
        add_btn = PrimaryPushButton('添加堂区')
        add_btn.clicked.connect(self.add_village)
        btn_layout.addWidget(add_btn)
        
        refresh_btn = PushButton('刷新')
        refresh_btn.clicked.connect(self.load_villages)
        btn_layout.addWidget(refresh_btn)
        
        left_layout.addLayout(btn_layout)
        
        # 表格
        self.table = TableWidget()
        self.table.setBorderVisible(True)
        self.table.setBorderRadius(8)
        self.table.setWordWrap(False)
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(['ID', '堂区名称', '操作'])
        self.table.verticalHeader().hide()
        # 设置行高
        self.table.verticalHeader().setDefaultSectionSize(60)
        left_layout.addWidget(self.table)
        
        # 连接表格选择事件
        self.table.itemSelectionChanged.connect(self.on_village_selected)
        
        # 右侧布局（详细信息）
        right_layout = QVBoxLayout()
        
        # 详细信息标题
        detail_title = QLabel('堂区详细信息')
        detail_title.setStyleSheet('font-size: 16px; font-weight: bold;')
        right_layout.addWidget(detail_title)
        
        # 详细信息内容
        self.detail_widget = QWidget()
        self.detail_layout = QFormLayout(self.detail_widget)
        
        # 堂区名称
        self.name_label = QLabel()
        self.name_label.setStyleSheet('font-weight: 500;')
        self.detail_layout.addRow('堂区名称:', self.name_label)

        # 建立日期
        self.establishment_date_label = QLabel()
        self.establishment_date_label.setStyleSheet('font-weight: 500;')
        self.detail_layout.addRow('建立日期:', self.establishment_date_label)

        # 堂区神父
        self.village_priest_label = QLabel()
        self.village_priest_label.setStyleSheet('font-weight: 500;')
        self.detail_layout.addRow('堂区神父:', self.village_priest_label)

        # 堂区地址
        self.address_label = QLabel()
        self.address_label.setStyleSheet('font-weight: 500;')
        self.address_label.setWordWrap(True)
        self.detail_layout.addRow('堂区地址:', self.address_label)

        # 堂区简介
        self.description_label = QLabel()
        self.description_label.setStyleSheet('font-weight: 500;')
        self.description_label.setWordWrap(True)
        self.description_label.setMinimumHeight(80)
        self.detail_layout.addRow('堂区简介:', self.description_label)

        # 堂区照片
        self.photo_label = QLabel('暂无图片')
        self.photo_label.setFixedSize(200, 200)
        self.photo_label.setStyleSheet('border: 1px solid #ddd;')
        self.photo_label.setAlignment(Qt.AlignCenter)
        self.detail_layout.addRow('堂区照片:', self.photo_label)
        
        # 初始状态下禁用详细信息
        self.detail_widget.setEnabled(False)
        
        right_layout.addWidget(self.detail_widget)
        right_layout.addStretch()
        
        # 添加左右布局到主布局
        main_layout.addLayout(left_layout, 1)
        main_layout.addLayout(right_layout, 1)
    
    def load_villages(self):
        # 清空表格
        self.table.setRowCount(0)
        
        # 加载堂区数据
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
    
    def on_village_selected(self):
        """处理堂区选择事件，更新详细信息"""
        selected_items = self.table.selectedItems()
        if not selected_items:
            # 无选择时清空详细信息
            self.clear_detail_info()
            self.detail_widget.setEnabled(False)
            return
        
        # 获取选中的堂区ID
        selected_row = selected_items[0].row()
        village_id = int(self.table.item(selected_row, 0).text())

        # 从数据库获取堂区详情
        db = SessionLocal()
        try:
            village = VillageService.get_village_by_id(db, village_id)
            if village:
                # 更新详细信息
                self.name_label.setText(village.name)
                self.establishment_date_label.setText(str(village.establishment_date))
                self.village_priest_label.setText(village.village_priest)
                self.address_label.setText(village.address)
                self.description_label.setText(village.description or '无')
                
                # 更新照片
                if village.photo:
                    photo_path = self.get_photo_path(village.photo)
                    if photo_path and os.path.exists(photo_path):
                        pixmap = QPixmap(photo_path)
                        pixmap = pixmap.scaled(200, 200, Qt.KeepAspectRatio)
                        self.photo_label.setPixmap(pixmap)
                        self.photo_label.setText('')
                    else:
                        self.photo_label.setText('暂无图片')
                else:
                    self.photo_label.setText('暂无图片')
                
                # 启用详细信息面板
                self.detail_widget.setEnabled(True)
            else:
                self.clear_detail_info()
                self.detail_widget.setEnabled(False)
        finally:
            db.close()
    
    def clear_detail_info(self):
        """清空详细信息"""
        self.name_label.setText('')
        self.establishment_date_label.setText('')
        self.village_priest_label.setText('')
        self.address_label.setText('')
        self.description_label.setText('')
        self.photo_label.setText('暂无图片')
        self.photo_label.clear()
        self.photo_label.setText('暂无图片')
    
    def add_village(self):
        # 创建对话框
        dialog = Dialog('添加堂区', '请输入堂区信息', self)

        # 创建内容 widget
        content = QWidget()
        layout = QFormLayout(content)

        name_edit = QLineEdit()
        layout.addRow('堂区名称:', name_edit)

        # 新增字段
        establishment_date_edit = QDateEdit()
        establishment_date_edit.setCalendarPopup(True)
        establishment_date_edit.setDate(QDate.currentDate())
        layout.addRow('建立日期:', establishment_date_edit)

        village_priest_edit = QLineEdit()
        layout.addRow('堂区神父:', village_priest_edit)

        address_edit = QLineEdit()
        layout.addRow('堂区地址:', address_edit)

        description_edit = QTextEdit()
        layout.addRow('堂区简介:', description_edit)
        
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
        layout.addRow('堂区照片:', photo_layout)
        
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
                    # 自动生成堂区代码
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
                        content='堂区代码已存在，请使用其他代码',
                        parent=self,
                        position=InfoBarPosition.TOP
                    )
                except Exception as e:
                    db.rollback()
                    InfoBar.error(
                        title='添加失败',
                        content=f'添加堂区失败: {str(e)}',
                        parent=self,
                        position=InfoBarPosition.TOP
                    )
                finally:
                    db.close()
    
    def edit_village(self, village):
        # 创建对话框
        dialog = Dialog('编辑堂区', '请修改堂区信息', self)

        # 创建内容 widget
        content = QWidget()
        layout = QFormLayout(content)

        name_edit = QLineEdit(village.name)
        layout.addRow('堂区名称:', name_edit)

        # 新增字段
        establishment_date_edit = QDateEdit()
        establishment_date_edit.setCalendarPopup(True)
        if village.establishment_date:
            establishment_date_edit.setDate(QDate.fromString(str(village.establishment_date), 'yyyy-MM-dd'))
        else:
            establishment_date_edit.setDate(QDate.currentDate())
        layout.addRow('建立日期:', establishment_date_edit)

        village_priest_edit = QLineEdit(village.village_priest)
        layout.addRow('堂区神父:', village_priest_edit)

        address_edit = QLineEdit(village.address)
        layout.addRow('堂区地址:', address_edit)

        description_edit = QTextEdit(village.description or '')
        layout.addRow('堂区简介:', description_edit)
        
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
        layout.addRow('堂区照片:', photo_layout)
        
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
                        content='堂区代码已存在，请使用其他代码',
                        parent=self,
                        position=InfoBarPosition.TOP
                    )
                except Exception as e:
                    db.rollback()
                    InfoBar.error(
                        title='修改失败',
                        content=f'修改堂区失败: {str(e)}',
                        parent=self,
                        position=InfoBarPosition.TOP
                    )
                finally:
                    db.close()
    
    def delete_village(self, village):
        db = SessionLocal()
        try:
            # 重新从数据库获取堂区对象，避免DetachedInstanceError
            village_obj = VillageService.get_village_by_id(db, village.id)
            if not village_obj:
                return

            # 检查是否有家庭
            if village_obj.households:
                InfoBar.error(
                    title='删除失败',
                    content='该堂区下有家庭，需删除所有家庭后才能删除堂区',
                    parent=self,
                    position=InfoBarPosition.TOP
                )
                return

            if VillageService.delete_village(db, village.id):
                self.load_villages()
        finally:
            db.close()