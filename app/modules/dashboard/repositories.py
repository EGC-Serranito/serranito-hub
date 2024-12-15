from core.repositories.BaseRepository import BaseRepository
from sqlalchemy import func
from app.modules.dataset.models import (
    Author,
    DSMetaData,
    DSViewRecord,
    DataSet,
    DSDownloadRecord

)


class DashboardRepository(BaseRepository):
    def __init__(self):
        super().__init__(Author)

    def get_author_names_and_dataset_counts(self):
        result = (
            Author.query.outerjoin(DSMetaData, Author.ds_meta_data_id == DSMetaData.id)
            .with_entities(
                Author.name, func.count(DSMetaData.id).label("dataset_count")
            )
            .group_by(Author.name)
            .order_by(func.count(DSMetaData.id).desc())
            .all()
        )
        return result

    def get_author_names_and_view_counts(self):
        result = (
            Author.query.join(DSMetaData, Author.ds_meta_data_id == DSMetaData.id)
            .join(DataSet, DSMetaData.id == DataSet.ds_meta_data_id)
            .outerjoin(DSViewRecord, DataSet.id == DSViewRecord.dataset_id)
            .with_entities(Author.name, func.count(DSViewRecord.id).label('view_count'))
            .group_by(Author.name)
            .order_by(func.count(DSViewRecord.id).desc())
            .all()
        )
        return result

    def get_views_over_time(self, filter_type="day"):
        if filter_type == "month":
            group_by_filter = func.date_format(DSViewRecord.view_date, '%Y-%m')
        elif filter_type == "year":
            group_by_filter = func.date_format(DSViewRecord.view_date, '%Y')
        else:
            group_by_filter = func.date_format(DSViewRecord.view_date, '%Y-%m-%d')

        result = (
            self.session.query(
                group_by_filter.label("view_dates"),
                func.count(DSViewRecord.id).label("view_counts_over_time")
            )
            .group_by(group_by_filter)
            .order_by(group_by_filter)
            .all()
        )

        return result

    def get_publication_types_count(self):
        result = (
            self.session
            .query(DSMetaData.publication_type, func.count(DSMetaData.id))
            .group_by(DSMetaData.publication_type)
            .all()
        )
        return result

    def get_downloads_by_day_data(self):
        result = (
            self.session.query(
                func.date(DSDownloadRecord.download_date).label("download_date"),
                func.count(DSDownloadRecord.id).label("download_count")
            )
            .group_by(func.date(DSDownloadRecord.download_date))
            .order_by(func.date(DSDownloadRecord.download_date))
            .all()
        )
        print(result)
        return result
