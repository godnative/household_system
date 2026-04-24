#!/usr/bin/env python3
"""
数据对账脚本：验证数据迁移的完整性

用法：
    python scripts/reconcile_data.py --source /path/to/old/household.db --target /path/to/new/household_system_web.db

功能：
    - 对比源数据库和目标数据库的记录数
    - 验证外键关系完整性
    - 抽样检查字段一致性
    - 生成对账报告
"""

import argparse
import json
import sqlite3
from datetime import datetime


def get_table_counts(conn: sqlite3.Connection, tables: list) -> dict:
    """获取表记录数"""
    cursor = conn.cursor()
    counts = {}
    for table in tables:
        try:
            cursor.execute(f'SELECT COUNT(*) FROM {table}')
            counts[table] = cursor.fetchone()[0]
        except sqlite3.OperationalError:
            counts[table] = None
    return counts


def check_foreign_keys(conn: sqlite3.Connection) -> dict:
    """检查外键关系完整性"""
    cursor = conn.cursor()
    issues = []

    # 检查家庭-堂区关系
    cursor.execute('''
        SELECT h.id, h.village_id
        FROM households h
        LEFT JOIN villages v ON h.village_id = v.id
        WHERE v.id IS NULL AND h.village_id IS NOT NULL
    ''')
    orphan_households = cursor.fetchall()
    if orphan_households:
        issues.append({
            'table': 'households',
            'issue': 'orphan_records',
            'description': f'发现 {len(orphan_households)} 个没有对应堂区的家庭',
            'ids': [h[0] for h in orphan_households[:10]]  # 只显示前10个
        })

    # 检查成员-家庭关系
    cursor.execute('''
        SELECT m.id, m.household_id
        FROM members m
        LEFT JOIN households h ON m.household_id = h.id
        WHERE h.id IS NULL
    ''')
    orphan_members = cursor.fetchall()
    if orphan_members:
        issues.append({
            'table': 'members',
            'issue': 'orphan_records',
            'description': f'发现 {len(orphan_members)} 个没有对应家庭的成员',
            'ids': [m[0] for m in orphan_members[:10]]
        })

    # 检查用户-角色关系
    cursor.execute('''
        SELECT u.id, u.role_id
        FROM users u
        LEFT JOIN roles r ON u.role_id = r.id
        WHERE r.id IS NULL
    ''')
    orphan_users = cursor.fetchall()
    if orphan_users:
        issues.append({
            'table': 'users',
            'issue': 'orphan_records',
            'description': f'发现 {len(orphan_users)} 个没有对应角色的用户',
            'ids': [u[0] for u in orphan_users[:10]]
        })

    return {'issues': issues, 'is_valid': len(issues) == 0}


def sample_field_check(source_conn: sqlite3.Connection, target_conn: sqlite3.Connection, table: str, sample_size: int = 10) -> dict:
    """抽样检查字段一致性"""
    source_cursor = source_conn.cursor()
    target_cursor = target_conn.cursor()

    result = {
        'table': table,
        'sample_size': 0,
        'matches': 0,
        'mismatches': []
    }

    # 获取源数据样本
    try:
        source_cursor.execute(f'SELECT * FROM {table} ORDER BY id LIMIT ?', (sample_size,))
        source_rows = source_cursor.fetchall()

        if not source_rows:
            return result

        # 获取列名
        source_cursor.execute(f'PRAGMA table_info({table})')
        columns = [col[1] for col in source_cursor.fetchall()]

        result['sample_size'] = len(source_rows)

        for source_row in source_rows:
            source_dict = dict(zip(columns, source_row))
            row_id = source_dict.get('id')

            # 在目标库查找对应记录
            target_cursor.execute(f'SELECT * FROM {table} WHERE id = ?', (row_id,))
            target_row = target_cursor.fetchone()

            if not target_row:
                result['mismatches'].append({
                    'id': row_id,
                    'issue': 'not_found_in_target'
                })
                continue

            target_dict = dict(zip(columns, target_row))

            # 比较字段
            mismatches = []
            for col in columns:
                if source_dict.get(col) != target_dict.get(col):
                    mismatches.append({
                        'column': col,
                        'source': source_dict.get(col),
                        'target': target_dict.get(col)
                    })

            if mismatches:
                result['mismatches'].append({
                    'id': row_id,
                    'field_mismatches': mismatches
                })
            else:
                result['matches'] += 1

    except sqlite3.OperationalError as e:
        result['error'] = str(e)

    return result


