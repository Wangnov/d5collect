# Gunicorn配置文件

# 绑定的IP和端口
bind = '0.0.0.0:9876'

# 工作进程数
workers = 4

# 工作模式
worker_class = 'sync'

# 超时时间
timeout = 120

# 日志级别
loglevel = 'info'

# 是否后台运行
daemon = False

# 指定应用模块
app_module = 'app:app'