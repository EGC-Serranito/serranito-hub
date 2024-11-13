from flask import render_template, request, jsonify
from app.modules.explore import explore_bp
from app.modules.explore.forms import ExploreForm
from app.modules.explore.services import ExploreService


@explore_bp.route('/explore', methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        query = request.args.get('query', '')
        form = ExploreForm()
        return render_template('explore/index.html', form=form, query=query)

    if request.method == 'POST':
        criteria = request.get_json()
        datasets = ExploreService().filter(**criteria)
        return jsonify([dataset.to_dict() for dataset in datasets])


@explore_bp.route('/explore/feature_models/<tag>', methods=['GET'])
def feature_models_by_tag(tag):
    """Ruta para mostrar la lista de Feature Models asociados a un tag específico."""
    feature_models = ExploreService().filter_feature_models([tag])
    return render_template('explore/feature_models.html', feature_models=feature_models, tag=tag)


@explore_bp.route('/explore/tag_cloud', methods=['GET'])
def tag_cloud():
    """Nueva ruta para obtener la nube de etiquetas."""
    tag_cloud = ExploreService().get_tag_cloud()
    return jsonify(tag_cloud)
