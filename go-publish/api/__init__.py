import os

from go-publish.db_models import PublishedFile
from go-publish.extensions import db
from go-publish.utils import get_celery_worker_status

from celery.result import AsyncResult

from email_validator import EmailNotValidError, validate_email

from flask import (Blueprint, current_app, jsonify, make_response, send_file, request)
from flask_sqlalchemy.BaseQuery import get_or_404


api = Blueprint('api', __name__, url_prefix='/')


@api.route('/data/<file_id>', methods=['GET'])
def view_file():
    current_app.logger.info("API call: Getting file %s" % file_id)
    datafile = PublishedFile().query.get_or_404(file_id)
    data = {"file": datafile}
    if os.path.exists(datafile.file_path):
        if datafile.status == "pulling" and os.path.getsize(datafile.file_path) == datafile.size:
            datafile.status = "available"
            db.session.commit()
    elif not datafile.status == "pulling":
        repo = current_app.repos.get_repo(datafile.repo_path)
        if repo.has_baricadr:
            # TODO : Add baricadr check if the file exists
            datafile.status = "pullable"
        else:
            datafile.status = "unavailable"
        db.session.commit()

@api.route('/data/get/<file_id>', methods=['GET'])
def get_file():
    current_app.logger.info("API call: Get file %s" % file_id)
    datafile = PublishedFile().query.get_or_404(file_id)
    if os.path.exists(datafile.file_path):
        return send_file(datafile.file_path)
    else:
        datafile.status = "unavailable"
        db.session.commit()
        return make_response(jsonify({'error': 'Missing file'}), 404)


@api.route('/data/pull/<file_id>', methods=['POST'])
def pull_file():
    current_app.logger.info("API call: pulling file %s" % file_id)
    datafile = PublishedFile().query.get_or_404(file_id)

    email = None
    if 'email' in request.json:
        email = request.json['email']
        try:
            v = validate_email(email)
            email = [v["email"]]
        except EmailNotValidError as e:
            return jsonify({'error': str(e)}), 400

    if os.path.exists(datafile.file_path):
        return make_response(jsonify({'message': 'Ok'}), 200)
    else:
        repo = current_app.repos.get_repo(datafile.repo_path)
        if repo.has_baricadr:
            task = current_app.celery.send_task("pull", (datafile.id, email))
            return make_response(jsonify({'message': 'Ok'}), 200)
        else:
            return make_response(jsonify({'message': 'Not managed by Baricadr'}), 400)
