from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTextEdit, QLabel, QApplication
from PyQt5.QtCore import Qt
import sys


class QTextEditHtmlTableTest(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # 标题
        title_label = QLabel('QTextEdit HTML 表格渲染测试')
        title_label.setStyleSheet('font-size: 16px; font-weight: bold;')
        layout.addWidget(title_label)
        
        # 按钮布局
        button_layout = QHBoxLayout()
        
        # 测试家庭信息表格
        test_household_btn = QPushButton('测试家庭信息表格')
        test_household_btn.clicked.connect(self.test_household_table)
        button_layout.addWidget(test_household_btn)
        
        # 测试成员信息表格
        test_member_btn = QPushButton('测试成员信息表格')
        test_member_btn.clicked.connect(self.test_member_table)
        button_layout.addWidget(test_member_btn)
        
        # 测试样式表格
        test_style_btn = QPushButton('测试样式表格')
        test_style_btn.clicked.connect(self.test_style_table)
        button_layout.addWidget(test_style_btn)
        
        layout.addLayout(button_layout)
        
        # QTextEdit 组件
        self.text_edit = QTextEdit()
        self.text_edit.setMinimumHeight(500)
        self.text_edit.setReadOnly(True)
        layout.addWidget(self.text_edit)
        
        # 设置窗口大小
        self.resize(900, 700)
        self.setWindowTitle('QTextEdit HTML 表格测试')
    
    def test_household_table(self):
        """测试家庭信息表格"""
        html = '''
        <h1 style="text-align: center; color: #333;">家庭信息表格</h1>
        
        <table border="1" cellpadding="8" cellspacing="0" style="width: 100%; border-collapse: collapse; font-family: Arial, sans-serif;">
            <tr bgcolor="#4CAF50" style="color: white;">
                <th style="text-align: left;">家庭编号</th>
                <th style="text-align: left;">户主</th>
                <th style="text-align: left;">片号</th>
                <th style="text-align: left;">家庭住址</th>
                <th style="text-align: left;">电话</th>
            </tr>
            <tr bgcolor="#f8f9fa">
                <td>HH001</td>
                <td>张三</td>
                <td>1</td>
                <td>幸福村1组1号</td>
                <td>13800138001</td>
            </tr>
            <tr bgcolor="#ffffff">
                <td>HH002</td>
                <td>李四</td>
                <td>2</td>
                <td>幸福村2组2号</td>
                <td>13900139002</td>
            </tr>
            <tr bgcolor="#f8f9fa">
                <td>HH003</td>
                <td>王五</td>
                <td>1</td>
                <td>幸福村1组3号</td>
                <td>13700137003</td>
            </tr>
            <tr bgcolor="#ffffff">
                <td>HH004</td>
                <td>赵六</td>
                <td>3</td>
                <td>幸福村3组4号</td>
                <td>13600136004</td>
            </tr>
        </table>
        '''
        self.text_edit.setHtml(html)
    
    def test_member_table(self):
        """测试成员信息表格"""
        html = '''
        <h1 style="text-align: center; color: #333;">家庭成员信息表格</h1>
        
        <table border="1" cellpadding="8" cellspacing="0" style="width: 100%; border-collapse: collapse; font-family: Arial, sans-serif;">
            <tr bgcolor="#2196F3" style="color: white;">
                <th style="text-align: center; width: 5%;">序号</th>
                <th style="text-align: left; width: 15%;">姓名</th>
                <th style="text-align: center; width: 10%;">性别</th>
                <th style="text-align: center; width: 15%;">圣名</th>
                <th style="text-align: left; width: 15%;">与户主关系</th>
                <th style="text-align: left; width: 15%;">文化程度</th>
                <th style="text-align: left; width: 25%;">从事职业</th>
            </tr>
            <tr bgcolor="#f0f8ff">
                <td style="text-align: center;">1</td>
                <td>张三</td>
                <td style="text-align: center;">男</td>
                <td style="text-align: center;">若瑟</td>
                <td>户主</td>
                <td>高中</td>
                <td>教师</td>
            </tr>
            <tr bgcolor="#ffffff">
                <td style="text-align: center;">2</td>
                <td>李四</td>
                <td style="text-align: center;">女</td>
                <td style="text-align: center;">玛利亚</td>
                <td>配偶</td>
                <td>大学</td>
                <td>医生</td>
            </tr>
            <tr bgcolor="#f0f8ff">
                <td style="text-align: center;">3</td>
                <td>张小明</td>
                <td style="text-align: center;">男</td>
                <td style="text-align: center;">保禄</td>
                <td>子女</td>
                <td>小学</td>
                <td>学生</td>
            </tr>
            <tr bgcolor="#ffffff">
                <td style="text-align: center;">4</td>
                <td>张父</td>
                <td style="text-align: center;">男</td>
                <td style="text-align: center;">伯多禄</td>
                <td>父母</td>
                <td>初中</td>
                <td>退休</td>
            </tr>
        </table>
        '''
        self.text_edit.setHtml(html)
    
    def test_style_table(self):
        """测试样式表格"""
        html = '''
        <h1 style="text-align: center; color: #333;">样式表格测试</h1>
        
        <table border="1" cellpadding="10" cellspacing="0" style="width: 100%; border-collapse: collapse; font-family: Arial, sans-serif; font-size: 14px;">
            <tr bgcolor="#9C27B0" style="color: white; font-weight: bold;">
                <th style="text-align: left; padding: 12px;">项目</th>
                <th style="text-align: left; padding: 12px;">描述</th>
                <th style="text-align: center; padding: 12px;">状态</th>
                <th style="text-align: right; padding: 12px;">数值</th>
            </tr>
            <tr bgcolor="#f3e5f5" style="hover: background-color: #e1bee7;">
                <td style="padding: 10px; border: 1px solid #ddd;">项目1</td>
                <td style="padding: 10px; border: 1px solid #ddd;">这是一个测试项目</td>
                <td style="padding: 10px; border: 1px solid #ddd; text-align: center;"><span style="background-color: #4CAF50; color: white; padding: 4px 8px; border-radius: 4px;">完成</span></td>
                <td style="padding: 10px; border: 1px solid #ddd; text-align: right;">100</td>
            </tr>
            <tr bgcolor="#ffffff">
                <td style="padding: 10px; border: 1px solid #ddd;">项目2</td>
                <td style="padding: 10px; border: 1px solid #ddd;">这是另一个测试项目</td>
                <td style="padding: 10px; border: 1px solid #ddd; text-align: center;"><span style="background-color: #FFC107; color: black; padding: 4px 8px; border-radius: 4px;">进行中</span></td>
                <td style="padding: 10px; border: 1px solid #ddd; text-align: right;">50</td>
            </tr>
            <tr bgcolor="#f3e5f5">
                <td style="padding: 10px; border: 1px solid #ddd;">项目3</td>
                <td style="padding: 10px; border: 1px solid #ddd;">这是第三个测试项目</td>
                <td style="padding: 10px; border: 1px solid #ddd; text-align: center;"><span style="background-color: #F44336; color: white; padding: 4px 8px; border-radius: 4px;">未开始</span></td>
                <td style="padding: 10px; border: 1px solid #ddd; text-align: right;">0</td>
            </tr>
            <tr bgcolor="#e1bee7" style="font-weight: bold;">
                <td style="padding: 10px; border: 1px solid #ddd;" colspan="3">总计</td>
                <td style="padding: 10px; border: 1px solid #ddd; text-align: right;">150</td>
            </tr>
        </table>
        
        <p style="margin-top: 20px; font-size: 14px;">表格支持以下特性：</p>
        <ul>
            <li>边框样式</li>
            <li>背景颜色</li>
            <li>文本对齐</li>
            <li>单元格合并</li>
            <li>内边距</li>
            <li>字体样式</li>
            <li>行悬停效果</li>
        </ul>
        '''
        self.text_edit.setHtml(html)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = QTextEditHtmlTableTest()
    window.show()
    sys.exit(app.exec_())