def run_reconciliation(source_db: str, target_db: str) -> dict:
    """执行对账"""
    report = {
        'source': source_db,
        'target': target_db,
        'timestamp': datetime.now().isoformat(),
        'status': 'completed'
    }

    source_conn = sqlite3.connect(source_db)
    target_conn = sqlite3.connect(target_db)

    tables = ['villages', 'households', 'members', 'users', 'roles', 'permissions']

    try:
        # 记录数对比
        report['source_counts'] = get_table_counts(source_conn, tables)
        report['target_counts'] = get_table_counts(target_conn, tables)

        # 计算差异
        report['count_diff'] = {}
        for table in tables:
            source_count = report['source_counts'].get(table)
            target_count = report['target_counts'].get(table)
            if source_count is not None and target_count is not None:
                report['count_diff'][table] = {
                    'source': source_count,
                    'target': target_count,
                    'diff': target_count - source_count,
                    'match': source_count == target_count
                }

        # 外键检查（只检查目标库）
        report['foreign_key_check'] = check_foreign_keys(target_conn)

        # 抽样检查
        report['sample_checks'] = {}
        for table in ['villages', 'households', 'members']:
            source_count = report['source_counts'].get(table)
            if source_count is not None and source_count > 0:
                report['sample_checks'][table] = sample_field_check(source_conn, target_conn, table)

    finally:
        source_conn.close()
        target_conn.close()

    # 计算总体状态
    all_counts_match = all(d.get('match', True) for d in report['count_diff'].values())
    fk_valid = report['foreign_key_check']['is_valid']
    report['overall_valid'] = all_counts_match and fk_valid

    return report


def print_report(report: dict) -> None:
    """打印对账报告"""
    print('\n' + '=' * 60)
    print('数据对账报告')
    print('=' * 60)
    print(f'源数据库: {report["source"]}')
    print(f'目标数据库: {report["target"]}')
    print(f'对账时间: {report["timestamp"]}')
    print()

    print('记录数对比:')
    print('-' * 40)
    for table, diff in report.get('count_diff', {}).items():
        status = '✓' if diff['match'] else '✗'
        print(f'  {status} {table}: 源={diff["source"]}, 目标={diff["target"]}, 差异={diff["diff"]}')
    print()

    print('外键完整性检查:')
    print('-' * 40)
    if report['foreign_key_check']['is_valid']:
        print('  ✓ 所有外键关系完整')
    else:
        for issue in report['foreign_key_check']['issues']:
            print(f'  ✗ {issue["description"]}')
    print()

    print('抽样检查:')
    print('-' * 40)
    for table, check in report.get('sample_checks', {}).items():
        if 'error' in check:
            print(f'  ✗ {table}: {check["error"]}')
        else:
            print(f'  {table}: 样本={check["sample_size"]}, 匹配={check["matches"]}, 不匹配={len(check["mismatches"])}')
    print()

    print('=' * 60)
    if report['overall_valid']:
        print('对账结果: ✓ 通过')
    else:
        print('对账结果: ✗ 存在问题')
    print('=' * 60)


def main():
    parser = argparse.ArgumentParser(description='数据对账脚本')
    parser.add_argument('--source', default='/root/household_system/household_system_web.db', help='源数据库路径')
    parser.add_argument('--target', default='/root/household_system/backend/household_system_web.db', help='目标数据库路径')
    parser.add_argument('--output', help='报告输出路径（JSON格式）')

    args = parser.parse_args()

    # 检查文件存在
    if not args.source.startswith(':memory:') and not __import__('os').path.exists(args.source):
        print(f'警告: 源数据库不存在: {args.source}')
    if not args.target.startswith(':memory:') and not __import__('os').path.exists(args.target):
        print(f'警告: 目标数据库不存在: {args.target}')

    # 执行对账
    report = run_reconciliation(args.source, args.target)

    # 打印报告
    print_report(report)

    # 保存报告
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        print(f'报告已保存到: {args.output}')

    return 0 if report['overall_valid'] else 1


if __name__ == '__main__':
    exit(main())
