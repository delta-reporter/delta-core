import os
from celery import Celery
from celery.result import AsyncResult
from data import crud

REDIS_URL = os.environ["REDIS_URL"]
BROKER_URL = os.environ["BROKER_URL"]

CELERY = Celery("tasks", backend=REDIS_URL, broker=BROKER_URL)


def get_job(job_id):
    return AsyncResult(job_id, app=CELERY)


@CELERY.task()
def delete_project(project_id):

    message = crud.Delete.delete_project(project_id)

    return message
