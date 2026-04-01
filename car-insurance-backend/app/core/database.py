"""
数据库连接管理
支持连接池，提高数据库访问性能
"""
import pymysql
from pymysql.cursors import DictCursor
from dbutils.pooled_db import PooledDB
from app.core.config import settings

# 全局连接池实例
_db_pool = None


def get_db_pool():
    """
    获取或创建数据库连接池
    
    Returns:
        PooledDB: 数据库连接池对象
    """
    global _db_pool
    
    if _db_pool is None:
        _db_pool = PooledDB(
            creator=pymysql,
            maxconnections=20,  # 最大连接数
            mincached=5,        # 初始化时创建的空闲连接数
            maxcached=10,       # 连接池最大空闲连接数
            blocking=True,      # 连接池满时是否阻塞
            maxusage=None,      # 单个连接最大使用次数（None 为不限制）
            setsession=[],      # 会话初始化命令
            ping=1,             # 检查连接是否可用（1=check before execute）
            host=settings.DB_HOST,
            user=settings.DB_USER,
            password=settings.DB_PASSWORD,
            database=settings.DB_NAME,
            charset="utf8mb4",
            cursorclass=DictCursor,
            autocommit=False
        )
    
    return _db_pool


def get_db_connection():
    """
    从连接池获取数据库连接
    
    Returns:
        pymysql.Connection: 数据库连接对象
    """
    try:
        pool = get_db_pool()
        return pool.connection()
    except Exception as e:
        raise Exception(f"数据库连接失败：{str(e)}")


def close_db_pool():
    """
    关闭数据库连接池
    
    在应用关闭时调用，释放所有连接资源
    """
    global _db_pool
    
    if _db_pool is not None:
        _db_pool.close()
        _db_pool = None


def init_database():
    """
    初始化数据库（创建表结构）
    
    注意：生产环境应使用迁移工具（如 Alembic）管理表结构
    """
    import os
    
    schema_file = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        "database",
        "strategy_schema.sql"
    )
    
    if not os.path.exists(schema_file):
        raise FileNotFoundError(f"数据库表结构文件不存在：{schema_file}")
    
    conn = get_db_connection()
    try:
        with open(schema_file, 'r', encoding='utf-8') as f:
            sql_script = f.read()
        
        # 执行 SQL 脚本（按分号分割）
        statements = sql_script.split(';')
        
        cursor = conn.cursor()
        for statement in statements:
            statement = statement.strip()
            if statement and not statement.startswith('--'):
                cursor.execute(statement)
        
        conn.commit()
        print("数据库表结构初始化成功")
    except Exception as e:
        conn.rollback()
        raise Exception(f"数据库初始化失败：{str(e)}")
    finally:
        conn.close()
