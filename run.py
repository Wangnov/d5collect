#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
应用启动入口文件
"""

from app import create_app

app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9877, debug=False)