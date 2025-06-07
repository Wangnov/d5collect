import sqlite3
import json
import logging
from datetime import datetime

# --- 配置 ---
DATABASE_FILE = 'database.db'
JSON_FILE = 'costumes_data.json'
logger = logging.getLogger('migration_script')
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def migrate_data():
    """
    读取 JSON 文件，将皮肤数据同步到数据库的 'costumes' 表中。
    此脚本可以重复运行以更新数据。
    """
    # 1. 连接数据库并创建新结构的表
    try:
        with sqlite3.connect(DATABASE_FILE) as conn:
            cursor = conn.cursor()
            # 创建一个结构更丰富的表来存储所有皮肤信息
            # 新增了 character_name, quality, quality_name, image_url, wiki_url 和 updated_at 字段
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS costumes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    character_name TEXT NOT NULL,
                    costume_name TEXT NOT NULL,
                    quality INTEGER NOT NULL,
                    quality_name TEXT,
                    image_url TEXT,
                    wiki_url TEXT,
                    updated_at TIMESTAMP NOT NULL,
                    -- 创建一个联合唯一索引，确保同一个角色不会有同名皮肤
                    UNIQUE(character_name, costume_name)
                )
            ''')
            # 为常用搜索字段创建索引，可以极大提升查询速度
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_costume_name ON costumes (costume_name)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_character_name ON costumes (character_name)")
            
            logger.info("'costumes' 表已更新至最新结构。")
            conn.commit()
    except sqlite3.Error as e:
        logger.critical(f"创建或更新 'costumes' 表结构失败: {e}")
        return

    # 2. 读取 JSON 文件
    try:
        with open(JSON_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            logger.info(f"成功从 '{JSON_FILE}' 加载了 {len(data)} 条待处理数据。")
    except (FileNotFoundError, json.JSONDecodeError) as e:
        logger.critical(f"读取或解析 '{JSON_FILE}' 文件失败: {e}")
        return
        
    # 3. 将数据同步到数据库
    inserted_count = 0
    updated_count = 0
    
    # 定义 SQL 语句，使用 ON CONFLICT 子句实现智能更新
    sql_upsert = """
        INSERT INTO costumes (
            character_name, costume_name, quality, quality_name, 
            image_url, wiki_url, updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(character_name, costume_name) DO UPDATE SET
            quality=excluded.quality,
            quality_name=excluded.quality_name,
            image_url=excluded.image_url,
            wiki_url=excluded.wiki_url,
            updated_at=excluded.updated_at;
    """

    try:
        with sqlite3.connect(DATABASE_FILE) as conn:
            cursor = conn.cursor()
            for item in data:
                # 准备要插入或更新的数据
                params = (
                    item.get('character'),
                    item.get('name'),
                    item.get('quality'),
                    item.get('quality_name'),
                    item.get('image_url'),
                    item.get('wiki_url'),
                    datetime.now() # 自动生成当前时间作为更新时间
                )
                
                cursor.execute(sql_upsert, params)
                
                # cursor.lastrowid 会在 INSERT 时返回新行的ID，UPDATE 时为 None 或 0
                # 我们可以通过这个粗略判断是插入还是更新
                if cursor.lastrowid:
                    inserted_count += 1
                else:
                    # 这不是一个精确的更新计数，但可以表示发生了冲突
                    # 精确计数需要更复杂的逻辑，目前够用
                    updated_count += 1

            conn.commit()
        logger.info(f"数据同步完成！新增: {inserted_count} 条, 更新/忽略: {updated_count} 条。")

    except sqlite3.Error as e:
        logger.critical(f"数据同步过程中发生数据库错误: {e}")

if __name__ == '__main__':
    migrate_data()