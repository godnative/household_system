import openpyxl
from openpyxl.styles import Font, Alignment, PatternFill
from io import BytesIO
from PyQt5.QtWidgets import QTextEdit
from PyQt5.QtCore import QUrl
from PyQt5.QtGui import QTextDocument


def get_member_excel_html(member):
    """
    生成成员信息的 Excel 表格 HTML
    """
    # 直接生成 HTML，避免处理 Excel 合并单元格的问题
    # 确保 HTML 表格的格式与 Excel 模板一致
    html = f'''
    <html>
    <head>
        <style>
            table {{ border-collapse: collapse; width: 100%; font-family: Arial, sans-serif; }}
            th {{ background-color: #f2f2f2; border: 1px solid #ddd; padding: 8px; text-align: left; }}
            td {{ border: 1px solid #ddd; padding: 8px; }}
            .section-title {{ background-color: #e6f7ff; font-weight: bold; }}
            .sub-section {{ background-color: #f9f9f9; }}
            .info-row {{ }}
            .empty {{ color: #999; }}
        </style>
    </head>
    <body>
        <h2 style="text-align: center; color: #333;">成员详细信息</h2>
        <p style="text-align: center; color: #666;">数据已按照圣名-教籍信息表格式渲染</p>
        
        <!-- 这里可以添加更多的 HTML 内容来模拟 Excel 表格的外观 -->
        <!-- 由于直接渲染 Excel 到 HTML 比较复杂，这里使用我们之前的表格格式，但确保字段顺序和 Excel 一致 -->
        
        <!-- 基本信息 -->
        <table>
            <tr class="section-title">
                <td colspan="8">基本信息</td>
            </tr>
            <tr class="info-row">
                <td width="12.5%">姓名</td>
                <td width="12.5%">性别</td>
                <td width="12.5%">圣名</td>
                <td width="12.5%">出生日期</td>
                <td width="12.5%">文化程度</td>
                <td width="12.5%">与户主关系</td>
                <td width="12.5%">何时迁入</td>
                <td width="12.5%">从事职业</td>
            </tr>
            <tr class="info-row">
                <td>{member.name}</td>
                <td>{member.gender if member.gender else '<span class="empty">无</span>'}</td>
                <td>{member.baptismal_name if member.baptismal_name else '<span class="empty">无</span>'}</td>
                <td>{str(member.birth_date) if member.birth_date else '<span class="empty">无</span>'}</td>
                <td>{member.education if member.education else '<span class="empty">无</span>'}</td>
                <td>{member.relation_to_head if member.relation_to_head else '<span class="empty">无</span>'}</td>
                <td>{str(member.move_in_date) if member.move_in_date else '<span class="empty">无</span>'}</td>
                <td>{member.occupation if member.occupation else '<span class="empty">无</span>'}</td>
            </tr>
        </table>
        
        <br>
        
        <!-- 教籍信息 -->
        <table>
            <tr class="section-title">
                <td colspan="2">教籍信息</td>
            </tr>
            <tr class="info-row">
                <td width="20%">教籍证件编号</td>
                <td width="80%">{member.church_id if member.church_id else '<span class="empty">无</span>'}</td>
            </tr>
        </table>
        
        <br>
        
        <!-- 圣洗信息 -->
        <table>
            <tr class="section-title">
                <td colspan="4">圣洗信息</td>
            </tr>
            <tr class="info-row">
                <td width="25%">施行人</td>
                <td width="25%">代父/母</td>
                <td width="25%">领洗时间</td>
                <td width="25%">备注</td>
            </tr>
            <tr class="info-row">
                <td>{member.baptism_priest if member.baptism_priest else '<span class="empty">无</span>'}</td>
                <td>{member.baptism_godparent if member.baptism_godparent else '<span class="empty">无</span>'}</td>
                <td>{str(member.baptism_date) if member.baptism_date else '<span class="empty">无</span>'}</td>
                <td>{member.baptism_note if member.baptism_note else '<span class="empty">无</span>'}</td>
            </tr>
        </table>
        
        <br>
        
        <!-- 初领圣体和补礼信息 -->
        <table>
            <tr class="section-title">
                <td colspan="4">初领圣体和补礼信息</td>
            </tr>
            <tr class="info-row">
                <td width="25%">初领圣体时间</td>
                <td width="25%">补礼神父</td>
                <td width="25%">补礼地点</td>
                <td width="25%">补礼日期</td>
            </tr>
            <tr class="info-row">
                <td>{str(member.first_communion_date) if member.first_communion_date else '<span class="empty">无</span>'}</td>
                <td>{member.supplementary_priest if member.supplementary_priest else '<span class="empty">无</span>'}</td>
                <td>{member.supplementary_place if member.supplementary_place else '<span class="empty">无</span>'}</td>
                <td>{str(member.supplementary_date) if member.supplementary_date else '<span class="empty">无</span>'}</td>
            </tr>
        </table>
        
        <br>
        
        <!-- 坚振信息 -->
        <table>
            <tr class="section-title">
                <td colspan="6">坚振信息</td>
            </tr>
            <tr class="info-row">
                <td width="16.67%">年月日</td>
                <td width="16.67%">施行人</td>
                <td width="16.67%">代父/母</td>
                <td width="16.67%">圣名</td>
                <td width="16.67%">年龄</td>
                <td width="16.67%">地点</td>
            </tr>
            <tr class="info-row">
                <td>{str(member.confirmation_date) if member.confirmation_date else '<span class="empty">无</span>'}</td>
                <td>{member.confirmation_priest if member.confirmation_priest else '<span class="empty">无</span>'}</td>
                <td>{member.confirmation_godparent if member.confirmation_godparent else '<span class="empty">无</span>'}</td>
                <td>{member.confirmation_name if member.confirmation_name else '<span class="empty">无</span>'}</td>
                <td>{str(member.confirmation_age) if member.confirmation_age else '<span class="empty">无</span>'}</td>
                <td>{member.confirmation_place if member.confirmation_place else '<span class="empty">无</span>'}</td>
            </tr>
        </table>
        
        <br>
        
        <!-- 婚配信息 -->
        <table>
            <tr class="section-title">
                <td colspan="6">婚配信息</td>
            </tr>
            <tr class="info-row">
                <td width="16.67%">年月日</td>
                <td width="16.67%">主礼神父</td>
                <td width="16.67%">证人</td>
                <td width="16.67%">宽免事项</td>
                <td width="16.67%">宽免神父</td>
                <td width="16.67%">地点</td>
            </tr>
            <tr class="info-row">
                <td>{str(member.marriage_date) if member.marriage_date else '<span class="empty">无</span>'}</td>
                <td>{member.marriage_priest if member.marriage_priest else '<span class="empty">无</span>'}</td>
                <td>{member.marriage_witness if member.marriage_witness else '<span class="empty">无</span>'}</td>
                <td>{member.marriage_dispensation_item if member.marriage_dispensation_item else '<span class="empty">无</span>'}</td>
                <td>{member.marriage_dispensation_priest if member.marriage_dispensation_priest else '<span class="empty">无</span>'}</td>
                <td>{member.marriage_place if member.marriage_place else '<span class="empty">无</span>'}</td>
            </tr>
        </table>
        
        <br>
        
        <!-- 病人傅油信息 -->
        <table>
            <tr class="section-title">
                <td colspan="5">病人傅油信息</td>
            </tr>
            <tr class="info-row">
                <td width="20%">年月日</td>
                <td width="20%">施行人</td>
                <td width="20%">地点</td>
                <td width="20%">死亡日期</td>
                <td width="20%">年龄</td>
            </tr>
            <tr class="info-row">
                <td>{str(member.anointing_date) if member.anointing_date else '<span class="empty">无</span>'}</td>
                <td>{member.anointing_priest if member.anointing_priest else '<span class="empty">无</span>'}</td>
                <td>{member.anointing_place if member.anointing_place else '<span class="empty">无</span>'}</td>
                <td>{str(member.death_date) if member.death_date else '<span class="empty">无</span>'}</td>
                <td>{str(member.death_age) if member.death_age else '<span class="empty">无</span>'}</td>
            </tr>
        </table>
        
        <br>
        
        <!-- 其他信息 -->
        <table>
            <tr class="section-title">
                <td colspan="2">其他信息</td>
            </tr>
            <tr class="info-row">
                <td width="20%">所属善会</td>
                <td width="80%">{member.association if member.association else '<span class="empty">无</span>'}</td>
            </tr>
            <tr class="info-row">
                <td>备注</td>
                <td>{member.note if member.note else '<span class="empty">无</span>'}</td>
            </tr>
        </table>
    </body>
    </html>
    '''
    
    return html