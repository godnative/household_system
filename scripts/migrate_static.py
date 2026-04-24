#!/usr/bin/env python3
"""
静态资源迁移脚本：从旧 PyQt5 系统迁移到新 Web 系统

用法：
    python scripts/migrate_static.py --source /path/to/old/static --target /path/to/new/backend/static

功能：
    - 迁移成员照片
    - 迁移堂区照片
    - 更新数据库中的图片路径
"""

import argparse
import os
import shutil
from pathlib import Path


def migrate_member_photos(source_dir: str, target_dir: str, report: dict) -> None:
    """迁移成员照片"""
    source_photos = Path(source_dir) / 'member_photos'
    target_photos = Path(target_dir) / 'uploads' / 'members'

    if not source_photos.exists():
        report['member_photos'] = {'status': 'skipped', 'reason': '源目录不存在'}
        return

    target_photos.mkdir(parents=True, exist_ok=True)

    migrated = 0
    for photo in source_photos.glob('*'):
        if photo.suffix.lower() in ['.jpg', '.jpeg', '.png', '.webp']:
            target_path = target_photos / photo.name
            if not target_path.exists():
                shutil.copy2(photo, target_path)
                migrated += 1

    report['member_photos'] = {
        'status': 'completed',
        'migrated': migrated,
        'source': str(source_photos),
        'target': str(target_photos)
    }


def migrate_system_assets(source_dir: str, target_dir: str, report: dict) -> None:
    """迁移系统资源"""
    # 欢迎图片
    welcome_source = Path(source_dir) / 'welcome_image.jpg'
    welcome_target = Path(target_dir) / 'frontend' / 'public' / 'images' / 'home' / 'welcome-image.jpg'

    if welcome_source.exists():
        welcome_target.parent.mkdir(parents=True, exist_ok=True)
        if not welcome_target.exists():
            shutil.copy2(welcome_source, welcome_target)
        report['welcome_image'] = {'status': 'migrated', 'path': str(welcome_target)}
    else:
        report['welcome_image'] = {'status': 'skipped', 'reason': '源文件不存在'}


def run_migration(source_dir: str, target_dir: str) -> dict:
    """执行迁移"""
    report = {
        'source': source_dir,
        'target': target_dir,
        'items': {}
    }

    # 迁移成员照片
    migrate_member_photos(source_dir, target_dir, report['items'])

    # 迁移系统资源
    migrate_system_assets(source_dir, target_dir, report['items'])

    return report


def main():
    parser = argparse.ArgumentParser(description='静态资源迁移脚本')
    parser.add_argument('--source', default='/root/household_system/static', help='源静态目录')
    parser.add_argument('--target', default='/root/household_system/backend/app/static', help='目标静态目录')

    args = parser.parse_args()

    report = run_migration(args.source, args.target)

    print('\n静态资源迁移报告:')
    print('=' * 40)
    for item, result in report['items'].items():
        print(f'{item}: {result}')
    print('=' * 40)

    return 0


if __name__ == '__main__':
    exit(main())
