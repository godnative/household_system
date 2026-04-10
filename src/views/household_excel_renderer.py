def get_household_excel_html(household, village):
    """
    生成家庭信息的 HTML 表格，使用 a4.html 模板

    Args:
        household: Household 对象，包含家庭信息
        village: Village 对象，包含堂区信息
    """
    import os
    # 读取 a4.html 模板文件
    template_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'doc', 'a4.html')
    with open(template_path, 'r', encoding='utf-8') as f:
        html = f.read()

    # 替换数据项
    # 所属堂区
    html = html.replace('所属堂区占位', f'{village.name if village else "无"}', 1)

    # 家庭户号（使用ID作为户号）
    html = html.replace('家庭户号占位', f'{household.id if household.id else "无"}', 1)

    # 片号
    html = html.replace('片号占位', f'{household.plot_number if household.plot_number else "无"}', 1)

    # 家庭住址
    html = html.replace('家庭住址占位', f'{household.address if household.address else "无"}', 1)

    # 户主姓名
    html = html.replace('户主姓名占位', f'{household.head_of_household if household.head_of_household else "无"}', 1)

    # 电话
    html = html.replace('电话占位', f'{household.phone if household.phone else "无"}', 1)

    return html
