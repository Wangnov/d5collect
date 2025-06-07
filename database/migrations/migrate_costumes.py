import sqlite3
import json
import logging
from datetime import datetime
from pypinyin import pinyin, Style

# --- 配置 ---
DATABASE_FILE = 'data/database.db'
JSON_FILE = 'data/costumes_data.json'
logger = logging.getLogger('migration_script')
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def generate_pinyin_index(name):
    """
    为皮肤名称生成拼音索引和首字符
    只处理首个有效字符（跳过标点符号）
    :param name: 皮肤名称
    :return: (pinyin_index, first_char) 元组
    """
    if not name:
        return '', ''
    
    # 找到第一个有效字符（跳过标点符号）
    first_char = ''
    pinyin_list = []
    
    for char in name:
        if char.isalpha() or '\u4e00' <= char <= '\u9fff':  # 英文字母或中文字符
            first_char = char.lower()
            
            # 只为首个有效字符生成拼音
            if '\u4e00' <= char <= '\u9fff':  # 中文字符
                # 获取所有可能的拼音（支持多音字）
                char_pinyins = pinyin(char, heteronym=True, style=Style.NORMAL)[0]
                pinyin_list.extend(char_pinyins)
            elif char.isalpha():  # 英文字符
                pinyin_list.append(char.lower())
            
            break  # 只处理第一个有效字符
    
    # 去重并连接
    pinyin_index = ','.join(list(set(pinyin_list)))
    
    return pinyin_index, first_char

def check_and_add_missing_columns():
    """
    检查表结构并添加缺失的字段
    """
    required_columns = {
        'id': 'INTEGER PRIMARY KEY AUTOINCREMENT',
        'character_name': 'TEXT NOT NULL',
        'costume_name': 'TEXT NOT NULL', 
        'quality': 'INTEGER NOT NULL',
        'quality_name': 'TEXT',
        'image_url': 'TEXT',
        'wiki_url': 'TEXT',
        'pinyin_index': 'TEXT',
        'first_char': 'TEXT',
        'updated_at': 'TIMESTAMP NOT NULL'
    }
    
    try:
        with sqlite3.connect(DATABASE_FILE) as conn:
            cursor = conn.cursor()
            
            # 首先创建表（如果不存在）
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS costumes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    character_name TEXT NOT NULL,
                    costume_name TEXT NOT NULL,
                    quality INTEGER NOT NULL,
                    quality_name TEXT,
                    image_url TEXT,
                    wiki_url TEXT,
                    pinyin_index TEXT,
                    first_char TEXT,
                    updated_at TIMESTAMP NOT NULL,
                    UNIQUE(character_name, costume_name)
                )
            ''')
            
            # 检查现有字段
            cursor.execute('PRAGMA table_info(costumes)')
            existing_columns = {row[1]: row[2] for row in cursor.fetchall()}
            
            # 添加缺失的字段
            for col_name, col_type in required_columns.items():
                if col_name not in existing_columns:
                    # 对于NOT NULL字段，需要提供默认值
                    if 'NOT NULL' in col_type:
                        if col_name == 'character_name':
                            default_value = "DEFAULT '未知角色'"
                        elif col_name == 'costume_name':
                            default_value = "DEFAULT '未知皮肤'"
                        elif col_name == 'quality':
                            default_value = "DEFAULT 0"
                        elif col_name == 'updated_at':
                            default_value = "DEFAULT CURRENT_TIMESTAMP"
                        else:
                            default_value = "DEFAULT ''"
                    else:
                        default_value = ""
                    
                    # 跳过主键字段（无法后添加）
                    if 'PRIMARY KEY' not in col_type:
                        alter_sql = f"ALTER TABLE costumes ADD COLUMN {col_name} {col_type.replace(' NOT NULL', '')} {default_value}"
                        try:
                            cursor.execute(alter_sql)
                            logger.info(f"已添加缺失字段: {col_name}")
                        except sqlite3.Error as e:
                            logger.warning(f"添加字段 {col_name} 失败: {e}")
            
            # 创建索引
            indexes = [
                "CREATE INDEX IF NOT EXISTS idx_costume_name ON costumes (costume_name)",
                "CREATE INDEX IF NOT EXISTS idx_character_name ON costumes (character_name)", 
                "CREATE INDEX IF NOT EXISTS idx_pinyin_index ON costumes (pinyin_index)",
                "CREATE INDEX IF NOT EXISTS idx_first_char ON costumes (first_char)"
            ]
            
            for index_sql in indexes:
                try:
                    cursor.execute(index_sql)
                except sqlite3.Error as e:
                    logger.warning(f"创建索引失败: {e}")
            
            conn.commit()
            logger.info("表结构检查和更新完成")
            
    except sqlite3.Error as e:
        logger.critical(f"检查表结构失败: {e}")
        return False
    
    return True

def migrate_data():
    """
    读取 JSON 文件，将皮肤数据同步到数据库的 'costumes' 表中。
    此脚本可以重复运行以更新数据。
    """
    # 1. 检查并更新表结构
    if not check_and_add_missing_columns():
        logger.critical("表结构检查失败，终止迁移")
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
            image_url, wiki_url, pinyin_index, first_char, updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(character_name, costume_name) DO UPDATE SET
            quality=excluded.quality,
            quality_name=excluded.quality_name,
            image_url=excluded.image_url,
            wiki_url=excluded.wiki_url,
            pinyin_index=excluded.pinyin_index,
            first_char=excluded.first_char,
            updated_at=excluded.updated_at;
    """

    try:
        with sqlite3.connect(DATABASE_FILE) as conn:
            cursor = conn.cursor()
            for item in data:
                # 生成拼音索引
                costume_name = item.get('name', '')
                pinyin_index, first_char = generate_pinyin_index(costume_name)
                
                # 准备要插入或更新的数据
                params = (
                    item.get('character'),
                    costume_name,
                    item.get('quality'),
                    item.get('quality_name'),
                    item.get('image_url'),
                    item.get('wiki_url'),
                    pinyin_index,
                    first_char,
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