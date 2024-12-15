from app.modules.dataset.repositories import (
    DataSetRepository,
)
from app.modules.dashboard.repositories import DashboardRepository
from core.services.BaseService import BaseService


class DashBoardService(BaseService):
    def __init__(self):
        super().__init__(DataSetRepository())
        self.dashboard_repository = DashboardRepository()

    def get_all_author_names_and_dataset_counts(self):
        author_data = self.dashboard_repository.get_author_names_and_dataset_counts()
        author_names = [data[0] for data in author_data]
        dataset_counts = [data[1] for data in author_data]
        return author_names, dataset_counts

    def get_all_author_names_and_view_counts(self):
        author_data = self.dashboard_repository.get_author_names_and_view_counts()
        author_names = [data[0] for data in author_data]
        view_counts = [data[1] for data in author_data]
        return author_names, view_counts

    def get_datasets_and_total_sizes(self):
        datasets = self.repository.get_all_datasets()
        dataset_info = []
        for dataset in datasets:
            total_size = sum(file.size for fm in dataset.feature_models for file in fm.files)
            dataset_info.append((dataset.name(), total_size))
        dataset_info.sort(key=lambda x: x[1], reverse=True)
        dataset_names = [name for name, _ in dataset_info]
        total_sizes = [size for _, size in dataset_info]

        return dataset_names, total_sizes

    def get_views_over_time_with_filter(self, filter_type="day"):
        result = self.dashboard_repository.get_views_over_time(filter_type)
        dates = [record[0] for record in result]
        view_counts = [record[1]for record in result]
        return dates, view_counts

    def get_publication_types_data(self):
        result = self.dashboard_repository.get_publication_types_count()
        publication_types_count = {str(row[0]): row[1] for row in result}
        return publication_types_count

    def get_downloads_by_day(self):
        result = self.dashboard_repository.get_downloads_by_day_data()
        downloads_by_day = {
            record.download_date.strftime('%Y-%m-%d'): record.download_count for record in result
        }
        return downloads_by_day
