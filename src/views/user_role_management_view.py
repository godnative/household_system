"""
用户角色管理视图

根据登录用户的权限显示不同内容：
- 超级管理员：完整的用户和角色管理界面
- 录入员/观察员：个人信息和修改密码界面
"""
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidgetItem,
                             QFormLayout, QLineEdit, QLabel, QDialog, QCheckBox, QScrollArea,
                             QGroupBox, QGridLayout, QComboBox)
from PyQt5.QtCore import Qt
from qfluentwidgets import (PrimaryPushButton, PushButton, TableWidget, Dialog, InfoBar,
                           InfoBarPosition, ComboBox, TabBar, StackedWidget, CardWidget,
                           BodyLabel, StrongBodyLabel, PasswordLineEdit)
from src.services.auth_service import AuthService
from src.services.permission_service import PermissionService
from src.services.village_service import VillageService
from src.models import SessionLocal, User, Role
from src.constants import PERM_USER_MANAGE, PERM_ROLE_MANAGE

class UserRoleManagementView(QWidget):
    """用户角色管理视图"""

    def __init__(self, user, parent=None):
        super().__init__(parent)
        self.user = user

        # 检查用户是否是超级管理员
        self.is_admin = (AuthService.check_permission(user, PERM_USER_MANAGE) or
                        AuthService.check_permission(user, PERM_ROLE_MANAGE))

        self.init_ui()

    def init_ui(self):
        """初始化界面"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)

        # 标题
        title_label = StrongBodyLabel('用户角色管理', self)
        title_label.setStyleSheet('font-size: 24px; font-weight: bold;')
        layout.addWidget(title_label)

        if self.is_admin:
            # 超级管理员：显示完整管理界面
            self._create_admin_view(layout)
        else:
            # 普通用户：显示个人信息界面
            self._create_user_view(layout)

    def _create_admin_view(self, layout):
        """创建超级管理员视图"""
        # 创建标签栏
        self.tab_bar = TabBar(self)
        self.tab_bar.addTab('user_tab', '用户管理')
        self.tab_bar.addTab('role_tab', '角色管理')
        self.tab_bar.setCurrentIndex(0)
        self.tab_bar.currentChanged.connect(self._on_tab_changed)
        layout.addWidget(self.tab_bar)

        # 创建堆叠窗口
        self.stacked_widget = StackedWidget(self)

        # 用户管理页面
        user_page = self._create_user_management_page()
        self.stacked_widget.addWidget(user_page)

        # 角色管理页面
        role_page = self._create_role_management_page()
        self.stacked_widget.addWidget(role_page)

        layout.addWidget(self.stacked_widget)

    def _create_user_view(self, layout):
        """创建普通用户视图（个人信息）"""
        # 创建个人信息卡片
        card = CardWidget(self)
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(20, 20, 20, 20)
        card_layout.setSpacing(15)

        # 卡片标题
        title_label = StrongBodyLabel('我的信息', self)
        title_label.setStyleSheet('font-size: 18px; font-weight: bold;')
        card_layout.addWidget(title_label)

        # 信息显示
        info_layout = QFormLayout()
        info_layout.setSpacing(10)

        # 用户名
        username_label = BodyLabel(self.user.username, self)
        info_layout.addRow('用户名：', username_label)

        # 角色
        role_label = BodyLabel(self.user.role.name if self.user.role else '无', self)
        info_layout.addRow('角色：', role_label)

        # 所属堂区或可访问堂区
        if self.user.village:
            village_label = BodyLabel(self.user.village.name, self)
            info_layout.addRow('所属堂区：', village_label)
        elif self.user.accessible_villages:
            villages_text = ', '.join([v.name for v in self.user.accessible_villages])
            villages_label = BodyLabel(villages_text, self)
            villages_label.setWordWrap(True)
            info_layout.addRow('可访问堂区：', villages_label)

        card_layout.addLayout(info_layout)

        # 修改密码按钮
        change_pwd_btn = PrimaryPushButton('修改密码', self)
        change_pwd_btn.clicked.connect(self._change_own_password)
        card_layout.addWidget(change_pwd_btn)

        layout.addWidget(card)
        layout.addStretch()

    def _on_tab_changed(self, index):
        """标签切换事件"""
        self.stacked_widget.setCurrentIndex(index)

        # 刷新数据
        if index == 0:
            self._load_users()
        elif index == 1:
            self._load_roles()

    def _create_user_management_page(self):
        """创建用户管理页面"""
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 10, 0, 0)

        # 操作按钮
        btn_layout = QHBoxLayout()
        add_user_btn = PrimaryPushButton('添加用户')
        add_user_btn.clicked.connect(self._add_user)
        btn_layout.addWidget(add_user_btn)

        refresh_btn = PushButton('刷新')
        refresh_btn.clicked.connect(self._load_users)
        btn_layout.addWidget(refresh_btn)
        btn_layout.addStretch()
        layout.addLayout(btn_layout)

        # 用户表格
        self.user_table = TableWidget()
        self.user_table.setBorderVisible(True)
        self.user_table.setBorderRadius(8)
        self.user_table.setWordWrap(False)
        self.user_table.setColumnCount(5)
        self.user_table.setHorizontalHeaderLabels(['ID', '用户名', '角色', '所属堂区/可访问堂区', '操作'])
        self.user_table.verticalHeader().hide()
        self.user_table.verticalHeader().setDefaultSectionSize(60)
        layout.addWidget(self.user_table)

        # 加载用户数据
        self._load_users()

        return page

    def _create_role_management_page(self):
        """创建角色管理页面"""
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 10, 0, 0)

        # 操作按钮
        btn_layout = QHBoxLayout()
        add_role_btn = PrimaryPushButton('添加角色')
        add_role_btn.clicked.connect(self._add_role)
        btn_layout.addWidget(add_role_btn)

        refresh_btn = PushButton('刷新')
        refresh_btn.clicked.connect(self._load_roles)
        btn_layout.addWidget(refresh_btn)
        btn_layout.addStretch()
        layout.addLayout(btn_layout)

        # 角色表格
        self.role_table = TableWidget()
        self.role_table.setBorderVisible(True)
        self.role_table.setBorderRadius(8)
        self.role_table.setWordWrap(False)
        self.role_table.setColumnCount(4)
        self.role_table.setHorizontalHeaderLabels(['ID', '角色名', '描述', '操作'])
        self.role_table.verticalHeader().hide()
        self.role_table.verticalHeader().setDefaultSectionSize(60)
        layout.addWidget(self.role_table)

        # 加载角色数据
        self._load_roles()

        return page

    def _load_users(self):
        """加载用户数据"""
        self.user_table.setRowCount(0)

        db = SessionLocal()
        try:
            users = db.query(User).all()
            for i, user in enumerate(users):
                self.user_table.insertRow(i)

                # ID
                self.user_table.setItem(i, 0, QTableWidgetItem(str(user.id)))

                # 用户名
                self.user_table.setItem(i, 1, QTableWidgetItem(user.username))

                # 角色
                role_name = user.role.name if user.role else '无'
                self.user_table.setItem(i, 2, QTableWidgetItem(role_name))

                # 所属堂区/可访问堂区
                if user.village:
                    village_info = user.village.name
                elif user.accessible_villages:
                    village_info = ', '.join([v.name for v in user.accessible_villages[:3]])
                    if len(user.accessible_villages) > 3:
                        village_info += f'等{len(user.accessible_villages)}个'
                else:
                    village_info = '全部' if role_name == '超级管理员' else '无'
                self.user_table.setItem(i, 3, QTableWidgetItem(village_info))

                # 操作按钮
                btn_widget = QWidget()
                btn_layout = QHBoxLayout(btn_widget)
                btn_layout.setContentsMargins(5, 5, 5, 5)
                btn_layout.setSpacing(5)

                edit_btn = PushButton('编辑')
                edit_btn.clicked.connect(lambda _, u=user: self._edit_user(u))
                btn_layout.addWidget(edit_btn)

                # 不能删除自己
                if user.id != self.user.id:
                    delete_btn = PushButton('删除')
                    delete_btn.clicked.connect(lambda _, u=user: self._delete_user(u))
                    btn_layout.addWidget(delete_btn)

                btn_layout.addStretch()
                self.user_table.setCellWidget(i, 4, btn_widget)

            self.user_table.resizeColumnsToContents()
        finally:
            db.close()

    def _load_roles(self):
        """加载角色数据"""
        self.role_table.setRowCount(0)

        db = SessionLocal()
        try:
            roles = PermissionService.get_all_roles(db)
            for i, role in enumerate(roles):
                self.role_table.insertRow(i)

                # ID
                self.role_table.setItem(i, 0, QTableWidgetItem(str(role.id)))

                # 角色名
                self.role_table.setItem(i, 1, QTableWidgetItem(role.name))

                # 描述
                description = role.description if role.description else '无'
                self.role_table.setItem(i, 2, QTableWidgetItem(description))

                # 操作按钮
                btn_widget = QWidget()
                btn_layout = QHBoxLayout(btn_widget)
                btn_layout.setContentsMargins(5, 5, 5, 5)
                btn_layout.setSpacing(5)

                view_perm_btn = PushButton('查看权限')
                view_perm_btn.clicked.connect(lambda _, r=role: self._view_role_permissions(r))
                btn_layout.addWidget(view_perm_btn)

                edit_btn = PushButton('编辑')
                edit_btn.clicked.connect(lambda _, r=role: self._edit_role(r))
                btn_layout.addWidget(edit_btn)

                # 检查是否有用户使用该角色
                user_count = db.query(User).filter(User.role_id == role.id).count()
                if user_count == 0:
                    delete_btn = PushButton('删除')
                    delete_btn.clicked.connect(lambda _, r=role: self._delete_role(r))
                    btn_layout.addWidget(delete_btn)

                btn_layout.addStretch()
                self.role_table.setCellWidget(i, 3, btn_widget)

            self.role_table.resizeColumnsToContents()
        finally:
            db.close()

    def _add_user(self):
        """添加用户对话框"""
        dialog = Dialog('添加用户', '请输入新用户信息', self)

        # 创建内容
        content = QWidget()
        layout = QFormLayout(content)

        # 用户名
        username_edit = QLineEdit()
        layout.addRow('用户名:', username_edit)

        # 密码
        password_edit = PasswordLineEdit()
        layout.addRow('密码:', password_edit)

        # 确认密码
        confirm_pwd_edit = PasswordLineEdit()
        layout.addRow('确认密码:', confirm_pwd_edit)

        # 角色选择
        role_combo = ComboBox()
        db = SessionLocal()
        try:
            roles = PermissionService.get_all_roles(db)
            for role in roles:
                role_combo.addItem(role.name, role.id)
        finally:
            db.close()
        layout.addRow('角色:', role_combo)

        # 所属堂区（录入员）
        village_combo = ComboBox()
        village_combo.addItem('无', None)
        db = SessionLocal()
        try:
            villages = VillageService.get_all_villages(db)
            for village in villages:
                village_combo.addItem(village.name, village.id)
        finally:
            db.close()
        layout.addRow('所属堂区（录入员）:', village_combo)

        # 可访问堂区（观察员） - 使用多选列表
        accessible_villages_label = QLabel('可访问堂区（观察员）:')
        accessible_villages_scroll = QScrollArea()
        accessible_villages_widget = QWidget()
        accessible_villages_layout = QVBoxLayout(accessible_villages_widget)
        accessible_villages_checkboxes = []

        db = SessionLocal()
        try:
            villages = VillageService.get_all_villages(db)
            for village in villages:
                checkbox = QCheckBox(village.name)
                checkbox.setProperty('village_id', village.id)
                accessible_villages_checkboxes.append(checkbox)
                accessible_villages_layout.addWidget(checkbox)
        finally:
            db.close()

        accessible_villages_scroll.setWidget(accessible_villages_widget)
        accessible_villages_scroll.setMaximumHeight(150)
        accessible_villages_scroll.setWidgetResizable(True)
        layout.addRow(accessible_villages_label, accessible_villages_scroll)

        # 替换对话框内容
        dialog.vBoxLayout.removeWidget(dialog.contentLabel)
        dialog.contentLabel.deleteLater()
        dialog.vBoxLayout.insertWidget(1, content)

        dialog.resize(500, 600)

        if dialog.exec():
            username = username_edit.text().strip()
            password = password_edit.text()
            confirm_pwd = confirm_pwd_edit.text()
            role_id = role_combo.currentData()
            village_id = village_combo.currentData()

            # 验证输入
            if not username:
                InfoBar.error(title='错误', content='用户名不能为空', parent=self,
                            position=InfoBarPosition.TOP)
                return

            if not password:
                InfoBar.error(title='错误', content='密码不能为空', parent=self,
                            position=InfoBarPosition.TOP)
                return

            if password != confirm_pwd:
                InfoBar.error(title='错误', content='两次输入的密码不一致', parent=self,
                            position=InfoBarPosition.TOP)
                return

            if not role_id:
                InfoBar.error(title='错误', content='请选择角色', parent=self,
                            position=InfoBarPosition.TOP)
                return

            # 获取选中的可访问堂区
            accessible_village_ids = [cb.property('village_id')
                                     for cb in accessible_villages_checkboxes if cb.isChecked()]

            # 创建用户
            db = SessionLocal()
            try:
                # 检查用户名是否已存在
                if AuthService.get_user_by_username(db, username):
                    InfoBar.error(title='错误', content='用户名已存在', parent=self,
                                position=InfoBarPosition.TOP)
                    return

                # 创建用户
                new_user = AuthService.create_user(db, username, password, role_id, village_id)

                # 如果有可访问堂区，分配给用户
                if accessible_village_ids:
                    PermissionService.assign_villages_to_user(db, new_user.id, accessible_village_ids)

                InfoBar.success(title='成功', content=f'用户 {username} 创建成功', parent=self,
                              position=InfoBarPosition.TOP)
                self._load_users()
            except Exception as e:
                db.rollback()
                InfoBar.error(title='错误', content=f'创建用户失败: {str(e)}', parent=self,
                            position=InfoBarPosition.TOP)
            finally:
                db.close()

    def _edit_user(self, user):
        """编辑用户对话框"""
        dialog = Dialog('编辑用户', f'编辑用户: {user.username}', self)

        # 重新从数据库获取用户对象（避免DetachedInstanceError）
        db = SessionLocal()
        try:
            user = db.query(User).filter(User.id == user.id).first()
            if not user:
                return

            # 创建内容
            content = QWidget()
            layout = QFormLayout(content)

            # 用户名（只读）
            username_label = QLabel(user.username)
            layout.addRow('用户名:', username_label)

            # 角色选择
            role_combo = ComboBox()
            roles = PermissionService.get_all_roles(db)
            for role in roles:
                role_combo.addItem(role.name, role.id)
                if user.role_id == role.id:
                    role_combo.setCurrentIndex(role_combo.count() - 1)
            layout.addRow('角色:', role_combo)

            # 所属堂区（录入员）
            village_combo = ComboBox()
            village_combo.addItem('无', None)
            villages = VillageService.get_all_villages(db)
            for village in villages:
                village_combo.addItem(village.name, village.id)
                if user.village_id == village.id:
                    village_combo.setCurrentIndex(village_combo.count() - 1)
            layout.addRow('所属堂区（录入员）:', village_combo)

            # 可访问堂区（观察员）
            accessible_villages_label = QLabel('可访问堂区（观察员）:')
            accessible_villages_scroll = QScrollArea()
            accessible_villages_widget = QWidget()
            accessible_villages_layout = QVBoxLayout(accessible_villages_widget)
            accessible_villages_checkboxes = []

            user_accessible_ids = [v.id for v in user.accessible_villages]
            villages = VillageService.get_all_villages(db)
            for village in villages:
                checkbox = QCheckBox(village.name)
                checkbox.setProperty('village_id', village.id)
                if village.id in user_accessible_ids:
                    checkbox.setChecked(True)
                accessible_villages_checkboxes.append(checkbox)
                accessible_villages_layout.addWidget(checkbox)

            accessible_villages_scroll.setWidget(accessible_villages_widget)
            accessible_villages_scroll.setMaximumHeight(150)
            accessible_villages_scroll.setWidgetResizable(True)
            layout.addRow(accessible_villages_label, accessible_villages_scroll)

            # 重置密码选项
            reset_pwd_checkbox = QCheckBox('重置密码')
            layout.addRow('', reset_pwd_checkbox)

            new_password_edit = PasswordLineEdit()
            new_password_edit.setEnabled(False)
            layout.addRow('新密码:', new_password_edit)

            reset_pwd_checkbox.stateChanged.connect(
                lambda state: new_password_edit.setEnabled(state == Qt.Checked)
            )

            # 替换对话框内容
            dialog.vBoxLayout.removeWidget(dialog.contentLabel)
            dialog.contentLabel.deleteLater()
            dialog.vBoxLayout.insertWidget(1, content)

            dialog.resize(500, 650)

            if dialog.exec():
                role_id = role_combo.currentData()
                village_id = village_combo.currentData()
                accessible_village_ids = [cb.property('village_id')
                                         for cb in accessible_villages_checkboxes if cb.isChecked()]

                # 更新用户
                try:
                    kwargs = {
                        'role_id': role_id,
                        'village_id': village_id
                    }

                    # 如果需要重置密码
                    if reset_pwd_checkbox.isChecked():
                        new_password = new_password_edit.text()
                        if not new_password:
                            InfoBar.error(title='错误', content='请输入新密码', parent=self,
                                        position=InfoBarPosition.TOP)
                            return
                        kwargs['password'] = new_password

                    AuthService.update_user(db, user.id, **kwargs)

                    # 更新可访问堂区
                    PermissionService.assign_villages_to_user(db, user.id, accessible_village_ids)

                    InfoBar.success(title='成功', content=f'用户 {user.username} 更新成功',
                                  parent=self, position=InfoBarPosition.TOP)
                    self._load_users()
                except Exception as e:
                    db.rollback()
                    InfoBar.error(title='错误', content=f'更新用户失败: {str(e)}', parent=self,
                                position=InfoBarPosition.TOP)
        finally:
            db.close()

    def _delete_user(self, user):
        """删除用户"""
        dialog = Dialog('确认删除', f'确定要删除用户 {user.username} 吗？\n\n此操作不可恢复。', self)

        if dialog.exec():
            db = SessionLocal()
            try:
                if AuthService.delete_user(db, user.id):
                    InfoBar.success(title='成功', content=f'用户 {user.username} 已删除',
                                  parent=self, position=InfoBarPosition.TOP)
                    self._load_users()
                else:
                    InfoBar.error(title='错误', content='删除用户失败', parent=self,
                                position=InfoBarPosition.TOP)
            finally:
                db.close()

    def _add_role(self):
        """添加角色对话框"""
        dialog = Dialog('添加角色', '请输入新角色信息', self)

        # 创建内容
        content = QWidget()
        layout = QVBoxLayout(content)

        # 角色名
        form_layout = QFormLayout()
        name_edit = QLineEdit()
        form_layout.addRow('角色名:', name_edit)

        # 描述
        description_edit = QLineEdit()
        form_layout.addRow('描述:', description_edit)

        layout.addLayout(form_layout)

        # 权限选择
        perm_label = QLabel('权限:')
        layout.addWidget(perm_label)

        perm_scroll = QScrollArea()
        perm_widget = QWidget()
        perm_layout = QVBoxLayout(perm_widget)
        perm_checkboxes = []

        db = SessionLocal()
        try:
            permissions = PermissionService.get_all_permissions(db)
            for perm in permissions:
                checkbox = QCheckBox(f'{perm.description} ({perm.name})')
                checkbox.setProperty('permission_id', perm.id)
                perm_checkboxes.append(checkbox)
                perm_layout.addWidget(checkbox)
        finally:
            db.close()

        perm_scroll.setWidget(perm_widget)
        perm_scroll.setMaximumHeight(200)
        perm_scroll.setWidgetResizable(True)
        layout.addWidget(perm_scroll)

        # 替换对话框内容
        dialog.vBoxLayout.removeWidget(dialog.contentLabel)
        dialog.contentLabel.deleteLater()
        dialog.vBoxLayout.insertWidget(1, content)

        dialog.resize(500, 500)

        if dialog.exec():
            name = name_edit.text().strip()
            description = description_edit.text().strip()

            if not name:
                InfoBar.error(title='错误', content='角色名不能为空', parent=self,
                            position=InfoBarPosition.TOP)
                return

            # 获取选中的权限
            permission_ids = [cb.property('permission_id')
                            for cb in perm_checkboxes if cb.isChecked()]

            # 创建角色
            db = SessionLocal()
            try:
                new_role = PermissionService.create_role(db, name, description)

                # 分配权限
                if permission_ids:
                    PermissionService.assign_permissions_to_role(db, new_role.id, permission_ids)

                InfoBar.success(title='成功', content=f'角色 {name} 创建成功', parent=self,
                              position=InfoBarPosition.TOP)
                self._load_roles()
            except Exception as e:
                db.rollback()
                InfoBar.error(title='错误', content=f'创建角色失败: {str(e)}', parent=self,
                            position=InfoBarPosition.TOP)
            finally:
                db.close()

    def _edit_role(self, role):
        """编辑角色对话框"""
        dialog = Dialog('编辑角色', f'编辑角色: {role.name}', self)

        db = SessionLocal()
        try:
            role = PermissionService.get_role_by_id(db, role.id)
            if not role:
                return

            # 创建内容
            content = QWidget()
            layout = QVBoxLayout(content)

            # 角色名和描述
            form_layout = QFormLayout()
            name_edit = QLineEdit(role.name)
            form_layout.addRow('角色名:', name_edit)

            description_edit = QLineEdit(role.description if role.description else '')
            form_layout.addRow('描述:', description_edit)

            layout.addLayout(form_layout)

            # 权限选择
            perm_label = QLabel('权限:')
            layout.addWidget(perm_label)

            perm_scroll = QScrollArea()
            perm_widget = QWidget()
            perm_layout = QVBoxLayout(perm_widget)
            perm_checkboxes = []

            role_perm_ids = [p.id for p in role.permissions]
            permissions = PermissionService.get_all_permissions(db)
            for perm in permissions:
                checkbox = QCheckBox(f'{perm.description} ({perm.name})')
                checkbox.setProperty('permission_id', perm.id)
                if perm.id in role_perm_ids:
                    checkbox.setChecked(True)
                perm_checkboxes.append(checkbox)
                perm_layout.addWidget(checkbox)

            perm_scroll.setWidget(perm_widget)
            perm_scroll.setMaximumHeight(200)
            perm_scroll.setWidgetResizable(True)
            layout.addWidget(perm_scroll)

            # 替换对话框内容
            dialog.vBoxLayout.removeWidget(dialog.contentLabel)
            dialog.contentLabel.deleteLater()
            dialog.vBoxLayout.insertWidget(1, content)

            dialog.resize(500, 500)

            if dialog.exec():
                name = name_edit.text().strip()
                description = description_edit.text().strip()

                if not name:
                    InfoBar.error(title='错误', content='角色名不能为空', parent=self,
                                position=InfoBarPosition.TOP)
                    return

                # 获取选中的权限
                permission_ids = [cb.property('permission_id')
                                for cb in perm_checkboxes if cb.isChecked()]

                # 更新角色
                try:
                    PermissionService.update_role(db, role.id, name=name, description=description)
                    PermissionService.assign_permissions_to_role(db, role.id, permission_ids)

                    InfoBar.success(title='成功', content=f'角色 {name} 更新成功', parent=self,
                                  position=InfoBarPosition.TOP)
                    self._load_roles()
                except Exception as e:
                    db.rollback()
                    InfoBar.error(title='错误', content=f'更新角色失败: {str(e)}', parent=self,
                                position=InfoBarPosition.TOP)
        finally:
            db.close()

    def _delete_role(self, role):
        """删除角色"""
        dialog = Dialog('确认删除', f'确定要删除角色 {role.name} 吗？\n\n此操作不可恢复。', self)

        if dialog.exec():
            db = SessionLocal()
            try:
                if PermissionService.delete_role(db, role.id):
                    InfoBar.success(title='成功', content=f'角色 {role.name} 已删除', parent=self,
                                  position=InfoBarPosition.TOP)
                    self._load_roles()
                else:
                    InfoBar.error(title='错误', content='删除角色失败', parent=self,
                                position=InfoBarPosition.TOP)
            finally:
                db.close()

    def _view_role_permissions(self, role):
        """查看角色权限"""
        db = SessionLocal()
        try:
            role = PermissionService.get_role_by_id(db, role.id)
            if not role:
                return

            perm_names = [f'• {p.description} ({p.name})' for p in role.permissions]
            perm_text = '\n'.join(perm_names) if perm_names else '该角色没有任何权限'

            dialog = Dialog('角色权限', f'角色 {role.name} 的权限：\n\n{perm_text}', self)
            dialog.exec()
        finally:
            db.close()

    def _change_own_password(self):
        """修改自己的密码"""
        dialog = Dialog('修改密码', '请输入密码信息', self)

        # 创建内容
        content = QWidget()
        layout = QFormLayout(content)

        # 旧密码
        old_pwd_edit = PasswordLineEdit()
        layout.addRow('旧密码:', old_pwd_edit)

        # 新密码
        new_pwd_edit = PasswordLineEdit()
        layout.addRow('新密码:', new_pwd_edit)

        # 确认新密码
        confirm_pwd_edit = PasswordLineEdit()
        layout.addRow('确认新密码:', confirm_pwd_edit)

        # 替换对话框内容
        dialog.vBoxLayout.removeWidget(dialog.contentLabel)
        dialog.contentLabel.deleteLater()
        dialog.vBoxLayout.insertWidget(1, content)

        dialog.resize(400, 300)

        if dialog.exec():
            old_password = old_pwd_edit.text()
            new_password = new_pwd_edit.text()
            confirm_password = confirm_pwd_edit.text()

            # 验证输入
            if not old_password:
                InfoBar.error(title='错误', content='请输入旧密码', parent=self,
                            position=InfoBarPosition.TOP)
                return

            if not new_password:
                InfoBar.error(title='错误', content='请输入新密码', parent=self,
                            position=InfoBarPosition.TOP)
                return

            if new_password != confirm_password:
                InfoBar.error(title='错误', content='两次输入的新密码不一致', parent=self,
                            position=InfoBarPosition.TOP)
                return

            # 验证旧密码
            if not AuthService.verify_password(old_password, self.user.password_hash):
                InfoBar.error(title='错误', content='旧密码不正确', parent=self,
                            position=InfoBarPosition.TOP)
                return

            # 更新密码
            db = SessionLocal()
            try:
                AuthService.update_user(db, self.user.id, password=new_password)

                InfoBar.success(title='成功', content='密码修改成功，请重新登录', parent=self,
                              position=InfoBarPosition.TOP, duration=3000)

                # 更新当前用户对象的密码哈希
                self.user.password_hash = AuthService.get_password_hash(new_password)
            except Exception as e:
                db.rollback()
                InfoBar.error(title='错误', content=f'修改密码失败: {str(e)}', parent=self,
                            position=InfoBarPosition.TOP)
            finally:
                db.close()
