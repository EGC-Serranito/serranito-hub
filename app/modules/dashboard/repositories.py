from core.repositories.BaseRepository import BaseRepository
from sqlalchemy import func

from app.modules.dataset.models import (
    Author,
    DSMetaData,
    DSViewRecord,
    DataSet

)


class DashboardAuthorRepository(BaseRepository):
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

