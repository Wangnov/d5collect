from .celery_worker import app
from .update_data import collect_all_costume_data, get_latest_costume_count

@app.task
def update_costumes_task():
    total_count = get_latest_costume_count()
    if total_count is not None:
        collect_all_costume_data(total_count)
    return f"Data update task finished. Total costumes: {total_count}"