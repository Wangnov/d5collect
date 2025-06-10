import json
import logging
from functools import wraps
from flask import render_template, request, Blueprint, flash, redirect, url_for, session, current_app
from werkzeug.security import check_password_hash

from database import get_request_stats, get_recent_requests

# 创建一个新的蓝图用于 Dashboard
dashboard_bp = Blueprint('dashboard', __name__, template_folder='../../templates')

logger = logging.getLogger('my_app')

def login_required(f):
    """登录保护装饰器"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            return redirect(url_for('dashboard.login'))
        return f(*args, **kwargs)
    return decorated_function

@dashboard_bp.route('/login', methods=['GET', 'POST'])
def login():
    """处理登录请求"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # 从配置中获取正确的用户名和密码哈希
        correct_username = current_app.config['DASHBOARD_USERNAME']
        correct_password_hash = current_app.config['DASHBOARD_PASSWORD_HASH']
        
        if username == correct_username and check_password_hash(correct_password_hash, password):
            session['logged_in'] = True
            logger.info(f"Dashboard 登录成功, IP: {request.remote_addr}")
            return redirect(url_for('dashboard.dashboard_view'))
        else:
            flash('无效的用户名或密码', 'error')
            logger.warning(f"Dashboard 登录失败, IP: {request.remote_addr}, 用户名: {username}")
            
    return render_template('login.html')

@dashboard_bp.route('/logout')
def logout():
    """处理登出请求"""
    session.pop('logged_in', None)
    flash('您已成功登出', 'info')
    return redirect(url_for('dashboard.login'))

@dashboard_bp.route('/')
@login_required
def dashboard_view():
    """显示 Dashboard 主页面"""
    try:
        # 获取统计数据
        days = request.args.get('days', 7, type=int)
        stats = get_request_stats(days=days)
        recent_reqs = get_recent_requests(limit=20)
        
        # 将所有动态数据打包到一个字典中
        page_data = {
            "stats": stats,
            "recent_requests": recent_reqs,
        }
        # 将整个数据包序列化为JSON字符串
        page_data_json = json.dumps(page_data)

        return render_template(
            'dashboard.html', 
            stats=stats, 
            recent_requests=recent_reqs,
            page_data_json=page_data_json, # 传递这个完整的JSON字符串
            active_days=days
        )
    except Exception as e:
        logger.error(f"加载 Dashboard 页面失败: {e}", exc_info=True)
        return "加载 Dashboard 时出错，请检查日志。", 500