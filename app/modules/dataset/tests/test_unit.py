import hashlib
import pytest
from unittest.mock import mock_open, patch, MagicMock
from app.modules.dataset.services import DataSetService, calculate_checksum_and_size, SizeService, DOIMappingService
from app.modules.dataset.services import DatasetRatingService
from app.modules.dataset.models import DataSet, DSMetaData, DatasetUserRate
from app.modules.auth.models import User
import os
from app import create_app, db
from app.modules.profile.models import UserProfile
from app.modules.conftest import login, logout


@pytest.fixture
def size_service():
    return SizeService()


@pytest.fixture
def dataset_service():
    return DataSetService()


@pytest.fixture
def dataset_rating_service():
    return DatasetRatingService()


@pytest.fixture
def doi_mapping_service():
    return DOIMappingService()


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
def mock_dataset():
    app = create_app()
    with app.app_context():
        dataset = MagicMock(spec=DataSet)
        dataset.id = 1
        dataset.feature_models = []
        return dataset


@pytest.fixture
def mock_dataset_rating():
    app = create_app()
    with app.app_context():
        dataset_user_rating = MagicMock(spec=DatasetUserRate)
        dataset_user_rating.rate = 5
        dataset_user_rating.dataset_id = 1
        dataset_user_rating.user_id = 1
        return dataset_user_rating


@pytest.fixture(scope="module")
def test_client(test_client):
    """
    Extends the test_client fixture to add additional specific data for module testing.
    """
    with test_client.application.app_context():
        user_test = User(email='user@example.com', password='test1234')
        db.session.add(user_test)
        db.session.commit()

        profile = UserProfile(user_id=user_test.id, name="Name", surname="Surname")
        db.session.add(profile)
        db.session.commit()

    yield test_client


def test_move_feature_models(dataset_service, mock_user, mock_dataset):
    with patch("app.modules.auth.services.AuthenticationService.get_authenticated_user", return_value=mock_user), \
            patch("shutil.move") as mock_move, \
            patch("os.makedirs") as mock_makedirs:

        dataset_service.move_feature_models(mock_dataset)

        mock_makedirs.assert_called_once()
        for feature_model in mock_dataset.feature_models:
            mock_move.assert_any_call(
                os.path.join(mock_user.temp_folder(), feature_model.fm_meta_data.uvl_filename),
                f"/uploads/user_{mock_user.id}/dataset_{mock_dataset.id}"
            )


def test_create_from_form(dataset_service, mock_user):
    form = MagicMock()
    form.get_dsmetadata.return_value = {
        "title": "Test Dataset",
        "description": "This is a test dataset",
        "doi": "10.1234/test"
    }
    form.get_authors.return_value = [
        {"name": "Author One", "affiliation": "University", "orcid": "0000-0002-1234-5678"}
    ]
    form.feature_models = []
    app = create_app()
    with app.app_context():
        with patch.object(dataset_service.dsmetadata_repository, 'create') as mock_create_dsmetadata, \
                patch.object(dataset_service.author_repository, 'create') as mock_create_author, \
                patch.object(dataset_service.repository, 'create') as mock_create_dataset, \
                patch.object(dataset_service.repository.session, 'commit'):

            mock_dsmetadata = MagicMock(spec=DSMetaData)
            mock_dsmetadata.id = 1
            mock_create_dsmetadata.return_value = mock_dsmetadata

            result = dataset_service.create_from_form(form, mock_user)

            mock_create_dsmetadata.assert_called_once_with(**form.get_dsmetadata())
            mock_create_author.assert_called_with(
                commit=False, ds_meta_data_id=mock_dsmetadata.id, **form.get_authors()[0]
            )
            assert result == mock_create_dataset.return_value


def test_get_synchronized(dataset_service):
    app = create_app()
    with app.app_context():
        with patch.object(dataset_service.repository, 'get_synchronized') as mock_get_synchronized:
            mock_dataset = MagicMock(spec=DataSet)
            mock_get_synchronized.return_value = mock_dataset

            user_id = 1
            result = dataset_service.get_synchronized(user_id)

            assert result == mock_dataset
            mock_get_synchronized.assert_called_once_with(user_id)


