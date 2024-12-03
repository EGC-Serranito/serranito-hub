from app.modules.dataset.repositories import (
    DataSetRepository,
)
from app import db
from app.modules.dashboard.repositories import DashboardAuthorRepository
from core.services.BaseService import BaseService
from sqlalchemy import func
from app.modules.dataset.models import DSViewRecord, DSMetaData, DSDownloadRecord


class DashBoardService(BaseService):
    def __init__(self):
        super().__init__(DataSetRepository())
        self.dashboard_author_repository = DashboardAuthorRepository()

    def get_all_author_names_and_dataset_counts(self):
        author_data = self.dashboard_author_repository.get_author_names_and_dataset_counts()
        author_names = [data.name for data in author_data]
        dataset_counts = [data.dataset_count for data in author_data]
        return author_names, dataset_counts

    def get_all_author_names_and_view_counts(self):
        author_data = self.dashboard_author_repository.get_author_names_and_view_counts()
        author_names = [data.name for data in author_data]
        view_counts = [data.view_count for data in author_data]
        return author_names, view_counts

    def get_datasets_and_total_sizes(self):
        datasets = self.repository.get_all_datasets()
        dataset_names = []
        total_sizes = []

        for dataset in datasets:
            total_size = sum(file.size for fm in dataset.feature_models for file in fm.files)
            dataset_names.append(dataset.name())
            total_sizes.append(total_size)

        return dataset_names, total_sizes

    def get_views_over_time_with_filter(self, filter_type="day"):
        if filter_type == "month":
            group_by_filter = func.date_format(DSViewRecord.view_date, '%Y-%m')
        elif filter_type == "year":
            group_by_filter = func.date_format(DSViewRecord.view_date, '%Y')
        else:  # Default to "day"
            group_by_filter = func.date_format(DSViewRecord.view_date, '%Y-%m-%d')

        # Construcción de la consulta
        result = (
            self.repository.session.query(
                group_by_filter.label("view_dates"),
                func.count(DSViewRecord.id).label("view_counts_over_time")
            )
            .group_by(group_by_filter)
            .order_by(group_by_filter)
            .all()
        )

        if not result:
            return [], []

        # Formatear las fechas y los datos
        dates = [record.view_dates for record in result]
        view_counts = [record.view_counts_over_time for record in result]

        return dates, view_counts

    @staticmethod
    def get_publication_types_data():
        result = (
            db.session
            .query(DSMetaData.publication_type, db.func.count(DSMetaData.id))
            .group_by(DSMetaData.publication_type)
            .all()
        )
        publication_types_count = {str(row[0]): row[1] for row in result}

        return publication_types_count

    def get_downloads_by_day(self):
        result = (
            db.session.query(
                func.date(DSDownloadRecord.download_date).label("download_date"),
                func.count(DSDownloadRecord.id).label("download_count")
            )
            .group_by(func.date(DSDownloadRecord.download_date))
            .order_by(func.date(DSDownloadRecord.download_date))
            .all()
        )

        downloads_by_day = {
            record.download_date.strftime('%Y-%m-%d'): record.download_count for record in result
        }

        return downloads_by_day
