"""
数据库备份和还原服务
"""
import os
import shutil
import subprocess
import platform
from datetime import datetime
from src.models.base import engine, DB_PATH


class DatabaseService:
    """数据库备份和还原服务"""

    @staticmethod
    def open_database_folder():
        """
        打开数据库文件所在的文件夹

        Returns:
            tuple[bool, str]: (是否成功, 消息)
        """
        try:
            db_dir = os.path.dirname(DB_PATH)

            # 确保目录存在
            if not os.path.exists(db_dir):
                os.makedirs(db_dir)

            # 根据操作系统打开文件夹
            system = platform.system()

            if system == 'Windows':
                os.startfile(db_dir)
            elif system == 'Darwin':  # macOS
                subprocess.run(['open', db_dir])
            else:  # Linux
                subprocess.run(['xdg-open', db_dir])

            return True, f"已打开数据库文件夹：{db_dir}"

        except Exception as e:
            return False, f"打开文件夹失败：{str(e)}"

    @staticmethod
    def import_database(import_path: str) -> tuple[bool, str]:
        """
        从指定路径还原数据库

        Args:
            import_path: 导入文件的路径

        Returns:
            tuple[bool, str]: (是否成功, 消息)
        """
        try:
            # 确保导入文件存在
            if not os.path.exists(import_path):
                return False, "导入文件不存在"

            # 验证是否是有效的SQLite数据库文件
            if not DatabaseService._is_valid_sqlite_db(import_path):
                return False, "所选文件不是有效的SQLite数据库文件"

            # 关闭所有数据库连接
            engine.dispose()

            # 如果原数据库文件存在，重命名为备份文件
            if os.path.exists(DB_PATH):
                # 获取原文件名（不含扩展名）
                db_dir = os.path.dirname(DB_PATH)
                db_filename = os.path.basename(DB_PATH)
                db_name, db_ext = os.path.splitext(db_filename)

                # 生成备份文件名：原名_日期时间.db
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                backup_filename = f"{db_name}_{timestamp}{db_ext}"
                backup_path = os.path.join(db_dir, backup_filename)

                # 重命名原数据库文件
                os.rename(DB_PATH, backup_path)

            # 复制选择的文件到数据库位置
            shutil.copy2(import_path, DB_PATH)

            return True, "数据库已成功还原，原数据库已重命名备份"

        except Exception as e:
            return False, f"还原数据库失败：{str(e)}"

    @staticmethod
    def _is_valid_sqlite_db(file_path: str) -> bool:
        """
        验证文件是否为有效的SQLite数据库

        Args:
            file_path: 文件路径

        Returns:
            bool: 是否为有效的SQLite数据库
        """
        try:
            # 读取文件头
            with open(file_path, 'rb') as f:
                header = f.read(16)

            # SQLite数据库文件头应该是 "SQLite format 3\x00"
            return header[:15] == b'SQLite format 3'

        except Exception:
            return False

    @staticmethod
    def get_database_info() -> dict:
        """
        获取数据库信息

        Returns:
            dict: 数据库信息
        """
        try:
            info = {
                'path': DB_PATH,
                'exists': os.path.exists(DB_PATH),
                'size': '0 B',
                'last_modified': '未知'
            }

            if info['exists']:
                # 获取文件大小
                file_size = os.path.getsize(DB_PATH)
                info['size'] = DatabaseService._format_file_size(file_size)

                # 获取最后修改时间
                mtime = os.path.getmtime(DB_PATH)
                info['last_modified'] = datetime.fromtimestamp(mtime).strftime('%Y-%m-%d %H:%M:%S')

            return info

        except Exception as e:
            return {
                'path': DB_PATH,
                'exists': False,
                'size': '0 B',
                'last_modified': '未知',
                'error': str(e)
            }

    @staticmethod
    def _format_file_size(size_bytes: int) -> str:
        """
        格式化文件大小

        Args:
            size_bytes: 字节数

        Returns:
            str: 格式化后的文件大小
        """
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.2f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.2f} TB"
