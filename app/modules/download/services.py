from app.modules.download.repositories import DownloadRepository
from app.modules.dataset.repositories import DataSetRepository
from app.modules.dataset.services import DataSetService
from core.services.BaseService import BaseService
import io
import os
import zipfile
import logging


class DownloadService(BaseService):
    def __init__(self):
        super().__init__(DownloadRepository())
        self.dataset_service = DataSetService()
        
    def get_all_dataset_ids(self):
        datasets = DataSetRepository().get_all_datasets()
        return [dataset.id for dataset in datasets]

    def create_zip_for_dataset(self, dataset_id):
        """Create a ZIP file containing all files related to a dataset and return its content in BytesIO."""
        try:
            dataset = self.get_or_404(dataset_id)
            zip_buffer = io.BytesIO()

            with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zipf:
                file_path = f"uploads/user_{dataset.user_id}/dataset_{dataset.id}/"
                for subdir, dirs, files in os.walk(file_path):
                    for file in files:
                        full_path = os.path.join(subdir, file)
                        relative_path = os.path.relpath(full_path, file_path)
                        zipf.write(full_path, arcname=relative_path)

            zip_buffer.seek(0)
            return zip_buffer
        except Exception as e:
            logging.error(f"Error while creating ZIP for dataset {dataset_id}: {e}")
            raise e

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