def test_get_uvlhub_doi(dataset_service, mock_dataset):
    app = create_app()
    with app.app_context():
        with patch("os.getenv", return_value="testdomain.com"):
            mock_dataset.ds_meta_data.dataset_doi = "10.1234/test-doi"

            result = dataset_service.get_uvlhub_doi(mock_dataset)

            assert result == "http://testdomain.com/doi/10.1234/test-doi"


def test_count_synchronized_datasets(dataset_service):
    with patch.object(dataset_service.repository, 'count_synchronized_datasets') as mock_count:
        mock_count.return_value = 5
        result = dataset_service.count_synchronized_datasets()

        assert result == 5
        mock_count.assert_called_once()


def test_total_dataset_downloads(dataset_service):
    with patch.object(dataset_service.dsdownloadrecord_repository, 'total_dataset_downloads') as mock_total_downloads:
        mock_total_downloads.return_value = 100
        result = dataset_service.total_dataset_downloads()

        assert result == 100
        mock_total_downloads.assert_called_once()


def test_total_dataset_views(dataset_service):
    with patch.object(dataset_service.dsviewrecord_repostory, 'total_dataset_views') as mock_total_views:
        mock_total_views.return_value = 200
        result = dataset_service.total_dataset_views()

        assert result == 200
        mock_total_views.assert_called_once()


def test_calculate_checksum_and_size():
    with patch("builtins.open", mock_open(read_data=b"test content")) as mock_file, \
            patch("os.path.getsize", return_value=12) as mock_getsize:
        checksum, size = calculate_checksum_and_size("/mock/path/to/file")
        mock_file.assert_called_once_with("/mock/path/to/file", "rb")
        mock_getsize.assert_called_once_with("/mock/path/to/file")
        assert checksum == hashlib.md5(b"test content").hexdigest()
        assert size == 12


def test_update_dsmetadata(dataset_service):
    with patch.object(dataset_service.dsmetadata_repository, 'update') as mock_update:
        mock_update.return_value = True

        result = dataset_service.update_dsmetadata(1, title="Updated Title")

        assert result is True
        mock_update.assert_called_once_with(1, title="Updated Title")


def test_get_human_readable_size(size_service):
    assert size_service.get_human_readable_size(500) == '500 bytes'
    assert size_service.get_human_readable_size(1024) == '1.0 KB'
    assert size_service.get_human_readable_size(1024 ** 2) == '1.0 MB'
    assert size_service.get_human_readable_size(1024 ** 3) == '1.0 GB'


def test_get_unsynchronized(dataset_service):
    app = create_app()
    with app.app_context():
        with patch.object(dataset_service.repository, 'get_unsynchronized') as mock_get_unsynchronized:
            mock_dataset = MagicMock(spec=DataSet)
            mock_get_unsynchronized.return_value = [mock_dataset]
            mock_dataset = MagicMock(spec=DataSet)
            mock_get_unsynchronized.return_value = mock_dataset

            user_id = 1
            result = dataset_service.get_unsynchronized(user_id)

            assert result == mock_dataset
            mock_get_unsynchronized.assert_called_once_with(user_id)


def test_get_unsynchronized_dataset(dataset_service):
    app = create_app()
    with app.app_context():
        with patch.object(dataset_service.repository, 'get_unsynchronized_dataset') as mock_get_unsynchronized_dataset:
            mock_dataset = MagicMock(spec=DataSet)
            mock_get_unsynchronized_dataset.return_value = mock_dataset

            user_id = 1
            dataset_id = 2
            result = dataset_service.get_unsynchronized_dataset(user_id, dataset_id)

            assert result == mock_dataset
            mock_get_unsynchronized_dataset.assert_called_once_with(user_id, dataset_id)


def test_get_new_doi(doi_mapping_service):
    with patch.object(doi_mapping_service.repository, 'get_new_doi') as mock_get_new_doi:
        mock_get_new_doi.return_value = MagicMock(dataset_doi_new="10.5678/new-doi")

        old_doi = "10.1234/old-doi"
        result = doi_mapping_service.get_new_doi(old_doi)

        assert result == "10.5678/new-doi"
        mock_get_new_doi.assert_called_once_with(old_doi)


