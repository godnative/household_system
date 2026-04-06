def get_member_excel_html(member):
    """
    生成成员信息的 HTML 表格，使用 a1.html 模板
    """
    # 读取 a1.html 模板文件
    with open(r"D:\dev\newhuanwei\household_system\doc\a3.html", 'r', encoding='utf-8') as f:
        html = f.read()
    
    # 替换数据项
    # 基本信息
    html = html.replace('姓名占位', f'{member.name}', 1)
    html = html.replace('性别占位', f'{member.gender if member.gender else "无"}', 1)
    html = html.replace('圣名占位', f'{member.baptismal_name if member.baptismal_name else "无"}', 1)
    html = html.replace('出生日期占位', f'{str(member.birth_date) if str(member.birth_date) != "1752-09-14" else "无"}', 1)
    html = html.replace('文化程度占位', f'{member.education if member.education else "无"}', 1)
    html = html.replace('与户主关系占位', f'{member.relation_to_head if member.relation_to_head else "无"}', 1)
    html = html.replace('何时迁入占位', f'{str(member.move_in_date) if str(member.move_in_date) != "1752-09-14" else "无"}', 1)
    html = html.replace('从事职业占位', f'{member.occupation if member.occupation else "无"}', 1)
    
    # 教籍证件编号
    html = html.replace('教籍证件编号占位', f'{member.church_id if member.church_id else "无"}', 1)
    
    # 圣洗信息
    html = html.replace('圣洗施行人占位', f'{member.baptism_priest if member.baptism_priest else "无"}', 1)
    html = html.replace('圣洗代父占位', f'{member.baptism_godparent if member.baptism_godparent else "无"}', 1)
    html = html.replace('领洗时间占位', f'{str(member.baptism_date) if str(member.baptism_date) != "1752-09-14" else "无"}', 1)
    html = html.replace('圣洗备注占位', f'{member.baptism_note if member.baptism_note else "无"}', 1)
    
    # 初领圣体时间
    html = html.replace('初领圣体时间占位', f'{str(member.first_communion_date) if str(member.first_communion_date) != "1752-09-14" else "无"}', 1)
    
    # 补礼信息
    html = html.replace('补礼神父占位', f'{member.supplementary_priest if member.supplementary_priest else "无"}', 1)
    html = html.replace('补礼地点占位', f'{member.supplementary_place if member.supplementary_place else "无"}', 1)
    html = html.replace('补礼日期占位', f'{str(member.supplementary_date) if str(member.supplementary_date) != "1752-09-14" else "无"}', 1)
    
    # 坚振信息
    html = html.replace('坚振日期占位', f'{str(member.confirmation_date) if str(member.confirmation_date) != "1752-09-14" else "无"}', 1)
    html = html.replace('坚振施行人占位', f'{member.confirmation_priest if member.confirmation_priest else "无"}', 1)
    html = html.replace('坚振代父占位', f'{member.confirmation_godparent if member.confirmation_godparent else "无"}', 1)
    html = html.replace('坚振圣名占位', f'{member.confirmation_name if member.confirmation_name else "无"}', 1)
    html = html.replace('坚振年龄占位', f'{str(member.confirmation_age) if member.confirmation_age else "无"}', 1)
    html = html.replace('坚振地点占位', f'{member.confirmation_place if member.confirmation_place else "无"}', 1)
    
    # 婚配信息
    html = html.replace('婚配日期占位', f'{str(member.marriage_date) if str(member.marriage_date) != "1752-09-14" else "无"}', 1)
    html = html.replace('婚配主礼神父占位', f'{member.marriage_priest if member.marriage_priest else "无"}', 1)
    html = html.replace('婚配证人占位', f'{member.marriage_witness if member.marriage_witness else "无"}', 1)
    html = html.replace('婚配事项占位', f'{member.marriage_dispensation_item if member.marriage_dispensation_item else "无"}', 1)
    html = html.replace('婚配神父占位', f'{member.marriage_dispensation_priest if member.marriage_dispensation_priest else "无"}', 1)
    html = html.replace('婚配地点占位', f'{member.marriage_place if member.marriage_place else "无"}', 1)
    
    # 病人傅油信息
    html = html.replace('病人傅油日期占位', f'{str(member.anointing_date) if str(member.anointing_date) != "1752-09-14" else "无"}', 1)
    html = html.replace('病人傅油施行人占位', f'{member.anointing_priest if member.anointing_priest else "无"}', 1)
    html = html.replace('病人傅油地点占位', f'{member.anointing_place if member.anointing_place else "无"}', 1)
    html = html.replace('病人傅油死亡日期占位', f'{str(member.death_date) if str(member.death_date) != "1752-09-14" else "无"}', 1)
    html = html.replace('病人傅油年龄占位', f'{str(member.death_age) if member.death_age else "无"}', 1)
    
    # 备注和所属善会
    html = html.replace('备注占位', f'{member.note if member.note else "无"}', 1)
    html = html.replace('所属善会占位', f'{member.association if member.association else "无"}', 1)
    
    # 图片处理
    # 找到图片单元格并替换内容
    if member.photo:
        html = html.replace('<p align="center" style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" font-size:14px; font-weight:600;">图片</span></p>', f'<p align="center" style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" font-size:14px; font-weight:600;">图片</span></p><p align="center" style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><img src="{member.photo}" alt="成员照片" style="width: 120px; height: 160px; object-fit: cover;" /></p>')

    return html