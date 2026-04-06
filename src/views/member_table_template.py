def get_member_table_html(member):
    """
    生成成员信息的 HTML 表格
    """
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
        
        <!-- 基本信息 -->
        <table>
            <tr class="section-title">
                <td colspan="4">基本信息</td>
            </tr>
            <tr class="info-row">
                <td width="15%">姓名:</td>
                <td width="35%">{member.name}</td>
                <td width="15%">性别:</td>
                <td width="35%">{member.gender if member.gender else '<span class="empty">无</span>'}</td>
            </tr>
            <tr class="info-row">
                <td>圣名:</td>
                <td>{member.baptismal_name if member.baptismal_name else '<span class="empty">无</span>'}</td>
                <td>出生日期:</td>
                <td>{str(member.birth_date) if member.birth_date else '<span class="empty">无</span>'}</td>
            </tr>
            <tr class="info-row">
                <td>文化程度:</td>
                <td>{member.education if member.education else '<span class="empty">无</span>'}</td>
                <td>与户主关系:</td>
                <td>{member.relation_to_head if member.relation_to_head else '<span class="empty">无</span>'}</td>
            </tr>
            <tr class="info-row">
                <td>何时迁入:</td>
                <td>{str(member.move_in_date) if member.move_in_date else '<span class="empty">无</span>'}</td>
                <td>从事职业:</td>
                <td>{member.occupation if member.occupation else '<span class="empty">无</span>'}</td>
            </tr>
            <tr class="info-row">
                <td>照片:</td>
                <td colspan="3">
                    {f'<img src="{member.photo}" alt="成员照片" style="width: 150px; height: 150px; object-fit: cover;" />' if member.photo else '<span class="empty">无照片</span>'}
                </td>
            </tr>
        </table>
        
        <br>
        
        <!-- 教籍证件编号 -->
        <table>
            <tr class="section-title">
                <td colspan="2">教籍信息</td>
            </tr>
            <tr class="info-row">
                <td width="15%">教籍证件编号:</td>
                <td width="85%">{member.church_id if member.church_id else '<span class="empty">无</span>'}</td>
            </tr>
        </table>
        
        <br>
        
        <!-- 圣洗信息 -->
        <table>
            <tr class="section-title">
                <td colspan="4">圣洗信息</td>
            </tr>
            <tr class="info-row">
                <td width="15%">施行人:</td>
                <td width="35%">{member.baptism_priest if member.baptism_priest else '<span class="empty">无</span>'}</td>
                <td width="15%">代父/母:</td>
                <td width="35%">{member.baptism_godparent if member.baptism_godparent else '<span class="empty">无</span>'}</td>
            </tr>
            <tr class="info-row">
                <td>领洗时间:</td>
                <td>{str(member.baptism_date) if member.baptism_date else '<span class="empty">无</span>'}</td>
                <td>备注:</td>
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
                <td width="15%">初领圣体时间:</td>
                <td colspan="3">{str(member.first_communion_date) if member.first_communion_date else '<span class="empty">无</span>'}</td>
            </tr>
            <tr class="sub-section">
                <td colspan="4">补礼信息</td>
            </tr>
            <tr class="info-row">
                <td>神父:</td>
                <td>{member.supplementary_priest if member.supplementary_priest else '<span class="empty">无</span>'}</td>
                <td>地点:</td>
                <td>{member.supplementary_place if member.supplementary_place else '<span class="empty">无</span>'}</td>
            </tr>
            <tr class="info-row">
                <td>日期:</td>
                <td colspan="3">{str(member.supplementary_date) if member.supplementary_date else '<span class="empty">无</span>'}</td>
            </tr>
        </table>
        
        <br>
        
        <!-- 坚振信息 -->
        <table>
            <tr class="section-title">
                <td colspan="4">坚振信息</td>
            </tr>
            <tr class="info-row">
                <td width="15%">年月日:</td>
                <td width="35%">{str(member.confirmation_date) if member.confirmation_date else '<span class="empty">无</span>'}</td>
                <td width="15%">施行人:</td>
                <td width="35%">{member.confirmation_priest if member.confirmation_priest else '<span class="empty">无</span>'}</td>
            </tr>
            <tr class="info-row">
                <td>代父/母:</td>
                <td>{member.confirmation_godparent if member.confirmation_godparent else '<span class="empty">无</span>'}</td>
                <td>圣名:</td>
                <td>{member.confirmation_name if member.confirmation_name else '<span class="empty">无</span>'}</td>
            </tr>
            <tr class="info-row">
                <td>年龄:</td>
                <td>{str(member.confirmation_age) if member.confirmation_age else '<span class="empty">无</span>'}</td>
                <td>地点:</td>
                <td>{member.confirmation_place if member.confirmation_place else '<span class="empty">无</span>'}</td>
            </tr>
        </table>
        
        <br>
        
        <!-- 婚配信息 -->
        <table>
            <tr class="section-title">
                <td colspan="4">婚配信息</td>
            </tr>
            <tr class="info-row">
                <td width="15%">年月日:</td>
                <td width="35%">{str(member.marriage_date) if member.marriage_date else '<span class="empty">无</span>'}</td>
                <td width="15%">主礼神父:</td>
                <td width="35%">{member.marriage_priest if member.marriage_priest else '<span class="empty">无</span>'}</td>
            </tr>
            <tr class="info-row">
                <td>证人:</td>
                <td colspan="3">{member.marriage_witness if member.marriage_witness else '<span class="empty">无</span>'}</td>
            </tr>
            <tr class="sub-section">
                <td colspan="4">宽免信息</td>
            </tr>
            <tr class="info-row">
                <td>事项:</td>
                <td>{member.marriage_dispensation_item if member.marriage_dispensation_item else '<span class="empty">无</span>'}</td>
                <td>神父:</td>
                <td>{member.marriage_dispensation_priest if member.marriage_dispensation_priest else '<span class="empty">无</span>'}</td>
            </tr>
            <tr class="info-row">
                <td>地点:</td>
                <td colspan="3">{member.marriage_place if member.marriage_place else '<span class="empty">无</span>'}</td>
            </tr>
        </table>
        
        <br>
        
        <!-- 病人傅油信息 -->
        <table>
            <tr class="section-title">
                <td colspan="4">病人傅油信息</td>
            </tr>
            <tr class="info-row">
                <td width="15%">年月日:</td>
                <td width="35%">{str(member.anointing_date) if member.anointing_date else '<span class="empty">无</span>'}</td>
                <td width="15%">施行人:</td>
                <td width="35%">{member.anointing_priest if member.anointing_priest else '<span class="empty">无</span>'}</td>
            </tr>
            <tr class="info-row">
                <td>地点:</td>
                <td>{member.anointing_place if member.anointing_place else '<span class="empty">无</span>'}</td>
                <td>死亡日期:</td>
                <td>{str(member.death_date) if member.death_date else '<span class="empty">无</span>'}</td>
            </tr>
            <tr class="info-row">
                <td>年龄:</td>
                <td>{str(member.death_age) if member.death_age else '<span class="empty">无</span>'}</td>
                <td colspan="2"></td>
            </tr>
        </table>
        
        <br>
        
        <!-- 其他信息 -->
        <table>
            <tr class="section-title">
                <td colspan="2">其他信息</td>
            </tr>
            <tr class="info-row">
                <td width="15%">所属善会:</td>
                <td width="85%">{member.association if member.association else '<span class="empty">无</span>'}</td>
            </tr>
            <tr class="info-row">
                <td>备注:</td>
                <td>{member.note if member.note else '<span class="empty">无</span>'}</td>
            </tr>
        </table>
    </body>
    </html>
    '''
    return html