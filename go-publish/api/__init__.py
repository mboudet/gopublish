import os

from go-publish.db_models import PublishedFile
from go-publish.extensions import db
from go-publish.utils import get_celery_worker_status

from celery.result import AsyncResult

from email_validator import EmailNotValidError, validate_email

from flask import (Blueprint, current_app, jsonify, make_response, request)


api = Blueprint('api', __name__, url_prefix='/')


# Endpoint to check if API is running for CLI tests
@api.route('/version', methods=['GET'])
def version():
    return jsonify({"version": current_app.config.get("GO-PUBLISH_VERSION", "unknown")})
