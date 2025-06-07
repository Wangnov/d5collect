# app.py

import os
import json
import logging
import datetime
from flask import Flask, render_template, request
from werkzeug.middleware.proxy_fix import ProxyFix
from logging.handlers import TimedRotatingFileHandler

import database

# ==================== 日志配置开始 ====================

LOG_DIR = os.path.join('log', 'app')
os.makedirs(LOG_DIR, exist_ok=True)

log_file_path = os.path.join(LOG_DIR, f'{datetime.date.today()}.log')
logger = logging.getLogger('my_app')
logger.setLevel(logging.INFO)

# when='D' 表示按天分割, backupCount 保留旧文件数量
handler = TimedRotatingFileHandler(
    log_file_path,
    when='D',
    interval=1,
    backupCount=999,
    encoding='utf-8'
)

formatter = logging.Formatter('%(asctime)s - %(levelname)s - [%(funcName)s] - %(message)s')
handler.setFormatter(formatter)

if not logger.handlers:
    logger.addHandler(handler)

# ==================== 日志配置结束 ====================

app = Flask(__name__)

# 中间件，用于在反向代理后获取真实IP
app.wsgi_app = ProxyFix(
    app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1
)

# --- 数据加载 ---
# 将数据加载放入 try-except 块中，如果关键文件丢失，应用将无法启动并记录致命错误
try:
    with open('costumes_data.json', 'r', encoding='utf-8') as f:
        costumes_data = json.load(f)
    logger.info("皮肤数据 'costumes_data.json' 加载成功。")
except FileNotFoundError:
    logger.critical("致命错误: 皮肤数据文件 'costumes_data.json' 未找到！应用无法启动。")
    exit() # 如果数据文件是必须的，直接退出程序
except json.JSONDecodeError:
    logger.critical("致命错误: 'costumes_data.json' 文件格式错误，无法解析！应用无法启动。")
    exit()

# --- 数据库初始化 ---
database.init_db()


@app.route('/', methods=['GET', 'POST'])
def index():
    try:
        input_text = None
        result = []
        user_ip = request.remote_addr

        if request.method == 'POST':
            input_text = request.form.get('input_text')
            if input_text:
                # 对输入的每个字符进行匹配
                costumes = []
                total_matches = 0
                
                for char in input_text:
                    # 跳过空格和标点符号
                    if char.isspace() or not (char.isalpha() or '\u4e00' <= char <= '\u9fff'):
                        costumes.append([])
                        continue
                    
                    # 使用新的数据库搜索功能
                    char_matches = database.search_costumes_by_pinyin(char, limit=20)
                    costumes.append(char_matches)
                    total_matches += len(char_matches)
                
                result = list(zip(input_text, costumes))
                
                # 记录到文件日志（用于调试和追踪）
                logger.info(f"用户IP: {user_ip} | 输入内容: {input_text} | 匹配结果: {total_matches}个匹配")
                
                # 存储到数据库（用于Dashboard统计）
                database.log_request(user_ip, input_text, total_matches)

        return render_template('index.html', 
                            input_text=input_text,
                            result=result)

    except Exception as e:
        logger.error(f"处理 / 路由时发生未知错误: {e}", exc_info=True)
        return "服务器发生内部错误，请联系管理员或稍后再试。", 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9877)