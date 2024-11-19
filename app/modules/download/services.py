from app.modules.download.repositories import DownloadRepository
from app.modules.dataset.repositories import DataSetRepository
from app.modules.dataset.services import DataSetService
from core.services.BaseService import BaseService
from app.modules.profile.repositories import UserProfileRepository
import io
import os
import zipfile
import logging


class DownloadService(BaseService):
    def __init__(self):
        super().__init__(DownloadRepository())
        self.dataset_service = DataSetService()
        self.user_profile_repository = UserProfileRepository()

    def get_all_dataset_ids(self):
        datasets = DataSetRepository().get_all_datasets()
        return [dataset.id for dataset in datasets]

    def get_in_date_range_dataset_ids(self, start_date, end_date):
        datasets = DataSetRepository().get_all_datasets()

        dataset_ids = [
            dataset.id
            for dataset in datasets
            if hasattr(dataset, "created_at")
            and start_date <= dataset.created_at <= end_date
        ]

        return dataset_ids

    def zip_all_datasets(self):
        """Create a single ZIP file containing all files from all datasets and return its content in BytesIO."""
        dataset_ids = self.get_all_dataset_ids()
        try:
            master_zip_buffer = io.BytesIO()
            with zipfile.ZipFile(
                master_zip_buffer, "w", zipfile.ZIP_DEFLATED
            ) as master_zip:
                for dataset_id in dataset_ids:
                    try:
                        dataset = self.dataset_service.get_or_404(dataset_id)
                        user_name = self.user_profile_repository.get_by_user_id(
                            dataset.user_id
                        ).name
                        user_unique_name = f"{user_name}_{dataset.user_id}"
                        dataset_name = self.dataset_service.get_dataset_title(
                            dataset_id
                        )
                        dataset_name = dataset_name.replace(" ", "_")
                        dataset_unique_name = f"{dataset_name}_{dataset_id}"
                        file_base_path = (
                            f"uploads/user_{dataset.user_id}/dataset_{dataset.id}/"
                        )

                        if not os.path.exists(file_base_path):
                            logging.error(f"Directory does not exist: {file_base_path}")
                            continue

                        for subdir, dirs, files in os.walk(file_base_path):
                            for file in files:
                                full_path = os.path.join(subdir, file)
                                relative_path = os.path.relpath(
                                    full_path, file_base_path
                                )
                                arcname = os.path.join(
                                    f"{user_unique_name}/{dataset_unique_name}",
                                    relative_path,
                                )
                                master_zip.write(full_path, arcname=arcname)
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

    def zip_datasets_by_date(self, start_date, end_date):
        """Create a single ZIP file containing all files from all datasets within
        a date range and return its content in BytesIO."""
        dataset_ids = self.get_in_date_range_dataset_ids(start_date, end_date)

        if not dataset_ids:
            return None

        try:
            master_zip_buffer = io.BytesIO()
            with zipfile.ZipFile(
                master_zip_buffer, "w", zipfile.ZIP_DEFLATED
            ) as master_zip:
                for dataset_id in dataset_ids:
                    try:
                        dataset = self.dataset_service.get_or_404(dataset_id)
                        user_name = self.user_profile_repository.get_by_user_id(
                            dataset.user_id
                        ).name
                        user_unique_name = f"{user_name}_{dataset.user_id}"
                        dataset_name = self.dataset_service.get_dataset_title(
                            dataset_id
                        )
                        dataset_name = dataset_name.replace(" ", "_")
                        dataset_unique_name = f"{dataset_name}_{dataset_id}"
                        file_base_path = (
                            f"uploads/user_{dataset.user_id}/dataset_{dataset.id}/"
                        )

                        if not os.path.exists(file_base_path):
                            logging.error(f"Directory does not exist: {file_base_path}")
                            continue

                        for subdir, dirs, files in os.walk(file_base_path):
                            for file in files:
                                full_path = os.path.join(subdir, file)
                                relative_path = os.path.relpath(
                                    full_path, file_base_path
                                )
                                arcname = os.path.join(
                                    f"{user_unique_name}/{dataset_unique_name}",
                                    relative_path,
                                )
                                master_zip.write(full_path, arcname=arcname)
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
