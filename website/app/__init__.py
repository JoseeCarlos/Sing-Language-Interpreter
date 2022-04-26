import imp
import os 
from flask import Flask


def create_app():
    app = Flask(__name__)
    app.config.from_mapping(
        SECRET_KEY='SENGRID_KEY',
        
    )

    from . import sli_page

    app.register_blueprint(sli_page.bp)

    return app