from app.modules.explore.repositories import ExploreRepository
from core.services.BaseService import BaseService


class ExploreService(BaseService):
    def __init__(self):
        super().__init__(ExploreRepository())

    def filter(self, query="", sorting="newest", publication_type="any", tags=[], **kwargs):
        return self.repository.filter(query, sorting, publication_type, tags, **kwargs)

    def filter_feature_models(self, tags=[]):
        """Llama a la función de repositorio para filtrar Feature Models por tags."""
        return self.repository.filter_feature_models(tags)

    def get_tag_cloud(self):
        """Obtiene la nube de etiquetas para los Feature Models."""
        return self.repository.get_tag_cloud()
