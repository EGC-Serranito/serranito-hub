from app.modules.dataset.repositories import (
    DataSetRepository,
)

from app.modules.dashboard.repositories import DashboardAuthorRepository
from core.services.BaseService import BaseService


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
            # Calcula el tamaño total en bytes sin convertirlo a KB o MB
            total_size = sum(file.size for fm in dataset.feature_models for file in fm.files)
            
            # Agrega el nombre del dataset y su tamaño en bytes
            dataset_names.append(dataset.name())
            total_sizes.append(total_size)  # Pasa el tamaño en bytes directamente
        
        return dataset_names, total_sizes
