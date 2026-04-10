"""
系统设置视图
"""
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QFileDialog
from qfluentwidgets import (
    PrimaryPushButton, PushButton, BodyLabel, StrongBodyLabel,
    CardWidget, InfoBar, InfoBarPosition, MessageBox
)
from src.services.database_service import DatabaseService


class SettingsView(QWidget):
    """系统设置视图"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.database_service = DatabaseService()
        self.init_ui()

    def init_ui(self):
        """初始化界面"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)

        # 标题
        title_label = StrongBodyLabel('系统设置', self)
        title_label.setStyleSheet('font-size: 24px; font-weight: bold;')
        layout.addWidget(title_label)

        # 数据库管理卡片
        db_card = self._create_database_card()
        layout.addWidget(db_card)

        # 添加弹簧，保持上部对齐
        layout.addStretch()

    def _create_database_card(self) -> CardWidget:
        """创建数据库管理卡片"""
        card = CardWidget(self)
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(20, 20, 20, 20)
        card_layout.setSpacing(15)

        # 卡片标题
        title_label = StrongBodyLabel('数据库管理', self)
        title_label.setStyleSheet('font-size: 18px; font-weight: bold;')
        card_layout.addWidget(title_label)

        # 数据库信息
        db_info = self.database_service.get_database_info()
        info_layout = QVBoxLayout()
        info_layout.setSpacing(8)

        info_items = [
            ('数据库路径', db_info.get('path', '未知')),
            ('文件大小', db_info.get('size', '未知')),
            ('最后修改', db_info.get('last_modified', '未知')),
        ]

        for label_text, value_text in info_items:
            item_layout = QHBoxLayout()
            label = BodyLabel(f'{label_text}：', self)
            label.setMinimumWidth(100)
            value = BodyLabel(value_text, self)
            value.setTextInteractionFlags(Qt.TextSelectableByMouse)
            item_layout.addWidget(label)
            item_layout.addWidget(value)
            item_layout.addStretch()
            info_layout.addLayout(item_layout)

        card_layout.addLayout(info_layout)

        # 分隔线
        card_layout.addSpacing(10)

        # 操作按钮
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)

        # 导出按钮（打开文件夹）
        export_btn = PrimaryPushButton('导出数据库', self)
        export_btn.setMinimumWidth(120)
        export_btn.clicked.connect(self._on_export_clicked)
        button_layout.addWidget(export_btn)

        # 导入按钮
        import_btn = PushButton('还原数据库', self)
        import_btn.setMinimumWidth(120)
        import_btn.clicked.connect(self._on_import_clicked)
        button_layout.addWidget(import_btn)

        button_layout.addStretch()
        card_layout.addLayout(button_layout)

        # 提示信息
        tip_label = BodyLabel('提示：导出将打开数据库文件夹，您可以手动复制数据库文件；还原将替换当前数据库，原数据库会自动备份。', self)
        tip_label.setStyleSheet('color: #888; font-size: 12px;')
        tip_label.setWordWrap(True)
        card_layout.addWidget(tip_label)

        return card

    def _on_export_clicked(self):
        """导出数据库按钮点击事件"""
        success, message = self.database_service.open_database_folder()

        if success:
            InfoBar.success(
                title='成功',
                content=message,
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=3000,
                parent=self
            )
        else:
            InfoBar.error(
                title='失败',
                content=message,
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=3000,
                parent=self
            )

    def _on_import_clicked(self):
        """导入数据库按钮点击事件"""
        # 弹出确认对话框
        msg_box = MessageBox(
            '确认还原数据库',
            '还原数据库将替换当前数据库，原数据库会自动重命名备份。\n\n是否继续？',
            self
        )

        if msg_box.exec():
            # 打开文件选择对话框
            file_path, _ = QFileDialog.getOpenFileName(
                self,
                '选择数据库文件',
                '',
                'SQLite 数据库文件 (*.db *.sqlite *.sqlite3);;所有文件 (*.*)'
            )

            if file_path:
                # 执行导入
                success, message = self.database_service.import_database(file_path)

                if success:
                    InfoBar.success(
                        title='成功',
                        content=message + '\n请重启应用以使更改生效。',
                        orient=Qt.Horizontal,
                        isClosable=True,
                        position=InfoBarPosition.TOP,
                        duration=5000,
                        parent=self
                    )
                    # 刷新数据库信息显示
                    self.refresh_database_info()
                else:
                    InfoBar.error(
                        title='失败',
                        content=message,
                        orient=Qt.Horizontal,
                        isClosable=True,
                        position=InfoBarPosition.TOP,
                        duration=3000,
                        parent=self
                    )

    def refresh_database_info(self):
        """刷新数据库信息显示"""
        # 重新创建界面以刷新信息
        # 清除当前布局
        layout = self.layout()
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # 重新初始化界面
        self.init_ui()
