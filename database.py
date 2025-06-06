import sqlite3
import datetime
import logging

# 获取在 app.py 中配置好的 logger 实例
# 这样数据库模块的日志会和主应用写在同一个文件里
logger = logging.getLogger('my_app')

DATABASE_FILE = 'dashboard.db'

def init_db():
    """
    初始化数据库，如果 'requests' 表不存在，则创建它。
    这个函数是幂等的，可以安全地多次调用。
    """
    try:
        # 使用 with 语句可以确保连接在使用后被安全关闭
        with sqlite3.connect(DATABASE_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS requests (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_ip TEXT NOT NULL,
                    input_text TEXT NOT NULL,
                    match_count INTEGER NOT NULL,
                    created_at TIMESTAMP NOT NULL
                )
            ''')
            conn.commit()
            logger.info("数据库初始化成功，'requests' 表已确认存在。")
    except sqlite3.Error as e:
        # 记录任何在数据库初始化期间发生的错误
        logger.critical(f"数据库初始化失败！错误: {e}", exc_info=True)
        # 如果数据库都无法创建，这通常是严重问题，直接退出程序
        raise

def log_request(user_ip: str, input_text: str, match_count: int):
    """
    将一次用户请求的数据记录到数据库中。
    """
    try:
        with sqlite3.connect(DATABASE_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO requests (user_ip, input_text, match_count, created_at) VALUES (?, ?, ?, ?)",
                (user_ip, input_text, match_count, datetime.datetime.now())
            )
            conn.commit()
    except sqlite3.Error as e:
        # 如果只是单次写入失败，记录错误即可，不需要让整个应用崩溃
        logger.error(f"写入数据库失败！数据: IP={user_ip}, Input={input_text}, Error={e}", exc_info=True)