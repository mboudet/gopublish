from flask import (Blueprint, render_template)


view = Blueprint('view', __name__, url_prefix='/')


@view.route('/', defaults={'path': ''})
@view.route('/<path:path>')
def home(path):
    """Render the html
    """
    title = "Go-publish"

    return render_template('index.html', title=title)
