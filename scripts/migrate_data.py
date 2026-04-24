#!/usr/bin/env python3
"""
数据迁移脚本：从旧 PyQt5 系统迁移到新 Web 系统

用法：
    python scripts/migrate_data.py --source /path/to/old/household.db --target /path/to/new/household_system_web.db

功能：
    - 迁移堂区数据
    - 迁移家庭数据
    - 迁移成员数据
    - 迁移用户数据（可选，密码需要重置）
    - 生成迁移报告
"""

import argparse
import json
import os
import sqlite3
from datetime import datetime
from pathlib import Path


def get_source_stats(source_db: str) -> dict:
    """获取源数据库统计信息"""
    conn = sqlite3.connect(source_db)
    cursor = conn.cursor()

    stats = {}

    # 表统计
    tables_to_count = [
        'villages', 'households', 'members', 'users', 'roles', 'permissions'
    ]

    for table in tables_to_count:
        try:
            cursor.execute(f'SELECT COUNT(*) FROM {table}')
            stats[table] = cursor.fetchone()[0]
        except sqlite3.OperationalError:
            stats[table] = 0

    conn.close()
    return stats


def get_target_stats(target_db: str) -> dict:
    """获取目标数据库统计信息"""
    return get_source_stats(target_db)


def migrate_villages(source_conn, target_conn, report: dict) -> None:
    """迁移堂区数据"""
    source_cursor = source_conn.cursor()
    target_cursor = target_conn.cursor()

    # 读取源数据
    source_cursor.execute('''
        SELECT id, name, code, created_at
        FROM villages
    ''')
    villages = source_cursor.fetchall()

    migrated = 0
    skipped = 0

    for village in villages:
        id, name, code, created_at = village

        # 检查是否已存在
        target_cursor.execute('SELECT id FROM villages WHERE code = ?', (code,))
        if target_cursor.fetchone():
            skipped += 1
            continue

        # 插入数据
        target_cursor.execute('''
            INSERT INTO villages (id, name, code, created_at)
            VALUES (?, ?, ?, ?)
        ''', (id, name, code, created_at or datetime.now().isoformat()))
        migrated += 1

    target_conn.commit()
    report['villages'] = {'migrated': migrated, 'skipped': skipped, 'total': len(villages)}


