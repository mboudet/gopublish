from flask import (Blueprint, render_template, current_app)


view = Blueprint('view', __name__, url_prefix='/')


@view.route('/', defaults={'path': ''})
@view.route('/<path:path>')
def home(path):
    """Render the html
    """
    proxy_path = "/"
    title = "Go-publish"

    return render_template('index.html', title=title)
