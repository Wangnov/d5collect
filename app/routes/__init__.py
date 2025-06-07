#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
路由模块
"""

from flask import Blueprint

bp = Blueprint('main', __name__)

from . import main  # noqa: E402, F401