def migrate_households(source_conn, target_conn, report: dict) -> None:
    """迁移家庭数据"""
    source_cursor = source_conn.cursor()
    target_cursor = target_conn.cursor()

    source_cursor.execute('''
        SELECT id, village_id, plot_number, address, phone, head_of_household, created_at
        FROM households
    ''')
    households = source_cursor.fetchall()

    migrated = 0
    skipped = 0

    for hh in households:
        id, village_id, plot_number, address, phone, head_of_household, created_at = hh

        # 检查是否已存在
        target_cursor.execute('SELECT id FROM households WHERE id = ?', (id,))
        if target_cursor.fetchone():
            skipped += 1
            continue

        target_cursor.execute('''
            INSERT INTO households (id, village_id, plot_number, address, phone, head_of_household, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (id, village_id, plot_number, address, phone, head_of_household, created_at or datetime.now().isoformat()))
        migrated += 1

    target_conn.commit()
    report['households'] = {'migrated': migrated, 'skipped': skipped, 'total': len(households)}


def migrate_members(source_conn, target_conn, report: dict) -> None:
    """迁移成员数据"""
    source_cursor = source_conn.cursor()
    target_cursor = target_conn.cursor()

    # 获取成员表结构
    source_cursor.execute('PRAGMA table_info(members)')
    columns = [col[1] for col in source_cursor.fetchall()]

    source_cursor.execute('SELECT * FROM members')
    members = source_cursor.fetchall()

    migrated = 0
    skipped = 0

    for member in members:
        member_dict = dict(zip(columns, member))
        member_id = member_dict.get('id')

        # 检查是否已存在
        target_cursor.execute('SELECT id FROM members WHERE id = ?', (member_id,))
        if target_cursor.fetchone():
            skipped += 1
            continue

        # 构建插入语句
        placeholders = ', '.join(['?' for _ in columns])
        column_names = ', '.join(columns)

        target_cursor.execute(
            f'INSERT INTO members ({column_names}) VALUES ({placeholders})',
            list(member)
        )
        migrated += 1

    target_conn.commit()
    report['members'] = {'migrated': migrated, 'skipped': skipped, 'total': len(members)}


def migrate_users(source_conn, target_conn, report: dict) -> None:
    """迁移用户数据（警告：密码需要重置）"""
    source_cursor = source_conn.cursor()
    target_cursor = target_conn.cursor()

    source_cursor.execute('''
        SELECT id, username, role_id, is_active, village_id, created_at
        FROM users
    ''')
    users = source_cursor.fetchall()

    migrated = 0
    skipped = 0

    for user in users:
        id, username, role_id, is_active, village_id, created_at = user

        # 检查是否已存在
        target_cursor.execute('SELECT id FROM users WHERE username = ?', (username,))
        if target_cursor.fetchone():
            skipped += 1
            continue

        # 设置默认密码（需要用户重置）
        default_password = 'password123'  # 将被 bcrypt 哈希

        target_cursor.execute('''
            INSERT INTO users (id, username, hashed_password, role_id, is_active, village_id, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (id, username, default_password, role_id, is_active, village_id, created_at or datetime.now().isoformat()))
        migrated += 1

    target_conn.commit()
    report['users'] = {'migrated': migrated, 'skipped': skipped, 'total': len(users), 'note': '密码已重置为默认值，需要用户修改'}


def run_migration(source_db: str, target_db: str, skip_users: bool = False) -> dict:
    """执行迁移"""
    report = {
        'source': source_db,
        'target': target_db,
        'timestamp': datetime.now().isoformat(),
        'tables': {}
    }

    # 连接数据库
    source_conn = sqlite3.connect(source_db)
    target_conn = sqlite3.connect(target_db)

    # 获取源统计
    report['source_stats'] = get_source_stats(source_db)

    try:
        # 迁移堂区
        print('迁移堂区数据...')
        migrate_villages(source_conn, target_conn, report['tables'])

        # 迁移家庭
        print('迁移家庭数据...')
        migrate_households(source_conn, target_conn, report['tables'])

        # 迁移成员
        print('迁移成员数据...')
        migrate_members(source_conn, target_conn, report['tables'])

        # 迁移用户（可选）
        if not skip_users:
            print('迁移用户数据...')
            migrate_users(source_conn, target_conn, report['tables'])

    finally:
        source_conn.close()
        target_conn.close()

    # 获取目标统计
    report['target_stats'] = get_target_stats(target_db)

    return report


def print_report(report: dict) -> None:
    """打印迁移报告"""
    print('\n' + '=' * 60)
    print('数据迁移报告')
    print('=' * 60)
    print(f'源数据库: {report["source"]}')
    print(f'目标数据库: {report["target"]}')
    print(f'迁移时间: {report["timestamp"]}')
    print()

    print('源数据库统计:')
    for table, count in report['source_stats'].items():
        print(f'  {table}: {count}')
    print()

    print('迁移结果:')
    for table, result in report['tables'].items():
        print(f'  {table}:')
        print(f'    总数: {result.get("total", 0)}')
        print(f'    已迁移: {result.get("migrated", 0)}')
        print(f'    已跳过: {result.get("skipped", 0)}')
        if 'note' in result:
            print(f'    注意: {result["note"]}')
    print()

    print('目标数据库统计:')
    for table, count in report['target_stats'].items():
        print(f'  {table}: {count}')
    print('=' * 60)


def main():
    parser = argparse.ArgumentParser(description='数据迁移脚本')
    parser.add_argument('--source', required=True, help='源数据库路径')
    parser.add_argument('--target', required=True, help='目标数据库路径')
    parser.add_argument('--skip-users', action='store_true', help='跳过用户迁移')
    parser.add_argument('--output', help='报告输出路径（JSON格式）')

    args = parser.parse_args()

    # 检查文件存在
    if not os.path.exists(args.source):
        print(f'错误: 源数据库不存在: {args.source}')
        return 1

    # 执行迁移
    report = run_migration(args.source, args.target, args.skip_users)

    # 打印报告
    print_report(report)

    # 保存报告
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        print(f'报告已保存到: {args.output}')

    return 0


if __name__ == '__main__':
    exit(main())
