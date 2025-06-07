#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
主路由模块
"""

import logging
from flask import render_template, request

from . import bp
from database import search_costumes_by_pinyin, log_request

# 获取logger实例
logger = logging.getLogger('my_app')


@bp.route('/', methods=['GET', 'POST'])
def index():
    """主页路由"""
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
                    
                    # 使用数据库搜索功能
                    char_matches = search_costumes_by_pinyin(char, limit=20)
                    costumes.append(char_matches)
                    total_matches += len(char_matches)
                
                result = list(zip(input_text, costumes))
                
                # 记录到文件日志（用于调试和追踪）
                logger.info(f"用户IP: {user_ip} | 输入内容: {input_text} | 匹配结果: {total_matches}个匹配")
                
                # 存储到数据库（用于Dashboard统计）
                log_request(user_ip, input_text, total_matches)

        return render_template('index.html', 
                            input_text=input_text,
                            result=result)

    except Exception as e:
        logger.error(f"处理 / 路由时发生未知错误: {e}", exc_info=True)
        return "服务器发生内部错误，请联系管理员或稍后再试。", 500