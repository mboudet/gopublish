from flask import (Blueprint, jsonify, make_response)

from gopublish.db_models import Tag

tag = Blueprint('tag', __name__, url_prefix='/')


@tag.route('/api/tags/list', methods=['GET'])
def list_tags():
    tag_list = [tag.tag for tag in Tag.query.all()]

    return make_response(jsonify({'tags': tag_list}), 200)