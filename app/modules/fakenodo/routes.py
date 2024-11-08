from flask import render_template
from app.modules.fakenodo import fakenodo_bp

base_url = '/fakenodo/api'


@fakenodo_bp.route(base_url, methods=['GET'])
def fakenodo():
    response = {
        'status': 'success',
        'message': 'Connected to Fake Zenodo API'
    }
    return response
