from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTextEdit, QLabel, QApplication
from PyQt5.QtCore import Qt
import sys


class QTextEditRichTextTest(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # 标题
        title_label = QLabel('QTextEdit 富文本渲染测试')
        title_label.setStyleSheet('font-size: 16px; font-weight: bold;')
        layout.addWidget(title_label)
        
        # 按钮布局
        button_layout = QHBoxLayout()
        
        # 测试 HTML 表格按钮
        test_table_btn = QPushButton('测试 HTML 表格')
        test_table_btn.clicked.connect(self.test_html_table)
        button_layout.addWidget(test_table_btn)
        
        # 测试复杂 HTML 表格按钮
        test_complex_table_btn = QPushButton('测试复杂 HTML 表格')
        test_complex_table_btn.clicked.connect(self.test_complex_html_table)
        button_layout.addWidget(test_complex_table_btn)
        
        # 测试样式按钮
        test_style_btn = QPushButton('测试样式')
        test_style_btn.clicked.connect(self.test_styles)
        button_layout.addWidget(test_style_btn)
        
        layout.addLayout(button_layout)
        
        # QTextEdit 组件
        self.text_edit = QTextEdit()
        self.text_edit.setMinimumHeight(400)
        self.text_edit.setReadOnly(True)
        layout.addWidget(self.text_edit)
        
        # 设置窗口大小
        self.resize(800, 600)
        self.setWindowTitle('QTextEdit 富文本测试')
    
    def test_html_table(self):
        """测试基本的 HTML 表格"""
        html = '''
        <h2>基本 HTML 表格测试</h2>
        <table border="1" cellpadding="5" cellspacing="0">
            <tr>
                <th>ID</th>
                <th>姓名</th>
                <th>年龄</th>
                <th>性别</th>
            </tr>
            <tr>
                <td>1</td>
                <td>张三</td>
                <td>30</td>
                <td>男</td>
            </tr>
            <tr>
                <td>2</td>
                <td>李四</td>
                <td>25</td>
                <td>女</td>
            </tr>
            <tr>
                <td>3</td>
                <td>王五</td>
                <td>35</td>
                <td>男</td>
            </tr>
        </table>
        '''
        self.text_edit.setHtml(html)
    
    def test_complex_html_table(self):
        """测试复杂的 HTML 表格"""
        html = '''
        <h2>复杂 HTML 表格测试</h2>
        <table border="1" cellpadding="5" cellspacing="0">
            <tr bgcolor="#f0f0f0">
                <th colspan="4">家庭成员信息</th>
            </tr>
            <tr bgcolor="#e0e0e0">
                <th>关系</th>
                <th>姓名</th>
                <th>年龄</th>
                <th>职业</th>
            </tr>
            <tr>
                <td>户主</td>
                <td>张三</td>
                <td>35</td>
                <td>教师</td>
            </tr>
            <tr bgcolor="#f9f9f9">
                <td>配偶</td>
                <td>李四</td>
                <td>32</td>
                <td>医生</td>
            </tr>
            <tr>
                <td>子女</td>
                <td>张小明</td>
                <td>8</td>
                <td>学生</td>
            </tr>
            <tr bgcolor="#f9f9f9">
                <td>父母</td>
                <td>张父</td>
                <td>65</td>
                <td>退休</td>
            </tr>
            <tr>
                <td>父母</td>
                <td>张母</td>
                <td>63</td>
                <td>退休</td>
            </tr>
        </table>
        '''
        self.text_edit.setHtml(html)
    
    def test_styles(self):
        """测试各种样式"""
        html = '''
        <h2>样式测试</h2>
        <p>这是 <b>粗体文本</b></p>
        <p>这是 <i>斜体文本</i></p>
        <p>这是 <u>下划线文本</u></p>
        <p>这是 <font color="red">红色文本</font></p>
        <p>这是 <font size="+2">大号文本</font></p>
        <p>这是 <font face="Arial">Arial 字体</font></p>
        <ul>
            <li>项目 1</li>
            <li>项目 2</li>
            <li>项目 3</li>
        </ul>
        <ol>
            <li>步骤 1</li>
            <li>步骤 2</li>
            <li>步骤 3</li>
        </ol>
        <table border="1" cellpadding="5" cellspacing="0">
            <tr>
                <th>产品</th>
                <th>价格</th>
            </tr>
            <tr>
                <td>苹果</td>
                <td>¥5.00</td>
            </tr>
            <tr>
                <td>香蕉</td>
                <td>¥3.00</td>
            </tr>
        </table>
        '''
        self.text_edit.setHtml(html)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = QTextEditRichTextTest()
    window.show()
    sys.exit(app.exec_())
