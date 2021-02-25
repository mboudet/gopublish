import base64
import os

from gopublish.db_models import PublishedFile
from gopublish.extensions import db
from gopublish.utils import get_celery_worker_status

from email_validator import EmailNotValidError, validate_email

from flask import (Blueprint, current_app, jsonify, make_response, send_file, request)


file = Blueprint('file', __name__, url_prefix='/')


@file.route('/api/view/<file_id>', methods=['GET'])
def view_file(file_id):
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
    return make_response(jsonify(data), 200)


@file.route('/api/download/<file_id>', methods=['GET'])
def download_file(file_id):
    current_app.logger.info("API call: Get file %s" % file_id)
    datafile = PublishedFile().query.get_or_404(file_id)
    if os.path.exists(datafile.file_path):
        return send_file(datafile.file_path)
    else:
        datafile.status = "unavailable"
        db.session.commit()
        return make_response(jsonify({'error': 'Missing file'}), 404)


@file.route('/api/pull/<file_id>', methods=['POST'])
def pull_file(file_id):
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
        return make_response(jsonify({'message': 'File already available'}), 200)
    else:
        repo = current_app.repos.get_repo(datafile.repo_path)
        if repo.has_baricadr:
            current_app.celery.send_task("pull", (datafile.id, email))
            return make_response(jsonify({'message': 'Ok'}), 200)
        else:
            return make_response(jsonify({'message': 'Not managed by Baricadr'}), 400)


@file.route('/api/publish', methods=['POST'])
def publish_file():

    if current_app.config['GO-PUBLISH_RUN_MODE'] == "prod":
        proxy_header = current_app.config["PROXY_HEADER"]
        username = request.headers.get(proxy_header)
        if not username:
            return jsonify({'error': 'Missing username in proxy header'}), 401
    else:
        username = request.json.get("username")
        if not username:
            return jsonify({'error': 'Missing username in body'}), 401

    if 'path' not in request.json:
        return jsonify({'error': 'Missing "path"'}), 400
    # Normalize path

    version = 1
    if 'version' in request.json:
        version = request.json['version']
        try:
            version = int(version)
            if not version > 0:
                raise ValueError()
        except ValueError:
            return make_response(jsonify({'error': "Value %s is not an integer > 0" % version}), 400)

    if not os.path.exists(request.json['path']):
        return make_response(jsonify({'error': 'File not found at path %s' % request.json['path']}), 404)

    celery_status = get_celery_worker_status(current_app.celery)
    if celery_status['availability'] is None:
        current_app.logger.error("Received publish request on path '%s', but no Celery worker available to process the request. Aborting." % request.json['path'])
        return jsonify({'error': 'No Celery worker available to process the request'}), 400

    email = None
    if 'email' in request.json:
        email = request.json['email']
        try:
            v = validate_email(email)
            email = [v["email"]]
        except EmailNotValidError as e:
            return make_response(jsonify({'error': str(e)}), 400)

    contact = None
    if 'contact' in request.json:
        contact = request.json['contact']
        try:
            v = validate_email(contact)
            email = [v["contact"]]
        except EmailNotValidError as e:
            return make_response(jsonify({'error': str(e)}), 400)

    repo = current_app.repos.get_repo(request.json['path'])
    if not repo:
        return make_response(jsonify({'error': 'File %s is not in any publishable repository' % request.json['path']}), 404)

    checks = repo.check_publish_file(request.json['path'], username=username, version=version)

    if checks["error"]:
        return make_response(jsonify({'error': 'Error checking file : %s' % checks["error"]}), 400)

    file_id = repo.publish_file(request.json['path'], version=version, mail=email, contact=contact)

    res = "File registering with id %s. An email will be sent to you when the file is ready." % file_id if email else "File registering with id %s. it should be ready soon" % file_id

    return make_response(jsonify({'message': res}), 200)


# Get file ID from file path (base64 encoded)
@file.route('/uri/<path>', methods=['GET'])
def get_file_uri(encoded_path):
    path = base64.b64decode(encoded_path)
    files = PublishedFile.query(PublishedFile.id).filter(PublishedFile.file_path == path | PublishedFile.old_file_path == path)
    return make_response(jsonify({'ids': files}), 200)