def test_count_authors(dataset_service):
    with patch.object(dataset_service, 'author_repository', MagicMock()) as author_repository_mock:
        author_repository_mock.count.return_value = 15
        result = dataset_service.count_authors()
        assert result == 15


def test_count_dsmetadata(dataset_service):
    with patch.object(dataset_service, 'dsmetadata_repository', MagicMock()) as dsmetadata_repository_mock:
        dsmetadata_repository_mock.count.return_value = 20
        result = dataset_service.count_dsmetadata()
        assert result == 20


def test_rate_for_first_time(dataset_rating_service, mock_dataset_rating):
    app = create_app()
    with app.app_context():
        with patch.object(dataset_rating_service.repository, 'add_rating') as mock_submit_rating, \
                patch.object(dataset_rating_service.repository, 'find_user_rating') as mock_find_rating:
            mock_submit_rating.return_value = mock_dataset_rating
            mock_find_rating.return_value = None

            dataset_id = 1
            user_id = 1
            rate = 5
            dataset_rating_service.submit_rating(dataset_id, user_id, rate)

            assert mock_dataset_rating.rate == rate
            assert mock_dataset_rating.dataset_id == dataset_id
            assert mock_dataset_rating.user_id == user_id
            mock_submit_rating.assert_called_once_with(dataset_id, user_id, rate)


def test_update_rate(dataset_rating_service, mock_dataset_rating):
    app = create_app()
    with app.app_context():
        with patch.object(dataset_rating_service.repository, 'find_user_rating') as mock_find_rating, \
                patch.object(dataset_rating_service.repository, 'update_rating') as mock_update_rating:

            # Configurar el mock para `find_user_rating`
            mock_old_dataset_rating = MagicMock(spec=DatasetUserRate)
            mock_old_dataset_rating.rate = 3
            mock_old_dataset_rating.dataset_id = 1
            mock_old_dataset_rating.user_id = 1
            mock_find_rating.return_value = mock_old_dataset_rating

            mock_update_rating.return_value = mock_old_dataset_rating

            dataset_id = 1
            user_id = 1
            rate = 5

            result = dataset_rating_service.submit_rating(dataset_id, user_id, rate)

            assert result == mock_old_dataset_rating
            assert mock_old_dataset_rating.rate == 3
            assert mock_dataset_rating.rate == 5

            mock_find_rating.assert_called_once_with(dataset_id, user_id)
            mock_update_rating.assert_called_once_with(mock_old_dataset_rating, rate)


def test_get_average_rating(dataset_rating_service):
    app = create_app()
    with app.app_context():
        with patch.object(dataset_rating_service.repository, 'get_all_ratings') as mock_get_all_ratings:
            mock_rating = MagicMock()
            mock_rating.rate = 5
            mock_get_all_ratings.return_value = [mock_rating]

            dataset_id = 1
            result = dataset_rating_service.get_average_rating(dataset_id)

            assert result == 5
            mock_get_all_ratings.assert_called_once_with(dataset_id)


def test_find_rating_by_user_and_dataset(dataset_rating_service, mock_dataset_rating):
    app = create_app()
    with app.app_context():
        with patch.object(dataset_rating_service.repository, 'find_user_rating') as mock_find_rating:
            mock_find_rating.return_value = mock_dataset_rating

            dataset_id = 1
            user_id = 1
            result = dataset_rating_service.find_rating_by_user_and_dataset(dataset_id, user_id)

            assert result == mock_dataset_rating
            mock_find_rating.assert_called_once_with(dataset_id, user_id)


def test_rate_dataset(test_client):
    login_response = login(test_client, "user@example.com", "test1234")
    assert login_response.status_code == 200, "Login was unsuccessful."

    response = test_client.post('/rate_dataset/1', data={
        'rate': '4'
    }, follow_redirects=True)
    assert response.status_code == 200
    logout(test_client)
