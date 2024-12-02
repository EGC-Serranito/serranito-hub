from flask import render_template
from app.modules.dashboard import dashboard_bp
from flask import request
from app.modules.dashboard.services import DashBoardService

dashboardservice = DashBoardService()


@dashboard_bp.route('/dashboard', methods=['GET', 'POST'])
def index():
    filter_type = request.args.get("filter", "day")  # Default to "day"
    author_names_dataset, dataset_counts = dashboardservice.get_all_author_names_and_dataset_counts()
    author_names_view, view_counts = dashboardservice.get_all_author_names_and_view_counts()
    dataset_names, total_sizes = dashboardservice.get_datasets_and_total_sizes()
    view_dates, view_counts_over_time = dashboardservice.get_views_over_time_with_filter(filter_type)
    publication_types_count = dashboardservice.get_publication_types_data()
    if request.method == 'POST':
        filter_type = request.json.get('filter', 'day')
        view_dates, view_counts_over_time = dashboardservice.get_views_over_time_with_filter(filter_type)
        return {
            "view_dates": view_dates,
            "view_counts_over_time": view_counts_over_time
        }
    return render_template(
        'dashboard/index.html',
        author_names_dataset=author_names_dataset,
        datasets_count=dataset_counts,
        author_names_view=author_names_view,
        view_counts=view_counts,
        dataset_names=dataset_names,
        total_sizes=total_sizes,
        view_dates=view_dates,
        view_counts_over_time=view_counts_over_time,
        publication_types_count=publication_types_count,
        current_filter=filter_type
    )
