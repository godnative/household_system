# -*- coding: utf-8 -*-
"""
登录界面UI定义
使用 PyQt-Fluent-Widgets 实现现代化登录界面
"""

from PyQt5 import QtCore, QtGui, QtWidgets
from qfluentwidgets import (BodyLabel, LineEdit, CheckBox,
                           PrimaryPushButton, TitleLabel)


class Ui_LoginForm(object):
    def setupUi(self, Form):
        Form.setObjectName("LoginForm")
        Form.resize(1000, 650)
        Form.setMinimumSize(QtCore.QSize(800, 500))

        # 主水平布局：左侧背景图，右侧登录表单
        self.horizontalLayout = QtWidgets.QHBoxLayout(Form)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setSpacing(0)
        self.horizontalLayout.setObjectName("horizontalLayout")

        # 左侧背景图片标签
        self.backgroundLabel = QtWidgets.QLabel(parent=Form)
        self.backgroundLabel.setText("")
        self.backgroundLabel.setScaledContents(False)
        self.backgroundLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.backgroundLabel.setObjectName("backgroundLabel")
        # 设置背景颜色（如果没有图片）
        self.backgroundLabel.setStyleSheet("""
            QLabel {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #667eea, stop:1 #764ba2);
            }
        """)
        self.horizontalLayout.addWidget(self.backgroundLabel)

        # 右侧登录表单容器
        self.loginWidget = QtWidgets.QWidget(parent=Form)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Preferred,
            QtWidgets.QSizePolicy.Preferred
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.loginWidget.sizePolicy().hasHeightForWidth()
        )
        self.loginWidget.setSizePolicy(sizePolicy)
        self.loginWidget.setMinimumSize(QtCore.QSize(360, 0))
        self.loginWidget.setMaximumSize(QtCore.QSize(420, 16777215))
        self.loginWidget.setStyleSheet("""
            QWidget {
                background-color: white;
            }
            QLabel {
                font: 13px 'Microsoft YaHei';
            }
        """)
        self.loginWidget.setObjectName("loginWidget")

        # 登录表单垂直布局
        self.verticalLayout = QtWidgets.QVBoxLayout(self.loginWidget)
        self.verticalLayout.setContentsMargins(30, 30, 30, 30)
        self.verticalLayout.setSpacing(12)
        self.verticalLayout.setObjectName("verticalLayout")

        # 顶部弹簧
        spacerItem = QtWidgets.QSpacerItem(
            20, 40,
            QtWidgets.QSizePolicy.Minimum,
            QtWidgets.QSizePolicy.Expanding
        )
        self.verticalLayout.addItem(spacerItem)

        # Logo图标
        self.logoLabel = QtWidgets.QLabel(parent=self.loginWidget)
        self.logoLabel.setMinimumSize(QtCore.QSize(100, 100))
        self.logoLabel.setMaximumSize(QtCore.QSize(100, 100))
        self.logoLabel.setText("")
        self.logoLabel.setScaledContents(True)
        self.logoLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.logoLabel.setObjectName("logoLabel")
        # 设置默认图标（十字架）
        self.logoLabel.setStyleSheet("""
            QLabel {
                background-color: #667eea;
                border-radius: 50px;
                font-size: 48px;
                color: white;
            }
        """)
        self.logoLabel.setText("✟")
        self.verticalLayout.addWidget(
            self.logoLabel, 0, QtCore.Qt.AlignHCenter
        )

        # 小间距
        spacerItem1 = QtWidgets.QSpacerItem(
            20, 20,
            QtWidgets.QSizePolicy.Minimum,
            QtWidgets.QSizePolicy.Fixed
        )
        self.verticalLayout.addItem(spacerItem1)

        # 系统标题
        self.titleLabel = TitleLabel(parent=self.loginWidget)
        self.titleLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.titleLabel.setObjectName("titleLabel")
        self.verticalLayout.addWidget(self.titleLabel)

        # 小间距
        spacerItem2 = QtWidgets.QSpacerItem(
            20, 15,
            QtWidgets.QSizePolicy.Minimum,
            QtWidgets.QSizePolicy.Fixed
        )
        self.verticalLayout.addItem(spacerItem2)

        # 用户名标签
        self.usernameLabel = BodyLabel(parent=self.loginWidget)
        self.usernameLabel.setObjectName("usernameLabel")
        self.verticalLayout.addWidget(self.usernameLabel)

        # 用户名输入框
        self.usernameLineEdit = LineEdit(parent=self.loginWidget)
        self.usernameLineEdit.setClearButtonEnabled(True)
        self.usernameLineEdit.setObjectName("usernameLineEdit")
        self.verticalLayout.addWidget(self.usernameLineEdit)

        # 密码标签
        self.passwordLabel = BodyLabel(parent=self.loginWidget)
        self.passwordLabel.setObjectName("passwordLabel")
        self.verticalLayout.addWidget(self.passwordLabel)

        # 密码输入框
        self.passwordLineEdit = LineEdit(parent=self.loginWidget)
        self.passwordLineEdit.setEchoMode(QtWidgets.QLineEdit.Password)
        self.passwordLineEdit.setClearButtonEnabled(True)
        self.passwordLineEdit.setObjectName("passwordLineEdit")
        self.verticalLayout.addWidget(self.passwordLineEdit)

        # 小间距
        spacerItem3 = QtWidgets.QSpacerItem(
            20, 8,
            QtWidgets.QSizePolicy.Minimum,
            QtWidgets.QSizePolicy.Fixed
        )
        self.verticalLayout.addItem(spacerItem3)

        # 记住密码复选框
        self.rememberCheckBox = CheckBox(parent=self.loginWidget)
        self.rememberCheckBox.setChecked(False)
        self.rememberCheckBox.setObjectName("rememberCheckBox")
        self.verticalLayout.addWidget(self.rememberCheckBox)

        # 小间距
        spacerItem4 = QtWidgets.QSpacerItem(
            20, 8,
            QtWidgets.QSizePolicy.Minimum,
            QtWidgets.QSizePolicy.Fixed
        )
        self.verticalLayout.addItem(spacerItem4)

        # 登录按钮
        self.loginButton = PrimaryPushButton(parent=self.loginWidget)
        self.loginButton.setMinimumHeight(36)
        self.loginButton.setObjectName("loginButton")
        self.verticalLayout.addWidget(self.loginButton)

        # 底部弹簧
        spacerItem5 = QtWidgets.QSpacerItem(
            20, 40,
            QtWidgets.QSizePolicy.Minimum,
            QtWidgets.QSizePolicy.Expanding
        )
        self.verticalLayout.addItem(spacerItem5)

        # 版权信息
        self.copyrightLabel = BodyLabel(parent=self.loginWidget)
        self.copyrightLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.copyrightLabel.setStyleSheet("color: #999; font-size: 11px;")
        self.copyrightLabel.setObjectName("copyrightLabel")
        self.verticalLayout.addWidget(self.copyrightLabel)

        # 将登录表单容器添加到主布局
        self.horizontalLayout.addWidget(self.loginWidget)

        # 设置文本
        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

        # 设置Tab顺序
        Form.setTabOrder(self.usernameLineEdit, self.passwordLineEdit)
        Form.setTabOrder(self.passwordLineEdit, self.rememberCheckBox)
        Form.setTabOrder(self.rememberCheckBox, self.loginButton)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("LoginForm", "天主教教籍管理系统"))
        self.titleLabel.setText(_translate("LoginForm", "天主教教籍管理系统"))
        self.usernameLabel.setText(_translate("LoginForm", "用户名"))
        self.usernameLineEdit.setPlaceholderText(_translate("LoginForm", "请输入用户名"))
        self.passwordLabel.setText(_translate("LoginForm", "密码"))
        self.passwordLineEdit.setPlaceholderText(_translate("LoginForm", "请输入密码"))
        self.rememberCheckBox.setText(_translate("LoginForm", "记住密码"))
        self.loginButton.setText(_translate("LoginForm", "登录"))
        self.copyrightLabel.setText(_translate("LoginForm", "© 2026 天主教教籍管理系统"))
