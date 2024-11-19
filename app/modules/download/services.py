from app.modules.download.repositories import DownloadRepository
from app.modules.dataset.repositories import DataSetRepository
from app.modules.dataset.services import DataSetService
from app.modules.auth.services import UserRepository
from core.services.BaseService import BaseService
import io
import os
import zipfile
import logging


class DownloadService(BaseService):
    def __init__(self):
        super().__init__(DownloadRepository())
        self.dataset_service = DataSetService()
        self.user_repository = UserRepository()
        
    def get_all_dataset_ids(self):
        datasets = DataSetRepository().get_all_datasets()
        return [dataset.id for dataset in datasets]

    def zip_all_datasets(self):
        """Create a single ZIP file containing all files from all datasets and return its content in BytesIO."""
        dataset_ids = self.get_all_dataset_ids()
        print(dataset_ids)
        try:
            master_zip_buffer = io.BytesIO()
            with zipfile.ZipFile(
                master_zip_buffer, "w", zipfile.ZIP_DEFLATED
            ) as master_zip:
                for dataset_id in dataset_ids:
                    try:
                        dataset = self.dataset_service.get_or_404(dataset_id)
                        username = self.user_repository.get_by_id(dataset.user_id).email
                        file_base_path = (
                            f"uploads/user_{dataset.user_id}/dataset_{dataset.id}/"
                        )

                        for subdir, dirs, files in os.walk(file_base_path):
                            for file in files:
                                full_path = os.path.join(subdir, file)
                                relative_path = os.path.relpath(full_path, "uploads/")
                                master_zip.write(full_path, arcname=relative_path)
                    except Exception as e:
                        logging.error(
                            f"Error while processing dataset {dataset_id}: {e}"
                        )
                        continue
            master_zip_buffer.seek(0)
            return master_zip_buffer
        except Exception as e:
            logging.error(f"Error while creating master ZIP: {e}")
            raise e
