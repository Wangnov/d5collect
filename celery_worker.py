from celery import Celery

app = Celery('d5collect')
app.config_from_object('celeryconfig')

# 导入任务模块
app.autodiscover_tasks(['tasks'])