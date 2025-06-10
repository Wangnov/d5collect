#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Flask应用工厂
"""

import os
import logging
import datetime
import shutil

# 兼容性导入 TOML 解析库    
try:
    import tomllib  # 优先使用 Python 3.11+ 的标准库
except ImportError:
    import tomli as tomllib # type: ignore # 在低版本中回退到 tomli，并使用相同名称

from flask import Flask
from werkzeug.middleware.proxy_fix import ProxyFix
from werkzeug.security import generate_password_hash
from logging.handlers import TimedRotatingFileHandler
from whitenoise import WhiteNoise # 导入 WhiteNoise

from .config import Config
from database import init_db


def setup_logging(app):
    LOG_DIR = os.path.join('logs', 'app')
    os.makedirs(LOG_DIR, exist_ok=True)
    log_file_path = os.path.join(LOG_DIR, f'{datetime.date.today()}.log')
    logger = logging.getLogger('my_app')
    logger.setLevel(logging.INFO)
    handler = TimedRotatingFileHandler(
        log_file_path, when='D', interval=1, backupCount=999, encoding='utf-8'
    )
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - [%(funcName)s] - %(message)s')
    handler.setFormatter(formatter)
    if not logger.handlers:
        logger.addHandler(handler)
    return logger


def load_external_config(app):
    """
    从 toml 文件加载外部配置。
    如果配置文件不存在，则从模板文件复制一份。
    """
    config_path = os.path.join(app.root_path, '..', 'main_config.toml')
    template_path = os.path.join(app.root_path, '..', 'main_config_template.toml')

    if not os.path.exists(config_path):
        app.logger.warning(f"配置文件 '{config_path}' 不存在。")
        try:
            shutil.copyfile(template_path, config_path)
            app.logger.info(f"已根据模板 '{template_path}' 创建新的配置文件。")
        except FileNotFoundError:
            app.logger.error(f"无法创建配置文件，因为模板文件 '{template_path}' 也不存在！")
            return
        except Exception as e:
            app.logger.error(f"从模板创建配置文件时出错: {e}")
            return

    try:
        with open(config_path, 'rb') as f:
            config_data = tomllib.load(f)

        dashboard_config = config_data.get('dashboard', {})
        username = dashboard_config.get('username')
        password = dashboard_config.get('password')

        if username and password:
            app.config['DASHBOARD_USERNAME'] = username
            app.config['DASHBOARD_PASSWORD_HASH'] = generate_password_hash(password)
            app.logger.info("成功从 main_config.toml 加载 Dashboard 凭据。")
        else:
            app.logger.warning("在 main_config.toml 中未找到有效的 Dashboard 凭据。")

    except Exception as e:
        app.logger.error(f"加载 main_config.toml 时出错: {e}")


def create_app(config_class=Config):
    """应用工厂函数"""
    app = Flask(__name__, template_folder='../templates', static_folder='../static')
    app.config.from_object(config_class)

    setup_logging(app)

    with app.app_context():
        load_external_config(app)

    # 使用 WhiteNoise 包装应用，使其能够处理静态文件
    app.wsgi_app = WhiteNoise(app.wsgi_app, root=os.path.join(os.path.dirname(app.root_path), 'static'))

    app.wsgi_app = ProxyFix(
        app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1
    )

    # 初始化数据库
    init_db()

    # 注册主应用蓝图
    from .routes import bp as main_bp
    app.register_blueprint(main_bp)

    # 注册 Dashboard 蓝图
    from .routes.dashboard import dashboard_bp
    app.register_blueprint(dashboard_bp, url_prefix='/dashboard')

    return app