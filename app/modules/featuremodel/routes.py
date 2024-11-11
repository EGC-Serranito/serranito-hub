from flask import render_template
from app.modules.featuremodel import featuremodel_bp
from app.modules.featuremodel.models import FeatureModel


@featuremodel_bp.route('/featuremodel/<tag>', methods=['GET'])
def index(tag):
    if tag:
        feature_models = FeatureModel.query.filter(FeatureModel.fm_meta_data.tags.contains(tag)).all()
    else:
        feature_models = FeatureModel.query.all()

    return render_template('featuremodel/index.html', feature_models=feature_models, tag=tag)
