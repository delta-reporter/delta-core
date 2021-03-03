from celery import Celery
from celery.result import AsyncResult
from data import crud

REDIS_URL = "redis://redis:6379/0"
BROKER_URL = "amqp://delta:123123@rabbit//"

CELERY = Celery("tasks", backend=REDIS_URL, broker=BROKER_URL)


def get_job(job_id):
    return AsyncResult(job_id, app=CELERY)


@CELERY.task()
def delete_project(project_id):

    message = crud.Delete.delete_project(project_id)

    return message
