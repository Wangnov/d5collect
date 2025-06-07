import sqlite3
import datetime
import logging
import threading
from contextlib import contextmanager
from typing import List, Dict, Any

# 获取在 app.py 中配置好的 logger 实例
# 这样数据库模块的日志会和主应用写在同一个文件里
logger = logging.getLogger('my_app')

DATABASE_FILE = 'dashboard.db'

# 简单的连接池实现
class ConnectionPool:
    def __init__(self, database_file: str, max_connections: int = 10):
        self.database_file = database_file
        self.max_connections = max_connections
        self._connections = []
        self._lock = threading.Lock()
    
    def get_connection(self):
        with self._lock:
            if self._connections:
                return self._connections.pop()
            else:
                conn = sqlite3.connect(self.database_file, check_same_thread=False)
                # 优化数据库性能配置
                conn.execute('PRAGMA journal_mode=WAL')
                conn.execute('PRAGMA synchronous=NORMAL')
                conn.execute('PRAGMA cache_size=10000')
                conn.execute('PRAGMA temp_store=MEMORY')
                return conn
    
    def return_connection(self, conn):
        with self._lock:
            if len(self._connections) < self.max_connections:
                self._connections.append(conn)
            else:
                conn.close()

# 全局连接池实例
_connection_pool = ConnectionPool(DATABASE_FILE)

@contextmanager
def get_db_connection():
    """获取数据库连接的上下文管理器"""
    conn = _connection_pool.get_connection()
    try:
        yield conn
    finally:
        _connection_pool.return_connection(conn)

def init_db():
    """
    初始化数据库，创建表和索引。
    这个函数是幂等的，可以安全地多次调用。
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # 创建表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS requests (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_ip TEXT NOT NULL,
                    input_text TEXT NOT NULL,
                    match_count INTEGER NOT NULL,
                    created_at TIMESTAMP NOT NULL
                )
            ''')
            
            # 创建索引以提高查询性能
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_user_ip ON requests(user_ip)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_created_at ON requests(created_at)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_ip_time ON requests(user_ip, created_at)')
            
            conn.commit()
            logger.info("数据库初始化成功，'requests' 表和索引已确认存在。")
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
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO requests (user_ip, input_text, match_count, created_at) VALUES (?, ?, ?, ?)",
                (user_ip, input_text, match_count, datetime.datetime.now())
            )
            conn.commit()
    except sqlite3.Error as e:
        # 如果只是单次写入失败，记录错误即可，不需要让整个应用崩溃
        logger.error(f"写入数据库失败！数据: IP={user_ip}, Input={input_text}, Error={e}", exc_info=True)

def log_requests_batch(requests_data: List[Dict[str, Any]]):
    """
    批量插入用户请求数据。
    
    Args:
        requests_data: 包含请求数据的字典列表，每个字典应包含:
                    {'user_ip': str, 'input_text': str, 'match_count': int}
    """
    if not requests_data:
        return
    
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            current_time = datetime.datetime.now()
            
            # 准备批量插入的数据
            batch_data = [
                (req['user_ip'], req['input_text'], req['match_count'], current_time)
                for req in requests_data
            ]
            
            cursor.executemany(
                "INSERT INTO requests (user_ip, input_text, match_count, created_at) VALUES (?, ?, ?, ?)",
                batch_data
            )
            conn.commit()
            logger.info(f"批量插入成功，共插入 {len(requests_data)} 条记录")
    except sqlite3.Error as e:
        logger.error(f"批量写入数据库失败！错误: {e}", exc_info=True)

def get_request_stats(days: int = 7) -> Dict[str, Any]:
    """
    获取最近N天的请求统计数据。
    
    Args:
        days: 统计最近多少天的数据，默认7天
    
    Returns:
        包含统计信息的字典
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # 计算起始时间
            start_date = datetime.datetime.now() - datetime.timedelta(days=days)
            
            # 总请求数
            cursor.execute(
                "SELECT COUNT(*) FROM requests WHERE created_at >= ?",
                (start_date,)
            )
            total_requests = cursor.fetchone()[0]
            
            # 独立IP数
            cursor.execute(
                "SELECT COUNT(DISTINCT user_ip) FROM requests WHERE created_at >= ?",
                (start_date,)
            )
            unique_ips = cursor.fetchone()[0]
            
            # 平均匹配数
            cursor.execute(
                "SELECT AVG(match_count) FROM requests WHERE created_at >= ?",
                (start_date,)
            )
            avg_matches = cursor.fetchone()[0] or 0
            
            # 最活跃的IP（前5个）
            cursor.execute(
                "SELECT user_ip, COUNT(*) as request_count FROM requests WHERE created_at >= ? GROUP BY user_ip ORDER BY request_count DESC LIMIT 5",
                (start_date,)
            )
            top_ips = cursor.fetchall()
            
            # 每日请求数统计
            cursor.execute(
                "SELECT DATE(created_at) as date, COUNT(*) as count FROM requests WHERE created_at >= ? GROUP BY DATE(created_at) ORDER BY date",
                (start_date,)
            )
            daily_stats = cursor.fetchall()
            
            return {
                'period_days': days,
                'total_requests': total_requests,
                'unique_ips': unique_ips,
                'avg_matches': round(avg_matches, 2),
                'top_ips': [{'ip': ip, 'count': count} for ip, count in top_ips],
                'daily_stats': [{'date': date, 'count': count} for date, count in daily_stats]
            }
    except sqlite3.Error as e:
        logger.error(f"获取统计数据失败！错误: {e}", exc_info=True)
        return {}

def get_recent_requests(limit: int = 100) -> List[Dict[str, Any]]:
    """
    获取最近的请求记录。
    
    Args:
        limit: 返回的记录数量限制，默认100条
    
    Returns:
        请求记录列表
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT user_ip, input_text, match_count, created_at FROM requests ORDER BY created_at DESC LIMIT ?",
                (limit,)
            )
            
            results = cursor.fetchall()
            return [
                {
                    'user_ip': row[0],
                    'input_text': row[1],
                    'match_count': row[2],
                    'created_at': row[3]
                }
                for row in results
            ]
    except sqlite3.Error as e:
        logger.error(f"获取最近请求失败！错误: {e}", exc_info=True)
        return []