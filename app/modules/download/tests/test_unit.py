import pytest
from unittest.mock import MagicMock
from app.modules.dataset.services import DataSetService
from app.modules.dataset.models import DataSet
from app import create_app
from app.modules.download.services import DownloadService
from app.modules.auth.models import User


@pytest.fixture
def dataset_service():
    return DataSetService()


@pytest.fixture
def mock_user():
    app = create_app()
    with app.app_context():
        user = MagicMock(spec=User)
        user.id = 1
        user.temp_folder.return_value = "/mock/temp/folder"
        user.profile.surname = "Doe"
        user.profile.name = "John"
        user.profile.affiliation = "Test University"
        user.profile.orcid = "0000-0001-2345-6789"
        return user


@pytest.fixture
def mock_datasets():
    app = create_app()
    with app.app_context():
        # Crear datasets mockeados para la prueba
        dataset1 = MagicMock(spec=DataSet)
        dataset1.id = 1
        dataset1.created_at = "1900-01-15"
        dataset1.user_id = 1
        dataset1.user = MagicMock()
        dataset1.user.mail = "mockuser@example.com"
        dataset1.user.profile = MagicMock()
        dataset1.user.profile.name = "John"
        dataset1.user.profile.surname = "Doe"
        dataset1.user.profile.affiliation = "Test University"
        dataset1.user.profile.orcid = "0000-0001-2345-6789"

        dataset2 = MagicMock(spec=DataSet)
        dataset2.id = 2
        dataset2.created_at = "2021-05-20"
        dataset2.user_id = 1

        dataset3 = MagicMock(spec=DataSet)
        dataset3.id = 3
        dataset3.created_at = "2022-03-10"
        dataset3.user_id = 2

        return [dataset1, dataset2, dataset3]


@pytest.fixture
def download_service(mock_datasets):
    app = create_app()
    with app.app_context():
        download_service = DownloadService()

        download_service.get_all_dataset_ids = MagicMock(
            return_value=[dataset.id for dataset in mock_datasets]
        )

        download_service.get_in_date_range_dataset_ids = MagicMock(
            side_effect=lambda start_date, end_date: [
                dataset.id
                for dataset in mock_datasets
                if start_date <= dataset.created_at <= end_date
            ]
        )

        download_service.get_dataset_ids_by_email = MagicMock(
            side_effect=lambda email: [
                dataset.id for dataset in mock_datasets if dataset.user.mail == email
            ]
        )

        return download_service


def test_get_all_dataset_ids(download_service):
    dataset_ids = download_service.get_all_dataset_ids()
    assert len(dataset_ids) == 3
    assert dataset_ids == [1, 2, 3]
    download_service.get_all_dataset_ids.assert_called_once()


def test_get_in_date_range_dataset_ids(download_service):
    start_date = "1900-01-01"
    end_date = "1901-01-01"
    dataset_ids = download_service.get_in_date_range_dataset_ids(start_date, end_date)
    assert len(dataset_ids) == 1
    assert dataset_ids == [1]
    download_service.get_in_date_range_dataset_ids.assert_called_once_with(
        start_date, end_date
    )


def test_get_dataset_ids_by_email(download_service):
    email = "mockuser@example.com"

    dataset_ids = download_service.get_dataset_ids_by_email(email)

    assert dataset_ids == [1]
    download_service.get_dataset_ids_by_email.assert_called_once_with(email)
