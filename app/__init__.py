#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Flask应用工厂
"""

import os
import json
import logging
import datetime
from flask import Flask
from werkzeug.middleware.proxy_fix import ProxyFix
from logging.handlers import TimedRotatingFileHandler

from .config import Config
from database import init_db


def setup_logging(app):
    """配置日志系统"""
    LOG_DIR = os.path.join('logs', 'app')
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
    
    return logger


def load_costume_data():
    """加载皮肤数据"""
    logger = logging.getLogger('my_app')
    
    try:
        with open('data/costumes_data.json', 'r', encoding='utf-8') as f:
            costumes_data = json.load(f)
        logger.info("皮肤数据 'costumes_data.json' 加载成功。")
        return costumes_data
    except FileNotFoundError:
        logger.critical("致命错误: 皮肤数据文件 'data/costumes_data.json' 未找到！应用无法启动。")
        exit()
    except json.JSONDecodeError:
        logger.critical("致命错误: 'data/costumes_data.json' 文件格式错误，无法解析！应用无法启动。")
        exit()


def create_app(config_class=Config):
    """应用工厂函数"""
    app = Flask(__name__, template_folder='../templates', static_folder='../static')
    app.config.from_object(config_class)
    
    # 设置日志
    setup_logging(app)
    
    # 中间件，用于在反向代理后获取真实IP
    app.wsgi_app = ProxyFix(
        app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1
    )
    
    # 加载皮肤数据
    costumes_data = load_costume_data()
    app.config['COSTUMES_DATA'] = costumes_data
    
    # 初始化数据库
    init_db()
    
    # 注册蓝图
    from .routes import bp as main_bp
    app.register_blueprint(main_bp)
    
    return app