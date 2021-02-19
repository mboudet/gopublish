import hashlib
import logging
import os
import request
import time
from datetime import datetime, timedelta

from go-publish.app import create_app, create_celery
from go-publish.db_models import PublishedFile
from go-publish.extensions import db
from go-publish.utils import celery_task_is_in_queue, get_celery_tasks, human_readable_size

from celery.signals import task_postrun, task_revoked

from flask_mail import Message


app = create_app(config='../local.cfg', is_worker=True)
app.app_context().push()
celery = create_celery(app)


#TODO : Define publish_file task (Move file, compute hash, add in DB)
# Checks need to be done before the task
@celery.task(bind=True, name="publish")
def publish_file(self, file_id):
    # Send task to copy file
    # (Copy file, create symlink)

    # Wait a bit in case the tasks begin just before it is recorded in the db
    time.sleep(2)
    p_file = PublishedFile.query.filter_by(id=file_id).one()
    p_file.task_id = self.request.id
    p_file.status = 'starting'
    db.session.commit()
    # Copy or move?
    shutil.copy(p_file.old_file_path, p_file.file_path)
    os.chmod(p_file.file_path, 0o0744)
    # Add duplicate potion (do not remove and link, just copy file)
    os.remove(p_file.old_file_path)
    os.symlink(p_file.file_path, p_file.old_file_path)

    p_file.status = 'hashing'
    p_file.size = os.path.getsize(p_file.file_path)
    db.session.commit()

    file_md5 = md5(p_file.file_path)
    p_file.hash = file_md5
    p_file.status = 'available'
    db.session.commit()

@celery.task(bind=True, name="pull")
def pull_file(self, file_id, email=""):
    # Send task to copy file
    # (Copy file, create symlink)
    p_file = PublishedFile.query.filter_by(id=file_id).one()
    pull_from_baricadr(p_file.file_path, email="")

@task_postrun.connect
def close_session(*args, **kwargs):
    # Flask SQLAlchemy will automatically create new sessions for you from
    # a scoped session factory, given that we are maintaining the same app
    # context, this ensures tasks have a fresh session (e.g. session errors
    # won't propagate across tasks)
    db.session.remove()

def pull_from_baricadr(file_path, email=""):
    url = "%s/pull" % app.config.get("BARICADR_URL")
    data = {"path": file_path}
    if email:
        data['email'] = email
    requests.post(url, auth=(app.config.get("BARICADR_USER"), app.config.get("BARICADR_PASSWORD")), json=data)
    # How do we manage failure? Mail admin?

def md5(fname):
    hash_md5 = hashlib.md5()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()
