"""
Celery application.
"""
from celery import Celery

from worker.config import WorkerSettings
from worker.container import WorkerContainer

worker_settings = WorkerSettings()
celery = Celery(
    "tasks",
    broker=worker_settings.celery_broker_url,
    backend=worker_settings.celery_result_backend,
)

celery.autodiscover_tasks(["services.assistant"])

task_routes = {"services.assistant.tasks.download_and_send_post": {"queue": "downloads"}}


@celery.on_after_configure.connect
def init_di_container(sender, **kwargs):
    container = WorkerContainer()
    container.wire(modules=[__name__, "services.assistant.tasks"])
