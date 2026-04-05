from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
from PyQt5.QtCore import Qt, pyqtSignal
from src.services.auth_service import AuthService
from src.models import SessionLocal

class LoginView(QWidget):
    login_success = pyqtSignal(object)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('户籍管理系统 - 登录')
        self.setGeometry(100, 100, 400, 300)
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)
        
        # 标题
        title_label = QLabel('户籍管理系统')
        title_label.setStyleSheet('font-size: 24px; font-weight: bold;')
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        # 用户名输入
        username_layout = QHBoxLayout()
        username_label = QLabel('用户名:')
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText('请输入用户名')
        username_layout.addWidget(username_label)
        username_layout.addWidget(self.username_input)
        layout.addLayout(username_layout)
        
        # 密码输入
        password_layout = QHBoxLayout()
        password_label = QLabel('密码:')
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setPlaceholderText('请输入密码')
        password_layout.addWidget(password_label)
        password_layout.addWidget(self.password_input)
        layout.addLayout(password_layout)
        
        # 登录按钮
        self.login_button = QPushButton('登录')
        self.login_button.clicked.connect(self.handle_login)
        layout.addWidget(self.login_button)
        
        self.setLayout(layout)
    
    def handle_login(self):
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()
        
        if not username or not password:
            QMessageBox.warning(self, '提示', '请输入用户名和密码')
            return
        
        # 验证用户
        db = SessionLocal()
        try:
            user = AuthService.authenticate_user(db, username, password)
            if user:
                # 登录成功，发射信号
                self.login_success.emit(user)
                self.close()
            else:
                QMessageBox.warning(self, '提示', '用户名或密码错误')
        except Exception as e:
            QMessageBox.critical(self, '错误', f'登录失败: {str(e)}')
        finally:
            db.close()