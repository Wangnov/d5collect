#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
应用配置文件
"""

import os


class Config:
    """基础配置类"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # 数据库配置
    DATABASE_FILE = 'data/database.db'
        
    # 日志配置
    LOG_DIR = 'logs/app'
    
    # 服务器配置
    HOST = '0.0.0.0'
    PORT = 9877

    # Dashboard 配置
    DASHBOARD_USERNAME = 'wangnov'
    # 'wangnov1' 的哈希值
    DASHBOARD_PASSWORD_HASH = 'pbkdf2:sha256:600000$6T3hBzRB7VJQ5x6n$704ec54bbd046aefecc35992b7850e7f3ad2654211550648c09b63384de1e0ae'


class DevelopmentConfig(Config):
    """开发环境配置"""
    DEBUG = True


class ProductionConfig(Config):
    """生产环境配置"""
    DEBUG = False


class TestingConfig(Config):
    """测试环境配置"""
    TESTING = True
    DATABASE_FILE = ':memory:'  # 使用内存数据库进行测试


# 配置字典
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}