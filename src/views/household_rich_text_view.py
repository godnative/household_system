from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTextEdit, QLabel, QComboBox, QApplication
from PyQt5.QtCore import Qt
import sys
import os

# 添加当前目录到 Python 路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from models import SessionLocal, Household, Member
from services.household_service import HouseholdService
from services.member_service import MemberService


class HouseholdRichTextView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        self.load_households()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # 标题
        title_label = QLabel('家庭成员信息富文本展示')
        title_label.setStyleSheet('font-size: 16px; font-weight: bold;')
        layout.addWidget(title_label)
        
        # 家庭选择
        household_layout = QHBoxLayout()
        household_label = QLabel('选择家庭:')
        self.household_combo = QComboBox()
        self.household_combo.currentIndexChanged.connect(self.on_household_changed)
        household_layout.addWidget(household_label)
        household_layout.addWidget(self.household_combo)
        household_layout.addStretch()
        layout.addLayout(household_layout)
        
        # 生成报告按钮
        generate_btn = QPushButton('生成家庭成员报告')
        generate_btn.clicked.connect(self.generate_report)
        layout.addWidget(generate_btn)
        
        # QTextEdit 组件
        self.text_edit = QTextEdit()
        self.text_edit.setMinimumHeight(500)
        self.text_edit.setReadOnly(True)
        layout.addWidget(self.text_edit)
        
        # 设置窗口大小
        self.resize(900, 700)
        self.setWindowTitle('家庭信息富文本展示')
    
    def load_households(self):
        """加载家庭数据"""
        db = SessionLocal()
        try:
            households = HouseholdService.get_all_households(db)
            self.household_combo.clear()
            for household in households:
                display_text = f'家庭 {household.id}'
                if household.head_of_household:
                    display_text += f' - {household.head_of_household}'
                self.household_combo.addItem(display_text, household.id)
            if households:
                self.on_household_changed(0)
        finally:
            db.close()
    
    def on_household_changed(self, index):
        """家庭选择变化时的处理"""
        household_id = self.household_combo.currentData()
        if household_id:
            self.generate_report()
    
    def generate_report(self):
        """生成家庭成员报告"""
        household_id = self.household_combo.currentData()
        if not household_id:
            return
        
        db = SessionLocal()
        try:
            # 获取家庭信息
            household = db.query(Household).filter(Household.id == household_id).first()
            if not household:
                return
            
            # 获取家庭成员
            members = MemberService.get_all_members(db, household_id=household_id)
            
            # 生成 HTML 报告
            html = self.generate_html_report(household, members)
            self.text_edit.setHtml(html)
        finally:
            db.close()
    
    def generate_html_report(self, household, members):
        """生成 HTML 报告"""
        html = f'''
        <h1 style="text-align: center; color: #333;">家庭成员信息报告</h1>
        
        <h2 style="color: #555;">家庭基本信息</h2>
        <table border="1" cellpadding="8" cellspacing="0" style="width: 100%; border-collapse: collapse;">
            <tr bgcolor="#f0f0f0">
                <th style="text-align: left; width: 20%;">项目</th>
                <th style="text-align: left; width: 80%;">内容</th>
            </tr>
            <tr>
                <td>家庭ID</td>
                <td>{household.id}</td>
            </tr>
            <tr bgcolor="#f9f9f9">
                <td>户主</td>
                <td>{household.head_of_household if household.head_of_household else '无'}</td>
            </tr>
            <tr>
                <td>片号</td>
                <td>{household.plot_number}</td>
            </tr>
            <tr bgcolor="#f9f9f9">
                <td>家庭住址</td>
                <td>{household.address if household.address else '无'}</td>
            </tr>
            <tr>
                <td>电话</td>
                <td>{household.phone if household.phone else '无'}</td>
            </tr>
        </table>
        
        <h2 style="color: #555; margin-top: 30px;">家庭成员列表</h2>
        <table border="1" cellpadding="8" cellspacing="0" style="width: 100%; border-collapse: collapse;">
            <tr bgcolor="#f0f0f0">
                <th style="text-align: center; width: 5%;">序号</th>
                <th style="text-align: left; width: 15%;">姓名</th>
                <th style="text-align: center; width: 10%;">性别</th>
                <th style="text-align: center; width: 15%;">圣名</th>
                <th style="text-align: left; width: 15%;">与户主关系</th>
                <th style="text-align: left; width: 15%;">文化程度</th>
                <th style="text-align: left; width: 25%;">从事职业</th>
            </tr>
        '''
        
        for i, member in enumerate(members, 1):
            bg_color = '#f9f9f9' if i % 2 == 0 else '#ffffff'
            html += f'''
            <tr bgcolor="{bg_color}">
                <td style="text-align: center;">{i}</td>
                <td>{member.name}</td>
                <td style="text-align: center;">{member.gender if member.gender else '无'}</td>
                <td style="text-align: center;">{member.baptismal_name if member.baptismal_name else '无'}</td>
                <td>{member.relation_to_head if member.relation_to_head else '无'}</td>
                <td>{member.education if member.education else '无'}</td>
                <td>{member.occupation if member.occupation else '无'}</td>
            </tr>
            '''
        
        html += '''
        </table>
        
        <h2 style="color: #555; margin-top: 30px;">成员详细信息</h2>
        '''
        
        for member in members:
            html += f'''
            <div style="border: 1px solid #ddd; padding: 15px; margin-bottom: 20px; border-radius: 5px;">
                <h3 style="color: #333; margin-top: 0;">{member.name} - 详细信息</h3>
                <table border="1" cellpadding="6" cellspacing="0" style="width: 100%; border-collapse: collapse;">
                    <tr bgcolor="#f0f0f0">
                        <th style="text-align: left; width: 20%;">项目</th>
                        <th style="text-align: left; width: 30%;">内容</th>
                        <th style="text-align: left; width: 20%;">项目</th>
                        <th style="text-align: left; width: 30%;">内容</th>
                    </tr>
                    <tr>
                        <td>出生日期</td>
                        <td>{str(member.birth_date) if member.birth_date else '无'}</td>
                        <td>何时迁入</td>
                        <td>{str(member.move_in_date) if member.move_in_date else '无'}</td>
                    </tr>
                    <tr bgcolor="#f9f9f9">
                        <td>教籍证件编号</td>
                        <td>{member.church_id if member.church_id else '无'}</td>
                        <td>所属善会</td>
                        <td>{member.association if member.association else '无'}</td>
                    </tr>
                    <tr>
                        <td>圣洗时间</td>
                        <td>{str(member.baptism_date) if member.baptism_date else '无'}</td>
                        <td>施行人</td>
                        <td>{member.baptism_priest if member.baptism_priest else '无'}</td>
                    </tr>
                    <tr bgcolor="#f9f9f9">
                        <td>初领圣体时间</td>
                        <td>{str(member.first_communion_date) if member.first_communion_date else '无'}</td>
                        <td>坚振时间</td>
                        <td>{str(member.confirmation_date) if member.confirmation_date else '无'}</td>
                    </tr>
                </table>
                <p style="margin-top: 10px;"><strong>备注:</strong> {member.note if member.note else '无'}</p>
            </div>
            '''
        
        return html


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = HouseholdRichTextView()
    window.show()
    sys.exit(app.exec_())
