def get_household_excel_html(household, village, for_print=False):
    """
    生成家庭信息的 HTML 表格

    Args:
        household: Household 对象，包含家庭信息
        village: Village 对象，包含堂区信息
        for_print: 是否使用打印模板（True 使用 a4_print.html，False 使用 a4.html）
    """
    import os
    template_name = 'a4_print.html' if for_print else 'a4.html'
    template_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'doc', template_name)
    with open(template_path, 'r', encoding='utf-8') as f:
        html = f.read()

    html = html.replace('所属堂区占位', f'{village.name if village else "无"}', 1)
    html = html.replace('家庭户号占位', f'{household.id if household.id else "无"}', 1)
    html = html.replace('片号占位', f'{household.plot_number if household.plot_number else "无"}', 1)
    html = html.replace('家庭住址占位', f'{household.address if household.address else "无"}', 1)
    html = html.replace('户主姓名占位', f'{household.head_of_household if household.head_of_household else "无"}', 1)
    html = html.replace('电话占位', f'{household.phone if household.phone else "无"}', 1)

    return html