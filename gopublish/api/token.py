import datetime

from flask import (Blueprint, current_app, jsonify, make_response, request)

from gopublish.db_models import Token
from gopublish.extensions import db
from gopublish.utils import authenticate_user, is_valid_uuid

import timedelta

token = Blueprint('file', __name__, url_prefix='/')


@token.route('/api/token/get', methods=['POST'])
def create_token():

    if not request.json:
        return make_response(jsonify({'error': 'Missing body'}), 400)

    if not (request.json.get("username") and request.json.get("password")):
        return make_response(jsonify({'error': 'Missing either username or password in body'}), 400)

    # Only check ldap in prod
    if current_app.config['GOPUBLISH_RUN_MODE'] == "prod":
        if not authenticate_user(request.json.get("username"), request.json.get("password"), current_app.config):
            return make_response(jsonify({'error': 'Incorrect credentials'}), 401)

    expire_date = datetime.datetime.utcnow() + timedelta(hours=current_app.config.get('TOKEN_DURATION'))
    token = Token(username=request.json.get("username"), expire_at=expire_date)
    db.session.add(token)
    db.session.commit()
    return make_response(jsonify({'token': token.id}), 200)


@token.route('/api/token/delete/<token_id>', methods=['DELETE'])
def revoke_token(token_id):

    if not is_valid_uuid(token_id):
        return make_response(jsonify({'error': 'Malformed token'}), 400)

    token = Token().query.get(token_id)

    if not token:
        return make_response(jsonify({'error': 'Token not found'}), 404)

    db.session.delete(token)
    db.session.commit()

    return make_response(jsonify({'status': 'Token revoked'}), 200)
