import hashlib
import os
import requests
import shutil
import time

from gopublish.app import create_app, create_celery
from gopublish.db_models import PublishedFile
from gopublish.extensions import db
from gopublish.extensions import mail

from celery.signals import task_postrun

from flask_mail import Message


app = create_app(config='../local.cfg', is_worker=True)
app.app_context().push()
celery = create_celery(app)


def on_failure(self, exc, task_id, args, kwargs, einfo):

    app.logger.warning("Task %s failed. Exception raised: %s" % (task_id, str(exc)))
    p_file = PublishedFile.query.filter_by(id=args[0]).one()
    p_file.error = str(exc)

    # args[1] is the email address
    if args[1]:
        body = """Hello,
Your publishing request on file '{path}' failed, with the following error:
{error}
Contact the administrator for more info.
Cheers
"""
        msg = Message(subject="Go-publish: Publishing task on {path} failed".format(path=p_file.old_file_path),
                      body=body.format(path=p_file.old_file_path, error=str(exc)),
                      sender=app.config.get('MAIL_SENDER', 'from@example.com'),
                      recipients=args[1])
        mail.send(msg)

    p_file.status = 'failed'
    db.session.commit()


@celery.task(bind=True, name="publish", on_failure=on_failure)
def publish_file(self, file_id, email=""):
    # Send task to copy file
    # (Copy file, create symlink)

    # Wait a bit in case the tasks begin just before it is recorded in the db
    time.sleep(2)
    p_file = PublishedFile.query.filter_by(id=file_id).one()
    p_file.task_id = self.request.id
    p_file.status = 'starting'
    db.session.commit()
    # Copy or move?
    repo = app.repos.get_repo(p_file.repo_path)

    if repo.copy_files:
        shutil.copy(p_file.old_file_path, p_file.file_path)
    else:
        shutil.move(p_file.old_file_path, p_file.file_path)
        os.symlink(p_file.file_path, p_file.old_file_path)

    os.chmod(p_file.file_path, 0o0744)

    file_md5 = md5(p_file.file_path)
    p_file.hash = file_md5
    p_file.status = 'available'
    db.session.commit()

    if email:
        body = """Hello,
Your publishing request on file '{path}' succeded.
Your file should be available here : {file_url}
Cheers
"""
        msg = Message(subject="Go-publish: Publishing task on {path} succeded".format(path=p_file.old_file_path),
                      body=body.format(path=p_file.old_file_path, file_url="%s/data/%s" % (app.config.get("BASE_URL"), p_file.id)),
                      sender=app.config.get('MAIL_SENDER', 'from@example.com'),
                      recipients=email)
        mail.send(msg)


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
