from flask import (
    Blueprint, render_template
)

bp = Blueprint('sli_page', __name__, url_prefix='/')

@bp.route('/', methods=['GET'])
def index():
    return render_template('homepage/index.html')