from flask import render_template
from app.modules.dashboard import dashboard_bp
from app.modules.dataset.services import DataSetService

datasetservice = DataSetService()


@dashboard_bp.route('/dashboard', methods=['GET'])
def index():
    author_names_dataset, dataset_counts = datasetservice.get_all_author_names_and_dataset_counts()
    author_names_view, view_counts = datasetservice.get_all_author_names_and_view_counts()
    return render_template('dashboard/index.html', author_names_dataset=author_names_dataset,
                           datasets_count=dataset_counts, author_names_view=author_names_view, view_counts=view_counts)