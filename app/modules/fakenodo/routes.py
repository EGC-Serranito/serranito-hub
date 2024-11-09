from flask import render_template, jsonify, make_response
from app.modules.fakenodo import fakenodo_bp

base_url = '/fakenodo/api'


@fakenodo_bp.route(base_url, methods=['GET'])
def test_connection_fakenodo():
    response = {
        'status': 'success',
        'message': 'Connected to Fakenodo API'
    }
    return jsonify(response)

@fakenodo_bp.route(base_url, methods=['POST'])
def create_fakenodo():
    response = {
        'status': 'success',
        'message': 'Created deposition (Fakenodo API)'
    }
    return make_response(jsonify(response), 201)

@fakenodo_bp.route(base_url + '/<depositionid>/files', methods=['POST'])
def deposition_files_fakenodo(depositionid):
    response = {
        'status': 'success',
        'message': f'Created deposition with ID {depositionid} (Fakenodo API)'
    }
    return make_response(jsonify(response), 201)

@fakenodo_bp.route(base_url + '/<depositionid>', methods=['DELETE'])
def delete_deposition_fakenodo(depositionid):
    response = {
        'status': 'success',
        'message': f'Deleted deposition with ID {depositionid} (Fakenodo API)'
    }
    return make_response(jsonify(response), 200)

@fakenodo_bp.route(base_url + '/<depositionid>/actions/publish', methods=['POST'])
def publish_deposition_fakenodo(depositionid):
    response = {
        'status': 'success',
        'message': f'Published deposition with ID {depositionid} (Fakenodo API)'
    }
    return make_response(jsonify(response), 202)

@fakenodo_bp.route(base_url + '/<depositionid>', methods=['GET'])
def get_deposition_fakenodo(depositionid):
    response = {
        'status': 'success',
        'message': f'Got deposition with ID {depositionid} (Fakenodo API)',
        'doi': '10.5072/fakenodo.123456'
    }
    return make_response(jsonify(response), 200)





