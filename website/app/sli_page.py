from flask import (
    Blueprint, render_template
)

bp = Blueprint('sli_page', __name__, url_prefix='/')

@bp.route('/', methods=['GET'])
def index():
    return render_template('homepage/index.html')

@bp.route('/features', methods=['GET'])
def features():
    return render_template('features/index.html')

@bp.route('/news', methods=['GET'])
def news():
    return render_template('news/index.html')

@bp.route('/test', methods=['GET'])
def test():
    return render_template('test/index.html')