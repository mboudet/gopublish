import logging
import os
import time
from datetime import datetime, timedelta

from go-publish.app import create_app, create_celery
from go-publish.db_models import go-publishTask
from go-publish.extensions import db, mail
from go-publish.utils import celery_task_is_in_queue, get_celery_tasks, human_readable_size

from celery.signals import task_postrun, task_revoked

from flask_mail import Message


app = create_app(config='../local.cfg', is_worker=True)
app.app_context().push()
celery = create_celery(app)


#TODO : Define publish_file task (Move file, compute hash, add in DB)
# Checks need to be done before the task

@task_postrun.connect
def close_session(*args, **kwargs):
    # Flask SQLAlchemy will automatically create new sessions for you from
    # a scoped session factory, given that we are maintaining the same app
    # context, this ensures tasks have a fresh session (e.g. session errors
    # won't propagate across tasks)
    db.session.remove()
