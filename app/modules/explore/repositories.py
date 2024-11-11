import re
from sqlalchemy import any_, or_, func
import unidecode
from app.modules.dataset.models import Author, DSMetaData, DataSet, PublicationType
from app.modules.featuremodel.models import FMMetaData, FeatureModel
from core.repositories.BaseRepository import BaseRepository
from app import db


class ExploreRepository(BaseRepository):
    def __init__(self):
        super().__init__(DataSet)

    def filter(self, query="", sorting="newest", publication_type="any", tags=[], **kwargs):
        # Normalize and remove unwanted characters
        normalized_query = unidecode.unidecode(query).lower()
        cleaned_query = re.sub(r'[,.":\'()\[\]^;!¡¿?]', "", normalized_query)

        filters = []
        for word in cleaned_query.split():
            filters.append(DSMetaData.title.ilike(f"%{word}%"))
            filters.append(DSMetaData.description.ilike(f"%{word}%"))
            filters.append(Author.name.ilike(f"%{word}%"))
            filters.append(Author.affiliation.ilike(f"%{word}%"))
            filters.append(Author.orcid.ilike(f"%{word}%"))
            filters.append(FMMetaData.uvl_filename.ilike(f"%{word}%"))
            filters.append(FMMetaData.title.ilike(f"%{word}%"))
            filters.append(FMMetaData.description.ilike(f"%{word}%"))
            filters.append(FMMetaData.publication_doi.ilike(f"%{word}%"))
            filters.append(FMMetaData.tags.ilike(f"%{word}%"))
            filters.append(DSMetaData.tags.ilike(f"%{word}%"))

        datasets = (
            self.model.query
            .join(DataSet.ds_meta_data)
            .join(DSMetaData.authors)
            .join(DataSet.feature_models)
            .join(FeatureModel.fm_meta_data)
            .filter(or_(*filters))
            .filter(DSMetaData.dataset_doi.isnot(None))  # Exclude datasets with empty dataset_doi
        )

        if publication_type != "any":
            matching_type = None
            for member in PublicationType:
                if member.value.lower() == publication_type:
                    matching_type = member
                    break

            if matching_type is not None:
                datasets = datasets.filter(DSMetaData.publication_type == matching_type.name)

        if tags:
            datasets = datasets.filter(DSMetaData.tags.ilike(any_(f"%{tag}%" for tag in tags)))

        # Order by sorting criteria
        if sorting == "oldest":
            datasets = datasets.order_by(self.model.created_at.asc())
        elif sorting == "newest":
            datasets = datasets.order_by(self.model.created_at.desc())
        elif sorting == "name_asc":
            datasets = datasets.order_by(DSMetaData.title.asc())
        elif sorting == "name_desc":
            datasets = datasets.order_by(DSMetaData.title.desc())
        elif sorting == "feature_models_asc":
            datasets = datasets.group_by(DataSet.id).order_by(func.count(FeatureModel.id).asc())
        elif sorting == "feature_models_desc":
            datasets = datasets.group_by(DataSet.id).order_by(func.count(FeatureModel.id).desc())

        return datasets.all()

    def filter_feature_models(self, tags=[]):
        """Filtra y devuelve Feature Models según etiquetas."""
        feature_models_query = (
            FeatureModel.query
            .join(FeatureModel.fm_meta_data)
            .filter(or_(FMMetaData.tags.ilike(f"%{tag}%") for tag in tags))
        )
        return feature_models_query.all()

    def get_tag_cloud(self):
        """Genera la nube de etiquetas con la frecuencia de uso de cada tag."""
        tag_counts = (
            db.session.query(FMMetaData.tags)
            .filter(FMMetaData.tags.isnot(None))
            .all()
        )
        tag_frequency = {}
        for tag_list in tag_counts:
            tags = tag_list[0].split(',')
            for tag in tags:
                tag = tag.strip().lower()
                if tag:
                    tag_frequency[tag] = tag_frequency.get(tag, 0) + 1

        return tag_frequency
