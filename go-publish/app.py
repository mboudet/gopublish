import os

from go-publish.utils import get_celery_worker_status

from celery import Celery

from flask import Flask, g, render_template

from flask_apscheduler import APScheduler

from go-publish.api.file import file
from go-publish.api.view import view
# Import model classes for flaks migrate
from .db_models import PublishedFile  # noqa: F401
from .extensions import (celery, db, mail, migrate)
from .model import backends


__all__ = ('create_app', 'create_celery', )

BLUEPRINTS = (
    file,
    view
)

CONFIG_KEYS = (
    'SECRET_KEY',
    'BARICADR_REPOS_CONF',
    'MAIL_SENDER',
    'MAIL_ADMIN',
    'BASE_URL',
    'PROXY_HEADER'
    'TASK_LOG_DIR',
    'DEBUG',
    'TESTING',
    'BROKER_TRANSPORT',
    'CELERY_BROKER_URL',
    'CELERY_RESULT_BACKEND',
    'CELERY_TASK_SERIALIZER',
    'CELERY_DISABLE_RATE_LIMITS',
    'CELERY_ACCEPT_CONTENT',
    'SQLALCHEMY_DATABASE_URI',
    'SQLALCHEMY_ECHO',
    'SQLALCHEMY_TRACK_MODIFICATIONS',
    'MAIL_SERVER',
    'MAIL_PORT',
    'MAIL_USE_SSL',
    'MAIL_SENDER',
    'MAIL_SUPPRESS_SEND',
    'LOG_FOLDER',
    'USE_BARICADR',
    'BARICADR_URL',
    'BARICADR_USER',
    'BARICADR_PASSWORD'
)

def create_app(config=None, app_name='go-publish', blueprints=None, run_mode=None, is_worker=False):
    app = Flask(app_name,
                static_folder=os.path.join(os.path.dirname(__file__), '..', 'static'),
                template_folder="templates"
                )

    with app.app_context():

        # Can be used to check if some code is executed in a Celery worker, or in the web app
        app.is_worker = is_worker

        configs = {
            "dev": "go-publish.config.DevelopmentConfig",
            "test": "go-publish.config.TestingConfig",
            "prod": "go-publish.config.ProdConfig"
        }
        if run_mode:
            config_mode = run_mode
        else:
            config_mode = os.getenv('GO-PUBLISH_RUN_MODE', 'prod')

        if 'GO-PUBLISH_RUN_MODE' not in app.config:
            app.config['GO-PUBLISH_RUN_MODE'] = config_mode

        app.config.from_object(configs[config_mode])

        app.config.from_pyfile('../local.cfg', silent=True)
        if config:
            app.config.from_pyfile(config)

        app.config = _merge_conf_with_env_vars(app.config)

        if 'TASK_LOG_DIR' in app.config:
            app.config['TASK_LOG_DIR'] = os.path.abspath(app.config['TASK_LOG_DIR'])
        else:
            app.config['TASK_LOG_DIR'] = os.path.abspath(os.getenv('TASK_LOG_DIR', '/var/log/go-publish/tasks/'))

        if app.is_worker:
            os.makedirs(app.config['TASK_LOG_DIR'], exist_ok=True)

        if 'USE_BARICADR' in app.config['USE_BARICADR'] and app.config['USE_BARICADR'] is True:
            # TODO : Print error somewhere...
            if check_baricadr(app.config):
                app.baricadr_enabled = True

        # Load the list of go-publish repositories
        if 'GO-PUBLISH_REPOS_CONF' in app.config:
            repos_file = app.config['GO-PUBLISH_REPOS_CONF']
        else:
            repos_file = os.getenv('GO-PUBLISH_REPOS_CONF', '/etc/go-publish/repos.yml')
        app.repos = Repos(repos_file)

        if blueprints is None:
            blueprints = BLUEPRINTS

        blueprints_fabrics(app, blueprints)
        extensions_fabrics(app)
        configure_logging(app)

        gvars(app)

    return app


def create_celery(app):
    celery = Celery(app.import_name, broker=app.config['CELERY_BROKER_URL'])
    celery.conf.update(app.config)
    TaskBase = celery.Task

    class ContextTask(TaskBase):
        abstract = True

        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)
    celery.Task = ContextTask

    app.celery = celery
    return celery


def blueprints_fabrics(app, blueprints):
    """Configure blueprints in views."""

    for blueprint in blueprints:
        app.register_blueprint(blueprint)


def extensions_fabrics(app):
    db.init_app(app)
    mail.init_app(app)
    migrate.init_app(app, db)
    celery.config_from_object(app.config)


def gvars(app):
    @app.before_request
    def gdebug():
        if app.debug:
            g.debug = True
        else:
            g.debug = False


def configure_logging(app):
    """Configure file(info) and email(error) logging."""

    if app.debug or app.testing:
        # Skip debug and test mode. Just check standard output.
        return

    import logging
    from logging.handlers import SMTPHandler

    # Set log level
    if app.config['BARICADR_RUN_MODE'] == 'test':
        app.logger.setLevel(logging.DEBUG)
    else:
        app.logger.setLevel(logging.INFO)

    info_log = os.path.join(app.config['LOG_FOLDER'], 'info.log')
    info_file_handler = logging.handlers.RotatingFileHandler(info_log, maxBytes=100000, backupCount=10)
    info_file_handler.setLevel(logging.INFO)
    info_file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s '
        '[in %(pathname)s:%(lineno)d]')
    )
    app.logger.addHandler(info_file_handler)

    credentials = None
    if 'MAIL_USERNAME' in app.config and 'MAIL_PASSWORD' in app.config:
        credentials = (app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD'])
    mailhost = app.config['MAIL_SERVER']
    if 'MAIL_PORT' in app.config:
        mailhost = (app.config['MAIL_SERVER'], app.config['MAIL_PORT'])
    mail_handler = SMTPHandler(mailhost,
                               app.config['MAIL_SENDER'],
                               app.config['MAIL_ADMIN'],
                               'GO-PUBLISH failed!',
                               credentials)
    mail_handler.setLevel(logging.ERROR)
    mail_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s '
        '[in %(pathname)s:%(lineno)d]')
    )
    app.logger.addHandler(mail_handler)

def _merge_conf_with_env_vars(config):

    for key in CONFIG_KEYS:
        envval = os.getenv(key)
        if envval is not None:
            config[key] = envval

    return config

def check_baricadr(config):
    baricadr_enabled = False
    if (config.get("BARICADR_URL") and config.get("BARICADR_USER") and config.get("BARICADR_PASSWORD")):
        url = "%s/version" % app.config.get("BARICADR_URL")
        res = requests.get(url, auth=(app.config.get("BARICADR_USER"), app.config.get("BARICADR_PASSWORD")))
        # TODO : Maybe restrict compatible versions here?
        if res.status_code == 200 and "version" in res.json:
            baricadr_enabled = True
    return baricadr_enabled
